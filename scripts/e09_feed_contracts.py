"""E09 collaborative-research-feed additive storage contracts (local only).

Phase 1 (E09.1) prework: fail-closed validators for the three additive record
types that live beside the authoritative publication/curator records —

* contribution records (non-authoritative until a curator decision),
* subscription preferences (opt-in cadence; identity-safe references only),
* delivery receipts (no-send first; uncertain outcomes stay explicit).

Rules shared with the grants contracts:

* exact field shapes — unknown or missing fields are rejected, never dropped;
* canonical identity text — no coercion, no whitespace padding, no trimmed
  variants silently becoming a different stable identity;
* real calendar dates in ``YYYY-MM-DD`` form and offset-aware RFC3339
  timestamps for instants;
* derived identity (thread id) must match exactly, never be recomputed
  implicitly into a different value;
* validated here is a local seam: no field flags these records as
  authoritative, and no actual Teams post, email send, schedule activation or
  tenant object change is performed or implied by this module.
"""

from __future__ import annotations

import re
from datetime import date, datetime
from typing import Any

CONTRIBUTION_FIELDS = {
    "contribution_id",
    "publication_key",
    "thread_id",
    "submitted_on",
    "contributor_id_kind",
    "contributor_urn",
    "identity_verification_ref",
    "evidence",
    "evidence_urls",
    "suggested_keywords",
    "status",
    "source_revision",
    "submitted_at_project_revision",
    "curator_decision_on",
    "curated_record_reference",
    "authoritative",
}

SUBSCRIPTION_FIELDS = {
    "subscription_id",
    "subscriber_urn",
    "cadence",
    "status",
    "enrolled_on",
    "revised_on",
    "revision",
    "contact_route",
    "delivery_authority_active",
    "delivery_authority_reference",
}

DELIVERY_RECEIPT_FIELDS = {
    "receipt_id",
    "publication_key",
    "thread_id",
    "trigger",
    "intended_outcome",
    "outcome",
    "discovered_on",
    "recorded_at",
    "delivery_authority_reference",
    "suppression_reason",
    "post_reference",
    "reconciliation_required",
    "revision",
}

CONTRIBUTION_ID_KINDS = {"anonymous", "declared", "authenticated"}
CONTRIBUTION_STATUSES = {
    "submitted", "curator_accepted", "curator_amended",
    "curator_rejected", "unresolved",
}
SUBSCRIPTION_CADENCES = {"weekly", "daily", "off"}
SUBSCRIPTION_STATUSES = {"active", "paused", "withdrawn"}
SUBSCRIPTION_ROUTES = {"authorised_list", "existing_digest_components"}
DELIVERY_TRIGGERS = {"first_discovery", "baseline", "catch_up", "revision_update"}
DELIVERY_INTENT_OUTCOMES = {"team_post", "email_edition", "no_send"}
DELIVERY_OUTCOMES = {"recorded_only", "suppressed_policy", "sent", "failed_uncertain"}

# Publications are referenced by their existing canonical registry SourceKey
# convention: ``{lowercase source}:{SourceID}``.  No new key family is minted
# here and no source family is admitted by these contracts.
_SOURCE_KEY_RE = re.compile(r"^[a-z0-9][a-z0-9-]{1,31}:[^|\s][^|]*$")

RFC3339_INSTANT = re.compile(
    r"^\d{4}-\d{2}-\d{2}T(?:[01]\d|2[0-3]):[0-5]\d:[0-5]\d"
    r"(?:\.\d+)?(?:Z|[+-](?:[01]\d|2[0-3]):[0-5]\d)$"
)


def _required_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be non-empty text")
    return value.strip()


def _required_identifier(value: Any, field: str) -> str:
    text = _required_text(value, field)
    if value != text:
        raise ValueError(f"{field} must not include surrounding whitespace")
    return text


def _full_iso_date(value: Any, field: str) -> date:
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise ValueError(f"{field} must use canonical YYYY-MM-DD date text")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{field} must be a real YYYY-MM-DD calendar date") from exc


