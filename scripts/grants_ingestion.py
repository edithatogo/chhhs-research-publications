"""Offline-testable RSS/Atom and API-shaped grants ingestion helpers."""
from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import Any, Iterable
from datetime import timezone

try:
    from .grants_source_identity import feed_source_ids, validate_source_id_path
    from .grants_registry import normalize_opportunity, parse_offset_instant, valid_official_url
    from .grants_sources import qualification_error, required_source_class_matches
    from .grants_deadline_schedule import require_source_schedule
except ImportError:  # direct script execution with scripts/ on sys.path
    from grants_source_identity import feed_source_ids, validate_source_id_path
    from grants_registry import normalize_opportunity, parse_offset_instant, valid_official_url
    from grants_sources import qualification_error, required_source_class_matches
    from grants_deadline_schedule import require_source_schedule


MAX_XML_BYTES = 2_000_000


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


_MACHINE_SOURCE_FIELDS = {
    "SourceID", "ExternalID", "Title", "title", "URL", "SourceRowURL", "Link", "link",
    "Funder", "Organization", "funder", "Description", "Summary", "summary",
    "Eligibility", "Geography", "Amount", "Deadline", "ClosingDate", "deadline",
    "DeadlineTimezone", "deadlineTimezone", "deadline_timezone",
    "SourceTimezone", "sourceTimezone", "source_timezone", "Timezone", "timezone", "time_zone",
    "Status", "Contact", "RoundID", "DeadlineScheduleJSON", "SourceDateFactsJSON", "SourceAttribution",
}


def _machine_source_record(record: Any, *, source: str, retrieved_at: str) -> dict[str, Any]:
    """Keep machine feeds from assigning internal review or relevance state."""
    if not isinstance(record, dict):
        raise TypeError("API record must be an object")
    for field in sorted(_MACHINE_SOURCE_FIELDS):
        if field in record and record[field] is not None and not isinstance(record[field], str):
            raise TypeError(f"API record {field} must be text or null")
        if (field in {"SourceID", "ExternalID", "RoundID"}
                and isinstance(record.get(field), str)
                and record[field] != record[field].strip()):
            raise ValueError(f"API record {field} must be unpadded text")
    values = {key: value for key, value in record.items() if key in _MACHINE_SOURCE_FIELDS}
    values["Source"] = source
    values["RetrievedUTC"] = retrieved_at
    require_source_schedule(values)
    # ReviewStatus, ReviewNotes and CHHHSRelevance are deliberately absent.
    # Only grants_reviewed_import admits human review assertions.
    return values


def _catalogue_row_error(row: dict[str, Any]) -> str | None:
    """Validate the identity/admission fields used at this second trust boundary."""
    source_id = row.get("source_id")
    enabled = row.get("enabled", True)
    if not isinstance(enabled, bool):
        return "catalogue_enabled_invalid"
    if not enabled:
        return "source_disabled"
    intake = row.get("intake")
    hosts = row.get("official_row_hosts")
    reconciliation = row.get("reconciliation")
    if not isinstance(source_id, str) or not source_id or source_id != source_id.strip():
        return "catalogue_source_id_invalid"
    if not required_source_class_matches(row):
        return "immutable_non_opportunity_entity_class"
    if not isinstance(intake, str):
        return "catalogue_intake_invalid"
    if (not isinstance(hosts, list) or not hosts
            or any(not isinstance(host, str) or not host
                   or host != host.strip() for host in hosts)):
        return "catalogue_official_row_hosts_invalid"
    if not isinstance(reconciliation, dict):
        return "catalogue_reconciliation_invalid"
    if any(not isinstance(reconciliation.get(field), str)
           for field in ("admission", "entity", "source_id_path")):
        return "catalogue_reconciliation_invalid"
    try:
        validate_source_id_path(reconciliation["source_id_path"], intake)
    except ValueError:
        return "catalogue_reconciliation_invalid"
    if reconciliation.get("admission") == "opportunity":
        if reconciliation.get("entity") != "opportunity":
            return "catalogue_opportunity_entity_invalid"
        source_qualification_error = qualification_error(row, require_opportunity=True)
        if source_qualification_error:
            return source_qualification_error
    return None


