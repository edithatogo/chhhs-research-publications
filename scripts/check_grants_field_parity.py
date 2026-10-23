"""Read-only comparison of a saved Grants Registry model, contract and native fields.

Model string columns can represent values from SharePoint Text/Note/Choice/URL;
they do not establish that the SharePoint physical field has the required type.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


PHYSICAL_TYPES = {"text": "Text", "multiline_text": "Note", "choice": "Choice", "url": "URL"}


def _bool(value: object) -> bool:
    return value is True or str(value).lower() == "true"


def _bool_metadata_is_well_formed(value: object) -> bool:
    return type(value) is bool or (isinstance(value, str) and value.casefold() in {"true", "false"})


def _choice_values(value: object) -> list[str] | None:
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return value
    # SharePoint OData verbose wraps multi-value properties in this shape.
    if (isinstance(value, dict) and set(value) == {"results"}
            and isinstance(value["results"], list)
            and all(isinstance(item, str) for item in value["results"])):
        return value["results"]
    return None


def parse_tmdl(text: str) -> dict[str, str]:
    """Return source-column to type, ignoring SharePoint's generated columns."""
    result: dict[str, str] = {}
    for match in re.finditer(r"(?m)^\s*column (?:'([^']+)'|([^\s]+))\s*\n(.*?)(?=^\s*(?:column |partition |annotation PBI_ResultType)|\Z)", text, re.S | re.M):
        body = match.group(3)
        dtype = re.search(r"(?m)^\s*dataType: ([A-Za-z0-9]+)\s*$", body)
        source = re.search(r"(?m)^\s*sourceColumn: (.+?)\s*$", body)
        if dtype and source:
            name = source.group(1).strip("'")
            if name in result:
                raise ValueError(f"duplicate model source column: {name}")
            result[name] = dtype.group(1)
    return result


def validate_native_inventory(native: dict) -> list[dict]:
    """Require a structurally complete native field readback before parity checks."""
    if not isinstance(native, dict):
        raise ValueError("complete exact-target native field inventory required")
    inventory = native.get("inventory")
    fields = native.get("all_native_fields")
    if (native.get("complete") is not True
            or native.get("list_id_matches_prior") is not True
            or not isinstance(inventory, dict)
            or inventory.get("complete") is not True
            or inventory.get("includes_hidden_and_system") is not True
            or inventory.get("continuation_exhausted") is not True
            or not isinstance(fields, list) or not fields
            or type(inventory.get("field_count")) is not int
            or inventory["field_count"] != len(fields)):
        raise ValueError("complete exact-target native field inventory required")
    names = [field.get("InternalName") if isinstance(field, dict) else None for field in fields]
    if any(not isinstance(name, str) or not name or name != name.strip() for name in names):
        raise ValueError("native field inventory contains an invalid internal name")
    if len(set(names)) != len(names):
        raise ValueError("native field inventory contains duplicate internal names")
    return fields


def validate_configured_inventory(native: dict, expected_names: set[str], expected_list_id: str) -> list[dict]:
    """Require a complete, exact-target inventory of configured contract fields.

    This bounded scope is for validating the writable contract columns only. It
    deliberately does not claim that hidden, computed, or system fields have
    been inventoried; callers must select it explicitly and bind the list ID.
    """
    if not isinstance(native, dict):
        raise ValueError("complete exact-target configured-field inventory required")
    fields = native.get("configured_fields")
    target = native.get("target")
    if (native.get("complete_configured_contract_fields") is not True
            or not isinstance(target, dict)
            or not isinstance(expected_list_id, str) or not expected_list_id
            or target.get("list_id") != expected_list_id
            or not isinstance(fields, list)
            or type(native.get("configured_field_count")) is not int
            or native["configured_field_count"] != len(fields)
            or native["configured_field_count"] != len(expected_names)):
        raise ValueError("complete exact-target configured-field inventory required")
    names = [field.get("InternalName") if isinstance(field, dict) else None for field in fields]
    if (any(not isinstance(name, str) or not name or name != name.strip() for name in names)
            or len(set(names)) != len(names)
            or set(names) != expected_names):
        raise ValueError("configured native fields must exactly match contract field names")
    required_metadata = {"TypeAsString", "ReadOnlyField", "Hidden", "Required", "Indexed", "EnforceUniqueValues"}
    for field in fields:
        if not required_metadata.issubset(field):
            raise ValueError("configured native field metadata is incomplete")
    return fields


