"""Validate university source and institutional-deadline discovery records."""
from __future__ import annotations

import json
from pathlib import Path

REQUIRED_INSTITUTIONS = {"jcu", "uq", "qut", "griffith"}


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
