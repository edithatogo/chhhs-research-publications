"""Fail-closed importer for human-reviewed grants source observations.

This is the fallback for authority pages that do not expose a permitted
RSS/Atom/API route. It never treats a discovered HTML row as accepted merely
because it has a title; a reviewer must provide the source identity, row URL,
observation timestamp and explicit ``Reviewed`` status.
"""
from __future__ import annotations

import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

try:
    from .grants_registry import normalize_opportunity, stable_key, valid_official_url
    from .grants_deadline_schedule import require_source_schedule
except ImportError:  # direct script execution with scripts/ on sys.path
    from grants_registry import normalize_opportunity, stable_key, valid_official_url
    from grants_deadline_schedule import require_source_schedule


# Reviewer identity and audit provenance cannot be established by a JSON row.
# Keep those fields out of the import contract so a source file cannot make a
# self-asserted identity look like authenticated review evidence.
UNTRUSTED_PROVENANCE_FIELDS = frozenset({
    "Reviewer", "ReviewerEmail", "ReviewerID", "ReviewedBy", "ReviewedByEmail",
    "ReviewedByID", "ReviewTimestamp", "ReviewedUTC", "ReviewEvidence",
    "Provenance", "NativeAccepted", "VerifiedBy",
})

# The target schema stores these source facts as text. Reject structured or
# numeric values at intake rather than letting the shared normalizer stringify
# them into apparently reviewed authority facts.
SOURCE_TEXT_FIELDS = frozenset({
    "SourceID", "RoundID", "Funder", "Organization", "funder", "Description", "SourceRowURL",
    "Summary", "summary", "Eligibility", "Geography", "Amount", "Deadline",
    "ClosingDate", "deadline", "DeadlineTimezone", "deadlineTimezone", "deadline_timezone",
    "SourceTimezone", "sourceTimezone", "source_timezone", "Timezone", "timezone", "time_zone",
    "Status", "Contact", "CHHHSRelevance", "DeadlineScheduleJSON", "SourceDateFactsJSON", "SourceAttribution",
})
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
PRIVATE_OPS_ROOT = REPOSITORY_ROOT / "private" / "ops"


def review_errors(row: dict[str, Any], *, expected_source: str | None = None,
                  official_hosts: Iterable[str] = ()) -> list[str]:
    """Return all admission errors without silently repairing reviewer input."""
    errors: list[str] = []
    try:
        require_source_schedule(row)
    except (ValueError, TypeError, KeyError):
        errors.append("invalid_source_schedule")
    if UNTRUSTED_PROVENANCE_FIELDS.intersection(row):
        errors.append("untrusted_reviewer_provenance")
    source = str(row.get("Source", "")).strip()
    if expected_source and source != expected_source:
        errors.append("source_mismatch")
    for field in ("Source", "Title", "RetrievedUTC"):
        if not isinstance(row.get(field), str) or not row[field].strip():
            errors.append(f"missing_{field}")
    for field in sorted(SOURCE_TEXT_FIELDS):
        if row.get(field) is not None and not isinstance(row[field], str):
            errors.append(f"invalid_{field}_type")
    if "OpportunityKey" in row:
        if not isinstance(row["OpportunityKey"], str):
            errors.append("invalid_OpportunityKey_type")
        elif row["OpportunityKey"] != stable_key(row):
            errors.append("OpportunityKey_mismatch")
    if not valid_official_url(row.get("URL"), official_hosts):
        errors.append("invalid_URL")
    if row.get("SourceRowURL") not in (None, "") and not valid_official_url(row.get("SourceRowURL"), official_hosts):
        errors.append("invalid_SourceRowURL")
    if not isinstance(row.get("ReviewStatus"), str) or row["ReviewStatus"].strip().casefold() != "reviewed":
        errors.append("ReviewStatus_not_Reviewed")
    if not isinstance(row.get("ReviewNotes"), str) or not row["ReviewNotes"].strip():
        errors.append("missing_ReviewNotes")
    if not (isinstance(row.get("SourceID"), str) and row["SourceID"].strip()
            or isinstance(row.get("RoundID"), str) and row["RoundID"].strip()):
        errors.append("missing_SourceID_or_RoundID")
    return errors


