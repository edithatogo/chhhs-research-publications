import json
from pathlib import Path
import unittest

from scripts.patch_grants_original_retention import patch


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
        for prefix in ["Original_Create", "Original_Update"]:
            self.assertIn(f"equals(body('{prefix}_Read_Content')?['$content'],item()?['content_base64'])", text)
            self.assertIn(f"@equals(length(body('{prefix}_Found')),0)", text)
            self.assertIn("base64ToBinary(item()?['content_base64'])", text)
