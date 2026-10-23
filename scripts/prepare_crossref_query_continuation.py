"""Continue a failed Crossref hedge using its verified complete-query prefix.

Preparation only; no acquisition, upload, native save, trigger or login. Crossref
cursors expire, so incomplete queries restart at '*' in the original window.
Previously complete queries retain their immutable archive pointers. Restore the
normal collector after the bounded manual recovery; never schedule this packet.
Both baseline and incremental recovery preserve the original window bounds.
Incremental recovery additionally pins the previous complete checkpoint; index
membership can still change, so existing page-total guards remain mandatory.
"""
from __future__ import annotations

import argparse
import copy
from datetime import datetime, timedelta
import json
import re
from pathlib import Path

from scripts.crossref_definition import fingerprint


def prepare(document, receipt, *, expected_definition_sha256):
    candidate = copy.deepcopy(document)
    evidence = copy.deepcopy(receipt)
    try:
        if (evidence.get('status') != 'VERIFIED_FAILED_HEDGE_RECOVERY_INPUTS'
                or evidence.get('source_terminal_status') not in {'Failed', 'TimedOut'}
                or evidence.get('native_terminal_gate_satisfied') is not True):
            raise ValueError('Verified native Failed/TimedOut terminal evidence required')
        props = candidate['properties']
        definition = props['definition']
        if not re.fullmatch('[0-9a-f]{64}', expected_definition_sha256 or ''):
            raise ValueError('Exact definition fingerprint required')
        if fingerprint(definition) != expected_definition_sha256:
            raise ValueError('Definition drift; reconcile before recovery')
        triggers = definition['triggers']
        if (props.get('state') != 'Stopped' or props.get('isManaged') is True
                or set(triggers) != {'manual'}
                or triggers['manual'].get('type') != 'Request'
                or triggers['manual'].get('kind') != 'Button'):
            raise ValueError('Stopped unmanaged manual-only collector preimage required')
        a = definition['actions']
        scope = a['Scope']['inputs']
        manifest = a['Manifest']['inputs']
        if (scope['policy']['source'] != 'crossref'
                or manifest.get('format') != 'rims-crossref-discovery-v1'
                or any(k in manifest for k in ('recovery', 'extension'))):
            raise ValueError('Normal qualified Crossref collector required')
        if evidence.get('scope_sha256') != scope['scope_sha256']:
            raise ValueError('Verified terminal failed-run evidence for this exact scope required')
        run = evidence['source_run']
        if not isinstance(run, str) or not re.fullmatch('[A-Za-z0-9_-]+', run):
            raise ValueError('Exact source run required')
        folder = a['Run_folder']['inputs']
        match = re.fullmatch(r"@concat\('([^']+/crossref-discovery-)',workflow\(\)\?\['run'\]\?\['name'\]\)", folder)
        if not match or evidence['archive_folder'] != match[1] + run:
            raise ValueError('Recovery archive must belong to this collector and failed run')
        cutoff = evidence['until']
        parsed = datetime.fromisoformat(cutoff.replace('Z', '+00:00'))
        if parsed.utcoffset() is None or not cutoff.endswith('Z'):
            raise ValueError('Original UTC source cutoff required')
        full = evidence.get('full_reconciliation')
        if type(full) is not bool:
            raise ValueError('Explicit original full/delta mode required')
        checkpoint = None
        if full:
            expected_window = 'until-created-date:' + cutoff.removesuffix('Z')
        else:
            checkpoint = evidence.get('previous_checkpoint', {})
            if (checkpoint.get('source') != 'crossref' or checkpoint.get('complete') is not True
                    or checkpoint.get('scope_sha256') != scope['scope_sha256']):
                raise ValueError('Verified last-good checkpoint for the same delta scope required')
            previous = datetime.fromisoformat(checkpoint['until'].replace('Z', '+00:00'))
            baseline = datetime.fromisoformat(checkpoint['baseline_completed_at'].replace('Z', '+00:00'))
            overlap = scope['hedge']['overlap_days']
            if (previous.utcoffset() is None or baseline.utcoffset() is None
                    or not checkpoint['until'].endswith('Z')
                    or not checkpoint['baseline_completed_at'].endswith('Z')
                    or not baseline <= previous <= parsed
                    or type(overlap) is not int or overlap < 0):
                raise ValueError('Original UTC checkpoint chronology and overlap required')
            start = (previous - timedelta(days=overlap)).strftime('%Y-%m-%dT%H:%M:%S')
            expected_window = 'from-index-date:' + start + ',until-index-date:' + cutoff.removesuffix('Z')
        if evidence['window_filter'] != expected_window:
            raise ValueError('Original complete frozen source window required')
        if scope['hedge'].get('created_date_partition'):
            return _prepare_partitioned_prefix(candidate, evidence, expected_window, full, checkpoint)
        planned = scope['hedge']['queries']
        queries = evidence['queries']
        keys = [q['key'] for q in planned]
        if (len(keys) != len(set(keys)) or not isinstance(queries, list)
                or not 0 < len(queries) < len(planned)
                or [q['key'] for q in queries] != keys[:len(queries)]):
            raise ValueError('A consecutive complete-query prefix with unfinished queries is required')
        readback_count = 0
        for expected, query in zip(planned, queries):
            if (query.get('complete') is not True or query.get('anchor') != expected['anchor']
                    or any(type(query.get(k)) is not int or query[k] < 0
                           for k in ('expected', 'received', 'unique_dois'))
                    or not query['expected'] == query['received'] == query['unique_dois']):
                raise ValueError('Only complete, source-matching hedge queries can be reused')
            pages = query['pages']
            if not isinstance(pages, list) or not pages:
                raise ValueError('Native page readbacks required, including a verified empty page')
            for index, page in enumerate(pages):
                if (page.get('file') != query['key'] + '-page-' + str(index) + '.json'
                        or page.get('saved_readback_equal') is not True
                        or type(page.get('rows')) is not int or not 0 <= page['rows'] <= 500
                        or (index < len(pages) - 1 and page['rows'] != 500)):
                    raise ValueError('Exact contiguous saved page prefix required')
            if (pages[-1]['rows'] >= 500 or sum(p['rows'] for p in pages) != query['received']):
                raise ValueError('Complete terminal page and reconciled row count required')
            query['archive_folder'] = evidence['archive_folder']
            readback_count += len(pages)
        if type(evidence.get('saved_page_readback_count')) is not int or evidence['saved_page_readback_count'] != readback_count:
            raise ValueError('Independent saved-page readback coverage required')
        init = a['Initialize_paging']['inputs']['variables']
        init_by_name = {v['name']: v for v in init}
        for name in ('Queries', 'DoiEntries', 'DoiIndex'):
            if name not in init_by_name:
                raise ValueError('Qualified collector initialization required')
        if init_by_name['DoiEntries']['value'] or init_by_name['DoiIndex']['value'] != 0:
            raise ValueError('DOI acquisition must not have started in this hedge continuation')
        query = a['For_each_query']['actions']['Query_may_run']
        if query['expression'] != "@not(variables('AcquisitionFailed'))":
            raise ValueError('Existing query gate changed')
        if query['actions']['Reset_Cursor']['inputs']['value'] != '*':
            raise ValueError('Incomplete queries must restart with a fresh provider cursor')
        init_by_name['Queries']['value'] = queries
        a['Cutoff']['inputs'] = cutoff
        a['Window_filter']['inputs'] = evidence['window_filter']
        a['Full_reconciliation']['inputs'] = full
        if checkpoint is not None:
            # The normal runtime still reads the last-good marker. Refuse drift
            # before reusing any query rather than silently moving its watermark.
            checks = []
            for name in ('source', 'scope_sha256', 'until', 'baseline_completed_at'):
                value = checkpoint[name]
                if not isinstance(value, str) or "'" in value:
                    raise ValueError('Checkpoint identity cannot be safely encoded')
                checks.append("equals(variables('Checkpoint')?['" + name + "'],'" + value + "')")
            checks.append("equals(variables('Checkpoint')?['complete'],true)")
            a['Guard_recovery_checkpoint'] = {
                'type': 'Compose', 'runAfter': {'Has_checkpoint': ['Succeeded']},
                'inputs': '@if(and(' + ','.join(checks) + "),true,json('CROSSREF_RECOVERY_CHECKPOINT_DRIFT'))"}
            if a['Full_reconciliation']['runAfter'] != {'Has_checkpoint': ['Succeeded']}:
                raise ValueError('Normal checkpoint dependency required')
            a['Full_reconciliation']['runAfter'] = {'Guard_recovery_checkpoint': ['Succeeded']}
        # A literal array avoids adding run dependencies or changing write actions.
        reused_keys = json.dumps(keys[:len(queries)], separators=(',', ':'))
        query['expression'] = ("@and(not(variables('AcquisitionFailed')),not(contains(json('"
                               + reused_keys + "'),items('For_each_query')?['key'])))")
        if "'" in reused_keys:
            raise ValueError('Query keys cannot be safely encoded')
        manifest['recovery'] = {'kind': 'verified_complete_hedge_prefix', 'source_run': run,
            'archive_folder': evidence['archive_folder'], 'reused_queries': len(queries),
            'incomplete_query_cursor_reused': False, 'full_reconciliation': full,
            'window_filter': expected_window}
    except (KeyError, TypeError, AttributeError, OverflowError) as error:
        raise ValueError('Incomplete or unexpected recovery input') from error
    return candidate


