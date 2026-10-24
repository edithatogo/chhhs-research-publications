"""Read-only typed identity comparison for a saved Power BI query and DEV registry.

This is a crosswalk for verification, not a migration of durable PUB keys or a
review/admission decision. Detailed identities are written only when requested.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

if __package__:
    from scripts.canonical_reference import normalize_pmid
else:
    from canonical_reference import normalize_pmid


def _pmid(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = normalize_pmid(value)
    return value if normalized == value else None


def _dora(key: object) -> bool:
    return (isinstance(key, str) and key.startswith("DORA:")
            and bool(key[5:]) and key == key.strip()
            and not any(character.isspace() for character in key[5:]))


def _rows(payload: object, label: str) -> list[dict]:
    if not isinstance(payload, dict):
        raise ValueError(f"{label} payload must be an object")
    if label == "registry":
        if payload.get("complete") is not True or payload.get("next_links") != []:
            raise ValueError("complete registry export with next_links=[] required")
        rows = payload.get("rows")
    else:
        if payload.get("error") or not isinstance(payload.get("results"), list) or len(payload["results"]) != 1:
            raise ValueError("one successful model query result required")
        tables = payload["results"][0].get("tables")
        if not isinstance(tables, list) or len(tables) != 1:
            raise ValueError("one model query table required")
        rows = tables[0].get("rows")
    if not isinstance(rows, list) or not rows or not all(isinstance(row, dict) for row in rows):
        raise ValueError(f"nonempty {label} rows required")
    return rows


def compare(model_rows: list[dict], registry_rows: list[dict]) -> tuple[dict, dict]:
    """Return aggregate receipt and private differences; reject duplicate identities."""
    if not model_rows or not registry_rows:
        raise ValueError("nonempty model and registry rows required")
    model: dict[str, dict] = {}
    registry: dict[str, dict] = {}
    invalid: list[dict] = []
    blank_registry = 0
    model_provenance = {"PubMed": 0, "PubMed; DORA": 0, "DORA": 0}
    seen_sources: set[str] = set()
    seen_registry_canonical: set[str] = set()

    for index, row in enumerate(model_rows):
        key, pmid = row.get("[CanonicalKey]"), row.get("[PMID]")
        source_set, dora_url = row.get("[SourceSet]"), row.get("[DORAURL]")
        if isinstance(key, str) and key.startswith("PMID:"):
            if _pmid(pmid) is None or key != f"PMID:{pmid}":
                invalid.append({"side": "model", "index": index, "reason": "malformed PMID identity", "row": row})
                continue
            if not ((source_set == "PubMed" and dora_url in (None, ""))
                    or (source_set == "PubMed; DORA" and isinstance(dora_url, str) and bool(dora_url.strip()))):
                invalid.append({"side": "model", "index": index, "reason": "PubMed source provenance mismatch", "row": row})
                continue
            typed = key
        elif _dora(key):
            if pmid not in (None, "") and _pmid(pmid) is None:
                invalid.append({"side": "model", "index": index, "reason": "invalid DORA PMID", "row": row})
                continue
            if source_set != "DORA" or not isinstance(dora_url, str) or not dora_url.strip():
                invalid.append({"side": "model", "index": index, "reason": "DORA source provenance mismatch", "row": row})
                continue
            typed = key
        else:
            invalid.append({"side": "model", "index": index, "reason": "malformed canonical key", "row": row})
            continue
        if typed in model:
            raise ValueError("duplicate model typed identity")
        model[typed] = row
        model_provenance[source_set] += 1

    for index, row in enumerate(registry_rows):
        source, key, pmid = row.get("SourceKey"), row.get("CanonicalKey"), row.get("PMID")
        if source in (None, ""):
            blank_registry += 1
            continue
        if not isinstance(source, str) or source != source.strip():
            invalid.append({"side": "registry", "index": index, "reason": "malformed SourceKey", "row": row})
            continue
        if source in seen_sources:
            raise ValueError("duplicate registry SourceKey")
        seen_sources.add(source)
        if isinstance(key, str):
            if key in seen_registry_canonical:
                raise ValueError("duplicate registry CanonicalKey")
            seen_registry_canonical.add(key)
        if isinstance(key, str) and key.startswith(("PUB:", "PMID:")):
            if not isinstance(key, str) or not key.split(":", 1)[1] or key != key.strip():
                reason = "malformed PUB/PMID canonical key"
            elif _pmid(pmid) is None or source != f"pubmed:{pmid}" or (key.startswith("PMID:") and key != f"PMID:{pmid}"):
                reason = "invalid PubMed source or positive PMID"
            else:
                reason = None
            if reason:
                invalid.append({"side": "registry", "index": index, "reason": reason, "row": row})
                continue
            typed = f"PMID:{pmid}"
        elif _dora(key):
            valid_pmid = pmid in (None, "") or _pmid(pmid) is not None
            valid_source = ((source.startswith("dora:") and bool(source[5:]))
                            or (_pmid(pmid) is not None and source == f"pubmed:{pmid}"))
            if not valid_source or not valid_pmid:
                invalid.append({"side": "registry", "index": index, "reason": "invalid source or PMID for DORA canonical key", "row": row})
                continue
            typed = key
        else:
            invalid.append({"side": "registry", "index": index, "reason": "malformed canonical key", "row": row})
            continue
        if typed in registry:
            raise ValueError("duplicate registry typed identity")
        registry[typed] = row

    model_only = sorted(model.keys() - registry.keys())
    registry_only = sorted(registry.keys() - model.keys())
    matched = model.keys() & registry.keys()
    exact_canonical = sum(
        model[typed].get("[CanonicalKey]") == registry[typed].get("CanonicalKey")
        for typed in matched
    )
    counts = {
        "model_rows": len(model_rows), "registry_rows": len(registry_rows),
        "registry_blank_sourcekey_rows": blank_registry,
        "model_valid_typed_rows": len(model), "registry_valid_typed_rows": len(registry),
        "model_invalid_rows": sum(item["side"] == "model" for item in invalid),
        "model_pubmed_only_rows": model_provenance["PubMed"],
        "model_pubmed_dora_rows": model_provenance["PubMed; DORA"],
        "model_dora_rows": model_provenance["DORA"],
        "registry_invalid_rows": sum(item["side"] == "registry" for item in invalid),
        "matched_typed_identities": len(model.keys() & registry.keys()),
        "matched_exact_canonical_keys": exact_canonical,
        "matched_different_canonical_representations": len(matched) - exact_canonical,
        "model_only_typed_identities": len(model_only),
        "registry_only_typed_identities": len(registry_only),
    }
    receipt = {
        "kind": "publication_model_registry_typed_identity_check_v1",
        "status": "PASS" if not invalid and not model_only and not registry_only else "FAIL",
        "counts": counts,
        "interpretation": "Read-only typed key and model-side SourceSet/DORAURL comparison; registry export has no SourceSet field. Exact canonical-key representation is reported separately. This is neither review admission nor tenant refresh acceptance",
    }
    differences = {
        "model_only": [{"TypedIdentity": key, "row": model[key]} for key in model_only],
        "registry_only": [{"TypedIdentity": key, "row": registry[key]} for key in registry_only],
        "invalid": invalid,
    }
    return receipt, differences


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True, type=Path, help="Saved executeQueries JSON")
    parser.add_argument("--registry", required=True, type=Path, help="Complete registry export JSON")
    parser.add_argument("--output", type=Path, help="Aggregate JSON receipt; stdout if omitted")
    parser.add_argument("--differences", type=Path, help="Optional private detailed rows")
    args = parser.parse_args()
    inputs = {args.model.resolve(), args.registry.resolve()}
    if args.output and args.output.resolve() in inputs:
        parser.error("aggregate receipt must not overwrite an input")
    if args.differences:
        destination = args.differences.resolve()
        private_root = (Path(__file__).resolve().parent.parent / "private").resolve()
        if not destination.is_relative_to(private_root):
            parser.error("detailed rows must remain under this repository's ignored private/ path")
        if destination in inputs or (args.output and destination == args.output.resolve()):
            parser.error("detailed rows need a separate output path")
    model_bytes, registry_bytes = args.model.read_bytes(), args.registry.read_bytes()
    model = _rows(json.loads(model_bytes), "model")
    registry = _rows(json.loads(registry_bytes), "registry")
    receipt, differences = compare(model, registry)
    receipt["inputs"] = {
        "model_sha256": hashlib.sha256(model_bytes).hexdigest(),
        "registry_sha256": hashlib.sha256(registry_bytes).hexdigest(),
    }
    rendered = json.dumps(receipt, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    if args.differences:
        args.differences.write_text(json.dumps(differences, indent=2) + "\n", encoding="utf-8")
    return 0 if receipt["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
