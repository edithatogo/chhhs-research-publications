import unittest

from scripts.grants_calendar import build_icalendar, event_uid, project_event


POLICY = {"PolicyKey": "CHHHS-INTAKE", "Version": "2026.09", "OrganisationKey": "CHHHS", "AnchorKind": "application_close", "LeadDays": 2, "HolidayCalendarVersion": "QLD-2026", "EffectiveFrom": "2026-01-01", "CalendarOrBusinessDays": "business", "HolidayDates": ["2026-09-25"]}


class GrantsCalendarTests(unittest.TestCase):
    def test_exact_date_projects_institutional_tentative_event(self):
        row = {"OpportunityKey": "GRANT:1", "Title": "Call, one", "URL": "https://example.org/call", "Source": "NHMRC", "Deadline": "2026-09-28", "DeadlinePrecision": "day", "Status": "Open"}
        event = project_event(row, POLICY)
        self.assertEqual(event["Date"], "2026-09-23")
        self.assertEqual(event["Anchor"], "institutional")
        self.assertEqual(event["ExternalDeadline"], "2026-09-28")
        self.assertEqual(event["Status"], "TENTATIVE")
        self.assertIn("Call\\, one", build_icalendar([row], POLICY, generated_utc="2026-09-20T04:00:00Z"))

    def test_unknown_or_partial_date_is_omitted(self):
        row = {"OpportunityKey": "GRANT:2", "Title": "Unknown", "Deadline": "2026-09", "DeadlinePrecision": "month"}
        self.assertIsNone(project_event(row, POLICY))
        self.assertNotIn("GRANT:2", build_icalendar([row], POLICY, generated_utc="2026-09-20T04:00:00Z"))

    def test_cancellation_is_explicit_and_uid_changes_with_policy(self):
        row = {"OpportunityKey": "GRANT:3", "Title": "Cancelled", "URL": "https://example.org/cancelled", "Deadline": "2026-10-01", "DeadlinePrecision": "day", "Status": "Cancelled"}
        event = project_event(row, POLICY)
        self.assertEqual(event["Status"], "CANCELLED")
        self.assertNotEqual(event_uid("GRANT:3", "institutional", "CHHHS-INTAKE", "2026.09"), event_uid("GRANT:3", "institutional", "CHHHS-INTAKE", "2026.10"))

    def test_duplicate_event_uid_fails_closed(self):
        row = {"OpportunityKey": "GRANT:4", "Title": "Duplicate", "URL": "https://example.org/duplicate", "Deadline": "2026-10-01", "DeadlinePrecision": "day"}
        with self.assertRaisesRegex(ValueError, "duplicate calendar event UID"):
            build_icalendar([row, dict(row)], POLICY, generated_utc="2026-09-20T04:00:00Z")

    def test_exact_date_requires_authoritative_url_and_key(self):
        with self.assertRaisesRegex(ValueError, r"requires an HTTP\(S\) URL"):
            project_event({"OpportunityKey": "GRANT:5", "Title": "No link", "URL": "not-a-url", "Deadline": "2026-10-01", "DeadlinePrecision": "day"}, POLICY)
        with self.assertRaisesRegex(ValueError, "missing OpportunityKey"):
            project_event({"Title": "No key", "URL": "https://example.org/no-key", "Deadline": "2026-10-01", "DeadlinePrecision": "day"}, POLICY)


if __name__ == "__main__":
    unittest.main()
