import copy
import unittest
from datetime import datetime, timezone

from scripts.preflight_grants_flow_activation import preflight
from scripts.grants_registry import stable_key
from scripts.grants_ingestion import ingest_batches
from scripts.grants_sources import OPPORTUNITY_QUALIFICATION_FIELDS


LIST = "11111111-1111-4111-8111-111111111111"
SITE = "https://example.sharepoint.com/sites/dev"
FLOW = "22222222-2222-4222-8222-222222222222"


def fixtures():
    t = "2026-09-26T00:00:00Z"
    row = {"Title": "Synthetic grant opportunity", "Source": "official", "SourceID": "1", "RoundID": "",
           "EvidenceHash": "abc", "RetrievedUTC": t,
           "ReviewStatus": "Reviewed", "ReviewNotes": "Verified official row."}
    row["OpportunityKey"] = stable_key(row)
    target = {"observed_at_utc": t, "site_url": SITE, "list_id": LIST, "flow_id": FLOW,
              "key_required": True, "key_indexed": True, "key_unique": True}
    flow = {"observed_at_utc": t, "complete": True, "saved_state": "Off", "flow_id": FLOW,
            "serial_loop": True, "exact_match_branches": True,
            "actions": {name: {"site_url": SITE, "list_id": LIST} for name in
                        ("SharePoint_Get_items", "SharePoint_Create_item", "SharePoint_Update_item")}}
    snapshot = {"observed_at_utc": t, "complete": True, "site_url": SITE,
                "list_id": LIST, "count": 1, "rows": [row]}
    batch = {"observed_at_utc": t, "complete": True, "rows": [dict(row)]}
    return {"flow": flow, "target": target, "snapshot": snapshot, "batch": batch}


def check(inputs):
    return preflight(**inputs, checked_at=datetime(2026, 9, 26, 1, tzinfo=timezone.utc))


class GrantsActivationPreflightTests(unittest.TestCase):
    def test_exact_replay_passes_locally(self):
        self.assertTrue(check(fixtures())["accepted"])

    def test_wrong_action_target_or_unproved_native_key_rejects(self):
        for mutation in (lambda x: x["flow"]["actions"]["SharePoint_Update_item"].update(list_id=FLOW),
                         lambda x: x["target"].update(key_unique=False),
                         lambda x: x["flow"].update(saved_state="On")):
            with self.subTest(mutation=mutation):
                inputs = fixtures(); mutation(inputs)
                self.assertFalse(check(inputs)["accepted"])

    def test_required_title_must_be_nonblank_text_in_snapshot_and_batch(self):
        for origin in ("snapshot", "batch"):
            for value in (None, "", "  ", 12, True):
                with self.subTest(origin=origin, value=value):
                    inputs = fixtures()
                    inputs[origin]["rows"][0]["Title"] = value
                    self.assertIn(f"{origin}_title_invalid", check(inputs)["errors"])

    def test_partial_snapshot_and_source_collision_reject(self):
        inputs = fixtures()
        inputs["snapshot"]["count"] = 2
        self.assertIn("snapshot_count_mismatch", check(inputs)["errors"])
        inputs = fixtures()
        inputs["batch"]["rows"][0]["OpportunityKey"] = "grant:other"
        self.assertIn("source_identity_key_collision", check(inputs)["errors"])

    def test_stale_replay_and_order_reject(self):
        inputs = fixtures()
        inputs["batch"]["rows"][0]["RetrievedUTC"] = "2026-09-25T00:00:00Z"
        self.assertIn("older_observation_replay", check(inputs)["errors"])
        inputs = fixtures()
        inputs["snapshot"]["observed_at_utc"] = "2026-09-25T00:00:00Z"
        self.assertIn("stale_or_unordered_binding_snapshot", check(inputs)["errors"])

    def test_batch_duplicates_and_missing_source_identity_reject(self):
        inputs = fixtures()
        inputs["batch"]["rows"].append(copy.deepcopy(inputs["batch"]["rows"][0]))
        self.assertIn("batch_duplicate_key", check(inputs)["errors"])
        inputs = fixtures()
        inputs["batch"]["rows"][0]["SourceID"] = ""
        self.assertIn("batch_identity_incomplete", check(inputs)["errors"])

    def test_unreviewed_or_mismatched_batch_key_rejects(self):
        inputs = fixtures()
        inputs["batch"]["rows"][0]["ReviewStatus"] = "Needs Review"
        self.assertIn("batch_review_unproved", check(inputs)["errors"])
        inputs = fixtures()
        inputs["batch"]["rows"][0]["ReviewNotes"] = ""
        self.assertIn("batch_review_unproved", check(inputs)["errors"])
        inputs = fixtures()
        inputs["batch"]["rows"][0]["OpportunityKey"] = "GRANT:bad"
        self.assertIn("batch_key_does_not_match_source_identity", check(inputs)["errors"])

    def test_source_identity_collision_is_not_hidden_by_changed_evidence_hash(self):
        inputs = fixtures()
        inputs["batch"]["rows"][0]["OpportunityKey"] = "GRANT:changed"
        inputs["batch"]["rows"][0]["EvidenceHash"] = "new-content-hash"
        self.assertIn("source_identity_key_collision", check(inputs)["errors"])

    def test_round_only_identity_can_replay_but_nontext_secondary_id_cannot(self):
        inputs = fixtures()
        for group in (inputs["snapshot"]["rows"], inputs["batch"]["rows"]):
            group[0]["SourceID"] = ""
            group[0]["RoundID"] = "2027-A"
            group[0]["OpportunityKey"] = stable_key(group[0])
        self.assertTrue(check(inputs)["accepted"])
        inputs["batch"]["rows"][0]["SourceID"] = 123
        self.assertIn("batch_identity_incomplete", check(inputs)["errors"])

    def test_stale_or_future_readbacks_reject(self):
        inputs = fixtures()
        inputs["flow"]["observed_at_utc"] = "2026-09-24T00:00:00Z"
        self.assertIn("stale_or_future_readback", check(inputs)["errors"])
        inputs = fixtures()
        inputs["batch"]["observed_at_utc"] = "2026-09-26T01:00:01Z"
        self.assertIn("stale_or_future_readback", check(inputs)["errors"])


