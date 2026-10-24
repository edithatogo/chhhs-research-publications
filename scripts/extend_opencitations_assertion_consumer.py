"""Extend the stopped assertion consumer, preserving its legacy paths and writer."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path


def extend(clientdata: dict) -> dict:
    result = copy.deepcopy(clientdata)
    definition = result["properties"]["definition"]
    actions = definition["actions"]
    trigger = definition["triggers"]["manual"]
    if set(definition["triggers"]) != {"manual"} or trigger["type"] != "Request" or trigger["kind"] != "Button":
        raise ValueError("Expected existing manual consumer")
    if "Guard_packet_path" in actions or "'opencitations'" in actions["Guard_packet"]["inputs"]:
        raise ValueError("Consumer already extended; reconcile before another save")
    default_path = actions["Read_packet"]["inputs"]["parameters"]["path"]
    if not default_path.endswith("/source-assertions-ready.json"):
        raise ValueError("Unexpected existing packet route")
    folder = default_path.rsplit("/", 1)[0]
    if "'" in folder:
        raise ValueError("Unsupported archive expression escaping")
    prefix = "opencitations-assertions-ready-"
    name = "triggerBody()?['text']"
    remainder = f"replace(replace({name},'{prefix}',''),'.json','')"
    for digit in "0123456789abcdef":
        remainder = f"replace({remainder},'{digit}','')"
    valid_name = f"and(startsWith({name},'{prefix}'),endsWith({name},'.json'),equals(length({name}),{len(prefix) + 69}),equals({remainder},''))"
    actions["Guard_packet_path"] = {"type": "Compose", "runAfter": {}, "inputs":
        f"@if(empty({name}),'{default_path}',if({valid_name},concat('{folder}/',{name}),json('INVALID_ASSERTION_PACKET_NAME')))"}
    trigger["inputs"]["schema"]["properties"]["text"] = {
        "type": "string", "title": "OpenCitations packet name (optional)"}
    actions["Read_packet"]["runAfter"] = {"Guard_packet_path": ["Succeeded"]}
    actions["Read_packet"]["inputs"]["parameters"]["path"] = "@outputs('Guard_packet_path')"
    source = "equals(outputs('Packet')?['source'],'opencitations')"
    scope = "outputs('Packet')?['scope_sha256']"
    valid_packet = ("and(equals(outputs('Packet')?['format'],'rims-source-assertion-verified-v1'),"
                    f"equals(outputs('Packet')?['archive_folder'],'{folder}'),equals(length({scope}),64),"
                    f"equals(outputs('Packet')?['manifest_name'],concat('opencitations-assertion-manifest-',{scope},'.json')),"
                    f"equals(outputs('Packet')?['projection_name'],concat('opencitations-assertion-projection-',{scope},'.json')),"
                    "greater(outputs('Packet')?['count'],0),lessOrEquals(outputs('Packet')?['count'],50))")
    old = actions["Guard_packet"]["inputs"]
    actions["Guard_packet"]["inputs"] = f"@if({source},if({valid_packet},true,json('OPENCITATIONS_PACKET_INVALID')),{old[1:]})"
    actions["Read_manifest"]["inputs"]["parameters"]["path"] = f"@concat(outputs('Packet')?['archive_folder'],'/',if({source},outputs('Packet')?['manifest_name'],'manifest.json'))"
    fields = actions["Stage_fields"]["inputs"]["select"]
    for field, expression in {"Title": "take(item()?['Summary'],255)", "FullSummary": "item()?['Summary']",
                              "ContextKind": "'publication_enrichment_assertion'"}.items():
        fields[field] = f"@if({source},{expression},{fields[field][1:]})"
    if actions["Refresh_records"] != clientdata["properties"]["definition"]["actions"]["Refresh_records"]:
        raise ValueError("Existing protected writer changed")
    if result["properties"]["connectionReferences"] != clientdata["properties"]["connectionReferences"]:
        raise ValueError("Connection references changed")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--expected-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw = args.input.read_bytes()
    if hashlib.sha256(raw).hexdigest() != args.expected_sha256:
        raise ValueError("Native preimage changed")
    candidate = extend(json.loads(raw))
    with args.output.open("x") as stream:
        json.dump(candidate, stream, indent=2)
    print(json.dumps({"prepared": True, "writer_preserved": True, "connections_preserved": True}))
