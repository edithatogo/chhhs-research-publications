// Add source context after canonical reconciliation; preserve membership and
// all original bibliography/review fields. Provider rows must already be accepted.
(Publications as table, Enrichment as table) as record =>
let
    Fields={"CitationCount_OpenAlex","OpenAccessStatus_OpenAlex","OAUrl_OpenAlex"},
    Times=List.Transform(Fields,each _&"_ObservedUTC"),
    CleanDOI=(V as any) as nullable text => if not Value.Is(V,type text) then null else let
        Lower=Text.Lower(Text.Trim(V)),Prefixes={"https://doi.org/","http://doi.org/","https://dx.doi.org/","http://dx.doi.org/","doi:"},
        Prefix=List.First(List.Select(Prefixes,each Text.StartsWith(Lower,_)),null),
        D=Text.Trim(if Prefix=null then Lower else Text.Range(Lower,Text.Length(Prefix)))
        in if Text.StartsWith(D,"10.") and Text.Contains(D,"/") then D else null,
    UTC=(V as any) as nullable datetimezone => if V=null then null else let
        T=DateTimeZone.From(V)
        in if DateTimeZone.ZoneHours(T)=0 and DateTimeZone.ZoneMinutes(T)=0 then T else error "UTC provider time required",
    Keys=Table.Column(Publications,"CanonicalKey"),
    KeyValid=List.AllTrue(List.Transform(Keys,each Value.Is(_,type text) and Text.Trim(_)<>"")) and
        List.Count(List.Distinct(Keys))=List.Count(Keys),
    Provider=Table.Buffer(Table.TransformColumns(Enrichment,{{"DOI",CleanDOI,type text}})),
    ProviderValid=List.NonNullCount(Provider[DOI])=Table.RowCount(Provider) and
        Table.RowCount(Table.Distinct(Provider,{"DOI"}))=Table.RowCount(Provider) and
        Table.RowCount(Table.Distinct(Provider,{"OpenAlexWorkID"}))=Table.RowCount(Provider),
    Incoming=(D as nullable text) as nullable record => if D=null then null else let
        Matches=Table.SelectRows(Provider,each [DOI]=D)
        in if Table.IsEmpty(Matches) then null else Matches{0},
    Merged=List.Transform(Table.ToRecords(if KeyValid and ProviderValid then Publications else error "Ambiguous canonical/provider identity"),(P)=>let
        D=CleanDOI(Record.FieldOrDefault(P,"DOI",null)),I=Incoming(D),
        Acc=List.Accumulate(Fields,[Row=P,Provenance={}],(A,F)=>if I=null then A else let
            V=Record.Field(I,F),Old=Record.FieldOrDefault(A[Row],F,null),TF=F&"_ObservedUTC",
            PriorTime=UTC(Record.FieldOrDefault(A[Row],TF,null)),At=UTC(I[OpenAlexObservedUTC]),
            Reason=if V=null then "preserve_missing" else if PriorTime<>null and At<PriorTime then "preserve_newer"
                else if PriorTime=At and Old<>null and Old<>V then error "Same-observation provider conflict" else "source_observation",
            Next=if Reason="source_observation" then Record.Combine({A[Row],Record.FromList({V,At},{F,TF})}) else A[Row],
            Proof=[CanonicalKey=P[CanonicalKey],Field=F,Source="OpenAlex",ProviderWorkID=I[OpenAlexWorkID],DOI=D,
                AttemptObservedUTC=At,OriginalValue=Old,IncomingValue=V,SelectedValue=Record.FieldOrDefault(Next,F,null),
                SelectedObservedUTC=Record.FieldOrDefault(Next,TF,null),Decision=Reason]
            in if At=null or At>DateTimeZone.UtcNow() then error "Invalid provider observation time" else
                [Row=Next,Provenance=A[Provenance]&{Proof}])
        in Acc),
    Columns=List.Union({Table.ColumnNames(Publications),Fields,Times}),
    Rows=Table.FromRecords(List.Transform(Merged,each [Row]),Columns,MissingField.UseNull),
    Typed=Table.TransformColumnTypes(Rows,{{"CitationCount_OpenAlex",Int64.Type},{"OpenAccessStatus_OpenAlex",type text},{"OAUrl_OpenAlex",type text}}&
        List.Transform(Times,each {_,type datetimezone})),
    Proofs=Table.FromRecords(List.Combine(List.Transform(Merged,each [Provenance])),
        {"CanonicalKey","Field","Source","ProviderWorkID","DOI","AttemptObservedUTC","OriginalValue","IncomingValue","SelectedValue","SelectedObservedUTC","Decision"},MissingField.UseNull)
in if Table.Column(Typed,"CanonicalKey")=Keys then [Publications=Typed,Provenance=Proofs] else error "Canonical membership changed"
