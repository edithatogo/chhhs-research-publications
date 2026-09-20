import json
import unittest
from pathlib import Path


class GrantsFlowContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = Path(__file__).parents[1] / "config/flows/grants-registry-reviewed-import.definition.json"
        cls.definition = json.loads(path.read_text(encoding="utf-8"))
        cls.actions = cls.definition["properties"]["definition"]["actions"]

    def test_manual_reviewed_import_contract_is_sharepoint_only(self):
        text = json.dumps(self.definition)
        self.assertIn("ReviewedRowsJson", text)
        self.assertIn("shared_sharepointonline", text)
        self.assertNotIn("shared_onedriveforbusiness", text)
        self.assertNotIn("OneDrive", text)

    def test_serial_loop_and_key_guard_are_required(self):
        loop = self.actions["Apply_to_each_Reviewed_Row"]
        self.assertEqual(loop["runtimeConfiguration"]["concurrency"]["repetitions"], 1)
        nested = loop["actions"]
        self.assertIn("SharePoint_Get_items", nested)
        self.assertIn("Condition_Duplicate_OpportunityKey", nested)
        self.assertIn("Condition_Is_New_Opportunity", nested)
        duplicate = nested["Condition_Duplicate_OpportunityKey"]
        failure_actions = duplicate["actions"]
        self.assertEqual(list(failure_actions), ["Compose_Duplicate_OpportunityKey_Failure"])
        diagnostic = failure_actions["Compose_Duplicate_OpportunityKey_Failure"]
        self.assertEqual(diagnostic["type"], "Compose")
        self.assertIn("DUPLICATE_OPPORTUNITY_KEY", diagnostic["inputs"])
        is_new = nested["Condition_Is_New_Opportunity"]
        self.assertEqual(is_new["expression"]["equals"][1], 0)

    def test_update_does_not_overwrite_manual_review_fields(self):
        update = self.actions["Apply_to_each_Reviewed_Row"]["actions"]["Condition_Is_New_Opportunity"]["else"]["actions"]["SharePoint_Update_item"]
        params = update["inputs"]["parameters"]
        self.assertNotIn("item/ReviewStatus", params)
        self.assertNotIn("item/ReviewNotes", params)

    def test_sharepoint_operation_ids_and_authentication_are_explicit(self):
        nested = self.actions["Apply_to_each_Reviewed_Row"]["actions"]
        self.assertEqual(nested["SharePoint_Get_items"]["inputs"]["host"]["operationId"], "GetItems")
        create = nested["Condition_Is_New_Opportunity"]["actions"]["SharePoint_Create_item"]
        update = nested["Condition_Is_New_Opportunity"]["else"]["actions"]["SharePoint_Update_item"]
        self.assertEqual(create["inputs"]["host"]["operationId"], "PostItem")
        self.assertEqual(update["inputs"]["host"]["operationId"], "PatchItem")
        self.assertTrue(create["inputs"].get("authentication"))
        self.assertTrue(update["inputs"].get("authentication"))

    def test_placeholders_are_explicit(self):
        text = json.dumps(self.definition)
        self.assertIn("{{SHAREPOINT_SITE_URL}}", text)
        self.assertIn("{{SHAREPOINT_LIST_ID}}", text)


if __name__ == "__main__":
    unittest.main()
