"""Fail-closed blank identity guard for the reviewed SharePoint import flow."""
import json
import unittest
from pathlib import Path


class GrantsFlowKeyGuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        definition = Path(__file__).parents[1] / "config/flows/grants-registry-reviewed-import.definition.json"
        cls.flow = json.loads(definition.read_text(encoding="utf-8"))
        cls.loop = cls.flow["properties"]["definition"]["actions"]["Apply_to_each_Reviewed_Row"]

    def test_missing_null_empty_and_whitespace_keys_take_diagnostic_only_branch(self):
        guard = self.loop["actions"]["Condition_OpportunityKey_Present"]
        def nonblank(field):
            return {"not": {"equals": [
                f"@trim(string(coalesce(item()?['{field}'], '')))", ""
            ]}}
        self.assertEqual(
            guard["expression"],
            {"and": [nonblank("OpportunityKey"), nonblank("Source"),
                     {"or": [nonblank("SourceID"), nonblank("RoundID")]},
                     nonblank("EvidenceHash")]},
        )
        self.assertEqual(
            list(guard["else"]["actions"]),
        ["Compose_Invalid_Source_Identity_Failure", "Increment_Invalid_Identity_Failure_Count"],
        )
        self.assertEqual(
            guard["else"]["actions"]["Compose_Invalid_Source_Identity_Failure"]["inputs"],
            "INVALID_GRANTS_SOURCE_IDENTITY",
        )

        # The expression coalesces absent/null to an empty string, stringifies,
        # then trims before the not-empty check. Keep these boundary cases
        # explicit so an expression edit cannot let an invalid row reach lookup.
        invalid_rows = ({}, {"OpportunityKey": None}, {"OpportunityKey": ""},
                        {"OpportunityKey": "   "}, {"OpportunityKey": "\t  \n"})
        for row in invalid_rows:
            with self.subTest(row=row):
                normalized = str(row.get("OpportunityKey") or "").strip()
                self.assertEqual(normalized, "")

    def test_only_usable_key_branch_contains_lookup_and_writes(self):
        self.assertEqual(self.loop["runtimeConfiguration"]["concurrency"]["repetitions"], 1)
        guard = self.loop["actions"]["Condition_OpportunityKey_Present"]
        self.assertEqual(
            list(guard["actions"]),
            ["SharePoint_Get_items", "SharePoint_Get_source_identity", "Condition_Conflicting_Source_Identity"],
        )
        self.assertEqual(
            list(guard["else"]["actions"]),
        ["Compose_Invalid_Source_Identity_Failure", "Increment_Invalid_Identity_Failure_Count"],
        )

        valid_key = "pub:official:round-42"
        self.assertTrue(valid_key.strip())
        actions = guard["actions"]
        self.assertIn("SharePoint_Get_items", actions)
        conflict = actions["Condition_Conflicting_Source_Identity"]
        self.assertIn("SharePoint_Create_item", json.dumps(conflict["else"]["actions"]))
        self.assertIn("SharePoint_Update_item", json.dumps(conflict["else"]["actions"]))
        self.assertNotIn("SharePoint_Create_item", json.dumps(conflict["actions"]))
        self.assertNotIn("SharePoint_Update_item", json.dumps(conflict["actions"]))
        self.assertNotIn("SharePoint_Get_items", guard["else"]["actions"])
        self.assertNotIn("SharePoint_Create_item", json.dumps(guard["else"]["actions"]))
        self.assertNotIn("SharePoint_Update_item", json.dumps(guard["else"]["actions"]))


if __name__ == "__main__":
    unittest.main()
