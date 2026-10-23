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


def native_receipt(fields):
    return {"complete": True, "list_id_matches_prior": True,
            "inventory": {"complete": True, "includes_hidden_and_system": True,
                          "continuation_exhausted": True, "field_count": len(fields)},
            "all_native_fields": fields}


def configured_receipt(fields, *, list_id="approved-list"):
    return {"complete_configured_contract_fields": True,
            "configured_field_count": len(fields),
            "target": {"list_id": list_id},
            "configured_fields": fields}


class GrantsFieldParityTests(unittest.TestCase):
    def test_model_string_does_not_hide_physical_type_mismatch(self):
        schema = {"fields": [{"display_name": "URL", "type": "url"}]}
        model = "table 'Grants Registry'\n column URL\n  dataType: string\n  sourceColumn: URL\n"
        native = native_receipt([{"InternalName": "URL", "TypeAsString": "Text", "Hidden": "false", "ReadOnlyField": "false"}])
        result = compare(schema, model, native)
        self.assertEqual(result["model_value_compatible_count"], 1)
        self.assertFalse(result["native_physical_parity"])
        self.assertEqual(result["findings"][0]["errors"], ["native_physical_type"])

    def test_computed_title_alias_is_ignored_and_required_checked(self):
        schema = {"fields": [{"display_name": "Title", "type": "text", "required": True}]}
        model = "table 'Grants Registry'\n column Title\n  dataType: string\n  sourceColumn: Title\n"
        native = native_receipt([
            {"InternalName": "LinkTitle", "Title": "Title", "TypeAsString": "Computed", "ReadOnlyField": "true", "Hidden": "false"},
            {"InternalName": "Title", "Title": "Title", "TypeAsString": "Text", "ReadOnlyField": "false", "Hidden": "false", "Required": "false"}])
        result = compare(schema, model, native)
        self.assertEqual(result["findings"][0]["native_internal_name"], "Title")
        self.assertEqual(result["findings"][0]["errors"], ["native_required"])

    def test_matching_choice_and_identity_flags(self):
        schema = {"fields": [{"display_name": "OpportunityKey", "type": "text", "required": True, "indexed": True, "unique": True},
                             {"display_name": "Status", "type": "choice"}]}
        model = "table 'Grants Registry'\n column OpportunityKey\n  dataType: string\n  sourceColumn: OpportunityKey\n column Status\n  dataType: string\n  sourceColumn: Status\n"
        native = native_receipt([
            {"InternalName": "OpportunityKey", "TypeAsString": "Text", "Hidden": "false", "ReadOnlyField": "false", "Required": "true", "Indexed": "true", "EnforceUniqueValues": "true"},
            {"InternalName": "Status", "TypeAsString": "Choice", "Hidden": "false", "ReadOnlyField": "false"}])
        self.assertTrue(compare(schema, model, native)["native_physical_parity"])

    def test_configured_scope_checks_exact_contract_fields_without_claiming_full_inventory(self):
        schema = {"fields": [
            {"display_name": "OpportunityKey", "type": "text", "required": True,
             "indexed": True, "unique": True},
            {"display_name": "DeadlineTemporalStatus", "type": "choice",
             "choices": ["unknown", "zone_resolved"]},
        ]}
        model = ("table 'Grants Registry'\n"
                 " column OpportunityKey\n  dataType: string\n  sourceColumn: OpportunityKey\n"
                 " column DeadlineTemporalStatus\n  dataType: string\n  sourceColumn: DeadlineTemporalStatus\n")
        native = configured_receipt([
            {"InternalName": "OpportunityKey", "TypeAsString": "Text", "ReadOnlyField": False,
             "Hidden": False, "Required": True, "Indexed": True, "EnforceUniqueValues": True},
            {"InternalName": "DeadlineTemporalStatus", "TypeAsString": "Choice", "ReadOnlyField": False,
             "Hidden": False, "Required": False, "Indexed": False, "EnforceUniqueValues": False,
             "Choices": ["unknown", "zone_resolved"]},
        ])
        result = compare(schema, model, native, scope="configured_contract", expected_list_id="approved-list")
        self.assertTrue(result["native_physical_parity"])
        self.assertFalse(result["native_field_inventory_complete"])
        self.assertTrue(result["configured_contract_inventory_complete"])
        self.assertEqual(result["native_scope"], "configured_contract")

    def test_configured_scope_accepts_sharepoint_odata_choice_shape(self):
        schema = {"fields": [{"display_name": "Status", "type": "choice",
                              "choices": ["Open", "Closed"]}]}
        model = "table 'Grants Registry'\n column Status\n  dataType: string\n  sourceColumn: Status\n"
        native = configured_receipt([{
            "InternalName": "Status", "TypeAsString": "Choice", "ReadOnlyField": False,
            "Hidden": False, "Required": False, "Indexed": False, "EnforceUniqueValues": False,
            "Choices": {"results": ["Open", "Closed"]},
        }])
        result = compare(schema, model, native, scope="configured_contract",
                         expected_list_id="approved-list")
        self.assertTrue(result["native_physical_parity"])

    def test_configured_scope_rejects_incomplete_or_wrong_target_inventory(self):
        schema = {"fields": [{"display_name": "Status", "type": "choice"}]}
        model = "table 'Grants Registry'\n column Status\n  dataType: string\n  sourceColumn: Status\n"
        field = {"InternalName": "Status", "TypeAsString": "Choice", "ReadOnlyField": False,
                 "Hidden": False, "Required": False, "Indexed": False, "EnforceUniqueValues": False}
        for native, expected_list_id in (
            (configured_receipt([field], list_id="other-list"), "approved-list"),
            (configured_receipt([], list_id="approved-list"), "approved-list"),
            ({"complete_configured_contract_fields": False, "configured_field_count": 1,
              "target": {"list_id": "approved-list"}, "configured_fields": [field]}, "approved-list"),
        ):
            with self.subTest(native=native), self.assertRaisesRegex(
                ValueError, "complete exact-target configured-field inventory"
            ):
                compare(schema, model, native, scope="configured_contract", expected_list_id=expected_list_id)

    def test_configured_scope_checks_writable_flags_and_exact_choices(self):
        schema = {"fields": [{"display_name": "Status", "type": "choice", "choices": ["Open", "Closed"]}]}
        model = "table 'Grants Registry'\n column Status\n  dataType: string\n  sourceColumn: Status\n"
        field = {"InternalName": "Status", "TypeAsString": "Choice", "ReadOnlyField": True,
                 "Hidden": False, "Required": False, "Indexed": False, "EnforceUniqueValues": False,
                 "Choices": ["Open"]}
        result = compare(schema, model, configured_receipt([field]), scope="configured_contract",
                         expected_list_id="approved-list")
        self.assertEqual(result["findings"][0]["errors"], ["native_not_writable_or_hidden", "native_choices"])

    def test_configured_scope_rejects_unrecognized_boolean_metadata(self):
        schema = {"fields": [{"display_name": "Status", "type": "choice"}]}
        model = "table 'Grants Registry'\n column Status\n  dataType: string\n  sourceColumn: Status\n"
        field = {"InternalName": "Status", "TypeAsString": "Choice", "ReadOnlyField": False,
                 "Hidden": False, "Required": "maybe", "Indexed": False, "EnforceUniqueValues": False}
        result = compare(schema, model, configured_receipt([field]), scope="configured_contract",
                         expected_list_id="approved-list")
        self.assertIn("native_metadata_invalid_Required", result["findings"][0]["errors"])

    def test_configured_scope_requires_expected_list_id_on_cli(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory(dir=root / "private" / "ops") as directory:
            folder = Path(directory)
            schema, model, native, output = [folder / name for name in
                                             ("schema.json", "model.tmdl", "native.json", "out.json")]
            schema.write_text(json.dumps({"fields": [{"display_name": "Status", "type": "choice"}]}))
            model.write_text("table 'Grants Registry'\n column Status\n  dataType: string\n  sourceColumn: Status\n")
            native.write_text(json.dumps(configured_receipt([{
                "InternalName": "Status", "TypeAsString": "Choice", "ReadOnlyField": False,
                "Hidden": False, "Required": False, "Indexed": False, "EnforceUniqueValues": False,
            }])))
            command = [sys.executable, str(root / "scripts/check_grants_field_parity.py"),
                       "--schema", str(schema), "--model", str(model), "--native", str(native),
                       "--output", str(output), "--scope", "configured_contract"]
            rejected = subprocess.run(command, cwd=root, capture_output=True, text=True)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn("--expected-list-id is required", rejected.stderr)
            accepted = subprocess.run(command + ["--expected-list-id", "approved-list"],
                                      cwd=root, capture_output=True, text=True)
            self.assertEqual(accepted.returncode, 0, accepted.stderr)
            result = json.loads(output.read_text())
            self.assertFalse(result["native_field_inventory_complete"])

    def test_cli_requires_complete_exact_native_readback_and_private_output(self):
        root = Path(__file__).resolve().parent.parent
        with tempfile.TemporaryDirectory(dir=root / "private" / "ops") as directory:
            folder = Path(directory)
            schema, model, native, output = [folder / name for name in
                                             ("schema.json", "model.tmdl", "native.json", "out.json")]
            schema.write_text(json.dumps({"fields": [{"display_name": "Title", "type": "text", "required": True}]}))
            model.write_text("table 'Grants Registry'\n column Title\n  dataType: string\n  sourceColumn: Title\n")
            payload = native_receipt([{"InternalName": "Title", "TypeAsString": "Text",
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
                invalid = json.loads(json.dumps(payload))
                mutate(invalid)
                native.write_text(json.dumps(invalid))
                rejected = subprocess.run(command + [str(output)], cwd=root, capture_output=True, text=True)
                self.assertNotEqual(rejected.returncode, 0)
            public = subprocess.run(command + [str(root / "public-parity.json")], cwd=root,
                                    capture_output=True, text=True)
            self.assertNotEqual(public.returncode, 0)


if __name__ == "__main__":
    unittest.main()
