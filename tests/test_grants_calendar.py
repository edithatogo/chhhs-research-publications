import unittest

from scripts.grants_calendar import build_icalendar, event_uid, project_event


SYNTHETIC_COVERAGE = {
    "CalendarVersion": "QLD-2026",
    "SourceID": "fixture:QLD-2026",
    "SourceURL": "https://example.org/holidays/2026",
    "ObservedAtUTC": "2026-01-01T00:00:00Z",
    "CoverageStart": "2026-01-01",
    "CoverageEnd": "2026-12-31",
    "CoverageVerified": True,
    "EvidenceSHA256": "0" * 64,
}

POLICY = {
    "PolicyKey": "CHHHS-INTAKE",
    "Version": "2026.09",
    "OrganisationKey": "CHHHS",
    "AnchorKind": "application_close",
    "LeadDays": 2,
    "HolidayCalendarVersion": "QLD-2026",
    "EffectiveFrom": "2026-01-01",
    "CalendarOrBusinessDays": "business",
    "HolidayDates": ["2026-09-25"],
    "HolidayCoverage": SYNTHETIC_COVERAGE,
}
AS_OF = "2026-09-20"


class GrantsCalendarTests(unittest.TestCase):
    def test_exact_date_projects_institutional_tentative_event(self):
        row = {
            "OpportunityKey": "GRANT:1", "Title": "Call, one", "URL": "https://example.org/call",
            "Source": "NHMRC", "Deadline": "2026-09-28", "DeadlinePrecision": "day", "Status": "Open", "ReviewStatus": "Reviewed",
        }
        event = project_event(row, POLICY, as_of=AS_OF)
        self.assertEqual(event["Date"], "2026-09-23")
        self.assertEqual(event["Anchor"], "institutional")
        self.assertEqual(event["ExternalDeadline"], "2026-09-28")
        self.assertEqual(event["Status"], "TENTATIVE")
        self.assertEqual(event["PolicyEvidenceStatus"], "provisional")
        self.assertIn("Call\\, one", build_icalendar([row], POLICY, generated_utc="2026-09-20T04:00:00Z"))
        self.assertIn("PROVISIONAL institutional planning date", build_icalendar([row], POLICY, generated_utc="2026-09-20T04:00:00Z"))

    def test_withdrawal_and_explicit_cancellation_keep_same_event_identity(self):
        row = {"OpportunityKey": "GRANT:CANCEL", "Deadline": "2026-09-28",
               "DeadlinePrecision": "day", "ReviewStatus": "Reviewed", "Status": "Open"}
        original = project_event(row, POLICY, as_of=AS_OF)
        for change in ({"Status": "Withdrawn"}, {"Status": " CANCELED "},
                       {"Cancelled": True}):
            with self.subTest(change=change):
                cancelled = project_event({**row, **change}, POLICY, as_of=AS_OF)
                self.assertEqual(cancelled["Status"], "CANCELLED")
                self.assertEqual(cancelled["UID"], original["UID"])
                self.assertIn("STATUS:CANCELLED", build_icalendar(
                    [{**row, **change}], POLICY, generated_utc="2026-09-20T04:00:00Z"))

    def test_business_policy_without_holiday_dates_fails_closed(self):
        row = {"OpportunityKey": "GRANT:HOLIDAY", "Deadline": "2026-09-28",
               "DeadlinePrecision": "day", "ReviewStatus": "Reviewed"}
        policy = {key: value for key, value in POLICY.items() if key != "HolidayDates"}
        with self.assertRaisesRegex(ValueError, "invalid institutional policy"):
            project_event(row, policy, as_of=AS_OF)

    def test_business_policy_requires_verified_source_coverage_metadata(self):
        row = {"OpportunityKey": "GRANT:COVERAGE", "Deadline": "2026-09-28",
               "DeadlinePrecision": "day", "ReviewStatus": "Reviewed"}
        for coverage in (
            None,
            {**SYNTHETIC_COVERAGE, "CoverageVerified": False},
            {**SYNTHETIC_COVERAGE, "SourceURL": "http://example.org/holidays"},
            {**SYNTHETIC_COVERAGE, "EvidenceSHA256": "not-a-hash"},
            {**SYNTHETIC_COVERAGE, "CalendarVersion": "QLD-2025"},
            {**SYNTHETIC_COVERAGE, "CoverageStart": "2026-12-31", "CoverageEnd": "2026-01-01"},
        ):
            with self.subTest(coverage=coverage):
                with self.assertRaisesRegex(ValueError, "invalid institutional policy"):
                    project_event(row, {**POLICY, "HolidayCoverage": coverage}, as_of=AS_OF)

    def test_business_projection_is_omitted_outside_holiday_coverage(self):
        row = {"OpportunityKey": "GRANT:OUTSIDE", "Deadline": "2027-01-04",
               "DeadlinePrecision": "day", "ReviewStatus": "Reviewed"}
        self.assertIsNone(project_event(row, POLICY, as_of=AS_OF))
        self.assertNotIn("BEGIN:VEVENT", build_icalendar(
            [row], POLICY, generated_utc="2026-12-20T04:00:00Z"))

    def test_coverage_must_span_the_entire_business_day_calculation(self):
        row = {"OpportunityKey": "GRANT:EDGE", "Deadline": "2026-09-28",
               "DeadlinePrecision": "day", "ReviewStatus": "Reviewed"}
        narrow = {**POLICY, "HolidayCoverage": {
            **SYNTHETIC_COVERAGE, "CoverageStart": "2026-09-25"}}
        self.assertIsNone(project_event(row, narrow, as_of=AS_OF))

    def test_calendar_day_policy_can_omit_unused_holiday_dates(self):
        row = {"OpportunityKey": "GRANT:CALENDAR", "Deadline": "2026-09-28",
               "DeadlinePrecision": "day", "ReviewStatus": "Reviewed"}
        policy = {key: value for key, value in POLICY.items()
                  if key not in {"HolidayDates", "HolidayCoverage"}}
        policy["CalendarOrBusinessDays"] = "calendar"
        self.assertEqual(project_event(row, policy, as_of=AS_OF)["Date"], "2026-09-26")

    def test_dtstamp_is_required_on_each_vevent_not_vcalendar(self):
        rows = [
            {"OpportunityKey": "GRANT:DT1", "Deadline": "2026-10-01", "DeadlinePrecision": "day", "ReviewStatus": "Reviewed"},
            {"OpportunityKey": "GRANT:DT2", "Deadline": "2026-10-02", "DeadlinePrecision": "day", "ReviewStatus": "Reviewed"},
        ]
        lines = build_icalendar(rows, POLICY, generated_utc="2026-09-20T04:00:00Z").splitlines()
        blocks = []
        current = None
        outside = []
        for line in lines:
            if line == "BEGIN:VEVENT":
                current = []
            elif line == "END:VEVENT":
                blocks.append(current)
                current = None
            elif current is not None:
                current.append(line)
            else:
                outside.append(line)
        self.assertEqual(len(blocks), 2)
        self.assertTrue(all(sum(line.startswith("DTSTAMP:") for line in block) == 1 for block in blocks))
        self.assertFalse(any(line.startswith("DTSTAMP:") for line in outside))
        self.assertEqual(sum(line == "BEGIN:VCALENDAR" for line in lines), 1)
        self.assertTrue(all("DTSTAMP:20260920T040000Z" in block for block in blocks))

    def test_unknown_or_partial_date_is_omitted(self):
        row = {"OpportunityKey": "GRANT:2", "Title": "Unknown", "Deadline": "2026-09", "DeadlinePrecision": "month"}
        self.assertIsNone(project_event(row, POLICY, as_of=AS_OF))
        self.assertNotIn("GRANT:2", build_icalendar([row], POLICY, generated_utc="2026-09-20T04:00:00Z"))

    def test_cancellation_is_explicit_and_uid_changes_with_policy_identity(self):
        row = {"OpportunityKey": "GRANT:3", "Title": "Cancelled", "Deadline": "2026-10-01", "DeadlinePrecision": "day", "Status": "Cancelled", "ReviewStatus": "Reviewed"}
        event = project_event(row, POLICY, as_of=AS_OF)
        self.assertEqual(event["Status"], "CANCELLED")
        self.assertEqual(event_uid("GRANT:3", "institutional", "CHHHS-INTAKE", "2026.09"), event_uid("GRANT:3", "institutional", "CHHHS-INTAKE", "2026.10"))
        self.assertNotEqual(event_uid("GRANT:3", "institutional", "CHHHS-INTAKE", "2026.09"), event_uid("GRANT:3", "institutional", "CHHHS-INTAKE-V2", "2026.09"))

    def test_uid_field_boundaries_cannot_alias_on_delimiter(self):
        left = event_uid("GRANT:A|B", "institutional", "POLICY:C", "v1")
        right = event_uid("GRANT:A", "B|institutional", "POLICY:C", "v1")
        self.assertNotEqual(left, right)

    def test_policy_revision_keeps_component_identity_for_cancellation(self):
        open_row = {"OpportunityKey": "GRANT:REV", "Title": "Call", "Deadline": "2026-10-01",
                    "DeadlinePrecision": "day", "Status": "Open", "ReviewStatus": "Reviewed"}
        cancelled_row = {**open_row, "Status": "Cancelled"}
        revised_policy = {**POLICY, "Version": "2026.10"}
        open_event = project_event(open_row, POLICY, as_of=AS_OF)
        cancelled_event = project_event(cancelled_row, revised_policy, as_of=AS_OF)
        self.assertEqual(open_event["UID"], cancelled_event["UID"])
        self.assertEqual(cancelled_event["Status"], "CANCELLED")
        self.assertEqual(cancelled_event["PolicyVersion"], "2026.10")

    def test_invalid_calendar_day_is_omitted_even_when_precision_claims_day(self):
        for raw in ("2026-02-30", "2026-13-01", "2026-01-01T00:00:00+10:00"):
            row = {"OpportunityKey": "GRANT:BAD-DATE", "Deadline": raw,
                   "DeadlinePrecision": "day", "ReviewStatus": "Reviewed"}
            self.assertIsNone(project_event(row, POLICY, as_of=AS_OF))

    def test_title_line_break_cannot_inject_calendar_properties(self):
        row = {"OpportunityKey": "GRANT:TEXT", "Title": "Call\r\nSTATUS:CANCELLED",
               "Deadline": "2026-10-01", "DeadlinePrecision": "day", "ReviewStatus": "Reviewed"}
        ical = build_icalendar([row], POLICY, generated_utc="2026-09-20T04:00:00Z")
        self.assertIn("SUMMARY:Call\\nSTATUS:CANCELLED", ical)
        self.assertEqual(sum(line.startswith("STATUS:") for line in ical.splitlines()), 1)

    def test_long_unicode_content_lines_fold_at_75_octets_and_unfold_exactly(self):
        title = "研究機会と研究者の適格性を確認してください — " * 8
        row = {"OpportunityKey": "GRANT:FOLD", "Title": title, "Deadline": "2026-10-01",
               "DeadlinePrecision": "day", "ReviewStatus": "Reviewed"}
        ical = build_icalendar([row], POLICY, generated_utc="2026-09-20T04:00:00Z")
        physical_lines = ical.splitlines()
        self.assertTrue(all(len(line.encode("utf-8")) <= 75 for line in physical_lines))
        unfolded = ical.replace("\r\n ", "")
        self.assertIn("SUMMARY:" + title, unfolded)
        self.assertEqual(unfolded.count("BEGIN:VEVENT"), 1)

    def test_duplicate_reviewed_opportunity_identity_fails_closed(self):
        row = {"OpportunityKey": "GRANT:DUP", "Deadline": "2026-10-01",
               "DeadlinePrecision": "day", "ReviewStatus": "Reviewed"}
        with self.assertRaisesRegex(ValueError, "unique non-empty OpportunityKey"):
            build_icalendar([row, dict(row)], POLICY, generated_utc="2026-09-20T04:00:00Z")

    def test_missing_reviewed_opportunity_identity_fails_closed(self):
        row = {"Deadline": "2026-10-01", "DeadlinePrecision": "day", "ReviewStatus": "Reviewed"}
        with self.assertRaisesRegex(ValueError, "unique non-empty OpportunityKey"):
            build_icalendar([row], POLICY, generated_utc="2026-09-20T04:00:00Z")

    def test_generated_timestamp_must_be_a_real_utc_instant(self):
        for value in ("2026-99-99T04:00:00Z", "2026-09-20T25:00:00Z"):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "real second-precision UTC"):
                build_icalendar([], POLICY, generated_utc=value)

    def test_unreviewed_exact_deadline_never_becomes_calendar_event(self):
        base = {"OpportunityKey": "GRANT:4", "Title": "Candidate", "Deadline": "2026-10-01", "DeadlinePrecision": "day", "Status": "Open"}
        for status in (None, "Needs Review", "Excluded"):
            row = {**base, "ReviewStatus": status}
            self.assertIsNone(project_event(row, POLICY, as_of=AS_OF))
            self.assertNotIn("BEGIN:VEVENT", build_icalendar([row], POLICY, generated_utc="2026-09-20T04:00:00Z"))

    def test_future_and_expired_policies_do_not_generate_calendar_events(self):
        row = {"OpportunityKey": "GRANT:STALE-POLICY", "Deadline": "2026-10-01",
               "DeadlinePrecision": "day", "ReviewStatus": "Reviewed"}
        expired = {**POLICY, "EffectiveTo": "2026-09-19"}
        future = {**POLICY, "EffectiveFrom": "2026-09-21"}
        for policy in (expired, future):
            with self.subTest(effective_from=policy["EffectiveFrom"],
                              effective_to=policy.get("EffectiveTo")):
                self.assertIsNone(project_event(row, policy, as_of=AS_OF))
                calendar = build_icalendar(
                    [row], policy, generated_utc="2026-09-20T04:00:00Z"
                )
                self.assertNotIn("BEGIN:VEVENT", calendar)

    def test_project_event_requires_an_explicit_valid_evaluation_date(self):
        row = {"OpportunityKey": "GRANT:AS-OF", "Deadline": "2026-10-01",
               "DeadlinePrecision": "day", "ReviewStatus": "Reviewed"}
        for invalid in (None, "2026-09", "2026-02-30", "2026-09-20T00:00:00Z"):
            with self.subTest(as_of=invalid), self.assertRaisesRegex(
                    ValueError, "as_of must be a real YYYY-MM-DD date"):
                project_event(row, POLICY, as_of=invalid)


if __name__ == "__main__":
    unittest.main()
