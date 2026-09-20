"""Render a source-preserving DoRA activity registry for RIMS ingestion."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from dora_activity import IDENTITY_FIELD, SOURCE_FIELDS, validate_records
from export_publication_register import safe_cell

PROVENANCE_FIELDS = [
    "DORAActivityKey",
    "DORARecordID",
    "DORAResourceID",
    "DORAResourceName",
    "DORAResourceLastModified",
    "DORAObservedUTC",
    "DORASourceURL",
]
EXPORT_FIELDS = PROVENANCE_FIELDS + SOURCE_FIELDS


def activity_key(resource_id: str, record: dict[str, Any]) -> str:
    record_id = str(record.get(IDENTITY_FIELD) or "").strip()
    if not record_id:
        raise ValueError("source _id is required for a DORA activity key")
    return f"dora-activity:{resource_id}:{record_id}"


def build_rows(envelope: dict[str, Any]) -> list[dict[str, Any]]:
    if envelope.get("schema_version") != "dora-activity-v1":
        raise ValueError("Unexpected DoRA activity receipt schema")
    source_payload = envelope.get("source_payload")
    if not isinstance(source_payload, dict):
        raise ValueError("DoRA activity source provenance is required")
    resource = source_payload.get("resource")
    if not isinstance(resource, dict) or not resource.get("id"):
        raise ValueError("DoRA activity resource provenance is required")
    records = envelope.get("records")
    if not isinstance(records, list):
        raise ValueError("DoRA activity records are required")
    validate_records(records, int(envelope.get("retrieved_count", -1)))
    resource_id = str(resource["id"])
    resource_url = str(resource.get("url") or "")
    observed_at = str(envelope.get("observed_at") or "")
    if not observed_at:
        raise ValueError("DoRA activity observation time is required")
    rows = []
    for record in records:
        row = {name: record.get(name) for name in SOURCE_FIELDS}
        row.update({
            "DORAActivityKey": activity_key(resource_id, record),
            "DORARecordID": record.get("_id"),
            "DORAResourceID": resource_id,
            "DORAResourceName": resource.get("name"),
            "DORAResourceLastModified": resource.get("last_modified"),
            "DORAObservedUTC": observed_at,
            "DORASourceURL": resource_url,
        })
        rows.append(row)
    return rows


def export_envelope(envelope: dict[str, Any], output: Path) -> Path:
    if output.exists():
        raise FileExistsError(f"Refusing to overwrite {output}")
    rows = build_rows(envelope)
    output.mkdir(parents=True)
    with (output / "dora-activity-registry.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=EXPORT_FIELDS, quoting=csv.QUOTE_ALL, lineterminator="\n")
        writer.writeheader()
        writer.writerows({name: safe_cell(row.get(name)) for name in EXPORT_FIELDS} for row in rows)
    (output / "dora-activity-registry.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return output


def export(envelope_path: Path, output: Path) -> Path:
    return export_envelope(json.loads(envelope_path.read_text(encoding="utf-8")), output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("envelope", type=Path, help="Collector output containing receipt.json and records.json")
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    receipt = json.loads((args.envelope / "receipt.json").read_text(encoding="utf-8"))
    receipt["records"] = json.loads((args.envelope / "records.json").read_text(encoding="utf-8"))
    print(export_envelope(receipt, args.output))
