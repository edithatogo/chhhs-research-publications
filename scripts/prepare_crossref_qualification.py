"""Derive an isolated, manual, two-request qualification; never deploy or run."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
from pathlib import Path

from scripts.crossref_definition import fingerprint


def cards(actions):
    for name, card in actions.items():
        yield name, card
        yield from cards(card.get('actions', {}))
        yield from cards(card.get('else', {}).get('actions', {}))


def prepare(pair, expected_sha256):
    if fingerprint(pair) != expected_sha256:
        raise ValueError('Paired candidate fingerprint mismatch')
    result = copy.deepcopy(pair['baseline_worker'])
    properties = result['properties']
    properties['displayName'] = 'CHHHS RIMS | Crossref isolated batch qualification v1'
    properties['state'] = 'Stopped'
    definition = properties['definition']
    definition['triggers'] = {'manual': {
        'type': 'Request', 'kind': 'Button',
        'inputs': {'schema': {'type': 'object', 'properties': {}, 'required': []}},
        'runtimeConfiguration': {'concurrency': {'runs': 1}}}}
    actions = definition['actions']
    scope = actions['B_Scope']['inputs']
    query = next(q for q in scope['hedge']['queries'] if q['key'] == 'yarrabah')
    parent_scope = scope['scope_sha256']
    scope['hedge']['queries'] = [query]
    scope['qualification'] = {'purpose': 'isolated-batch-v1',
        'parent_scope_sha256': parent_scope, 'accepted': False,
        'provider_request_cap': 2, 'query_key': 'yarrabah'}
    scope.pop('scope_sha256')
    scope['scope_sha256'] = fingerprint(scope)
    branch = actions['B_Baseline_due']['actions']
    old = branch['B_Batch_finalize']
    branch['B_Batch_finalize'] = {'type': 'Compose', 'runAfter': old['runAfter'],
        'inputs': {'qualification_only': True, 'accepted': False,
                   'complete': False, 'verified_windows': "@length(variables('B_Queries'))"}}
    failure = next(c for n, c in cards(branch) if n == 'B_Failure_receipt')
    failure['inputs'] = {
        'schema_version': 1, 'source': 'crossref', 'qualification_only': True,
        'complete': False, 'accepted': False,
        'run_id': "@workflow()?['run']?['name']",
        'scope_sha256': "@outputs('B_Scope')?['scope_sha256']",
        'cutoff': "@outputs('B_Generation_cutoff')",
        'acquisition_failed': "@variables('B_AcquisitionFailed')",
        'verified_windows': "@length(variables('B_Queries'))",
        'progress_verification_status': "@actions('B_Batch_verify_progress')?['status']",
        'qualification_result_status': "@actions('B_Batch_finalize')?['status']"}
    attempt = next(c for n, c in cards(branch) if n == 'B_Until_query_attempt')
    attempt['expression'] = "@greaterOrEquals(variables('B_QueryAttempt'),1)"
    attempt['limit'] = {'count': 1, 'timeout': 'PT20M'}
    paging = next(c for n, c in cards(branch) if n == 'B_Until_query_complete')
    paging['limit'] = {'count': 2, 'timeout': 'PT15M'}
    paging['actions']['B_Qualification_request_guard'] = {
        'type': 'Compose', 'runAfter': {},
        'inputs': "@if(and(less(variables('B_Page'),2),equals(variables('B_QueryAttempt'),1)),true,json('CROSSREF_QUALIFICATION_REQUEST_CAP'))"}
    paging['actions']['B_Request_uri']['runAfter'] = {
        'B_Qualification_request_guard': ['Succeeded']}
    provider = next(c for n, c in cards(branch) if n == 'B_Get_page')
    provider['inputs']['retryPolicy'] = {'type': 'none'}
    # Replace all baseline storage prefixes, including reads and failure paths.
    serialized = json.dumps(result, ensure_ascii=False)
    for before, after in (
        ('crossref-discovery-baseline-', 'crossref-discovery-qualification-v1-'),
        ('crossref-progress-baseline-', 'crossref-progress-qualification-v1-'),
        ('crossref-failed-', 'crossref-qualification-v1-failed-'),
        ('crossref-baseline-complete-', 'crossref-qualification-disabled-complete-')):
        serialized = serialized.replace(before, after)
    result = json.loads(serialized)
    names = {name for name, _ in cards(result['properties']['definition']['actions'])}
    referenced = set(re.findall(
        r"\b(?:outputs|body|actions|result|items)\('([^']+)'\)",
        json.dumps(result['properties']['definition'])))
    if referenced - names:
        raise ValueError('Missing action references: ' + ', '.join(sorted(referenced - names)))
    # Accepted-marker writers and DOI acquisition must be physically absent.
    for name, card in cards(result['properties']['definition']['actions']):
        if card.get('type') == 'Http' and name != 'B_Get_page':
            raise ValueError('Unexpected provider action: ' + name)
        inputs = card.get('inputs')
        if isinstance(inputs, dict) and inputs.get('host', {}).get('operationId') == 'CreateFile':
            target = json.dumps(card['inputs']['parameters'])
            if 'complete-' in target or 'manifest' in name.lower():
                raise ValueError('Accepted completion writer retained: ' + name)
            allowed = {'B_Save_scope', 'B_Save_query_summary', 'B_Save_page',
                       'B_Save_attempt_summary', 'B_Save_failure_receipt',
                       'B_Batch_save_progress'}
            if name not in allowed:
                raise ValueError('Unexpected storage writer: ' + name)
            parameters = inputs['parameters']
            if name in {'B_Save_failure_receipt', 'B_Batch_save_progress'}:
                if 'qualification-v1-' not in parameters['name']:
                    raise ValueError('Shared namespace writer: ' + name)
            elif parameters['folderPath'] != "@outputs('B_Run_folder')":
                raise ValueError('Unexpected archive folder: ' + name)
    return result


def main():
    if sys.version_info[:3] != (3, 15, 1):
        raise SystemExit('Explicit qualified Python 3.15.1 required')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--expected-sha256', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    raw = args.input.read_bytes()
    if hashlib.sha256(raw).hexdigest() != args.expected_sha256:
        raise ValueError('Input file bytes differ from reviewed candidate')
    pair = json.loads(raw)
    result = prepare(pair, fingerprint(pair))
    with args.output.open('x', encoding='utf-8') as output:
        json.dump(result, output, ensure_ascii=False, indent=2)
        output.write('\n')
    print(json.dumps({'status': 'local-only', 'definition_sha256': fingerprint(
        result['properties']['definition']), 'provider_request_cap': 2,
        'accepted_checkpoint_writes': 0}))


if __name__ == '__main__':
    main()
