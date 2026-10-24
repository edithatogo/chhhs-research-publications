"""Independently verify downloaded native NIH acquisition/archive artifacts.

Read-only, offline. This does not promote a register row or qualify refresh/alerts.
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
    from .grants_us_gov_api import prepare_snapshot
except ImportError:
    from grants_us_gov_api import prepare_snapshot

ROLES = ["search-current", "detail-current", "search-replay", "detail-replay"]


def verify(directory: Path) -> dict:
    manifest = json.loads((directory / "acquisition.json").read_bytes())
    if (manifest.get("format") != "rims-nih-acquisition-v1"
            or manifest.get("source") != "us-grants-gov-nih-pa-25-301"
            or manifest.get("acquisition_complete") is not True
            or any(manifest.get(k) is not False for k in
                   ["accepted", "register_updated", "model_refreshed", "end_to_end_qualified"])
            or manifest.get("attachment_files_retained") is not True
            or [x.get("role") for x in manifest.get("responses", [])] != ROLES):
        raise ValueError("incomplete_or_wrong_acquisition_manifest")
    files, payloads = [], []
    for entry in manifest["responses"]:
        name = entry["role"] + ".json"
        raw = (directory / name).read_bytes()
        if (entry.get("http_status") != 200
                or raw != base64.b64decode(entry["content_base64"], validate=True)
                or json.loads(raw) != entry["response"]):
            raise ValueError("response_bytes_or_values_mismatch")
        files.append({"name": name, "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()})
        payloads.append(json.loads(raw))
    prepared = prepare_snapshot(*payloads, retrieved_at=manifest["observed_utc"])
    folders = payloads[1]["data"]["synopsisAttachmentFolders"]
    replay_folders = payloads[3]["data"]["synopsisAttachmentFolders"]
    retained = manifest.get("attachment_folders")
    if (folders != replay_folders or not isinstance(retained, list)
            or len(retained) != len(folders)
            or [x.get("folder_metadata") for x in retained] != folders
            or len({x["id"] for x in folders}) != len(folders)):
        raise ValueError("incomplete_attachment_folder_coverage")
    members = []
    for entry in retained:
        folder = entry["folder_metadata"]
        name = f"attachment-folder-{folder['id']}.zip"
        raw = (directory / name).read_bytes()
        if (raw != base64.b64decode(entry["content_base64"], validate=True)
                or len(raw) != folder["zipLobSize"]):
            raise ValueError("attachment_binary_or_size_mismatch")
        expected = folder["synopsisAttachments"]
        if len({x["fileName"] for x in expected}) != len(expected):
            raise ValueError("duplicate_attachment_identity")
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            entries = archive.infolist()
            if (len(entries) != len(expected)
                    or {x.filename for x in entries} != {x["fileName"] for x in expected}
                    or sum(x.file_size for x in entries) > 104857600
                    or archive.testzip() is not None):
                raise ValueError("incomplete_or_corrupt_attachment_archive")
            for item in expected:
                info = archive.getinfo(item["fileName"])
                if (info.is_dir() or Path(info.filename).name != info.filename
                        or info.file_size != item["fileLobSize"]
                        or item["opportunityId"] != 357812):
                    raise ValueError("attachment_member_identity_or_size_mismatch")
                content = archive.read(info)
                members.append({"name": info.filename, "bytes": len(content),
                                "sha256": hashlib.sha256(content).hexdigest()})
        files.append({"name": name, "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()})
    return {"source": manifest["source"], "run": manifest["run"],
            "source_replay_valid": True, "files": files, "attachment_members": members,
            "normalization_records": len(prepared["batch"]["records"]),
            "register_updated": False, "model_refreshed": False, "end_to_end_qualified": False,
            "representation": manifest["scope"]["representation"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.write_text(json.dumps(verify(args.directory), indent=2) + "\n")


if __name__ == "__main__":
    main()