def _parse_aware_instant(value: Any, field: str) -> datetime:
    if not isinstance(value, str) or not RFC3339_INSTANT.fullmatch(value):
        raise ValueError(f"{field} must be a timezone-aware RFC3339 timestamp")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00" if value.endswith("Z") else value)
    except ValueError as exc:
        raise ValueError(f"{field} must be a timezone-aware RFC3339 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field} must be a timezone-aware RFC3339 timestamp")
    return parsed


def _string_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list):
        raise ValueError(f"{field} must be a list")
    items: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            raise ValueError(f"{field}[{index}] must be non-empty text")
        if item != item.strip() or "|" in item:
            raise ValueError(f"{field}[{index}] must be unpadded text without the '|' separator")
        items.append(item)
    return items


def _positive_int(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"{field} must be an integer of at least 1")
    return value


def _boolean(value: Any, field: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"{field} must be a boolean")
    return value


def publication_source_key(value: Any, field: str = "publication_key") -> str:
    key = _required_identifier(value, field)
    if not _SOURCE_KEY_RE.fullmatch(key):
        raise ValueError(
            f"{field} must use the registry SourceKey form 'source:SourceID' "
            "with a lowercase source token and no '|' or whitespace"
        )
    return key


def stable_thread_id(publication_key: str) -> str:
    """Derive the additive thread identity beside the authoritative record."""
    return f"thread:{publication_source_key(publication_key, 'publication_key')}"


def _exact_fields(record: dict[str, Any], allowed: set[str], context: str) -> None:
    present = set(record)
    if present - allowed:
        raise ValueError(
            f"{context} has unsupported fields: {sorted(present - allowed)}"
        )


def _require_any(all_fields: set[str], record: dict[str, Any], context: str) -> dict[str, Any]:
    _exact_fields(record, all_fields, context)
    missing = all_fields - present_fields(record)
    if missing:
        raise ValueError(f"{context} is missing fields: {sorted(missing)}")
    return record


def present_fields(record: dict[str, Any]) -> set[str]:
    return set(record)


def validate_contribution_record(record: dict[str, Any]) -> dict[str, Any]:
    """Validate one non-authoritative contribution toward a publication."""
    if not isinstance(record, dict):
        raise ValueError("contribution record must be an object")
    context = "contribution record"
    _require_any(CONTRIBUTION_FIELDS, record, context)

    contribution_id = _required_identifier(record["contribution_id"], "contribution_id")
    publication_key = publication_source_key(record["publication_key"])
    thread_id = _required_identifier(record["thread_id"], "thread_id")
    if thread_id != stable_thread_id(publication_key):
        raise ValueError("thread_id must derive exactly from publication_key")

    submitted_on = _full_iso_date(record["submitted_on"], "submitted_on")
    contributor_id_kind = _required_identifier(record["contributor_id_kind"], "contributor_id_kind")
    if contributor_id_kind not in CONTRIBUTION_ID_KINDS:
        raise ValueError(f"contributor_id_kind must be one of {sorted(CONTRIBUTION_ID_KINDS)}")

    contributor_urn = record["contributor_urn"]
    identity_verification_ref = record["identity_verification_ref"]
    if contributor_id_kind == "anonymous":
        if contributor_urn is not None:
            raise ValueError("contributor_urn must be null for anonymous contributions")
        if identity_verification_ref is not None:
            raise ValueError("identity_verification_ref must be null for anonymous contributions")
    else:
        contributor_urn = _required_identifier(contributor_urn, "contributor_urn")
        if contributor_id_kind == "authenticated":
            if identity_verification_ref is None:
                raise ValueError(
                    "authenticated contributions need verified references")
            identity_verification_ref = _required_identifier(
                identity_verification_ref, "identity_verification_ref")
        elif identity_verification_ref is not None:
            raise ValueError("identity_verification_ref must be null unless the contributor is authenticated")

    _required_text(record["evidence"], "evidence")
    _string_list(record["evidence_urls"], "evidence_urls")
    for index, item in enumerate(_string_list(record["evidence_urls"], "evidence_urls")):
        if not item.startswith("https://"):
            raise ValueError(f"evidence_urls[{index}] must use HTTPS")
    _string_list(record["suggested_keywords"], "suggested_keywords")

    status = _required_identifier(record["status"], "status")
    if status not in CONTRIBUTION_STATUSES:
        raise ValueError(f"status must be one of {sorted(CONTRIBUTION_STATUSES)}")

    _positive_int(record["source_revision"], "source_revision")
    _positive_int(record["submitted_at_project_revision"], "submitted_at_project_revision")

    decided = status in {"curator_accepted", "curator_amended", "curator_rejected"}
    curator_decision_on = record["curator_decision_on"]
    curated_record_reference = record["curated_record_reference"]
    if decided:
        decision_date = _full_iso_date(curator_decision_on, "curator_decision_on")
        if decision_date < submitted_on:
            raise ValueError("curator_decision_on must not predate submitted_on")
        if status in {"curator_accepted", "curator_amended"}:
            curated_record_reference = _required_identifier(
                curated_record_reference, "curated_record_reference")
        elif curated_record_reference is not None:
            raise ValueError("curated_record_reference must be null for rejected contributions")
    else:
        if curator_decision_on is not None:
            raise ValueError("curator_decision_on must be null before a curator decision")
        if curated_record_reference is not None:
            raise ValueError("curated_record_reference must be null before a curator decision")

    if _boolean(record["authoritative"], "authoritative") is not False:
        raise ValueError(
            "authoritative must be false; contributions stay non-authoritative "
            "until a native curator decision record is implemented")
    return {**record, "contribution_id": contribution_id, "publication_key": publication_key,
            "thread_id": thread_id, "contributor_id_kind": contributor_id_kind,
            "status": status}


