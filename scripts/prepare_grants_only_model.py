"""Derive a grants-only isolated model from a hash-pinned accepted definition.

No native calls, credentials, source rebind or refresh. The existing model remains
untouched; native creation and source/model parity require their own receipts.
"""
import base64
import hashlib
import json

TABLE_PATHS=('definition/tables/Grants Registry.tmdl','definition/tables/Grants Deadline Occurrences.tmdl')


def fingerprint(definition):
    return hashlib.sha256(json.dumps(definition,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def isolate(definition, *, expected_sha256):
    if fingerprint(definition)!=expected_sha256: raise ValueError('Accepted definition fingerprint differs')
    parts=definition['parts'];mapping={x['path']:x for x in parts}
    if len(mapping)!=len(parts):raise ValueError('Duplicate definition paths')
    required=['definition.pbism','definition/database.tmdl',*TABLE_PATHS,'definition/relationships.tmdl']
    if any(path not in mapping for path in required):raise ValueError('Required grants parts missing')
    relationships=base64.b64decode(mapping['definition/relationships.tmdl']['payload'],validate=True).decode()
    selected=[block for block in relationships.split('\n\n') if "fromColumn: 'Grants Deadline Occurrences'.OpportunityKey" in block and "toColumn: 'Grants Registry'.OpportunityKey" in block]
    if len(selected)!=1:raise ValueError('Exactly one qualified parent/occurrence relationship required')
    output=[dict(mapping[path]) for path in required[:-1]]
    model="model Model\n\tculture: en-US\n\tdefaultPowerBIDataSourceVersion: powerBI_V3\n\tsourceQueryCulture: en-US\n\nref table 'Grants Registry'\nref table 'Grants Deadline Occurrences'\n"
    for path,text in [('definition/model.tmdl',model),('definition/relationships.tmdl',selected[0]+'\n')]:
        output.append({'path':path,'payload':base64.b64encode(text.encode()).decode(),'payloadType':'InlineBase64'})
    return {'format':'TMDL','parts':output}
