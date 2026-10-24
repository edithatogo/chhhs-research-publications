"""Analyse the published sitemap as opaque version evidence, never UTC coverage."""
import re
import xml.etree.ElementTree as ET

NS = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
PREFIX = "https://dora.health.qld.gov.au/qldresearchjspui/handle/1/"


def inventory(xml: str, required: list[str]) -> dict:
    if (len(required) != len(set(required)) or not required
            or any(not re.fullmatch(r"[1-9][0-9]*", key) for key in required)
            or "<!DOCTYPE" in xml.upper() or "<!ENTITY" in xml.upper()):
        raise ValueError("Unique canonical handles and entity-free XML required")
    root = ET.fromstring(xml)
    if root.tag != NS + "urlset":
        raise ValueError("Expected the actual published sitemap page")
    selected = {}
    wanted = set(required)
    for node in root.findall(NS + "url"):
        url = node.findtext(NS + "loc", "")
        if not url.startswith(PREFIX):
            continue
        key = url[len(PREFIX):]
        if key not in wanted:
            continue
        if key in selected:
            raise ValueError("Duplicate selected sitemap handle")
        stamp = node.findtext(NS + "lastmod", "")
        if not stamp or stamp != stamp.strip():
            raise ValueError("Missing opaque source version")
        selected[key] = {"source_url": url, "source_stamp": stamp}
    return {"versions": selected, "missing": sorted(wanted - selected.keys()),
            "timestamps_are_opaque": True, "utc_cutoff_proven": False}


def select_work(versions: dict, cache: dict, *, version_contract_qualified=False) -> dict:
    """Fail closed until current-source change semantics and cache lineage pass.

    The qualification flag is an external evidence gate, not inferred from a
    stable sitemap, Last-Modified header, elapsed time or this local test.
    No native collector currently invokes this selector.
    """
    fetch, reuse = [], []
    for key, version in sorted(versions.items()):
        entry = cache.get(key, {})
        valid = (entry.get("source_stamp") == version["source_stamp"]
                 and entry.get("source_url") == version["source_url"]
                 and isinstance(entry.get("bytes"), int) and not isinstance(entry.get("bytes"), bool)
                 and entry["bytes"] > 0 and entry.get("native_id") and entry.get("etag")
                 and entry.get("archive_folder") and entry.get("file")
                 and re.fullmatch(r"[a-f0-9]{64}", entry.get("sha256", "")))
        if version_contract_qualified and valid:
            reuse.append({"key": key, "evidence": dict(entry)})
        else:
            fetch.append(key)
    return {"fetch": fetch, "reuse": reuse, "native_deployed": False,
            "version_contract_qualified": version_contract_qualified}
