"""Prepare resumable Crossref batches for the existing Microsoft cloud flow.

Pure local transformation: no authentication, deployment, provider call or run.
Progress is a separate, unaccepted artifact; only the original completion chain
can advance last-good. Connector cards are cloned from the exact native preimage.
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

from scripts.prepare_crossref_low_copy import prepare as low_copy
from scripts.crossref_definition import fingerprint
from scripts.crossref_plan_projection import optimize as optimize_plan


def _compose(value, previous):
    return {'type': 'Compose', 'inputs': value,
            'runAfter': {previous: ['Succeeded']} if previous else {}}


def _init(name, kind, value, previous):
    return {'type': 'InitializeVariable', 'runAfter': {previous: ['Succeeded']},
            'inputs': {'variables': [{'name': name, 'type': kind, 'value': value}]}}


def _replace(value, old, new):
    if isinstance(value, str):
        return value.replace(old, new)
    if isinstance(value, dict):
        return {k: _replace(v, old, new) for k, v in value.items()}
    if isinstance(value, list):
        return [_replace(v, old, new) for v in value]
    return value


def prepare(document, *, expected_definition_sha256, max_windows=50,
            max_archive_bytes=32_000_000, max_minutes=20):
    """Bound admission of new windows; finish an admitted window atomically.

    Limits are soft admission budgets, not internal platform quota measurements.
    DOI acquisition remains behind complete hedge coverage. A failed batch leaves
    the last saved prefix and last-good intact; its extra verified archives can be
    reconciled through the separately gated failed-run recovery route.
    """
    for value, ceiling in ((max_windows, 100), (max_archive_bytes, 100_000_000),
                           (max_minutes, 120)):
        if type(value) is not int or not 1 <= value <= ceiling:
            raise ValueError('Positive conservative batch admission budgets required')
    result = low_copy(document, expected_definition_sha256=expected_definition_sha256)
    a = result['properties']['definition']['actions']
    if any(k.startswith(('Batch_', 'Progress_')) for k in a):
        raise ValueError('Batch graph already present')
    if a['Full_reconciliation']['runAfter'] != {'Has_checkpoint': ['Succeeded']}:
        raise ValueError('Normal checkpoint dependency required')
    # Cutoff before checkpoint discovery remains the current observation ceiling.
    # All acquisition and acceptance references use the frozen generation cutoff.
    for key in list(a):
        if key not in {'Scope', 'Cutoff', 'Find_last_complete', 'Last_marker_name',
                       'Initialize_checkpoint', 'Has_checkpoint'}:
            a[key] = _replace(a[key], "outputs('Cutoff')", "outputs('Generation_cutoff')")
    a['Progress_initialize'] = _init('BatchProgress', 'object', {}, 'Has_checkpoint')
    find = copy.deepcopy(a['Find_last_complete'])
    find['runAfter'] = {'Progress_initialize': ['Succeeded']}
    find['inputs']['parameters']['parameters/uri'] = find['inputs']['parameters'][
        'parameters/uri'].replace('crossref-complete-', 'crossref-progress-')
    a['Progress_find'] = find
    a['Progress_name'] = _compose(
        "@if(empty(body('Progress_find')?['value']),'',first(body('Progress_find')?['value'])?['Name'])",
        'Progress_find')
    read = copy.deepcopy(a['Has_checkpoint']['actions']['Read_checkpoint'])
    read['inputs']['parameters']['path'] = read['inputs']['parameters']['path'].replace(
        "outputs('Last_marker_name')", "outputs('Progress_name')")
    read['runAfter'] = {}
    schema = {'type': 'object', 'required': ['format', 'source', 'accepted', 'complete',
        'scope_sha256', 'until', 'full_reconciliation', 'previous_marker', 'queries',
        'attempt_summaries'],
        'properties': {
            'format': {'type': 'string', 'enum': ['rims-crossref-progress-v1']},
            'source': {'type': 'string', 'enum': ['crossref']},
            'accepted': {'type': 'boolean', 'enum': [False]},
            'complete': {'type': 'boolean', 'enum': [False]},
            'scope_sha256': {'type': 'string'}, 'until': {'type': 'string'},
            'full_reconciliation': {'type': 'boolean'},
            'previous_marker': {'type': 'string'},
            'attempt_summaries': {'type': 'array'},
            'queries': {'type': 'array', 'items': {'type': 'object',
                'required': ['query_window_key', 'key', 'anchor', 'window_filter',
                    'window_index', 'created_from', 'created_until', 'archive_folder',
                    'complete', 'expected', 'received', 'unique_dois', 'pages'],
                'properties': {'query_window_key': {'type': 'string'},
                    'archive_folder': {'type': 'string'}, 'pages': {'type': 'array'},
                    'complete': {'type': 'boolean', 'enum': [True]},
                    'expected': {'type': 'integer', 'minimum': 0},
                    'received': {'type': 'integer', 'minimum': 0},
                    'unique_dois': {'type': 'integer', 'minimum': 0}}}}}}
    # Pin the exact last-good identity. Progress from an already accepted
    # generation is ignored; incompatible unfinished progress fails closed.
    guard = (
        "and(equals(variables('BatchProgress')?['format'],'rims-crossref-progress-v1'),"
        "equals(variables('BatchProgress')?['scope_sha256'],outputs('Scope')?['scope_sha256']),"
        "equals(variables('BatchProgress')?['accepted'],false),"
        "equals(variables('BatchProgress')?['complete'],false),"
        "equals(variables('BatchProgress')?['previous_marker'],outputs('Last_marker_name')),"
        "lessOrEquals(ticks(variables('BatchProgress')?['until']),ticks(outputs('Cutoff'))))")
    a['Progress_load'] = {'type': 'If', 'runAfter': {'Progress_name': ['Succeeded']},
        'expression': "@not(empty(outputs('Progress_name')))", 'actions': {
            'Progress_read': read,
            'Progress_schema': {'type': 'ParseJson', 'runAfter': {'Progress_read': ['Succeeded']},
                'inputs': {'content': "@json(base64ToString(body('Progress_read')?['$content']))",
                           'schema': schema}},
            'Progress_parse': {'type': 'SetVariable', 'runAfter': {'Progress_schema': ['Succeeded']},
                'inputs': {'name': 'BatchProgress',
                           'value': "@body('Progress_schema')"}},
            'Progress_is_obsolete': {'type': 'If', 'runAfter': {'Progress_parse': ['Succeeded']},
                'expression': "@equals(variables('BatchProgress')?['until'],variables('Checkpoint')?['until'])",
                'actions': {'Progress_discard': {'type': 'SetVariable', 'runAfter': {},
                    'inputs': {'name': 'BatchProgress', 'value': {}}}},
                'else': {'actions': {'Progress_guard': _compose(
                    "@if(" + guard + ",true,json('CROSSREF_PROGRESS_DRIFT'))", None)}}}},
        'else': {'actions': {}}}
    a['Generation_cutoff'] = _compose(
        "@if(empty(variables('BatchProgress')),outputs('Cutoff'),variables('BatchProgress')?['until'])",
        'Progress_load')
    old_full = a['Full_reconciliation']['inputs'][1:]
    # A baseline may take multiple scheduled batches. Its source watermark stays
    # frozen, but the periodic-reconciliation clock starts at actual acceptance
    # so a slow baseline does not immediately schedule another full baseline.
    old_full = old_full.replace(
        "coalesce(variables('Checkpoint')?['baseline_completed_at'],",
        "coalesce(variables('Checkpoint')?['baseline_accepted_at'],variables('Checkpoint')?['baseline_completed_at'],")
    a['Full_reconciliation']['inputs'] = (
        "@if(empty(variables('BatchProgress'))," + old_full +
        ",variables('BatchProgress')?['full_reconciliation'])")
    a['Full_reconciliation']['runAfter'] = {'Generation_cutoff': ['Succeeded']}
    a['Initialize_paging_Queries']['inputs']['variables'][0]['value'] = (
        "@coalesce(variables('BatchProgress')?['queries'],json('[]'))")
    a['Initialize_paging_AttemptSummaries']['inputs']['variables'][0]['value'] = (
        "@coalesce(variables('BatchProgress')?['attempt_summaries'],json('[]'))")
    previous = 'Initialize_paging'
    for name, kind, value in [('BatchNewWindows', 'integer', 0),
                              ('BatchArchiveBytes', 'integer', 0),
                              ('BatchWindowPlan', 'array', [])]:
        key = 'Batch_initialize_' + name
        a[key] = _init(name, kind, value, previous)
        previous = key
    a['Batch_started'] = _compose('@utcNow()', previous)
    a['Run_folder']['runAfter'] = {previous: ['Succeeded']}

    loop = a['For_each_query']
    query = loop['actions']['Query_may_run']
    old = query['actions']
    windows = old['Until_created_windows']['actions']
    # Build the entire frozen plan before provider work. Flatten acquisition to
    # one window per foreach item, avoiding an additional nested provider loop.
    plan_query = copy.deepcopy(old)
    plan_windows = plan_query['Until_created_windows']['actions']
    keep = {'Increment_expected_query_windows', 'Set_created_window_end',
            'Created_window_filter', 'Advance_created_window'}
    plan_query['Until_created_windows']['actions'] = {k: v for k, v in plan_windows.items() if k in keep}
    plan_windows = plan_query['Until_created_windows']['actions']
    plan_windows['Batch_append_plan'] = {'type': 'AppendToArrayVariable',
        'runAfter': {'Created_window_filter': ['Succeeded']}, 'inputs': {
            'name': 'BatchWindowPlan', 'value': {
                'key': "@items('For_each_query')?['key']",
                'anchor': "@items('For_each_query')?['anchor']",
                'window_index': "@variables('CreatedWindowIndex')",
                'query_window_key': "@concat(items('For_each_query')?['key'],'-window-',string(variables('CreatedWindowIndex')))",
                'window_filter': "@outputs('Created_window_filter')",
                'created_from': windows['Query_summary']['inputs']['created_from'],
                'created_until': windows['Query_summary']['inputs']['created_until']}}}
    plan_windows['Advance_created_window']['runAfter'] = {'Batch_append_plan': ['Succeeded']}
    plan_windows['Plan_created_window_filter'] = plan_windows.pop('Created_window_filter')
    plan_windows['Batch_append_plan']['runAfter'] = {'Plan_created_window_filter': ['Succeeded']}
    plan_windows['Batch_append_plan'] = _replace(plan_windows['Batch_append_plan'],
        "outputs('Created_window_filter')", "outputs('Plan_created_window_filter')")
    a['Batch_plan'] = {'type': 'Foreach', 'foreach': loop['foreach'],
        'runAfter': copy.deepcopy(loop['runAfter']),
        'runtimeConfiguration': copy.deepcopy(loop['runtimeConfiguration']),
        'actions': _replace(plan_query, "items('For_each_query')", "items('Batch_plan')")}
    # Re-read every reused summary at its original immutable archive location.
    # Prefix validation is separate from completion and cannot advance last-good.
    summary_read = copy.deepcopy(windows['Read_query_summary'])
    summary_read['runAfter'] = {}
    summary_read['inputs']['parameters']['path'] = (
        "@concat(items('Batch_verify_prefix')?['archive_folder'],'/',"
        "items('Batch_verify_prefix')?['query_window_key'],'-complete.json')")
    a['Batch_verify_prefix'] = {'type': 'Foreach',
        'foreach': "@variables('Queries')", 'runAfter': {'Batch_plan': ['Succeeded']},
        'runtimeConfiguration': {'concurrency': {'repetitions': 1}}, 'actions': {
            'Batch_expected_window': {'type': 'Query', 'runAfter': {}, 'inputs': {
                'from': "@variables('BatchWindowPlan')", 'where':
                "@equals(item()?['query_window_key'],items('Batch_verify_prefix')?['query_window_key'])"}},
            'Batch_guard_window': _compose(
                "@if(and(equals(length(body('Batch_expected_window')),1),"
                "equals(items('Batch_verify_prefix')?['anchor'],first(body('Batch_expected_window'))?['anchor']),"
                "equals(items('Batch_verify_prefix')?['window_filter'],first(body('Batch_expected_window'))?['window_filter']),"
                "equals(items('Batch_verify_prefix')?['created_from'],first(body('Batch_expected_window'))?['created_from']),"
                "equals(items('Batch_verify_prefix')?['created_until'],first(body('Batch_expected_window'))?['created_until']),"
                "startsWith(items('Batch_verify_prefix')?['archive_folder'],"
                + json.dumps(a['Save_completion']['inputs']['parameters']['folderPath'] + '/crossref-discovery-').replace('"', "'")
                + ")),true,json('CROSSREF_PROGRESS_WINDOW_DRIFT'))", 'Batch_expected_window'),
            'Batch_read_summary': summary_read,
            'Batch_guard_summary': _compose(
                "@if(and(equals(base64(string(items('Batch_verify_prefix'))),body('Batch_read_summary')?['$content']),"
                "equals(items('Batch_verify_prefix')?['complete'],true),"
                "equals(items('Batch_verify_prefix')?['received'],items('Batch_verify_prefix')?['expected']),"
                "equals(items('Batch_verify_prefix')?['unique_dois'],items('Batch_verify_prefix')?['expected'])),"
                "true,json('CROSSREF_PROGRESS_SUMMARY_DRIFT'))", 'Batch_read_summary')}}
    summary_read['runAfter'] = {'Batch_guard_window': ['Succeeded']}
    a['Batch_prefix_keys'] = {'type': 'Select',
        'runAfter': {'Batch_verify_prefix': ['Succeeded']},
        'inputs': {'from': "@variables('Queries')", 'select': {
            'query_window_key': "@item()?['query_window_key']"}}}
    a['Batch_plan_keys'] = {'type': 'Select', 'runAfter': {'Batch_prefix_keys': ['Succeeded']},
        'inputs': {'from': "@variables('BatchWindowPlan')", 'select': {
            'query_window_key': "@item()?['query_window_key']"}}}
    a['Batch_guard_prefix'] = _compose(
        "@if(and(equals(outputs('Batch_prefix_keys')?['body'],take(outputs('Batch_plan_keys')?['body'],length(variables('Queries')))),"
        "lessOrEquals(length(variables('Queries')),length(variables('BatchWindowPlan')))),"
        "true,json('CROSSREF_PROGRESS_PREFIX_REJECTED'))", 'Batch_plan_keys')
    a['Batch_started']['runAfter'] = {'Batch_guard_prefix': ['Succeeded']}
    loop['foreach'] = "@variables('BatchWindowPlan')"
    loop['runAfter'] = {'Batch_started': ['Succeeded']}
    acquisition = {k: copy.deepcopy(v) for k, v in windows.items() if k not in keep
                   and k != 'Stop_created_windows_after_failure'}
    acquisition['Created_window_filter'] = _compose(
        "@items('For_each_query')?['window_filter']", None)
    # Preserve the old filenames and all provider/byte guards, with the window
    # index coming directly from the frozen plan rather than a mutable loop.
    acquisition = _replace(acquisition, "variables('CreatedWindowIndex')",
                           "items('For_each_query')?['window_index']")
    summary = acquisition['Query_summary']['inputs']
    summary['created_from'] = "@items('For_each_query')?['created_from']"
    summary['created_until'] = "@items('For_each_query')?['created_until']"
    summary['archive_folder'] = "@outputs('Run_folder')"
    attempt_summary = acquisition['Until_query_attempt']['actions']['Query_attempt_summary']['inputs']
    attempt_summary['created_from'] = "@items('For_each_query')?['created_from']"
    attempt_summary['created_until'] = "@items('For_each_query')?['created_until']"
    attempt_summary['archive_folder'] = "@outputs('Run_folder')"
    acquisition['Batch_increment_windows'] = {'type': 'IncrementVariable',
        'runAfter': {'Append_query': ['Succeeded']},
        'inputs': {'name': 'BatchNewWindows', 'value': 1}}
    page = acquisition['Until_query_attempt']['actions']['Until_query_complete']['actions']
    # Base64 length is a conservative byte upper bound (at most two bytes extra).
    page['Batch_count_page_bytes'] = {'type': 'IncrementVariable',
        'runAfter': {'Verify_page': ['Succeeded']}, 'inputs': {
            'name': 'BatchArchiveBytes',
            'value': "@mul(div(length(body('Read_page')?['$content']),4),3)"}}
    # Count only after equality succeeds and before page bookkeeping advances.
    for key, action in page.items():
        if key != 'Batch_count_page_bytes' and 'Verify_page' in action.get('runAfter', {}):
            action['runAfter']['Batch_count_page_bytes'] = action['runAfter'].pop('Verify_page')
    query['actions'] = acquisition
    query['expression'] = (
        "@and(not(variables('AcquisitionFailed')),"
        "not(contains(body('Batch_prefix_keys'),addProperty(json('{}'),'query_window_key',items('For_each_query')?['query_window_key']))),"
        f"less(variables('BatchNewWindows'),{max_windows}),"
        f"less(variables('BatchArchiveBytes'),{max_archive_bytes}),"
        f"less(ticks(utcNow()),ticks(addMinutes(outputs('Batch_started'),{max_minutes}))))")
    # A progress record is never named crossref-complete-* and always accepted=false.
    a['Batch_guard_acquisition'] = _compose(
        "@if(not(variables('AcquisitionFailed')),true,json('CROSSREF_BATCH_FAILED'))", 'For_each_query')
    a['Batch_progress'] = _compose({
        'format': 'rims-crossref-progress-v1', 'source': 'crossref',
        'accepted': False, 'complete': False,
        'scope_sha256': "@outputs('Scope')?['scope_sha256']",
        'until': "@outputs('Generation_cutoff')",
        'full_reconciliation': "@outputs('Full_reconciliation')",
        'phase': "@if(outputs('Full_reconciliation'),'full-reconciliation','daily-incremental')",
        'window_filter': "@outputs('Window_filter')",
        'previous_marker': "@outputs('Last_marker_name')",
        'queries': "@variables('Queries')",
        'attempt_summaries': "@variables('AttemptSummaries')",
        'planned_windows': "@length(variables('BatchWindowPlan'))",
        'verified_windows': "@length(variables('Queries'))",
        'remaining_windows': "@sub(length(variables('BatchWindowPlan')),length(variables('Queries')))",
        'new_windows': "@variables('BatchNewWindows')",
        'admission_limits': {'new_windows': max_windows,
            'archive_bytes_upper_bound': max_archive_bytes, 'elapsed_minutes': max_minutes},
        'archive_bytes_upper_bound': "@variables('BatchArchiveBytes')",
        'capture_run': "@workflow()?['run']?['name']",
        'observed_at_utc': '@utcNow()',
        'last_good_preserved_until_final_acceptance': True}, 'Batch_guard_acquisition')
    for stem in ('Save', 'Read', 'Verify'):
        card = copy.deepcopy(a[stem + '_completion'])
        card = _replace(card, 'crossref-complete-', 'crossref-progress-')
        card = _replace(card, "outputs('Manifest')", "outputs('Batch_progress')")
        card = _replace(card, "body('Read_completion')", "body('Batch_read_progress')")
        card['runAfter'] = { {'Save': 'Batch_progress', 'Read': 'Batch_save_progress',
                              'Verify': 'Batch_read_progress'}[stem]: ['Succeeded']}
        a['Batch_' + stem.lower() + '_progress'] = card
    a['Batch_has_more'] = {'type': 'If',
        'runAfter': {'Batch_verify_progress': ['Succeeded']},
        'expression': "@less(length(variables('Queries')),length(variables('BatchWindowPlan')))",
        'actions': {'Batch_yield': {'type': 'Terminate', 'runAfter': {},
                                  'inputs': {'runStatus': 'Succeeded'}}},
        'else': {'actions': {}}}
    a['Guard_all_queries']['runAfter'] = {'Batch_has_more': ['Succeeded']}
    a['Manifest']['inputs']['batch_progress_format'] = 'rims-crossref-progress-v1'
    a['Manifest']['inputs']['baseline_accepted_at'] = (
        "@if(outputs('Full_reconciliation'),utcNow(),"
        "coalesce(variables('Checkpoint')?['baseline_accepted_at'],variables('Checkpoint')?['baseline_completed_at']))")
    return optimize_plan(result)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--expected-definition-sha256', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--max-windows', type=int, default=50)
    parser.add_argument('--max-archive-bytes', type=int, default=32_000_000)
    parser.add_argument('--max-minutes', type=int, default=20)
    args = parser.parse_args()
    candidate = prepare(json.loads(args.input.read_text()),
        expected_definition_sha256=args.expected_definition_sha256,
        max_windows=args.max_windows, max_archive_bytes=args.max_archive_bytes,
        max_minutes=args.max_minutes)
    args.output.write_text(json.dumps(candidate, indent=2) + '\n')
    print(json.dumps({'status': 'LOCAL_CANDIDATE_NATIVE_UNQUALIFIED',
                      'definition_sha256': fingerprint(candidate['properties']['definition'])}))


if __name__ == '__main__':
    main()
