import copy
import unittest

from scripts.prepare_ingestion_low_copy import fingerprint, prepare


class LowCopyTests(unittest.TestCase):
    def definition(self):
        return {"triggers": {"daily": {"type": "Recurrence"}}, "actions": {
            "Loop": {"type": "Foreach", "foreach": "@outputs('IDs')", "actions": {
                "Fetch": {"type": "Http", "inputs": {"uri": "https://example.org"}},
                "Raw": {"type": "Compose", "inputs": "@string(body('Fetch'))",
                        "runAfter": {"Fetch": ["Succeeded"]}},
                "Save": {"type": "OpenApiConnection", "runAfter": {"Raw": ["Succeeded"]},
                         "inputs": {"body": "@outputs('Raw')"}},
                "Verify": {"type": "Compose", "inputs": "@equals(base64(outputs('Raw')),body('Read'))"}
            }}}}

    def test_archive_serialization_and_trigger_preserved(self):
        before = self.definition()
        snapshot = copy.deepcopy(before)
        result = prepare(before, ["Loop/Raw"], fingerprint(before))
        self.assertEqual(before, snapshot)
        actions = result["definition"]["actions"]["Loop"]["actions"]
        self.assertNotIn("Raw", actions)
        self.assertEqual(actions["Save"]["inputs"]["body"], "@string(body('Fetch'))")
        self.assertEqual(actions["Save"]["runAfter"], {"Fetch": ["Succeeded"]})
        self.assertEqual(actions["Verify"]["inputs"], "@equals(base64(string(body('Fetch'))),body('Read'))")
        self.assertEqual(result["definition"]["triggers"], before["triggers"])

    def test_preimage_drift_rejected(self):
        with self.assertRaises(ValueError):
            prepare(self.definition(), ["Loop/Raw"], "0" * 64)

    def test_failure_or_status_consumers_rejected(self):
        for fault in ("failure", "status", "metadata", "provider"):
            d = self.definition()
            a = d["actions"]["Loop"]["actions"]
            if fault == "failure":
                a["Save"]["runAfter"]["Raw"] = ["Failed"]
            elif fault == "status":
                a["Verify"]["inputs"] = "@actions('Raw')?['status']"
            elif fault == "metadata":
                a["Raw"]["trackedProperties"] = {"proof": True}
            else:
                a["Fetch"]["type"] = "Compose"
            with self.subTest(fault=fault), self.assertRaises(ValueError):
                prepare(d, ["Loop/Raw"], fingerprint(d))

    def test_nonidentity_payload_rejected(self):
        d = self.definition()
        d["actions"]["Loop"]["actions"]["Raw"]["inputs"] = {"body": "@body('Fetch')"}
        with self.assertRaises((ValueError, TypeError)):
            prepare(d, ["Loop/Raw"], fingerprint(d))
