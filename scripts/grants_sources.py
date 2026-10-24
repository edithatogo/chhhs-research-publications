"""Validate official, machine-readable and reconciled grants sources only."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from pathlib import PurePosixPath
from typing import Any
from urllib.parse import urlsplit

try:
    from scripts.grants_source_identity import validate_source_id_path
except ImportError:
    from grants_source_identity import validate_source_id_path

REQUIRED_SOURCE_IDS = {"arc-awards-api", "queensland-grants-finder-catalogue-api"}
# These two canonical rows are required for context, but their entity classes
# must never be promoted into opportunity intake by editing catalogue labels.
REQUIRED_SOURCE_CLASS = {
    "arc-awards-api": ("awarded_grant_context", "awarded_grant", "context_only"),
    "queensland-grants-finder-catalogue-api": (
        "source_metadata_only", "source_catalogue", "metadata_only"
    ),
}
ALLOWED_INTAKE = {"rss", "atom", "api"}
ALLOWED_HEALTH = {"verified_sample"}
ALLOWED_ADMISSION = {"opportunity", "awarded_grant", "context_only", "metadata_only", "candidate_only"}
DEFAULT_CATALOGUE = Path(__file__).resolve().parents[1] / "config" / "grants-sources.json"
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
OPPORTUNITY_QUALIFICATION_FIELDS = (
    "access",
    "response_schema",
    "bounded_sample",
    "complete_pagination",
    "replay_keyset",
    "stable_identity",
    "round_semantics",
    "lifecycle_semantics",
    "reuse_terms",
    "entity_reconciliation",
)
QUALIFICATION_STATUSES = {"verified", "partial", "unverified", "not_applicable"}
REUSE_DECISIONS = {"permitted", "restricted", "not_permitted", "unresolved", "not_applicable"}
# Access decisions are classifications of source evidence, not permission grants.
ACCESS_DECISIONS = {
    "public", "existing_authorized", "restricted", "unavailable", "unresolved", "not_applicable"
}

NIH_SELECTED_SOURCE = "us-grants-gov-nih-pa-25-301"
NIH_SEARCH_URL = "https://api.grants.gov/v1/api/search2"
NIH_SEARCH_BODY = {
    "oppNum": "PA-25-301", "rows": 10,
    "oppStatuses": "forecasted|posted|closed|archived",
}


def source_request_contract(row: dict[str, Any]) -> tuple[str, dict | None]:
    """Allow only the selected documented read-only POST, never generic POSTs."""
    method = row.get("request_method", "GET")
    if row.get("source_id") == NIH_SELECTED_SOURCE:
        reconciliation = row.get("reconciliation")
        if (method != "POST" or row.get("intake") != "api"
                or row.get("api_url") != NIH_SEARCH_URL
                or row.get("request_body") != NIH_SEARCH_BODY
                or not isinstance(reconciliation, dict)
                or reconciliation.get("source_id_path") != "data.oppHits[].id"):
            raise ValueError("selected NIH request scope must remain exact")
        return method, dict(NIH_SEARCH_BODY)
    if method != "GET" or "request_body" in row:
        raise ValueError("unsupported source request; only selected NIH read-only POST is qualified")
    return method, None


def qualification_error(row: dict[str, Any], *, require_opportunity: bool = False) -> str | None:
    """Validate the recorded evidence state for one source catalogue row."""
    qualification = row.get("qualification")
    if not isinstance(qualification, dict):
        return "source_qualification_missing"
    observed_at = qualification.get("observed_at")
    if not isinstance(observed_at, str) or observed_at != observed_at.strip():
        return "source_qualification_observation_missing"
    try:
        observed = datetime.fromisoformat(observed_at.replace("Z", "+00:00"))
    except ValueError:
        return "source_qualification_observation_invalid"
    if observed.tzinfo is None or observed.utcoffset() is None:
        return "source_qualification_observation_invalid"
    for field in OPPORTUNITY_QUALIFICATION_FIELDS:
        field_qualification = qualification.get(field)
        status = field_qualification.get("status") if isinstance(field_qualification, dict) else None
        if not isinstance(status, str) or status not in QUALIFICATION_STATUSES:
            return "source_qualification_status_invalid"
    if any(
        not isinstance(qualification[field].get("evidence_refs"), list)
        or not qualification[field]["evidence_refs"]
        or any(not _valid_evidence_ref(ref)
               for ref in qualification[field]["evidence_refs"])
        for field in OPPORTUNITY_QUALIFICATION_FIELDS
    ):
        return "source_qualification_evidence_invalid"
    reuse_decision = qualification["reuse_terms"].get("decision")
    reuse_status = qualification["reuse_terms"]["status"]
    if (not isinstance(reuse_decision, str) or reuse_decision not in REUSE_DECISIONS
            or (reuse_decision == "permitted" and reuse_status != "verified")):
        return "source_qualification_reuse_decision_invalid"
    access_decision = qualification["access"].get("decision")
    access_status = qualification["access"]["status"]
    if (not isinstance(access_decision, str) or access_decision not in ACCESS_DECISIONS
            or (access_decision in {"public", "existing_authorized"}
                and access_status != "verified")):
        return "source_qualification_access_decision_invalid"
    if require_opportunity and any(
        qualification[field]["status"] != "verified"
        for field in OPPORTUNITY_QUALIFICATION_FIELDS
    ):
        return "source_qualification_incomplete"
    if require_opportunity and reuse_decision != "permitted":
        return "source_qualification_incomplete"
    if require_opportunity and access_decision not in {"public", "existing_authorized"}:
        return "source_qualification_incomplete"
    return None


def required_source_class_matches(row: dict[str, Any]) -> bool:
    """Keep canonical award/metadata sources out of opportunity intake."""
    expected = REQUIRED_SOURCE_CLASS.get(row.get("source_id"))
    if expected is None:
        return True
    reconciliation = row.get("reconciliation")
    if not isinstance(reconciliation, dict):
        return False
    return (
        row.get("record_kind"), reconciliation.get("entity"),
        reconciliation.get("admission"),
    ) == expected


def _https_url(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    raw = value
    if raw != raw.strip() or any(char.isspace() or ord(char) < 32 for char in raw):
        return False
    try:
        parsed = urlsplit(raw)
        host = parsed.hostname
        # Catalogue endpoints and authority pages are public source locations,
        # so credentials and custom ports are never part of the contract. In
        # particular, checking only netloc would accept URLs such as
        # https://official.example@attacker.test/...
        return (parsed.scheme.casefold() == "https" and bool(host) and "." in host
                and not host.endswith(".") and not parsed.username and not parsed.password
                and parsed.port is None)
    except ValueError:
        return False


def _valid_evidence_ref(value: Any) -> bool:
    if _https_url(value):
        return True
    if not isinstance(value, str) or not value or value != value.strip() or "\\" in value:
        return False
    path = PurePosixPath(value)
    if (path.is_absolute() or value != path.as_posix()
            or any(part in {".", ".."} for part in path.parts)
            or len(path.parts) < 2 or not path.suffix):
        return False
    try:
        resolved = (REPOSITORY_ROOT / Path(*path.parts)).resolve(strict=True)
        resolved.relative_to(REPOSITORY_ROOT.resolve())
    except (OSError, RuntimeError, ValueError):
        return False
    return resolved.is_file()


def load_catalogue(path: str | Path) -> list[dict[str, Any]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("grants source catalogue must be a list")
    seen: set[str] = set()
    for row in payload:
        if not isinstance(row, dict):
            raise ValueError("each source catalogue row must be an object")
        source_id_value = row.get("source_id")
        if not isinstance(source_id_value, str):
            raise ValueError("source_id must be text")
        source_id = source_id_value.strip()
        if source_id != source_id_value or not source_id:
            raise ValueError("source_id must be nonempty unpadded text")
        if source_id in seen:
            raise ValueError(f"duplicate or missing source_id: {source_id!r}")
        seen.add(source_id)
        if not isinstance(row.get("enabled"), bool):
            raise ValueError(f"source {source_id!r} needs boolean enabled state")
        if (not _https_url(row.get("authority_url"))
                or not isinstance(row.get("title"), str)
                or not row["title"].strip()):
            raise ValueError(f"source {source_id!r} needs official HTTPS authority_url and title")
        intake = row.get("intake")
        if intake not in ALLOWED_INTAKE:
            raise ValueError(f"source {source_id!r} has unsupported non-machine intake")
        endpoint_field = "api_url" if intake == "api" else "feed_url"
        if not _https_url(row.get(endpoint_field)):
            raise ValueError(f"source {source_id!r} with {intake} intake needs HTTPS {endpoint_field}")
        source_request_contract(row)
        if row.get("health_status") not in ALLOWED_HEALTH:
            raise ValueError(f"source {source_id!r} is not verified for machine reconciliation")
        reconciliation = row.get("reconciliation")
        if not isinstance(reconciliation, dict):
            raise ValueError(f"source {source_id!r} needs reconciliation contract")
        if not isinstance(reconciliation.get("source_id_path"), str) or not reconciliation["source_id_path"].strip():
            raise ValueError(f"source {source_id!r} needs reconciliation source_id_path")
        try:
            validate_source_id_path(reconciliation["source_id_path"], intake)
        except ValueError as exc:
            raise ValueError(f"source {source_id!r} has invalid reconciliation source_id_path") from exc
        stable_key_prefix = reconciliation.get("stable_key_prefix")
        if (not isinstance(stable_key_prefix, str) or not stable_key_prefix
                or stable_key_prefix != stable_key_prefix.strip()):
            raise ValueError(
                f"source {source_id!r} needs a nonempty unpadded reconciliation stable_key_prefix"
            )
        if reconciliation.get("admission") not in ALLOWED_ADMISSION:
            raise ValueError(f"source {source_id!r} has unsupported reconciliation admission")
        if not required_source_class_matches(row):
            raise ValueError(f"source {source_id!r} has an immutable non-opportunity entity class")
        if reconciliation.get("admission") == "opportunity":
            if reconciliation.get("entity") != "opportunity":
                raise ValueError(f"source {source_id!r} has mismatched opportunity entity")
            hosts = row.get("official_row_hosts")
            if (not isinstance(hosts, list) or not hosts
                    or any(not isinstance(host, str) or not host
                           or host != host.strip().casefold()
                           or not _https_url(f"https://{host}/")
                           or urlsplit(f"https://{host}/").hostname != host
                           for host in hosts)):
                raise ValueError(f"source {source_id!r} needs official_row_hosts")
        source_qualification_error = qualification_error(
            row, require_opportunity=reconciliation.get("admission") == "opportunity"
        )
        if source_qualification_error:
            raise ValueError(f"source {source_id!r} {source_qualification_error}")
        for field in ("authority_type", "eligibility_scope", "format", "access", "coverage", "record_kind"):
            if not isinstance(row.get(field), str) or not row[field].strip():
                raise ValueError(f"source {source_id!r} needs {field}")
    missing = REQUIRED_SOURCE_IDS - seen
    if missing:
        raise ValueError(f"required sources missing: {sorted(missing)}")
    return payload


def require_enabled_source(path: str | Path, source_id: str) -> dict[str, Any]:
    """Resolve one exact catalogue row and fail before network access if stopped."""
    rows = load_catalogue(path)
    matches = [row for row in rows if row["source_id"] == source_id]
    if len(matches) != 1:
        raise ValueError("source_missing_or_ambiguous")
    if not matches[0]["enabled"]:
        raise ValueError("source_disabled")
    return matches[0]


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("catalogue", type=Path)
    args = parser.parse_args()
    rows = load_catalogue(args.catalogue)
    print(f"validated {len(rows)} official reconciled grant source rows")
