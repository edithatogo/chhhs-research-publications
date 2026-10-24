"""Offline preparation oracle; supplied key parity never certifies native acceptance."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

STAGES = ('source', 'canonical', 'registry', 'model', 'full_export', 'monthly_export')
LINEAGE = ('generation_id', 'source_snapshot_id', 'identity_contract_sha256')


def sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def text(value):
    return isinstance(value, str) and bool(value) and value == value.strip()


def keyset(rows, allow_empty=False):
    if not isinstance(rows, list) or (not rows and not allow_empty):
        raise ValueError('Nonempty key rows required; empty generation needs separate qualification')
    keys = [row.get('key') for row in rows]
    if any(not text(key) for key in keys) or len(set(keys)) != len(keys):
        raise ValueError('Blank, padded or duplicate keys; never normalize or silently discard')
    return set(keys)


def reconcile(packet):
    if packet.get('schema_version') != 1 or any(not text(packet.get(k)) for k in LINEAGE):
        raise ValueError('Explicit correlated lineage required')
    if not re.fullmatch(r'[0-9a-f]{64}', packet['identity_contract_sha256']):
        raise ValueError('Identity contract digest required')
    period = packet.get('reporting_month')
    if not isinstance(period, str) or not re.fullmatch(r'\d{4}-(0[1-9]|1[0-2])', period):
        raise ValueError('Explicit valid reporting month required')
    stages = packet.get('stages', {})
    if not isinstance(stages, dict) or set(stages) - set(STAGES):
        raise ValueError('Unexpected stage')
    blockers, usable, fingerprints = [], {}, {}
    for name in STAGES:
        stage = stages.get(name)
        if stage is None:
            blockers.append(name + ': missing capture')
            continue
        fingerprints[name] = sha(stage)
        if any(stage.get(k) != packet[k] for k in LINEAGE):
            blockers.append(name + ': mixed generation/identity lineage')
            continue
        if stage.get('complete') is not True or stage.get('next_links') != []:
            blockers.append(name + ': incomplete pagination')
            continue
        if stage.get('data_kind') != 'native_readback':
            blockers.append(name + ': native readback not supplied')
            continue
        if (stage.get('terminal_status') != 'Succeeded' or not text(stage.get('operation_ref'))
                or not text(stage.get('evidence_ref')) or not text(stage.get('query_version'))):
            blockers.append(name + ': terminal/query/evidence correlation missing')
            continue
        if name in ('source', 'canonical') and stage.get('accepted_commit') is not True:
            blockers.append(name + ': accepted durable commit not supplied')
            continue
        if not isinstance(stage.get('artifact_sha256'), str) or not re.fullmatch(r'[0-9a-f]{64}', stage['artifact_sha256']):
            blockers.append(name + ': retained artifact fingerprint missing')
            continue
        rows = stage.get('rows')
        try:
            keys = keyset(rows, allow_empty=name == 'monthly_export')
        except (ValueError, AttributeError, TypeError) as exc:
            blockers.append(name + ': ' + str(exc))
            continue
        count = stage.get('independent_expected_count')
        if type(count) is not int or count != len(rows):
            blockers.append(name + ': independent count mismatch/missing')
            continue
        usable[name] = (stage, keys)
    differences = {}
    def compare(label, expected, actual):
        differences[label] = {'missing': sorted(expected-actual), 'unexpected': sorted(actual-expected)}
        if expected != actual:
            blockers.append(label + ': key sets differ')
    for name in ('full_export', 'monthly_export'):
        if name in usable:
            stage = usable[name][0]
            if 'model' in usable and stage.get('model_refresh_correlation') != usable['model'][0]['operation_ref']:
                blockers.append(name + ': wrong model refresh correlation')
            if not isinstance(stage.get('extraction_contract_sha256'), str) or not re.fullmatch(r'[0-9a-f]{64}', stage['extraction_contract_sha256']):
                blockers.append(name + ': extraction contract missing')
    if 'full_export' in usable and 'monthly_export' in usable:
        for field in ('query_version', 'extraction_contract_sha256', 'model_refresh_correlation'):
            if usable['full_export'][0].get(field) != usable['monthly_export'][0].get(field):
                blockers.append('full/monthly export: different ' + field)
    canonical = usable.get('canonical')
    if canonical:
        mappings = {}
        for row in canonical[0]['rows']:
            sources = row.get('source_keys')
            if not isinstance(sources, list) or not sources or any(not text(k) for k in sources):
                raise ValueError('Every canonical key requires explicit source identity evidence')
            if not text(row.get('identity_evidence_ref')):
                raise ValueError('Identity mappings require evidence, not title/DOI guesses')
            for source in sources:
                if source in mappings:
                    raise ValueError('Source identity maps more than once')
                mappings[source] = row['key']
        if 'source' in usable:
            compare('source_to_canonical_membership', usable['source'][1], set(mappings))
        for stage in ('registry', 'model', 'full_export'):
            if stage in usable:
                compare('canonical_to_'+stage, canonical[1], usable[stage][1])
        monthkeys, unknown = set(), []
        for row in canonical[0]['rows']:
            month = row.get('publication_month')
            if month in (None, ''):
                unknown.append(row['key'])
            elif not isinstance(month, str) or not re.fullmatch(r'\d{4}-(0[1-9]|1[0-2])', month):
                raise ValueError('Invalid publication month; preserve unknown dates explicitly')
            elif month == period:
                monthkeys.add(row['key'])
        if 'monthly_export' in usable:
            compare('canonical_month_to_monthly_export', monthkeys, usable['monthly_export'][1])
            if usable['monthly_export'][0].get('reporting_month') != period:
                blockers.append('monthly_export: wrong reporting month')
        # Full/monthly exported dates must agree with canonical dates, including unknowns.
        months = {r['key']: r.get('publication_month') or None for r in canonical[0]['rows']}
        for stage in ('model', 'full_export', 'monthly_export'):
            if stage in usable:
                bad = [r['key'] for r in usable[stage][0]['rows']
                       if r['key'] in months and r.get('publication_month', None) != months[r['key']]]
                if bad:
                    differences[stage+'_month_metadata'] = {'mismatched': sorted(bad)}
                    blockers.append(stage + ': date metadata differs')
    else:
        unknown = []
    return {'schema_version': 1, 'status': 'BLOCKED' if blockers else 'PASS_SUPPLIED_KEY_PARITY_ONLY',
            'generation_id': packet['generation_id'], 'reporting_month': period,
            'stage_fingerprints': fingerprints, 'counts': {k: len(v[1]) for k,v in usable.items()},
            'differences': differences, 'unknown_month_keys': unknown, 'blockers': blockers,
            'native_acceptance': False, 'operational_acceptance': False,
            'boundary': 'Offline supplied evidence comparison; verify authenticity, native lineage, metadata and preservation separately.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('packet', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        root = Path(__file__).resolve().parents[1]
        output = args.output.resolve()
        if not output.is_relative_to(root/'private/ops') or subprocess.run(
                ['git','check-ignore','-q','--',str(output)],cwd=root,check=False).returncode:
            raise ValueError('Detailed differences must remain in ignored checkout private/ops')
        result = reconcile(json.loads(args.packet.read_text()))
        with output.open('x') as stream:
            json.dump(result, stream, indent=2)
        print(result['status'] + ': native_acceptance=false; detailed result saved privately')
        return 1 if result['blockers'] else 0
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        parser.exit(2, f'Reconciliation failed: {exc}\n')


if __name__ == '__main__':
    raise SystemExit(main())
