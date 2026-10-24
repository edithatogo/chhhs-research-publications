"""Prepare bounded incoming citation-link acquisition from accepted DOI identities."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from prepare_opencitations_metadata import prepare_metadata


def prepare_citations(seed: list[dict], site: str, folder: str) -> dict:
    packet = prepare_metadata(seed, site, folder)
    digest = hashlib.sha256(json.dumps({"capability": "opencitations_incoming_citations_v1", "seed": seed},
                                      sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    source = "opencitations_citations"
    marker = f"opencitations-citations-complete-{digest}.json"
    root = packet["definition"]["actions"]
    cached = root["Use_cached_snapshot"]["actions"]
    acquire = root["Use_cached_snapshot"]["else"]["actions"]
    per_doi = acquire["Acquire_metadata"]["actions"]["Use_retained_entry"]["else"]["actions"]
    endpoint = "@concat('https://api.opencitations.net/index/v2/citations/doi:',uriComponent(items('Acquire_metadata')))"
    root["Scope"]["inputs"].update(source=source, capability="incoming_citation_links", scope_sha256=digest)
    root["Find_completed"]["inputs"]["parameters"]["parameters/uri"] = root["Find_completed"]["inputs"]["parameters"]["parameters/uri"].replace(packet["marker"], marker)
    cached["Read_cached_manifest"]["inputs"]["parameters"]["path"] = folder + "/" + marker
    cached["Cached_manifest"]["inputs"]["schema"]["properties"]["source"]["const"] = source
    cached["Guard_cached_scope"]["inputs"] = cached["Guard_cached_scope"]["inputs"].replace("'opencitations_meta'", "'" + source + "'")
    cached["Verify_cached_raw"]["actions"]["Guard_cached_path"]["inputs"] = cached["Verify_cached_raw"]["actions"]["Guard_cached_path"]["inputs"].replace("'opencitations-meta-'", "'opencitations-citations-'")
    cached["Replay_complete"]["inputs"].update(scope_sha256=digest, capability="incoming_citation_links")

    per_doi["Provider_request"]["actions"]["Fetch_metadata"]["inputs"]["uri"] = endpoint
    per_doi["Parse_metadata"]["inputs"]["schema"] = {
        "type": "array", "maxItems": 5000,
        "items": {"type": "object", "required": ["oci", "citing", "cited"],
                  "properties": {key: {"type": "string", "minLength": 1} for key in ("oci", "citing", "cited")}}}
    per_doi["Invalid_metadata_ids"]["inputs"]["where"] = (
        "@not(and(contains(split(toLower(replace(item()?['cited'],';',' ')),' '),"
        "concat('doi:',toLower(items('Acquire_metadata')))),not(empty(trim(item()?['citing']))),"
        "equals(length(split(item()?['oci'],'-')),2),"
        "not(empty(first(split(item()?['oci'],'-')))),not(empty(last(split(item()?['oci'],'-'))))))")
    per_doi["Guard_metadata_ids"]["inputs"] = "@if(equals(length(body('Invalid_metadata_ids')),0),true,json('OPENCITATIONS_CITATION_IDENTITY_MISMATCH'))"
    per_doi["Citation_keys"] = {"type": "Select", "runAfter": {"Guard_metadata_ids": ["Succeeded"]},
                                "inputs": {"from": "@body('Parse_metadata')", "select": "@item()?['oci']"}}
    per_doi["Guard_citation_keys"] = {"type": "Compose", "runAfter": {"Citation_keys": ["Succeeded"]},
                                     "inputs": "@if(equals(length(union(body('Citation_keys'),body('Citation_keys'))),length(body('Parse_metadata'))),true,json('OPENCITATIONS_DUPLICATE_CITATION'))"}
    per_doi["Envelope"]["runAfter"] = {"Guard_citation_keys": ["Succeeded"]}
    per_doi["Envelope"]["inputs"].update(source=source, capability="incoming_citation_links",
                                          scope_sha256=digest, request_url=endpoint,
                                          disposition="@if(equals(length(body('Parse_metadata')),0),'no_incoming_citations','incoming_citations')")
    per_doi["Raw_name"]["inputs"] = per_doi["Raw_name"]["inputs"].replace("'opencitations-meta-'", "'opencitations-citations-'")
    acquire["Manifest"]["inputs"].update(source=source, capability="incoming_citation_links", scope_sha256=digest,
                                          scope="complete returned incoming citation responses for selected archived DOI identities; not outgoing references, whole corpus, quality or confirmed collaboration")
    acquire["Save_manifest"]["inputs"]["parameters"]["name"] = marker
    acquire["Read_saved_manifest"]["inputs"]["parameters"]["path"] = folder + "/" + marker

    names = {"Acquire_metadata": "Acquire_citations", "Fetch_metadata": "Fetch_citations",
             "Parse_metadata": "Parse_citations", "Guard_metadata_response": "Guard_citation_response",
             "Invalid_metadata_ids": "Invalid_citation_ids", "Guard_metadata_ids": "Guard_citation_ids",
             "Remember_metadata_failure": "Remember_citation_failure"}

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
            "marker": marker, "capability": "incoming_citation_links"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=Path, required=True)
    parser.add_argument("--site", required=True)
    parser.add_argument("--folder", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    packet = prepare_citations(json.loads(args.seed.read_text()), args.site, args.folder)
    with args.output.open("x") as stream:
        json.dump(packet, stream, indent=2)
    print(json.dumps({"scope_sha256": packet["scope_sha256"], "marker": packet["marker"]}))
