"""Verify one scheduled acquisition's observation clocks and actual HTTP receipts.

Fresh observation does not imply a changed provider record or live register/model.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime


def timestamp(value: str) -> datetime:
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None:
        raise ValueError("timezone_required")
    return result


def verify(manifest: dict, run: dict, repetitions: dict, http_outputs: list[dict],
           *, checked_at: str, max_age_seconds: int = 300) -> dict:
    prop = run["properties"]
    trigger = prop["trigger"]
    start, end = timestamp(prop["startTime"]), timestamp(prop["endTime"])
    observed, checked = timestamp(manifest["observed_utc"]), timestamp(checked_at)
    scheduled = timestamp(trigger["scheduledTime"])
    if (prop["status"] != "Succeeded" or manifest["run"] != run["name"]
            or trigger["name"] != "Recurrence" or trigger["status"] != "Succeeded"
            or trigger["originHistoryName"] != run["name"]
            or abs((start - scheduled).total_seconds()) > 30
            or not start <= observed <= end):
        raise ValueError("not_a_correlated_scheduled_observation")
    age = (checked - observed).total_seconds()
    if type(max_age_seconds) is not int or max_age_seconds < 1 or not 0 <= age <= max_age_seconds:
        raise ValueError("stale_or_future_observation")
    entries = repetitions.get("repetitions", [])
    if (repetitions.get("action") != "Fetch_response"
            or repetitions.get("truncated") is not False or repetitions.get("count") != 4
            or len(entries) != 4 or len(http_outputs) != 4
            or len(manifest.get("responses", [])) != 4):
        raise ValueError("incomplete_http_execution_evidence")
    receipts = []
    for index, (entry, output, archived) in enumerate(zip(entries, http_outputs, manifest["responses"])):
        action = entry["properties"]
        if (entry.get("runName") != run["name"] or entry.get("actionName") != "Fetch_response"
                or action["status"] != "Succeeded"
                or action["repetitionIndexes"][0]["itemIndex"] != index
                or not start <= timestamp(action["startTime"]) <= timestamp(action["endTime"]) <= end
                or output.get("statusCode") != 200 or output.get("body") != archived["response"]):
            raise ValueError("http_execution_or_archive_mismatch")
        headers = {k.lower(): v for k, v in output.get("headers", {}).items()}
        if not headers.get("date"):
            raise ValueError("provider_response_date_missing")
        provider_date = parsedate_to_datetime(headers["date"])
        if (provider_date.tzinfo is None
                or not start - timedelta(seconds=30) <= provider_date <= end + timedelta(seconds=30)):
            raise ValueError("provider_response_clock_outside_run")
        receipts.append({"role": archived["role"], "provider_http_date": headers["date"],
                         "http_start_utc": action["startTime"], "http_end_utc": action["endTime"]})
    detail = manifest["responses"][1]["response"]["data"]
    return {"scheduled_observation_verified": True, "run": run["name"],
            "scheduled_utc": trigger["scheduledTime"], "observed_utc": manifest["observed_utc"],
            "checked_at_utc": checked_at, "observation_age_seconds": age,
            "freshness_bound_seconds": max_age_seconds, "http_receipts": receipts,
            "provider_last_updated_raw": detail.get("synopsis", {}).get("lastUpdatedDate"),
            "provider_update_timezone": "unknown unless explicitly supplied by source",
            "source_change_inferred": False, "register_freshness_qualified": False,
            "model_freshness_qualified": False}
