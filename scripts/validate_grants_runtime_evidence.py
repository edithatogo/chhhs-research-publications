"""Check correlated runtime evidence; a local pass is not tenant acceptance."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def evaluate(packet: dict, evidence: dict) -> dict:
    errors = []
    def require(condition, message):
        if not condition:
            errors.append(message)

    require(evidence.get('packet_sha256') == hashlib.sha256(
        json.dumps(packet, sort_keys=True, separators=(',', ':')).encode()).hexdigest(),
        'packet fingerprint mismatch')
    target = evidence.get('target')
    require(isinstance(target, dict) and all(target.get(k) for k in
        ('environment', 'flow', 'site', 'list')), 'exact target missing')
    require(evidence.get('data_layer_accepted') is True, 'data-layer gate open')
    require(bool(evidence.get('run_authorization_reference')), 'run authority missing')
    require(bool(evidence.get('rollback_reference')), 'rollback evidence missing')
    require(evidence.get('final_flow_state') == 'Off', 'original Off state not restored')
    records = evidence.get('cases', [])
    expected = packet.get('cases', [])
    require([r.get('case') for r in records] == [r['case'] for r in expected],
            'cases missing, duplicated or out of order')
    previous = evidence.get('baseline_rows')
    require(isinstance(previous, list), 'complete baseline rows missing')
    run_ids = set()
    for case, record in zip(expected, records):
        name = case['case']
        require(record.get('target') == target, name + ': target mismatch')
        run_id = record.get('run_id')
        require(bool(run_id) and run_id not in run_ids, name + ': run correlation missing or reused')
        run_ids.add(run_id)
        require(bool(record.get('request_reference')) and bool(record.get('action_reference')),
                name + ': raw request/action references missing')
        require(record.get('submitted_rows') == case['rows'], name + ': submitted rows mismatch')
        require(record.get('run_status') == case['expected_run_status'], name + ': terminal status mismatch')
        require(record.get('write_count') == case['expected_write_count'], name + ': write count mismatch')
        if case.get('expected_diagnostic'):
            require(case['expected_diagnostic'] in record.get('diagnostics', []), name + ': diagnostic missing')
        before, after = record.get('before_rows'), record.get('after_rows')
        require(record.get('snapshots_complete') is True, name + ': incomplete snapshot')
        require(isinstance(before, list) and isinstance(after, list), name + ': row/version snapshots missing')
        require(before == previous, name + ': snapshot chain broken')
        if isinstance(before, list) and isinstance(after, list):
            valid_rows = all(isinstance(r, dict) and r.get('ID') is not None and
                        'versions' in r and isinstance(r['versions'], list) and r['versions']
                        for r in before + after)
            require(valid_rows, name + ': IDs/version history missing')
            if not valid_rows:
                previous = after
                continue
            require(len({r.get('ID') for r in after}) == len(after), name + ': duplicate item IDs')
            if case['expected_write_count'] == 0:
                require(before == after, name + ': rejected row changed data or versions')
            else:
                key = case['rows'][0]['OpportunityKey']
                old = [r for r in before if r.get('OpportunityKey') == key]
                new = [r for r in after if r.get('OpportunityKey') == key]
                require(len(old) == int(case['requires_fixture']), name + ': wrong prior fixture count')
                require(len(new) == 1, name + ': expected one keyed row')
                require([r for r in before if r.get('OpportunityKey') != key] ==
                        [r for r in after if r.get('OpportunityKey') != key], name + ': unrelated rows changed')
                if len(new) == 1:
                    for field in ('Title', 'Source', 'SourceID', 'EvidenceHash'):
                        require(new[0].get(field) == case['rows'][0][field], name + ': field mismatch ' + field)
                    for field in ('URL', 'SourceRowURL'):
                        value = new[0].get(field)
                        if isinstance(value, dict):
                            value = value.get('Url')
                        require(value == case['rows'][0].get(field), name + ': field mismatch ' + field)
                    for field in ('RetrievedUTC', 'RetrievedTimestampStatus', 'DeadlinePrecision',
                                  'DeadlineTimezone', 'DeadlineLocalTime', 'DeadlineUTCInstant',
                                  'DeadlineBrisbaneDate', 'DeadlineBrisbaneTime', 'DeadlineTemporalStatus'):
                        value = new[0].get(field)
                        expected_value = case['rows'][0].get(field)
                        if isinstance(value, dict) and field in ('RetrievedTimestampStatus',
                                                               'DeadlinePrecision', 'DeadlineTemporalStatus'):
                            value = value.get('Value')
                        # SharePoint serializes empty optional text fields as null.
                        if value is None and expected_value == '' and field in new[0]:
                            value = ''
                        require(value == expected_value, name + ': field mismatch ' + field)
                    if old:
                        require(new[0].get('ID') == old[0].get('ID'), name + ': item identity changed')
                        for field in ('ReviewStatus', 'ReviewNotes'):
                            require(new[0].get(field) == old[0].get(field), name + ': reviewer field changed')
                        require(new[0]['versions'][:len(old[0]['versions'])] == old[0]['versions'],
                                name + ': prior versions lost')
                    else:
                        for field, value in case.get('expected_create_review', {}).items():
                            require(new[0].get(field) == value, name + ': create review default mismatch')
        previous = after
    require(evidence.get('cleanup_rows') == evidence.get('baseline_rows') and
            evidence.get('cleanup_complete') is True, 'cleanup does not restore complete baseline')
    require(bool(evidence.get('cleanup_reference')), 'cleanup readback reference missing')
    return {'status': 'FAIL' if errors else 'PASS_RECORDED_EVIDENCE', 'errors': errors,
            'native_acceptance': False,
            'limitation': 'Checks supplied evidence only; raw native provenance, field types and remaining G03 gates require verification.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--packet', type=Path, required=True)
    parser.add_argument('--evidence', type=Path, required=True)
    args = parser.parse_args()
    private = Path(__file__).resolve().parents[1] / 'private' / 'ops'
    if not all(p.resolve().is_relative_to(private.resolve()) for p in (args.packet, args.evidence)):
        parser.error('Inputs must remain under private/ops/')
    result = evaluate(json.loads(args.packet.read_text()), json.loads(args.evidence.read_text()))
    print(json.dumps(result, indent=2))
    return int(bool(result['errors']))


if __name__ == '__main__':
    raise SystemExit(main())
