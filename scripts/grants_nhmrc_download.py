"""Retain the current NHMRC outcomes workbook without transforming it.

This is an explicit, read-only download route for the official NHMRC outcomes
page. It captures the page, the exact linked workbook, publisher copyright
guidance, and a private integrity receipt. It does not admit awards to
opportunity intake or map NHMRC identifiers to the RIMS grant key.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import urllib.error
import urllib.request
import zipfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit
from xml.etree import ElementTree as ET

REPO_ROOT = Path(__file__).resolve().parents[1]
PRIVATE_OPS = REPO_ROOT / "private" / "ops"
SOURCE_PAGE = "https://www.nhmrc.gov.au/funding/data-research/outcomes"
COPYRIGHT_PAGE = "https://www.nhmrc.gov.au/copyright"
OFFICIAL_HOST = "www.nhmrc.gov.au"
MAX_PAGE_BYTES = 5_000_000
MAX_WORKBOOK_BYTES = 20_000_000
USER_AGENT = "CHHHS-RIMS-NHMRC-outcomes-readback/1.0"
XLSX_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
NS = {
    "m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}


class _Links(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[dict[str, str]] = []
        self._current: dict[str, str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "a":
            self._current = {"href": dict(attrs).get("href") or "", "text": ""}

    def handle_data(self, data: str) -> None:
        if self._current is not None:
            self._current["text"] += data

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._current is not None:
            self.links.append(self._current)
            self._current = None


def _fetch(
    url: str, limit: int, allowed_host: str = OFFICIAL_HOST,
) -> tuple[bytes, dict[str, str], str]:
    request = urllib.request.Request(
        url, headers={"User-Agent": USER_AGENT, "Accept": "text/html,*/*"}, method="GET"
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        final = urlsplit(response.geturl())
        original = urlsplit(url)
        if (final.scheme != "https" or final.hostname != allowed_host
                or original.hostname != allowed_host or final.username or final.password):
            raise ValueError("request redirected outside the expected official host")
        if not 200 <= int(response.getcode() or 0) < 300:
            raise ValueError("official source returned a non-success status")
        body = response.read(limit + 1)
        if len(body) > limit:
            raise ValueError("official response exceeded the bounded read size")
        headers = {name.lower(): str(value) for name, value in response.headers.items()}
        return body, headers, response.geturl()


def _workbook_inventory(body: bytes) -> list[dict[str, str | None]]:
    """Read workbook labels and bounds while retaining the original bytes."""
    with zipfile.ZipFile(__import__("io").BytesIO(body)) as archive:
        if archive.testzip() is not None:
            raise ValueError("downloaded workbook failed ZIP integrity validation")
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        relationships = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        targets = {item.attrib["Id"]: item.attrib["Target"] for item in relationships}
        shared_strings: list[str] = []
        if "xl/sharedStrings.xml" in archive.namelist():
            shared_root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            shared_strings = [
                "".join(text.text or "" for text in item.findall(".//m:t", NS))
                for item in shared_root.findall("m:si", NS)
            ]
        result = []
        for sheet in workbook.findall("m:sheets/m:sheet", NS):
            target = targets[sheet.attrib[f"{{{NS['r']}}}id"]].lstrip("/")
            if not target.startswith("xl/"):
                target = "xl/" + target
            root = ET.fromstring(archive.read(target))
            dimension = root.find("m:dimension", NS)
            first_row = root.find("m:sheetData/m:row", NS)
            headers: list[str] = []
            if first_row is not None:
                for cell in first_row.findall("m:c", NS):
                    value = cell.find("m:v", NS)
                    if value is not None and value.text:
                        raw = value.text
                        headers.append(
                            shared_strings[int(raw)]
                            if cell.attrib.get("t") == "s" else raw
                        )
            result.append({
                "sheet": sheet.attrib.get("name"),
                "dimension": dimension.attrib.get("ref") if dimension is not None else None,
                "first_row_cells": ", ".join(headers[:30]),
            })
        return result


def _dataset_metadata(body: bytes) -> dict[str, str]:
    """Read the workbook's source-declared metadata without projecting rows."""
    with zipfile.ZipFile(__import__("io").BytesIO(body)) as archive:
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        relationships = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        targets = {item.attrib["Id"]: item.attrib["Target"] for item in relationships}
        shared_strings: list[str] = []
        if "xl/sharedStrings.xml" in archive.namelist():
            shared_root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            shared_strings = [
                "".join(text.text or "" for text in item.findall(".//m:t", NS))
                for item in shared_root.findall("m:si", NS)
            ]
        metadata_sheet = next(
            sheet for sheet in workbook.findall("m:sheets/m:sheet", NS)
            if sheet.attrib.get("name") == "METADATA"
        )
        target = targets[metadata_sheet.attrib[f"{{{NS['r']}}}id"]].lstrip("/")
        if not target.startswith("xl/"):
            target = "xl/" + target
        root = ET.fromstring(archive.read(target))
        values: dict[str, str] = {}
        for row in root.findall("m:sheetData/m:row", NS):
            cells = row.findall("m:c", NS)
            if len(cells) < 2:
                continue
            pair: list[str] = []
            for cell in cells[:2]:
                value = cell.find("m:v", NS)
                raw = value.text if value is not None and value.text else ""
                if cell.attrib.get("t") == "s" and raw:
                    raw = shared_strings[int(raw)]
                pair.append(raw)
            label, value = pair
            if label and value:
                values[label] = value

    allowlist = (
        "Identifier", "Title", "Description", "Data custodian", "Access rights",
        "Security classification", "Updated frequency", "Legal authority",
        "Publisher", "Sensitive data", "Temporal coverage from (yyyy-mm-dd)",
        "Temporal coverage to (yyyy-mm-dd)", "Publish date (yyyy-mm-dd)",
        "Date modified (yyyy-mm-dd)",
    )
    result = {key: values[key] for key in allowlist if key in values}
    excel_epoch = dt.datetime(1899, 12, 30)
    for key in allowlist:
        value = result.get(key)
        if value and "(yyyy-mm-dd)" in key:
            try:
                result[key] = (excel_epoch + dt.timedelta(days=float(value))).date().isoformat()
            except (ValueError, OverflowError):
                pass
    return result