def parse_feed(xml_payload: str | bytes, *, source: str, retrieved_at: str,
               source_id_path: str, intake: str) -> list[dict[str, Any]]:
    """Parse RSS/Atom entries while retaining raw deadline text for review."""
    if not isinstance(source, str) or not source or source != source.strip():
        raise ValueError("invalid_source_identity")
    if not isinstance(retrieved_at, str) or not retrieved_at.strip():
        raise ValueError("invalid_observation_time")
    try:
        parse_offset_instant(retrieved_at)
    except ValueError as exc:
        raise ValueError("invalid_observation_time") from exc
    if not isinstance(xml_payload, (str, bytes)):
        raise TypeError("feed XML payload must be text or bytes")
    if len(xml_payload) > MAX_XML_BYTES or (isinstance(xml_payload, str)
                                            and len(xml_payload.encode("utf-8")) > MAX_XML_BYTES):
        raise ValueError("feed_xml_payload_too_large")
    root = ET.fromstring(xml_payload)
    # A page or API response containing an incidental <item> must not be
    # mistaken for a reconciled feed snapshot.
    kind = _local(root.tag)
    if intake == "rss" and kind == "rss":
        entries = [item for channel in root if _local(channel.tag) == "channel"
                   for item in channel if _local(item.tag) == "item"]
    elif intake == "atom" and kind == "feed":
        entries = [item for item in root if _local(item.tag) == "entry"]
    elif intake == "rss" and kind == "rdf":  # RSS 1.0 uses an RDF root with direct item children.
        entries = [item for item in root if _local(item.tag) == "item"]
    else:
        raise ValueError("feed_envelope_does_not_match_catalogue_intake")
    if not entries:
        raise ValueError("feed contains no RSS items or Atom entries")
    source_ids = feed_source_ids(xml_payload, source_id_path, intake=intake)
    if len(source_ids) != len(entries):
        raise ValueError("feed_reconciliation_identity_count_mismatch")
    result: list[dict[str, Any]] = []
    for entry, source_id in zip(entries, source_ids):
        link = _child_text(entry, "link", "url")
        if not link:
            # Atom feeds can put a machine/API self link before the human
            # opportunity page. Prefer the standard alternate relation for
            # the row URL that downstream official-host reconciliation uses.
            # Keep a deterministic fallback for feeds that publish only one
            # link or use RSS-style elements.
            atom_links: list[tuple[str, str]] = []
            for child in entry:
                if _local(child.tag) == "link" and child.attrib.get("href"):
                    atom_links.append((child.attrib.get("rel", "alternate").casefold(),
                                       child.attrib["href"]))
            link = next((href for rel, href in atom_links if rel == "alternate"), "")
            if not link and atom_links:
                link = atom_links[0][1]
        result.append(normalize_opportunity({
            "Source": source,
            "SourceID": source_id,
            "Title": _child_text(entry, "title"),
            "URL": link,
            "Description": _child_text(entry, "description", "summary", "content"),
            "Deadline": _child_text(entry, "deadline", "closingdate", "closing-date"),
            "RetrievedUTC": retrieved_at,
        }, retrieved_at=retrieved_at))
    return result


