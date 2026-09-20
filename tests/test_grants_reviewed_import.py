import unittest

from scripts.grants_reviewed_import import import_reviewed_rows


class ReviewedImportTests(unittest.TestCase):
    def _row(self, **overrides):
        row = {
            "Source": "nhmrc",
            "SourceID": "GO-123",
            "Title": "Reviewed opportunity",
            "URL": "https://example.org/opportunity/123",
            "SourceRowURL": "https://example.org/opportunity/123#row",
            "Eligibility": "Australian public health researchers; reviewer confirmed source wording.",
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

    def test_missing_row_evidence_and_eligibility_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "invalid_SourceRowURL"):
            import_reviewed_rows([self._row(SourceRowURL="", Eligibility="eligible")])
        with self.assertRaisesRegex(ValueError, "missing_Eligibility"):
            import_reviewed_rows([self._row(Eligibility="")])

    def test_one_bad_row_rejects_the_complete_batch(self):
        with self.assertRaisesRegex(ValueError, "row 1"):
            import_reviewed_rows([self._row(), self._row(URL="not-a-url")])

    def test_reviewer_fields_are_not_coerced(self):
        with self.assertRaisesRegex(ValueError, "invalid_Source"):
            import_reviewed_rows([self._row(Source=True)])
        with self.assertRaisesRegex(ValueError, "invalid_ReviewStatus"):
            import_reviewed_rows([self._row(ReviewStatus=True)])
        with self.assertRaisesRegex(ValueError, "invalid_SourceID_or_RoundID"):
            import_reviewed_rows([self._row(SourceID=123)])


if __name__ == "__main__":
    unittest.main()
