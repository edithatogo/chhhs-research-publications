"""Install primary-owned initial checkpoint adoption from a complete new baseline.

The worker never writes a daily marker. Partial progress and old-scope markers
cannot pass this gate. Called on the new targeted daily candidate only.
"""
from __future__ import annotations
import copy
from scripts.crossref_page_batches import compose, setvar


def install(document):
    a = document['properties']['definition']['actions']
    first = next(k for k, c in a.items() if c['type'] == 'InitializeVariable' and not c.get('runAfter'))
    a['Declare_ActiveMarkerName'] = {'type': 'InitializeVariable', 'runAfter': {},
        'inputs': {'variables': [{'name': 'ActiveMarkerName', 'type': 'string', 'value': ''}]}}
    a[first]['runAfter'] = {'Declare_ActiveMarkerName': ['Succeeded']}
    def replace(v):
        if isinstance(v, str): return v.replace("outputs('Last_marker_name')", "variables('ActiveMarkerName')")
        if isinstance(v, list): return [replace(x) for x in v]
        if isinstance(v, dict): return {k: replace(x) for k, x in v.items()}
        return v
    for k in list(a): a[k] = replace(a[k])
    a['Set_active_marker'] = setvar('ActiveMarkerName', "@outputs('Last_marker_name')", 'Last_marker_name')
    a['Initialize_checkpoint']['runAfter'] = {'Set_active_marker': ['Succeeded']}
    find = copy.deepcopy(a['Find_last_complete']); find['runAfter'] = {}
    find['inputs']['parameters']['parameters/uri'] = find['inputs']['parameters']['parameters/uri'].replace('crossref-complete-', 'crossref-baseline-complete-')
    read = copy.deepcopy(a['Has_checkpoint']['actions']['Read_checkpoint'])
    read['runAfter'] = {'Bootstrap_require_baseline': ['Succeeded']}
    read['inputs']['parameters']['path'] = read['inputs']['parameters']['path'].replace("variables('ActiveMarkerName')", "outputs('Bootstrap_baseline_name')")
    marker = "@concat('crossref-complete-',workflow()?['run']?['name'],'_bootstrap.json')"
    baseline = "json(base64ToString(body('Bootstrap_read_baseline')?['$content']))"
    cards = {'Bootstrap_find_baseline': find,
        'Bootstrap_baseline_name': compose("@if(empty(body('Bootstrap_find_baseline')?['value']),'',first(body('Bootstrap_find_baseline')?['value'])?['Name'])", 'Bootstrap_find_baseline'),
        'Bootstrap_require_baseline': compose("@if(not(empty(outputs('Bootstrap_baseline_name'))),true,json('CROSSREF_NEW_SCOPE_BASELINE_REQUIRED'))", 'Bootstrap_baseline_name'),
        'Bootstrap_read_baseline': read,
        'Bootstrap_guard_baseline': compose("@if(and(equals(" + baseline + "?['source'],'crossref'),equals(" + baseline + "?['complete'],true),equals(" + baseline + "?['collection_lane'],'baseline'),equals(" + baseline + "?['full_reconciliation'],true),equals(" + baseline + "?['scope_sha256'],outputs('Scope')?['scope_sha256']),lessOrEquals(ticks(" + baseline + "?['until']),ticks(outputs('Generation_cutoff')))),true,json('CROSSREF_BASELINE_SCOPE_NOT_ACCEPTED'))", 'Bootstrap_read_baseline'),
        'Bootstrap_manifest': compose("@setProperty(setProperty(setProperty(" + baseline + ",'collection_lane','incremental'),'bootstrap_baseline_marker',outputs('Bootstrap_baseline_name')),'bootstrap_observed_utc',utcNow())", 'Bootstrap_guard_baseline')}
    original = cards['Bootstrap_manifest']['inputs'][1:]
    cards['Bootstrap_manifest']['inputs'] = "@setProperty(setProperty(" + original + ",'bootstrap_baseline_capture_run'," + baseline + "?['capture_run']),'capture_run',workflow()?['run']?['name'])"
    final = a['Batch_finalize']['actions']
    for stem, previous in [('Save', 'Bootstrap_manifest'), ('Read', 'Bootstrap_save'), ('Verify', 'Bootstrap_read')]:
        c = copy.deepcopy(final[stem + '_completion'])
        c = replace(c)
        c['runAfter'] = {previous: ['Succeeded']}
        def rewrite(v):
            if isinstance(v,str):
                v = v.replace("outputs('Manifest')", "outputs('Bootstrap_manifest')").replace("body('Read_completion')", "body('Bootstrap_read')")
                old = "concat('crossref-complete-',workflow()?['run']?['name'],'.json')"
                return v.replace(old, marker[1:])
            if isinstance(v,list):return [rewrite(x) for x in v]
            if isinstance(v,dict):return {k:rewrite(x) for k,x in v.items()}
            return v
        cards['Bootstrap_' + stem.lower()] = rewrite(c)
    cards['Bootstrap_set_marker'] = setvar('ActiveMarkerName', marker, 'Bootstrap_verify')
    cards['Bootstrap_set_checkpoint'] = setvar('Checkpoint', "@outputs('Bootstrap_manifest')", 'Bootstrap_set_marker')
    a['Bootstrap_if_needed'] = {'type': 'If', 'runAfter': {'Generation_cutoff': ['Succeeded']},
        'expression': "@not(and(equals(variables('Checkpoint')?['complete'],true),equals(variables('Checkpoint')?['scope_sha256'],outputs('Scope')?['scope_sha256'])))",
        'actions': cards, 'else': {'actions': {}}}
    a['Require_incremental_checkpoint']['runAfter'] = {'Bootstrap_if_needed': ['Succeeded']}
    return document
