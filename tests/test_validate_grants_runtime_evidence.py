import pytest
import unittest
from pathlib import Path

# Skip entire module if private/ops evidence files not present
ROOT = Path(__file__).resolve().parents[1]
PRIVATE_OPS_ROOT = ROOT / "private" / "ops"
REQUIRED_EVIDENCE_FILES = [
    "2026-09-28-arc-awards-two-pass-keyset-snapshot-private.json",
    "2026-09-28-grants-finder-contribution-api-reconciliation-private.json",
    "2026-10-07-g02-arc-two-date-row-reconciliation-private.json",
    "2026-10-23-g02-qgip-official-resource-recheck/full-snapshot.json",
    "2026-10-23-g02-qgip-official-resource-recheck/snapshot-comparison.json",
]
if not all((PRIVATE_OPS_ROOT / f).exists() for f in REQUIRED_EVIDENCE_FILES):
    raise unittest.SkipTest("private/ops evidence files not present; skipping tests")

import copy
import hashlib
import json

import pytest
import unittest

from scripts.build_grants_runtime_cases import build_cases
from scripts.validate_grants_runtime_evidence import evaluate


def fixture():
    packet = build_cases('2026-10-05T00:00:00Z')
    target = dict(environment='fixture', flow='fixture', site='fixture', list='fixture')
    evidence = dict(packet_sha256=hashlib.sha256(json.dumps(packet, sort_keys=True,
        separators=(',', ':')).encode()).hexdigest(), target=target,
        data_layer_accepted=True, run_authorization_reference='fixture-only',
        rollback_reference='fixture-only', final_flow_state='Off', baseline_rows=[],
        cleanup_rows=[], cleanup_complete=True, cleanup_reference='fixture-only', cases=[])
    rows = []
    for i, case in enumerate(packet['cases']):
        before = copy.deepcopy(rows)
        if case['expected_write_count']:
            payload = case['rows'][0]
            existing = next((r for r in rows if r['OpportunityKey'] == payload['OpportunityKey']), None)
            if existing:
                existing.update({k: v for k, v in payload.items()
                                 if k not in ('ReviewStatus', 'ReviewNotes')})
                existing['versions'].append({'version': str(i + 1)})
            else:
                created = dict(payload, ID=len(rows) + 1, versions=[{'version': str(i + 1)}])
                created.update(case['expected_create_review'])
                rows.append(created)
        evidence['cases'].append(dict(case=case['case'], target=target, run_id=str(i),
            request_reference='fixture-only', action_reference='fixture-only',
            submitted_rows=case['rows'], run_status=case['expected_run_status'],
            write_count=case['expected_write_count'], diagnostics=[case['expected_diagnostic']],
            snapshots_complete=True, before_rows=before, after_rows=copy.deepcopy(rows)))
    return packet, evidence


def test_complete_synthetic_evidence_passes_without_claiming_native_acceptance():
    packet, evidence = fixture()
    result = evaluate(packet, evidence)
    assert result['status'] == 'PASS_RECORDED_EVIDENCE'
    assert result['errors'] == []
    assert result['native_acceptance'] is False


@pytest.mark.parametrize('field,value,message', [
    ('data_layer_accepted', False, 'data-layer gate open'),
    ('final_flow_state', 'On', 'original Off state not restored'),
    ('cleanup_complete', False, 'cleanup does not restore complete baseline'),
    ('packet_sha256', 'wrong', 'packet fingerprint mismatch'),
])
def test_execution_and_cleanup_gates_fail_closed(field, value, message):
    packet, evidence = fixture()
    evidence[field] = value
    assert message in evaluate(packet, evidence)['errors']


def test_rejection_cannot_hide_version_only_write():
    packet, evidence = fixture()
    evidence['cases'][3]['after_rows'][0]['versions'].append({'version': 'unintended'})
    assert any('rejected row changed data or versions' in e for e in evaluate(packet, evidence)['errors'])


def test_missing_case_and_reused_run_are_rejected():
    packet, evidence = fixture()
    evidence['cases'][1]['run_id'] = evidence['cases'][0]['run_id']
    evidence['cases'].pop()
    errors = evaluate(packet, evidence)['errors']
    assert 'cases missing, duplicated or out of order' in errors
    assert any('run correlation missing or reused' in e for e in errors)


def test_reviewer_change_and_lost_history_are_rejected():
    packet, evidence = fixture()
    row = evidence['cases'][2]['after_rows'][0]
    row['ReviewNotes'] = 'overwritten'
    row['versions'] = [{'version': 'replacement'}]
    errors = evaluate(packet, evidence)['errors']
    assert any('reviewer field changed' in e for e in errors)
    assert any('prior versions lost' in e for e in errors)


def test_missing_version_history_is_failure_not_a_crash():
    packet, evidence = fixture()
    del evidence['cases'][1]['after_rows'][0]['versions']
    assert any('IDs/version history missing' in e for e in evaluate(packet, evidence)['errors'])


def test_sharepoint_url_object_shape_and_provenance_loss():
    packet, evidence = fixture()
    for record in evidence['cases']:
        for group in ('before_rows', 'after_rows'):
            for row in record[group]:
                for field in ('URL', 'SourceRowURL'):
                    row[field] = {'Url': row[field], 'Description': 'synthetic fixture'}
    assert evaluate(packet, evidence)['errors'] == []
    evidence['cases'][0]['after_rows'][0]['SourceRowURL']['Url'] = 'https://example.invalid/wrong'
    assert any('field mismatch SourceRowURL' in e for e in evaluate(packet, evidence)['errors'])


@pytest.mark.parametrize('field', ['RetrievedUTC', 'RetrievedTimestampStatus', 'DeadlinePrecision',
    'DeadlineTimezone', 'DeadlineLocalTime', 'DeadlineUTCInstant', 'DeadlineBrisbaneDate',
    'DeadlineBrisbaneTime', 'DeadlineTemporalStatus'])
def test_observation_and_deadline_mapping_loss_rejected(field):
    packet, evidence = fixture()
    del evidence['cases'][0]['after_rows'][0][field]
    assert any('field mismatch ' + field in e for e in evaluate(packet, evidence)['errors'])


def test_native_empty_text_and_choice_values_accepted():
    packet, evidence = fixture()
    for record in evidence['cases']:
        for group in ('before_rows', 'after_rows'):
            for row in record[group]:
                for field in ('DeadlineTimezone', 'DeadlineLocalTime', 'DeadlineUTCInstant',
                              'DeadlineBrisbaneDate', 'DeadlineBrisbaneTime'):
                    if row[field] == '':
                        row[field] = None
                for field in ('RetrievedTimestampStatus', 'DeadlinePrecision', 'DeadlineTemporalStatus'):
                    row[field] = {'Value': row[field]}
    assert evaluate(packet, evidence)['errors'] == []
    evidence['cases'][0]['after_rows'][0]['DeadlineTemporalStatus'] = {'Value': 'invented'}
    assert any('field mismatch DeadlineTemporalStatus' in e for e in evaluate(packet, evidence)['errors'])
