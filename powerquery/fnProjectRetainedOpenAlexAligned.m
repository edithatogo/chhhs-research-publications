// Add compatible fields to the existing validated source; no provider calls.
// Limits must come from the exact qualified physical destination schema.
(Observations as table, Limits as record) as table =>
let
    Base=fnProjectRetainedOpenAlex(Observations),
    Names={"FunderNames","GrantIDs","MeSHHeadings","AuthorKeywords","AffiliationsRaw"},
    LimitValid=List.AllTrue(List.Transform(Names,(N)=>let V=Record.FieldOrDefault(Limits,N,null)
        in Value.Is(V,type number) and V>0 and Number.RoundDown(V)=V)),
    Rows=(P as record,N as text) as list => let V=Record.FieldOrDefault(P,N,null)
        in if V=null then {} else if Value.Is(V,type list) and List.AllTrue(List.Transform(V,each Value.Is(_,type record)))
        then V else error "OpenAlex aligned list schema drift",
    Joined=(Values as list) as nullable text =>
        if not List.AllTrue(List.Transform(Values,each _=null or Value.Is(_,type text))) then error "OpenAlex aligned text schema drift"
        else let Kept=List.Distinct(List.Select(Values,each _<>null and Text.Trim(_)<>""))
        in if List.IsEmpty(Kept) then null else Text.Combine(Kept,"; "),
    Additional=List.Transform(Table.ToRecords(Observations),(R)=>let
        E=Json.Document(R[MetadataJSON]),P=Json.Document(Binary.FromText(E[raw_response_base64],BinaryEncoding.Base64)),
        Funders=Rows(P,"funders"),Awards=Rows(P,"awards"),Legacy=Rows(P,"grants"),
        Authors=Rows(P,"authorships"),
        Affiliations=List.Combine(List.Transform(Authors,(A)=>let Raw=Record.FieldOrDefault(A,"raw_affiliation_strings",null),
            Texts=if Raw=null then {} else if Value.Is(Raw,type list) then Raw else error "Invalid raw affiliation strings"
            in Texts & List.Transform(Rows(A,"affiliations"),each Record.FieldOrDefault(_,"raw_affiliation_string",null)))),
        Values=[
            FunderNames=Joined(List.Transform(Funders,each Record.FieldOrDefault(_,"display_name",null)) &
                List.Transform(Awards & Legacy,each Record.FieldOrDefault(_,"funder_display_name",null))),
            GrantIDs=Joined(List.Transform(Awards,each Record.FieldOrDefault(_,"funder_award_id",null)) &
                List.Transform(Legacy,each Record.FieldOrDefault(_,"award_id",null))),
            MeSHHeadings=Joined(List.Transform(Rows(P,"mesh"),each Record.FieldOrDefault(_,"descriptor_name",null))),
            AuthorKeywords=Joined(List.Transform(Rows(P,"keywords"),each let V=Record.FieldOrDefault(_,"display_name",null)
                in if V=null or V="" then Record.FieldOrDefault(_,"keyword",null) else V)),
            AffiliationsRaw=Joined(Affiliations)],
        Checked=List.Transform(Names,(N)=>let V=Record.Field(Values,N),Max=List.Min({32766,Record.Field(Limits,N)}),
            Oversize=V<>null and Text.Length(V)>Max
            in [Field=N,Value=if Oversize then null else V,
                Diagnostic=if Oversize then [Field=N,Status="projection_rejected_size",Characters=Text.Length(V),Limit=Max] else null]),
        Diagnostics=List.RemoveNulls(List.Transform(Checked,each [Diagnostic])),
        Projected=Record.FromList(List.Transform(Checked,each [Value]),List.Transform(Names,each _ & "_OpenAlex"))
    in Record.Combine({[OpenAlexWorkID=R[SourceID]],Projected,[SourceObservedUTCRaw=E[observed_utc],
        RawResponseSHA256=E[raw_response_sha256],ProjectionDiagnostics=Text.FromBinary(Json.FromValue(Diagnostics),TextEncoding.Utf8)]})),
    ExtraType=type table [OpenAlexWorkID=text,FunderNames_OpenAlex=nullable text,GrantIDs_OpenAlex=nullable text,
        MeSHHeadings_OpenAlex=nullable text,AuthorKeywords_OpenAlex=nullable text,AffiliationsRaw_OpenAlex=nullable text,
        SourceObservedUTCRaw=text,RawResponseSHA256=text,ProjectionDiagnostics=text],
    Extras=if LimitValid then Table.FromRecords(Additional,ExtraType) else error "Qualified physical destination limits required",
    Columns=List.RemoveItems(Table.ColumnNames(Extras),{"OpenAlexWorkID"}),
    JoinedRows=Table.NestedJoin(Base,{"OpenAlexWorkID"},Extras,{"OpenAlexWorkID"},"Aligned",JoinKind.LeftOuter),
    Result=Table.ExpandTableColumn(JoinedRows,"Aligned",Columns,Columns),
    Unique=Table.RowCount(Extras)=Table.RowCount(Base) and Table.RowCount(Table.Distinct(Extras,{"OpenAlexWorkID"}))=Table.RowCount(Extras)
in if Unique and Table.RowCount(Result)=Table.RowCount(Base) then Result else error "Aligned source key/count drift"
