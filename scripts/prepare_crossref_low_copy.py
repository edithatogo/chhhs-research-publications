"""Prepare a local-only, same-envelope Crossref page graph reduction.

No network, authentication, save, trigger or deployment operations. Apply to an
exact fingerprinted normal monthly collector; recovery remains a separate gate.
"""
from __future__ import annotations

import copy
import json

from scripts.crossref_definition import fingerprint


def prepare(document, *, expected_definition_sha256):
    """Remove only Raw_page and inline its ordered envelope at its two uses.

    Raw response fields and provider payload are retained without field selection.
    Both save and equality check serialize the same expression. Native expression
    evaluation/serialization parity still requires future saved/runtime proof.
    """
    result = copy.deepcopy(document)
    definition = result['properties']['definition']
    if fingerprint(definition) != expected_definition_sha256:
        raise ValueError('Definition drift; exact reviewed fingerprint required')
    actions = definition['actions']
    if actions['Scope']['inputs']['policy']['source'] != 'crossref':
        raise ValueError('Crossref collector required')
    if actions['Manifest']['inputs'].get('recovery'):
        raise ValueError('Prepare from normal graph before building continuation')
    page = actions['For_each_query']['actions']['Query_may_run']['actions'][
        'Until_created_windows']['actions']['Until_query_attempt']['actions'][
        'Until_query_complete']['actions']
    raw = page['Raw_page']
    expected = {
        'request_url': "@outputs('Request_uri')",
        'status_code': "@outputs('Get_page')?['statusCode']",
        'headers': "@outputs('Get_page')?['headers']",
        'body': "@body('Get_page')",
    }
    if (raw['type'] != 'Compose' or raw['inputs'] != expected
            or raw['runAfter'] != {'Guard_page': ['Succeeded']}):
        raise ValueError('Unrecognized raw envelope or guard ordering')
    save, verify = page['Save_page'], page['Verify_page']
    if (save['type'] != 'OpenApiConnection'
            or save['inputs']['host']['operationId'] != 'CreateFile'
            or save['runAfter'] != {'Raw_page': ['Succeeded']}
            or save['inputs']['parameters']['body'] != "@string(outputs('Raw_page'))"
            or verify['runAfter'] != {'Read_page': ['Succeeded']}
            or verify['inputs'] != "@if(equals(base64(string(outputs('Raw_page'))),body('Read_page')?['$content']),true,json('CROSSREF_ACQUISITION_REJECTED'))"):
        raise ValueError('Unrecognized archive save/readback contract')
    # Reconstruct in the existing field order, using object functions rather than
    # concatenating unescaped JSON text or altering body/headers representation.
    envelope = "json('{}')"
    for key, expression in raw['inputs'].items():
        envelope = f"addProperty({envelope},'{key}',{expression[1:]})"
    del page['Raw_page']
    save['runAfter'] = copy.deepcopy(raw['runAfter'])
    save['inputs']['parameters']['body'] = f'@string({envelope})'
    verify['inputs'] = verify['inputs'].replace("outputs('Raw_page')", envelope)
    if "Raw_page" in json.dumps(definition):
        raise ValueError('Unexpected additional Raw_page dependency')
    return result
