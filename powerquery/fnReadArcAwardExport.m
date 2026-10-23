// Retained awards only. Caller supplies one exact accepted export folder.
(Files as table, ExpectedRun as text, ExpectedSourceRun as text, ExpectedRows as number) as table =>
let
    Fail = (Message as text) => error Error.Record("ARC award export", Message, null),
    Fields = {"RecordKind", "Source", "SourceID", "AwardCode", "Title", "Funder", "URL", "Description", "Amount", "Status", "RetrievedUTC", "EvidenceHash"},
    Names = Table.Column(Files, "Name"),
    File = (Name as text) as binary =>
        let Matches = Table.SelectRows(Files, each [Name] = Name)
        in if Table.RowCount(Matches) = 1 then Binary.Buffer(Matches{0}[Content]) else Fail("Missing or duplicate export file"),
    Manifest = Json.Document(File("manifest.json")),
    Valid = Manifest[format] = "rims-arc-award-export-v1"
        and Manifest[record_kind] = "awards_only"
        and Manifest[canonical_opportunity_admission] = false
        and Manifest[lifecycle_semantics_proven] = false
        and Manifest[run] = ExpectedRun and Manifest[source_run] = ExpectedSourceRun
        and Manifest[source_total] = ExpectedRows and ExpectedRows > 0
        and Number.RoundDown(ExpectedRows) = ExpectedRows
        and Manifest[rows_per_page] = 500
        and Manifest[page_count] = Number.RoundUp(ExpectedRows / 500)
        and Manifest[fields] = Fields,
    Pages = if Valid then {1..Manifest[page_count]} else Fail("Export identity or contract mismatch"),
    ExpectedNames = List.Combine({{"manifest.json"}, List.Combine(List.Transform(Pages,
        each {"awards-page-" & Text.From(_, "en-US") & ".json", "awards-page-" & Text.From(_, "en-US") & ".csv"}))}),
    Inventory = if List.Sort(Names) = List.Sort(ExpectedNames) then true else Fail("Export inventory mismatch"),
    Declared = Table.FromRecords(Manifest[files]),
    DeclaredNames = Table.Column(Declared, "name"),
    DeclaredValid = List.Sort(DeclaredNames) = List.Sort(List.RemoveItems(ExpectedNames, {"manifest.json"})),
    Source = Json.Document(Binary.FromText(Manifest[source_manifest_base64], BinaryEncoding.Base64)),
    SourceValid = Source[run] = ExpectedSourceRun and Source[source_total] = ExpectedRows
        and Source[page_count] = Manifest[page_count],
    ReadPage = (Page as number) as list =>
        let
            Stem = "awards-page-" & Text.From(Page, "en-US"),
            Rows = Json.Document(File(Stem & ".json")),
            Count = if Page < Manifest[page_count] then 500 else ExpectedRows - (Page - 1) * 500,
            Declarations = Table.SelectRows(Declared, each [name] = Stem & ".json" or [name] = Stem & ".csv"),
            CountsValid = Table.RowCount(Declarations) = 2 and List.AllTrue(List.Transform(Table.Column(Declarations, "rows"), each _ = Count)),
            RowsValid = Value.Is(Rows, type list) and List.Count(Rows) = Count and CountsValid
                and List.AllTrue(List.Transform(Rows, (Row) => Value.Is(Row, type record)
                    and List.Sort(Record.FieldNames(Row)) = List.Sort(Fields)
                    and List.AllTrue(List.Transform(Record.FieldValues(Row), each Value.Is(_, type text)))
                    and Row[RecordKind] = "Award" and Row[Source] = "arc" and Text.Trim(Row[SourceID]) <> ""))
        in if RowsValid then Rows else Fail("Invalid award page or row"),
    Rows = if Inventory and DeclaredValid and SourceValid then List.Combine(List.Transform(Pages, ReadPage)) else Fail("Incomplete committed export"),
    Result = Table.Buffer(Table.FromRecords(Rows, Fields, MissingField.Error)),
    Keys = Table.Column(Result, "SourceID"),
    Checked = if Table.RowCount(Result) = ExpectedRows and List.Count(List.Distinct(Keys)) = ExpectedRows
        then Table.TransformColumnTypes(Result, List.Transform(Fields, each {_, type text}))
        else Fail("Missing or duplicate award identities")
in
    Checked
