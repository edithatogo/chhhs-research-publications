"""Canonical, review-gated grants and funding opportunities registry.

The module accepts already-collected RSS/Atom or API-shaped dictionaries. It
does not fetch external sites, submit applications, or infer eligibility.
"""
from __future__ import annotations

import hashlib
import re
from datetime import date, datetime, timezone
from typing import Any, Iterable
from urllib.parse import urlsplit, urlunsplit


def _text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip())


def normalize_url(value: Any) -> str:
    raw = _text(value)
    if not raw:
        return ""
    parts = urlsplit(raw)
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), parts.path.rstrip("/"), parts.query, ""))


def normalize_title(value: Any) -> str:
    return re.sub(r"[^a-z0-9]", "", _text(value).casefold())


def stable_key(record: dict[str, Any]) -> str:
    source = _text(record.get("Source")) or "unknown"
    identifier = _text(record.get("SourceID") or record.get("ExternalID"))
    if identifier:
        basis = f"{source}:{identifier.casefold()}"
    elif normalize_url(record.get("URL")):
        basis = f"url:{normalize_url(record['URL'])}"
    else:
        basis = f"title:{normalize_title(record.get('Title'))}|funder:{normalize_title(record.get('Funder'))}"
    if record.get('RoundID'):
        basis += '|round:' + _text(record['RoundID'])
    return "GRANT:" + hashlib.sha256(basis.encode("utf-8")).hexdigest()[:24]


def _date(value: Any) -> tuple[str | None, str]:
    raw = _text(value)
    if not raw:
        return None, "unknown"
    match = re.fullmatch(r"(\d{4})(?:-(\d{2})(?:-(\d{2}))?)?", raw)
    if not match:
        return None, "unknown"
    year, month, day = match.groups()
    try:
        date(int(year), int(month or 1), int(day or 1))
    except ValueError:
        return None, 'unknown'
    if month and day:
        return f"{year}-{month}-{day}", "day"
    if month:
        return f"{year}-{month}", "month"
    return year, "year"


def normalize_opportunity(record: dict[str, Any], retrieved_at: str | None = None) -> dict[str, Any]:
    """Normalize RSS/Atom/API-shaped records without inventing missing values."""
    record = dict(record)
    record['Title'] = record.get('Title') or record.get('title') or ''
    record['URL'] = record.get('URL') or record.get('Link') or record.get('link') or ''
    record['Funder'] = record.get('Funder') or record.get('Organization') or record.get('funder') or ''
    deadline, precision = _date(record.get("Deadline") or record.get("ClosingDate") or record.get("deadline"))
    retrieved = retrieved_at or _text(record.get("RetrievedUTC")) or datetime.now(timezone.utc).isoformat()
    result = {
        "OpportunityKey": stable_key(record),
        "Title": _text(record.get("Title") or record.get("title")),
        "Funder": _text(record.get("Funder") or record.get("Organization") or record.get("funder")),
        "Source": _text(record.get("Source")) or "unknown",
        "SourceID": _text(record.get("SourceID") or record.get("ExternalID")),
        "RoundID": _text(record.get('RoundID')),
        "URL": normalize_url(record.get("URL") or record.get("Link") or record.get("link")),
        "Description": _text(record.get("Description") or record.get("Summary") or record.get("summary")),
        "Eligibility": _text(record.get("Eligibility")),
        "Geography": _text(record.get("Geography")),
        "Amount": _text(record.get("Amount")),
        "Deadline": deadline,
        "DeadlineRaw": _text(record.get("Deadline") or record.get("ClosingDate") or record.get("deadline")),
        "DeadlinePrecision": precision,
        "Status": _text(record.get("Status")) or "Unknown",
        "Contact": _text(record.get("Contact")),
        "CHHHSRelevance": _text(record.get("CHHHSRelevance")) or "Unknown",
        "ReviewStatus": _text(record.get("ReviewStatus")) or "Needs Review",
        "RetrievedUTC": retrieved,
        "EvidenceHash": hashlib.sha256(repr(sorted(record.items())).encode("utf-8")).hexdigest(),
    }
    if not result["Title"] or not result["URL"]:
        result["ReviewStatus"] = "Needs Review"
    return result


def merge_observations(records: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Merge exact stable keys while retaining source-specific observations."""
    grouped: dict[str, dict[str, Any]] = {}
    for raw in records:
        normalized = normalize_opportunity(raw, raw.get("RetrievedUTC"))
        key = normalized["OpportunityKey"]
        if key not in grouped:
            grouped[key] = {**normalized, "SourceObservations": []}
        grouped[key]["SourceObservations"].append({
            "Source": normalized["Source"], "SourceID": normalized["SourceID"],
            "URL": normalized["URL"], "RetrievedUTC": normalized["RetrievedUTC"],
            "EvidenceHash": normalized["EvidenceHash"],
            "Snapshot": dict(normalized),
        })
        if grouped[key]["Title"] == "" and normalized["Title"]:
            grouped[key]["Title"] = normalized["Title"]
    return sorted(grouped.values(), key=lambda item: (item["Deadline"] or "9999", item["Title"].casefold()))


def sharepoint_field_map(record: dict[str, Any]) -> dict[str, Any]:
    """Map the canonical record to stable display names for a future list."""
    return {field: record.get(field) for field in (
        "OpportunityKey", "Title", "Funder", "Source", "SourceID", "RoundID", "URL", "Description",
        "Eligibility", "Geography", "Amount", "Deadline", "DeadlineRaw", "DeadlinePrecision",
        "Status", "Contact", "CHHHSRelevance", "ReviewStatus", "RetrievedUTC", "EvidenceHash",
    )}
