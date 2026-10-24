"""Prepare an isolated OpenCitations Meta flow from accepted DOI bootstrap identities."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from prepare_opencitations_flow import prepare


def prepare_metadata(seed: list[dict], site: str, folder: str) -> dict:
    packet = prepare(seed, site, folder)
    digest = hashlib.sha256(json.dumps({"capability": "opencitations_meta_v1", "seed": seed},
                                      sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    old_marker = packet["marker"]
    marker = f"opencitations-meta-complete-{digest}.json"
    root = packet["definition"]["actions"]
    cached = root["Use_cached_snapshot"]["actions"]
    acquire = root["Use_cached_snapshot"]["else"]["actions"]
    per_doi = acquire["Acquire_counts"]["actions"]["Use_retained_entry"]["else"]["actions"]
    acquire["Acquire_counts"]["actions"]["Remember_metadata_failure"] = {
        "type": "SetVariable", "inputs": {"name": "ProviderFailed", "value": True},
        "runAfter": {"Use_retained_entry": ["Failed", "TimedOut"]}}
    endpoint = "@concat('https://api.opencitations.net/meta/v1/metadata/doi:',uriComponent(items('Acquire_counts')))"

    root["Scope"]["inputs"].update(source="opencitations_meta", capability="bibliographic_metadata",
                                    scope_sha256=digest)
    root["Find_completed"]["inputs"]["parameters"]["parameters/uri"] = root["Find_completed"]["inputs"]["parameters"]["parameters/uri"].replace(old_marker, marker)
    cached["Read_cached_manifest"]["inputs"]["parameters"]["path"] = folder + "/" + marker
    cached["Cached_manifest"]["inputs"]["schema"]["properties"]["source"]["const"] = "opencitations_meta"
    cached["Guard_cached_scope"]["inputs"] = cached["Guard_cached_scope"]["inputs"].replace("'opencitations'", "'opencitations_meta'")
    cached["Verify_cached_raw"]["actions"]["Guard_cached_path"]["inputs"] = cached["Verify_cached_raw"]["actions"]["Guard_cached_path"]["inputs"].replace("'opencitations-'", "'opencitations-meta-'")
    cached["Replay_complete"]["inputs"].update(scope_sha256=digest, capability="bibliographic_metadata")

    per_doi["Provider_request"]["actions"]["Fetch_count"]["inputs"]["uri"] = endpoint
    per_doi["Parse_count"]["inputs"]["schema"] = {
        "type": "array", "maxItems": 1000,
        "items": {"type": "object", "required": ["id"], "properties": {"id": {"type": "string", "minLength": 1}}}}
    per_doi["Guard_count"]["inputs"] = "@if(equals(outputs('Fetch_count')?['statusCode'],200),true,json('OPENCITATIONS_META_HTTP_FAILURE'))"
    per_doi["Invalid_metadata_ids"] = {"type": "Query", "runAfter": {"Guard_count": ["Succeeded"]}, "inputs": {
        "from": "@body('Parse_count')",
        "where": "@not(contains(split(toLower(item()?['id']),' '),concat('doi:',toLower(items('Acquire_counts')))))"}}
    per_doi["Guard_metadata_ids"] = {"type": "Compose", "runAfter": {"Invalid_metadata_ids": ["Succeeded"]},
                                       "inputs": "@if(equals(length(body('Invalid_metadata_ids')),0),true,json('OPENCITATIONS_META_DOI_MISMATCH'))"}
    per_doi["Envelope"]["runAfter"] = {"Guard_metadata_ids": ["Succeeded"]}
    per_doi["Envelope"]["inputs"].update(source="opencitations_meta", capability="bibliographic_metadata",
                                          scope_sha256=digest, request_url=endpoint,
                                          count="@length(body('Parse_count'))",
                                          disposition="@if(equals(length(body('Parse_count')),0),'no_hit',if(equals(length(body('Parse_count')),1),'single_match','multiple_matches_unadjudicated'))")
    per_doi["Raw_name"]["inputs"] = per_doi["Raw_name"]["inputs"].replace("'opencitations-'", "'opencitations-meta-'")
    acquire["Manifest"]["inputs"].update(source="opencitations_meta", capability="bibliographic_metadata",
                                          scope_sha256=digest,
                                          scope="complete returned exact-DOI metadata responses; explicit no-hits and unadjudicated multiple matches; not full corpus")
    acquire["Save_manifest"]["inputs"]["parameters"]["name"] = marker
    acquire["Read_saved_manifest"]["inputs"]["parameters"]["path"] = folder + "/" + marker

    names = {"Acquire_counts": "Acquire_metadata", "Fetch_count": "Fetch_metadata",
             "Parse_count": "Parse_metadata", "Guard_count": "Guard_metadata_response"}

    def rename(value):
        if isinstance(value, dict):
            return {names.get(key, key): rename(item) for key, item in value.items()}
        if isinstance(value, list):
            return [rename(item) for item in value]
        if isinstance(value, str):
            for before, after in names.items():
                value = value.replace("'" + before + "'", "'" + after + "'")
        return value

    return {"definition": rename(packet["definition"]), "scope_sha256": digest,
            "marker": marker, "capability": "bibliographic_metadata"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=Path, required=True)
    parser.add_argument("--site", required=True)
    parser.add_argument("--folder", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    packet = prepare_metadata(json.loads(args.seed.read_text()), args.site, args.folder)
    with args.output.open("x") as stream:
        json.dump(packet, stream, indent=2)
    print(json.dumps({"scope_sha256": packet["scope_sha256"], "marker": packet["marker"]}))
