"""Compare complete registry primary-source readback with saved model provenance.

This is read-only. Registry SourceSet is the item's primary classification;
model SourceSet may contain derived cross-source membership. An extra model
member is evidence for review, not proof that the registry admitted it.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


SOURCES = {"PubMed", "DORA"}
MODEL_SETS = {"PubMed", "DORA", "PubMed; DORA"}


def _text(value: object) -> str:
    return value.strip() if isinstance(value, str) else ""


def _identity(row: dict, *, model: bool) -> str | None:
    canonical_value = row.get("[CanonicalKey]" if model else "CanonicalKey")
    pmid_value = row.get("[PMID]" if model else "PMID")
    source_value = row.get("SourceKey") if not model else ""
    if (not all(isinstance(value, str) for value in (canonical_value, source_value))
            or not isinstance(pmid_value, (str, type(None)))):
        return None
    canonical, pmid, source = _text(canonical_value), _text(pmid_value), _text(source_value)
    if model:
        if canonical.startswith("PMID:") and canonical[5:].isdigit() and int(canonical[5:]) > 0 and pmid == canonical[5:]:
            return canonical
        if canonical.startswith("DORA:") and canonical[5:]:
            return canonical
        return None
    if canonical.startswith("DORA:") and canonical[5:] and (
        source.startswith("dora:") or (pmid.isdigit() and int(pmid) > 0 and source == f"pubmed:{pmid}")
    ):
        return canonical
    if source.startswith("pubmed:") and pmid.isdigit() and int(pmid) > 0 and source == f"pubmed:{pmid}":
        return f"PMID:{pmid}"
    return None


def _model_rows(payload: object) -> list[dict]:
    if not isinstance(payload, dict) or payload.get("error") or not isinstance(payload.get("results"), list) or len(payload["results"]) != 1:
        raise ValueError("one successful model query result required")
    tables = payload["results"][0].get("tables")
    if not isinstance(tables, list) or len(tables) != 1 or not isinstance(tables[0].get("rows"), list):
        raise ValueError("one model query table required")
    rows = tables[0]["rows"]
    if not rows or any(not isinstance(row, dict) or not {"[CanonicalKey]", "[PMID]", "[SourceSet]", "[DORAURL]"} <= row.keys() for row in rows):
        raise ValueError("nonempty complete model provenance projection required")
    return rows


def _registry_rows(payload: object) -> list[dict]:
    if not isinstance(payload, dict) or payload.get("complete") is not True:
        raise ValueError("complete registry keyed-row readback required")
    rows, total, keyed_total = payload.get("keyed_rows"), payload.get("total_rows"), payload.get("keyed_total")
    if (not isinstance(total, int) or isinstance(total, bool) or total <= 0
            or not isinstance(keyed_total, int) or isinstance(keyed_total, bool)
            or not isinstance(rows, list) or not rows or len(rows) != keyed_total or len(rows) > total):
        raise ValueError("valid registry total and nonempty keyed rows required")
    fields = {"Id", "SourceKey", "CanonicalKey", "SourceSet", "PMID", "DORAURL", "ReviewStatus"}
    if any(not isinstance(row, dict) or not fields <= row.keys() for row in rows):
        raise ValueError("registry keyed-row projection missing required fields")
    return rows


def compare(registry_rows: list[dict], model_rows: list[dict]) -> tuple[dict, dict]:
    registry: dict[str, dict] = {}
    model: dict[str, dict] = {}
    invalid: list[dict] = []
    for side, rows, index in (("registry", registry_rows, registry), ("model", model_rows, model)):
        seen_raw: set[str] = set()
        seen_folded: set[str] = set()
        seen_registry_canonical: set[str] = set()
        for row_number, row in enumerate(rows):
            if side == "registry" and (type(row.get("Id")) is not int or row["Id"] <= 0):
                invalid.append({"side": side, "row_number": row_number,
                                "reason": "registry item Id must be a positive integer",
                                "raw_key": _text(row.get("SourceKey"))})
                continue
            if side == "registry" and not isinstance(row.get("ReviewStatus"), (str, type(None))):
                invalid.append({"side": side, "row_number": row_number,
                                "reason": "registry review status must be text",
                                "raw_key": _text(row.get("SourceKey"))})
                continue
            raw_value = row.get("SourceKey" if side == "registry" else "[CanonicalKey]")
            raw = _text(raw_value)
            if not isinstance(raw_value, str):
                invalid.append({"side": side, "row_number": row_number,
                                "reason": "source/canonical key must be text", "raw_key": None})
                continue
            folded = raw.casefold()
            if not raw or raw in seen_raw or folded in seen_folded:
                raise ValueError(f"blank or case-insensitive duplicate {side} source/canonical key")
            seen_raw.add(raw)
            seen_folded.add(folded)
            if side == "registry":
                canonical_value = row.get("CanonicalKey")
                if not isinstance(canonical_value, str):
                    invalid.append({"side": side, "row_number": row_number,
                                    "reason": "canonical key must be text", "raw_key": raw})
                    continue
                canonical = _text(canonical_value)
                canonical_folded = canonical.casefold()
                if canonical and canonical_folded in seen_registry_canonical:
                    raise ValueError("case-insensitive duplicate registry CanonicalKey")
                if canonical:
                    seen_registry_canonical.add(canonical_folded)
            typed = _identity(row, model=side == "model")
            source_set = row.get("SourceSet" if side == "registry" else "[SourceSet]")
            pmid = row.get("PMID" if side == "registry" else "[PMID]")
            if not isinstance(pmid, (str, type(None))):
                typed = None
            if not isinstance(source_set, str):
                typed = None
            if side == "model" and row.get("[DORAURL]") is not None and not isinstance(row.get("[DORAURL]"), str):
                typed = None
            if side == "registry" and row.get("DORAURL") is not None and not isinstance(row.get("DORAURL"), str):
                typed = None
            allowed = SOURCES if side == "registry" else MODEL_SETS
            if not typed or source_set not in allowed:
                invalid.append({"side": side, "row_number": row_number, "reason": "invalid typed identity or source classification", "raw_key": raw})
                continue
            if typed in index:
                raise ValueError(f"duplicate {side} typed identity")
            index[typed] = row

    model_only = sorted(model.keys() - registry.keys())
    registry_only = sorted(registry.keys() - model.keys())
    primary_missing: list[str] = []
    additional: list[dict] = []
    exact: list[str] = []
    for key in sorted(registry.keys() & model.keys()):
        primary = registry[key]["SourceSet"]
        model_set = model[key]["[SourceSet]"]
        members = set(model_set.split("; "))
        if primary not in members:
            primary_missing.append(key)
        elif len(members) > 1:
            additional.append({"typed_identity": key, "registry_primary": primary, "model_membership": model_set,
                               "registry_dora_url_present": bool(_text(registry[key]["DORAURL"])),
                               "model_dora_url_present": bool(_text(model[key]["[DORAURL]"]))})
        else:
            exact.append(key)

    counts = {"registry_keyed_rows": len(registry_rows), "model_rows": len(model_rows),
              "registry_invalid": sum(x["side"] == "registry" for x in invalid),
              "model_invalid": sum(x["side"] == "model" for x in invalid),
              "matched_typed": len(registry.keys() & model.keys()), "registry_only": len(registry_only),
              "model_only": len(model_only), "matched_primary_missing_from_model": len(primary_missing),
              "matched_exact_source_classification": len(exact),
              "matched_model_additional_membership": len(additional)}
    receipt = {"kind": "publication_registry_model_provenance_comparison_v1",
               "status": "PASS_KEYED_PRIMARY_COVERAGE" if not invalid and not model_only and not registry_only and not primary_missing else "REVIEW_REQUIRED",
               "counts": counts,
               "interpretation": "Registry SourceSet is primary classification; model SourceSet may be derived co-membership. Additional model membership is review evidence, not registry admission or refresh acceptance."}
    detail = {"invalid": invalid, "registry_only": registry_only, "model_only": model_only,
              "primary_missing_from_model": primary_missing, "model_additional_membership": additional}
    return receipt, detail


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", required=True, type=Path)
    parser.add_argument("--model", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--details", type=Path)
    args = parser.parse_args()
    inputs = {args.registry.resolve(), args.model.resolve()}
    for target in (args.output, args.details):
        if target and target.resolve() in inputs:
            parser.error("output must not overwrite an input")
    if args.details:
        private_root = (Path(__file__).resolve().parent.parent / "private").resolve()
        if not args.details.resolve().is_relative_to(private_root):
            parser.error("detailed identities must remain under ignored private/")
    registry_bytes, model_bytes = args.registry.read_bytes(), args.model.read_bytes()
    registry = json.loads(registry_bytes)
    model = json.loads(model_bytes)
    receipt, detail = compare(_registry_rows(registry), _model_rows(model))
    receipt["inputs"] = {"registry_sha256": hashlib.sha256(registry_bytes).hexdigest(),
                         "model_sha256": hashlib.sha256(model_bytes).hexdigest(),
                         "registry_total_rows": registry["total_rows"]}
    output = json.dumps(receipt, indent=2) + "\n"
    if args.output:
        args.output.write_text(output, encoding="utf-8")
    else:
        print(output, end="")
    if args.details:
        args.details.write_text(json.dumps(detail, indent=2) + "\n", encoding="utf-8")
    return 0 if receipt["status"] == "PASS_KEYED_PRIMARY_COVERAGE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
