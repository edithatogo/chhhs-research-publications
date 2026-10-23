import hashlib
import json
import tempfile
import unittest
import uuid
import zipfile
from pathlib import Path

from scripts.build_grants_flow_package import DEFAULT_DEFINITION, build_package

SOURCE_DEFINITION_SHA256 = hashlib.sha256(DEFAULT_DEFINITION.read_bytes()).hexdigest()

ROOT = Path(__file__).resolve().parents[1]
PRIVATE_OPS_ROOT = ROOT / "private" / "ops"

@unittest.skipUnless(
    PRIVATE_OPS_ROOT.exists(),
    "private/ops directory not present; skipping grants flow package tests"
)
class GrantsFlowPackageTests(unittest.TestCase):
    def test_private_package_injects_target_without_placeholders(self):
        private_root = Path(__file__).parents[1] / "private"
        private_root.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=private_root) as folder:
            output = Path(folder) / "grants.zip"
            list_id = str(uuid.uuid4())
            build_package(
                output,
                intent="update",
                site_url="https://example.sharepoint.com/personal/dev",
                list_id=list_id,
                flow_id=str(uuid.uuid4()),
                connection_display_name="DEV SharePoint",
                expected_definition_sha256=SOURCE_DEFINITION_SHA256,
            )
            with zipfile.ZipFile(output) as archive:
                names = set(archive.namelist())
                self.assertIn("manifest.json", names)
                self.assertIn("Microsoft.Flow/flows/manifest.json", names)
                definition = json.loads(archive.read(next(n for n in names if n.endswith("/definition.json"))))
                text = json.dumps(definition)
                self.assertNotIn("{{", text)
                self.assertIn("shared_sharepointonline", text)
                self.assertNotIn("shared_onedriveforbusiness", text)
                manifest = json.loads(archive.read("manifest.json"))
                resource = manifest["resources"][definition["name"]]
                self.assertEqual(resource["creationType"], "Update")
                self.assertEqual(resource["suggestedCreationType"], "Update")
                valid_key = definition["properties"]["definition"]["actions"]["Apply_to_each_Reviewed_Row"]["actions"]["Condition_OpportunityKey_Present"]["actions"]
                upsert = valid_key["Condition_Conflicting_Source_Identity"]["else"]["actions"]
                create = upsert["Condition_Is_New_Opportunity"]["actions"]["SharePoint_Create_item"]["inputs"]["parameters"]
                update = upsert["Condition_Is_New_Opportunity"]["else"]["actions"]["Condition_Exactly_One_Opportunity"]["actions"]["Condition_Observation_Time_Known"]["actions"]["Condition_Observation_Not_Older"]["actions"]["SharePoint_Update_item"]["inputs"]["parameters"]
                get_items = valid_key["SharePoint_Get_items"]["inputs"]["parameters"]
                source_identity = valid_key["SharePoint_Get_source_identity"]["inputs"]["parameters"]
                conflict = valid_key["Condition_Conflicting_Source_Identity"]
                self.assertEqual(
                    list(conflict["else"]["actions"]),
                    ["Condition_Duplicate_OpportunityKey", "Condition_Is_New_Opportunity"],
                )
                self.assertNotIn("SharePoint_Create_item", json.dumps(conflict["actions"]))
                self.assertNotIn("SharePoint_Update_item", json.dumps(conflict["actions"]))
                self.assertIn("SharePoint_Create_item", json.dumps(conflict["else"]["actions"]))
                self.assertIn("SharePoint_Update_item", json.dumps(conflict["else"]["actions"]))
                self.assertIsInstance(create["item/DeadlinePrecision"], dict)
                self.assertEqual(create["item/DeadlinePrecision"]["Value"], "@{item()?['DeadlinePrecision']}")
                self.assertIsInstance(create["item/Status"], dict)
                self.assertIsInstance(create["item/CHHHSRelevance"], dict)
                self.assertEqual(create["item/URL"], "@{item()?['URL']}")
                self.assertEqual(update["item/OpportunityKey"], "@{item()?['OpportunityKey']}")

                # The resolved package is the object imported into the tenant.
                # Check all read/write actions use the exact requested target;
                # a local-definition-only assertion would miss a broken
                # placeholder substitution in this packaging boundary.
                target = "https://example.sharepoint.com/personal/dev"
                expected_list = str(uuid.UUID(list_id))
                for name, parameters in (("lookup", get_items), ("source identity lookup", source_identity), ("create", create), ("update", update)):
                    with self.subTest(action=name):
                        self.assertEqual(parameters["dataset"], target)
                        self.assertEqual(parameters["table"], expected_list)

    def test_rejects_non_guid_list(self):
        private_root = Path(__file__).parents[1] / "private"
        private_root.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=private_root) as folder:
            with self.assertRaises(ValueError):
                build_package(Path(folder) / "x.zip", intent="update", site_url="https://example.org", list_id="bad",
                              flow_id=str(uuid.uuid4()), connection_display_name="DEV",
                              expected_definition_sha256=SOURCE_DEFINITION_SHA256)

    def test_refuses_same_output_overwrite(self):
        private_root = Path(__file__).parents[1] / "private"
        private_root.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=private_root) as folder:
            output = Path(folder) / "existing.zip"
            output.write_bytes(b"preserve existing artifact")
            with self.assertRaisesRegex(FileExistsError, "refusing to overwrite"):
                build_package(
                    output,
                    intent="update",
                    site_url="https://example.sharepoint.com/sites/dev",
                    list_id=str(uuid.uuid4()),
                    flow_id=str(uuid.uuid4()),
                    connection_display_name="DEV",
                    expected_definition_sha256=SOURCE_DEFINITION_SHA256,
                )
            self.assertEqual(output.read_bytes(), b"preserve existing artifact")

    def test_rejects_malformed_or_credential_bearing_site_url(self):
        private_root = Path(__file__).parents[1] / "private"
        private_root.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=private_root) as folder:
            for site_url in ("https://", "https://user:secret@example.org/site", "https://example.org/site?token=x"):
                with self.subTest(site_url=site_url), self.assertRaises(ValueError):
                    build_package(
                        Path(folder) / "x.zip",
                        intent="update",
                        site_url=site_url,
                        list_id=str(uuid.uuid4()),
                        flow_id=str(uuid.uuid4()),
                        connection_display_name="DEV",
                        expected_definition_sha256=SOURCE_DEFINITION_SHA256,
                    )

    def test_rejects_empty_or_unresolved_connection_name(self):
        private_root = Path(__file__).parents[1] / "private"
        private_root.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=private_root) as folder:
            for name in (" ", "{{CONNECTION}}", "DEV {{CONNECTION}}"):
                with self.subTest(name=name), self.assertRaisesRegex(ValueError, "concrete connection"):
                    build_package(
                        Path(folder) / "candidate.zip",
                        intent="update",
                        site_url="https://example.sharepoint.com/sites/dev",
                        list_id=str(uuid.uuid4()),
                        flow_id=str(uuid.uuid4()),
                        connection_display_name=name,
                        expected_definition_sha256=SOURCE_DEFINITION_SHA256,
                    )

    def test_manifest_records_explicit_create_or_update_intent(self):
        private_root = Path(__file__).parents[1] / "private"
        private_root.mkdir(exist_ok=True)
        for intent, expected in (("create", "New"), ("update", "Update")):
            with self.subTest(intent=intent), tempfile.TemporaryDirectory(dir=private_root) as folder:
                output = Path(folder) / "grants.zip"
                build_package(output, intent=intent,
                              site_url="https://example.sharepoint.com/sites/dev",
                              list_id=str(uuid.uuid4()), flow_id=str(uuid.uuid4()),
                              connection_display_name="DEV",
                              expected_definition_sha256=SOURCE_DEFINITION_SHA256)
                with zipfile.ZipFile(output) as archive:
                    manifest = json.loads(archive.read("manifest.json"))
                flow = next(item for item in manifest["resources"].values()
                            if item["type"] == "Microsoft.Flow/flows")
                self.assertEqual(flow["creationType"], expected)
                self.assertEqual(flow["suggestedCreationType"], expected)

    def test_package_intent_cannot_be_implicit_or_unknown(self):
        private_root = Path(__file__).parents[1] / "private"
        private_root.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=private_root) as folder:
            arguments = {"site_url": "https://example.sharepoint.com/sites/dev",
                         "list_id": str(uuid.uuid4()), "flow_id": str(uuid.uuid4()),
                         "connection_display_name": "DEV",
                         "expected_definition_sha256": SOURCE_DEFINITION_SHA256}
            with self.assertRaises(TypeError):
                build_package(Path(folder) / "missing-intent.zip", **arguments)
            with self.assertRaisesRegex(ValueError, "explicit package intent"):
                build_package(Path(folder) / "invalid-intent.zip", intent="replace", **arguments)

    def test_refuses_stale_source_definition_fingerprint(self):
        private_root = Path(__file__).parents[1] / "private"
        private_root.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=private_root) as folder:
            output = Path(folder) / "stale-source.zip"
            with self.assertRaisesRegex(ValueError, "source definition fingerprint mismatch"):
                build_package(
                    output,
                    intent="update",
                    site_url="https://example.sharepoint.com/sites/dev",
                    list_id=str(uuid.uuid4()),
                    flow_id=str(uuid.uuid4()),
                    connection_display_name="DEV",
                    expected_definition_sha256="0" * 64,
                )
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
