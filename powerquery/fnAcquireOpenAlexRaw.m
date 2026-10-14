// Bounded native binary acquisition only; no registry or accepted-source writes.
// Kind/Fields/Items schema shape matches the existing raw-envelope contract.
(DOIs as list, InputSHA256 as text) as table =>
let
    Valid=List.Count(DOIs)>0 and List.Count(DOIs)<=50 and
        List.Count(List.Distinct(DOIs))=List.Count(DOIs) and
        List.AllTrue(List.Transform(DOIs,each Value.Is(_,type text) and
            Text.StartsWith(_,"10.") and Text.Contains(_,"/") and Text.Lower(Text.Trim(_))=_)) and
        Text.Length(InputSHA256)=64 and Text.Select(InputSHA256,{"0".."9","a".."f"})=InputSHA256,
    Scope=if Valid then List.Buffer(DOIs) else error "Invalid frozen OpenAlex acquisition scope",
    Describe=(V as any) as record =>
        if V=null then [Kind="null"]
        else if Value.Is(V,type record) then [Kind="record",Fields=List.Transform(Record.FieldNames(V),
            (N)=>[Name=N,Schema=@Describe(Record.Field(V,N))])]
        else if Value.Is(V,type list) then [Kind="list",Items=List.Distinct(List.Transform(V,each @Describe(_)))]
        else if Value.Is(V,type text) then [Kind="text"]
        else if Value.Is(V,type logical) then [Kind="logical"]
        else if Value.Is(V,type number) then [Kind="number"] else [Kind="other"],
    CleanDOI=(V as any) as nullable text => if not Value.Is(V,type text) then null else let
        Lower=Text.Lower(Text.Trim(V)),Prefixes={"https://doi.org/","http://doi.org/","doi:"},
        Prefix=List.First(List.Select(Prefixes,each Text.StartsWith(Lower,_)),null)
        in if Prefix=null then Lower else Text.Trim(Text.Range(Lower,Text.Length(Prefix))),
    Fetch=(DOI as text, Attempt as number, Delay as number) as list => let
        Path="works/https://doi.org/"&Uri.EscapeDataString(DOI),
        Call=try Function.InvokeAfter(()=>Web.Contents("https://api.openalex.org/",
            [RelativePath=Path,Timeout=#duration(0,0,0,45),IsRetry=Attempt>1,
             ManualStatusHandling={404,429,500,502,503,504}]),
            #duration(0,0,0,Delay)),
        Metadata=if Call[HasError] then [] else Value.Metadata(Call[Value]),
        HTTP=if Call[HasError] then null else Record.FieldOrDefault(Metadata,"Response.Status",200),
        Raw=if Call[HasError] then #binary({}) else Binary.Buffer(Call[Value]),
        Length=Binary.Length(Raw),
        Parsed=try Json.Document(Raw),
        Payload=if Parsed[HasError] then null else Parsed[Value],
        Work=if Value.Is(Payload,type record) then Record.FieldOrDefault(Payload,"id",null) else null,
        ReturnedDOI=if Value.Is(Payload,type record) then CleanDOI(Record.FieldOrDefault(Payload,"doi",null)) else null,
        Identity=if Value.Is(Work,type text) then Text.StartsWith(Work,"https://openalex.org/W") and
            Text.Length(Text.Range(Work,Text.Length("https://openalex.org/W")))>0 and Text.Select(Text.Range(Work,Text.Length("https://openalex.org/W")),{"0".."9"})=Text.Range(Work,Text.Length("https://openalex.org/W")) and
            ReturnedDOI=DOI else false,
        Headers=Record.FieldOrDefault(Metadata,"Headers",[]),
        BudgetNames={"X-RateLimit-Limit","X-RateLimit-Remaining","X-RateLimit-Credits-Used","X-RateLimit-Reset","Retry-After"},
        Present=if Value.Is(Headers,type record) then List.Select(BudgetNames,(N)=>
            List.AnyTrue(List.Transform(Record.FieldNames(Headers),each Text.Lower(_)=Text.Lower(N)))) else {},
        Budget=Record.FromList(List.Transform(Present,(N)=>Record.Field(Headers,
            List.First(List.Select(Record.FieldNames(Headers),each Text.Lower(_)=Text.Lower(N))))),Present),
        Credit=try Number.FromText(Text.From(Record.FieldOrDefault(Budget,"X-RateLimit-Credits-Used",null)),"en-US"),
        Cost=if Credit[HasError] then null else Credit[Value],
        Status=if Call[HasError] then "transport_or_auth_error" else
            if Cost<>null and Cost>0 then "budget_mismatch" else
            if Length>16*1024*1024 then "response_too_large" else
            if HTTP=404 then "not_found" else if HTTP=429 then "rate_limited" else
            if List.Contains({500,502,503,504},HTTP) then "unavailable" else
            if HTTP<>200 then "http_error" else if Parsed[HasError] then "invalid_response" else
            if not Identity then "identity_mismatch" else "success",
        Observed=if Length>=0 then DateTimeZone.ToText(DateTimeZone.UtcNow(),"yyyy-MM-dd'T'HH:mm:ss.fffffff'Z'","en-US")
            else error "Raw byte acquisition incomplete",
        Schema=if Parsed[HasError] then [Kind="invalid-json"] else Describe(Payload),
        Current=[RequestedDOI=DOI,RawAttempt=Attempt,RawEndpoint="https://api.openalex.org/"&Path,
            RawRequestJSON=Text.FromBinary(Json.FromValue([method="GET",relative_path=Path,
                requested_doi=DOI,input_sha256=InputSHA256,credential_mode="Anonymous",operation="singleton"]),TextEncoding.Utf8),
            RawAcquiredUTC=Observed,RawHTTPStatus=HTTP,
            RawStatus=if Text.Length(Observed)>0 then Status else error "Missing raw capture time",RawByteCount=Length,
            RawBinary=Raw,RawSchemaJSON=Text.FromBinary(Json.FromValue(Schema),TextEncoding.Utf8),
            RawBudgetHeadersJSON=Text.FromBinary(Json.FromValue(Budget),TextEncoding.Utf8)],
        HasRetryHint=Record.HasFields(Budget,"Retry-After"),
        RetryHint=try Number.FromText(Text.From(Record.FieldOrDefault(Budget,"Retry-After",null)),"en-US"),
        HintValid=if not HasRetryHint then true else if RetryHint[HasError] then false
            else Value.Is(RetryHint[Value],type number) and RetryHint[Value]>=0 and RetryHint[Value]<=30,
        NextDelay=if HasRetryHint and HintValid then List.Max({1,RetryHint[Value]}) else Number.Power(2,Attempt),
        Retry=List.Contains({"rate_limited","unavailable"},Current[RawStatus]) and Attempt<3 and HintValid
        // Keep every returned retry body; failure never clears accepted data.
        in {Current}&(if Retry then @Fetch(DOI,Attempt+1,NextDelay) else {}),
    Pass=List.Accumulate(Scope,[Stopped=false,Responses={}],(State,DOI)=>
        if State[Stopped] then State else let
            Attempts=List.Buffer(Fetch(DOI,1,1)),Last=List.Last(Attempts),
            Stop=not List.Contains({"success","not_found"},Last[RawStatus])
        in [Stopped=Stop,Responses=State[Responses]&Attempts]),
    Responses=List.Buffer(Pass[Responses]),
    Rows=List.Combine(List.Transform(List.Positions(Responses),(R)=>let
        V=Responses{R},P=Binary.ToText(V[RawBinary],BinaryEncoding.Base64),
        SchemaBytes=Text.ToBinary(V[RawSchemaJSON],TextEncoding.Utf8),S=Binary.ToText(SchemaBytes,BinaryEncoding.Base64),
        Count=List.Max({1,Number.RoundUp(Text.Length(P)/24000),Number.RoundUp(Text.Length(S)/24000)})
        in List.Transform(List.Numbers(0,Count),(I)=>[RequestedDOI=V[RequestedDOI],RawResponseIndex=R,RawAttempt=V[RawAttempt],
            RawEndpoint=V[RawEndpoint],RawRequestJSON=V[RawRequestJSON],RawAcquiredUTC=V[RawAcquiredUTC],
            RawHTTPStatus=V[RawHTTPStatus],RawStatus=V[RawStatus],RawByteCount=V[RawByteCount],
            RawSchemaByteCount=Binary.Length(SchemaBytes),RawChunkIndex=I,RawChunkCount=Count,
            RawPayloadBase64=Text.Range(P,List.Min({Text.Length(P),I*24000}),List.Min({24000,List.Max({0,Text.Length(P)-I*24000})})),
            RawSchemaBase64=Text.Range(S,List.Min({Text.Length(S),I*24000}),List.Min({24000,List.Max({0,Text.Length(S)-I*24000})})),
            RawBudgetHeadersJSON=V[RawBudgetHeadersJSON]]))),
    Result=Table.FromRecords(Rows,type table [RequestedDOI=text,RawResponseIndex=Int64.Type,RawAttempt=Int64.Type,
        RawEndpoint=text,RawRequestJSON=text,RawAcquiredUTC=text,RawHTTPStatus=nullable number,RawStatus=text,
        RawByteCount=Int64.Type,RawSchemaByteCount=Int64.Type,RawChunkIndex=Int64.Type,RawChunkCount=Int64.Type,
        RawPayloadBase64=text,RawSchemaBase64=text,RawBudgetHeadersJSON=text])
in Table.Buffer(Result)
