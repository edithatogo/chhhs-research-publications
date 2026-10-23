import contextlib
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from scripts.grants_reviewed_import import (
    PRIVATE_OPS_ROOT, import_reviewed_rows, main, reconcile_reviewed_batches,
)


class ReviewedImportTests(unittest.TestCase):
    def _import(self, rows, **kwargs):
        return import_reviewed_rows(rows, official_hosts=["example.org"], **kwargs)

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
        records = self._import([self._row()], expected_source="nhmrc")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["DeadlinePrecision"], "month")
        self.assertEqual(records[0]["ReviewStatus"], "Reviewed")

    def test_deadline_zone_projection_is_preserved_in_reviewed_record(self):
        record = self._import([self._row(
            Deadline="2026-01-15T12:00:00",
            DeadlineTimezone="Australia/Sydney",
        )])[0]
        self.assertEqual(record["DeadlineTimezone"], "Australia/Sydney")
        self.assertEqual(record["DeadlineUTCInstant"], "2026-01-15T01:00:00Z")
        self.assertEqual(record["DeadlineBrisbaneDate"], "2026-01-15")
        self.assertEqual(record["DeadlineTemporalStatus"], "zone_resolved")
        snake_case = self._import([self._row(
            Deadline="2026-01-15T12:00:00", deadline_timezone="Australia/Sydney",
        )])[0]
        self.assertEqual(snake_case["DeadlineTimezone"], "Australia/Sydney")
        self.assertEqual(snake_case["DeadlineUTCInstant"], "2026-01-15T01:00:00Z")

    def test_distinct_source_row_url_is_preserved_and_must_use_an_admitted_host(self):
        row_url = "https://example.org/funding#round-123"
        record = self._import([self._row(SourceRowURL=row_url)])[0]
        self.assertEqual(record["URL"], "https://example.org/opportunity/123")
        self.assertEqual(record["SourceRowURL"], row_url)
        with self.assertRaisesRegex(ValueError, "invalid_SourceRowURL"):
            self._import([self._row(SourceRowURL="https://other.example/funding#round-123")])

    def test_candidate_row_without_review_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "ReviewStatus_not_Reviewed"):
            self._import([self._row(ReviewStatus="Needs Review")])

    def test_missing_row_identity_and_notes_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "missing_SourceID_or_RoundID"):
            self._import([self._row(SourceID="", RoundID="", ReviewNotes="")])

    def test_one_bad_row_rejects_the_complete_batch(self):
        with self.assertRaisesRegex(ValueError, "row 1"):
            self._import([self._row(), self._row(URL="not-a-url")])

    def test_official_host_and_observation_are_required(self):
        for changes, error in [
            ({"URL": "https://example.org@evil.test/row"}, "invalid_URL"),
            ({"RetrievedUTC": "2026-09-20T02:00:00"}, "RetrievedUTC_not_timezone_aware"),
            ({"Deadline": "2027-02-30"}, "invalid_Deadline"),
        ]:
            with self.subTest(error=error):
                with self.assertRaisesRegex(ValueError, error):
                    self._import([self._row(**changes)])

    def test_duplicate_reviewed_identity_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "duplicate OpportunityKey"):
            self._import([self._row(), self._row()])

    def test_round_only_identity_survives_official_url_change(self):
        first = self._import([self._row(SourceID="", RoundID="2027-A")])[0]
        moved = self._import([self._row(SourceID="", RoundID="2027-A",
                                        URL="https://example.org/new-location")])[0]
        self.assertEqual(first["OpportunityKey"], moved["OpportunityKey"])
        other_source = self._import([self._row(Source="other", SourceID="", RoundID="2027-A")])[0]
        self.assertNotEqual(first["OpportunityKey"], other_source["OpportunityKey"])

    def test_official_url_rejects_surrounding_whitespace(self):
        with self.assertRaisesRegex(ValueError, "invalid_URL"):
            self._import([self._row(URL=" https://example.org/opportunity/123 ")])

    def test_row_cannot_assert_reviewer_identity_or_platform_provenance(self):
        for field, value in [
            ("ReviewerEmail", "trusted@example.org"),
            ("ReviewedByID", "reviewer-123"),
            ("ReviewTimestamp", "2026-09-20T02:00:00Z"),
            ("NativeAccepted", True),
        ]:
            with self.subTest(field=field), self.assertRaisesRegex(
                    ValueError, "untrusted_reviewer_provenance"):
                self._import([self._row(**{field: value})])

    def test_invalid_mapping_types_do_not_become_review_evidence(self):
        for change, error in [
            ({"Source": {"name": "nhmrc"}}, "missing_Source"),
            ({"ReviewNotes": {"text": "checked"}}, "missing_ReviewNotes"),
            ({"ReviewStatus": ["Reviewed"]}, "ReviewStatus_not_Reviewed"),
            ({"SourceID": {"id": "GO-123"}, "RoundID": ""}, "missing_SourceID_or_RoundID"),
            ({"DeadlineTimezone": 10}, "invalid_DeadlineTimezone_type"),
            ({"deadline_timezone": ["Australia/Sydney"]}, "invalid_deadline_timezone_type"),
        ]:
            with self.subTest(error=error), self.assertRaisesRegex(ValueError, error):
                self._import([self._row(**change)])

    def test_secondary_identity_must_not_be_stringified_into_key(self):
        for changes, error in [
            ({"SourceID": "GO-123", "RoundID": 2027}, "invalid_RoundID_type"),
            ({"SourceID": 123, "RoundID": "2027-A"}, "invalid_SourceID_type"),
        ]:
            with self.subTest(changes=changes), self.assertRaisesRegex(ValueError, error):
                self._import([self._row(**changes)])

    def test_supplied_opportunity_key_must_match_canonical_source_identity(self):
        canonical = self._import([self._row()])[0]["OpportunityKey"]
        accepted = self._import([self._row(OpportunityKey=canonical)])
        self.assertEqual(accepted[0]["OpportunityKey"], canonical)
        for supplied, error in (("GRANT:wrong", "OpportunityKey_mismatch"),
                                (123, "invalid_OpportunityKey_type")):
            with self.subTest(supplied=supplied), self.assertRaisesRegex(ValueError, error):
                self._import([self._row(OpportunityKey=supplied)])

    def test_delimiter_bearing_keys_round_trip_without_aliasing_reviewed_rows(self):
        first = self._import([self._row(Source="A:B", SourceID="C", RoundID="D")])[0]
        second = self._import([self._row(Source="A", SourceID="B:C", RoundID="D")])[0]
        self.assertTrue(first["OpportunityKey"].startswith("GRANTX:"))
        self.assertTrue(second["OpportunityKey"].startswith("GRANTX:"))
        self.assertNotEqual(first["OpportunityKey"], second["OpportunityKey"])
        result = reconcile_reviewed_batches([first, second])
        self.assertCountEqual(result["added_keys"], [first["OpportunityKey"], second["OpportunityKey"]])

    def test_legacy_delimiter_key_is_rejected_for_explicit_reconciliation(self):
        old_basis = "A:B:C|round:D"
        legacy_key = "GRANT:" + hashlib.sha256(old_basis.encode("utf-8")).hexdigest()[:24]
        with self.assertRaisesRegex(ValueError, "OpportunityKey_mismatch"):
            self._import([self._row(Source="A:B", SourceID="C", RoundID="D",
                                    OpportunityKey=legacy_key)])

    def test_optional_source_fact_must_not_be_stringified_after_review(self):
        for field, value in (("Status", {"value": "Open"}), ("Amount", 1000),
                             ("Eligibility", ["Queensland researchers"]),
                             ("Description", {"text": "Authority summary"})):
            with self.subTest(field=field), self.assertRaisesRegex(
                    ValueError, f"invalid_{field}_type"):
                self._import([self._row(**{field: value})])

    def test_review_decision_and_notes_are_preserved_in_canonical_record(self):
        record = self._import([self._row(ReviewNotes="Verified against official round terms.")])[0]
        self.assertEqual(record["ReviewStatus"], "Reviewed")
        self.assertEqual(record["ReviewNotes"], "Verified against official round terms.")
        self.assertNotIn("ReviewerEmail", record)
        self.assertNotIn("NativeAccepted", record)

    def test_non_iterable_batch_fails_with_contract_error(self):
        with self.assertRaisesRegex(ValueError, "iterable of row objects"):
            import_reviewed_rows(None, official_hosts=["example.org"])

    def test_interrupted_row_iterator_rejects_partial_reviewed_batch(self):
        def interrupted_rows():
            yield self._row()
            raise RuntimeError("private source read failure")

        with self.assertRaisesRegex(ValueError, "iterable of row objects") as raised:
            import_reviewed_rows(interrupted_rows(), official_hosts=["example.org"])

        self.assertNotIn("private source read failure", str(raised.exception))

    def test_reviewed_batch_reconciliation_is_order_independent_and_does_not_infer_deletion(self):
        first = self._row()
        second = self._row(SourceID="GO-124", URL="https://example.org/opportunity/124")
        prior = self._import([first, second])
        reordered = self._import([second, first])
        baseline = reconcile_reviewed_batches(prior)
        same = reconcile_reviewed_batches(reordered, prior)
        self.assertEqual(baseline["current_digest"], same["current_digest"])
        self.assertEqual(same["unchanged_keys"], sorted(row["OpportunityKey"] for row in prior))
        self.assertEqual(same["changed_keys"], [])
        self.assertEqual(same["unobserved_in_current_batch"], [])

        updated = self._import([self._row(ReviewNotes="Reviewed revised official terms.")])
        difference = reconcile_reviewed_batches(updated, prior)
        self.assertEqual(difference["changed_keys"], [updated[0]["OpportunityKey"]])
        self.assertEqual(difference["unobserved_in_current_batch"], [prior[1]["OpportunityKey"]])
        self.assertFalse(difference["deletion_inferred"])

    def test_reconciliation_rejects_unreviewed_or_duplicate_normalized_records(self):
        reviewed = self._import([self._row()])[0]
        with self.assertRaisesRegex(ValueError, "unique reviewed OpportunityKeys"):
            reconcile_reviewed_batches([reviewed, reviewed])
        with self.assertRaisesRegex(ValueError, "unique reviewed OpportunityKeys"):
            reconcile_reviewed_batches([{**reviewed, "ReviewStatus": "Needs Review"}])

    def test_reconciliation_rejects_pre_normalized_identity_key_mismatch(self):
        reviewed = self._import([self._row()])[0]
        with self.assertRaisesRegex(ValueError, "keys matching text source identities"):
            reconcile_reviewed_batches([{**reviewed, "SourceID": "GO-999"}])
        with self.assertRaisesRegex(ValueError, "keys matching text source identities"):
            reconcile_reviewed_batches([{**reviewed, "RoundID": 2027}])

    def test_reconciliation_rejects_older_same_key_observation(self):
        prior = self._import([self._row(RetrievedUTC="2026-09-21T02:00:00Z")])
        older = self._import([self._row(RetrievedUTC="2026-09-21T10:00:00+10:00",
                                        ReviewNotes="Changed from an older observation.")])
        with self.assertRaisesRegex(ValueError, "older_observation"):
            reconcile_reviewed_batches(older, prior)
        newer = self._import([self._row(RetrievedUTC="2026-09-21T13:00:00+10:00")])
        self.assertEqual(reconcile_reviewed_batches(newer, prior)["changed_keys"],
                         [prior[0]["OpportunityKey"]])

    def test_reconciliation_requires_valid_timestamps_even_for_pre_normalized_input(self):
        reviewed = self._import([self._row()])[0]
        with self.assertRaisesRegex(ValueError, "valid observation timestamps"):
            reconcile_reviewed_batches([{**reviewed, "RetrievedUTC": "2026-09-20T02:00:00"}])

    def test_same_instant_conflicting_authority_fact_is_rejected(self):
        for changed_field, original, changed in (
            ("Deadline", "2027-04", "2027-05"),
            ("DeadlineTimezone", "Australia/Sydney", "Australia/Brisbane"),
            ("SourceRowURL", "https://example.org/list#row-123", "https://example.org/list#row-456"),
        ):
            with self.subTest(field=changed_field):
                prior = self._import([self._row(**{changed_field: original})])
                conflict = self._import([self._row(**{changed_field: changed})])
                with self.assertRaisesRegex(ValueError, "conflicting_same_time_observation"):
                    reconcile_reviewed_batches(conflict, prior)

    def test_same_instant_reviewer_note_update_is_allowed(self):
        prior = self._import([self._row()])
        re_review = self._import([self._row(ReviewNotes="Rechecked the authority page.")])
        result = reconcile_reviewed_batches(re_review, prior)
        self.assertEqual(result["changed_keys"], [prior[0]["OpportunityKey"]])

    def test_cli_prints_summary_without_reviewed_or_contact_values(self):
        raw_row = self._row(Contact="funding-contact@example.org",
                            ReviewNotes="Reviewed by service lead; internal discussion.")
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "input.json"
            source.write_text(json.dumps({"rows": [raw_row]}), encoding="utf-8")
            output = io.StringIO()
            args = [str(source), "--source", "nhmrc", "--official-host", "example.org"]
            with contextlib.redirect_stdout(output):
                self.assertEqual(main(args), 0)
        visible = output.getvalue()
        self.assertNotIn("funding-contact@example.org", visible)
        self.assertNotIn("internal discussion", visible)
        self.assertNotIn("GO-123", visible)
        self.assertNotIn("Reviewed opportunity", visible)
        self.assertNotIn("input.json", visible)
        summary = json.loads(visible)
        self.assertEqual(summary["status"], "validated_reviewed_import")
        self.assertEqual(summary["validated_row_count"], 1)
        self.assertNotIn("current_batch_digest", summary)
        self.assertFalse(summary["tenant_admission"])
        self.assertTrue(summary["raw_records_omitted"])

    def test_cli_full_receipt_is_private_and_never_printed(self):
        raw_row = self._row(Contact="funding-contact@example.org")
        with tempfile.TemporaryDirectory() as input_directory, \
                tempfile.TemporaryDirectory(dir=PRIVATE_OPS_ROOT) as private_directory:
            source = Path(input_directory) / "input.json"
            source.write_text(json.dumps({"rows": [raw_row]}), encoding="utf-8")
            receipt_path = Path(private_directory) / "reviewed-import.json"
            output = io.StringIO()
            args = [str(source), "--source", "nhmrc", "--official-host", "example.org",
                    "--out", str(receipt_path)]
            with contextlib.redirect_stdout(output):
                self.assertEqual(main(args), 0)
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            self.assertEqual(receipt["validated_row_count"], 1)
            self.assertEqual(receipt["records"][0]["Contact"], "funding-contact@example.org")
            self.assertNotIn("funding-contact@example.org", output.getvalue())

    def test_cli_rejects_nonprivate_or_overwrite_output_before_reading_input(self):
        with tempfile.TemporaryDirectory() as outside:
            invalid_output = Path(outside) / "raw.json"
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as raised:
                main(["missing-input.json", "--official-host", "example.org", "--out", str(invalid_output)])
            self.assertEqual(raised.exception.code, 2)

        with tempfile.TemporaryDirectory(dir=PRIVATE_OPS_ROOT) as private_directory:
            existing = Path(private_directory) / "existing.json"
            existing.write_text("{}", encoding="utf-8")
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as raised:
                main(["missing-input.json", "--official-host", "example.org", "--out", str(existing)])
            self.assertEqual(raised.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