def acquire(round_year: int, destination: Path) -> dict[str, object]:
    destination = destination.resolve()
    try:
        destination.relative_to(PRIVATE_OPS.resolve())
    except ValueError as exc:
        raise ValueError("output must be inside this repository's ignored private/ops directory") from exc
    if destination.exists():
        raise FileExistsError("output directory already exists; use a new evidence path")

    page, page_headers, page_final = _fetch(SOURCE_PAGE, MAX_PAGE_BYTES)
    parser = _Links()
    parser.feed(page.decode("utf-8", "replace"))
    candidates = []
    for link in parser.links:
        label = " ".join(link["text"].split())
        href = urljoin(page_final, link["href"])
        parsed = urlsplit(href)
        if (str(round_year) in label and "NHMRC" in label
                and "Grant Application Round" in label and parsed.path.lower().endswith(".xlsx")):
            if parsed.scheme != "https" or parsed.hostname != OFFICIAL_HOST:
                raise ValueError("selected workbook link is outside the official NHMRC host")
            candidates.append({"label": label, "url": href})
    if len(candidates) != 1:
        raise ValueError(f"expected one official workbook for round {round_year}; found {len(candidates)}")

    workbook_url = candidates[0]["url"]
    workbook_request = urllib.request.Request(
        workbook_url,
        headers={"User-Agent": USER_AGENT, "Accept": XLSX_MIME},
        method="GET",
    )
    with urllib.request.urlopen(workbook_request, timeout=60) as response:
        final = urlsplit(response.geturl())
        if (final.scheme != "https" or final.hostname != OFFICIAL_HOST
                or final.username or final.password):
            raise ValueError("workbook request redirected outside the official NHMRC host")
        if not 200 <= int(response.getcode() or 0) < 300:
            raise ValueError("official workbook returned a non-success status")
        content_type = response.headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
        if content_type != XLSX_MIME:
            raise ValueError("official workbook response did not have the XLSX media type")
        body = response.read(MAX_WORKBOOK_BYTES + 1)
        headers = {name.lower(): str(value) for name, value in response.headers.items()}
    if len(body) > MAX_WORKBOOK_BYTES:
        raise ValueError("official workbook exceeded the bounded read size")
    inventory = _workbook_inventory(body)
    dataset_metadata = _dataset_metadata(body)
    copyright_page, copyright_headers, copyright_final = _fetch(COPYRIGHT_PAGE, MAX_PAGE_BYTES)
    if "text/html" not in copyright_headers.get("content-type", "").lower():
        raise ValueError("NHMRC copyright guidance response was not HTML")
    observed_at = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    from urllib.parse import unquote
    basename = Path(unquote(urlsplit(workbook_url).path)).name
    safe_name = re.sub(r"[^A-Za-z0-9._-]+", "-", basename) or f"nhmrc-{round_year}-outcomes.xlsx"
    destination.mkdir(parents=True)
    (destination / "source-page.html").write_bytes(page)
    (destination / "copyright-page.html").write_bytes(copyright_page)
    (destination / safe_name).write_bytes(body)
    receipt: dict[str, object] = {
        "status": "acquired_unmodified_official_source",
        "observed_at": observed_at,
        "source": "NHMRC outcomes of funding rounds",
        "source_page_url": SOURCE_PAGE,
        "source_page_final_url": page_final,
        "source_page_last_modified": page_headers.get("last-modified"),
        "source_page_sha256": hashlib.sha256(page).hexdigest(),
        "selected_link_label": candidates[0]["label"],
        "workbook_url": workbook_url,
        "workbook_final_url": response.geturl(),
        "workbook_content_type": content_type,
        "workbook_last_modified": headers.get("last-modified"),
        "workbook_etag": headers.get("etag"),
        "workbook_bytes": len(body),
        "workbook_sha256": hashlib.sha256(body).hexdigest(),
        "workbook_path": safe_name,
        "workbook_zip_integrity": "passed",
        "sheet_inventory": inventory,
        "dataset_metadata": dataset_metadata,
        "access_rights_is_not_a_reuse_license": True,
        "record_kind": "awarded_grant_outcomes_context",
        "identity_observed": "GRANTS DATA includes Application ID and Grant Opportunity ID fields; no canonical RIMS OpportunityKey mapping established",
        "opportunity_admission": False,
        "licensing": {
            "policy_page": COPYRIGHT_PAGE,
            "policy_final_url": copyright_final,
            "policy_page_sha256": hashlib.sha256(copyright_page).hexdigest(),
            "policy_capture": "copyright-page.html",
            "basis": "NHMRC copyright guidance says item-level notices govern; material without a CC notice may be retained unaltered for use within an organisation. The captured workbook remains unchanged.",
            "adaptation_or_external_redistribution": "not assessed or authorised by this acquisition",
        },
        "recovery": "Repeat to a new private/ops directory; this command refuses an existing output directory.",
    }
    (destination / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fetch", action="store_true", help="explicitly fetch the official current outcome workbook")
    parser.add_argument("--round-year", type=int, default=2026)
    parser.add_argument("--out", type=Path, help="new directory under ignored private/ops/ for raw files and receipt")
    args = parser.parse_args()
    if not args.fetch:
        parser.error("live downloads require explicit --fetch")
    if args.out is None:
        parser.error("--out is required for private evidence retention")
    try:
        receipt = acquire(args.round_year, args.out)
    except (OSError, ValueError, urllib.error.URLError, zipfile.BadZipFile, KeyError, ET.ParseError) as exc:
        parser.error(f"NHMRC acquisition failed: {exc}")
    print(json.dumps({
        "status": receipt["status"],
        "observed_at": receipt["observed_at"],
        "workbook_sha256": receipt["workbook_sha256"],
        "workbook_bytes": receipt["workbook_bytes"],
        "sheet_count": len(receipt["sheet_inventory"]),
        "opportunity_admission": False,
    }, indent=2))


if __name__ == "__main__":
    main()
