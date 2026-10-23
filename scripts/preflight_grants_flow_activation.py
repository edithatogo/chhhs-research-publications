"""Fail-closed, read-only grants flow binding and replay preflight.

Inputs are private, current native exports/readbacks, not a plan or a package
template. PASS permits a controlled test decision; it is not activation approval.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import UUID

try:
    from .grants_registry import stable_key
except ImportError:
    from grants_registry import stable_key

MAX_READBACK_AGE_HOURS = 24


def _utc(value: Any) -> datetime:
    if not isinstance(value, str):
        raise ValueError("missing UTC observation time")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timezone-aware observation time required")
    return parsed.astimezone(timezone.utc)


def _identity(row: dict[str, Any]) -> tuple[str, str, str]:
    return tuple(row.get(name, "").strip() if isinstance(row.get(name), str) else ""
                 for name in ("Source", "SourceID", "RoundID"))


def preflight(*, flow: dict[str, Any], target: dict[str, Any], snapshot: dict[str, Any],
              batch: dict[str, Any], checked_at: datetime | None = None) -> dict[str, Any]:
    errors: list[str] = []
    def reject(condition: bool, code: str) -> None:
        if condition:
            errors.append(code)

    try:
        list_id = str(UUID(target["list_id"]))
    except (KeyError, ValueError, TypeError, AttributeError):
        return {"accepted": False, "errors": ["invalid_target_list_id"]}
    site = target.get("site_url")
    reject(not isinstance(site, str) or not site.startswith("https://") or "{{" in site,
           "invalid_target_site")
    reject(target.get("key_required") is not True or target.get("key_indexed") is not True
           or target.get("key_unique") is not True, "missing_native_unique_key_proof")
    reject(flow.get("complete") is not True or flow.get("saved_state") != "Off",
           "flow_export_or_off_state_unproved")
    reject(flow.get("flow_id") != target.get("flow_id"), "flow_identity_mismatch")
    actions = flow.get("actions")
    required = ("SharePoint_Get_items", "SharePoint_Create_item", "SharePoint_Update_item")
    if not isinstance(actions, dict) or set(actions) != set(required):
        errors.append("flow_actions_incomplete")
    else:
        for action in required:
            binding = actions[action]
            reject(not isinstance(binding, dict) or binding.get("site_url") != site
                   or binding.get("list_id") != list_id, f"{action}_target_mismatch")
    reject(flow.get("serial_loop") is not True or flow.get("exact_match_branches") is not True,
           "replay_graph_unproved")
    reject(snapshot.get("complete") is not True or snapshot.get("list_id") != list_id
           or snapshot.get("site_url") != site, "snapshot_incomplete_or_wrong_target")
    rows = snapshot.get("rows")
    incoming = batch.get("rows")
    reject(not isinstance(rows, list) or snapshot.get("count") != (len(rows) if isinstance(rows, list) else None),
           "snapshot_count_mismatch")
    reject(not isinstance(incoming, list) or not incoming or batch.get("complete") is not True,
           "batch_incomplete_or_empty")
    try:
        checked = checked_at or datetime.now(timezone.utc)
        if checked.tzinfo is None or checked.utcoffset() is None:
            raise ValueError("check time requires timezone")
        checked = checked.astimezone(timezone.utc)
        times = [_utc(item.get("observed_at_utc")) for item in (flow, target, snapshot, batch)]
        reject(not (times[0] <= times[2] <= times[3]), "stale_or_unordered_binding_snapshot")
        reject(times[1] > times[2], "target_observed_after_snapshot")
        reject(any(not 0 <= (checked - observed).total_seconds() <= MAX_READBACK_AGE_HOURS * 3600
                   for observed in times), "stale_or_future_readback")
    except ValueError:
        errors.append("observation_time_invalid")
    if not isinstance(rows, list) or not isinstance(incoming, list):
        return {"accepted": False, "errors": sorted(set(errors))}

    keys: dict[str, dict[str, Any]] = {}
    identities: dict[tuple[str, str, str], str] = {}
    for origin, group in (("snapshot", rows), ("batch", incoming)):
        local_keys: set[str] = set()
        for row in group:
            if not isinstance(row, dict):
                errors.append(f"{origin}_row_invalid")
                continue
            title = row.get("Title")
            if not isinstance(title, str) or not title.strip():
                errors.append(f"{origin}_title_invalid")
            key = row.get("OpportunityKey")
            identity = _identity(row)
            evidence_hash = row.get("EvidenceHash")
            if (not isinstance(key, str) or not key.strip() or key != key.strip()
                    or not identity[0] or not any(identity[1:])
                    or not isinstance(evidence_hash, str) or not evidence_hash.strip()
                    or any(row.get(name) is not None and not isinstance(row[name], str)
                           for name in ("SourceID", "RoundID"))):
                errors.append(f"{origin}_identity_incomplete")
                continue
            if origin == "batch":
                if stable_key(row) != key:
                    errors.append("batch_key_does_not_match_source_identity")
                if row.get("ReviewStatus") != "Reviewed" or not isinstance(row.get("ReviewNotes"), str) or not row["ReviewNotes"].strip():
                    errors.append("batch_review_unproved")
            try:
                _utc(row.get("RetrievedUTC"))
            except ValueError:
                errors.append(f"{origin}_retrieval_time_invalid")
            if key in local_keys:
                errors.append(f"{origin}_duplicate_key")
            local_keys.add(key)
            prior_key = identities.setdefault(identity, key)
            if prior_key != key:
                errors.append("source_identity_key_collision")
            prior = keys.get(key)
            if prior is not None and _identity(prior) != identity:
                errors.append("key_reassigned_to_different_source")
            if origin == "batch" and prior is not None:
                try:
                    if _utc(row.get("RetrievedUTC")) < _utc(prior.get("RetrievedUTC")):
                        errors.append("older_observation_replay")
                except ValueError:
                    errors.append("retrieval_time_invalid")
            keys[key] = row
    return {"accepted": not errors, "errors": sorted(set(errors)),
            "snapshot_count": len(rows), "batch_count": len(incoming),
            "boundary": "Local preflight only; native graph, run and row-level acceptance require saved readback."}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("flow", "target", "snapshot", "batch"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    private = (Path(__file__).resolve().parents[1] / "private" / "ops").resolve()
    paths = [getattr(args, name).resolve() for name in ("flow", "target", "snapshot", "batch")]
    if not all(path.is_relative_to(private) for path in paths) or not args.output.resolve().is_relative_to(private):
        parser.error("all inputs and output must stay under ignored private/ops")
    result = preflight(**{name: json.loads(getattr(args, name).read_text())
                          for name in ("flow", "target", "snapshot", "batch")})
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(f"accepted={result['accepted']} errors={','.join(result['errors'])}")
    return 0 if result["accepted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
