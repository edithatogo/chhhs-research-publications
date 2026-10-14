"""Page accepted OpenAlex bytes for the existing archive and plan uncached DOIs.

Local preparation only: no provider requests, tenant writes or commit marker.
The archive owner must verify saved bytes and bind native generation evidence
before admitting these pages through the existing committed-history reader.
"""
import argparse
import copy
import hashlib
import json
import os
import re
from pathlib import Path

from enrich_openalex import clean_doi
from extend_openalex_native_bootstrap import validate
from prepare_openalex_retention import private_path


def encode(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode()


def build(prepared, records, batch_id, page_rows=2):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,95}', batch_id):
        raise ValueError('Safe fixed archive batch identity required')
    if type(page_rows) is not int or not 1 <= page_rows <= 100:
        raise ValueError('Bounded archive page size required')
    if not isinstance(records, list) or any(not isinstance(r, dict) for r in records):
        raise ValueError('Frozen canonical record list required')
    retained_dois = validate(prepared)
    scope = {doi.casefold() for row in records if (doi := clean_doi(row.get('DOI')))}
    if not retained_dois <= scope:
        raise ValueError('Retained DOI outside canonical source scope')
    outcomes = prepared['attempt_statuses']
    attempted = [s['RequestedDOI'] for s in outcomes]
    if len(attempted) != len(set(attempted)) or not set(attempted) <= scope:
        raise ValueError('Duplicate or foreign provider outcomes')
    successes = {s['RequestedDOI'] for s in outcomes if s['Status'] == 'success'}
    not_found = {s['RequestedDOI'] for s in outcomes if s['Status'] == 'not_found'}
    if successes != retained_dois or successes | not_found != set(attempted):
        raise ValueError('Only complete success/not-found outcomes can stage')
    chunks = sorted(prepared['chunks'], key=lambda r: (r['OpenAlexWorkID'], r['ChunkIndex']))
    files = {}
    index = []
    for offset in range(0, len(chunks), page_rows):
        rows = [{f'[{k}]': v for k, v in r.items()} for r in chunks[offset:offset + page_rows]]
        name = f'uncommitted-{batch_id}-OpenAlexMetadataChunks-{len(index)}.json'
        raw = encode(rows)
        files[name] = raw
        index.append({'name': name, 'rows': len(rows), 'bytes': len(raw),
                      'sha256': hashlib.sha256(raw).hexdigest()})
    remaining = sorted(scope - set(attempted))
    receipt = {
        'kind': 'openalex_archive_stage_v1', 'batch_id': batch_id,
        'prepared_sha256': hashlib.sha256(encode(prepared)).hexdigest(),
        'canonical_records_sha256': hashlib.sha256(encode(records)).hexdigest(),
        'source_spec': {'Source': 'OpenAlex', 'ChunkTable': 'OpenAlexMetadataChunks',
                        'KeyColumn': 'OpenAlexWorkID', 'PageCount': len(index),
                        'ExpectedRecords': len(prepared['expected_keys']),
                        'ExpectedKeys': sorted(prepared['expected_keys'])},
        'files': index, 'attempt_statuses': outcomes,
        'coverage': {'canonical_records': len(records), 'distinct_dois': len(scope),
                     'retained_successes': len(successes), 'not_found': len(not_found),
                     'not_requested': len(remaining)},
        'remaining_doi_batches': [remaining[i:i + 50] for i in range(0, len(remaining), 50)],
        'native_storage_verified': False, 'accepted_commit': False,
        'commit_marker_emitted': False,
        'integration': 'Use existing archive writer and commit-last readback gates; '
                       'retain original observation times/input hashes, other source pages and '
                       'canonical membership. Native owner binds generation and rollback.',
    }
    return files, receipt