def validate_subscription_preference(record: dict[str, Any]) -> dict[str, Any]:
    """Validate one identity-safe opt-in subscription preference."""
    if not isinstance(record, dict):
        raise ValueError("subscription preference must be an object")
    context = "subscription preference"
    _require_any(SUBSCRIPTION_FIELDS, record, context)

    subscription_id = _required_identifier(record["subscription_id"], "subscription_id")
    subscriber_urn = _required_identifier(record["subscriber_urn"], "subscriber_urn")
    cadence = _required_identifier(record["cadence"], "cadence")
    if cadence not in SUBSCRIPTION_CADENCES:
        raise ValueError(f"cadence must be one of {sorted(SUBSCRIPTION_CADENCES)}")
    status = _required_identifier(record["status"], "status")
    if status not in SUBSCRIPTION_STATUSES:
        raise ValueError(f"status must be one of {sorted(SUBSCRIPTION_STATUSES)}")

    enrolled_on = _full_iso_date(record["enrolled_on"], "enrolled_on")
    revised_on = _full_iso_date(record["revised_on"], "revised_on")
    if revised_on < enrolled_on:
        raise ValueError("revised_on must not predate enrolled_on")
    _positive_int(record["revision"], "revision")

    route = _required_identifier(record["contact_route"], "contact_route")
    if route not in SUBSCRIPTION_ROUTES:
        raise ValueError(f"contact_route must be one of {sorted(SUBSCRIPTION_ROUTES)}")

    authority_active = _boolean(record["delivery_authority_active"], "delivery_authority_active")
    delivery_authority_reference = record["delivery_authority_reference"]
    if authority_active:
        delivery_authority_reference = _required_identifier(
            delivery_authority_reference, "delivery_authority_reference")
    elif delivery_authority_reference is not None:
        raise ValueError("delivery_authority_reference must be null without active delivery authority")
    return {**record, "subscription_id": subscription_id, "subscriber_urn": subscriber_urn,
            "cadence": cadence, "status": status, "contact_route": route,
            "delivery_authority_active": authority_active}


