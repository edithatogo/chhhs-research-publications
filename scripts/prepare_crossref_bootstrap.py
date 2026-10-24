"""Prepare unaccepted, provenance-preserving inputs for revised-scope migration.

Never writes a native progress/completion marker or relabels an original window.
Native terminal reconciliation and scope-specific coverage adoption are required.
"""
from __future__ import annotations
import hashlib
import json
from scripts.crossref_targeted_policy import normalize_doi, digest


def prepare(original_checkpoint, original_prefix, archive_inputs, queue, new_scope):
    if original_checkpoint.get('complete') is not True or original_checkpoint.get('source') != 'crossref':
        raise ValueError('Accepted last-good required')
    if new_scope['scope_sha256'] in {original_checkpoint['scope_sha256'], original_prefix['scope_sha256']}:
        raise ValueError('New scope requires a distinct fingerprint')
    if archive_inputs['source_run'] != original_prefix['source_run'] or archive_inputs['until'] != original_prefix['until']:
        raise ValueError('Frozen original run/cutoff differs')
    entries = {e['doi']: e for e in queue['entries']}
    accepted = {normalize_doi(e['doi']) for e in original_checkpoint['doi_lookups']}
    if None in accepted or not accepted <= entries.keys():
        raise ValueError('An accepted DOI would become unreachable')
    files = {f['file']: f for f in archive_inputs['files']}
    eligible = []
    for query in new_scope['hedge']['queries']:
        originals = [q for q in original_prefix['queries'] if q['key'] == query['key'] and q['anchor'] == query['anchor']]
        for q in originals:
            if (q.get('complete') is not True or q['expected'] != q['received'] or
                    q['expected'] != q['unique_dois']):
                raise ValueError('Incomplete original window cannot seed coverage')
            pointers = []
            for page in q['pages']:
                proof = files[page['file']]
                if proof['rows'] != page['rows'] or not proof['sha256'] or not proof['proof']['frozen_request_contract_equal']:
                    raise ValueError('Archive proof does not cover selected page')
                pointers.append({'file': page['file'], 'sha256': proof['sha256'], 'bytes': proof['bytes']})
            eligible.append({'key': q['key'], 'anchor': q['anchor'], 'original_window': q['query_window_key'],
                'original_filter': q['window_filter'], 'original_bounds': [q['created_from'], q['created_until']],
                'rows': q['received'], 'pages': pointers,
                'adoption': 'eligible evidence only; partition/reader equivalence and native summaries must be qualified'})
    return {'format': 'rims-crossref-targeted-bootstrap-inputs-v1', 'accepted': False,
        'complete': False, 'native_terminal_gate_satisfied': False,
        'original_run': original_prefix['source_run'], 'original_scope_sha256': original_prefix['scope_sha256'],
        'original_cutoff': original_prefix['until'], 'new_scope_sha256': new_scope['scope_sha256'],
        'last_good_scope_sha256': original_checkpoint['scope_sha256'], 'accepted_dois_preserved': len(accepted),
        'queue_dois': len(entries), 'queue_sha256': digest(queue), 'eligible_original_windows': eligible,
        'remaining_query_keys': [q['key'] for q in new_scope['hedge']['queries'] if q['key'] not in {e['key'] for e in eligible}],
        'required_gates': ['actual original terminal reconciliation', 'fresh native ID/ETag/hash checks',
            'new partition/reader coverage equivalence', 'primary-owned new-scope bootstrap',
            'exact native saved definition/settings readback', 'actual continuation and final manifest/replay']}


def stage_bundle(packet, original_prefix, archive_inputs, inventory, new_scope):
    """Create local create-only support-file payloads, not native state.

    Compatible full original query windows only. Never repartition a donor by
    relabelling it. Bounds and anchor must match the new19-window plan exactly.
    The baseline's initial progress pins the old cutoff, then acquires the17
    genuinely unresolved queries; later daily increments catch up from there.
    """
    from pathlib import PurePosixPath
    if packet.get('accepted') is not False or packet.get('native_terminal_gate_satisfied') is not False:
        raise ValueError('Unaccepted preparation packet required')
    parent = str(PurePosixPath(original_prefix['archive_folder']).parent)
    folder = parent + '/crossref-discovery-baseline-bootstrap-' + new_scope['scope_sha256']
    metadata = {f['name']: f for f in inventory['files']}
    proofs = {f['file']: f for f in archive_inputs['files']}
    original_queries = {q['key']: q for q in original_prefix['queries'] if q['created_from'] is None and q['created_until'] is None}
    summaries = []; files = []
    for query in new_scope['hedge']['queries']:
        old = original_queries.get(query['key'])
        if old is None: break  # Only a consecutive exact prefix is safe.
        if old['anchor'] != query['anchor'] or old['window_index'] != 0:
            raise ValueError('Donor query identity mismatch')
        expected_filter = 'until-created-date:' + original_prefix['until'].removesuffix('Z')
        if old['window_filter'] != expected_filter:
            raise ValueError('Donor cutoff/filter differs')
        q = json.loads(json.dumps(old)); q['archive_folder'] = original_prefix['archive_folder']; q['summary_folder'] = folder
        q['migration_proof'] = {'original_run': packet['original_run'], 'original_scope_sha256': packet['original_scope_sha256'], 'new_scope_sha256': new_scope['scope_sha256']}
        for page in q['pages']:
            m = metadata[page['file']]; proof = proofs[page['file']]
            if m['bytes'] != proof['bytes']:
                raise ValueError('Donor page length differs')
            page.update(id=m['id'], etag=m['etag'], bytes=m['bytes'], sha256=proof['sha256'], archive_folder=original_prefix['archive_folder'])
        summaries.append(q); files.append({'folder': folder, 'name': q['query_window_key'] + '-complete.json', 'content': q})
    files.insert(0, {'folder': folder, 'name': 'scope.json', 'content': new_scope})
    progress = {'format': 'rims-crossref-progress-baseline-v2', 'source': 'crossref',
        'accepted': False, 'complete': False, 'scope_sha256': new_scope['scope_sha256'],
        'until': original_prefix['until'], 'full_reconciliation': True, 'collection_lane': 'baseline',
        'previous_marker': '', 'queries': summaries, 'attempt_summaries': [],
        'pending_window': {}, 'changed_dois': [], 'planned_windows': len(new_scope['hedge']['queries'])}
    return {'status': 'LOCAL_CREATE_ONLY_BUNDLE_NATIVE_TERMINAL_AND_DRIFT_GATED',
        'accepted': False, 'native_writes': 0, 'support_files': files,
        'progress_folder': parent, 'progress_name': 'crossref-progress-baseline-bootstrap-' + new_scope['scope_sha256'] + '.json',
        'progress': progress, 'donor_windows': len(summaries),
        'preconditions': ['actual retained run terminal and reconciled', 'no existing conflicting new-scope baseline marker/progress',
            'fresh donor metadata/hash checks', 'new definitions exact native readback before runtime',
            'create-only support writes and exact native bytes readback before progress last']}
