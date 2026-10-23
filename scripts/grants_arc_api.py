"""Read-only adapter for the ARC NCGP public grants JSON API.

The endpoint contains awarded/project records, not an open-opportunity
calendar. Keep its output typed as ``Award`` so it can enrich relationship
review without entering the opportunity upsert path.
"""
from __future__ import annotations

import datetime as dt
import base64
from email.utils import parsedate_to_datetime
import hashlib
import json
import math
import os
import urllib.parse
import urllib.error
import urllib.request
from typing import Any, Callable
from pathlib import Path

try:
    from scripts.grants_sources import DEFAULT_CATALOGUE, require_enabled_source
except ImportError:
    from grants_sources import DEFAULT_CATALOGUE, require_enabled_source

API_BASE = "https://dataportal.arc.gov.au/NCGP/API/grants"
MAX_PAGE_SIZE = 1000
# At 500 records, the observed 34,960-award source needs 70 pages. Keep
# headroom for source growth and smaller safe page sizes; byte-limit every page.
MAX_PAGES = 1000
MAX_TOTAL_AWARDS = 50_000
MAX_RESPONSE_BYTES = 2_000_000
# Bound the combined original response bodies retained across both snapshot
# passes. Per-page limits alone allow a 1,000-page replay to retain several GB.
MAX_TOTAL_RESPONSE_BYTES = 256_000_000
API_HOST = "dataportal.arc.gov.au"
PRIVATE_OPS_ROOT = Path(__file__).parents[1] / "private" / "ops"


class ARCAPIHTTPError(ValueError):
    """Sanitized HTTP failure evidence for the read-only ARC adapter.

    Keep only the response status and the two operational headers used to
    decide when a caller may safely try again. The adapter itself never retries.
    """

    def __init__(self, status: int, headers: Any = None):
        self.status = status
        retry_after = _safe_http_date_or_delta(headers, "Retry-After", allow_delta=True)
        response_date = _safe_http_date_or_delta(headers, "Date", allow_delta=False)
        self.metadata = {"status": status}
        if retry_after is not None:
            self.metadata["retry_after"] = retry_after
        if response_date is not None:
            self.metadata["date"] = response_date
        super().__init__(f"ARC API returned HTTP {status}")


class ARCPageValidationError(ValueError):
    """Safe stage metadata for a malformed bounded sample response."""

    def __init__(self, stage: str):
        if stage not in {"response_validation", "award_record_validation"}:
            raise ValueError("invalid ARC page validation stage")
        self.metadata = {"stage": stage, "failure_class": "ValueError"}
        super().__init__("ARC page validation failed")


class ARCSnapshotFetchError(ValueError):
    """Safe request-failure location for an incomplete full-snapshot attempt.

    Never retain the request URL, response body, or any accumulated award rows.
    The adapter does not retry; this metadata helps plan a later bounded run.
    """

    def __init__(self, *, pass_number: int, page_number: int,
                 completed_pages: int, total_pages: int,
                 failure_kind: str, http_metadata: dict[str, str | int] | None = None):
        self.metadata: dict[str, Any] = {
            "pass_number": pass_number,
            "page_number": page_number,
            "completed_pages_in_pass": completed_pages,
            "declared_total_pages": total_pages,
            "failure_kind": failure_kind,
        }
        if http_metadata is not None:
            self.metadata["http"] = dict(http_metadata)
        super().__init__(
            f"ARC snapshot request failed on pass {pass_number}, page {page_number}"
        )


