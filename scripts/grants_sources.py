"""Validate the reviewed, source-only grants catalogue.

The catalogue records proposed intake routes and evidence state. It never
claims that a page is a working feed merely because an official URL exists.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REQUIRED_SOURCE_IDS = {
    "nhmrc", "mrff", "arc", "queensland-health", "emf-queensland",
    "advance-queensland", "fnqhf",
}
ALLOWED_INTAKE = {"rss", "atom", "api", "reviewed_import", "manual_review"}
ALLOWED_HEALTH = {"unverified", "research_only", "reviewed_import", "verified_sample"}


def load_catalogue(path: str | Path) -> list[dict[str, Any]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("grants source catalogue must be a list")
    seen: set[str] = set()
    for row in payload:
        if not isinstance(row, dict):
            raise ValueError("each source catalogue row must be an object")
        source_id = str(row.get("source_id", "")).strip()
        if not source_id or source_id in seen:
            raise ValueError(f"duplicate or missing source_id: {source_id!r}")
        seen.add(source_id)
        if not row.get("authority_url") or not row.get("title"):
            raise ValueError(f"source {source_id!r} needs title and authority_url")
        if row.get("intake") not in ALLOWED_INTAKE:
            raise ValueError(f"source {source_id!r} has unsupported intake")
        if row.get("health_status") not in ALLOWED_HEALTH:
            raise ValueError(f"source {source_id!r} has unsupported health_status")
        if not isinstance(row.get("eligibility_scope"), str):
            raise ValueError(f"source {source_id!r} needs eligibility_scope")
    missing = REQUIRED_SOURCE_IDS - seen
    if missing:
        raise ValueError(f"required sources missing: {sorted(missing)}")
    return payload


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("catalogue", type=Path)
    args = parser.parse_args()
    rows = load_catalogue(args.catalogue)
    print(f"validated {len(rows)} grant source catalogue rows")
