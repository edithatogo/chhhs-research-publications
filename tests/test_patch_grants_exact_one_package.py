import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from scripts.patch_grants_exact_one_package import ROOT, patch_definition, patch_package


class GrantsExactOnePackageTests(unittest.TestCase):
    def setUp(self):
        (ROOT / "private").mkdir(exist_ok=True)
        self.fixture = tempfile.TemporaryDirectory(dir=ROOT / "private")
        self.addCleanup(self.fixture.cleanup)
        self.source = Path(self.fixture.name) / "synthetic-grants.zip"
        count = "@length(body('SharePoint_Get_items')?['value'])"
        flow_id = "00000000-0000-4000-8000-000000000001"
        document = {
            "name": flow_id, "id": "/synthetic/flows/" + flow_id,
            "properties": {"definition": {"actions": {
                "Apply_to_each_Reviewed_Row": {"actions": {
                    "SharePoint_Get_items": {"inputs": {"parameters": {
                        "$top": 2, "$filter": "OpportunityKey eq 'synthetic'"}}},
                    "Condition_Duplicate_OpportunityKey": {
                        "expression": {"greater": [count, 1]},
                        "actions": {"Terminate_Duplicate_OpportunityKey": {"type": "Terminate"}}},
                    "Condition_Is_New_Opportunity": {
                        "expression": {"equals": [count, 0]}, "actions": {},
                        "else": {"actions": {"SharePoint_Update_item": {
                            "inputs": {"host": {"operationId": "PatchItem"}},
                            "type": "OpenApiConnection"}}}},
                    "Unrelated_sentinel": {"type": "Compose", "inputs": "preserve"},
                }}
            }}, "connectionReferences": {"synthetic": {"connectionName": "preserve"}}},
        }
        manifest = {"resources": {flow_id: {
            "type": "Microsoft.Flow/flows", "creationType": "New",
            "suggestedCreationType": "New"}}}
        with zipfile.ZipFile(self.source, "w") as archive:
            archive.writestr("manifest.json", json.dumps(manifest))
            archive.writestr(f"Microsoft.Flow/flows/{flow_id}/definition.json", json.dumps(document))
            archive.writestr("unrelated.txt", "preserve exact bytes")

    def test_narrow_update_and_rollback(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "private") as folder:
            output = Path(folder) / "update.zip"
            original = self.source.read_bytes()
            patch_package(self.source, output, expected_sha256=hashlib.sha256(original).hexdigest())
            self.assertEqual(self.source.read_bytes(), original)
            with zipfile.ZipFile(self.source) as before, zipfile.ZipFile(output) as after:
                self.assertEqual(before.namelist(), after.namelist())
                changed = [n for n in before.namelist() if before.read(n) != after.read(n)]
                definition_name = next(n for n in changed if n.endswith("/definition.json"))
                self.assertEqual(set(changed), {"manifest.json", definition_name})
                old = json.loads(before.read(definition_name))
                new = json.loads(after.read(definition_name))
                self.assertEqual(old["name"], new["name"])
                self.assertEqual(old["id"], new["id"])
                old_actions = old["properties"]["definition"]["actions"]["Apply_to_each_Reviewed_Row"]["actions"]
                new_actions = new["properties"]["definition"]["actions"]["Apply_to_each_Reviewed_Row"]["actions"]
                expected = copy.deepcopy(old_actions)
                expected["Condition_Duplicate_OpportunityKey"]["actions"] = new_actions["Condition_Duplicate_OpportunityKey"]["actions"]
                expected["Condition_Is_New_Opportunity"]["else"]["actions"] = new_actions["Condition_Is_New_Opportunity"]["else"]["actions"]
                self.assertEqual(expected, new_actions)
                self.assertEqual(new_actions["Condition_Is_New_Opportunity"]["else"]["actions"]["Condition_Exactly_One_Opportunity"]["expression"]["equals"][1], 1)
                manifest_old = json.loads(before.read("manifest.json"))
                manifest_new = json.loads(after.read("manifest.json"))
                flow_id = definition_name.split("/")[2]
                manifest_old["resources"][flow_id]["suggestedCreationType"] = "Update"
                manifest_old["resources"][flow_id]["creationType"] = "Existing, Update"
                self.assertEqual(manifest_old, manifest_new)

    def test_rejects_drift_and_same_path(self):
        with zipfile.ZipFile(self.source) as archive:
            name = next(n for n in archive.namelist() if n.endswith("/definition.json"))
            document = json.loads(archive.read(name))
        actions = document["properties"]["definition"]["actions"]["Apply_to_each_Reviewed_Row"]["actions"]
        actions["SharePoint_Get_items"]["inputs"]["parameters"]["$top"] = 1
        with self.assertRaisesRegex(ValueError, "drifted"):
            patch_definition(document)
        with self.assertRaisesRegex(ValueError, "rollback"):
            patch_package(self.source, self.source, expected_sha256=hashlib.sha256(self.source.read_bytes()).hexdigest())

    def test_rejects_stale_preimage_and_existing_candidate(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "private") as folder:
            output = Path(folder) / "update.zip"
            with self.assertRaisesRegex(ValueError, "fingerprint mismatch"):
                patch_package(self.source, output, expected_sha256="0" * 64)
            self.assertFalse(output.exists())
            output.write_bytes(b"preserve existing candidate")
            with self.assertRaisesRegex(FileExistsError, "refusing to overwrite"):
                patch_package(self.source, output, expected_sha256=hashlib.sha256(self.source.read_bytes()).hexdigest())
            self.assertEqual(output.read_bytes(), b"preserve existing candidate")


if __name__ == "__main__":
    unittest.main()