def _safe_http_date_or_delta(headers: Any, name: str, *, allow_delta: bool) -> str | None:
    """Return a short, syntactically valid HTTP date or Retry-After value."""
    if headers is None:
        return None
    try:
        value = headers.get(name)
    except Exception:
        return None
    if not isinstance(value, str):
        return None
    value = value.strip()
    if not value or len(value) > 128 or any(ord(character) < 32 or ord(character) > 126
                                             for character in value):
        return None
    if allow_delta and value.isascii() and value.isdigit():
        return value
    try:
        parsedate_to_datetime(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return value


def _validated_self_link(value: Any, source_ids: set[str]) -> str:
    """Require the official ARC record endpoint to identify this record."""
    if not isinstance(value, str) or not value or value != value.strip():
        raise ValueError("ARC award self-link must be unpadded text")
    raw = value
    try:
        parsed = urllib.parse.urlsplit(raw)
        path = urllib.parse.unquote(parsed.path)
        prefix = "/NCGP/API/grants/"
        linked_id = path[len(prefix):] if path.startswith(prefix) else ""
        segments = linked_id.split("/")
        safe_segments = all(segment not in {"", ".", ".."}
                            and "\\" not in segment
                            and all(ord(character) >= 32 and ord(character) != 127
                                    for character in segment)
                            for segment in segments)
        valid = (
            parsed.scheme.casefold() in {"http", "https"}
            and parsed.hostname == API_HOST
            and parsed.port is None
            and parsed.username is None
            and parsed.password is None
            and not parsed.query
            and not parsed.fragment
            and linked_id in source_ids
            and safe_segments
        )
    except ValueError:
        valid = False
    if not valid:
        raise ValueError("ARC award self-link must identify this record on the official API host")
    # The official JSON API currently emits an HTTP self-link even when the
    # page is fetched over HTTPS. Validate its exact host and identity above,
    # then expose only the HTTPS form to consumers.
    return urllib.parse.urlunsplit(("https", API_HOST, parsed.path, "", ""))


def _request_url(page_number: int, page_size: int) -> str:
    if (type(page_number) is not int or type(page_size) is not int
            or page_number < 1 or page_size < 1 or page_size > MAX_PAGE_SIZE):
        raise ValueError("page_number must be positive and page_size must be 1..1000")
    return API_BASE + "?" + urllib.parse.urlencode(
        {"page[number]": page_number, "page[size]": page_size}
    )


def _read_json(url: str, opener: Callable[..., Any], *,
               retained_responses: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        headers={"Accept": "application/json", "User-Agent": "CHHHS-RIMS-grants-arc/0.1"},
        method="GET",
    )
    transport_failure: tuple[int, Any] | None = None
    try:
        response_context = opener(request, timeout=20)
    except urllib.error.HTTPError as exc:
        # HTTPError is raised by urllib before a response context is returned.
        # Preserve only bounded status/Retry-After/Date evidence and suppress
        # the original exception, which includes the request URL and body.
        status = exc.code if type(exc.code) is int and 100 <= exc.code <= 599 else 0
        headers = exc.headers
        exc.close()
        transport_failure = (status, headers)
    if transport_failure is not None:
        # Raise after leaving the except block so the raw HTTPError is not
        # retained as a chained/context exception.
        raise ARCAPIHTTPError(*transport_failure)
    with response_context as response:
        status = int(response.getcode() or 0)
        if status != 200:
            raise ARCAPIHTTPError(status, response.headers)
        content_type = str(response.headers.get("Content-Type", ""))
        if "json" not in content_type.casefold():
            raise ValueError("ARC API response is not JSON")
        raw = response.read(MAX_RESPONSE_BYTES + 1)
    if len(raw) > MAX_RESPONSE_BYTES:
        raise ValueError("ARC API response exceeds byte limit")
    payload = json.loads(raw)
    if not isinstance(payload, dict) or not isinstance(payload.get("data"), list):
        raise ValueError("ARC API payload must contain a data list")
    if retained_responses is not None:
        # Keep complete successful source bytes before selecting award fields.
        # Unknown attributes, relationships, links and metadata remain recoverable.
        retained_total = sum(
            item.get("bytes", 0) for item in retained_responses
            if isinstance(item, dict) and type(item.get("bytes")) is int
        )
        if retained_total + len(raw) > MAX_TOTAL_RESPONSE_BYTES:
            raise ValueError("ARC raw source capture exceeds aggregate byte limit")
        retained_responses.append({
            "request_url": url, "status": status, "content_type": content_type,
            "captured_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
            "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
            "body_base64": base64.b64encode(raw).decode("ascii"),
            "fidelity": "original_successful_HTTP_response_body_bytes",
        })
    return payload


def parse_award_page(payload: dict[str, Any], *, retrieved_at: str) -> list[dict[str, Any]]:
    """Convert one API page to typed award observations without opportunity promotion."""
    if not isinstance(retrieved_at, str) or not retrieved_at.strip():
        raise ValueError("retrieved_at must be timezone-aware")
    try:
        observed_at = dt.datetime.fromisoformat(retrieved_at.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("retrieved_at must be timezone-aware") from exc
    if observed_at.tzinfo is None or observed_at.utcoffset() is None:
        raise ValueError("retrieved_at must be timezone-aware")
    if not isinstance(payload, dict) or not isinstance(payload.get("data"), list):
        raise ValueError("ARC API payload must contain a data list")
    records: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for item in payload["data"]:
        if not isinstance(item, dict):
            raise ValueError("ARC API data item must be an object")
        attrs = item.get("attributes")
        if not isinstance(attrs, dict):
            raise ValueError("ARC API item must contain attributes")
        item_id = item.get("id")
        if not isinstance(item_id, str) or not item_id.strip() or item_id != item_id.strip():
            raise ValueError("ARC API award data[].id must be nonblank unpadded text")
        source_id = item_id
        if source_id in seen_ids:
            raise ValueError("ARC API page contains duplicate data[].id")
        seen_ids.add(source_id)
        code_value = attrs.get("code")
        if (not isinstance(code_value, str) or not code_value.strip()
                or code_value != code_value.strip()):
            raise ValueError("ARC API award code must be nonblank unpadded text")
        code = code_value
        links = item.get("links")
        if not isinstance(links, dict):
            raise ValueError("ARC API item links must be an object")
        link = _validated_self_link(links.get("self"),
                                    {value for value in (code, item_id) if value})
        title_value = attrs.get("grant-summary")
        scheme_value = attrs.get("scheme-name")
        status_value = attrs.get("grant-status")
        for field, value in (("grant-summary", title_value), ("scheme-name", scheme_value),
                             ("grant-status", status_value)):
            if value is not None and not isinstance(value, str):
                raise ValueError(f"ARC API award {field} must be text or null")
        amount_value = attrs.get("current-funding-amount")
        if (amount_value is not None
                and not isinstance(amount_value, (str, int, float))):
            raise ValueError("ARC API award current-funding-amount must be text or numeric")
        if isinstance(amount_value, bool) or (isinstance(amount_value, float) and not math.isfinite(amount_value)):
            raise ValueError("ARC API award current-funding-amount must be finite and not boolean")
        records.append({
            "RecordKind": "Award",
            "Source": "arc",
            "SourceID": source_id,
            "AwardCode": code,
            "Title": (title_value or scheme_value or "").strip(),
            "Funder": "Australian Research Council",
            "URL": link,
            "Description": (title_value or "").strip(),
            "Amount": str(amount_value).strip() if amount_value is not None else "",
            "Status": (status_value or "Unknown").strip(),
            "RetrievedUTC": retrieved_at,
            "EvidenceHash": "",
        })
    return records


def fetch_award_page(*, page_number: int = 1, page_size: int = 1000,
                     retrieved_at: str | None = None,
                     opener: Callable[..., Any] = urllib.request.urlopen,
                     catalogue_path: str | Path = DEFAULT_CATALOGUE) -> dict[str, Any]:
    """Fetch one bounded ARC page and return typed awards plus pagination metadata."""
    require_enabled_source(catalogue_path, "arc-awards-api")
    observed = (dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
                if retrieved_at is None else retrieved_at)
    url = _request_url(page_number, page_size)
    response_failure: str | None = None
    retained_responses: list[dict[str, Any]] = []
    try:
        payload = _read_json(url, opener, retained_responses=retained_responses)
    except ARCAPIHTTPError:
        raise
    except ValueError:
        response_failure = "response_validation"
    if response_failure is not None:
        # Raise after leaving the except block so malformed raw data is not
        # retained as an exception context on the sanitized failure object.
        raise ARCPageValidationError(response_failure)
    record_failure: str | None = None
    try:
        records = parse_award_page(payload, retrieved_at=observed)
    except ValueError:
        record_failure = "award_record_validation"
    if record_failure is not None:
        raise ARCPageValidationError(record_failure)
    return {
        "source": "arc",
        "record_kind": "awards_only",
        "api_url": url,
        "meta": payload.get("meta", {}),
        "raw_source": {"http_responses": retained_responses},
        "records": records,
    }


def _exact_meta(payload: dict[str, Any], page_number: int, page_size: int) -> tuple[int, int]:
    meta = payload.get("meta")
    if not isinstance(meta, dict):
        raise ValueError("ARC API page lacks pagination metadata")
    fields = ("requested-page-number", "requested-page-size", "actual-page-size",
              "total-pages", "total-size")
    if any(not isinstance(meta.get(key), int) or isinstance(meta[key], bool) for key in fields):
        raise ValueError("ARC API pagination metadata must contain exact integers")
    total, pages = meta["total-size"], meta["total-pages"]
    expected_pages = max(1, (total + page_size - 1) // page_size)
    expected_size = min(page_size, max(0, total - (page_number - 1) * page_size))
    if (total < 0 or total > MAX_TOTAL_AWARDS or pages != expected_pages or pages > MAX_PAGES
            or meta["requested-page-number"] != page_number
            or meta["requested-page-size"] != page_size
            or meta["actual-page-size"] != expected_size
            or len(payload["data"]) != expected_size):
        raise ValueError("ARC API page count or pagination metadata changed")
    return total, pages


def _cli_success_summary(result: dict[str, Any], *, snapshot: bool,
                         private_output_saved: bool) -> dict[str, Any]:
    """Return safe classification and count metadata without award row values."""
    records = result.get("records")
    if not isinstance(records, list):
        raise ValueError("ARC result must contain a records list")
    summary: dict[str, Any] = {
        "source": "arc",
        "record_kind": "awards_only",
        "record_count": len(records),
        "canonical_opportunity_admission": False,
        "private_output_saved": private_output_saved,
    }
    if snapshot:
        for key in ("snapshot_complete", "source_total", "page_count", "page_size",
                    "snapshot_hash", "replay_passes", "authoritative_lifecycle_semantics_proven"):
            value = result.get(key)
            if ((key.endswith("_complete") or key.endswith("_proven")) and type(value) is bool
                    or (key in {"source_total", "page_count", "page_size", "replay_passes"}
                        and type(value) is int)
                    or (key == "snapshot_hash" and isinstance(value, str)
                        and len(value) == 64 and all(character in "0123456789abcdef" for character in value))):
                summary[key] = value
    else:
        summary["sample_complete"] = True
        meta = result.get("meta")
        if isinstance(meta, dict):
            safe_meta = {key: meta[key] for key in (
                "requested-page-number", "requested-page-size", "actual-page-size",
                "total-pages", "total-size") if type(meta.get(key)) is int}
            if safe_meta:
                summary["page_metadata"] = safe_meta
    return summary


def fetch_award_snapshot(*, page_size: int = 500, retrieved_at: str | None = None,
                         opener: Callable[..., Any] = urllib.request.urlopen,
                         catalogue_path: str | Path = DEFAULT_CATALOGUE) -> dict[str, Any]:
    """Capture the complete official award set twice, failing closed on drift.

    An equal replay is a bounded observation, not proof of immutable award IDs,
    authoritative deletions, or opportunity status.
    """
    require_enabled_source(catalogue_path, "arc-awards-api")
    _request_url(1, page_size)
    observed = (dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
                if retrieved_at is None else retrieved_at)
    # Validate the observation timestamp even for an empty source.
    parse_award_page({"data": []}, retrieved_at=observed)
    retained_responses: list[dict[str, Any]] = []
    pass_digests: list[str] = []
    final_records: list[dict[str, Any]] = []
    total = pages = 0
    for pass_number in range(2):
        row_hashes: dict[str, str] = {}
        records: list[dict[str, Any]] = []
        page_number = 1
        while True:
            try:
                payload = _read_json(_request_url(page_number, page_size), opener,
                                     retained_responses=retained_responses)
            except ARCAPIHTTPError as exc:
                raise ARCSnapshotFetchError(
                    pass_number=pass_number + 1,
                    page_number=page_number,
                    completed_pages=page_number - 1,
                    total_pages=pages,
                    failure_kind="http_failure",
                    http_metadata=exc.metadata,
                ) from None
            except (urllib.error.URLError, TimeoutError):
                raise ARCSnapshotFetchError(
                    pass_number=pass_number + 1,
                    page_number=page_number,
                    completed_pages=page_number - 1,
                    total_pages=pages,
                    failure_kind="network_request_failure",
                ) from None
            page_total, page_count = _exact_meta(payload, page_number, page_size)
            if page_number == 1:
                if pass_number and (page_total, page_count) != (total, pages):
                    raise ValueError("ARC API total changed between passes")
                total, pages = page_total, page_count
            elif (page_total, page_count) != (total, pages):
                raise ValueError("ARC API total changed during capture")
            typed = parse_award_page(payload, retrieved_at=observed)
            for source, record in zip(payload["data"], typed):
                source_id = record["SourceID"]
                if source_id in row_hashes:
                    raise ValueError("ARC API repeated an award ID across pages")
                encoded = json.dumps(source, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode("utf-8")
                row_hashes[source_id] = hashlib.sha256(encoded).hexdigest()
            records.extend(typed)
            if page_number == pages:
                break
            page_number += 1
        if len(row_hashes) != total:
            raise ValueError("ARC API capture does not cover declared total")
        digest = hashlib.sha256(json.dumps(sorted(row_hashes.items()),
                                           separators=(",", ":")).encode("utf-8")).hexdigest()
        pass_digests.append(digest)
        final_records = records
    if pass_digests[0] != pass_digests[1]:
        raise ValueError("ARC API award content changed between passes")
    return {
        "source": "arc",
        "record_kind": "awards_only",
        "retrieved_utc": observed,
        "source_total": total,
        "page_count": pages,
        "page_size": page_size,
        "snapshot_complete": True,
        "snapshot_hash": pass_digests[1],
        "replay_passes": 2,
        "authoritative_lifecycle_semantics_proven": False,
        "canonical_opportunity_admission": False,
        "raw_source": {"http_responses": retained_responses,
                       "complete_reads": 2, "candidate_filter_applied": False},
        "records": final_records,
    }


def main(argv: list[str] | None = None, *, sample_fetcher=fetch_award_page,
         snapshot_fetcher=fetch_award_snapshot) -> int:
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--sample", action="store_true", help="fetch the first bounded award page")
    mode.add_argument("--snapshot", action="store_true", help="fetch and replay the complete bounded award set")
    parser.add_argument("--catalogue", type=Path, default=DEFAULT_CATALOGUE,
                        help="source catalogue used to enforce the ARC enabled switch")
    parser.add_argument("--out", type=Path,
                        help="save fetched award rows under ignored private/ops/; never overwrites")
    args = parser.parse_args(argv)
    if not args.sample and not args.snapshot:
        parser.print_help()
        return 0
    destination = None
    if args.out:
        destination = args.out.resolve()
        try:
            destination.relative_to(PRIVATE_OPS_ROOT.resolve())
        except ValueError:
            parser.error("--out must be inside the repository's ignored private/ops directory")
        if destination.exists():
            parser.error("--out refuses to overwrite existing private evidence")
    if args.snapshot and destination is None:
        parser.error("--snapshot requires --out inside ignored private/ops/")
    try:
        require_enabled_source(args.catalogue, "arc-awards-api")
    except ValueError:
        parser.error("ARC source is missing or disabled in the source catalogue")
    try:
        result = (snapshot_fetcher(catalogue_path=args.catalogue) if args.snapshot
                  else sample_fetcher(page_size=1, catalogue_path=args.catalogue))
    except ARCSnapshotFetchError as exc:
        print(json.dumps({
            "source": "arc",
            "snapshot_complete": False,
            "failure": "snapshot_request_failed",
            "failure_metadata": exc.metadata,
        }, indent=2))
        return 1
    except ARCPageValidationError as exc:
        print(json.dumps({
            "source": "arc",
            "failure": "snapshot_validation_failed" if args.snapshot else "sample_validation_failed",
            "failure_metadata": exc.metadata,
            **({"snapshot_complete": False} if args.snapshot else {}),
        }, indent=2))
        return 1
    except ARCAPIHTTPError as exc:
        print(json.dumps({
            "source": "arc",
            "failure": "snapshot_request_failed" if args.snapshot else "sample_request_failed",
            "failure_metadata": {"http": exc.metadata},
            **({"snapshot_complete": False} if args.snapshot else {}),
        }, indent=2))
        return 1
    except ValueError as exc:
        # Keep validation detail out of CLI output: upstream payloads and
        # catalogue paths must not be echoed into logs. The class is enough
        # to distinguish a bounded sample validation failure for triage.
        failure = {
            "source": "arc",
            "failure": "snapshot_validation_failed" if args.snapshot else "sample_validation_failed",
            "failure_metadata": {"failure_class": type(exc).__name__},
        }
        if args.snapshot:
            failure["snapshot_complete"] = False
        print(json.dumps(failure, indent=2))
        return 1
    if destination:
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            descriptor = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
                stream.write(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
        except FileExistsError:
            print(json.dumps({"source": "arc", "failure": "private_output_exists"}, indent=2))
            return 1
        except OSError as exc:
            print(json.dumps({"source": "arc", "failure": "private_output_write_failed",
                              "failure_metadata": {"failure_class": type(exc).__name__}}, indent=2))
            return 1
    print(json.dumps(_cli_success_summary(result, snapshot=args.snapshot,
                                          private_output_saved=destination is not None), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
