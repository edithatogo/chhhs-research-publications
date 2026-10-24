"""Prepare source assertions from accepted archives; no source or tenant requests."""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import quote


def encode(value) -> bytes:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode()


def load_observations(manifest_path: Path, acceptance_path: Path, source: str):
    raw = manifest_path.read_bytes()
    accepted = json.loads(acceptance_path.read_text())
    manifest = json.loads(raw)
    if (not str(accepted.get("status", "")).startswith("PASS_")
            or hashlib.sha256(raw).hexdigest() != accepted["manifest"]["sha256"]
            or manifest.get("source") != source or manifest.get("complete") is not True):
        raise ValueError("Accepted source manifest required")
    evidence = {entry["name"]: entry for entry in accepted["raw_files"]}
    observations, files = {}, []
    for entry in manifest["entries"]:
        name = entry["name"]
        content = base64.b64decode(entry["content_base64"], validate=True)
        digest = hashlib.sha256(content).hexdigest()
        body = json.loads(content)
        if (not re.fullmatch(r"opencitations-[A-Za-z0-9-]+\.json", name)
                or digest != evidence[name]["sha256"] or body.get("source") != source
                or body.get("http_status") != 200 or body.get("doi") != entry["doi"]
                or entry["doi"] in observations):
            raise ValueError("Raw observation identity/hash mismatch")
        observations[entry["doi"]] = (body, {"name": name, "sha256": digest})
        files.append({"name": name, "content_base64": entry["content_base64"]})
    if not observations or len(observations) > 50:
        raise ValueError("Select at most50 verified DOI observations")
    files.append({"name": accepted["manifest"]["name"], "content_base64": base64.b64encode(raw).decode()})
    return observations, files, accepted["manifest"]


def prepare(count_manifest: Path, count_acceptance: Path, metadata_manifest: Path,
            metadata_acceptance: Path, folder: str, output: Path) -> dict:
    counts, count_files, count_proof = load_observations(count_manifest, count_acceptance, "opencitations")
    metadata, meta_files, meta_proof = load_observations(metadata_manifest, metadata_acceptance, "opencitations_meta")
    if set(counts) != set(metadata) or not folder.startswith("/Documents/") or ".." in folder:
        raise ValueError("Exact matching DOI selections and approved archive folder required")
    scope = {"capability": "opencitations_source_assertions_v1", "count_manifest": count_proof,
             "metadata_manifest": meta_proof,
             "interpretation": "Source assertions only; observation times remain source-specific; no canonical identity or business relationship decision"}
    digest = hashlib.sha256(encode(scope)).hexdigest()
    manifest_name = f"opencitations-assertion-manifest-{digest}.json"
    projection_name = f"opencitations-assertion-projection-{digest}.json"
    packet_name = f"opencitations-assertions-ready-{digest}.json"
    rows, entries = [], {}
    for doi in sorted(counts):
        count, count_ref = counts[doi]
        meta, meta_ref = metadata[doi]
        if (not isinstance(count.get("count"), int) or isinstance(count["count"], bool)
                or count["count"] < 0 or int(count["response"][0]["count"]) != count["count"]
                or not isinstance(meta.get("response"), list)
                or any("doi:" + doi not in row["id"].casefold().split() for row in meta["response"])):
            raise ValueError("Observation content mismatch")
        disposition = "no_hit" if not meta["response"] else "single_match" if len(meta["response"]) == 1 else "multiple_matches_unadjudicated"
        if meta.get("disposition") != disposition:
            raise ValueError("Metadata disposition mismatch")
        title = meta["response"][0].get("title") if disposition == "single_match" else None
        key = "opencitations:" + doi
        rows.append({"SourceKey": key, "DOI": doi, "Summary": title or f"{doi}: {disposition}",
                     "SourceURL": meta["request_url"], "MetadataDisposition": disposition,
                     "CountArchive": count_ref, "MetadataArchive": meta_ref,
                     "CitationObservation": count, "MetadataObservation": meta,
                     "Interpretation": "unadjudicated provider observations; not a canonical publication or confirmed person/organisation relationship"})
        entries[quote(key, safe="~()*!.'-_")] = {"name": meta_ref["name"], "sha256": meta_ref["sha256"],
                                                   "source_url": meta["request_url"], "captured_utc": meta["observed_utc"]}
    projection = encode(rows)
    all_files = count_files + meta_files
    if len({entry["name"] for entry in all_files}) != len(all_files):
        raise ValueError("Duplicate archive pointer")
    manifest = encode({"source": "opencitations", "scope": scope, "complete": True, "count": len(rows),
                       "projection_sha256": hashlib.sha256(projection).hexdigest(),
                       "raw_files": [{"name": f["name"], "sha256": hashlib.sha256(base64.b64decode(f["content_base64"])).hexdigest()}
                                     for f in all_files]})
    packet = encode({"format": "rims-source-assertion-verified-v1", "source": "opencitations",
                     "scope_sha256": digest, "archive_folder": folder, "count": len(rows), "entries": entries,
                     "manifest_name": manifest_name, "manifest_base64": base64.b64encode(manifest).decode(),
                     "manifest_sha256": hashlib.sha256(manifest).hexdigest(),
                     "projection_name": projection_name, "projection_base64": base64.b64encode(projection).decode(),
                     "raw_files": all_files})
    output.mkdir(parents=True, exist_ok=False)
    for name, content in ((manifest_name, manifest), (projection_name, projection), (packet_name, packet)):
        with (output / name).open("xb") as stream:
            stream.write(content)
    receipt = {"status": "PREPARED_FROM_ACCEPTED_NATIVE_ARCHIVES", "count": len(rows),
               "scope_sha256": digest, "packet_name": packet_name, "raw_archive_pointers": len(all_files),
               "provider_requests": 0, "files": {name: {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
                    for name, data in ((manifest_name, manifest), (projection_name, projection), (packet_name, packet))}}
    (output / "preparation.json").write_text(json.dumps(receipt, indent=2))
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("count-manifest", "count-acceptance", "metadata-manifest", "metadata-acceptance", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--folder", required=True)
    args = parser.parse_args()
    receipt = prepare(args.count_manifest, args.count_acceptance, args.metadata_manifest,
                      args.metadata_acceptance, args.folder, args.output)
    print(json.dumps({"status": receipt["status"], "count": receipt["count"], "packet_name": receipt["packet_name"]}))