def _created_window_plan(scope, cutoff, full, window_filter):
    """Mirror the deployed monthly boundaries; never infer a receipt's windows."""
    policy = scope['hedge']['created_date_partition']
    if (policy.get('strategy') != 'full-reconciliation-only-inclusive-created-date-windows-v1'
            or policy.get('months_per_window') != 1
            or policy.get('first_unbounded_until') != '2002-12-31'):
        raise ValueError('Qualified one-month partition policy required')
    if type(full) is not bool or not isinstance(cutoff, str) or not cutoff.endswith('Z'):
        raise ValueError('Explicit original mode and UTC cutoff required')
    ceiling = datetime.fromisoformat(cutoff.replace('Z', '+00:00'))
    if ceiling.utcoffset() != timedelta(0):
        raise ValueError('Original UTC cutoff required')
    queries = scope['hedge']['queries']
    keys = [q['key'] for q in queries]
    partition_keys = policy.get('query_keys')
    if (not keys or len(set(keys)) != len(keys)
            or not isinstance(partition_keys, list) or not partition_keys
            or len(set(partition_keys)) != len(partition_keys)
            or not set(partition_keys) <= set(keys)):
        raise ValueError('Unique frozen query and partition identities required')
    for query in queries:
        months = query.get('created_date_window_months', 0)
        if type(months) is not int or months != (1 if query['key'] in partition_keys else 0):
            raise ValueError('Query partition differs from frozen policy')
    first_end = datetime.fromisoformat('2002-12-31T23:59:59+00:00')
    planned = []
    for query in queries:
        key = query['key']
        if not re.fullmatch('[A-Za-z0-9_-]+', key):
            raise ValueError('Safe frozen query key required')
        windowed = full and query.get('created_date_window_months', 0) > 0
        if windowed and (key not in policy['query_keys'] or query['created_date_window_months'] != 1):
            raise ValueError('Query partition differs from frozen policy')
        index, start = 0, None
        while True:
            if not windowed:
                end, bounded_filter = None, window_filter
            else:
                if index == 0:
                    end = min(first_end, ceiling)
                else:
                    next_month = start.replace(year=start.year + (start.month == 12),
                                               month=1 if start.month == 12 else start.month + 1)
                    end = min(next_month - timedelta(seconds=1), ceiling)
                end_filter = cutoff.removesuffix('Z') if end == ceiling else end.strftime('%Y-%m-%d')
                bounded_filter = ('' if start is None else 'from-created-date:' + start.strftime('%Y-%m-%d') + ',') + 'until-created-date:' + end_filter
            planned.append({'key': key, 'anchor': query['anchor'], 'window_index': index,
                'query_window_key': key + '-window-' + str(index),
                'window_filter': bounded_filter, 'created_from': start, 'created_until': end})
            if not windowed or end == ceiling:
                break
            start = (datetime.fromisoformat('2003-01-01T00:00:00+00:00') if index == 0
                     else next_month)
            index += 1
            if index >= 5000:
                raise ValueError('Window plan exceeds the deployed loop limit')
    return planned


