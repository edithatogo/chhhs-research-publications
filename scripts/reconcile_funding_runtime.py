#!/usr/bin/env python3
"""Fail-closed runtime parity for a complete DEV grants list and bound model readback.

Inputs are saved authenticated receipts; this tool never connects to a tenant.
Keep source rows and IDs under ignored private/ops. The output contains counts
only, so it can be shared without exposing opportunity identities.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID


# The complete string projection in config/grants-registry.schema.json and
# config/GrantsRegistry.m. Keep this contract in step with the schema.
CANONICAL_FIELDS = (
    "OpportunityKey", "Title", "Funder", "Source", "SourceID", "RoundID",
    "URL", "SourceRowURL", "Description", "Eligibility", "Geography", "Amount", "Deadline",
    "DeadlineRaw", "DeadlineTimezone", "DeadlineLocalTime", "DeadlineUTCInstant",
    "DeadlineBrisbaneDate", "DeadlineBrisbaneTime", "DeadlineTemporalStatus",
    "DeadlinePrecision", "DeadlineScheduleJSON", "SourceDateFactsJSON", "SourceAttribution", "Status", "Contact", "CHHHSRelevance",
    "ReviewStatus", "ReviewNotes", "RetrievedUTC", "RetrievedTimestampStatus",
    "EvidenceHash",
)


def _time(value: object) -> datetime:
    if not isinstance(value, str):
        raise ValueError("timezone-aware observed/end time required")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("timezone-aware observed/end time required")
    return parsed.astimezone(timezone.utc)


def _keys(rows: object, key_field: str, status_field: str) -> tuple[set[str], int]:
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        raise ValueError("rows must be an array of objects")
    keys: set[str] = set()
    unreviewed = 0
    for row in rows:
        key = row.get(key_field)
        if not isinstance(key, str) or not key or key != key.strip():
            raise ValueError("blank or malformed OpportunityKey")
        if key in keys:
            raise ValueError("duplicate OpportunityKey")
        keys.add(key)
        status = row.get(status_field)
        if status != "Reviewed":
            unreviewed += 1
    return keys, unreviewed


def _projection(rows: list[dict], *, model: bool) -> dict[str, dict[str, str | None]]:
    """Require the full canonical row and preserve null versus empty text."""
    projected = {}
    for row in rows:
        values = {}
        for field in CANONICAL_FIELDS:
            name = f"[{field}]" if model else field
            if name not in row:
                raise ValueError(f"missing canonical field {field}")
            value = row[name]
            # SharePoint REST represents URL fields as {Url, Description};
            # the model's text projection contains the Url value.
            if field in {"URL", "SourceRowURL"} and not model and isinstance(value, dict):
                value = value.get("Url")
            if value is not None and not isinstance(value, str):
                raise ValueError(f"non-text canonical field {field}")
            values[field] = value
        projected[values["OpportunityKey"]] = values
    return projected


def _guid(value: object) -> UUID:
    if not isinstance(value, str):
        raise ValueError("SharePoint list GUID required")
    try:
        return UUID(value.strip("{}"))
    except ValueError as exc:
        raise ValueError("SharePoint list GUID required") from exc


def _count(receipt: dict, name: str, rows: object) -> int:
    """Require a native/query total that agrees with the exported rows."""
    value = receipt.get(name)
    if type(value) is not int or value < 0 or value != len(rows):
        raise ValueError(f"{name} must equal the complete exported row count")
    return value


def reconcile(list_receipt: dict, model_receipt: dict, refresh_receipt: dict,
              binding_receipt: dict) -> dict:
    """Require non-vacuous exact keys, reviewed admission and ordered refresh evidence."""
    if list_receipt.get("complete") is not True or list_receipt.get("next_links") != []:
        raise ValueError("complete list export with next_links=[] required")
    if model_receipt.get("complete") is not True or model_receipt.get("truncated") is not False:
        raise ValueError("complete, nontruncated model query required")
    list_id = list_receipt.get("list_id")
    model_id = model_receipt.get("dataset_id")
    if not isinstance(list_id, str) or not list_id or not isinstance(model_id, str) or not model_id:
        raise ValueError("list and dataset identities required")
    if refresh_receipt.get("dataset_id") != model_id:
        raise ValueError("refresh dataset does not match queried model")
    if binding_receipt.get("complete") is not True:
        raise ValueError("complete native model source binding required")
    if binding_receipt.get("dataset_id") != model_id or _guid(binding_receipt.get("list_id")) != _guid(list_id):
        raise ValueError("model source binding does not match list and dataset")
    if binding_receipt.get("table") != "Grants Registry" or binding_receipt.get("source_kind") != "SharePoint.Tables":
        raise ValueError("native Grants Registry SharePoint.Tables binding required")
    list_site = list_receipt.get("site_url")
    binding_site = binding_receipt.get("site_url")
    if not all(isinstance(site, str) and site.startswith("https://") for site in (list_site, binding_site)):
        raise ValueError("list and binding HTTPS site URLs required")
    if list_site.rstrip("/").casefold() != binding_site.rstrip("/").casefold():
        raise ValueError("model source binding site does not match list site")
    list_time = _time(list_receipt.get("observed_at"))
    model_time = _time(model_receipt.get("observed_at"))
    binding_time = _time(binding_receipt.get("observed_at"))
    refresh_end = _time(refresh_receipt.get("endTime")) if refresh_receipt.get("status") == "Completed" else None
    list_keys, list_unreviewed = _keys(list_receipt.get("rows"), "OpportunityKey", "ReviewStatus")
    model_keys, model_unreviewed = _keys(model_receipt.get("rows"), "[OpportunityKey]", "[ReviewStatus]")
    _count(list_receipt, "item_count", list_receipt["rows"])
    _count(model_receipt, "row_count", model_receipt["rows"])
    list_rows = _projection(list_receipt["rows"], model=False)
    model_rows = _projection(model_receipt["rows"], model=True)
    mismatched_fields = sorted({field for key in list_keys & model_keys
                                for field in CANONICAL_FIELDS
                                if list_rows[key][field] != model_rows[key][field]})
    counts = {
        "list_rows": len(list_keys), "model_rows": len(model_keys),
        "list_unreviewed_rows": list_unreviewed, "model_unreviewed_rows": model_unreviewed,
        "list_only_keys": len(list_keys - model_keys), "model_only_keys": len(model_keys - list_keys),
        "mismatched_fields": len(mismatched_fields),
    }
    # Both key inventories must describe state observed after the terminal refresh.
    evidence_ordered = bool(refresh_end and refresh_end <= binding_time <= list_time
                            and binding_time <= model_time)
    status = "PASS" if (list_keys and model_keys and refresh_receipt.get("status") == "Completed"
                        and evidence_ordered and list_unreviewed == model_unreviewed == 0
                        and list_keys == model_keys and not mismatched_fields) else "UNPROVEN"
    return {
        "kind": "funding_grants_runtime_parity_v1", "status": status,
        "counts": counts,
        "mismatched_field_names": mismatched_fields,
        "terminal_refresh_completed": refresh_receipt.get("status") == "Completed",
        "native_source_binding_matched": True,
        "evidence_ordered": evidence_ordered,
        "interpretation": "Exact nonempty canonical row and Reviewed parity after a completed bound-model refresh; report filters/rendering and flow delivery are separate gates",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list", type=Path, required=True)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--refresh", type=Path, required=True)
    parser.add_argument("--binding", type=Path, required=True,
                        help="Complete current native Grants Registry partition/source receipt")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = reconcile(*(json.loads(path.read_text(encoding="utf-8")) for path in
                         (args.list, args.model, args.refresh, args.binding)))
    rendered = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