def import_reviewed_rows(
    rows: Iterable[dict[str, Any]],
    *,
    expected_source: str | None = None,
    official_hosts: Iterable[str] = (),
) -> list[dict[str, Any]]:
    """Normalize reviewed rows or reject the complete batch fail-closed."""
    try:
        materialized = list(rows)
    except Exception as exc:
        # A stream may fail after yielding some rows. Never expose or accept
        # that partial materialization; report one stable contract error.
        raise ValueError("reviewed import must be an iterable of row objects") from exc
    failures: list[tuple[int, list[str]]] = []
    result: list[dict[str, Any]] = []
    for index, row in enumerate(materialized):
        if not isinstance(row, dict):
            failures.append((index, ["row_not_object"]))
            continue
        errors = review_errors(row, expected_source=expected_source, official_hosts=official_hosts)
        if errors:
            failures.append((index, errors))
            continue
        normalized = normalize_opportunity(row, retrieved_at=row["RetrievedUTC"])
        if normalized["RetrievedTimestampStatus"] != "valid":
            failures.append((index, ["RetrievedUTC_not_timezone_aware"]))
            continue
        if normalized["DeadlineRaw"] and normalized["DeadlinePrecision"] == "unknown":
            failures.append((index, ["invalid_Deadline"]))
            continue
        result.append(normalized)
    if failures:
        detail = "; ".join(f"row {index}: {','.join(errors)}" for index, errors in failures)
        raise ValueError(f"reviewed import rejected: {detail}")
    if not result:
        raise ValueError("reviewed import rejected: empty batch")
    keys = [row["OpportunityKey"] for row in result]
    if len(keys) != len(set(keys)):
        raise ValueError("reviewed import rejected: duplicate OpportunityKey")
    return result


