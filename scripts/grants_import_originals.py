"""Prepare complete byte-preserving NIH originals for the reviewed-import trigger.

Local admission/input preparation only; the native flow performs retention.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import io
import json
from pathlib import Path
import zipfile

try:
    from .grants_us_gov_api import SOURCE, OPPORTUNITY_ID, prepare_snapshot
    from .grants_registry import normalize_opportunity
    from .grants_deadline_schedule import require_source_schedule
except ImportError:
    from grants_us_gov_api import SOURCE, OPPORTUNITY_ID, prepare_snapshot
    from grants_registry import normalize_opportunity
    from grants_deadline_schedule import require_source_schedule

ROLES = ("search-current", "detail-current", "search-replay", "detail-replay")


def _unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON property in original")
        result[key] = value
    return result


def prepare(row: dict, responses: dict[str, bytes], attachments: dict[int, bytes],
            *, source_observed_at: str | None = None) -> dict:
    if row.get("Source") != SOURCE or set(responses) != set(ROLES):
        raise ValueError("one exact NIH row and four complete response files required")
    if any(not isinstance(b, bytes) or not 0 < len(b) <= 10485760 for b in responses.values()):
        raise ValueError("invalid original response bytes/size")
    payloads = [json.loads(responses[role], object_pairs_hook=_unique) for role in ROLES]
    # EvidenceHash covers the pre-normalization producer record. Its original
    # observation spelling (for example Z versus +00:00) must not be guessed.
    observed_at = source_observed_at or row["RetrievedUTC"]
    prepared = prepare_snapshot(*payloads, retrieved_at=observed_at)
    require_source_schedule(row)
    if json.loads(row["SourceDateFactsJSON"]) != prepared["source_date_facts"]:
        raise ValueError("source date facts mismatch")
    raw_row = prepared["batch"]["records"][0]
    raw_row.update({key: row[key] for key in ["DeadlineScheduleJSON", "SourceDateFactsJSON", "SourceAttribution"]})
    if normalize_opportunity(raw_row, retrieved_at=observed_at) != row:
        raise ValueError("row or evidence hash does not match the complete original source projection")
    folders = payloads[1]["data"].get("synopsisAttachmentFolders")
    if (not isinstance(folders, list) or len(folders) > 10
            or folders != payloads[3]["data"].get("synopsisAttachmentFolders")
            or len({f["id"] for f in folders}) != len(folders)
            or set(attachments) != {f["id"] for f in folders}):
        raise ValueError("incomplete original attachment coverage")
    files = []
    for role in ROLES:
        files.append((role, responses[role]))
    for folder in folders:
        raw = attachments[folder["id"]]
        if (folder["opportunityId"] != OPPORTUNITY_ID or not isinstance(raw, bytes)
                or len(raw) != folder["zipLobSize"] or not 0 < len(raw) <= 52428800):
            raise ValueError("attachment parent or bytes mismatch")
        expected = folder["synopsisAttachments"]
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            entries = archive.infolist()
            if (len(entries) != len(expected)
                    or {e.filename for e in entries} != {e["fileName"] for e in expected}
                    or sum(e.file_size for e in entries) > 104857600 or archive.testzip() is not None):
                raise ValueError("incomplete or corrupt attachment ZIP")
            for item in expected:
                if (Path(item["fileName"]).name != item["fileName"]
                        or archive.getinfo(item["fileName"]).file_size != item["fileLobSize"]
                        or item["opportunityId"] != OPPORTUNITY_ID):
                    raise ValueError("attachment member mismatch")
        files.append((f"attachment-folder-{folder['id']}", raw))
    return {"schema_version": "grants-originals-v1", **{key: row[key] for key in
            ["Source", "SourceID", "RoundID", "OpportunityKey", "RetrievedUTC", "EvidenceHash"]},
            "files": [{"role": role, "sha256": hashlib.sha256(raw).hexdigest(),
                       "byte_length": len(raw), "content_base64": base64.b64encode(raw).decode()}
                      for role, raw in files]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--projection", type=Path, required=True)
    parser.add_argument("--originals", type=Path, required=True)
    parser.add_argument("--attachments", type=Path, required=True)
    parser.add_argument("--source-observed-at", help="Original producer observation text, if normalized projection changed its spelling")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    projection = json.loads(args.projection.read_bytes())
    rows = projection.get("records") if isinstance(projection, dict) else projection
    if not isinstance(rows, list) or len(rows) != 1:
        raise ValueError("selected NIH import requires exactly one projected row")
    responses = {role: (args.originals / (role + ".json")).read_bytes() for role in ROLES}
    detail = json.loads(responses["detail-current"])
    attachments = {f["id"]: (args.attachments / f"attachment-folder-{f['id']}.zip").read_bytes()
                   for f in detail["data"]["synopsisAttachmentFolders"]}
    result = prepare(rows[0], responses, attachments, source_observed_at=args.source_observed_at)
    args.output.write_text(json.dumps(result, separators=(",", ":")) + "\n")


if __name__ == "__main__":
    main()