def validate_delivery_receipt(record: dict[str, Any]) -> dict[str, Any]:
    """Validate one additive thread delivery receipt (no-send first)."""
    if not isinstance(record, dict):
        raise ValueError("delivery receipt must be an object")
    context = "delivery receipt"
    _require_any(DELIVERY_RECEIPT_FIELDS, record, context)

    receipt_id = _required_identifier(record["receipt_id"], "receipt_id")
    publication_key = publication_source_key(record["publication_key"])
    thread_id = _required_identifier(record["thread_id"], "thread_id")
    if thread_id != stable_thread_id(publication_key):
        raise ValueError("thread_id must derive exactly from publication_key")

    trigger = _required_identifier(record["trigger"], "trigger")
    if trigger not in DELIVERY_TRIGGERS:
        raise ValueError(f"trigger must be one of {sorted(DELIVERY_TRIGGERS)}")
    intended_outcome = _required_identifier(record["intended_outcome"], "intended_outcome")
    if intended_outcome not in DELIVERY_INTENT_OUTCOMES:
        raise ValueError(f"intended_outcome must be one of {sorted(DELIVERY_INTENT_OUTCOMES)}")
    outcome = _required_identifier(record["outcome"], "outcome")
    if outcome not in DELIVERY_OUTCOMES:
        raise ValueError(f"outcome must be one of {sorted(DELIVERY_OUTCOMES)}")

    discovered_on = _full_iso_date(record["discovered_on"], "discovered_on")
    recorded_at = _parse_aware_instant(record["recorded_at"], "recorded_at")
    if recorded_at.date() < discovered_on:
        raise ValueError("recorded_at must not predate discovered_on")

    delivery_authority_reference = record["delivery_authority_reference"]
    post_reference = record["post_reference"]
    suppression_reason = record["suppression_reason"]
    if outcome == "sent":
        delivery_authority_reference = _required_identifier(
            delivery_authority_reference, "delivery_authority_reference")
        post_reference = _required_identifier(post_reference, "post_reference")
        if suppression_reason is not None:
            raise ValueError("suppression_reason must be null when the outcome is sent")
    elif outcome == "suppressed_policy":
        _required_identifier(record["suppression_reason"], "suppression_reason")
        if delivery_authority_reference is not None or post_reference is not None:
            raise ValueError("delivery/post references must be null for a suppressed outcome")
    else:
        if delivery_authority_reference is not None or post_reference is not None:
            raise ValueError("delivery/post references must be null without a sent outcome")
        if suppression_reason is not None:
            raise ValueError("suppression_reason must be null without a suppressed outcome")

    if intended_outcome == "no_send" and outcome == "sent":
        raise ValueError("a no-send intended outcome must not be recorded as sent")

    reconciliation_required = _boolean(record["reconciliation_required"], "reconciliation_required")
    if reconciliation_required != (outcome == "failed_uncertain"):
        raise ValueError("reconciliation_required must be true exactly for failed_uncertain outcomes")

    _positive_int(record["revision"], "revision")
    return {**record, "receipt_id": receipt_id, "publication_key": publication_key,
            "thread_id": thread_id, "trigger": trigger, "intended_outcome": intended_outcome,
            "outcome": outcome, "reconciliation_required": reconciliation_required}


_VALIDATORS = {
    "contribution": validate_contribution_record,
    "subscription": validate_subscription_preference,
    "delivery_receipt": validate_delivery_receipt,
}
_ID_FIELDS = {
    "contribution": "contribution_id",
    "subscription": "subscription_id",
    "delivery_receipt": "receipt_id",
}


def validate_contract_batch(kind: str, rows: Any) -> list[dict[str, Any]]:
    """Validate a list of same-kind records and reject duplicate stable ids."""
    validator = _VALIDATORS[kind]
    id_field = _ID_FIELDS[kind]
    if not isinstance(rows, list):
        raise ValueError(f"{kind} batch must be a list")
    validated: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, row in enumerate(rows):
        valid = validator(row)
        identifier = valid[id_field]
        if identifier in seen:
            raise ValueError(f"{kind} batch row {index} repeats {id_field}: {identifier!r}")
        seen.add(identifier)
        validated.append(valid)
    return validated