def _prepare_partitioned_prefix(candidate, evidence, window_filter, full, checkpoint):
    """Reuse only an independently verified consecutive complete-window prefix."""
    a = candidate['properties']['definition']['actions']
    plan = _created_window_plan(a['Scope']['inputs'], evidence['until'], full, window_filter)
    queries = evidence['queries']
    if not isinstance(queries, list) or not 0 < len(queries) < len(plan):
        raise ValueError('A nonempty completed-window prefix with remaining windows is required')
    readbacks = 0
    for expected, query in zip(plan, queries):
        for field in ('key', 'anchor', 'window_index', 'query_window_key', 'window_filter'):
            if query.get(field) != expected[field] or (field == 'window_index' and type(query[field]) is not int):
                raise ValueError('Recovery windows must be the exact consecutive frozen prefix')
        for field in ('created_from', 'created_until'):
            value = query.get(field)
            if expected[field] is None:
                if value is not None:
                    raise ValueError('Unexpected created-date bound')
            elif (not isinstance(value, str) or not value.endswith('Z')
                  or datetime.fromisoformat(value.replace('Z', '+00:00')) != expected[field]):
                raise ValueError('Created-date boundary differs from frozen plan')
        if (query.get('complete') is not True
                or any(type(query.get(k)) is not int or query[k] < 0 for k in ('expected', 'received', 'unique_dois'))
                or not query['expected'] == query['received'] == query['unique_dois']):
            raise ValueError('Only complete reconciled windows can be reused')
        attempt = query.get('accepted_attempt')
        if (type(attempt) is not int or not 1 <= attempt <= 2
                or type(query.get('attempt_count')) is not int or query['attempt_count'] != attempt):
            raise ValueError('Exact accepted bounded attempt required')
        pages = query['pages']
        if not isinstance(pages, list) or not pages:
            raise ValueError('Verified terminal page required, including an empty page')
        for index, page in enumerate(pages):
            name = expected['query_window_key'] + '-attempt-' + str(attempt) + '-page-' + str(index) + '.json'
            if (page.get('file') != name or page.get('saved_readback_equal') is not True
                    or type(page.get('rows')) is not int or not 0 <= page['rows'] <= 500
                    or (index < len(pages) - 1 and page['rows'] != 500)):
                raise ValueError('Exact contiguous window page readbacks required')
        if pages[-1]['rows'] >= 500 or sum(p['rows'] for p in pages) != query['received']:
            raise ValueError('Terminal window page and total do not reconcile')
        query['archive_folder'] = evidence['archive_folder']
        readbacks += len(pages)
    if type(evidence.get('saved_page_readback_count')) is not int or evidence['saved_page_readback_count'] != readbacks:
        raise ValueError('Independent page readback coverage required')

    # Accept only the actual sequential initialization layout saved by Dataverse.
    initializers = {k: v for k, v in a.items() if k == 'Initialize_paging' or k.startswith('Initialize_paging_')}
    variables, visited, key = {}, set(), 'Initialize_paging'
    while key in initializers:
        if key in visited:
            raise ValueError('Initialization dependency cycle')
        visited.add(key)
        action = initializers[key]
        values = action['inputs']['variables']
        if action['type'] != 'InitializeVariable' or len(values) != 1 or len(action['runAfter']) != 1:
            raise ValueError('Sequential single-variable initialization required')
        variable = values[0]
        if variable['name'] in variables:
            raise ValueError('Duplicate variable initialization')
        variables[variable['name']] = variable
        key = next(iter(action['runAfter']))
    if visited != set(initializers) or key != 'Window_filter':
        raise ValueError('Initialization chain must finish before Run_folder')
    for name, value in [('Queries', []), ('DoiEntries', []), ('DoiIndex', 0), ('ExpectedQueryWindowCount', 0)]:
        if name not in variables or variables[name]['value'] != value:
            raise ValueError('Normal empty recovery initialization required')
    variables['Queries']['value'] = queries

    windows = a['For_each_query']['actions']['Query_may_run']['actions']['Until_created_windows']['actions']
    attempt = windows['Until_query_attempt']['actions']
    if attempt['Attempt_reset_Cursor']['inputs']['value'] != '*':
        raise ValueError('Incomplete windows must restart from a fresh cursor')
    keep = {'Increment_expected_query_windows', 'Set_created_window_end', 'Created_window_filter', 'Advance_created_window'}
    if not keep <= set(windows) or windows['Initialize_query_attempt']['runAfter'] != {'Created_window_filter': ['Succeeded']}:
        raise ValueError('Normal window dependency graph required')
    if 'Window_requires_acquisition' in windows:
        raise ValueError('Reconcile the existing recovery graph before editing')
    acquisition = {k: windows.pop(k) for k in list(windows) if k not in keep}
    acquisition['Initialize_query_attempt']['runAfter'] = {}
    reused = json.dumps([q['query_window_key'] for q in queries], separators=(',', ':'))
    windows['Window_requires_acquisition'] = {'type': 'If',
        'runAfter': {'Created_window_filter': ['Succeeded']},
        'expression': "@not(contains(json('" + reused + "'),concat(items('For_each_query')?['key'],'-window-',string(variables('CreatedWindowIndex')))))",
        'actions': acquisition, 'else': {'actions': {}}}
    windows['Advance_created_window']['runAfter'] = {'Window_requires_acquisition': ['Succeeded']}
    a['Cutoff']['inputs'] = evidence['until']
    a['Window_filter']['inputs'] = window_filter
    a['Full_reconciliation']['inputs'] = full
    if checkpoint is not None:
        checks = []
        for field in ('source', 'scope_sha256', 'until', 'baseline_completed_at'):
            value = checkpoint[field]
            if not isinstance(value, str) or "'" in value:
                raise ValueError('Safe pinned checkpoint identity required')
            checks.append("equals(variables('Checkpoint')?['" + field + "'],'" + value + "')")
        checks.append("equals(variables('Checkpoint')?['complete'],true)")
        if a['Full_reconciliation']['runAfter'] != {'Has_checkpoint': ['Succeeded']}:
            raise ValueError('Normal checkpoint dependency required')
        a['Guard_recovery_checkpoint'] = {'type': 'Compose', 'runAfter': {'Has_checkpoint': ['Succeeded']},
            'inputs': '@if(and(' + ','.join(checks) + "),true,json('CROSSREF_RECOVERY_CHECKPOINT_DRIFT'))"}
        a['Full_reconciliation']['runAfter'] = {'Guard_recovery_checkpoint': ['Succeeded']}
    a['Manifest']['inputs']['recovery'] = {'kind': 'verified_complete_window_prefix',
        'source_run': evidence['source_run'], 'archive_folder': evidence['archive_folder'],
        'reused_query_windows': len(queries), 'incomplete_query_cursor_reused': False,
        'full_reconciliation': full, 'window_filter': window_filter}
    return candidate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--receipt', type=Path, required=True)
    parser.add_argument('--expected-definition-sha256', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    candidate = prepare(json.loads(args.input.read_text()),
                        json.loads(args.receipt.read_text()),
                        expected_definition_sha256=args.expected_definition_sha256)
    # Refuse to replace a reviewed candidate, and never write an output when a
    # preparation gate fails. This command has no native execution path.
    with args.output.open('x') as destination:
        destination.write(json.dumps(candidate, indent=2) + '\n')
    print(json.dumps({'status': 'LOCAL_RECOVERY_PREPARED_NATIVE_UNQUALIFIED',
                      'definition_sha256': fingerprint(candidate['properties']['definition'])}))


if __name__ == '__main__':
    main()
