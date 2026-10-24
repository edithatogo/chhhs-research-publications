"""Prepare version-conditional existing-row commits; no native calls.

Re-read after retention because attachment additions may advance the item version.
Refuse source drift, then commit source fields and exact ISO text in one MERGE.
Human classification and review fields are never included in the update payload.
"""
from __future__ import annotations

import copy
import re

HUMAN_FIELDS = frozenset({'ReviewStatus', 'ReviewNotes', 'CHHHSRelevance'})


def patch(document):
    result = copy.deepcopy(document)
    definition = result['properties']['definition']
    manual = definition['triggers']['manual']
    if manual.get('kind') != 'Button':
        raise ValueError('Preserve the existing owner manual trigger')
    manual.setdefault('runtimeConfiguration', {})['concurrency'] = {'runs': 1}
    matches = []

    def walk(actions):
        if 'SharePoint_Update_item' in actions:
            matches.append(actions)
        for action in actions.values():
            walk(action.get('actions', {}))
            walk(action.get('else', {}).get('actions', {}))

    walk(definition['actions'])
    if len(matches) != 1:
        raise ValueError('Exactly one existing update branch required')
    actions = matches[0]
    update = actions['SharePoint_Update_item']
    iso = actions.get('SharePoint_Update_item_Preserve_ISO_Text')
    if (update['inputs']['host']['operationId'] != 'PatchItem' or not iso
            or iso.get('runAfter') != {'SharePoint_Update_item': ['Succeeded']}
            or set(actions) != {'SharePoint_Update_item', 'SharePoint_Update_item_Preserve_ISO_Text'}):
        raise ValueError('Unexpected update graph; reconcile before patching')
    params = update['inputs']['parameters']
    fields = {k[5:]: v for k, v in params.items() if k.startswith('item/')}
    if any(f in fields for f in ('ReviewNotes', 'ReviewStatus')):
        raise ValueError('Unexpected review-field writes in source preimage')
    fields.pop('CHHHSRelevance', None)
    if not {'RetrievedUTC', 'DeadlineUTCInstant', 'EvidenceHash', 'OpportunityKey'} <= fields.keys():
        raise ValueError('Missing source/ISO/identity mappings')
    initial = "first(body('SharePoint_Get_items')?['value'])"
    fresh = "first(body('SharePoint_Read_commit_version')?['value'])"
    host = copy.deepcopy(update['inputs']['host'])
    read_host = copy.deepcopy(host)
    read_host['operationId'] = 'GetItems'
    read = {'type': 'OpenApiConnection', 'runAfter': {}, 'inputs': {
        'host': read_host, 'parameters': {'dataset': params['dataset'], 'table': params['table'],
        '$filter': "OpportunityKey eq '@{replace(string(item()?['OpportunityKey']),'''','''''')}'", '$top': 2},
        'retryPolicy': {'type': 'none'}}}
    checks = ["equals(length(body('SharePoint_Read_commit_version')?['value']),1)",
              f"equals({fresh}?['ID'],{initial}?['ID'])",
              f"not(empty({fresh}?['@odata.etag']))", f"not(equals({fresh}?['@odata.etag'],'*'))"]
    checks += [f"equals({fresh}?['{field}'],{initial}?['{field}'])" for field in sorted(fields)]
    guard = {'type': 'Compose', 'runAfter': {'SharePoint_Read_commit_version': ['Succeeded']},
             'inputs': "@if(and(" + ','.join(checks) + "),true,json('GRANTS_SOURCE_VERSION_DRIFT'))"}

    def expression(field, value):
        if isinstance(value, dict) and set(value) == {'Value'}:
            value = value['Value']
        if not isinstance(value, str) or not re.fullmatch(r"@\{item\(\)\?\['[A-Za-z]+'\]\}", value):
            if field != 'SourceRowURL' or value != "@if(empty(item()?['SourceRowURL']), null, item()?['SourceRowURL'])":
                raise ValueError('Unknown source mapping: ' + field)
        if field in ('URL', 'SourceRowURL'):
            return (f"if(empty(item()?['{field}']),null,setProperty(setProperty(json('{{}}'),"
                    f"'Url',item()?['{field}']),'Description',item()?['{field}']))")
        return f"string(coalesce(item()?['{field}'],''))"

    body = "json('{}')"
    for field, value in fields.items():
        body = f"setProperty({body},'{field}',{expression(field, value)})"
    host['operationId'] = 'HttpRequest'
    commit = {'type': 'OpenApiConnection', 'runAfter': {'Guard_Commit_Source_Unchanged': ['Succeeded']},
        'inputs': {'host': host, 'retryPolicy': {'type': 'none'}, 'parameters': {
            'dataset': params['dataset'], 'parameters/method': 'POST',
            'parameters/uri': "_api/web/lists(guid'" + params['table'] + "')/items(@{" + fresh + "?['ID']})",
            'parameters/headers': {'Accept': 'application/json;odata=nometadata',
                'Content-Type': 'application/json;odata=nometadata', 'X-HTTP-Method': 'MERGE',
                'IF-MATCH': '@' + fresh + "?['@odata.etag']"},
            'parameters/body': '@string(' + body + ')'}}}
    actions.clear()
    actions.update(SharePoint_Read_commit_version=read, Guard_Commit_Source_Unchanged=guard,
                   SharePoint_Update_item=commit)
    return result