def compare(schema: dict, model_text: str, native: dict, *, scope: str = "all_native",
            expected_list_id: str | None = None) -> dict:
    fields = schema["fields"]
    names = [field["display_name"] for field in fields]
    if len(set(names)) != len(names):
        raise ValueError("duplicate schema field")
    model = parse_tmdl(model_text)
    if scope == "all_native":
        native_fields = validate_native_inventory(native)
    elif scope == "configured_contract":
        native_fields = validate_configured_inventory(native, set(names), expected_list_id or "")
    else:
        raise ValueError("scope must be all_native or configured_contract")
    findings = []
    for field in fields:
        name = field["display_name"]
        dtype = model.get(name)
        # Title has computed, read-only display aliases. Match the actual writable field.
        matches = [item for item in native_fields if item.get("InternalName") == name
                   and (scope == "configured_contract"
                        or (not _bool(item.get("ReadOnlyField")) and not _bool(item.get("Hidden"))))]
        errors = []
        if dtype != "string":
            errors.append("model_missing_or_nonstring")
        if len(matches) != 1:
            errors.append("native_writable_field_count")
        else:
            actual = matches[0]
            if scope == "configured_contract":
                for native_name in ("ReadOnlyField", "Hidden", "Required", "Indexed", "EnforceUniqueValues"):
                    if not _bool_metadata_is_well_formed(actual.get(native_name)):
                        errors.append("native_metadata_invalid_" + native_name)
            if actual.get("TypeAsString") != PHYSICAL_TYPES[field["type"]]:
                errors.append("native_physical_type")
            if _bool(actual.get("ReadOnlyField")) or _bool(actual.get("Hidden")):
                errors.append("native_not_writable_or_hidden")
            for property_name, native_name in (("required", "Required"), ("indexed", "Indexed"), ("unique", "EnforceUniqueValues")):
                if property_name in field and _bool(actual.get(native_name)) != field[property_name]:
                    errors.append("native_" + property_name)
            if "choices" in field:
                choices = _choice_values(actual.get("Choices"))
                if choices != field["choices"]:
                    errors.append("native_choices")
        findings.append({"field": name, "model_type": dtype, "model_value_compatible": dtype == "string",
                         "expected_native_type": PHYSICAL_TYPES[field["type"]],
                         "native_type": matches[0].get("TypeAsString") if len(matches) == 1 else None,
                         "native_internal_name": matches[0].get("InternalName") if len(matches) == 1 else None,
                         "errors": errors})
    return {"schema_version": schema.get("schema_version"), "field_count": len(fields),
            "model_value_compatible_count": sum(f["model_value_compatible"] for f in findings),
            "native_scope": scope,
            "native_field_inventory_complete": scope == "all_native",
            "configured_contract_inventory_complete": True,
            "native_field_count": len(native_fields),
            "native_physical_parity": all(not f["errors"] for f in findings),
            "findings": findings,
            "boundary": "Saved metadata comparison only; no refresh, row parity, native runtime or tenant acceptance proof."}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--scope", choices=("all_native", "configured_contract"), default="all_native",
                        help="all_native requires every hidden/system field; configured_contract compares only exact contract fields")
    parser.add_argument("--expected-list-id", help="required with configured_contract to bind the receipt to the approved exact list")
    args = parser.parse_args()
    private_ops = (Path(__file__).resolve().parent.parent / "private" / "ops").resolve()
    output = args.output.resolve()
    inputs = {args.schema.resolve(), args.model.resolve(), args.native.resolve()}
    if not output.is_relative_to(private_ops) or output in inputs:
        parser.error("output must be a separate file under ignored private/ops")
    schema = json.loads(args.schema.read_text())
    model_text = args.model.read_text()
    native = json.loads(args.native.read_text())
    try:
        if args.scope == "all_native":
            validate_native_inventory(native)
        elif not args.expected_list_id:
            parser.error("--expected-list-id is required with configured_contract scope")
    except ValueError as exc:
        parser.error(str(exc))
    result = compare(schema, model_text, native, scope=args.scope, expected_list_id=args.expected_list_id)
    result["input_sha256"] = {key: hashlib.sha256(path.read_bytes()).hexdigest() for key, path in
                              (("schema", args.schema), ("model", args.model), ("native", args.native))}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(f"fields={result['field_count']} model_compatible={result['model_value_compatible_count']} native_physical_parity={result['native_physical_parity']}")
    return 0 if result["native_physical_parity"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
