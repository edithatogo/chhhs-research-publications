"""Validate university source and institutional-deadline discovery records."""
from __future__ import annotations

import json
from pathlib import Path

REQUIRED_INSTITUTIONS = {"jcu", "uq", "qut", "griffith"}


def _validate_lead_time(value, key):
    if value is None:
        return
    if not isinstance(value, dict):
        raise ValueError(f"institution {key!r} internal_lead_time must be an object or null")
    if value.get("unit") not in {"business_days", "working_days", "calendar_days"}:
        raise ValueError(f"institution {key!r} has unsupported lead-time unit")
    numeric_values = [item for name, item in value.items() if name != "unit" and isinstance(item, (int, float))]
    if not numeric_values:
        raise ValueError(f"institution {key!r} needs a numeric lead-time value")
    if any(type(item) not in {int, float} or item < 0 or item > 3660 for item in numeric_values):
        raise ValueError(f"institution {key!r} has an invalid lead-time value")


def load_universities(path):
    rows = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(rows, list):
        raise ValueError("university catalogue must be a list")
    seen = set()
    for row in rows:
        key = str(row.get("institution_id", "")).strip()
        if not key or key in seen:
            raise ValueError(f"duplicate or missing institution_id: {key!r}")
        seen.add(key)
        for field in ("name", "authority_url", "access", "format", "intake", "eligibility_scope", "policy_note", "last_verified"):
            if not isinstance(row.get(field), str) or not row[field].strip():
                raise ValueError(f"institution {key!r} needs {field}")
        _validate_lead_time(row.get("internal_lead_time"), key)
        if row["intake"] != "manual_review":
            raise ValueError(f"institution {key!r} must remain manual_review until access is proven")
    missing = REQUIRED_INSTITUTIONS - seen
    if missing:
        raise ValueError(f"required universities missing: {sorted(missing)}")
    return rows


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("catalogue", type=Path)
    args = parser.parse_args()
    print(f"validated {len(load_universities(args.catalogue))} university rows")
