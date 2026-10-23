// Current native review state; registered identity material contains no review values.
(Source as table, SiteUrl as text, ListId as text, Material as table, RegisteredGeneration as text) as table =>
let
    Lists = Table.SelectRows(Source, each [Id] = ListId),
    Native = if Table.RowCount(Lists) = 1 then Lists{0}[Items] else error "Exact relationship list missing or duplicated",
    Required = {"ID", "RelationshipKey", "RelationshipType", "FromKey", "ToKey", "AwardID", "EvidenceURL", "Confidence", "ReviewStatus", "Modified"},
    Missing = List.Difference(Required, Table.ColumnNames(Native)),
    Buffered = if List.IsEmpty(Missing) then Table.Buffer(Native) else error "Relationship source column drift",
    Observed = DateTimeZone.ToText(DateTimeZone.FixedUtcNow(), [Format = "yyyy-MM-ddTHH:mm:ss.fffffffzzz", Culture = "en-US"]),
    AsText = (v as any) as nullable text => if Value.Is(v, type text) then v else null,
    JsonText = (v as any) as nullable text => try Text.FromBinary(Json.FromValue(v), TextEncoding.Utf8) otherwise null,
    LinkText = (v as any) as nullable text =>
        if Value.Is(v, type text) then Text.Trim(v)
        else if Value.Is(v, type record) then
            let u = Record.FieldOrDefault(v, "Url", null) in if Value.Is(u, type text) then Text.Trim(u) else null
        else null,
    ETag = (r as record) as nullable text =>
        let m = Record.FieldOrDefault(r, "__metadata", []), vm = Value.Metadata(r),
            candidates = {Record.FieldOrDefault(r, "@odata.etag", null), Record.FieldOrDefault(r, "ETag", null),
                if Value.Is(m, type record) then Record.FieldOrDefault(m, "etag", null) else null,
                Record.FieldOrDefault(vm, "etag", null), Record.FieldOrDefault(vm, "ETag", null)},
            actual = List.Select(candidates, each Value.Is(_, type text) and _ <> "")
        in if List.IsEmpty(actual) then null else actual{0},
    Prepared = Table.FromRecords(List.Transform(Table.ToRecords(Buffered), (r) =>
        let evidence = r[EvidenceURL], tag = ETag(r) in [
            NativeItemID = r[ID], RelationshipKey = AsText(r[RelationshipKey]),
            RelationshipType = AsText(r[RelationshipType]), FromKey = AsText(r[FromKey]),
            ToKey = AsText(r[ToKey]), AwardID = AsText(r[AwardID]),
            EvidenceURL = LinkText(evidence), EvidenceURLRawJSON = JsonText(evidence),
            Confidence = AsText(r[Confidence]), ConfidenceRawJSON = JsonText(r[Confidence]),
            ReviewStatusRaw = AsText(r[ReviewStatus]), ReviewStatusRawJSON = JsonText(r[ReviewStatus]),
            NativeModifiedRawJSON = JsonText(r[Modified]), NativeETag = tag,
            NativeETagAvailability = if tag = null then "Not exposed by SharePoint.Tables; not inferred" else "Native connector metadata",
            NativeVersionRawJSON = JsonText(Record.FieldOrDefault(r, "Version", null)),
            NativeSourceURL = SiteUrl & "/_layouts/15/listform.aspx?PageType=4&ListId=" & ListId & "&ID=" & Text.From(r[ID], "en-US"),
            SourceReadUTC = Observed, IdentityGeneration = RegisteredGeneration,
            SourceColumns = Text.Combine(Table.ColumnNames(Buffered), "|")
        ]), type table [NativeItemID = Int64.Type, RelationshipKey = nullable text,
            RelationshipType = nullable text, FromKey = nullable text, ToKey = nullable text,
            AwardID = nullable text, EvidenceURL = nullable text, EvidenceURLRawJSON = nullable text,
            Confidence = nullable text, ConfidenceRawJSON = nullable text,
            ReviewStatusRaw = nullable text, ReviewStatusRawJSON = nullable text,
            NativeModifiedRawJSON = nullable text, NativeETag = nullable text,
            NativeETagAvailability = text, NativeVersionRawJSON = nullable text,
            NativeSourceURL = text, SourceReadUTC = text, IdentityGeneration = text, SourceColumns = text]),
    NativeIDs = Prepared[NativeItemID],
    Complete = if List.NonNullCount(NativeIDs) = List.Count(NativeIDs) and List.Count(List.Distinct(NativeIDs)) = List.Count(NativeIDs)
        then Prepared else error "Native relationship item identity missing or duplicated",
    TypedKeys = {"RelationshipKey", "RelationshipType", "FromKey", "ToKey", "AwardID", "EvidenceURL"},
    CrossKeys = {"FromKey", "ToKey", "AwardID"},
    MapFields = {"PublicationCanonicalKey", "AwardSourceID"},
    UniqueMaterial = if Table.RowCount(Material) = Table.RowCount(Table.Distinct(Material, TypedKeys))
        then Material else error "Duplicate registered relationship identity",
    Cross = Table.Distinct(Table.SelectColumns(UniqueMaterial, List.Combine({CrossKeys, MapFields}))),
    CrossCounts = Table.Group(Cross, CrossKeys, {{"N", each Table.RowCount(_), Int64.Type}}),
    UniqueCross = if List.AllTrue(List.Transform(CrossCounts[N], each _ = 1)) then Cross else error "Ambiguous model identity crosswalk",
    Joined = Table.NestedJoin(Complete, CrossKeys, UniqueCross, CrossKeys, "Identity", JoinKind.LeftOuter),
    WithIdentityCount = Table.AddColumn(Joined, "IdentityMatchCount", each Table.RowCount([Identity]), Int64.Type),
    Expanded = Table.ExpandTableColumn(WithIdentityCount, "Identity", MapFields, MapFields),
    TypedJoin = Table.NestedJoin(Expanded, TypedKeys, UniqueMaterial, TypedKeys, "TypedIdentity", JoinKind.LeftOuter),
    WithTypedCount = Table.AddColumn(TypedJoin, "TypedBindingCount", each Table.RowCount([TypedIdentity]), Int64.Type),
    WithoutNested = Table.RemoveColumns(WithTypedCount, {"TypedIdentity"}),
    KeyCounts = Table.Group(Complete, {"RelationshipKey"}, {{"NativeKeyCount", each Table.RowCount(_), Int64.Type}}),
    WithKeyCounts = Table.ExpandTableColumn(Table.NestedJoin(WithoutNested, {"RelationshipKey"}, KeyCounts, {"RelationshipKey"}, "KeyCount", JoinKind.LeftOuter), "KeyCount", {"NativeKeyCount"}),
    Classified = Table.AddColumn(WithKeyCounts, "TypedAdmissionState", each
        let raw = [ReviewStatusRaw], status = if raw <> null and raw = Text.Trim(raw) then Text.Lower(raw, "en-US") else null in
            if [IdentityMatchCount] <> 1 then "unresolved_identity"
            else if [TypedBindingCount] <> 1 or [NativeKeyCount] <> 1 then "unclassified"
            else if [RelationshipType] = "candidate_award_match" and [Confidence] = "candidate" and List.Contains({"needs review", "reviewed"}, status) then "candidate"
            else if [RelationshipType] = "funded_by_award" and [Confidence] = "confirmed" and status = "reviewed" then "confirmed_reviewed"
            else "unclassified", type text),
    Result = if Table.RowCount(Classified) = Table.RowCount(Complete) then Classified else error "Relationship consumer multiplied or dropped source rows"
in
    Result
