"""Read-only adapter for the ARC NCGP public grants JSON API.

The endpoint contains awarded/project records, not an open-opportunity
calendar. Keep its output typed as ``Award`` so it can enrich relationship
review without entering the opportunity upsert path.
"""
from __future__ import annotations

import datetime as dt
import json
import urllib.parse
import urllib.request
from typing import Any, Callable

API_BASE = "https://dataportal.arc.gov.au/NCGP/API/grants"
MAX_PAGE_SIZE = 1000


def _request_url(page_number: int, page_size: int) -> str:
    if page_number < 1 or page_size < 1 or page_size > MAX_PAGE_SIZE:
        raise ValueError("page_number must be positive and page_size must be 1..1000")
    return API_BASE + "?" + urllib.parse.urlencode(
        {"page[number]": page_number, "page[size]": page_size}
    )


def _read_json(url: str, opener: Callable[..., Any]) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        headers={"Accept": "application/json", "User-Agent": "CHHHS-RIMS-grants-arc/0.1"},
        method="GET",
    )
    with opener(request, timeout=20) as response:
        if int(response.getcode() or 0) != 200:
            raise ValueError(f"ARC API returned HTTP {response.getcode()}")
        content_type = str(response.headers.get("Content-Type", ""))
        if "json" not in content_type.casefold():
            raise ValueError("ARC API response is not JSON")
        payload = json.loads(response.read(2_000_001))
    if not isinstance(payload, dict) or not isinstance(payload.get("data"), list):
        raise ValueError("ARC API payload must contain a data list")
    return payload


def parse_award_page(payload: dict[str, Any], *, retrieved_at: str) -> list[dict[str, Any]]:
    """Convert one API page to typed award observations without opportunity promotion."""
    if not retrieved_at or dt.datetime.fromisoformat(retrieved_at.replace("Z", "+00:00")).tzinfo is None:
        raise ValueError("retrieved_at must be timezone-aware")
    records: list[dict[str, Any]] = []
    for item in payload["data"]:
        if not isinstance(item, dict):
            raise ValueError("ARC API data item must be an object")
        attrs = item.get("attributes")
        if not isinstance(attrs, dict):
            raise ValueError("ARC API item must contain attributes")
        source_id = str(attrs.get("code") or item.get("id") or "").strip()
        if not source_id:
            raise ValueError("ARC API award is missing code/id")
        link = str((item.get("links") or {}).get("self") or "").strip()
        if not link.startswith(("http://", "https://")):
            raise ValueError("ARC API award is missing an evidence URL")
        records.append({
            "RecordKind": "Award",
            "Source": "arc",
            "SourceID": source_id,
            "Title": str(attrs.get("grant-summary") or attrs.get("scheme-name") or "").strip(),
            "Funder": "Australian Research Council",
            "URL": link,
            "Description": str(attrs.get("grant-summary") or "").strip(),
            "Amount": str(attrs.get("current-funding-amount") or "").strip(),
            "Status": str(attrs.get("grant-status") or "Unknown").strip(),
            "RetrievedUTC": retrieved_at,
            "EvidenceHash": "",
        })
    return records


def fetch_award_page(*, page_number: int = 1, page_size: int = 1000,
                     retrieved_at: str | None = None,
                     opener: Callable[..., Any] = urllib.request.urlopen) -> dict[str, Any]:
    """Fetch one bounded ARC page and return typed awards plus pagination metadata."""
    observed = retrieved_at or dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    url = _request_url(page_number, page_size)
    payload = _read_json(url, opener)
    return {
        "source": "arc",
        "record_kind": "awards_only",
        "api_url": url,
        "meta": payload.get("meta", {}),
        "records": parse_award_page(payload, retrieved_at=observed),
    }


if __name__ == "__main__":
    print(json.dumps(fetch_award_page(page_size=1), indent=2))
