// Pending only. Read frozen archived rows; never evaluate the provider query.
(CaptureRows as list, Sidecar as record) as table =>
let
    ChunkType=type table [OpenAlexWorkID=text,ChunkIndex=Int64.Type,ChunkCount=Int64.Type,
        MetadataCharacters=Int64.Type,Encoding=text,MetadataChunk=text],
    Normalize=(R as record) as record => Record.FromList(Record.FieldValues(R),
        List.Transform(Record.FieldNames(R),each if Text.EndsWith(_, "]") then
            Text.BeforeDelimiter(Text.AfterDelimiter(_, "[", {0,RelativePosition.FromEnd}),"]") else _)),
    Rows=List.Buffer(List.Transform(CaptureRows,Normalize)),
    Specs=Sidecar[responses],
    Indices=List.Sort(List.Distinct(List.Transform(Rows,each [RawResponseIndex]))),
    Guard=List.Count(Specs)>0 and Indices=List.Numbers(0,List.Count(Specs)) and
        List.Count(Rows)=Sidecar[row_count],
    // Python ensure_ascii=false contract: escape only JSON syntax/control text.
    // Character-wise construction distinguishes literal backslashes from escapes.
    Q=Character.FromNumber(34), B=Character.FromNumber(92),
    Quote=(T as text) as text => Q&Text.Combine(List.Transform(Text.ToList(T),(C)=>let
        N=Character.ToNumber(C)
        in if N=34 then B&Q else if N=92 then B&B
        else if N=8 then B&"b" else if N=9 then B&"t" else if N=10 then B&"n"
        else if N=12 then B&"f" else if N=13 then B&"r"
        else if N<32 then B&"u"&Text.Lower(Binary.ToText(#binary({0,N}),BinaryEncoding.Hex))
        else C))&Q,
    JSON=(V as any) as text => if V=null then "null"
        else if Value.Is(V,type text) then Quote(V)
        else if Value.Is(V,type logical) then if V then "true" else "false"
        else if Value.Is(V,type number) then if Number.RoundDown(V)=V then Number.ToText(V,"0","en-US")
            else error "Noninteger envelope scalar outside retained contract"
        else if Value.Is(V,type record) then "{"&Text.Combine(List.Transform(Record.FieldNames(V),
            (N)=>Quote(N)&":"&@JSON(Record.Field(V,N))),",")&"}"
        else if Value.Is(V,type list) then "["&Text.Combine(List.Transform(V,each @JSON(_)),",")&"]"
        else error "Unsupported retained JSON value",
    Sorted=(V as any) as any => if Value.Is(V,type record) then let
        Names=List.Sort(Record.FieldNames(V),Comparer.Ordinal)
        in Record.FromList(List.Transform(Names,each @Sorted(Record.Field(V,_))),Names)
        else if Value.Is(V,type list) then List.Transform(V,each @Sorted(_)) else V,
    Schema=(D as record) as record =>
        if D[Kind]="record" then [type="object",fields=Record.FromList(
            List.Transform(D[Fields],each @Schema([Schema])),List.Transform(D[Fields],each [Name]))]
        else if D[Kind]="list" then let
            Variants=List.Distinct(List.Transform(D[Items],each JSON(Sorted(@Schema(_))))),
            Ordered=List.Sort(Variants,Comparer.Ordinal)
            in [type="array",variants=List.Transform(Ordered,each Json.Document(_))]
        else [type=Record.Field([null="null",text="string",logical="boolean",number="number"],D[Kind])],
    Prepared=if Guard then List.Transform(Specs,(S)=>let
        Group=List.Sort(List.Select(Rows,each [RawResponseIndex]=S[index]),
            (A,B)=>Number.Sign(A[RawChunkIndex]-B[RawChunkIndex])),
        HeaderNames=Record.FieldNames(S[headers]),
        Exact=List.Count(Group)=S[headers][RawChunkCount] and
            List.Transform(Group,each [RawChunkIndex])=List.Numbers(0,S[headers][RawChunkCount]) and
            List.AllTrue(List.Transform(Group,each Record.SelectFields(_,HeaderNames)=S[headers])),
        Raw64=if Exact then Text.Combine(List.Transform(Group,each [RawPayloadBase64]))
            else error "Frozen raw header/chunk drift",
        Raw=Binary.Buffer(Binary.FromText(Raw64,BinaryEncoding.Base64)),
        Descriptor=Binary.Buffer(Binary.FromText(Text.Combine(List.Transform(Group,each [RawSchemaBase64])),BinaryEncoding.Base64)),
        Lengths=Binary.Length(Raw)=S[headers][RawByteCount] and Binary.Length(Descriptor)=S[headers][RawSchemaByteCount],
        Payload=if Lengths and S[headers][RawStatus]="success" then Json.Document(Raw) else null,
        Work=if Payload=null then null else Record.FieldOrDefault(Payload,"id",null),
        Identity=if Payload=null then true else Work=S[work_id] and Record.FieldOrDefault(Payload,"doi",null)=S[returned_doi],
        Envelope=if Lengths and Identity and S[headers][RawStatus]="success" and S[final] then
            [kind="openalex_retained_observation_v1",source="OpenAlex",
             requested_doi=S[headers][RequestedDOI],work_id=Work,observed_utc=S[headers][RawAcquiredUTC],
             input_sha256=Sidecar[input_sha256],http_status=200,
             request=[origin="https://api.openalex.org",relative_path="works/https://doi.org/"&S[headers][RequestedDOI]],
             raw_response_base64=Raw64,raw_response_sha256=S[raw_response_sha256],
             raw_byte_count=Binary.Length(Raw),observed_schema=Schema(Json.Document(Descriptor))]
            else if Lengths and Identity then null else error "Frozen binary/schema/identity drift",
        Encoded=if Envelope=null then "" else Text.Upper(Binary.ToText(Text.ToBinary(JSON(Envelope),TextEncoding.Utf8),BinaryEncoding.Hex)),
        Hex=if Envelope=null or Text.Length(Encoded)=S[expected_metadata_characters] then Encoded
            else error "Pending envelope serialization length differs from retained reference",
        Count=Number.RoundUp(Text.Length(Hex)/24000),
        Chunks=if Envelope=null then {} else List.Transform(List.Numbers(0,Count),(I)=>
            [OpenAlexWorkID=Work,ChunkIndex=I,ChunkCount=Count,MetadataCharacters=Text.Length(Hex),
             Encoding="UTF8-HEX",MetadataChunk=Text.Range(Hex,I*24000,List.Min({24000,Text.Length(Hex)-I*24000}))])
        // Force checks for retry/not-found rows too, even though they emit no work.
        in if Lengths and Identity then Chunks else error "Raw attempt drift")
        else error "Frozen raw response scope drift",
    Output=List.Combine(Prepared)
in Table.FromRecords(Output,ChunkType)
