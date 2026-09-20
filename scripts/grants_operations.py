"""Fail-closed local operational checks for a future grants ingestion run."""
from __future__ import annotations

from typing import Any, Iterable


def evaluate_run(records: Iterable[dict[str, Any]], health: Iterable[dict[str, Any]], prior_records=None):
    records = list(records)
    health = list(health)
    keys = [row.get('OpportunityKey') for row in records]
    record_sources = {
        str(row.get('Source', '')).strip()
        for row in records
        if str(row.get('Source', '')).strip()
    }
    health_sources = {
        str(item.get('source', '')).strip()
        for item in health
        if str(item.get('source', '')).strip()
    }
    errors = []
    if not records:
        errors.append('empty_batch')
    if not health:
        errors.append('missing_source_health')
    if any(not key for key in keys):
        errors.append('missing_opportunity_key')
    if len(keys) != len(set(keys)):
        errors.append('duplicate_opportunity_key')
    if any(item.get('status') != 'succeeded' for item in health):
        errors.append('source_failure')
    if record_sources - health_sources:
        errors.append('unreported_source')
    accepted = not errors
    return {
        'status': 'accepted' if accepted else 'rejected',
        'errors': errors,
        'records': records if accepted else list(prior_records or []),
        'preserved_prior': bool(errors and prior_records),
    }
