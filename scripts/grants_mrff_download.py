"""Retain the official MRFF grant-recipient workbook set without transforming it.

The command discovers the three current Excel resources from the Department's
public dataset page, validates the official host and XLSX payloads, and stores
the originals with private source and copyright evidence. It does not admit
award rows or funded-rate summaries to opportunity intake.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import urllib.error
import zipfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

try:
    from scripts.grants_nhmrc_download import _Links, _fetch, _workbook_inventory
except ImportError:
    from grants_nhmrc_download import _Links, _fetch, _workbook_inventory

REPO_ROOT = Path(__file__).resolve().parents[1]
PRIVATE_OPS = REPO_ROOT / "private" / "ops"
SOURCE_PAGE = (
    "https://www.health.gov.au/resources/publications/"
    "medical-research-future-fund-mrff-grant-recipients?language=en"
)
COPYRIGHT_PAGE = "https://www.health.gov.au/using-our-websites/copyright"
OFFICIAL_HOST = "www.health.gov.au"
MAX_PAGE_BYTES = 5_000_000
MAX_WORKBOOK_BYTES = 20_000_000
XLSX_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


class _Text(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


def _filename(url: str) -> str:
    name = Path(unquote(urlsplit(url).path)).name
    return re.sub(r"[^A-Za-z0-9._-]+", "-", name) or "mrff-resource.xlsx"


def _resource_kind(label: str, url: str) -> str:
    # The publisher exposes the same visible link label for every Excel
    # attachment; distinguish the resource type using the official filename.
    folded = (label + " " + urlsplit(url).path).casefold()
    if "funded rates" in folded or "funded_rates" in folded or "funded-rates" in folded:
        return "opportunity_funded_rates_summary"
    if "summary" in folded:
        return "awarded_grants_summary"
    if "recipient" in folded or "grant recipients" in folded:
        return "awarded_grant_recipients"
    raise ValueError("unrecognized MRFF Excel attachment; refusing source misclassification")


def acquire(destination: Path) -> dict[str, object]:
    destination = destination.resolve()
    try:
        destination.relative_to(PRIVATE_OPS.resolve())
    except ValueError as exc:
        raise ValueError("output must be inside this repository's ignored private/ops directory") from exc
    if destination.exists():
        raise FileExistsError("output directory already exists; use a new evidence path")

    page, page_headers, page_final = _fetch(SOURCE_PAGE, MAX_PAGE_BYTES, OFFICIAL_HOST)
    parser = _Links()
    parser.feed(page.decode("utf-8", "replace"))
    resources: list[dict[str, str]] = []
    for link in parser.links:
        label = " ".join(link["text"].split())
        url = urljoin(page_final, link["href"])
        parsed = urlsplit(url)
        if ".xlsx" not in parsed.path.casefold():
            continue
        if "medical research future fund" not in label.casefold() or "excel" not in label.casefold():
            continue
        if parsed.scheme != "https" or parsed.hostname != OFFICIAL_HOST:
            raise ValueError("selected workbook link is outside the official Department host")
        resources.append({"label": label, "url": url, "kind": _resource_kind(label, url)})
    kinds = [row["kind"] for row in resources]
    expected = {"awarded_grant_recipients", "awarded_grants_summary", "opportunity_funded_rates_summary"}
    if len(resources) != 3 or set(kinds) != expected or len(set(kinds)) != 3:
        raise ValueError("expected exactly one recipients, award-summary and funded-rates workbook")

    text = _Text()
    text.feed(page.decode("utf-8", "replace"))
    page_text = " ".join(" ".join(text.parts).split())
    as_of = re.search(r"correct as at\s+(\d{1,2}\s+[A-Za-z]+\s+\d{4})", page_text, re.I)
    published = re.search(r"Publication date:\s*(\d{1,2}\s+[A-Za-z]+\s+\d{4})", page_text, re.I)
    if not as_of or not published:
        raise ValueError("official dataset page did not expose its data-as-of and publication dates")

    captured: list[dict[str, object]] = []
    payloads: list[tuple[str, bytes]] = []
    for resource in resources:
        body, headers, final_url = _fetch(resource["url"], MAX_WORKBOOK_BYTES, OFFICIAL_HOST)
        content_type = headers.get("content-type", "").split(";", 1)[0].strip().lower()
        if content_type != XLSX_MIME:
            raise ValueError(f"{resource['kind']} response did not have the XLSX media type")
        inventory = _workbook_inventory(body)
        basename = _filename(resource["url"])
        payloads.append((basename, body))
        captured.append({
            "resource_kind": resource["kind"],
            "record_kind": resource["kind"],
            "label": resource["label"],
            "url": resource["url"],
            "final_url": final_url,
            "content_type": content_type,
            "last_modified": headers.get("last-modified"),
            "etag": headers.get("etag"),
            "path": basename,
            "bytes": len(body),
            "sha256": hashlib.sha256(body).hexdigest(),
            "zip_integrity": "passed",
            "sheet_inventory": inventory,
        })

    copyright_body, copyright_headers, copyright_final = _fetch(
        COPYRIGHT_PAGE, MAX_PAGE_BYTES, OFFICIAL_HOST
    )
    if "text/html" not in copyright_headers.get("content-type", "").lower():
        raise ValueError("Department copyright guidance response was not HTML")
    observed_at = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    destination.mkdir(parents=True)
    (destination / "source-page.html").write_bytes(page)
    (destination / "copyright-page.html").write_bytes(copyright_body)
    for name, body in payloads:
        (destination / name).write_bytes(body)

    receipt: dict[str, object] = {
        "status": "acquired_unmodified_official_sources",
        "observed_at": observed_at,
        "source_page": SOURCE_PAGE,
        "source_page_final_url": page_final,
        "source_page_last_modified": page_headers.get("last-modified"),
        "source_page_sha256": hashlib.sha256(page).hexdigest(),
        "data_correct_as_at": as_of.group(1),
        "publication_date": published.group(1),
        "audience": "General public",
        "resources": captured,
        "copyright": {
            "policy_page": COPYRIGHT_PAGE,
            "policy_final_url": copyright_final,
            "policy_page_sha256": hashlib.sha256(copyright_body).hexdigest(),
            "policy_capture": "copyright-page.html",
            "basis": "Department guidance permits unaltered download and reproduction for internal organisational use unless otherwise indicated, with copyright and disclaimer notices retained.",
            "item_specific_exception_check": "The dataset page exposes no separate licence notice in its metadata; the original resources and page are retained unaltered for internal use.",
            "adaptation_or_external_redistribution": "not performed or authorised",
        },
        "opportunity_admission": False,
        "identity_limit": "Recipients file includes Grant ID; this acquisition does not qualify stable round identity, lifecycle semantics or a canonical RIMS OpportunityKey mapping.",
        "recovery": "Repeat to a new private/ops directory; this command refuses an existing output directory.",
    }
    (destination / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fetch", action="store_true", help="explicitly fetch the official MRFF Excel resources")
    parser.add_argument("--out", type=Path, help="new directory under ignored private/ops/ for raw files and receipt")
    args = parser.parse_args()
    if not args.fetch:
        parser.error("live downloads require explicit --fetch")
    if args.out is None:
        parser.error("--out is required for private evidence retention")
    try:
        receipt = acquire(args.out)
    except (OSError, ValueError, urllib.error.URLError, zipfile.BadZipFile, KeyError):
        parser.error("MRFF acquisition failed; inspect the official page, host, licence, and workbook response")
    print(json.dumps({
        "status": receipt["status"],
        "observed_at": receipt["observed_at"],
        "data_correct_as_at": receipt["data_correct_as_at"],
        "publication_date": receipt["publication_date"],
        "resource_count": len(receipt["resources"]),
        "total_bytes": sum(item["bytes"] for item in receipt["resources"]),
        "opportunity_admission": False,
    }, indent=2))


if __name__ == "__main__":
    main()
