"""Prepare a narrow, private Update package for the isolated grants flow."""

from __future__ import annotations

import argparse
import copy
import hashlib
import io
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
COUNT = "@length(body('SharePoint_Get_items')?['value'])"


def patch_definition(document: dict) -> dict:
    result = copy.deepcopy(document)
    actions = result["properties"]["definition"]["actions"]["Apply_to_each_Reviewed_Row"]["actions"]
    lookup = actions["SharePoint_Get_items"]["inputs"]["parameters"]
    if lookup.get("$top") != 2 or "OpportunityKey eq" not in lookup.get("$filter", ""):
        raise ValueError("Grants lookup contract has drifted")
    duplicate = actions["Condition_Duplicate_OpportunityKey"]
    if duplicate["expression"] != {"greater": [COUNT, 1]}:
        raise ValueError("Duplicate condition has drifted")
    old = duplicate["actions"]
    if set(old) != {"Terminate_Duplicate_OpportunityKey"} or old["Terminate_Duplicate_OpportunityKey"]["type"] != "Terminate":
        raise ValueError("Duplicate diagnostic has drifted")
    duplicate["actions"] = {"Compose_Duplicate_OpportunityKey_Failure": {
        "type": "Compose",
        "inputs": "@concat('DUPLICATE_OPPORTUNITY_KEY: ', string(item()?['OpportunityKey']))",
    }}
    branch = actions["Condition_Is_New_Opportunity"]
    if branch["expression"] != {"equals": [COUNT, 0]}:
        raise ValueError("Create condition has drifted")
    update_actions = branch["else"]["actions"]
    if set(update_actions) != {"SharePoint_Update_item"}:
        raise ValueError("Update branch has drifted")
    update = update_actions["SharePoint_Update_item"]
    if update["inputs"]["host"].get("operationId") != "PatchItem":
        raise ValueError("Update action has drifted")
    branch["else"]["actions"] = {"Condition_Exactly_One_Opportunity": {
        "type": "If",
        "expression": {"equals": [COUNT, 1]},
        "actions": {"SharePoint_Update_item": update},
        "else": {"actions": {}},
    }}
    return result


def patch_package(source: Path, output: Path, *, expected_sha256: str) -> Path:
    """Prepare an Update candidate from one fingerprinted New package.

    The source archive remains the rollback preimage. Refuse a stale preimage
    and an existing output so neither drift nor a prior candidate is hidden.
    """
    private = (ROOT / "private").resolve()
    if not source.resolve().is_relative_to(private) or not output.resolve().is_relative_to(private):
        raise ValueError("Packages must remain under ignored private/")
    if source.resolve() == output.resolve():
        raise ValueError("Preserve source ZIP for rollback")
    if not isinstance(expected_sha256, str) or len(expected_sha256) != 64:
        raise ValueError("expected_sha256 must be the source package SHA-256")
    source_bytes = source.read_bytes()
    actual_sha256 = hashlib.sha256(source_bytes).hexdigest()
    if actual_sha256 != expected_sha256.lower():
        raise ValueError("source package fingerprint mismatch")
    if output.exists():
        raise FileExistsError(f"refusing to overwrite existing candidate: {output}")
    # Parse the same immutable byte snapshot whose fingerprint was checked;
    # reopening the path here would leave a source-replacement race.
    with zipfile.ZipFile(io.BytesIO(source_bytes)) as archive:
        entries = [(info, archive.read(info.filename)) for info in archive.infolist()]
    names = [info.filename for info, _ in entries]
    definitions = [n for n in names if n.startswith("Microsoft.Flow/flows/") and n.endswith("/definition.json")]
    if len(definitions) != 1 or names.count("manifest.json") != 1 or len(names) != len(set(names)):
        raise ValueError("Expected one flow definition and one manifest")
    changed = []
    for info, data in entries:
        if info.filename == definitions[0]:
            data = json.dumps(patch_definition(json.loads(data)), indent=2, ensure_ascii=False).encode()
        elif info.filename == "manifest.json":
            manifest = json.loads(data)
            flow_id = definitions[0].split("/")[2]
            resource = manifest["resources"].get(flow_id)
            if resource is None or resource.get("type") != "Microsoft.Flow/flows":
                raise ValueError("Manifest flow identity has drifted")
            if resource.get("creationType") != "New":
                raise ValueError("Expected original New package")
            resource["suggestedCreationType"] = "Update"
            resource["creationType"] = "Existing, Update"
            data = json.dumps(manifest, indent=2, ensure_ascii=False).encode()
        changed.append((info, data))
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        raise FileExistsError(f"refusing to overwrite existing candidate: {output}")
    # Exclusive creation closes the race between the preflight and opening the
    # candidate, and preserves any candidate another owner created meanwhile.
    with output.open("xb") as stream:
        with zipfile.ZipFile(stream, "w") as archive:
            for info, data in changed:
                archive.writestr(info, data)
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--expected-sha256", required=True)
    args = parser.parse_args()
    print(patch_package(args.source, args.output, expected_sha256=args.expected_sha256))
