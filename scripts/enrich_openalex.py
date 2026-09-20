"""OpenAlex API enrichment module for CHHHS Publication Registry.

Queries OpenAlex REST API for work metadata, citation counts, open access status,
grants/funders, and keywords using polite pool headers.
"""
from __future__ import annotations

import json
import logging
import os
import re
import time
import sys
from pathlib import Path
from typing import Any
import urllib.parse
import urllib.request
import urllib.error

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from project_utils import ROOT, save_json

logger = logging.getLogger(__name__)

OPENALEX_BASE_URL = "https://api.openalex.org/works"
DEFAULT_POLITE_EMAIL = os.environ.get("OPENALEX_POLITE_EMAIL", "")
USER_AGENT = f"CHHHS-Research-Registry/1.0 (mailto:{DEFAULT_POLITE_EMAIL})"


def clean_doi(raw_doi: Any) -> str | None:
    """Normalize DOI string by stripping URL prefixes and whitespace."""
    if not raw_doi or not isinstance(raw_doi, str):
        return None
    cleaned = raw_doi.strip()
    cleaned = re.sub(r'^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)', '', cleaned, flags=re.I).strip()
    if re.fullmatch(r'10\.\d{4,9}/\S+', cleaned):
        return cleaned
    return None


def fetch_openalex_work_by_doi(doi: str, email: str = DEFAULT_POLITE_EMAIL, timeout: int = 10) -> dict[str, Any] | None:
    """Fetch OpenAlex metadata for a single DOI."""
    normalized_doi = clean_doi(doi)
    if not normalized_doi:
        return None

    doi_url = f"https://doi.org/{normalized_doi}"
    encoded_doi = urllib.parse.quote(doi_url, safe="")
    url = f"{OPENALEX_BASE_URL}/{encoded_doi}?mailto={urllib.parse.quote(email)}"

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                return data
    except urllib.error.HTTPError as e:
        if e.code == 404:
            logger.debug("DOI %s not found in OpenAlex", normalized_doi)
        else:
            logger.warning("HTTP error %d fetching OpenAlex for DOI %s: %s", e.code, normalized_doi, e.reason)
    except Exception as e:
        logger.warning("Error fetching OpenAlex for DOI %s: %s", normalized_doi, e)

    return None


def fetch_openalex_batch(
    dois: list[str],
    email: str = DEFAULT_POLITE_EMAIL,
    timeout: int = 15,
) -> dict[str, dict[str, Any]]:
    """Fetch OpenAlex metadata for a batch of DOIs (up to 50 per request)."""
    cleaned_dois = [clean_doi(d) for d in dois if clean_doi(d)]
    if not cleaned_dois:
        return {}

    filter_val = "|".join(f"https://doi.org/{d}" for d in cleaned_dois)
    url = f"{OPENALEX_BASE_URL}?filter=doi:{urllib.parse.quote(filter_val)}&per_page=50&mailto={urllib.parse.quote(email)}"

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
        },
    )

    results_by_doi: dict[str, dict[str, Any]] = {}
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                for item in data.get("results", []):
                    item_doi = clean_doi(item.get("doi"))
                    if item_doi:
                        results_by_doi[item_doi] = extract_openalex_metrics(item)
    except urllib.error.HTTPError as e:
        logger.warning("HTTP error %d fetching OpenAlex batch: %s", e.code, e.reason)
    except Exception as e:
        logger.warning("Error fetching OpenAlex batch: %s", e)

    return results_by_doi


def extract_openalex_metrics(raw_data: dict[str, Any] | None) -> dict[str, Any]:
    """Extract standard registry enrichment fields from raw OpenAlex payload."""
    if not raw_data or not isinstance(raw_data, dict):
        return {
            "OpenAlexID": None,
            "CitationCount_OpenAlex": None,
            "OpenAccessStatus": None,
            "OAUrl": None,
            "FunderNames": None,
            "GrantIDs": None,
            "MeSHHeadings": None,
            "AuthorKeywords": None,
            "AffiliationsRaw": None,
            "AffiliationHierarchy": None,
        }

    oa_id = raw_data.get("id")
    citations = raw_data.get("cited_by_count")

    oa_info = raw_data.get("open_access", {})
    oa_status = oa_info.get("oa_status")
    if oa_status:
        oa_status = oa_status.capitalize()
    oa_url = oa_info.get("oa_url")

    # Grants & Funders
    grants = raw_data.get("grants", [])
    funder_names = []
    grant_ids = []
    for g in grants:
        if isinstance(g, dict):
            fn = g.get("funder_display_name") or g.get("funder")
            if fn and fn not in funder_names:
                funder_names.append(fn)
            gid = g.get("award_id")
            if gid and gid not in grant_ids:
                grant_ids.append(gid)

    # MeSH
    mesh = raw_data.get("mesh", [])
    mesh_headings = [m.get("descriptor_name") for m in mesh if isinstance(m, dict) and m.get("descriptor_name")]

    # Keywords
    keywords = raw_data.get("keywords", [])
    kw_list = [k.get("keyword") for k in keywords if isinstance(k, dict) and k.get("keyword")]

    # Affiliations
    authorships = raw_data.get("authorships", [])
    raw_affils = []
    hierarchies = []
    for auth in authorships:
        if isinstance(auth, dict):
            for inst in auth.get("institutions", []):
                dn = inst.get("display_name")
                if dn and dn not in raw_affils:
                    raw_affils.append(dn)
                ror = inst.get("ror")
                country = inst.get("country_code")
                if dn:
                    hierarchies.append(f"{dn} [ROR: {ror or 'N/A'}, Country: {country or 'N/A'}]")

    # Field of Research / Topic
    primary_topic = raw_data.get("primary_topic") or {}
    field_name = (primary_topic.get("field") or {}).get("display_name")
    topic_name = primary_topic.get("display_name")
    for_val = field_name or topic_name

    return {
        "OpenAlexID": oa_id,
        "CitationCount_OpenAlex": int(citations) if citations is not None else None,
        "OpenAccessStatus": oa_status,
        "OAUrl": oa_url,
        "FunderNames": "; ".join(funder_names) if funder_names else None,
        "GrantIDs": "; ".join(grant_ids) if grant_ids else None,
        "MeSHHeadings": "; ".join(mesh_headings[:15]) if mesh_headings else None,
        "AuthorKeywords": "; ".join(kw_list[:10]) if kw_list else None,
        "AffiliationsRaw": "; ".join(raw_affils) if raw_affils else None,
        "AffiliationHierarchy": "; ".join(hierarchies[:5]) if hierarchies else None,
        "FieldOfResearch": for_val,
    }


def enrich_record_with_openalex(record: dict[str, Any], email: str = DEFAULT_POLITE_EMAIL) -> dict[str, Any]:
    """Enrich a publication dictionary in-place with OpenAlex metrics."""
    doi = record.get("DOI")
    if not doi:
        return record

    data = fetch_openalex_work_by_doi(doi, email=email)
    if data:
        metrics = extract_openalex_metrics(data)
        for k, v in metrics.items():
            if v is not None:
                record[k] = v
        record["CitationMetricsObservedUTC"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    return record
