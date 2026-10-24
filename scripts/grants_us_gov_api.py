"""Prepare one exact Grants.gov opportunity from retained official API evidence.

This is local preparation, not a collector or source admission. Full original
envelopes stay private. A selected source still needs catalogue qualification
and native acceptance; this module never supplies a reviewed decision.
"""
from __future__ import annotations

import argparse
import copy
from datetime import date
import hashlib
import json
from pathlib import Path
from typing import Any

try:
    from .grants_registry import normalize_opportunity, valid_official_url
    from .grants_deadline_schedule import attach_nih_schedule, NIH_SOURCE, NIH_ATTRIBUTION
except ImportError:
    from grants_registry import normalize_opportunity, valid_official_url
    from grants_deadline_schedule import attach_nih_schedule, NIH_SOURCE, NIH_ATTRIBUTION

SOURCE = NIH_SOURCE
FON = "PA-25-301"
OPPORTUNITY_ID = 357812
OFFICIAL_NOFO = "https://grants.nih.gov/grants/guide/pa-files/PA-25-301.html"
ATTRIBUTION = NIH_ATTRIBUTION


def _data(envelope: Any) -> dict[str, Any]:
    if (not isinstance(envelope, dict)
            or type(envelope.get("errorcode")) is not int
            or envelope["errorcode"] != 0
            or not isinstance(envelope.get("data"), dict)):
        raise ValueError("unsuccessful_or_malformed_api_envelope")
    return envelope["data"]


def semantic_detail(detail: dict[str, Any]) -> dict[str, Any]:
    """Compare applicant categories by their IDs while retaining raw order.

    The two live reads return the same ID/description categories in different
    orders. Only this named category collection is order independent; no other
    source field or collection is dropped from the replay comparison.
    """
    result = copy.deepcopy(detail)
    histories = result.get("opportunityHistoryDetails", [])
    if not isinstance(histories, list):
        raise ValueError("invalid_opportunity_history")
    for item in [result, *histories]:
        synopsis = item.get("synopsis") if isinstance(item, dict) else None
        if not isinstance(synopsis, dict):
            raise ValueError("invalid_synopsis")
        categories = synopsis.get("applicantTypes")
        if (not isinstance(categories, list) or not categories
                or any(not isinstance(category, dict)
                       or not isinstance(category.get("id"), str) or not category["id"]
                       or not isinstance(category.get("description"), str)
                       for category in categories)
                or len({category["id"] for category in categories}) != len(categories)):
            raise ValueError("invalid_applicant_categories")
        synopsis["applicantTypes"] = sorted(categories, key=lambda category: category["id"])
    return result


