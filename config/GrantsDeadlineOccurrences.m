// Reference the existing parent query. No second SharePoint connection or write.
let
    Parents = Table.SelectColumns(#"Grants Registry", {
        "OpportunityKey", "Source", "SourceID", "RoundID", "DeadlineScheduleJSON", "SourceAttribution"
    }),
    Lists = Table.AddColumn(Parents, "Occurrences", each
        if [DeadlineScheduleJSON] = null or [DeadlineScheduleJSON] = "" then {}
        else let
            Parent = _,
            Envelope = Json.Document([DeadlineScheduleJSON]),
            Rows = Envelope[occurrences],
            Valid = Envelope[schema_version] = "grants-deadline-schedule-v1"
                and Envelope[Source] = [Source] and Envelope[SourceID] = [SourceID]
                and Envelope[RoundID] = [RoundID]
                and List.Count(Rows) = Envelope[occurrence_count] and List.Count(Rows) > 0,
            Projected = if not Valid then error "Invalid deadline schedule envelope" else
                List.Transform(Rows, (Occurrence) =>
                    if Occurrence[parent_source_id] <> Parent[Source]
                        or Occurrence[parent_source_record_id] <> Parent[SourceID]
                        or Occurrence[parent_funding_opportunity_number] <> Parent[RoundID]
                    then error "Deadline occurrence identity mismatch" else [
                        OpportunityKey = Parent[OpportunityKey],
                        OccurrenceKey = Occurrence[occurrence_candidate_id],
                        ApplicationType = Occurrence[application_type],
                        NominalDueDate = Occurrence[due_date],
                        EffectiveDueDate = null,
                        SourceLocalTime = Occurrence[source_due_time],
                        SourceTimezoneRule = Occurrence[source_timezone_rule],
                        SourceURL = Envelope[source_url],
                        TemporalStatus = "source_nominal_date; effective deadline unresolved",
                        SourceAttribution = Parent[SourceAttribution],
                        SourceOccurrenceJSON = Text.FromBinary(Json.FromValue(Occurrence), TextEncoding.Utf8)
                    ])
        in Projected),
    Flat = List.Combine(Lists[Occurrences]),
    Result = Table.FromRecords(Flat, type table [
        OpportunityKey = text, OccurrenceKey = text, ApplicationType = text,
        NominalDueDate = text, EffectiveDueDate = nullable text, SourceLocalTime = text,
        SourceTimezoneRule = text, SourceURL = text, TemporalStatus = text,
        SourceAttribution = nullable text, SourceOccurrenceJSON = text
    ]),
    Checked = if Table.RowCount(Result) <> Table.RowCount(Table.Distinct(Result, {"OpportunityKey", "OccurrenceKey"}))
        then error "Duplicate deadline occurrence identity" else Result
in
    Checked
