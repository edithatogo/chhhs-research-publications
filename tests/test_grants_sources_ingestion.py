import unittest
from pathlib import Path

from scripts.grants_ingestion import ingest_batches, parse_feed
from scripts.grants_sources import load_catalogue


class GrantsSourceTests(unittest.TestCase):
    def test_catalogue_has_required_sources_and_explicit_health(self):
        rows = load_catalogue(Path(__file__).parents[1] / "config/grants-sources.json")
        self.assertGreaterEqual(len(rows), 13)
        self.assertTrue(all(row["last_verified"] for row in rows))
        ids = {row["source_id"] for row in rows}
        self.assertTrue({
            "qh-health-practitioner-research", "metro-south-research-support",
            "metro-north-research-grants", "torres-cape-research-support",
        } <= ids)

    def test_arc_public_api_is_verified_as_awards_only(self):
        rows = load_catalogue(Path(__file__).parents[1] / "config/grants-sources.json")
        arc = next(row for row in rows if row["source_id"] == "arc")
        self.assertEqual(arc["intake"], "api")
        self.assertEqual(arc["health_status"], "verified_sample")
        self.assertTrue(arc["api_url"].startswith("https://dataportal.arc.gov.au/NCGP/API/grants"))
        self.assertEqual(arc["record_kind"], "awards_only")
        self.assertIn("not an open-opportunity calendar", arc["coverage"])

    def test_queensland_grants_finder_api_is_metadata_only(self):
        rows = load_catalogue(Path(__file__).parents[1] / "config/grants-sources.json")
        finder = next(row for row in rows if row["source_id"] == "queensland-grants-finder")
        self.assertEqual(finder["intake"], "api")
        self.assertEqual(finder["health_status"], "verified_sample")
        self.assertEqual(finder["record_kind"], "metadata_only")
        self.assertIn("does not expose opportunity rows", finder["coverage"])

    def test_atom_and_rss_shapes_are_preserved_as_canonical_records(self):
        rss = """<rss><channel><item><guid>r1</guid><title>Call</title><link>https://example.org/call/</link><description>Summary</description><deadline>2027-04</deadline></item></channel></rss>"""
        atom = """<feed xmlns='http://www.w3.org/2005/Atom'><entry><id>a1</id><title>Call</title><link href='https://example.org/call'/><summary>Summary</summary></entry></feed>"""
        a = parse_feed(rss, source="R", retrieved_at="2026-09-20T00:00:00+10:00")[0]
        b = parse_feed(atom, source="A", retrieved_at="2026-09-20T00:00:00+10:00")[0]
        self.assertEqual(a["DeadlinePrecision"], "month")
        self.assertEqual(a["URL"], "https://example.org/call")
        self.assertEqual(b["Title"], "Call")
        self.assertEqual(a["RetrievedTimestampStatus"], "valid")

    def test_bad_source_does_not_discard_successful_batch(self):
        result = ingest_batches([
            {"source": "good", "retrieved_at": "2026-09-20T00:00:00Z", "records": [{"Title": "Good", "URL": "https://example.org/g"}]},
            {"source": "bad", "retrieved_at": "2026-09-20T00:00:00Z", "xml": "<broken"},
        ])
        self.assertEqual(len(result["records"]), 1)
        self.assertEqual([item["status"] for item in result["health"]], ["succeeded", "failed"])
        self.assertFalse(result["accepted"])

    def test_duplicate_feed_identity_fails_closed(self):
        xml = """<rss><channel>
        <item><guid>same</guid><title>One</title><link>https://example.org/1</link></item>
        <item><guid>same</guid><title>Two</title><link>https://example.org/2</link></item>
        </channel></rss>"""
        with self.assertRaisesRegex(ValueError, "duplicate source identity"):
            parse_feed(xml, source="R", retrieved_at="2026-09-20T00:00:00Z")

    def test_missing_feed_title_fails_closed(self):
        xml = """<rss><channel><item><guid>r1</guid><link>https://example.org/1</link></item></channel></rss>"""
        with self.assertRaisesRegex(ValueError, "missing title"):
            parse_feed(xml, source="R", retrieved_at="2026-09-20T00:00:00Z")

    def test_missing_feed_identity_fails_closed(self):
        xml = """<rss><channel><item><title>Unbound call</title></item></channel></rss>"""
        with self.assertRaisesRegex(ValueError, "missing source identity"):
            parse_feed(xml, source="R", retrieved_at="2026-09-20T00:00:00Z")

    def test_current_record_uses_newest_observation_but_preserves_review(self):
        from scripts.grants_registry import merge_observations
        rows = merge_observations([
            {"Source":"X", "SourceID":"1", "Title":"Old", "URL":"https://x/1", "RetrievedUTC":"2026-09-19T00:00:00Z", "ReviewStatus":"Reviewed", "ReviewNotes":"human note"},
            {"Source":"X", "SourceID":"1", "Title":"New", "URL":"https://x/1", "RetrievedUTC":"2026-09-20T00:00:00Z"},
        ])
        self.assertEqual(rows[0]["Title"], "New")
        self.assertEqual(rows[0]["ReviewStatus"], "Reviewed")
        self.assertEqual(rows[0]["ReviewNotes"], "human note")
        self.assertEqual(len(rows[0]["SourceObservations"]), 2)


if __name__ == "__main__":
    unittest.main()