class MachineInputPreflightTests(unittest.TestCase):
    """Synthetic qualification never establishes admission of a real source."""

    def setUp(self):
        self.inputs = fixtures()
        t = self.inputs["batch"]["observed_at_utc"]
        self.catalogue = [{
            "source_id": "synthetic-api", "enabled": True, "intake": "api",
            "official_row_hosts": ["example.gov"],
            "reconciliation": {"admission": "opportunity", "entity": "opportunity",
                               "source_id_path": "data[].id"},
            "qualification": {"observed_at": t, **{
                field: {"status": "verified", "evidence_refs": ["https://example.gov/evidence"]}
                for field in OPPORTUNITY_QUALIFICATION_FIELDS}}}]
        self.catalogue[0]["qualification"]["access"]["decision"] = "public"
        self.catalogue[0]["qualification"]["reuse_terms"]["decision"] = "permitted"
        self.envelopes = [{"source": "synthetic-api", "retrieved_at": t,
                           "pagination": {"total_pages": 1, "pages_received": [1], "complete": True},
                           "records": [{"SourceID": "1", "Title": "Synthetic API opportunity",
                                        "URL": "https://example.gov/opportunity/1"}]}]
        self.inputs["snapshot"].update(rows=[], count=0)
        self.inputs["batch"]["rows"] = ingest_batches(
            self.envelopes, catalogue=self.catalogue)["records"]

    def run_preflight(self):
        return preflight(**self.inputs, input_mode="machine", machine_catalogue=self.catalogue,
                         machine_batches=self.envelopes,
                         checked_at=datetime(2026, 9, 26, 1, tzinfo=timezone.utc))

    def test_admitted_machine_facts_do_not_need_or_create_review_decision(self):
        result = self.run_preflight()
        self.assertTrue(result["accepted"], result)
        self.assertEqual(result["input_mode"], "machine")
        self.assertEqual(self.inputs["batch"]["rows"][0]["ReviewStatus"], "Needs Review")
        self.assertEqual(self.inputs["batch"]["rows"][0]["ReviewNotes"], "")

    def test_unqualified_or_disabled_source_cannot_bypass_review(self):
        for mutation in (lambda: self.catalogue[0].update(enabled=False),
                         lambda: self.catalogue[0]["qualification"]["stable_identity"].update(status="partial")):
            with self.subTest(mutation=mutation):
                self.setUp()
                mutation()
                self.assertIn("machine_source_admission_failed", self.run_preflight()["errors"])

    def test_prepared_row_must_match_entire_admitted_projection(self):
        for field, value in [("Title", "altered"), ("EvidenceHash", "altered"),
                             ("ReviewStatus", "Reviewed"), ("ReviewNotes", "invented review")]:
            with self.subTest(field=field):
                self.setUp()
                self.inputs["batch"]["rows"][0][field] = value
                self.assertIn("machine_projection_mismatch", self.run_preflight()["errors"])

    def test_partial_or_extra_failed_source_is_not_accepted(self):
        self.envelopes[0]["pagination"]["complete"] = False
        self.assertIn("machine_source_admission_failed", self.run_preflight()["errors"])
        self.setUp()
        extra = copy.deepcopy(self.envelopes[0])
        extra["source"] = "unknown"
        self.envelopes.append(extra)
        self.assertIn("machine_source_admission_failed", self.run_preflight()["errors"])

    def test_shared_binding_and_native_uniqueness_guards_remain_required(self):
        self.inputs["flow"]["actions"]["SharePoint_Update_item"]["list_id"] = FLOW
        self.inputs["target"]["key_unique"] = False
        result = self.run_preflight()
        self.assertIn("SharePoint_Update_item_target_mismatch", result["errors"])
        self.assertIn("missing_native_unique_key_proof", result["errors"])

    def test_mode_and_proof_inputs_cannot_be_omitted_or_mixed(self):
        result = preflight(**self.inputs, input_mode="machine")
        self.assertIn("machine_admission_inputs_missing", result["errors"])
        result = preflight(**self.inputs, machine_catalogue=self.catalogue,
                           machine_batches=self.envelopes)
        self.assertIn("machine_inputs_require_machine_mode", result["errors"])
        self.assertIn("batch_review_unproved", result["errors"])


if __name__ == "__main__":
    unittest.main()
