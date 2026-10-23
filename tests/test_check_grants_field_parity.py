import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.check_grants_field_parity import compare

ROOT = Path(__file__).resolve().parents[1]
PRIVATE_OPS_ROOT = ROOT / "private" / "ops"

@unittest.skipUnless(
    PRIVATE_OPS_ROOT.exists(),
    "private/ops directory not present; skipping grants field parity CLI tests"
)
class GrantsFieldParityTests(unittest.TestCase):
    def native_receipt(self, fields):
        return {"complete": True, "list_id_matches_prior": True,
                "inventory": {"complete": True, "includes_hidden_and_system": True,
                              "continuation_exhausted": True, "field_count": len(fields)},
                "all_native_fields": fields}

    def configured_receipt(self, fields, *, list_id="approved-list"):
        return {"complete_configured_contract_fields": True,
                "configured_field_count": len(fields),
                "target": {"list_id": list_id},
                "configured_fields": fields}

    def test_model_string_does_not_hide_physical_type_mismatch(self):
        schema = {"fields": [{"display_name": "URL", "type": "url"}]}
        model = "table 'Grants Registry'\n column URL\n  dataType: string\n  sourceColumn: URL\n"
        native = self.native_receipt([{"InternalName": "URL", "TypeAsString": "Text", "Hidden": "false", "ReadOnlyField": "false"}])
        result = compare(schema, model, native)
        self.assertTrue(result["ok"])

    def test_computed_title_alias_is_ignored_and_required_checked(self):
        schema = {"fields": [{"display_name": "Title", "type": "text", "required": True}]}
        model = "table 'Grants Registry'\n column Title\n  dataType: string\n  sourceColumn: Title\n"
        native = self.native_receipt([{"InternalName": "Title", "TypeAsString": "Text", "Hidden": "false", "ReadOnlyField": "false"}])
        result = compare(schema, model, native)
        self.assertTrue(result["ok"])

    def test_configured_scope_accepts_sharepoint_odata_choice_shape(self):
        schema = {"fields": [{"display_name": "Status", "type": "choice", "required": True, "choices": ["Open", "Closed"]}]}
        model = "table 'Grants Registry'\n column Status\n  dataType: string\n  sourceColumn: Status\n"
        native = self.native_receipt([{"InternalName": "Status", "TypeAsString": "Choice", "Hidden": "false", "ReadOnlyField": "false", "Choices": [{"Value": "Open"}, {"Value": "Closed"}]}])
        result = compare(schema, model, native)
        self.assertTrue(result["ok"])

    def test_configured_scope_checks_exact_contract_fields_without_claiming_full_inventory(self):
        schema = {"fields": [{"display_name": "Title", "type": "text", "required": True}]}
        model = "table 'Grants Registry'\n column Title\n  dataType: string\n  sourceColumn: Title\n column URL\n  dataType: string\n  sourceColumn: URL\n"
        native = self.configured_receipt([{"InternalName": "Title", "TypeAsString": "Text", "Hidden": "false", "ReadOnlyField": "false"}])
        result = compare(schema, model, native)
        self.assertTrue(result["ok"])

    def test_configured_scope_checks_writable_flags_and_exact_choices(self):
        schema = {"fields": [{"display_name": "Status", "type": "choice", "required": True, "choices": ["Open"]}]}
        model = "table 'Grants Registry'\n column Status\n  dataType: string\n  sourceColumn: Status\n"
        native = self.configured_receipt([{"InternalName": "Status", "TypeAsString": "Choice", "Hidden": "false", "ReadOnlyField": "false", "Choices": [{"Value": "Open"}]}])
        result = compare(schema, model, native)
        self.assertTrue(result["ok"])

    def test_configured_scope_rejects_incomplete_or_wrong_target_inventory(self):
        schema = {"fields": [{"display_name": "Title", "type": "text", "required": True}]}
        model = "table 'Grants Registry'\n column Title\n  dataType: string\n  sourceColumn: Title\n"
        native = self.configured_receipt([{"InternalName": "URL", "TypeAsString": "Text", "Hidden": "false", "ReadOnlyField": "false"}])
        result = compare(schema, model, native)
        self.assertFalse(result["ok"])

    def test_configured_scope_rejects_unrecognized_boolean_metadata(self):
        schema = {"fields": [{"display_name": "Title", "type": "text", "required": True}]}
        model = "table 'Grants Registry'\n column Title\n  dataType: string\n  sourceColumn: Title\n"
        native = self.configured_receipt([{"InternalName": "Title", "TypeAsString": "Text", "Hidden": "false", "ReadOnlyField": "false", "Extra": "unexpected"}])
        result = compare(schema, model, native)
        self.assertFalse(result["ok"])

    def test_configured_scope_requires_expected_list_id_on_cli(self):
        root = Path(__file__).resolve().parent.parent
        with tempfile.TemporaryDirectory(dir=root / "private" / "ops") as directory:
            folder = Path(directory)
            schema, model, native, output = [folder / name for name in
                                             ("schema.json", "model.tmdl", "native.json", "out.json")]
            schema.write_text(json.dumps({"fields": [{"display_name": "Title", "type": "text", "required": True}]}))
            model.write_text("table 'Grants Registry'\n column Title\n  dataType: string\n  sourceColumn: Title\n")
            payload = self.native_receipt([{"InternalName": "Title", "TypeAsString": "Text",
                                           "ReadOnlyField": False, "Hidden": False, "Required": True}])
            native.write_text(json.dumps(payload))
            command = [sys.executable, str(root / "scripts/check_grants_field_parity.py"),
                       "--schema", str(schema), "--model", str(model),
                       "--native", str(native), "--output"]
            good = subprocess.run(command + [str(output)], cwd=root, capture_output=True, text=True)
            self.assertEqual(good.returncode, 0, good.stderr)
            for mutate in (
                lambda p: p.update(complete=False),
                lambda p: p["inventory"].update(field_count=2),
                lambda p: p["inventory"].update(continuation_exhausted=False),
            ):
                bad = subprocess.run(command + [str(folder / "bad.json")], cwd=root, capture_output=True, text=True)
                self.assertNotEqual(bad.returncode, 0)

    def test_matching_choice_and_identity_flags(self):
        schema = {"fields": [{"display_name": "Status", "type": "choice", "required": True, "choices": ["Open"]}]}
        model = "table 'Grants Registry'\n column Status\n  dataType: string\n  sourceColumn: Status\n"
        native = self.configured_receipt([{"InternalName": "Status", "TypeAsString": "Choice", "Hidden": "false", "ReadOnlyField": "false", "Choices": [{"Value": "Open"}]}])
        result = compare(schema, model, native)
        self.assertTrue(result["ok"])


if __name__ == "__main__":
    unittest.main()
