"""Build a bounded, archive-backed OpenCitations count collector; no network writes."""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
from pathlib import Path


def prepare(seed: list[dict], site: str, folder: str, recovered: list[dict] | None = None,
            reuse_manifest: dict | None = None) -> dict:
    if not 1 <= len(seed) <= 50:
        raise ValueError("Select 1..50 archived DOI identities")
    dois = [row["doi"] for row in seed]
    if len(set(dois)) != len(dois) or any(not doi.startswith("10.") or "/" not in doi for doi in dois):
        raise ValueError("DOIs must be unique complete identifiers")
    if not site.startswith("https://") or not folder.startswith("/Documents/") or ".." in folder:
        raise ValueError("Use the existing qualified site and archive folder")
    digest = hashlib.sha256(json.dumps(seed, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    recovered = recovered or []
    if recovered and (len(recovered) != len(seed) or [r.get("doi") for r in recovered] != dois
                      or any(r.get("scope_sha256") != digest or r.get("http_status") != 200
                             or not isinstance(r.get("response"), list) or len(r["response"]) != 1
                             or int(r["response"][0]["count"]) < 0 for r in recovered)):
        raise ValueError("Recovered responses must match this exact seed and successful provider scope")
    marker = f"opencitations-complete-{digest}.json"
    reused = []
    if reuse_manifest is not None:
        if reuse_manifest.get("source") != "opencitations" or reuse_manifest.get("complete") is not True:
            raise ValueError("Reuse requires an accepted complete OpenCitations manifest")
        reused = reuse_manifest.get("entries", [])
        if not isinstance(reused, list) or not reused or len(reused) > len(seed):
            raise ValueError("Reuse must be a nonempty subset of this DOI selection")
        reused_dois = []
        for entry in reused:
            payload = json.loads(base64.b64decode(entry["content_base64"], validate=True))
            if (entry["doi"] not in dois or not re.fullmatch(r"opencitations-[A-Za-z0-9-]+\.json", entry["name"])
                    or payload.get("source") != "opencitations" or payload.get("doi") != entry["doi"]
                    or payload.get("http_status") != 200 or payload.get("count") != entry["count"]
                    or not isinstance(entry["count"], int) or isinstance(entry["count"], bool) or entry["count"] < 0):
                raise ValueError("Retained envelope identity/count/path mismatch")
            reused_dois.append(entry["doi"])
        if len(set(reused_dois)) != len(reused_dois):
            raise ValueError("Retained DOI entries must be unique")

    def action(kind, inputs, after=None, **extra):
        result = {"type": kind, "runAfter": {after: ["Succeeded"]} if after else {}, "inputs": inputs}
        result.update(extra)
        return result

    def sp(op, params, after=None):
        return action("OpenApiConnection", {
            "host": {"apiId": "/providers/Microsoft.PowerApps/apis/shared_sharepointonline",
                     "connectionName": "shared_sharepointonline", "operationId": op},
            "parameters": {"dataset": site, **params}, "retryPolicy": {"type": "none"}}, after)

    def read(path, after=None):
        return sp("GetFileContentByPath", {"path": path, "inferContentType": False}, after)

    def guard(expression, after):
        return action("Compose", f"@if({expression},true,json('OPENCITATIONS_INTEGRITY_FAILURE'))", after)

    schema = {"type": "object", "required": ["source", "scope_sha256", "seed", "complete", "entries"],
              "properties": {"source": {"const": "opencitations"}, "scope_sha256": {"type": "string"},
                             "seed": {"type": "array"}, "complete": {"type": "boolean"},
                             "entries": {"type": "array", "minItems": len(seed), "maxItems": len(seed),
                                         "items": {"type": "object", "required": ["doi", "name", "content_base64", "count"],
                                                   "properties": {"doi": {"type": "string"}, "name": {"type": "string"},
                                                                  "content_base64": {"type": "string"},
                                                                  "count": {"type": "integer", "minimum": 0}}}}}}
    cached = {
        "Read_cached_manifest": read(folder + "/" + marker),
        "Cached_manifest": action("ParseJson", {"content": "@json(base64ToString(body('Read_cached_manifest')?['$content']))", "schema": schema}, "Read_cached_manifest"),
        "Guard_cached_scope": guard("and(equals(body('Cached_manifest')?['source'],'opencitations'),equals(body('Cached_manifest')?['scope_sha256'],outputs('Scope')?['scope_sha256']),equals(body('Cached_manifest')?['seed'],outputs('Scope')?['seed']),equals(body('Cached_manifest')?['complete'],true))", "Cached_manifest"),
        "Verify_cached_raw": {"type": "Foreach", "foreach": "@body('Cached_manifest')?['entries']", "runAfter": {"Guard_cached_scope": ["Succeeded"]}, "runtimeConfiguration": {"concurrency": {"repetitions": 1}}, "actions": {
            "Guard_cached_path": guard("and(startsWith(items('Verify_cached_raw')?['name'],'opencitations-'),not(contains(items('Verify_cached_raw')?['name'],'/')),not(contains(items('Verify_cached_raw')?['name'],'..')),contains(outputs('Scope')?['dois'],items('Verify_cached_raw')?['doi']))", None),
            "Read_cached_raw": read("@concat(outputs('Scope')?['folder'],'/',items('Verify_cached_raw')?['name'])", "Guard_cached_path"),
            "Guard_cached_bytes": guard("equals(body('Read_cached_raw')?['$content'],items('Verify_cached_raw')?['content_base64'])", "Read_cached_raw")}},
        "Cached_keys": action("Select", {"from": "@body('Cached_manifest')?['entries']", "select": "@item()?['doi']"}, "Verify_cached_raw"),
        "Guard_cached_keys": guard(f"equals(length(union(body('Cached_keys'),body('Cached_keys'))),{len(seed)})", "Cached_keys"),
        "Replay_complete": action("Compose", {"provider_requests": 0, "archive_writes": 0, "scope_sha256": digest, "reused": len(seed)}, "Guard_cached_keys")}
    per_doi = {
        "Fetch_count": action("Http", {"uri": "@concat('https://api.opencitations.net/index/v2/citation-count/doi:',uriComponent(items('Acquire_counts')))", "method": "GET", "headers": {"Accept": "application/json"}, "retryPolicy": {"type": "none"}}, limit={"timeout": "PT1M"}),
        "Parse_count": action("ParseJson", {"content": "@body('Fetch_count')", "schema": {"type": "array", "minItems": 1, "maxItems": 1, "items": {"type": "object", "required": ["count"], "properties": {"count": {"type": ["string", "integer"]}}}}}, "Fetch_count"),
        "Guard_count": guard("and(equals(outputs('Fetch_count')?['statusCode'],200),greaterOrEquals(int(first(body('Parse_count'))?['count']),0))", "Parse_count"),
        "Envelope": action("Compose", {"source": "opencitations", "doi": "@items('Acquire_counts')", "scope_sha256": digest, "observed_utc": "@utcNow()", "request_url": "@concat('https://api.opencitations.net/index/v2/citation-count/doi:',uriComponent(items('Acquire_counts')))", "http_status": "@outputs('Fetch_count')?['statusCode']", "response_headers": "@outputs('Fetch_count')?['headers']", "response": "@body('Fetch_count')", "licence": "CC0", "count": "@int(first(body('Parse_count'))?['count'])"}, "Guard_count"),
        "Raw_name": action("Compose", "@concat('opencitations-',workflow()?['run']?['name'],'-',guid(),'.json')", "Envelope"),
        "Save_raw": sp("CreateFile", {"folderPath": folder, "name": "@outputs('Raw_name')", "body": "@string(outputs('Envelope'))"}, "Raw_name"),
        "Read_raw": read("@concat(outputs('Scope')?['folder'],'/',outputs('Raw_name'))", "Save_raw"),
        "Guard_saved_raw": guard("equals(body('Read_raw')?['$content'],base64(string(outputs('Envelope'))))", "Read_raw"),
        "Remember_entry": action("AppendToArrayVariable", {"name": "Entries", "value": {"doi": "@items('Acquire_counts')", "name": "@outputs('Raw_name')", "content_base64": "@body('Read_raw')?['$content']", "count": "@outputs('Envelope')?['count']"}}, "Guard_saved_raw"),
        "Pace": action("Wait", {"interval": {"count": 2, "unit": "Second"}}, "Remember_entry")}
    fetch = per_doi.pop("Fetch_count")
    per_doi["Guard_previous_provider"] = guard("equals(variables('ProviderFailed'),false)", None)
    per_doi["Recovered_match"] = action("Query", {"from": "@outputs('Scope')?['recovered']", "where": "@equals(item()?['doi'],items('Acquire_counts'))"}, "Guard_previous_provider")
    per_doi["Guard_recovery_match"] = guard("lessOrEquals(length(body('Recovered_match')),1)", "Recovered_match")
    per_doi["Provider_request"] = {"type": "If", "expression": "@empty(body('Recovered_match'))", "runAfter": {"Guard_recovery_match": ["Succeeded"]}, "actions": {
        "Fetch_count": fetch,
        "Remember_provider_failure": {"type": "SetVariable", "inputs": {"name": "ProviderFailed", "value": True}, "runAfter": {"Fetch_count": ["Failed", "TimedOut"]}}}, "else": {"actions": {}}}
    per_doi["Selected_response"] = action("Compose", "@if(empty(body('Recovered_match')),body('Fetch_count'),first(body('Recovered_match'))?['response'])", "Provider_request")
    per_doi["Parse_count"]["runAfter"] = {"Selected_response": ["Succeeded"]}
    per_doi["Parse_count"]["inputs"]["content"] = "@outputs('Selected_response')"
    per_doi["Guard_count"]["inputs"] = "@if(and(equals(if(empty(body('Recovered_match')),outputs('Fetch_count')?['statusCode'],first(body('Recovered_match'))?['http_status']),200),greaterOrEquals(int(first(body('Parse_count'))?['count']),0)),true,json('OPENCITATIONS_INTEGRITY_FAILURE'))"
    envelope = per_doi["Envelope"]["inputs"]
    envelope["observed_utc"] = "@if(empty(body('Recovered_match')),utcNow(),first(body('Recovered_match'))?['observed_utc'])"
    envelope["http_status"] = "@if(empty(body('Recovered_match')),outputs('Fetch_count')?['statusCode'],first(body('Recovered_match'))?['http_status'])"
    envelope["response_headers"] = "@if(empty(body('Recovered_match')),outputs('Fetch_count')?['headers'],first(body('Recovered_match'))?['response_headers'])"
    envelope["response"] = "@outputs('Selected_response')"
    retained_actions = {
        "Find_retained_entry": action("Query", {"from": "@outputs('Scope')?['retained_entries']", "where": "@equals(item()?['doi'],items('Acquire_counts'))"}),
        "Guard_retained_unique": guard("lessOrEquals(length(body('Find_retained_entry')),1)", "Find_retained_entry"),
        "Use_retained_entry": {"type": "If", "expression": "@equals(length(body('Find_retained_entry')),1)", "runAfter": {"Guard_retained_unique": ["Succeeded"]}, "actions": {
            "Read_retained_raw": read("@concat(outputs('Scope')?['folder'],'/',first(body('Find_retained_entry'))?['name'])"),
            "Guard_retained_bytes": guard("equals(body('Read_retained_raw')?['$content'],first(body('Find_retained_entry'))?['content_base64'])", "Read_retained_raw"),
            "Remember_retained_entry": action("AppendToArrayVariable", {"name": "Entries", "value": "@first(body('Find_retained_entry'))"}, "Guard_retained_bytes")}, "else": {"actions": per_doi}}}
    acquire = {
        "Acquire_counts": {"type": "Foreach", "foreach": "@outputs('Scope')?['dois']", "runAfter": {}, "runtimeConfiguration": {"concurrency": {"repetitions": 1}}, "actions": retained_actions},
        "Guard_batch_complete": guard(f"equals(length(variables('Entries')),{len(seed)})", "Acquire_counts"),
        "Manifest": action("Compose", {"source": "opencitations", "scope_sha256": digest, "seed": seed, "complete": True, "run": "@workflow()?['run']?['name']", "entries": "@variables('Entries')", "scope": "frozen DOI citation-count observations; not citation-edge or corpus coverage"}, "Guard_batch_complete"),
        "Save_manifest": sp("CreateFile", {"folderPath": folder, "name": marker, "body": "@string(outputs('Manifest'))"}, "Manifest"),
        "Read_saved_manifest": read(folder + "/" + marker, "Save_manifest"),
        "Guard_saved_manifest": guard("equals(body('Read_saved_manifest')?['$content'],base64(string(outputs('Manifest'))))", "Read_saved_manifest")}
    root = {
        "Scope": action("Compose", {"source": "opencitations", "scope_sha256": digest, "seed": seed, "dois": dois, "folder": folder, "recovered": recovered, "retained_entries": reused}),
        "Initialize_entries": action("InitializeVariable", {"variables": [{"name": "Entries", "type": "array", "value": []}]}, "Scope"),
        "Initialize_provider_failure": action("InitializeVariable", {"variables": [{"name": "ProviderFailed", "type": "boolean", "value": False}]}, "Initialize_entries"),
        "Find_completed": sp("HttpRequest", {"parameters/method": "GET", "parameters/uri": "_api/web/GetFolderByServerRelativePath(decodedurl='" + "/personal/" + site.split("/personal/")[1] + folder + "')/Files?$select=Name&$filter=Name%20eq%20'" + marker + "'&$top=2", "parameters/headers": {"Accept": "application/json;odata=nometadata"}}, "Initialize_provider_failure"),
        "Guard_single_marker": guard("lessOrEquals(length(body('Find_completed')?['value']),1)", "Find_completed"),
        "Use_cached_snapshot": {"type": "If", "expression": "@equals(length(body('Find_completed')?['value']),1)", "runAfter": {"Guard_single_marker": ["Succeeded"]}, "actions": cached, "else": {"actions": acquire}}}
    return {"definition": {"$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#", "contentVersion": "1.0.0.0", "parameters": {"$authentication": {"defaultValue": {}, "type": "SecureObject"}, "$connections": {"defaultValue": {}, "type": "Object"}}, "triggers": {"manual": {"type": "Request", "kind": "Button", "inputs": {"schema": {"type": "object", "properties": {}}}, "runtimeConfiguration": {"concurrency": {"runs": 1}}}}, "actions": root}, "scope_sha256": digest, "marker": marker}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=Path, required=True)
    parser.add_argument("--site", required=True)
    parser.add_argument("--folder", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--recovered", type=Path)
    parser.add_argument("--reuse-manifest", type=Path)
    args = parser.parse_args()
    result = prepare(json.loads(args.seed.read_text()), args.site, args.folder,
                     json.loads(args.recovered.read_text()) if args.recovered else None,
                     json.loads(args.reuse_manifest.read_text()) if args.reuse_manifest else None)
    with args.output.open("x") as stream:
        json.dump(result, stream, indent=2)
    print(json.dumps({"scope_sha256": result["scope_sha256"], "marker": result["marker"]}))