def load_reviewed_import(path: str | Path, *, expected_source: str | None = None,
                         official_hosts: Iterable[str] = ()) -> list[dict[str, Any]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    rows = payload.get("rows") if isinstance(payload, dict) else payload
    if not isinstance(rows, list):
        raise ValueError("reviewed import must be a list or an object with rows")
    return import_reviewed_rows(rows, expected_source=expected_source, official_hosts=official_hosts)


def reconcile_reviewed_batches(
    current: Iterable[dict[str, Any]], prior: Iterable[dict[str, Any]] = (),
) -> dict[str, Any]:
    """Compare already validated imports without inferring closure from absence.

    A reviewed file may be a partial export. Its missing keys are therefore
    observations to investigate, never deletion or status instructions.
    """
    def index(rows: Iterable[dict[str, Any]]) -> dict[str, dict[str, Any]]:
        indexed: dict[str, dict[str, Any]] = {}
        for row in rows:
            if not isinstance(row, dict) or not isinstance(row.get("OpportunityKey"), str):
                raise ValueError("reconciliation requires normalized reviewed records")
            key = row["OpportunityKey"]
            if not key or key in indexed or row.get("ReviewStatus") != "Reviewed":
                raise ValueError("reconciliation requires unique reviewed OpportunityKeys")
            if (not isinstance(row.get("Source"), str) or not row["Source"].strip()
                    or any(row.get(field) is not None and not isinstance(row[field], str)
                           for field in ("SourceID", "RoundID"))
                    or not (str(row.get("SourceID") or "").strip()
                            or str(row.get("RoundID") or "").strip())
                    or stable_key(row) != key):
                raise ValueError("reconciliation requires keys matching text source identities")
            indexed[key] = row
        return indexed

    def observed_at(row: dict[str, Any]) -> datetime:
        value = row.get("RetrievedUTC")
        if row.get("RetrievedTimestampStatus") != "valid" or not isinstance(value, str):
            raise ValueError("reconciliation requires valid observation timestamps")
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError("reconciliation requires valid observation timestamps") from exc
        if parsed.tzinfo is None:
            raise ValueError("reconciliation requires valid observation timestamps")
        return parsed.astimezone(timezone.utc)

    current_index, prior_index = index(current), index(prior)
    if not current_index:
        raise ValueError("reconciliation requires a nonempty current reviewed batch")

    # A reviewed file can be a partial snapshot, but a row for a key already
    # seen must not roll that key back to an older source observation.
    for row in (*current_index.values(), *prior_index.values()):
        observed_at(row)
    if any(observed_at(current_index[key]) < observed_at(prior_index[key])
           for key in current_index.keys() & prior_index.keys()):
        raise ValueError("reviewed import rejected: older_observation")

    # An unchanged observation instant cannot establish which of two
    # conflicting authority facts is newer. Reviewer notes may change on
    # re-review; source facts require a newer observation before replacement.
    source_fields = (
        "Title", "Funder", "Source", "SourceID", "RoundID", "URL", "SourceRowURL",
        "Description", "Eligibility", "Geography", "Amount", "Deadline",
        "DeadlineRaw", "DeadlinePrecision", "DeadlineTimezone", "DeadlineLocalTime",
        "DeadlineUTCInstant", "DeadlineBrisbaneDate", "DeadlineBrisbaneTime",
        "DeadlineTemporalStatus", "DeadlineScheduleJSON", "SourceDateFactsJSON", "SourceAttribution", "Status", "Contact",
    )
    if any(observed_at(current_index[key]) == observed_at(prior_index[key])
           and any(current_index[key].get(field) != prior_index[key].get(field)
                   for field in source_fields)
           for key in current_index.keys() & prior_index.keys()):
        raise ValueError("reviewed import rejected: conflicting_same_time_observation")

    def digest(rows: dict[str, dict[str, Any]]) -> str:
        canonical = json.dumps(rows, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    current_keys, prior_keys = set(current_index), set(prior_index)
    shared = current_keys & prior_keys
    return {
        "current_count": len(current_index),
        "current_digest": digest(current_index),
        "prior_count": len(prior_index),
        "prior_digest": digest(prior_index) if prior_index else None,
        "added_keys": sorted(current_keys - prior_keys),
        "changed_keys": sorted(key for key in shared if current_index[key] != prior_index[key]),
        "unchanged_keys": sorted(key for key in shared if current_index[key] == prior_index[key]),
        "unobserved_in_current_batch": sorted(prior_keys - current_keys),
        "deletion_inferred": False,
    }


def public_import_summary(records: list[dict[str, Any]], reconciliation: dict[str, Any],
                          *, compared: bool) -> dict[str, Any]:
    """Return bounded acceptance metadata without reviewed/source row values."""
    return {
        "status": "validated_reviewed_import",
        "validated_row_count": len(records),
        "prior_batch_compared": compared,
        "prior_row_count": reconciliation["prior_count"],
        "added_key_count": len(reconciliation["added_keys"]),
        "changed_key_count": len(reconciliation["changed_keys"]),
        "unchanged_key_count": len(reconciliation["unchanged_keys"]),
        "not_observed_in_current_count": len(reconciliation["unobserved_in_current_batch"]),
        "deletion_inferred": False,
        "tenant_admission": False,
        "raw_records_omitted": True,
    }


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument("--source")
    parser.add_argument("--official-host", action="append", required=True)
    parser.add_argument("--compare-to", type=Path, help="earlier reviewed import to reconcile")
    parser.add_argument(
        "--out", type=Path,
        help="save full validated rows and reconciliation under ignored private/ops/",
    )
    args = parser.parse_args(argv)
    destination = None
    if args.out:
        destination = args.out.resolve()
        try:
            destination.relative_to(PRIVATE_OPS_ROOT.resolve())
        except ValueError:
            parser.error("--out must be inside the repository's ignored private/ops directory")
        if destination.exists():
            parser.error("--out refuses to overwrite existing private evidence")
    records = load_reviewed_import(args.path, expected_source=args.source, official_hosts=args.official_host)
    prior = (load_reviewed_import(args.compare_to, expected_source=args.source,
                                  official_hosts=args.official_host) if args.compare_to else ())
    reconciliation = reconcile_reviewed_batches(records, prior)
    if destination:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps({"validated_row_count": len(records),
                                           "reconciliation": reconciliation,
                                           "records": records}, indent=2, ensure_ascii=False) + "\n",
                              encoding="utf-8")
    print(json.dumps(public_import_summary(records, reconciliation, compared=bool(args.compare_to)),
                     indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
