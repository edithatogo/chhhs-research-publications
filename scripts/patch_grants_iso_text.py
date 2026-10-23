"""Preserve exact ISO text after SharePoint's dynamic item date coercion.

The existing create/update actions, identities and guards remain intact. A
dependent same-item REST MERGE uses literal JSON text rather than the connector's
dynamic field schema. Failure remains a failed run; no timestamp guard is relaxed.
"""
from __future__ import annotations

import copy


def patch(document):
    result = copy.deepcopy(document)
    definition = result['properties']['definition']
    found = []

    def walk(value):
        if not isinstance(value, dict):
            return
        for key, actions in list(value.items()):
            if key == 'actions' and isinstance(actions, dict):
                for name in ('SharePoint_Create_item', 'SharePoint_Update_item'):
                    if name not in actions:
                        continue
                    source = actions[name]
                    params = source['inputs']['parameters']
                    expected = 'PostItem' if name == 'SharePoint_Create_item' else 'PatchItem'
                    if source['inputs']['host']['operationId'] != expected:
                        raise ValueError('Unexpected item write operation')
                    for field in ('RetrievedUTC', 'DeadlineUTCInstant'):
                        if params.get('item/' + field) != "@{item()?['" + field + "']}":
                            raise ValueError('ISO source mapping drift')
                    tail = name + '_Preserve_ISO_Text'
                    if tail in actions:
                        raise ValueError('ISO repair already exists; reconcile')
                    item_id = ("body('SharePoint_Create_item')?['ID']" if expected == 'PostItem'
                               else "first(body('SharePoint_Get_items')?['value'])?['ID']")
                    host = copy.deepcopy(source['inputs']['host'])
                    host['operationId'] = 'HttpRequest'
                    body = ("@string(setProperty(setProperty(json('{}'), 'RetrievedUTC', "
                            "string(coalesce(item()?['RetrievedUTC'], ''))), 'DeadlineUTCInstant', "
                            "string(coalesce(item()?['DeadlineUTCInstant'], ''))))")
                    actions[tail] = {
                        'type': 'OpenApiConnection',
                        'inputs': {'host': host, 'parameters': {
                            'dataset': params['dataset'],
                            'parameters/method': 'POST',
                            'parameters/uri': "_api/web/lists(guid'" + params['table'] + "')/items(@{" + item_id + "})",
                            'parameters/headers': {'Accept': 'application/json;odata=nometadata',
                                                   'Content-Type': 'application/json;odata=nometadata',
                                                   'IF-MATCH': '*', 'X-HTTP-Method': 'MERGE'},
                            'parameters/body': body,
                        }},
                        'runAfter': {name: ['Succeeded']},
                    }
                    found.append(name)
            if isinstance(actions, dict):
                walk(actions)

    walk(definition)
    if sorted(found) != ['SharePoint_Create_item', 'SharePoint_Update_item']:
        raise ValueError('Exactly one existing create and update required')
    return result
