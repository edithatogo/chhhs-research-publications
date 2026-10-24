from copy import deepcopy
import unittest

from scripts.prepare_dora_pacing import prepare
from scripts.prepare_ingestion_low_copy import fingerprint


class DoRAPacingTests(unittest.TestCase):
    def definition(self):
        return {"triggers": {"daily": {"type": "Recurrence"}}, "actions": {
            "Before": {"type": "Compose", "inputs": True},
            "For_each_record": {"type": "Foreach", "runAfter": {"Before": ["Succeeded"]},
                "foreach": "@variables('FirstKeys')", "runtimeConfiguration": {"concurrency": {"repetitions": 1}},
                "actions": {
                    "Polite_record_delay": {"runAfter": {}, "type": "Wait", "inputs": {"interval": {"count": 5, "unit": "Second"}}},
                    "Guard_handle_key": {"type": "Compose", "runAfter": {"Polite_record_delay": ["Succeeded"]},
                        "inputs": "@if(and(greater(int(items('For_each_record')),0),equals(string(int(items('For_each_record'))),items('For_each_record'))),true,json('GUARD_FAILED'))"},
                    "Get_full_record": {"type": "Http", "runAfter": {"Guard_handle_key": ["Succeeded"]},
                        "inputs": {"method": "GET", "uri": "https://example.org", "retryPolicy": {"type": "none"}}},
                    "Save": {"type": "Compose", "runAfter": {"Get_full_record": ["Succeeded"]}, "inputs": "@body('Get_full_record')"}
                }}}}

    def test_serial_admission_precedes_delay_and_request(self):
        d = self.definition()
        before = deepcopy(d)
        r = prepare(d, fingerprint(d))["definition"]
        a = r["actions"]["For_each_record"]["actions"]
        self.assertEqual(d, before)
        self.assertEqual(r["triggers"], d["triggers"])
        self.assertEqual(a["Guard_handle_key"]["runAfter"], {})
        self.assertIn("equals(variables('DoRAProviderFailed'),false)", a["Guard_handle_key"]["inputs"])
        self.assertEqual(a["Polite_record_delay"]["runAfter"], {"Guard_handle_key": ["Succeeded"]})
        self.assertEqual(a["Get_full_record"]["runAfter"], {"Polite_record_delay": ["Succeeded"]})
        self.assertEqual(a["Polite_record_delay"]["inputs"]["interval"]["count"], 10)
        self.assertEqual(a["Get_full_record"]["inputs"], d["actions"]["For_each_record"]["actions"]["Get_full_record"]["inputs"])
        self.assertEqual(a["Save"], d["actions"]["For_each_record"]["actions"]["Save"])

    def test_failure_latch_and_root_initializer(self):
        d = self.definition()
        r = prepare(d, fingerprint(d))["definition"]
        self.assertEqual(r["actions"]["Initialize_DoRA_provider_failure"]["runAfter"], {"Before": ["Succeeded"]})
        loop = r["actions"]["For_each_record"]
        self.assertEqual(loop["runAfter"], {"Initialize_DoRA_provider_failure": ["Succeeded"]})
        latch = loop["actions"]["Latch_DoRA_provider_failure"]
        self.assertEqual(latch["runAfter"], {"Get_full_record": ["Failed", "TimedOut"]})
        self.assertIs(latch["inputs"]["value"], True)

    def test_drift_and_concurrent_or_repeated_application_rejected(self):
        d = self.definition()
        with self.assertRaises(ValueError):
            prepare(d, "0" * 64)
        d["actions"]["For_each_record"]["runtimeConfiguration"]["concurrency"]["repetitions"] = 2
        with self.assertRaises(ValueError):
            prepare(d, fingerprint(d))
        d = self.definition()
        r = prepare(d, fingerprint(d))["definition"]
        with self.assertRaises(ValueError):
            prepare(r, fingerprint(r))
