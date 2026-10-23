import copy
import hashlib
import json
from pathlib import Path
import unittest

from scripts.grants_deadline_schedule import attach_nih_schedule, canonical_object, NIH_SOURCE
from scripts.grants_registry import normalize_opportunity, sharepoint_field_map
from scripts.grants_ingestion import _machine_source_record
from scripts.prepare_grants_schedule_native import model_candidate, patch_flow


class ScheduleTests(unittest.TestCase):
    def setUp(self):
        self.row = dict(Source="test", SourceID="record", RoundID="round", Title="Synthetic",
                        URL="https://example.org", RetrievedUTC="2026-10-23T12:00:00Z")
        self.prepared = dict(batch={"records": [self.row]}, source_date_facts={"close": "2028-01-07"},
                             attribution="Synthetic attribution")
        occurrence = dict(occurrence_candidate_id="local:1", parent_source_id="test",
                          parent_source_record_id="record", parent_funding_opportunity_number="round",
                          due_date="2027-06-05", application_type="New", source_due_time="17:00:00",
                          source_timezone_rule="applicant local", iana_timezone=None, utc_instant=None,
                          original_extra_field="  preserve   whitespace  ")
        self.candidate = dict(source={"official_nofo_url": "https://example.org"},
                              source_capture={"raw_page_retained": False},
                              observed_on="2026-10-23", as_of_date="2026-10-23",
                              deadline_occurrences=[occurrence])

    def attach(self, candidate=None):
        candidate = candidate or self.candidate
        raw = json.dumps(candidate).encode()
        receipt = dict(candidate_sha256=hashlib.sha256(raw).hexdigest(),
                       confirmed_occurrence_count=len(candidate["deadline_occurrences"]),
                       confirmed_occurrence_dates=[x["due_date"] for x in candidate["deadline_occurrences"]])
        return attach_nih_schedule(self.prepared, raw, receipt)

    def test_schedule_survives_machine_and_registry_without_new_parent_or_effective_date(self):
        result = self.attach()
        machine = _machine_source_record(result["batch"]["records"][0], source="test",
                                         retrieved_at=self.row["RetrievedUTC"])
        mapped = sharepoint_field_map(normalize_opportunity(machine))
        schedule = json.loads(mapped["DeadlineScheduleJSON"])
        self.assertEqual(schedule["occurrences"], self.candidate["deadline_occurrences"])
        self.assertEqual(mapped["OpportunityKey"], normalize_opportunity(self.row)["OpportunityKey"])
        self.assertIsNone(mapped["Deadline"])
        self.assertEqual(mapped["SourceAttribution"], "Synthetic attribution")
        self.assertFalse(result["source_admitted"])
        self.assertFalse(result["native_submission_allowed"])
        self.assertEqual(self.prepared["batch"]["records"], [self.row])

    def test_foreign_occurrence_cannot_attach_to_parent(self):
        candidate = copy.deepcopy(self.candidate)
        candidate["deadline_occurrences"][0]["parent_source_record_id"] = "foreign"
        with self.assertRaisesRegex(ValueError, "identity mismatch"):
            self.attach(candidate)

    def test_duplicate_occurrence_and_unqualified_timezone_rejected(self):
        candidate = copy.deepcopy(self.candidate)
        candidate["deadline_occurrences"] *= 2
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self.attach(candidate)
        candidate = copy.deepcopy(self.candidate)
        candidate["deadline_occurrences"][0]["iana_timezone"] = "Australia/Brisbane"
        with self.assertRaisesRegex(ValueError, "unqualified"):
            self.attach(candidate)

    def test_bad_hash_and_truncated_source_receipt_rejected(self):
        raw = json.dumps(self.candidate).encode()
        with self.assertRaisesRegex(ValueError, "fingerprint"):
            attach_nih_schedule(self.prepared, raw, {"candidate_sha256": "wrong"})
        with self.assertRaisesRegex(ValueError, "reconcile"):
            attach_nih_schedule(self.prepared, raw, {"candidate_sha256": hashlib.sha256(raw).hexdigest(),
                                "confirmed_occurrence_count": 2, "confirmed_occurrence_dates": []})

    def test_ambiguous_json_is_rejected(self):
        for raw in ('{"x":1,"x":2}', '{"x":NaN}', '[]'):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                canonical_object(raw)

    def test_legacy_nih_projection_cannot_erase_schedule_after_admission(self):
        row = dict(self.row, SourceID="357812", RoundID="PA-25-301")
        with self.assertRaisesRegex(ValueError, "complete schedule"):
            _machine_source_record(row, source=NIH_SOURCE, retrieved_at=row["RetrievedUTC"])

    def test_model_patch_preserves_parent_binding_and_requires_preimage_hash(self):
        raw = b"createOrReplace\n\ttable 'Grants Registry'\n\t\tpartition 'Grants Registry' = m\n\t\t\tmode: import\n\t\t\tsource = existing\n"
        result = model_candidate(raw, "let Result = null in Result", expected_sha256=hashlib.sha256(raw).hexdigest())
        self.assertIn(b"source = existing", result)
        self.assertIn(b"measure 'Funding Source Attribution'", result)
        self.assertIn(b"table 'Grants Deadline Occurrences'", result)
        with self.assertRaisesRegex(ValueError, "fingerprint"):
            model_candidate(raw, "", expected_sha256="wrong")

    def test_flow_patch_is_idempotent_and_preserves_bindings_and_triggers(self):
        document = json.loads((Path(__file__).parents[1] / "config/flows/grants-registry-reviewed-import.definition.json").read_text())
        candidate = patch_flow(document)
        self.assertEqual(candidate, patch_flow(candidate))
        self.assertEqual(document["properties"]["definition"]["triggers"], candidate["properties"]["definition"]["triggers"])
        self.assertEqual(document["properties"].get("connectionReferences"), candidate["properties"].get("connectionReferences"))


if __name__ == "__main__":
    unittest.main()