def build_stage_fragment(native_flow, files, receipt):
    """Reuse exact archive connector actions, preserving required trigger input.

    The owning integrator supplies the generation/manifest checks and connects
    the commit-last action only after Require_OpenAlex_archive_persisted. This
    fragment cannot create or overwrite a commit marker.
    """
    definition = native_flow['properties']['definition']
    trigger = definition['triggers'].get('manual', {})
    if 'text' not in trigger.get('inputs', {}).get('schema', {}).get('required', []):
        raise ValueError('Existing validated-manifest trigger required')
    found = {}
    def visit(node):
        if isinstance(node, dict):
            inputs = node.get('inputs')
            host = inputs.get('host', {}) if isinstance(inputs, dict) else {}
            operation = host.get('operationId')
            if operation in ('GetFileContentByPath', 'CreateFile'):
                if host.get('connectionName') != 'shared_onedriveforbusiness':
                    raise ValueError('Existing archive OneDrive connection required')
                found.setdefault(operation, copy.deepcopy(node))
            for value in node.values():
                visit(value)
        elif isinstance(node, list):
            for value in node:
                visit(value)
    visit(definition['actions'])
    read, write = found['GetFileContentByPath'], found['CreateFile']
    folder = write['inputs']['parameters']['folderPath']
    if not folder.endswith('/01 Source archive'):
        raise ValueError('Exact approved archive folder required')
    expected_files = {entry['name'] for entry in receipt['files']}
    if set(files) != expected_files or receipt['accepted_commit'] is not False:
        raise ValueError('Complete uncommitted page package required')
    items = []
    for entry in receipt['files']:
        raw = files[entry['name']]
        if len(raw) != entry['bytes'] or hashlib.sha256(raw).hexdigest() != entry['sha256']:
            raise ValueError('Archive page fingerprint drift')
        items.append({'name': entry['name'], 'content': raw.decode('utf-8')})
    read['inputs']['parameters']['path'] = "@concat('" + folder.replace("'", "''") + "/',items('OpenAlex_Archive_Pages')['name'])"
    read['runAfter'] = {}
    write['inputs']['parameters'].update(name="@items('OpenAlex_Archive_Pages')['name']",
                                          body="@items('OpenAlex_Archive_Pages')['content']")
    write['runAfter'] = {'Require_OpenAlex_page_absent': ['Succeeded']}
    readback = copy.deepcopy(read)
    readback['runAfter'] = {'OpenAlex_Page_Exists': ['Succeeded']}
    nested = {
        'OpenAlex_Page_Existing': read,
        'OpenAlex_Page_Exists': {
            'type': 'If', 'expression': "@equals(outputs('OpenAlex_Page_Existing')?['statusCode'],200)",
            'runAfter': {'OpenAlex_Page_Existing': ['Succeeded', 'Failed']},
            'actions': {}, 'else': {'actions': {
                'Require_OpenAlex_page_absent': {'type': 'Compose', 'runAfter': {},
                    'inputs': "@if(equals(outputs('OpenAlex_Page_Existing')?['statusCode'],404),'ABSENT',int('ARCHIVE_READ_FAILED'))"},
                'OpenAlex_Page_Write': write}}},
        'OpenAlex_Page_Readback': readback,
        'Require_OpenAlex_page_exact': {'type': 'Compose',
            'runAfter': {'OpenAlex_Page_Readback': ['Succeeded']},
            'inputs': "@if(equals(base64ToString(body('OpenAlex_Page_Readback')['$content']),items('OpenAlex_Archive_Pages')['content']),'VERIFIED',int('ARCHIVE_CONFLICT'))"},
    }
    return {'kind': 'openalex_archive_persistence_fragment_v1',
            'batch_id': receipt['batch_id'], 'source_spec': receipt['source_spec'],
            'actions': {
                'OpenAlex_Archive_Pages': {'type': 'Foreach', 'foreach': items,
                    'runAfter': {'Require_OpenAlex_generation': ['Succeeded']},
                    'runtimeConfiguration': {'concurrency': {'repetitions': 1}},
                    'actions': nested},
                'Require_OpenAlex_archive_persisted': {'type': 'Compose',
                    'runAfter': {'OpenAlex_Archive_Pages': ['Succeeded']},
                    'inputs': 'Every complete raw OpenAlex page has exact stored readback.'}},
            'marker_run_after': {'Require_OpenAlex_archive_persisted': ['Succeeded']},
            'required_existing_input': 'text', 'commit_marker_emitted': False,
            'native_written': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--private-root', required=True, type=Path)
    parser.add_argument('--prepared', required=True)
    parser.add_argument('--records', required=True)
    parser.add_argument('--output-directory', required=True)
    parser.add_argument('--batch-id', required=True)
    args = parser.parse_args()
    root = args.private_root.resolve()
    if root.name != 'ops' or root.parent.name != 'private' or not root.is_dir():
        raise ValueError('Existing ignored private/ops directory required')
    source, records, output = [private_path(v, root) for v in
                              (args.prepared, args.records, args.output_directory)]
    source_raw, records_raw = source.read_bytes(), records.read_bytes()
    files, receipt = build(json.loads(source_raw), json.loads(records_raw), args.batch_id)
    receipt['prepared_file_sha256'] = hashlib.sha256(source_raw).hexdigest()
    receipt['canonical_file_sha256'] = hashlib.sha256(records_raw).hexdigest()
    if source.read_bytes() != source_raw or records.read_bytes() != records_raw:
        raise ValueError('Frozen source drift before output')
    output.mkdir(mode=0o700)
    files['stage-receipt-private.json'] = encode(receipt)
    for name, raw in files.items():
        with os.fdopen(os.open(output / name, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), 'wb') as stream:
            stream.write(raw)
    print(json.dumps({'status': 'prepared_uncommitted', 'files': len(files) - 1,
                      'coverage': receipt['coverage'], 'native_storage_verified': False}))


if __name__ == '__main__':
    main()
