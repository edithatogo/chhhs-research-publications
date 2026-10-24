"""Prepare provider-compliant DoRA pacing and a failure latch; no network effects."""
from copy import deepcopy

from scripts.prepare_ingestion_low_copy import fingerprint


def prepare(definition: dict, expected_sha256: str) -> dict:
    if fingerprint(definition) != expected_sha256:
        raise ValueError("DoRA native preimage drift")
    result = deepcopy(definition)
    root = result["actions"]
    loop = root["For_each_record"]
    actions = loop["actions"]
    delay = actions["Polite_record_delay"]
    guard = actions["Guard_handle_key"]
    request = actions["Get_full_record"]
    if (delay != {"runAfter": {}, "type": "Wait", "inputs": {"interval": {"count": 5, "unit": "Second"}}}
            or guard["runAfter"] != {"Polite_record_delay": ["Succeeded"]}
            or request["runAfter"] != {"Guard_handle_key": ["Succeeded"]}
            or request["type"] != "Http"
            or request["inputs"]["method"] != "GET"
            or request["inputs"]["retryPolicy"] != {"type": "none"}
            or loop.get("runtimeConfiguration", {}).get("concurrency", {}).get("repetitions") != 1
            or "DoRAProviderFailed" in str(definition)
            or not guard["inputs"].startswith("@if(and(")):
        raise ValueError("Unexpected serial DoRA acquisition contract")
    root["Initialize_DoRA_provider_failure"] = {
        "type": "InitializeVariable", "runAfter": deepcopy(loop["runAfter"]),
        "inputs": {"variables": [{"name": "DoRAProviderFailed", "type": "boolean", "value": False}]}}
    loop["runAfter"] = {"Initialize_DoRA_provider_failure": ["Succeeded"]}
    guard["runAfter"] = {}
    guard["inputs"] = guard["inputs"].replace(
        "@if(and(", "@if(and(equals(variables('DoRAProviderFailed'),false),", 1)
    delay["runAfter"] = {"Guard_handle_key": ["Succeeded"]}
    # The public provider's robots policy specifies Crawl-delay: 10. Faster
    # bounded probes do not override that published policy or prove headroom.
    delay["inputs"]["interval"]["count"] = 10
    request["runAfter"] = {"Polite_record_delay": ["Succeeded"]}
    actions["Latch_DoRA_provider_failure"] = {
        "type": "SetVariable", "runAfter": {"Get_full_record": ["Failed", "TimedOut"]},
        "inputs": {"name": "DoRAProviderFailed", "value": True}}
    return {"definition": result, "preimage_sha256": expected_sha256,
            "definition_sha256": fingerprint(result), "delay_seconds": 10,
            "failure_policy": "No more provider requests in this generation after a failed/timed-out GET",
            "runtime_performance_proven": False, "native_deployed": False}
