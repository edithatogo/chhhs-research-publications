import unittest

from scripts.grants_reviewed_import import import_reviewed_rows


class ReviewedImportTests(unittest.TestCase):
    def _row(self, **overrides):
        row = {
            "Source": "nhmrc",
            "SourceID": "GO-123",
            "Title": "Reviewed opportunity",
            "URL": "https://example.org/opportunity/123",
            "Deadline": "2027-04",
            "RetrievedUTC": "2026-09-20T02:00:00Z",
            "ReviewStatus": "Reviewed",
            "ReviewNotes": "Checked against the named authority page and row link.",
        }
        row.update(overrides)
        return row

    def test_reviewed_row_is_normalized_and_admitted(self):
        records = import_reviewed_rows([self._row()], expected_source="nhmrc")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["DeadlinePrecision"], "month")
        self.assertEqual(records[0]["ReviewStatus"], "Reviewed")

    def test_candidate_row_without_review_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "ReviewStatus_not_Reviewed"):
            import_reviewed_rows([self._row(ReviewStatus="Needs Review")])

    def test_missing_row_identity_and_notes_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "missing_SourceID_or_RoundID"):
            import_reviewed_rows([self._row(SourceID="", RoundID="", ReviewNotes="")])

    def test_one_bad_row_rejects_the_complete_batch(self):
        with self.assertRaisesRegex(ValueError, "row 1"):
            import_reviewed_rows([self._row(), self._row(URL="not-a-url")])


if __name__ == "__main__":
    unittest.main()
