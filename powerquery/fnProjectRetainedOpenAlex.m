// Called only with OpenAlex rows from the existing committed history reader.
// MetadataJSON retains full response bytes/schema; no external API/key is used.
(Observations as table) as table =>
let
    OutputType=type table [OpenAlexWorkID=text, DOI=text,
        CitationCount_OpenAlex=nullable number, OpenAccessStatus_OpenAlex=nullable text,
        OAUrl_OpenAlex=nullable text, OpenAlexObservedUTC=datetimezone],
    CleanDOI=(Value as any) as nullable text =>
        if not Value.Is(Value,type text) then null else let
            Lower=Text.Lower(Text.Trim(Value)),
            Prefixes={"https://doi.org/","http://doi.org/","https://dx.doi.org/","http://dx.doi.org/","doi:"},
            Prefix=List.First(List.Select(Prefixes,each Text.StartsWith(Lower,_)),null),
            DOI=Text.Trim(if Prefix=null then Lower else Text.Range(Lower,Text.Length(Prefix)))
        in if Text.StartsWith(DOI,"10.") and Text.Contains(DOI,"/") then DOI else null,
    Rows=List.Transform(Table.ToRecords(Observations),(R)=>let
        Envelope=Json.Document(R[MetadataJSON]),
        Bytes=Binary.FromText(Envelope[raw_response_base64],BinaryEncoding.Base64),
        Payload=Json.Document(Bytes), Work=Payload[id], DOI=CleanDOI(Payload[doi]),
        Observed=DateTimeZone.FromText(Envelope[observed_utc]),
        WorkPrefix="https://openalex.org/W",
        Suffix=if Value.Is(Work,type text) and Text.StartsWith(Work,WorkPrefix)
            then Text.Range(Work,Text.Length(WorkPrefix)) else "",
        Identity=Envelope[kind]="openalex_retained_observation_v1" and Envelope[source]="OpenAlex" and
            R[Source]="OpenAlex" and R[SourceID]=Work and Envelope[work_id]=Work and
            Suffix<>"" and Text.Select(Suffix,{"0".."9"})=Suffix and
            DOI<>null and DOI=Envelope[requested_doi] and Envelope[http_status]=200 and
            Binary.Length(Bytes)=Envelope[raw_byte_count] and
            DateTimeZone.ZoneHours(Observed)=0 and DateTimeZone.ZoneMinutes(Observed)=0,
        Count=Record.FieldOrDefault(Payload,"cited_by_count",null),
        CountValid=if Count=null then true else if not Value.Is(Count,type number) then false
            else Count>=0 and Number.RoundDown(Count)=Count,
        OA=Record.FieldOrDefault(Payload,"open_access",null),
        OAValid=OA=null or Value.Is(OA,type record),
        Status=if OA=null then null else Record.FieldOrDefault(OA,"oa_status",null),
        URL=if OA=null then null else Record.FieldOrDefault(OA,"oa_url",null),
        TextValid=(V as any) as logical => V=null or Value.Is(V,type text)
    in if Identity and CountValid and OAValid and TextValid(Status) and TextValid(URL) then
        [OpenAlexWorkID=Work,DOI=DOI,CitationCount_OpenAlex=Count,
         OpenAccessStatus_OpenAlex=Status,OAUrl_OpenAlex=URL,OpenAlexObservedUTC=Observed]
        else error "Rejected OpenAlex projection; preserve the previous accepted generation"),
    Result=Table.FromRecords(Rows,OutputType),
    Unique=Table.RowCount(Table.Distinct(Result,{"OpenAlexWorkID"}))=Table.RowCount(Result) and
        Table.RowCount(Table.Distinct(Result,{"DOI"}))=Table.RowCount(Result)
in if Unique then Result else error "Conflicting OpenAlex work/DOI identities"
