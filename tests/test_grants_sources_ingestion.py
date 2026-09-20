import unittest
from pathlib import Path

from scripts.grants_ingestion import ingest_batches, parse_feed
from scripts.grants_sources import load_catalogue


class GrantsSourceTests(unittest.TestCase):
    def test_catalogue_has_required_sources_and_explicit_health(self):
        rows = load_catalogue(Path(__file__).parents[1] / "config/grants-sources.json")
        self.assertGreaterEqual(len(rows), 7)
        self.assertTrue(all(row["last_verified"] for row in rows))

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
