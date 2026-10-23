"""Reduce native planning/history overhead without caching unverified coverage."""
from __future__ import annotations

import json


def optimize(document):
    """Mutate a freshly prepared local batch graph; no native effects.

    Build each query's monthly rows in one Select, rather than scheduling seven
    built-ins per calendar month. Always reconstruct the plan from frozen scope
    and cutoff. Prefix validation uses corresponding plan ordinals, avoiding a
    Filter array that copies the full plan for every reused summary.
    """
    a = document['properties']['definition']['actions']
    policy = a['Scope']['inputs']['hedge']['created_date_partition']
    if policy['months_per_window'] != 1 or policy['first_unbounded_until'] != '2002-12-31':
        raise ValueError('Qualified monthly partition boundaries required')
    monthly = "and(outputs('Full_reconciliation'),greater(int(coalesce(items('Batch_plan')?['created_date_window_months'],0)),0))"
    cutoff = "outputs('Generation_cutoff')"
    prefix_end = "'2002-12-31T23:59:59Z'"
    count = (f"if({monthly},if(lessOrEquals(ticks({cutoff}),ticks({prefix_end})),1,"
             f"add(add(mul(sub(int(formatDateTime({cutoff},'yyyy')),2003),12),"
             f"int(formatDateTime({cutoff},'MM'))),1)),1)")
    start = "addToTime('2003-01-01T00:00:00Z',sub(item(),1),'Month')"
    end = f"if(equals(item(),0),{prefix_end},addSeconds(addToTime('2003-01-01T00:00:00Z',item(),'Month'),-1))"
    bounded_end = f"if(greater(ticks({end}),ticks({cutoff})),{cutoff},{end})"
    upper = (f"if(equals(ticks({bounded_end}),ticks({cutoff})),"
             f"formatDateTime({cutoff},'yyyy-MM-ddTHH:mm:ss'),formatDateTime({bounded_end},'yyyy-MM-dd'))")
    window_filter = (f"@if({monthly},concat(if(equals(item(),0),'',concat('from-created-date:',"
                     f"formatDateTime({start},'yyyy-MM-dd'),',')),'until-created-date:',{upper}),outputs('Window_filter'))")
    a['Batch_plan']['actions'] = {
        'Plan_window_count': {'type': 'Compose', 'runAfter': {}, 'inputs': '@' + count},
        'Plan_guard_count': {'type': 'Compose', 'runAfter': {'Plan_window_count': ['Succeeded']},
            'inputs': "@if(and(greater(outputs('Plan_window_count'),0),lessOrEquals(outputs('Plan_window_count'),5000)),true,json('CROSSREF_PLAN_LIMIT'))"},
        'Plan_windows': {'type': 'Select', 'runAfter': {'Plan_guard_count': ['Succeeded']},
            'inputs': {'from': "@range(0,outputs('Plan_window_count'))", 'select': {
                'key': "@items('Batch_plan')?['key']", 'anchor': "@items('Batch_plan')?['anchor']",
                'window_index': '@item()',
                'query_window_key': "@concat(items('Batch_plan')?['key'],'-window-',string(item()))",
                'window_filter': window_filter,
                'created_from': f"@if(and({monthly},greater(item(),0)),formatDateTime({start},'yyyy-MM-ddTHH:mm:ssZ'),null)",
                'created_until': f'@if({monthly},{bounded_end},null)'}}},
        'Plan_combined': {'type': 'Compose', 'runAfter': {'Plan_windows': ['Succeeded']},
            'inputs': "@union(variables('BatchWindowPlan'),body('Plan_windows'))"},
        'Plan_set_windows': {'type': 'SetVariable', 'runAfter': {'Plan_combined': ['Succeeded']},
            'inputs': {'name': 'BatchWindowPlan', 'value': "@outputs('Plan_combined')"}}}
    a['Plan_expected_count'] = {'type': 'SetVariable', 'runAfter': {'Batch_plan': ['Succeeded']},
        'inputs': {'name': 'ExpectedQueryWindowCount', 'value': "@length(variables('BatchWindowPlan'))"}}
    a['Plan_guard_total'] = {'type': 'Compose', 'runAfter': {'Plan_expected_count': ['Succeeded']},
        'inputs': "@if(and(greater(variables('ExpectedQueryWindowCount'),0),lessOrEquals(variables('ExpectedQueryWindowCount'),5000)),true,json('CROSSREF_PLAN_LIMIT'))"}
    prefix = a['Batch_verify_prefix']
    prefix['runAfter'] = {'Plan_guard_total': ['Succeeded']}
    prefix['foreach'] = "@range(0,length(variables('Queries')))"
    cards = prefix['actions']
    cards.pop('Batch_expected_window')
    query = "variables('Queries')[items('Batch_verify_prefix')]"
    expected = "variables('BatchWindowPlan')[items('Batch_verify_prefix')]"
    # Rewrite only expressions, preserving serialized field order of old saved
    # summary objects. Byte readback equality remains the acceptance condition.
    def rewrite(v):
        if isinstance(v, str) and v.startswith('@'):
            return v.replace("items('Batch_verify_prefix')", query)
        if isinstance(v, dict):
            return {k: rewrite(x) for k, x in v.items()}
        if isinstance(v, list):
            return [rewrite(x) for x in v]
        return v
    for name in ('Batch_read_summary', 'Batch_guard_summary'):
        cards[name] = rewrite(cards[name])
    checks = [f"equals({query}?['{field}'],{expected}?['{field}'])" for field in (
        'key', 'anchor', 'window_index', 'query_window_key', 'window_filter', 'created_from', 'created_until')]
    folder = a['Save_completion']['inputs']['parameters']['folderPath']
    if "'" in folder:
        raise ValueError('Qualified archive folder required')
    checks.append(f"startsWith({query}?['archive_folder'],'{folder}/crossref-discovery-')")
    cards['Batch_guard_window'] = {'type': 'Compose', 'runAfter': {},
        'inputs': "@if(and(" + ','.join(checks) + "),true,json('CROSSREF_PROGRESS_WINDOW_DRIFT'))"}
    # The four mutable date variables existed solely for the removed monthly
    # planning loop. Remove declarations and repair their initialization chain.
    for name in ('CreatedWindowIndex', 'CreatedWindowStart', 'CreatedWindowEnd', 'CreatedWindowDone'):
        a.pop('Initialize_paging_' + name)
    a['Initialize_paging']['runAfter'] = {'Initialize_paging_AttemptSummaries': ['Succeeded']}
    text = json.dumps(document)
    if any("variables('" + name + "')" in text for name in (
            'CreatedWindowIndex', 'CreatedWindowStart', 'CreatedWindowEnd', 'CreatedWindowDone')):
        raise ValueError('Unexpected mutable date variable dependency')
    return document
