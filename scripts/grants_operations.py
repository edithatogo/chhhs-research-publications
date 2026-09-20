"""Fail-closed local operational checks for a future grants ingestion run."""
from __future__ import annotations

from typing import Any, Iterable


def evaluate_run(records: Iterable[dict[str, Any]], health: Iterable[dict[str, Any]], prior_records=None):
    records = list(records)
    health = list(health)
    invalid_record_objects = any(not isinstance(row, dict) for row in records)
    invalid_health_objects = any(not isinstance(item, dict) for item in health)
    safe_records = [row if isinstance(row, dict) else {} for row in records]
    safe_health = [item if isinstance(item, dict) else {} for item in health]
    keys = [row.get('OpportunityKey') for row in safe_records]
    record_source_values = [row.get('Source').strip() if isinstance(row.get('Source'), str) else '' for row in safe_records]
    record_sources = {
        source for source in record_source_values if source
    }
    health_source_values = [item.get('source').strip() if isinstance(item.get('source'), str) else '' for item in safe_health]
    health_sources = {
        source for source in health_source_values if source
    }
    health_counts = {}
    errors = []
    if invalid_record_objects:
        errors.append('invalid_record_object')
    if invalid_health_objects:
        errors.append('invalid_health_object')
    if not records:
        errors.append('empty_batch')
    if not health:
        errors.append('missing_source_health')
    if any(not isinstance(item.get('source'), str) for item in safe_health):
        errors.append('invalid_health_source')
    if any(not source for source in health_source_values):
        errors.append('missing_health_source')
    if len(health_source_values) != len(set(health_source_values)):
        errors.append('duplicate_health_source')
    for item in safe_health:
        source = item.get('source').strip() if isinstance(item.get('source'), str) else ''
        count = item.get('count')
        if type(count) is not int or count < 0:
            errors.append('invalid_health_count')
        elif source:
            health_counts[source] = count
    if any(not isinstance(row.get('Source'), str) for row in safe_records):
        errors.append('invalid_record_source')
    if any(not source.strip() for source in record_source_values):
        errors.append('missing_record_source')
    if any(not isinstance(key, str) for key in keys):
        errors.append('invalid_opportunity_key')
    if any(isinstance(key, str) and not key.strip() for key in keys):
        errors.append('missing_opportunity_key')
    comparable_keys = [key for key in keys if isinstance(key, str)]
    if len(comparable_keys) != len(set(comparable_keys)):
        errors.append('duplicate_opportunity_key')
    if any(item.get('status') != 'succeeded' for item in safe_health):
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
