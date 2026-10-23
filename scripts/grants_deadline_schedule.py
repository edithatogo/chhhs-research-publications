"""Lossless, source-stated application schedules within one opportunity row.

The JSON envelope remains on its parent registry row, so one atomic upsert
preserves all occurrences. Calendar dates/UTC instants are never inferred.
"""
from __future__ import annotations

import copy
from datetime import date, time
import hashlib
import json
from typing import Any

SCHEDULE_VERSION = "grants-deadline-schedule-v1"
NIH_SOURCE = "us-grants-gov-nih-pa-25-301"
NIH_ATTRIBUTION = ("This product uses the Grants.gov API but is not endorsed or "
                   "certified by the U.S. Department of Health and Human Services.")
SCHEDULE_FIELDS = ("DeadlineScheduleJSON", "SourceDateFactsJSON", "SourceAttribution")
NIH_POLICY = "https://www.grants.nih.gov/grants-process/submit/submission-policies"


def require_source_schedule(record: dict) -> None:
    """Reject older incomplete NIH projections at the actual intake boundary."""
    if record.get("Source") != NIH_SOURCE:
        return
    if (record.get("SourceID") != "357812" or record.get("RoundID") != "PA-25-301"
            or any(not isinstance(record.get(f), str) or not record[f] for f in SCHEDULE_FIELDS)
            or record["SourceAttribution"] != NIH_ATTRIBUTION):
        raise ValueError("NIH intake requires its complete schedule, date facts and attribution")
    normalize_schedule(record["DeadlineScheduleJSON"], record)
    facts = json.loads(canonical_object(record["SourceDateFactsJSON"]))
    if not all(facts.get(k) for k in ("response_date", "responseDateStr", "archiveDateStr")):
        raise ValueError("NIH intake requires source announcement date facts")


def canonical_object(value: Any) -> str:
    if value is None or value == "":
        return ""
    if not isinstance(value, str):
        raise ValueError("source JSON must be text or null")
    def unique_pairs(pairs):
        result = {}
        for key, val in pairs:
            if key in result:
                raise ValueError("duplicate source JSON property")
            result[key] = val
        return result
    def invalid_constant(value):
        raise ValueError("nonfinite source JSON value")
    obj = json.loads(value, object_pairs_hook=unique_pairs, parse_constant=invalid_constant)
    if not isinstance(obj, dict):
        raise ValueError("source JSON must contain an object")
    result = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    if len(result) > 60000:
        raise ValueError("source JSON exceeds bounded plain-text field size")
    return result


def normalize_schedule(value: Any, record: dict) -> str:
    text = canonical_object(value)
    if not text:
        return text
    schedule = json.loads(text)
    if (schedule.get("schema_version") != SCHEDULE_VERSION
            or schedule.get("Source") != record.get("Source")
            or schedule.get("SourceID") != record.get("SourceID")
            or schedule.get("RoundID") != record.get("RoundID")):
        raise ValueError("deadline schedule parent identity mismatch")
    rows = schedule.get("occurrences")
    if (not isinstance(rows, list) or not 1 <= len(rows) <= 500
            or type(schedule.get("occurrence_count")) is not int
            or schedule["occurrence_count"] != len(rows)):
        raise ValueError("incomplete deadline schedule")
    ids = set()
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("invalid schedule occurrence")
        key = row.get("occurrence_candidate_id")
        if not isinstance(key, str) or not key or key != key.strip() or key in ids:
            raise ValueError("invalid or duplicate occurrence key")
        ids.add(key)
        if (row.get("parent_source_id") != record.get("Source")
                or row.get("parent_source_record_id") != record.get("SourceID")
                or row.get("parent_funding_opportunity_number") != record.get("RoundID")):
            raise ValueError("deadline occurrence parent identity mismatch")
        stated = row.get("due_date")
        if not isinstance(stated, str) or date.fromisoformat(stated).isoformat() != stated:
            raise ValueError("invalid source schedule date")
        if not isinstance(row.get("application_type"), str) or not row["application_type"].strip():
            raise ValueError("missing application type")
        stated_time = row.get("source_due_time")
        if (not isinstance(stated_time, str) or len(stated_time) != 8
                or time.fromisoformat(stated_time).isoformat() != stated_time
                or not isinstance(row.get("source_timezone_rule"), str)
                or not row["source_timezone_rule"].strip()):
            raise ValueError("invalid source schedule time rule")
        # This version represents source-stated dates only. Applicant-zone and
        # holiday/closure resolution requires a separately evidenced revision.
        if (row.get("iana_timezone") is not None or row.get("utc_instant") is not None
                or row.get("effective_due_date") is not None):
            raise ValueError("unqualified effective deadline or timezone")
    return text


def attach_nih_schedule(prepared: dict, candidate_bytes: bytes, readback: dict) -> dict:
    """Bind an independently retained, hash-pinned schedule to the API batch."""
    if hashlib.sha256(candidate_bytes).hexdigest() != readback.get("candidate_sha256"):
        raise ValueError("schedule candidate fingerprint mismatch")
    candidate = json.loads(candidate_bytes)
    occurrences = candidate.get("deadline_occurrences")
    if (not isinstance(occurrences, list)
            or len(occurrences) != readback.get("confirmed_occurrence_count")
            or [x.get("due_date") for x in occurrences] != readback.get("confirmed_occurrence_dates")):
        raise ValueError("schedule does not reconcile to source readback")
    result = copy.deepcopy(prepared)
    rows = result["batch"]["records"]
    if len(rows) != 1:
        raise ValueError("NIH attachment requires one exact parent opportunity")
    row = rows[0]
    envelope = {
        "schema_version": SCHEDULE_VERSION,
        **{name: row[name] for name in ("Source", "SourceID", "RoundID")},
        "source_url": candidate["source"]["official_nofo_url"],
        "observed_on": candidate["observed_on"],
        "as_of_date": candidate["as_of_date"],
        "coverage": "future source-stated dates as of as_of_date; not all historic cycles",
        "source_capture": candidate["source_capture"],
        "date_interpretation": "published nominal dates; effective deadline not calculated",
        "adjustment_policy_url": NIH_POLICY,
        "adjustment_policy": "weekends, federal holidays and DC federal office closures move submission to next business day",
        "occurrence_count": len(occurrences),
        "occurrences": occurrences,
    }
    row["DeadlineScheduleJSON"] = normalize_schedule(json.dumps(envelope), row)
    row["SourceDateFactsJSON"] = canonical_object(json.dumps(result["source_date_facts"]))
    row["SourceAttribution"] = result["attribution"]
    result["source_admitted"] = False
    result["native_submission_allowed"] = False
    return result
