"""Build a private Power Automate package for the isolated grants DEV flow."""
from __future__ import annotations

import argparse
import hashlib
import json
from urllib.parse import urlsplit
import zipfile
from pathlib import Path
from typing import Any
from uuid import UUID

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DEFINITION = ROOT / "config/flows/grants-registry-reviewed-import.definition.json"


def _replace(value: Any, replacements: dict[str, str]) -> Any:
    if isinstance(value, str):
        for old, new in replacements.items():
            value = value.replace(old, new)
        return value
    if isinstance(value, list):
        return [_replace(item, replacements) for item in value]
    if isinstance(value, dict):
        return {key: _replace(item, replacements) for key, item in value.items()}
    return value


def build_package(
    output: Path,
    *,
    intent: str,
    site_url: str,
    list_id: str,
    flow_id: str,
    connection_display_name: str,
    expected_definition_sha256: str,
    definition_path: Path = DEFAULT_DEFINITION,
) -> Path:
    if intent not in {"create", "update"}:
        raise ValueError("explicit package intent must be 'create' or 'update'")
    if not output.resolve().is_relative_to((ROOT / "private").resolve()):
        raise ValueError("tenant-specific package must be written under ignored private/")
    if output.exists():
        raise FileExistsError("refusing to overwrite an existing package; choose a distinct output path")
    parsed_site_url = urlsplit(site_url)
    if (
        parsed_site_url.scheme.lower() != "https"
        or not parsed_site_url.hostname
        or parsed_site_url.username is not None
        or parsed_site_url.password is not None
        or parsed_site_url.query
        or parsed_site_url.fragment
        or "{{" in site_url
        or site_url != site_url.strip()
    ):
        raise ValueError("a concrete HTTPS SharePoint site URL is required")
    for value, label in ((list_id, "list_id"), (flow_id, "flow_id")):
        try:
            UUID(value)
        except ValueError as exc:
            raise ValueError(f"{label} must be a GUID") from exc
    if (not connection_display_name.strip() or "{{" in connection_display_name
            or "}}" in connection_display_name):
        raise ValueError("a concrete connection display name is required")

    source_bytes = definition_path.read_bytes()
    actual_definition_sha256 = hashlib.sha256(source_bytes).hexdigest()
    if (not isinstance(expected_definition_sha256, str)
            or expected_definition_sha256 != actual_definition_sha256):
        raise ValueError("source definition fingerprint mismatch")
    document = json.loads(source_bytes)
    document = _replace(document, {
        "{{FLOW_ID}}": flow_id,
        "{{SHAREPOINT_SITE_URL}}": site_url,
        "{{SHAREPOINT_LIST_ID}}": list_id,
    })
    creation_type = "New" if intent == "create" else "Update"
    manifest = {
        "schema": "1.0",
        "details": {
            "displayName": document["properties"]["displayName"],
            "description": "Isolated DEV reviewed grants import; remains disabled until native test approval.",
            "createdTime": "2026-09-20T00:00:00Z",
            "creator": "N/A",
            "sourceEnvironment": "",
        },
        "resources": {
            flow_id: {
                "type": "Microsoft.Flow/flows",
                "suggestedCreationType": creation_type,
                "creationType": creation_type,
                "details": {"displayName": document["properties"]["displayName"]},
                "configurableBy": "User",
                "hierarchy": "Root",
                "dependsOn": ["sp_api_id", "sp_conn_id"],
            },
            "sp_api_id": {
                "id": "/providers/Microsoft.PowerApps/apis/shared_sharepointonline",
                "name": "shared_sharepointonline",
                "type": "Microsoft.PowerApps/apis",
                "suggestedCreationType": "Existing",
                "details": {"displayName": "SharePoint"},
                "configurableBy": "System",
                "hierarchy": "Child",
                "dependsOn": [],
            },
            "sp_conn_id": {
                "type": "Microsoft.PowerApps/apis/connections",
                "suggestedCreationType": "Existing",
                "creationType": "Existing",
                "details": {"displayName": connection_display_name},
                "configurableBy": "User",
                "hierarchy": "Child",
                "dependsOn": ["sp_api_id"],
            },
        },
    }
    flow_root = f"Microsoft.Flow/flows/{flow_id}"
    files = {
        f"{flow_root}/definition.json": json.dumps(document, indent=2).encode(),
        f"{flow_root}/apisMap.json": json.dumps({"shared_sharepointonline": "sp_api_id"}, indent=2).encode(),
        f"{flow_root}/connectionsMap.json": json.dumps({"shared_sharepointonline": "sp_conn_id"}, indent=2).encode(),
        "manifest.json": json.dumps(manifest, indent=2).encode(),
        "Microsoft.Flow/flows/manifest.json": json.dumps({
            "packageSchemaVersion": "1.0",
            "flowAssets": {"assetPaths": [flow_id]},
        }, indent=2).encode(),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "x", zipfile.ZIP_DEFLATED) as archive:
        for name, content in files.items():
            archive.writestr(name, content)
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--intent", choices=("create", "update"), required=True)
    parser.add_argument("--site-url", required=True)
    parser.add_argument("--list-id", required=True)
    parser.add_argument("--flow-id", required=True)
    parser.add_argument("--connection-display-name", required=True)
    parser.add_argument("--expected-definition-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(build_package(args.output, intent=args.intent, site_url=args.site_url, list_id=args.list_id,
                        flow_id=args.flow_id, connection_display_name=args.connection_display_name,
                        expected_definition_sha256=args.expected_definition_sha256))
