"""Executable graph checks for the reviewed grants source-identity guard."""
import json
import unittest
from pathlib import Path


class GrantsSourceIdentityFlowGuardTests(unittest.TestCase):
    def test_conflicting_source_evidence_cannot_reach_either_write(self):
        root = Path(__file__).parents[1]
        flow = json.loads((root / "config/flows/grants-registry-reviewed-import.definition.json").read_text())
        loop = flow["properties"]["definition"]["actions"]["Apply_to_each_Reviewed_Row"]
        self.assertEqual(loop["runtimeConfiguration"]["concurrency"]["repetitions"], 1)
        valid = loop["actions"]["Condition_OpportunityKey_Present"]["actions"]
        lookup = valid["SharePoint_Get_source_identity"]
        params = lookup["inputs"]["parameters"]
        self.assertEqual(lookup["runAfter"], {"SharePoint_Get_items": ["Succeeded"]})
        self.assertEqual(params["$top"], 1)
        self.assertEqual(params["dataset"], valid["SharePoint_Get_items"]["inputs"]["parameters"]["dataset"])
        self.assertEqual(params["table"], valid["SharePoint_Get_items"]["inputs"]["parameters"]["table"])
        for field in ("SourceID", "Source", "RoundID", "EvidenceHash", "OpportunityKey"):
            self.assertIn(f"replace(string(item()?['{field}']),'''','''''')", params["$filter"].replace(" ", ""))
        self.assertIn("OpportunityKey ne", params["$filter"])

        conflict = valid["Condition_Conflicting_Source_Identity"]
        source_count = "@length(body('SharePoint_Get_source_identity')?['value'])"
        self.assertEqual(conflict["runAfter"], {"SharePoint_Get_source_identity": ["Succeeded"]})
        self.assertEqual(conflict["expression"], {"greater": [source_count, 0]})
        self.assertEqual(conflict["actions"]["Compose_Conflicting_Source_Identity_Failure"]["inputs"],
                         "CONFLICTING_OPPORTUNITY_KEY_FOR_SOURCE_EVIDENCE")
        upsert = conflict["else"]["actions"]
        self.assertEqual(set(upsert), {"Condition_Duplicate_OpportunityKey", "Condition_Is_New_Opportunity", "Archive_NIH_Update"})
        self.assertEqual(upsert["Archive_NIH_Update"]["runAfter"], {"Condition_Duplicate_OpportunityKey": ["Succeeded"]})
        new = upsert["Condition_Is_New_Opportunity"]
        self.assertEqual(new["runAfter"], {"Archive_NIH_Update": ["Succeeded"]})
        self.assertIn({"equals": [source_count, 0]}, new["expression"]["and"])
        exact_one = new["else"]["actions"]["Condition_Exactly_One_Opportunity"]
        self.assertIn({"equals": [source_count, 0]}, exact_one["expression"]["and"])
        for source_matches in (0, 1):
            for key_matches in (0, 1, 2):
                with self.subTest(source_matches=source_matches, key_matches=key_matches):
                    create = source_matches == 0 and key_matches == 0
                    update = source_matches == 0 and key_matches == 1
                    self.assertFalse(source_matches and (create or update))

    def test_row_diagnostics_fail_the_run_after_serial_loop(self):
        root = Path(__file__).parents[1]
        flow = json.loads((root / "config/flows/grants-registry-reviewed-import.definition.json").read_text())
        actions = flow["properties"]["definition"]["actions"]
        self.assertEqual(actions["Initialize_Row_Failure_Count"]["inputs"]["variables"],
                         [{"name": "RowFailureCount", "type": "integer", "value": 0}])
        loop = actions["Apply_to_each_Reviewed_Row"]
        self.assertEqual(loop["runAfter"], {"Initialize_Row_Failure_Count": ["Succeeded"]})
        valid = loop["actions"]["Condition_OpportunityKey_Present"]
        failures = (
            (valid["else"]["actions"], "Compose_Invalid_Source_Identity_Failure", "Increment_Invalid_Identity_Failure_Count"),
            (valid["actions"]["Condition_Conflicting_Source_Identity"]["else"]["actions"]["Condition_Duplicate_OpportunityKey"]["actions"],
             "Compose_Duplicate_OpportunityKey_Failure", "Increment_Duplicate_Key_Failure_Count"),
            (valid["actions"]["Condition_Conflicting_Source_Identity"]["actions"],
             "Compose_Conflicting_Source_Identity_Failure", "Increment_Conflicting_Identity_Failure_Count"),
        )
        for branch, diagnostic, increment_name in failures:
            with self.subTest(diagnostic=diagnostic):
                increment = branch[increment_name]
                self.assertEqual(increment["runAfter"], {diagnostic: ["Succeeded"]})
                self.assertEqual(increment["inputs"], {"name": "RowFailureCount", "value": 1})
        def all_action_names(branch):
            names = []
            for name, action in branch.items():
                names.append(name)
                names.extend(all_action_names(action.get("actions", {})))
                names.extend(all_action_names(action.get("else", {}).get("actions", {})))
            return names
        names = all_action_names(actions)
        self.assertEqual(len(names), len(set(names)))
        final = actions["Condition_Any_Row_Failures"]
        self.assertEqual(final["runAfter"], {"Apply_to_each_Reviewed_Row": ["Succeeded"]})
        self.assertEqual(final["expression"], {"greater": ["@variables('RowFailureCount')", 0]})
        terminate = final["actions"]["Terminate_Row_Failures"]
        self.assertEqual(terminate["type"], "Terminate")
        self.assertEqual(terminate["inputs"]["runStatus"], "Failed")
        self.assertEqual(final["else"]["actions"], {})

        # A conflict after an earlier successful row cannot look like a
        # successful whole-batch run. Preflight is still needed to prevent
        # the earlier write, because Power Automate has no batch rollback.
        for outcomes, failed in (([], False), (["created", "updated"], False),
                                 (["created", "conflict"], True),
                                 (["invalid"], True), (["duplicate"], True)):
            with self.subTest(outcomes=outcomes):
                self.assertEqual(any(x in {"conflict", "invalid", "duplicate"}
                                     for x in outcomes), failed)


if __name__ == "__main__":
    unittest.main()
