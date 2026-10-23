"""Prepare independent daily-delta and bounded-baseline cloud flow candidates.

Local preparation only. Preserve the existing incremental identity/trigger;
stage a separate Stopped baseline worker using the existing connection reference.
No authentication, provider calls, native save or execution is performed here.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
from pathlib import Path

from scripts.prepare_crossref_batches import prepare as batches
from scripts.crossref_definition import fingerprint


def _cards(actions):
    for key, card in actions.items():
        yield key, card
        yield from _cards(card.get('actions', {}))
        yield from _cards(card.get('else', {}).get('actions', {}))


def _namespace(actions, prefix, global_initializers):
    names = {k for k, _ in _cards(actions)}
    variables = {}
    for _, card in _cards(actions):
        if card['type'] == 'InitializeVariable':
            for variable in card['inputs']['variables']:
                variables[variable['name']] = prefix + variable['name']

    def value(v):
        if isinstance(v, str):
            if v.startswith('@'):
                v = re.sub(r"\b(outputs|body|actions|items|result)\('([^']+)'\)",
                    lambda m: m[1] + "('" + (prefix + m[2] if m[2] in names else m[2]) + "')", v)
                v = re.sub(r"\bvariables\('([^']+)'\)",
                    lambda m: "variables('" + variables.get(m[1], m[1]) + "')", v)
            return v
        if isinstance(v, dict):
            return {k: value(x) for k, x in v.items()}
        if isinstance(v, list):
            return [value(x) for x in v]
        return v

    def transform(cards):
        result = {}
        for key, card in cards.items():
            new = value({k: v for k, v in card.items() if k not in {'actions', 'else'}})
            new['runAfter'] = {prefix + k: v for k, v in card.get('runAfter', {}).items()}
            if card['type'] == 'InitializeVariable':
                initialized = card['inputs']['variables']
                if len(initialized) != 1:
                    raise ValueError('Qualified sequential single-variable initialization required')
                variable = initialized[0]
                kind = variable['type']
                neutral = {'string': '', 'integer': 0, 'boolean': False,
                           'array': [], 'object': {}, 'float': 0.0}[kind]
                name = variables[variable['name']]
                global_initializers.append({'name': name, 'type': kind, 'value': neutral})
                # InitializeVariable is legal only at root. Its former position
                # becomes a SetVariable so dynamic values retain their ordering.
                new['type'] = 'SetVariable'
                new['inputs'] = {'name': name, 'value': value(variable['value'])}
            elif card['type'] in {'SetVariable', 'IncrementVariable', 'AppendToArrayVariable'}:
                new['inputs']['name'] = variables.get(card['inputs']['name'], card['inputs']['name'])
            if 'actions' in card:
                new['actions'] = transform(card['actions'])
            if 'else' in card:
                new['else'] = {'actions': transform(card['else'].get('actions', {}))}
            result[prefix + key] = new
        return result

    return transform(actions)


def _isolate_finalization(a):
    """Yield this lane rather than terminate the entire daily flow."""
    a.pop('Batch_has_more')
    a['Guard_all_queries']['runAfter'] = {}
    # Follow the existing acceptance DAG, preserving provider/DOI/output guards.
    final = {'Guard_all_queries'}
    changed = True
    while changed:
        changed = False
        for key, card in a.items():
            if key != 'Observe_failed_generation' and key not in final and any(
                    dependency in final for dependency in card.get('runAfter', {})):
                final.add(key)
                changed = True
    a['Batch_finalize'] = {'type': 'If',
        'runAfter': {'Batch_verify_progress': ['Succeeded']},
        'expression': "@equals(length(variables('Queries')),length(variables('BatchWindowPlan')))",
        'actions': {k: a.pop(k) for k in list(a) if k in final}, 'else': {'actions': {}}}
    observer = a['Observe_failed_generation']
    observer['runAfter'] = {'Batch_finalize': ['Failed', 'TimedOut', 'Skipped']}
    observer['actions']['Terminate_failed_generation'] = {
        'type': 'SetVariable',
        'runAfter': {'Verify_failure_receipt': ['Succeeded', 'Failed', 'TimedOut', 'Skipped']},
        'inputs': {'name': 'LaneFailed', 'value': True}}


def _lane(template, lane):
    a = copy.deepcopy(template)
    _isolate_finalization(a)
    a['Lane_failed_initialize'] = {'type': 'InitializeVariable', 'runAfter': {},
        'inputs': {'variables': [{'name': 'LaneFailed', 'type': 'boolean', 'value': False}]}}
    a['Scope']['runAfter'] = {'Lane_failed_initialize': ['Succeeded']}
    for _, card in _cards(a):
        # Storage identities, not action keys or source scope, distinguish lanes.
        def paths(v):
            if isinstance(v, str):
                v = v.replace('crossref-progress-', 'crossref-progress-' + lane + '-')
                v = v.replace('/crossref-discovery-', '/crossref-discovery-' + lane + '-')
                if lane == 'baseline':
                    v = v.replace('crossref-complete-', 'crossref-baseline-complete-')
                return v
            if isinstance(v, dict):
                return {k: paths(x) for k, x in v.items()}
            if isinstance(v, list):
                return [paths(x) for x in v]
            return v
        # Do not visit nested action cards twice and double-prefix their paths.
        for key in ('inputs', 'expression', 'foreach'):
            if key in card:
                card[key] = paths(card[key])
    a['Full_reconciliation']['inputs'] = lane == 'baseline'
    a['Batch_progress']['inputs']['collection_lane'] = lane
    final = a['Batch_finalize']['actions']
    final['Manifest']['inputs']['collection_lane'] = lane
    # A lane can never adopt progress produced for the other acquisition mode.
    guard = a['Progress_load']['actions']['Progress_is_obsolete']['else']['actions']['Progress_guard']
    expression = guard['inputs']
    expression = expression.replace('@if(and(', '@if(and('
        + "equals(variables('BatchProgress')?['collection_lane'],'" + lane + "'),"
        + "equals(variables('BatchProgress')?['full_reconciliation'],"
        + ('true' if lane == 'baseline' else 'false') + '),', 1)
    guard['inputs'] = expression
    a['Progress_load']['actions']['Progress_schema']['inputs']['schema']['required'].append('collection_lane')
    a['Progress_load']['actions']['Progress_schema']['inputs']['schema']['properties'][
        'collection_lane'] = {'type': 'string', 'enum': [lane]}
    if lane == 'incremental':
        # Do not silently bootstrap an unbounded historical delta or advance a
        # new source scope without an accepted baseline for that exact scope.
        a['Require_incremental_checkpoint'] = {
            'type': 'Compose', 'runAfter': {'Generation_cutoff': ['Succeeded']},
            'inputs': "@if(and(equals(variables('Checkpoint')?['complete'],true),"
                "equals(variables('Checkpoint')?['scope_sha256'],outputs('Scope')?['scope_sha256'])),"
                "true,json('CROSSREF_INCREMENTAL_BASELINE_REQUIRED'))"}
        a['Full_reconciliation']['runAfter'] = {'Require_incremental_checkpoint': ['Succeeded']}
    else:
        # The baseline's own checkpoint/progress identities are independent of
        # daily commits. An existing accepted normal marker can seed the first
        # scheduling clock without becoming baseline-progress authority.
        a['Has_checkpoint']['else']['actions']['Seed_baseline_clock'] = {
            'type': 'SetVariable', 'runAfter': {},
            'inputs': {'name': 'Checkpoint', 'value': "@variables('D_Checkpoint')"}}
        interval = a['Scope']['inputs']['hedge']['full_reconciliation_days']
        if type(interval) is not int or interval < 1:
            raise ValueError('Positive existing full-reconciliation interval required')
        a['Baseline_due'] = {'type': 'If',
            'runAfter': {'Full_reconciliation': ['Succeeded']},
            'expression': "@or(not(empty(variables('BatchProgress'))),"
                "not(equals(variables('Checkpoint')?['scope_sha256'],outputs('Scope')?['scope_sha256'])),"
                "lessOrEquals(ticks(coalesce(variables('Checkpoint')?['baseline_accepted_at'],"
                "variables('Checkpoint')?['baseline_completed_at'],'1900-01-01T00:00:00Z')),"
                f"ticks(addDays(utcNow(),-{interval}))))", 'actions': {}, 'else': {'actions': {}}}
        # Everything downstream of Full_reconciliation is gated by due status.
        tail = {'Window_filter'}
        changed = True
        while changed:
            changed = False
            for key, card in a.items():
                if key not in tail and key != 'Baseline_due' and any(
                        dependency in tail for dependency in card.get('runAfter', {})):
                    tail.add(key)
                    changed = True
        a['Window_filter']['runAfter'] = {}
        a['Baseline_due']['actions'] = {k: a.pop(k) for k in list(a) if k in tail}
    return a


def _standalone(actions, prefix):
    initializers = []
    transformed = _namespace(actions, prefix, initializers)
    root = {}
    previous = None
    for v in initializers:
        key = 'Declare_' + v['name']
        root[key] = {'type': 'InitializeVariable',
            'runAfter': {previous: ['Succeeded']} if previous else {},
            'inputs': {'variables': [v]}}
        previous = key
    transformed[prefix + 'Lane_failed_initialize']['runAfter'] = {previous: ['Succeeded']}
    root.update(transformed)
    final = prefix + ('Baseline_due' if prefix == 'B_' else 'Batch_finalize')
    root['Guard_lane_result'] = {'type': 'Compose',
        'runAfter': {final: ['Succeeded', 'Failed', 'TimedOut', 'Skipped']},
        'inputs': "@if(and(not(variables('" + prefix + "LaneFailed')),"
            "equals(actions('" + final + "')?['status'],'Succeeded')),"
            "true,json('CROSSREF_LANE_FAILURE_INSPECT_INDEPENDENT_PROGRESS'))"}
    if prefix != 'B_':
        root['Guard_lane_result']['runAfter'][prefix + 'Observe_failed_generation'] = [
            'Succeeded', 'Failed', 'TimedOut', 'Skipped']
    cards = list(_cards(root))
    if len(cards) > 500:
        raise ValueError('Independent lane graph exceeds supported 500-action limit')
    return root


def prepare(document, *, expected_definition_sha256, baseline_monthly_keys=('tropical', 'cairns'), **budgets):
    candidate = batches(document, expected_definition_sha256=expected_definition_sha256, **budgets)
    template = candidate['properties']['definition']['actions']
    delta = _lane(template, 'incremental')
    baseline_template = copy.deepcopy(template)
    scope = baseline_template['Scope']['inputs']
    hedge = scope['hedge']
    by_key = {q['key']: q for q in hedge['queries']}
    if (not baseline_monthly_keys or len(set(baseline_monthly_keys)) != len(baseline_monthly_keys)
            or not set(baseline_monthly_keys) <= set(by_key)
            or not set(hedge['created_date_partition']['query_keys']) <= set(baseline_monthly_keys)):
        raise ValueError('Existing monthly partitions and exact frozen query keys required')
    # Measured Cairns single window was 53.8MB: larger than the 32MB admission
    # budget. Partition only the independent full worker, never the daily scope.
    for key in baseline_monthly_keys:
        by_key[key]['created_date_window_months'] = 1
    hedge['created_date_partition']['query_keys'] = list(baseline_monthly_keys)
    hedge['batch_page_pacing'] = {
        'minimum_seconds': 5, 'seconds_per_archive_megabyte': 20,
        'projected_history_multiplier': 4,
        'projected_history_megabytes_per_five_minutes': 60,
        'qualification': 'historical-volume-derived projection; native metering unverified'}
    scope['scope_sha256'] = hashlib.sha256(json.dumps(
        {'policy': scope['policy'], 'hedge': hedge}, sort_keys=True,
        separators=(',', ':')).encode()).hexdigest()
    final_manifest = baseline_template['Manifest']['inputs']
    final_manifest['scope_sha256'] = scope['scope_sha256']
    final_manifest['created_date_partition'] = copy.deepcopy(hedge['created_date_partition'])
    baseline = _lane(baseline_template, 'baseline')
    paced = 0
    for key, card in _cards(baseline):
        if key == 'Polite_delay':
            if card['type'] != 'Wait' or card['inputs'] != {
                    'interval': {'count': 5, 'unit': 'Second'}}:
                raise ValueError('Qualified baseline page pacing preimage required')
            # Ceiling(base64 decoded byte upper bound * 20 / 1,000,000).
            # At a planning multiplier of four this targets 60MB of history per
            # five minutes; it is not the service's quota meter or a guarantee.
            card['inputs']['interval']['count'] = (
                "@max(5,div(add(mul(mul(div(length(body('Read_page')?['$content']),4),3),20),999999),1000000))")
            paced += 1
    if paced != 1:
        raise ValueError('Exactly one baseline page pacing action required')
    # The separate worker obtains its scheduling fallback using the existing
    # read-only connector, never another flow's variables or a shared cache.
    branch = baseline['Has_checkpoint']['else']['actions']
    branch.clear()
    find = copy.deepcopy(baseline['Find_last_complete'])
    find['runAfter'] = {}
    find['inputs']['parameters']['parameters/uri'] = find['inputs']['parameters'][
        'parameters/uri'].replace('crossref-baseline-complete-', 'crossref-complete-')
    branch['Find_seed_checkpoint'] = find
    branch['Seed_checkpoint_name'] = {'type': 'Compose',
        'runAfter': {'Find_seed_checkpoint': ['Succeeded']},
        'inputs': "@if(empty(body('Find_seed_checkpoint')?['value']),'',first(body('Find_seed_checkpoint')?['value'])?['Name'])"}
    read = copy.deepcopy(baseline['Has_checkpoint']['actions']['Read_checkpoint'])
    read['inputs']['parameters']['path'] = read['inputs']['parameters']['path'].replace(
        "outputs('Last_marker_name')", "outputs('Seed_checkpoint_name')")
    branch['Has_seed_checkpoint'] = {'type': 'If',
        'runAfter': {'Seed_checkpoint_name': ['Succeeded']},
        'expression': "@not(empty(outputs('Seed_checkpoint_name')))",
        'actions': {'Read_seed_checkpoint': read,
            'Seed_baseline_clock': {'type': 'SetVariable',
                'runAfter': {'Read_seed_checkpoint': ['Succeeded']},
                'inputs': {'name': 'Checkpoint',
                    'value': "@json(base64ToString(body('Read_seed_checkpoint')?['$content']))"}},
            'Guard_seed_checkpoint': {'type': 'Compose',
                'runAfter': {'Seed_baseline_clock': ['Succeeded']},
                'inputs': "@if(and(equals(variables('Checkpoint')?['source'],'crossref'),"
                    "equals(variables('Checkpoint')?['complete'],true),"
                    "lessOrEquals(ticks(variables('Checkpoint')?['until']),ticks(outputs('Cutoff')))),"
                    "true,json('CROSSREF_BASELINE_CLOCK_SEED_REJECTED'))"}},
        'else': {'actions': {}}}
    incremental = copy.deepcopy(candidate)
    incremental['properties']['definition']['actions'] = _standalone(delta, '')
    # This is a creation input, not an invented second stable ID or a deployment.
    # Preserve the entire qualified connection-reference map; no new connection.
    worker = {'properties': {
        'displayName': 'CHHHS RIMS | Data spaces | Crossref full reconciliation',
        'state': 'Stopped',
        'connectionReferences': copy.deepcopy(candidate['properties']['connectionReferences']),
        'definition': copy.deepcopy(candidate['properties']['definition'])}}
    worker['properties']['definition']['actions'] = _standalone(baseline, 'B_')
    return {'incremental': incremental, 'baseline_worker': worker}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--expected-definition-sha256', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    candidate = prepare(json.loads(args.input.read_text()),
                        expected_definition_sha256=args.expected_definition_sha256)
    args.output.write_text(json.dumps(candidate, indent=2) + '\n')
    print(json.dumps({'status': 'LOCAL_INDEPENDENT_LANES_NATIVE_UNQUALIFIED',
                      'definition_sha256': {key: fingerprint(value['properties']['definition'])
                          for key, value in candidate.items()}}))


if __name__ == '__main__':
    main()
