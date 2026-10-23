// Read-only enrichment projection over the already selected canonical universe.
// Caller supplies the exact existing native register, canonical table and read UTC.
// Registered provider fields are preserved; this function does NOT assign ANZSRC
// codes, infer trial absence, replace qualified OA evidence or change membership.
(Registry as table, Canonical as table, ReadUTC as datetimezone, SourceIdentity as record) as record =>
let
    AliasMap = {
        {"NativeItemID", {"ID", "Id"}},
        {"SourceKey", {"SourceKey", "field_1"}},
        {"RegisteredCanonicalKey", {"CanonicalKey", "field_2"}},
        {"PMID", {"PMID", "field_10"}},
        {"ReviewStatus", {"ReviewStatus", "field_17"}},
        {"RegisteredOpenAccessStatus", {"OpenAccessStatus"}},
        {"RegisteredFundingType", {"Funding Type", "Funding_x0020_Type"}},
        {"RegisteredStudyDesign", {"Study Design", "Study_x0020_Design"}},
        {"ProviderResearchField", {"Field of Research", "Field_x0020_of_x0020_Research"}},
        {"RegisteredClinicalTrialID", {"Clinical Trial ID", "Clinical_x0020_Trial_x0020_ID"}},
        {"NativeModified", {"Modified"}}
    },
    ObservedUTC = DateTimeZone.SwitchZone(ReadUTC, 0),
    SiteUrl = SourceIdentity[SiteUrl],
    ListId = SourceIdentity[ListId],
    IdentityValid = Value.Is(SiteUrl, type text) and Value.Is(ListId, type text)
        and SiteUrl = Text.Trim(SiteUrl) and ListId = Text.Trim(ListId)
        and Text.StartsWith(SiteUrl, "https://") and ListId <> "",
    Names = Table.ColumnNames(Registry),
    Resolve = (Aliases as list) as text =>
        let Found = List.Select(Aliases, each List.Contains(Names, _))
        in if List.Count(Found) = 1 then Found{0}
           else error "Missing or ambiguous registered analytics field alias.",
    Resolved = List.Transform(AliasMap, each {_{0}, Resolve(_{1})}),
    Selected = Table.SelectColumns(Registry, List.Transform(Resolved, each _{1}), MissingField.Error),
    Renames = List.Select(List.Transform(Resolved, each {_{1}, _{0}}), each _{0} <> _{1}),
    Renamed = Table.RenameColumns(Selected, Renames, MissingField.Error),
    AsText = (Value as any) as nullable text =>
        if Value = null then null else if Value.Is(Value, type text) then Value
        else error "Unexpected registered analytics field shape; no coercion.",
    TextNames = List.RemoveItems(List.Transform(AliasMap, each _{0}), {"NativeItemID", "NativeModified"}),
    Typed = Table.TransformColumns(Renamed, List.Transform(TextNames, each {_, AsText, type nullable text})),
    Buffered = Table.Buffer(Typed),
    PositivePMID = (Value as nullable text) as logical =>
        Value <> null and Value <> "" and Value = Text.Trim(Value)
        and Text.Select(Value, {"0".."9"}) = Value and not Text.StartsWith(Value, "0"),
    DoraKey = (Value as nullable text) as logical =>
        Value <> null and Text.StartsWith(Value, "DORA:") and Text.Length(Value) > 5
        and not List.AnyTrue(List.Transform({" ", "#(tab)", "#(cr)", "#(lf)"}, each Text.Contains(Value, _))),
    CanonicalKeys = List.Buffer(Table.Column(Canonical, "CanonicalKey")),
    ValidCanonical = Table.RowCount(Canonical) > 0
        and List.Count(List.Distinct(CanonicalKeys)) = List.Count(CanonicalKeys)
        and List.AllTrue(List.Transform(CanonicalKeys, each
            if _ = null or not Value.Is(_, type text) then false
            else if Text.StartsWith(_, "PMID:") then PositivePMID(Text.Range(_, 5))
            else DoraKey(_))),
    SourceKeys = List.RemoveNulls(List.Select(Buffered[SourceKey], each _ <> "")),
    UniqueSourceKeys = List.Count(List.Distinct(SourceKeys)) = List.Count(SourceKeys),
    RegisteredKeys = List.RemoveNulls(Table.SelectRows(Buffered, each [SourceKey] <> null and [SourceKey] <> "")[RegisteredCanonicalKey]),
    UniqueRegisteredKeys = List.Count(List.Distinct(RegisteredKeys)) = List.Count(RegisteredKeys),
    WithIdentity = Table.AddColumn(Buffered, "TypedKey", each
        let S = [SourceKey], K = [RegisteredCanonicalKey], P = [PMID],
            PubSource = PositivePMID(P) and S = "pubmed:" & P,
            NonblankKey = K <> null and K <> "" and K = Text.Trim(K),
            PubKey = NonblankKey and ((Text.StartsWith(K, "PUB:") and Text.Length(K) > 4)
                or (Text.StartsWith(K, "PMID:") and Text.Length(K) > 5)),
            PubKeyAgrees = PubKey and (not Text.StartsWith(K, "PMID:") or K = "PMID:" & P),
            DoraSource = S <> null and Text.StartsWith(S, "dora:") and Text.Length(S) > 5,
            ValidDoraPMID = P = null or P = "" or PositivePMID(P)
        in if S = null or S = "" or S <> Text.Trim(S) then null
           else if PubSource and PubKeyAgrees then "PMID:" & P
           else if DoraKey(K) and ValidDoraPMID and (DoraSource or PubSource) then K
           else null, type nullable text),
    Invalid = Table.SelectRows(WithIdentity, each [TypedKey] = null),
    InvalidOverlap = Table.SelectRows(Invalid, each
        List.Contains(CanonicalKeys, [RegisteredCanonicalKey])
        or (PositivePMID([PMID]) and List.Contains(CanonicalKeys, "PMID:" & [PMID]))),
    Matched = Table.SelectRows(WithIdentity, each [TypedKey] <> null and List.Contains(CanonicalKeys, [TypedKey])),
    ExactUniverse = Table.RowCount(Matched) = List.Count(CanonicalKeys)
        and List.Count(List.Distinct(Matched[TypedKey])) = List.Count(CanonicalKeys),
    Guarded = if not IdentityValid then error "Qualified source identity is required."
        else if not ValidCanonical then error "Invalid canonical identity universe."
        else if not UniqueSourceKeys then error "Duplicate registered source identity."
        else if not UniqueRegisteredKeys then error "Duplicate durable registered canonical identity."
        else if Table.RowCount(InvalidOverlap) <> 0 then error "Unqualified registered identity overlaps canonical universe."
        else if not ExactUniverse then error "Incomplete or ambiguous canonical analytics crosswalk."
        else Matched,
    AddModified = Table.AddColumn(Guarded, "NativeModifiedRawJSON", each
        Text.FromBinary(Json.FromValue([NativeModified]), TextEncoding.Utf8), type text),
    RemoveNative = Table.RemoveColumns(AddModified, {"NativeModified", "PMID"}),
    RenameIdentity = Table.RenameColumns(RemoveNative, {{"TypedKey", "CanonicalKey"}}),
    AddSite = Table.AddColumn(RenameIdentity, "SourceSiteURL", each SiteUrl, type text),
    AddList = Table.AddColumn(AddSite, "SourceListID", each ListId, type text),
    AddLink = Table.AddColumn(AddList, "SourceItemURL", each
        Text.TrimEnd(SiteUrl, {"/"}) & "/_layouts/15/listform.aspx?PageType=4&ListId="
        & Uri.EscapeDataString(ListId) & "&ID=" & Uri.EscapeDataString(Text.From([NativeItemID], "en-US")), type text),
    AddRead = Table.AddColumn(AddLink, "SourceReadUTC", each ObservedUTC, type datetimezone),
    AddMeaning = Table.AddColumn(AddRead, "ClassificationProvenance", each
        "Registered assertion; original classification source/version not recorded. Read UTC is not classification date.", type text),
    Rows = Table.AddColumn(AddMeaning, "ProviderFieldMeaning", each
        "Provider research-field label; not an ANZSRC classification.", type text),
    BlankSourceCount = Table.RowCount(Table.SelectRows(WithIdentity, each [SourceKey] = null or [SourceKey] = "")),
    Diagnostics = [RawRows = Table.RowCount(Buffered), CanonicalRows = Table.RowCount(Rows),
        BlankSourceKeyRows = BlankSourceCount,
        InvalidOutsideCanonicalRows = Table.RowCount(Invalid) - BlankSourceCount,
        ValidOutsideCanonicalRows = Table.RowCount(WithIdentity) - Table.RowCount(Invalid) - Table.RowCount(Rows),
        SourceReadUTC = ObservedUTC, AltersCanonicalMembership = false,
        Interpretation = "Outside rows remain in source; no review/admission decision or ANZSRC assignment."]
in
    [Rows = Rows, Diagnostics = Diagnostics]