def ingest_batches(batches: Iterable[dict[str, Any]], *, catalogue: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Admit complete opportunity observations only; isolate failed sources."""
    try:
        batch_iterator = iter(batches)
    except Exception:
        return {"records": [], "health": [{"source": "intake", "status": "failed", "count": 0,
                                              "error": "batches_not_iterable"}], "accepted": False}
    try:
        catalogue_rows = list(catalogue)
    except Exception:
        return {"records": [], "health": [{"source": "catalogue", "status": "failed", "count": 0,
                                              "error": "catalogue_not_iterable"}], "accepted": False}
    malformed_catalogue = any(not isinstance(row, dict) for row in catalogue_rows)
    # Do not let caller-provided catalogue rows shadow one another. The normal
    # catalogue loader rejects duplicates, but this boundary is also used by
    # imported/reviewed batches and must fail closed if handed an invalid
    # catalogue directly.
    grouped_catalogue: dict[str, list[dict[str, Any]]] = {}
    catalogue_errors: dict[int, str] = {}
    disabled_sources: set[str] = set()
    for row in catalogue_rows:
        if not isinstance(row, dict):
            continue
        row_error = _catalogue_row_error(row)
        if row_error:
            if row_error == "source_disabled" and isinstance(row.get("source_id"), str):
                disabled_sources.add(row["source_id"].strip())
                continue
            catalogue_errors[id(row)] = row_error
            continue
        source_id = row["source_id"].strip()
        grouped_catalogue.setdefault(source_id, []).append(row)
    duplicate_sources = {source_id for source_id, rows in grouped_catalogue.items() if len(rows) > 1}
    admitted = {source_id: rows[0] for source_id, rows in grouped_catalogue.items()
                if source_id not in duplicate_sources}
    by_source: dict[str, list[dict[str, Any]]] = {}
    seen_sources: set[str] = set()
    health: list[dict[str, Any]] = []
    iterator_failed = False

    def read_batches():
        nonlocal iterator_failed
        while True:
            try:
                yield next(batch_iterator)
            except StopIteration:
                return
            except Exception:
                # The failing batch cannot be attributed reliably to a
                # source; the outer snapshot is therefore not committable.
                iterator_failed = True
                return

    for batch in read_batches():
        if not isinstance(batch, dict):
            health.append({"source": "unknown", "status": "failed", "count": 0,
                           "error": "batch_not_object"})
            continue
        raw_source = batch.get("source")
        if not isinstance(raw_source, str) or not raw_source or raw_source != raw_source.strip():
            health.append({"source": "unknown", "status": "failed", "count": 0,
                           "error": "invalid_source_identity"})
            continue
        source = raw_source
        if source in seen_sources:
            # A source may supply only one complete snapshot per intake cycle.
            # Two individually complete batches can otherwise hide a truncated
            # or conflicting observation and make the result order dependent.
            by_source.pop(source, None)
            health = [item for item in health if item["source"] != source]
            health.append({"source": source, "status": "failed", "count": 0,
                           "error": "duplicate_source_batch"})
            continue
        seen_sources.add(source)
        try:
            if source in disabled_sources:
                raise ValueError("source_disabled")
            if malformed_catalogue:
                raise ValueError("catalogue_row_not_object")
            if catalogue_errors:
                raise ValueError("invalid_catalogue_row")
            if source in duplicate_sources:
                raise ValueError("duplicate_catalogue_source_id")
            contract = admitted.get(source)
            if not contract or contract.get("intake") not in {"rss", "atom", "api"}:
                raise ValueError("source_not_admitted")
            reconciliation = contract.get("reconciliation", {})
            if reconciliation.get("admission") != "opportunity" or reconciliation.get("entity") != "opportunity":
                raise ValueError("wrong_entity_kind")
            hosts = contract.get("official_row_hosts", [])
            if not hosts:
                raise ValueError("missing_official_row_hosts")
            pages = batch.get("pagination", {})
            expected = pages.get("total_pages") if isinstance(pages, dict) else None
            seen = pages.get("pages_received") if isinstance(pages, dict) else None
            if (not isinstance(expected, int) or isinstance(expected, bool) or expected < 1
                    # Python considers True == 1 and 1.0 == 1. Pagination
                    # receipts are protocol counters, so accepting either
                    # would let malformed adapter output satisfy completeness.
                    or not isinstance(seen, list)
                    or any(type(page) is not int for page in seen)
                    or seen != list(range(1, expected + 1))
                    or pages.get("complete") is not True):
                raise ValueError("incomplete_pagination")
            prior = batch.get("prior_observed_at")
            retrieved_at = batch.get("retrieved_at")
            if not isinstance(retrieved_at, str) or not retrieved_at.strip():
                raise ValueError("invalid_observation_time")
            try:
                retrieved_instant = parse_offset_instant(retrieved_at)
            except ValueError as exc:
                raise ValueError("invalid_observation_time") from exc
            if prior is not None and not isinstance(prior, str):
                raise ValueError("invalid_prior_observation_time")
            if prior:
                try:
                    prior_instant = parse_offset_instant(prior)
                except ValueError as exc:
                    raise ValueError("invalid_prior_observation_time") from exc
                if retrieved_instant.astimezone(timezone.utc) < prior_instant.astimezone(timezone.utc):
                    raise ValueError("older_observation")
            if "xml" in batch:
                if contract["intake"] not in {"rss", "atom"}:
                    raise ValueError("intake_mismatch")
                parsed = parse_feed(
                    batch["xml"], source=source, retrieved_at=batch["retrieved_at"],
                    source_id_path=contract["reconciliation"]["source_id_path"],
                    intake=contract["intake"],
                )
            else:
                if contract["intake"] != "api" or not isinstance(batch.get("records"), list):
                    raise ValueError("intake_mismatch")
                parsed = [normalize_opportunity(
                    _machine_source_record(row, source=source, retrieved_at=batch["retrieved_at"]),
                    retrieved_at=batch["retrieved_at"],
                )
                          for row in batch["records"]]
            if not parsed:
                raise ValueError("empty_observation_requires_separate_verification")
            keys: set[str] = set()
            for row in parsed:
                if (not row["SourceID"] or not row["Title"]
                        or not valid_official_url(row["URL"], hosts)
                        or (row["SourceRowURL"]
                            and not valid_official_url(row["SourceRowURL"], hosts))):
                    raise ValueError("invalid_identity_or_official_row_url")
                if row["RetrievedTimestampStatus"] != "valid":
                    raise ValueError("invalid_observation_time")
                if row["DeadlineRaw"] and row["DeadlinePrecision"] == "unknown":
                    raise ValueError("invalid_deadline")
                if row["OpportunityKey"] in keys:
                    raise ValueError("duplicate_opportunity_key")
                keys.add(row["OpportunityKey"])
            by_source[source] = parsed
            health.append({"source": source, "status": "succeeded", "count": len(parsed)})
        except (ET.ParseError, AttributeError, TypeError, ValueError, KeyError) as exc:
            health.append({"source": source, "status": "failed", "count": 0, "error": str(exc)})
    if iterator_failed:
        by_source.clear()
        health.append({"source": "intake", "status": "failed", "count": 0,
                       "error": "batch_iteration_failed"})
    records = [row for rows in by_source.values() for row in rows]
    return {"records": records, "health": health, "accepted": bool(records) and all(item["status"] == "succeeded" for item in health)}
