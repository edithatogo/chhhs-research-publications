"""Read official RSS/Atom/API endpoints and record bounded probe evidence.

This module deliberately does not fetch or parse authority landing pages. A
successful probe proves only that the configured endpoint returned unique,
identifiable records; it never admits a source to opportunity intake.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlsplit

try:
    from scripts.grants_source_identity import feed_source_ids, json_source_ids
    from scripts.grants_sources import load_catalogue, source_request_contract, NIH_SELECTED_SOURCE
except ImportError:
    from grants_source_identity import feed_source_ids, json_source_ids
    from grants_sources import load_catalogue, source_request_contract, NIH_SELECTED_SOURCE

# Match the existing QGIP adapter's bounded CKAN page limit. The configured
# page contains up to 100 records and can exceed 128 KiB; keep a hard ceiling
# so a valid large page is not misclassified and unbounded bodies are rejected.
MAX_BYTES = 2_000_000
USER_AGENT = "CHHHS-RIMS-grants-endpoint-readback/0.2"
REPO_ROOT = Path(__file__).resolve().parents[1]
PRIVATE_OPS_ROOT = REPO_ROOT / "private" / "ops"


def _endpoint(row: dict[str, Any]) -> str:
    return row["api_url"] if row["intake"] == "api" else row["feed_url"]


# Keep the historical private helper names while sharing the exact path logic
# with ingestion, so probing and parsing cannot diverge.
_path_value = json_source_ids
_xml_path_value = feed_source_ids


def _is_json_media_type(value: str) -> bool:
    """Accept JSON media types, not an incidental ``json`` substring."""
    media_type = value.split(";", 1)[0].strip().casefold()
    top_level, separator, subtype = media_type.partition("/")
    return bool(separator and top_level == "application"
                and (subtype == "json" or subtype.endswith("+json")))


def _probe_row(row: dict[str, Any], opener: Callable[..., Any]) -> dict[str, Any]:
    url = _endpoint(row)
    method, request_body = source_request_contract(row)
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json, application/rss+xml, application/atom+xml"}
    body = None
    if request_body is not None:
        headers["Content-Type"] = "application/json"
        body = json.dumps(request_body).encode("utf-8")
    request = urllib.request.Request(url, headers=headers, data=body, method=method)
    observed_at = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    result: dict[str, Any] = {"source_id": row["source_id"], "endpoint_url": url, "observed_at": observed_at, "probe_kind": "machine_endpoint_bounded_" + method.lower()}
    try:
        with opener(request, timeout=15) as response:
            final_url = response.geturl()
            requested = urlsplit(url)
            final = urlsplit(final_url)
            # urllib follows redirects automatically. A successful response
            # from a different host is not evidence for the catalogue's
            # official machine endpoint: it could be a login/error page or an
            # unrelated payload with coincidentally matching keys. Keep this
            # adapter fail-closed rather than maintaining a guessed redirect
            # allowlist.
            if (final.scheme.casefold() != "https"
                    or not final.hostname
                    or final.hostname.casefold() != (requested.hostname or "").casefold()
                    or final.username or final.password or final.port is not None):
                raise ValueError("endpoint_redirected_outside_official_host")
            # urllib normally raises for HTTP errors, but custom openers and
            # proxies can return an error response as a normal context manager.
            # Its body may still contain a matching key, which is not a
            # successful source observation.
            status = int(response.getcode() or 0)
            if not 200 <= status < 300:
                result.update({"status": status, "error": "endpoint_http_status_not_success",
                               "reconciled": False})
                return result
            content_type = str(response.headers.get("Content-Type", ""))
            if row["intake"] == "api" and not _is_json_media_type(content_type):
                raise ValueError("endpoint API response is not JSON")
            body = response.read(MAX_BYTES + 1)
            if len(body) > MAX_BYTES:
                raise ValueError("endpoint response exceeds bounded readback")
            if row["intake"] == "api":
                payload = json.loads(body)
                identifiers = json_source_ids(payload, row["reconciliation"]["source_id_path"])
                if row["source_id"] == NIH_SELECTED_SOURCE:
                    data = payload.get("data") if isinstance(payload, dict) else None
                    params = data.get("searchParams") if isinstance(data, dict) else None
                    hits = data.get("oppHits") if isinstance(data, dict) else None
                    if (not isinstance(payload, dict)
                            or type(payload.get("errorcode")) is not int or payload["errorcode"] != 0
                            or not isinstance(params, dict) or params.get("oppNum") != "PA-25-301"
                            or set(str(params.get("oppStatuses", "")).split("|"))
                            != {"forecasted", "posted", "closed", "archived"}
                            or type(data.get("hitCount")) is not int or data["hitCount"] != 1
                            or type(data.get("startRecord")) is not int or data["startRecord"] != 0
                            or identifiers != ["357812"] or not isinstance(hits, list)
                            or len(hits) != 1 or hits[0].get("number") != "PA-25-301"
                            or hits[0].get("oppStatus") != "posted"):
                        raise ValueError("selected_nih_query_or_lifecycle_drift")
            else:
                identifiers = feed_source_ids(body, row["reconciliation"]["source_id_path"], intake=row["intake"])
            if not identifiers:
                raise ValueError("endpoint response lacks configured reconciliation identity")
            # A present key is not enough for reconciliation when a response
            # repeats it: downstream upserts would otherwise collapse distinct
            # records or make the winner depend on page order.
            seen: set[str] = set()
            duplicate_keys: set[str] = set()
            for key in identifiers:
                if key in seen:
                    duplicate_keys.add(key)
                seen.add(key)
            duplicates = sorted(duplicate_keys)
            if duplicates:
                result.update({
                    "status": int(response.getcode() or 0),
                    "content_type": content_type,
                    "final_url": final_url,
                    "bytes_read": len(body),
                    "body_sha256": hashlib.sha256(body).hexdigest(),
                    "reconciliation_ids": identifiers,
                    "reconciliation_count": len(identifiers),
                    "duplicate_reconciliation_ids": duplicates,
                    "error": "duplicate_reconciliation_identity",
                    "reconciled": False,
                })
                return result
            result.update({"status": int(response.getcode() or 0), "content_type": content_type, "final_url": final_url, "bytes_read": len(body), "body_sha256": hashlib.sha256(body).hexdigest(), "reconciliation_ids": identifiers, "reconciliation_count": len(identifiers), "reconciled": True})
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError, ValueError, json.JSONDecodeError, ET.ParseError) as exc:
        retry_after = None
        response_date = None
        if isinstance(exc, urllib.error.HTTPError):
            retry_after = exc.headers.get("Retry-After") if exc.headers else None
            response_date = exc.headers.get("Date") if exc.headers else None
            exc.close()
        result.update({"status": getattr(exc, "code", None), "error": "endpoint_readback_failed", "reason": str(exc), "retry_after": retry_after, "response_date": response_date, "reconciled": False})
    return result


def collect_private_probe_evidence(
    path: str | Path, opener: Callable[..., Any] = urllib.request.urlopen,
) -> dict[str, Any]:
    """Collect the full response evidence for storage under ignored private/."""
    rows = load_catalogue(path)
    results = []
    for row in rows:
        if row["enabled"]:
            results.append(_probe_row(row, opener))
        else:
            results.append({"source_id": row["source_id"], "endpoint_url": _endpoint(row),
                            "observed_at": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
                            "probe_kind": "machine_endpoint_bounded_get", "status": "skipped",
                            "error": "source_disabled", "reconciled": False})
    enabled_results = [result for row, result in zip(rows, results) if row["enabled"]]
    probe_complete = bool(enabled_results) and all(row["reconciled"] for row in enabled_results)
    return {
        "status": "observed",
        "observed_at": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "catalogue": str(path),
        "max_bytes": MAX_BYTES,
        "results": results,
        "endpoint_probe_complete": probe_complete,
        "enabled_source_count": len(enabled_results),
        "disabled_source_ids": [row["source_id"] for row in rows if not row["enabled"]],
        # A bounded first-page/identity probe cannot prove full pagination,
        # lifecycle, or canonical opportunity reconciliation.
        "opportunity_intake_accepted": False,
        "admitted_opportunity_sources": [],
    }


def public_probe_summary(payload: dict[str, Any]) -> dict[str, Any]:
    """Return classification-only output, omitting response-level identities and details."""
    safe_fields = (
        "source_id", "observed_at", "probe_kind", "status", "content_type",
        "bytes_read", "body_sha256", "reconciliation_count", "reconciled", "error",
    )
    results = []
    for row in payload["results"]:
        results.append({key: row[key] for key in safe_fields if key in row})
    return {
        "status": payload["status"],
        "observed_at": payload["observed_at"],
        "catalogue_source_count": len(payload["results"]),
        "max_bytes": payload["max_bytes"],
        "results": results,
        "endpoint_probe_complete": payload["endpoint_probe_complete"],
        "enabled_source_count": payload["enabled_source_count"],
        "disabled_source_ids": payload["disabled_source_ids"],
        "opportunity_intake_accepted": False,
        "admitted_opportunity_sources": [],
        "raw_response_identities_omitted": True,
    }


def probe_catalogue(path: str | Path, opener: Callable[..., Any] = urllib.request.urlopen) -> dict[str, Any]:
    """Probe configured endpoints and return classification-only results."""
    return public_probe_summary(collect_private_probe_evidence(path, opener))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("catalogue", type=Path)
    parser.add_argument(
        "--out", type=Path,
        help="save full raw probe evidence under this repository's ignored private/ops directory",
    )
    args = parser.parse_args()
    destination = None
    if args.out:
        destination = args.out.resolve()
        try:
            destination.relative_to(PRIVATE_OPS_ROOT.resolve())
        except ValueError:
            parser.error("--out must be inside the repository's ignored private/ops directory")
    payload = collect_private_probe_evidence(args.catalogue)
    if destination:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(public_probe_summary(payload), indent=2))


if __name__ == "__main__":
    main()