def prepare_snapshot(search: Any, detail: Any, replay_search: Any,
                     replay_detail: Any, *, retrieved_at: str) -> dict[str, Any]:
    """Fail closed unless both exact-FON reads account for one same record."""
    searches = [_data(search), _data(replay_search)]
    for result in searches:
        params, hits = result.get("searchParams"), result.get("oppHits")
        if (not isinstance(params, dict) or params.get("oppNum") != FON
                or set(str(params.get("oppStatuses", "")).split("|"))
                != {"forecasted", "posted", "closed", "archived"}
                or type(result.get("hitCount")) is not int or result["hitCount"] != 1
                or type(result.get("startRecord")) is not int or result["startRecord"] != 0
                or not isinstance(hits, list) or len(hits) != 1
                or not isinstance(hits[0], dict)
                or hits[0].get("id") != str(OPPORTUNITY_ID)
                or hits[0].get("number") != FON
                or hits[0].get("oppStatus") != "posted"
                or not isinstance(hits[0].get("closeDate"), str)):
            raise ValueError("incomplete_or_wrong_selected_query")
    current, replay = _data(detail), _data(replay_detail)
    if (semantic_detail(current) != semantic_detail(replay)
            or searches[0]["oppHits"] != searches[1]["oppHits"]):
        raise ValueError("selected_source_changed_between_reads")
    synopsis = current.get("synopsis")
    if (type(current.get("id")) is not int or current["id"] != OPPORTUNITY_ID
            or current.get("opportunityNumber") != FON
            or current.get("listed") != "L" or current.get("ost") != "POSTED"
            or current.get("docType") != "synopsis" or current.get("draftMode") != "N"
            or not isinstance(synopsis, dict)
            or type(synopsis.get("opportunityId")) is not int
            or synopsis["opportunityId"] != OPPORTUNITY_ID):
        raise ValueError("wrong_or_unpublished_opportunity_detail")
    history = current.get("opportunityHistoryDetails")
    if not isinstance(history, list) or any(
            not isinstance(item, dict) or item.get("opportunityId") != OPPORTUNITY_ID
            or item.get("opportunityNumber") != FON for item in history):
        raise ValueError("invalid_opportunity_history")
    link = synopsis.get("fundingDescLinkDesc")
    if link != OFFICIAL_NOFO or not valid_official_url(link, ["grants.nih.gov"]):
        raise ValueError("unexpected_official_nofo_link")
    closing = synopsis.get("responseDateStr")
    # Grants.gov exposes one search closeDate and detail responseDate for this
    # announcement. NIH's official NOFO shows multiple application due dates
    # within the FON's active period; do not project the announcement boundary
    # into the calendar Deadline. Retain nominal occurrences separately from
    # effective deadlines, which still need an applicant timezone and policy.
    if not isinstance(closing, str) or len(closing) != 19 or closing[10:] != "-00-00-00":
        raise ValueError("unsupported_source_closing_date")
    response_date = date.fromisoformat(closing[:10]).isoformat()
    search_close_date = searches[0]["oppHits"][0]["closeDate"]
    if search_close_date != date.fromisoformat(response_date).strftime("%m/%d/%Y"):
        raise ValueError("search_close_response_date_mismatch")
    fields = {"opportunityTitle": current.get("opportunityTitle"),
              "agencyName": synopsis.get("agencyName"),
              "synopsisDesc": synopsis.get("synopsisDesc"),
              "applicantEligibilityDesc": synopsis.get("applicantEligibilityDesc")}
    if any(not isinstance(value, str) or not value.strip() for value in fields.values()):
        raise ValueError("missing_source_text")
    row = {"Source": SOURCE, "SourceID": str(OPPORTUNITY_ID), "RoundID": FON,
           "Title": fields["opportunityTitle"], "Funder": fields["agencyName"],
           "URL": link, "Description": fields["synopsisDesc"],
           "Eligibility": fields["applicantEligibilityDesc"],
           "Deadline": "", "Status": "Open", "RetrievedUTC": retrieved_at}
    normalized = normalize_opportunity(row, retrieved_at=retrieved_at)
    if normalized["RetrievedTimestampStatus"] != "valid":
        raise ValueError("invalid_observation_timestamp")
    return {"source_admitted": False, "native_submission_allowed": False,
            "attribution": ATTRIBUTION,
            "scope": "One exact FON, all four source statuses, one complete page per read",
            "source_date_facts": {
                "search_close_date": search_close_date,
                "responseDateStr": closing,
                "response_date": response_date,
                "archiveDateStr": synopsis.get("archiveDateStr"),
                "mapped_to_actionable_deadline": False,
                "reason": "Grants.gov search closeDate and detail responseDate identify one announcement boundary, while the official NIH NOFO lists multiple application due dates under this FON. Retain the announcement boundary as source metadata and nominal application occurrences separately; do not show it as the next application deadline.",
                "schedule_source_url": OFFICIAL_NOFO,
            },
            "source_detail_sha256": hashlib.sha256(json.dumps(
                semantic_detail(current), sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
            "batch": {"source": SOURCE, "retrieved_at": retrieved_at,
                      "pagination": {"total_pages": 1, "pages_received": [1], "complete": True},
                      "records": [row]},
            "normalization_preview": [normalized]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("search", "detail", "replay-search", "replay-detail"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--retrieved-at", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--schedule", type=Path)
    parser.add_argument("--schedule-readback", type=Path)
    args = parser.parse_args()
    if bool(args.schedule) != bool(args.schedule_readback):
        parser.error("--schedule and --schedule-readback must be supplied together")
    private = Path(__file__).resolve().parents[1] / "private" / "ops"
    output = args.out.resolve()
    if not output.is_relative_to(private.resolve()) or output.exists():
        parser.error("--out must be a new file in ignored private/ops")
    result = prepare_snapshot(
        json.loads(args.search.read_text()), json.loads(args.detail.read_text()),
        json.loads(args.replay_search.read_text()), json.loads(args.replay_detail.read_text()),
        retrieved_at=args.retrieved_at)
    if args.schedule:
        result = attach_nih_schedule(result, args.schedule.read_bytes(),
                                     json.loads(args.schedule_readback.read_text()))
        result["normalization_preview"] = [normalize_opportunity(row, retrieved_at=args.retrieved_at)
                                           for row in result["batch"]["records"]]
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"prepared_rows": 1, "source_admitted": False,
                      "native_submission_allowed": False}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
