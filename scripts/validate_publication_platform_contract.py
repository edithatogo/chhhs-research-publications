"""Validate the local publication SharePoint flow contract.

This is a structural guard only. It does not certify tenant state or a live run.
"""
from __future__ import annotations

import json
from pathlib import Path
import zipfile


ROOT = Path(__file__).resolve().parent.parent
PACKAGE = ROOT / "private" / "ops" / "flow-packages" / "sharepoint-upsert.zip"


def _graph_errors(actions: dict, scope: str = "root") -> list[str]:
    errors: list[str] = []
    names = set(actions)
    for name, action in actions.items():
        unknown = set((action.get("runAfter") or {})) - names
        if unknown:
            errors.append(f"{scope}.{name} has unknown runAfter action(s): {sorted(unknown)}")
        for branch in ("actions", "else"):
            nested = action.get(branch, {})
            if branch == "else":
                nested = nested.get("actions", {}) if isinstance(nested, dict) else {}
            if isinstance(nested, dict):
                errors.extend(_graph_errors(nested, f"{scope}.{name}.{branch}"))
    return errors


def _definition() -> dict:
    with zipfile.ZipFile(PACKAGE) as archive:
        name = next(n for n in archive.namelist() if n.endswith("/definition.json"))
        return json.loads(archive.read(name))["properties"]["definition"]


def validate(definition: dict) -> list[str]:
    errors: list[str] = []
    actions = definition.get("actions", {})
    errors.extend(_graph_errors(actions))
    loop = actions.get("Apply_to_each_Publication", {})
    if loop.get("type") != "Foreach":
        errors.append("registry writes must be inside an explicit record loop")
    if not loop.get("foreach") or "rows" not in str(loop.get("foreach")):
        errors.append("record loop must consume the validated query rows")
    if loop.get("runtimeConfiguration", {}).get("concurrency", {}).get("repetitions") != 1:
        errors.append("record loop must use single-write concurrency")
    record_actions = loop.get("actions", {})
    get_items = record_actions.get("SharePoint_Get_items", {})
    get_inputs = get_items.get("inputs", {})
    host = get_inputs.get("host", {})
    parameters = get_inputs.get("parameters", {})

    if host.get("apiId") != "/providers/Microsoft.PowerApps/apis/shared_sharepointonline":
        errors.append("registry lookup must use the SharePoint Online connector")
    if not parameters.get("dataset") or not parameters.get("table"):
        errors.append("registry lookup must specify site and list identifiers")
    if "SourceKey" not in str(parameters.get("$filter", "")):
        errors.append("registry lookup must filter by SourceKey")

    condition = record_actions.get("Condition_Is_New_Publication", {})
    if "length(body('SharePoint_Get_items')?['value'])" not in json.dumps(condition):
        errors.append("registry upsert must branch on SharePoint lookup result")

    create = condition.get("actions", {}).get("SharePoint_Create_item", {})
    create_text = json.dumps(create)
    if "item/field_19" not in create_text or "item/field_20" not in create_text:
        errors.append("new records must set first and last observed timestamps")

    update = condition.get("else", {}).get("actions", {}).get("SharePoint_Update_item", {})
    update_text = json.dumps(update)
    if "item/field_20" not in update_text or "item/field_19" in update_text:
        errors.append("existing records must update last observed without overwriting first observed")

    duplicate = record_actions.get("Condition_Duplicate_SourceKey", {})
    if "greater" not in json.dumps(duplicate) or "DUPLICATE_SOURCE_KEY" not in json.dumps(duplicate):
        errors.append("duplicate SourceKey results must fail closed")
    if "replace(" not in str(parameters.get("$filter", "")):
        errors.append("SourceKey filter must escape apostrophes")
    if any(name in actions for name in {"SharePoint_Get_items", "Condition_Is_New_Publication", "SharePoint_Create_item", "SharePoint_Update_item"}):
        errors.append("record-scoped SharePoint actions must not be top-level")

    if "shared_onedriveforbusiness" in json.dumps(definition).lower():
        errors.append("registry definition must not use OneDrive for registry persistence")
    return errors


def main() -> int:
    if not PACKAGE.exists():
        print(f"SKIP: private package not present: {PACKAGE}")
        return 0
    errors = validate(_definition())
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print("PASS: publication SharePoint flow contract is structurally valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
