// Files must be scoped by the caller to the approved source-archive folder.
// A commit is written last, after all page, key, metadata and generation gates.
(Files as table) as table =>
let
    StoredType=type table [Source=text,SourceID=text,FirstObservedAtUTC=datetimezone,LastObservedAtUTC=datetimezone,LastBatchID=text,MetadataJSON=text],
    ReadFile=(Name as text) as binary =>
        let Matches=Table.SelectRows(Files,each [Name]=Name)
        in if Table.RowCount(Matches)=1 then Binary.Buffer(Matches{0}[Content]) else error "Missing or duplicate committed file",
    VerifyRaw=(M as record) as logical =>
        if not Record.HasFields(M,"RawObservation") then true else let
            R=M[RawObservation], D=Json.Document(ReadFile(R[DescriptorName])),
            Chain=M[ProcessingChain], R1=Chain[steps]{0},
            Bound=R[Version]=1 and R[StoredBytesVerified]=true and D=R[Descriptor] and
                R[DescriptorName]="raw-observation-"&M[BatchID]&"-descriptor.json" and
                D[kind]="raw_observation_descriptor_v1" and D[accepted_commit]=false and D[typed_status]="accepted" and
                D[batch_id]=M[BatchID] and D[model_id]=M[ModelID] and D[workspace_id]=Chain[workspace_id] and
                D[source_capture_definition_sha256]=Chain[definition_sha256] and D[source_request_id]=R1[request_id] and
                D[source_started_at_utc]=R1[started_at_utc] and D[source_completed_at_utc]=R1[completed_at_utc] and
                D[typed_audit_counts]=[rows=9,distinct_checks=9,expected_checks=9,failed_rows=0],
            Parts=List.Transform(List.Positions(D[file_parts]),(i)=>let
                E=D[file_parts]{i}, P=Json.Document(ReadFile(E[name]))
                in if E[name]="raw-observation-"&M[BatchID]&"-descriptor-part-"&Text.From(i)&".json" and
                    P[kind]="raw_observation_file_index_v1" and P[batch_id]=M[BatchID] and
                    P[source_request_id]=D[source_request_id] and P[part_index]=i then P[files] else error "Raw index drift"),
            Entries=List.Buffer(List.Combine(Parts)),
            Pages=List.Transform(List.Positions(Entries),(i)=>let E=Entries{i}, Rows=Json.Document(ReadFile(E[name]))
                in if E[name]="raw-observation-"&M[BatchID]&"-PubMedRawResponseChunks-"&Text.From(i)&".json" and
                    Value.Is(Rows,type list) and E[rows]>0 and List.Count(Rows)=E[rows] then Rows else error "Raw page drift"),
            WireRows=List.Combine(Pages),
            Rows=List.Buffer(List.Transform(WireRows,(r)=>Record.TransformFields(Record.FromList(Record.FieldValues(r),
                List.Transform(Record.FieldNames(r),each if Text.StartsWith(_,"[") and Text.EndsWith(_, "]") then Text.Middle(_,1,Text.Length(_)-2) else error "Raw wire field drift")),{}))),
            Pairs=List.Transform(Rows,each Text.From([RawResponseIndex])&":"&Text.From([RawChunkIndex])),
            ResponseIDs=List.Sort(List.Distinct(List.Transform(Rows,each [RawResponseIndex]))),
            ResponsesComplete=ResponseIDs=List.Numbers(0,D[independent_response_count]) and List.AllTrue(List.Transform(ResponseIDs,(ID)=>let
                Chunks=List.Sort(List.Select(Rows,each [RawResponseIndex]=ID),(a,b)=>Value.Compare(a[RawChunkIndex],b[RawChunkIndex])),
                H=Chunks{0}, Headers={"RawEndpoint","RawRequestJSON","RawAcquiredUTC","RawByteCount","RawSchemaByteCount","RawChunkCount","RawHTTPStatus"},
                Same=List.AllTrue(List.Transform(Chunks,each Record.SelectFields(_,Headers)=Record.SelectFields(H,Headers))),
                Payload=Binary.FromText(Text.Combine(List.Transform(Chunks,each [RawPayloadBase64])),BinaryEncoding.Base64),
                Schema=Binary.FromText(Text.Combine(List.Transform(Chunks,each [RawSchemaBase64])),BinaryEncoding.Base64),
                Observed=DateTimeZone.FromText(H[RawAcquiredUTC])
                in Same and H[RawChunkCount]>0 and List.Transform(Chunks,each [RawChunkIndex])=List.Numbers(0,H[RawChunkCount]) and
                    Binary.Length(Payload)=H[RawByteCount] and Binary.Length(Schema)=H[RawSchemaByteCount] and
                    Value.Is(Json.Document(Schema),type record) and
                    Observed>=DateTimeZone.FromText(D[source_started_at_utc]) and Observed<=DateTimeZone.FromText(D[source_completed_at_utc]))),
            Complete=List.Count(Entries)=D[data_file_count] and List.Count(Entries)>0 and
                List.Count(Rows)=D[independent_chunk_count] and List.Count(List.Distinct(Pairs))=List.Count(Rows) and
                List.Count(List.Distinct(List.Transform(Rows,each [RawResponseIndex])))=D[independent_response_count] and
                List.AllTrue(List.Transform(Rows,each [SourceKind]="PubMedRawResponseChunks" and [RawHTTPStatus]>=200 and [RawHTTPStatus]<300))
        in if Bound and Complete and ResponsesComplete then true else error "Unaccepted or incomplete raw-backed commit",
    CommitFiles=Table.SelectRows(Files,each Text.StartsWith([Name],"commit-") and Text.EndsWith([Name],".json")),
    Manifests=List.Buffer(List.Transform(Table.ToRecords(CommitFiles),(f)=>
        let M=Json.Document(f[Content]),
            Valid=M[SchemaVersion]=1 and M[Status]="committed" and
                f[Name]="commit-" & M[BatchID] & ".json" and
                M[Validation][Keysets]=true and M[Validation][Metadata]=true and M[Validation][RefreshGeneration]=true and VerifyRaw(M),
            At=DateTimeZone.FromText(M[ObservedAtUTC])
        in if Valid then [BatchID=M[BatchID],At=At,Sources=M[Sources]] else error "Invalid commit manifest")),
    Ordered=List.Sort(Manifests,(a,b)=>if a[At]<b[At] then -1 else if a[At]>b[At] then 1 else Value.Compare(a[BatchID],b[BatchID])),
    Unique=List.Count(List.Distinct(List.Transform(Ordered,each [BatchID])))=List.Count(Ordered),
    Result=List.Accumulate(if Unique then Ordered else error "Duplicate batch identity",#table(StoredType,{}),(History,Batch)=>
        List.Accumulate(Batch[Sources],History,(Prior,S)=>
            let
                Count=S[PageCount],
                ValidCount=Value.Is(Count,type number) and Count>0 and Number.RoundDown(Count)=Count,
                Pages=if ValidCount then List.Transform(List.Numbers(0,Count),(i)=>
                    let Name="uncommitted-" & Batch[BatchID] & "-" & S[ChunkTable] & "-" & Text.From(i,"en-US") & ".json",
                        Rows=Json.Document(ReadFile(Name))
                    in if Value.Is(Rows,type list) and List.Count(Rows)>0 then Table.FromRecords(Rows) else error "Invalid committed page") else error "Invalid page count",
                Raw=Table.Combine(Pages),
                Normal=Table.TransformColumnNames(Raw,each if Text.StartsWith(_,"[") and Text.EndsWith(_, "]") then Text.Middle(_,1,Text.Length(_)-2) else _),
                Incoming=fnReconstructMetadata(Normal,S[KeyColumn]),
                Keys=Incoming[SourceID], Expected=S[ExpectedKeys],
                Complete=List.Count(Keys)=S[ExpectedRecords] and List.Count(List.Distinct(Expected))=List.Count(Expected) and
                    List.Sort(Keys)=List.Sort(Expected),
                Retained=fnRetainSourceObservations(Prior,Incoming,S[Source],Batch[BatchID],Batch[At],Complete)
            in Retained))
in
    if List.IsEmpty(Ordered) then error "No accepted history commit; preserve previous model state" else Result
