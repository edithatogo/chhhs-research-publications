"""Fail-closed local operational checks for a future grants ingestion run."""
from __future__ import annotations

from typing import Any, Iterable


def evaluate_run(records: Iterable[dict[str, Any]], health: Iterable[dict[str, Any]], prior_records=None):
    records = list(records)
    health = list(health)
    keys = [row.get('OpportunityKey') for row in records]
    record_source_values = [str(row.get('Source', '')).strip() for row in records]
    record_sources = {
        source for source in record_source_values if source
    }
    health_source_values = [str(item.get('source', '')).strip() for item in health]
    health_sources = {
        source for source in health_source_values if source
    }
    health_counts = {}
    errors = []
    if not records:
        errors.append('empty_batch')
    if not health:
        errors.append('missing_source_health')
    if any(not source for source in health_source_values):
        errors.append('missing_health_source')
    if len(health_source_values) != len(set(health_source_values)):
        errors.append('duplicate_health_source')
    for item in health:
        source = str(item.get('source', '')).strip()
        count = item.get('count')
        if type(count) is not int or count < 0:
            errors.append('invalid_health_count')
        elif source:
            health_counts[source] = count
    if any(not source for source in record_source_values):
        errors.append('missing_record_source')
    if any(not key for key in keys):
        errors.append('missing_opportunity_key')
    if len(keys) != len(set(keys)):
        errors.append('duplicate_opportunity_key')
    if any(item.get('status') != 'succeeded' for item in health):
        errors.append('source_failure')
    if record_sources - health_sources:
        errors.append('unreported_source')
    actual_counts = {}
    for source in record_source_values:
        if source:
            actual_counts[source] = actual_counts.get(source, 0) + 1
    if health_counts != actual_counts:
        errors.append('health_record_count_mismatch')
    accepted = not errors
    return {
        'status': 'accepted' if accepted else 'rejected',
        'errors': errors,
        'records': records if accepted else list(prior_records or []),
        'preserved_prior': bool(errors and prior_records),
    }
