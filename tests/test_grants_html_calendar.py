import unittest

from scripts.grants_html_calendar import parse_calendar_html


class GrantsHtmlCalendarTests(unittest.TestCase):
    def test_extracts_candidates_without_inventing_exact_deadline_or_review(self):
        html = """<table><tr><th>Grant opportunity</th><th>Applications close</th><th>Status</th></tr>
        <tr><td>Example call</td><td>11 Nov 2026 - 5:00pm</td><td>Open</td></tr></table>"""
        result = parse_calendar_html(
            html,
            source="MRFF",
            source_url="https://example.gov.au/calendar",
            retrieved_utc="2026-09-20T04:00:00Z",
        )
        self.assertEqual(result["status"], "candidate_rows")
        self.assertEqual(len(result["records"]), 1)
        self.assertIsNone(result["records"][0]["Deadline"])
        self.assertEqual(result["records"][0]["DeadlineRaw"], "11 Nov 2026 - 5:00pm")
        self.assertEqual(result["records"][0]["ReviewStatus"], "Needs Review")
        self.assertEqual(result["records"][0]["SourceColumns"]["grant opportunity"], "Example call")
        self.assertEqual(result["records"][0]["SourceColumns"]["status"], "Open")
        self.assertEqual(len(result["records"][0]["SourceCells"]), 3)
        self.assertEqual(result["records"][0]["SourceCells"][0], {"header": "grant opportunity", "value": "Example call"})

    def test_no_matching_table_is_explicit(self):
        result = parse_calendar_html(
            "<table><tr><th>Name</th><th>Date</th></tr><tr><td>x</td><td>y</td></tr></table>",
            source="NHMRC",
            source_url="https://example.gov.au/calendar",
            retrieved_utc="2026-09-20T04:00:00Z",
        )
        self.assertEqual(result["status"], "no_matching_table")
        self.assertEqual(result["records"], [])

    def test_requires_explicit_utc(self):
        with self.assertRaises(ValueError):
            parse_calendar_html(
                "<table><tr><th>Title</th><th>Close</th></tr></table>",
                source="X",
                source_url="https://example.gov.au",
                retrieved_utc="2026-09-20T04:00:00",
            )

    def test_duplicate_source_rows_fail_closed(self):
        html = """<table><tr><th>Title</th><th>Close</th></tr>
        <tr><td>Same</td><td>2026-11-01</td></tr>
        <tr><td>Same</td><td>2026-11-01</td></tr></table>"""
        result = parse_calendar_html(
            html,
            source="NHMRC",
            source_url="https://example.gov.au/calendar",
            retrieved_utc="2026-09-20T04:00:00Z",
        )
        self.assertEqual(result["status"], "duplicate_source_identity")
        self.assertEqual(result["records"], [])

    def test_repeated_headers_are_not_candidates(self):
        html = """<table><tr><th>Title</th><th>Close</th></tr>
        <tr><td>First</td><td>2026-11-01</td></tr>
        <tr><th>Title</th><th>Close</th></tr>
        <tr><td>Second</td><td>2026-12-01</td></tr></table>"""
        result = parse_calendar_html(
            html,
            source="NHMRC",
            source_url="https://example.gov.au/calendar",
            retrieved_utc="2026-09-20T04:00:00Z",
        )
        self.assertEqual([row["Title"] for row in result["records"]], ["First", "Second"])


if __name__ == "__main__":
    unittest.main()
