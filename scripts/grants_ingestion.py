"""Offline-testable RSS/Atom and API-shaped grants ingestion helpers."""
from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import Any, Iterable

try:
    from .grants_registry import normalize_opportunity
except ImportError:  # direct script execution with scripts/ on sys.path
    from grants_registry import normalize_opportunity


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].casefold()


def _child_text(element: ET.Element, *names: str) -> str:
    wanted = {name.casefold() for name in names}
    for child in element.iter():
        if child is element:
            continue
        if _local(child.tag) in wanted and (child.text or "").strip():
            return " ".join((child.text or "").split())
    return ""


def parse_feed(xml_payload: str | bytes, *, source: str, retrieved_at: str) -> list[dict[str, Any]]:
    """Parse RSS/Atom entries while retaining raw deadline text for review."""
    root = ET.fromstring(xml_payload)
    entries = [node for node in root.iter() if _local(node.tag) in {"item", "entry"}]
    if not entries:
        raise ValueError("feed contains no RSS items or Atom entries")
    result: list[dict[str, Any]] = []
    seen_source_ids: set[str] = set()
    for entry in entries:
        link = _child_text(entry, "link", "url")
        if not link:
            for child in entry:
                if _local(child.tag) == "link" and child.attrib.get("href"):
                    link = child.attrib["href"]
                    break
        source_id = _child_text(entry, "guid", "id", "identifier")
        if source_id:
            if source_id in seen_source_ids:
                raise ValueError(f"duplicate source identity: {source_id}")
            seen_source_ids.add(source_id)
        if not source_id and not link:
            raise ValueError("feed entry missing source identity")
        title = _child_text(entry, "title")
        if not title:
            raise ValueError("feed entry missing title")
        result.append(normalize_opportunity({
            "Source": source,
            "SourceID": source_id,
            "Title": title,
            "URL": link,
            "Description": _child_text(entry, "description", "summary", "content"),
            "Deadline": _child_text(entry, "deadline", "closingdate", "closing-date"),
            "RetrievedUTC": retrieved_at,
        }, retrieved_at=retrieved_at))
    return result


def ingest_batches(batches: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Ingest independent source batches; one bad source cannot erase others."""
    records: list[dict[str, Any]] = []
    health: list[dict[str, Any]] = []
    for batch in batches:
        source = str(batch.get("source", "unknown"))
        try:
            if "xml" in batch:
                parsed = parse_feed(batch["xml"], source=source, retrieved_at=batch["retrieved_at"])
            else:
                parsed = [normalize_opportunity({**row, "Source": source}, retrieved_at=batch["retrieved_at"])
                          for row in batch.get("records", [])]
            records.extend(parsed)
            health.append({"source": source, "status": "succeeded", "count": len(parsed)})
        except (ET.ParseError, TypeError, ValueError, KeyError) as exc:
            health.append({"source": source, "status": "failed", "count": 0, "error": str(exc)})
    return {"records": records, "health": health, "accepted": bool(records) and all(item["status"] == "succeeded" for item in health)}
