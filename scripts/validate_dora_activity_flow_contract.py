"""Validate the local DoRA Activity Registry SharePoint flow contract."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFINITION_PATH = ROOT / "config/flows/dora-activity-registry-upsert.definition.json"
SCHEMA_PATH = ROOT / "config/dora-activity-registry.schema.json"
KEY = "DORAActivityKey"
MAPPED_FIELDS = [
    "DORAActivityKey", "DORARecordID", "DORAResourceID", "DORAResourceName",
    "DORAResourceLastModified", "DORAObservedUTC", "DORASourceURL", "Project ID",
    "Review Reference", "HREC (Ethics) Reference Number", "Full Project Title",
    "Short Project Title", "Project Description", "Clinical Trial (Yes/No)",
    "PI Name", "PI Email", "Contact Person Name", "Contact Person Email",
    "Site Name", "Sponsor Name", "Start Date", "Finish Date", "Disease Category",
    "Multi/Single site", "DORA Authority (Yes/No)", "DORA Consent (Yes/No)",
]


def _definition() -> dict[str, Any]:
    return json.loads(DEFINITION_PATH.read_text(encoding="utf-8"))["properties"]["definition"]


def _graph_errors(actions: dict[str, Any], scope: str = "root") -> list[str]:
    errors: list[str] = []
    names = set(actions)
    for name, action in actions.items():
        unknown = set(action.get("runAfter", {})) - names
        if unknown:
            errors.append(f"{scope}.{name} has unknown runAfter action(s): {sorted(unknown)}")
        for branch in ("actions", "else"):
            nested = action.get(branch, {})
            if branch == "else":
                nested = nested.get("actions", {}) if isinstance(nested, dict) else {}
            if isinstance(nested, dict):
                errors.extend(_graph_errors(nested, f"{scope}.{name}.{branch}"))
    return errors


def validate(definition: dict[str, Any]) -> list[str]:
    errors = _graph_errors(definition.get("actions", {}))
    try:
        registry_schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"DoRA registry schema cannot be loaded: {exc}")
        registry_schema = {}
    schema_fields = {
        field.get("name"): field
        for field in registry_schema.get("fields", [])
        if isinstance(field, dict)
    }
    identity_field = schema_fields.get(KEY)
    if not isinstance(identity_field, dict) or identity_field.get("unique") is not True:
        errors.append("DoRA registry schema must declare DORAActivityKey unique")
    trigger = definition.get("triggers", {}).get("manual", {})
    schema = trigger.get("inputs", {}).get("schema", {})
    if trigger.get("type") != "Request" or "ActivityRowsJson" not in schema.get("required", []):
        errors.append("manual trigger must require ActivityRowsJson")
    actions = definition.get("actions", {})
    loop = actions.get("Apply_to_each_DORA_Activity", {})
    if loop.get("type") != "Foreach":
        errors.append("DoRA activity writes must be inside an explicit record loop")
    if loop.get("runtimeConfiguration", {}).get("concurrency", {}).get("repetitions") != 1:
        errors.append("DoRA activity loop must use single-write concurrency")
    nested = loop.get("actions", {})
    lookup = nested.get("SharePoint_Get_items", {})
    lookup_inputs = lookup.get("inputs", {})
    host = lookup_inputs.get("host", {})
    params = lookup_inputs.get("parameters", {})
    if host.get("apiId") != "/providers/Microsoft.PowerApps/apis/shared_sharepointonline":
        errors.append("DoRA lookup must use the SharePoint Online connector")
    if host.get("operationId") != "GetItems":
        errors.append("DoRA lookup must use SharePoint GetItems")
    if KEY not in str(params.get("$filter", "")) or params.get("$top") != 2:
        errors.append("DoRA lookup must cap and filter by DORAActivityKey")
    duplicate = nested.get("Condition_Duplicate_DORAActivityKey", {})
    if "greater" not in json.dumps(duplicate) or "DUPLICATE_DORA_ACTIVITY_KEY" not in json.dumps(duplicate):
        errors.append("duplicate DoRA keys must fail closed")
    is_new = nested.get("Condition_Is_New_DORA_Activity", {})
    if is_new.get("expression", {}).get("equals", [None, None])[1:] != [0]:
        errors.append("DoRA create branch must require zero matches")
    exactly_one = is_new.get("else", {}).get("actions", {}).get("Condition_Exactly_One_DORA_Activity", {})
    if exactly_one.get("expression", {}).get("equals", [None, None])[1:] != [1]:
        errors.append("DoRA update branch must require exactly one match")
    create = is_new.get("actions", {}).get("SharePoint_Create_item", {})
    update = exactly_one.get("actions", {}).get("SharePoint_Update_item", {})
    for label, action, operation in (("create", create, "PostItem"), ("update", update, "PatchItem")):
        action_inputs = action.get("inputs", {})
        action_host = action_inputs.get("host", {})
        action_params = action_inputs.get("parameters", {})
        if action_host.get("apiId") != "/providers/Microsoft.PowerApps/apis/shared_sharepointonline":
            errors.append(f"DoRA {label} must use SharePoint Online")
        if action_host.get("operationId") != operation:
            errors.append(f"DoRA {label} must use SharePoint {operation}")
        if action_params.get("dataset") != params.get("dataset") or action_params.get("table") != params.get("table"):
            errors.append(f"DoRA {label} must target the lookup site and list")
        if not action_inputs.get("authentication"):
            errors.append(f"DoRA {label} must declare connector authentication")
        missing = [field for field in MAPPED_FIELDS if f"item/{field}" not in action_params]
        if missing:
            errors.append(f"DoRA {label} omits mapped field(s): {missing}")
    if "shared_onedriveforbusiness" in json.dumps(definition).lower() or "OneDrive" in json.dumps(definition):
        errors.append("DoRA registry definition must not use OneDrive")
    if any(name in actions for name in {"SharePoint_Get_items", "SharePoint_Create_item", "SharePoint_Update_item"}):
        errors.append("DoRA record-scoped SharePoint actions must not be top-level")
    return errors


if __name__ == "__main__":
    failures = validate(_definition())
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        raise SystemExit(1)
    print("PASS: DoRA Activity Registry SharePoint flow contract is structurally valid")
