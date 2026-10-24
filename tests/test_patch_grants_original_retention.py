import json
from pathlib import Path
import unittest

from scripts.patch_grants_original_retention import patch, remove_rejected_auth_annotations


class OriginalRetentionGraphTests(unittest.TestCase):
    def setUp(self):
        self.definition = json.loads((Path(__file__).parents[1] / "config/flows/grants-registry-reviewed-import.definition.json").read_text())["properties"]["definition"]

    def test_reapplication_refuses_instead_of_duplicating_actions(self):
        with self.assertRaisesRegex(ValueError, "already installed"):
            patch(self.definition)

    def test_native_nesting_limit_is_preserved(self):
        def depth(actions, level=0):
            result = level
            for action in actions.values():
                result = max(result, level + 1)
                for nested in [action.get("actions", {}), action.get("else", {}).get("actions", {})]:
                    result = max(result, depth(nested, level + 1))
            return result
        self.assertLessEqual(depth(self.definition["actions"]), 8)

    def test_nih_envelope_validation_precedes_any_row_write(self):
        actions = self.definition["actions"]
        self.assertEqual(actions["Initialize_Row_Failure_Count"]["runAfter"], {"Condition_Require_NIH_Originals": ["Succeeded"]})
        self.assertIn("OriginalResponsesJson", self.definition["triggers"]["manual"]["inputs"]["schema"]["properties"])
        self.assertEqual(self.definition["triggers"]["manual"]["runtimeConfiguration"]["concurrency"]["runs"], 1)

    def test_archive_always_reads_back_before_its_success(self):
        text = json.dumps(self.definition)
        self.assertNotIn('"operationId": "DeleteAttachment"', text)
        for prefix in ["Original_Update"]:
            self.assertIn(f"equals(body('{prefix}_Read_Content')?['$content'],item()?['content_base64'])", text)
            self.assertIn(f"equals(length(body('{prefix}_Found')),0)", text)
            self.assertIn("base64ToBinary(item()?['content_base64'])", text)

    def test_native_auth_annotation_removal_preserves_host_binding(self):
        host = {"connectionName": "existing", "operationId": "GetItems"}
        raw = {"actions": {"Read": {"type": "OpenApiConnection", "inputs": {
            "host": host, "authentication": {"type": "Raw", "value": "@parameters('$authentication')"}}}}}
        cleaned = remove_rejected_auth_annotations(raw)
        self.assertEqual(cleaned["actions"]["Read"]["inputs"], {"host": host})
        self.assertIn("authentication", raw["actions"]["Read"]["inputs"])
        raw["actions"]["Read"]["inputs"]["authentication"] = {"type": "Basic"}
        with self.assertRaisesRegex(ValueError, "unqualified"):
            remove_rejected_auth_annotations(raw)

    def test_json_originals_use_distinct_names_and_binary_readback(self):
        def visit(actions):
            for name, action in actions.items():
                if name in ("Original_Update_Name",):
                    self.assertIn("'raw-original-'", action["inputs"])
                    self.assertIn("'.json'", action["inputs"])
                if name in ("Original_Update_Read_Content",):
                    self.assertEqual(action["inputs"]["host"]["operationId"], "GetFileContent")
                    self.assertIs(action["inputs"]["parameters"]["inferContentType"], False)
                    self.assertNotIn("table", action["inputs"]["parameters"])
                visit(action.get("actions", {}))
                visit(action.get("else", {}).get("actions", {}))
        visit(self.definition["actions"])
        schema = self.definition["actions"]["Condition_Require_NIH_Originals"]["actions"]["Parse_Originals_Envelope"]["inputs"]["schema"]
        self.assertNotIn('"pattern"', json.dumps(schema))
        self.assertEqual(schema["properties"]["EvidenceHash"]["minLength"], 64)

    def test_missing_nih_parent_fails_before_create(self):
        actions = self.definition["actions"]["Apply_to_each_Reviewed_Row"]["actions"]["Condition_OpportunityKey_Present"]["actions"]["Condition_Conflicting_Source_Identity"]["else"]["actions"]["Condition_Is_New_Opportunity"]["actions"]
        self.assertNotIn("Archive_NIH_Create", actions)
        self.assertEqual(actions["SharePoint_Create_item"]["runAfter"], {"Guard_NIH_Parent_Already_Admitted": ["Succeeded"]})
        self.assertIn("NIH_PARENT_NOT_ADMITTED", actions["Guard_NIH_Parent_Already_Admitted"]["inputs"])

    def test_json_upload_is_raw_rest_and_not_binary_attachment_conversion(self):
        archive = self.definition["actions"]["Apply_to_each_Reviewed_Row"]["actions"]["Condition_OpportunityKey_Present"]["actions"]["Condition_Conflicting_Source_Identity"]["else"]["actions"]["Archive_NIH_Update"]["actions"]["Original_Update_Files"]["actions"]
        json_upload = archive["Original_Update_Add_JSON_If_Missing"]
        self.assertIn("not(startsWith(item()?['role'],'attachment-folder-'))", json_upload["expression"])
        action = json_upload["actions"]["Original_Update_Create_JSON"]
        self.assertEqual(action["inputs"]["host"]["operationId"], "HttpRequest")
        params = action["inputs"]["parameters"]
        self.assertIn("/AttachmentFiles/add(FileName=", params["parameters/uri"])
        self.assertEqual(params["parameters/body"], "@base64ToString(item()?['content_base64'])")
        self.assertEqual(params["parameters/headers"]["Content-Type"], "application/octet-stream; charset=utf-8")
        self.assertEqual(action["inputs"]["retryPolicy"], {"type": "none"})
        self.assertEqual(set(archive["Original_Update_Readback_List"]["runAfter"]), {"Original_Update_Add_If_Missing", "Original_Update_Add_JSON_If_Missing"})
