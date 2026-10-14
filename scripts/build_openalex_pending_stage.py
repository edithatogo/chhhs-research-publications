"""Prepare a hidden pending envelope table from frozen archived native capture.

Local source preparation only; no provider/native calls. Native byte/hash parity
is required before archive commit or consumer admission. Original raw attempts
remain in the archive, including retries and not-found bodies.
"""
import argparse
import base64
import copy
import hashlib
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASELINE_SHA = '0b75cc5ca227db267d8f9513e00c85c218af550c2407ec89cfb2c2744982096d'
TABLE = 'OpenAlexPendingEnvelopeChunks'
EXPRESSION = 'definition/expressions.tmdl'
HEADERS = ['RequestedDOI','RawAttempt','RawEndpoint','RawRequestJSON','RawAcquiredUTC',
           'RawHTTPStatus','RawStatus','RawByteCount','RawSchemaByteCount','RawChunkCount','RawBudgetHeadersJSON']


def sha(raw): return hashlib.sha256(raw).hexdigest()
def compact(value): return json.dumps(value, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode()


def build(baseline_bytes, capture, retained, manifest, archive_acceptance=None):
    if sha(baseline_bytes) != BASELINE_SHA:
        raise ValueError('Exact 47-part frozen preimage required')
    baseline = json.loads(baseline_bytes)
    old = baseline['definition']['parts']
    if len(old) != 47 or len({p['path'] for p in old}) != 47:
        raise ValueError('Unique 47-part preimage required')
    if capture.get('http') != 200 or retained['kind'] != 'openalex_retention_preparation_v1':
        raise ValueError('Accepted complete capture and retention required')
    rows = [{k[k.rfind('[')+1:-1] if k.endswith(']') else k:v for k,v in r.items()}
            for r in capture['body']['results'][0]['tables'][0]['rows']]
    # Locate exact stored raw file(s); never embed raw bytes in M expressions.
    raw_rows = capture['body']['results'][0]['tables'][0]['rows']
    stored = compact(raw_rows)
    raw_files = manifest['AcquisitionRaw']['Files']
    files = [f for f in raw_files if f.get('disposition') == 'accepted-identity-guard']
    if files:
        if len(files) != 1 or files[0]['bytes'] != len(stored) or files[0]['sha256'] != sha(stored):
            raise ValueError('Exact accepted archived raw capture file required')
    else:
        if not archive_acceptance or archive_acceptance.get('status') != 'PASS' or archive_acceptance.get('native_stage_marker_exact') is not True or archive_acceptance.get('raw_native_readback_verified') is not True:
            raise ValueError('Verified streamed raw stage required')
        if archive_acceptance.get('source_input_sha256') != retained['input_sha256']:
            raise ValueError('Streamed archive source generation drift')
        files = raw_files
        ordered = sorted(rows,key=lambda r:(r['RawResponseIndex'],r['RawChunkIndex']))
        offset = 0
        for entry in files:
            page = [{'['+k+']':v for k,v in r.items()} for r in ordered[offset:offset+entry['rows']]]
            body = compact(page)
            if len(page)!=entry['rows'] or len(body)!=entry['bytes'] or sha(body)!=entry['sha256']:
                raise ValueError('Streamed raw page differs from exact captured rows')
            offset += entry['rows']
        if offset != len(rows): raise ValueError('Incomplete streamed raw capture')
    if manifest['Provenance']['InputSHA256'] != retained['input_sha256']:
        raise ValueError('Source input generation drift')
    groups = {}
    for r in rows: groups.setdefault(r['RawResponseIndex'], []).append(r)
    if sorted(groups) != list(range(len(groups))) or not groups:
        raise ValueError('Complete response indices required')
    specs = []
    expected_by_work = {}
    for chunk in retained['chunks']:
        expected_by_work.setdefault(chunk['OpenAlexWorkID'], []).append(chunk)
    final = {r['RequestedDOI']:r['RawResponseIndex'] for r in sorted(rows,key=lambda r:r['RawResponseIndex'])}
    for i in sorted(groups):
        group = sorted(groups[i],key=lambda r:r['RawChunkIndex']); head=group[0]
        headers = {k:head[k] for k in HEADERS}
        if [r['RawChunkIndex'] for r in group] != list(range(head['RawChunkCount'])) or any({k:r[k] for k in HEADERS} != headers for r in group):
            raise ValueError('Frozen chunk/header drift')
        raw=base64.b64decode(''.join(r['RawPayloadBase64'] for r in group),validate=True)
        descriptor=base64.b64decode(''.join(r['RawSchemaBase64'] for r in group),validate=True)
        if len(raw)!=head['RawByteCount'] or len(descriptor)!=head['RawSchemaByteCount']:
            raise ValueError('Binary length drift')
        request=json.loads(head['RawRequestJSON'])
        if request['input_sha256']!=retained['input_sha256'] or request['requested_doi']!=head['RequestedDOI']:
            raise ValueError('Request scope drift')
        if head['RawStatus'] not in ['success','not_found','rate_limited','unavailable']:
            raise ValueError('Inadmissible raw outcome; preserve capture')
        payload=json.loads(raw) if head['RawStatus']=='success' else None
        expected_rows = expected_by_work.get(payload['id'], []) if payload else []
        if payload and i==final[head['RequestedDOI']] and not expected_rows:
            raise ValueError('Final work absent from accepted retention reference')
        specs.append({'index':i,'headers':headers,'final':i==final[head['RequestedDOI']],
                      'raw_response_sha256':sha(raw),'raw_schema_sha256':sha(descriptor),
                      'expected_metadata_characters':expected_rows[0]['MetadataCharacters'] if expected_rows else None,
                      'work_id':payload['id'] if payload else None,'returned_doi':payload['doi'] if payload else None})
    if any(s['headers']['RawStatus'] not in ['success','not_found'] for s in specs if s['final']):
        raise ValueError('Incomplete terminal DOI outcomes')
    sidecar={'kind':'openalex_pending_capture_sidecar_v1','input_sha256':retained['input_sha256'],
             'row_count':len(rows),'capture_sha256':sha(compact(capture)),'files':files,'responses':specs}
    function=(ROOT/'powerquery/fnPrepareOpenAlexCapturedEnvelope.m').read_text().strip()
    encoded=base64.b64encode(compact(sidecar)).decode()
    snapshot='''let
    Sidecar=Json.Document(Binary.FromText("SIDECAR",BinaryEncoding.Base64)),
    Groups=List.Transform(Sidecar[files],(F)=>let
        Matches=Table.SelectRows(RetainedArchiveFiles,each [Name]=F[name]),
        Raw=if Table.RowCount(Matches)=1 then Binary.Buffer(Matches{0}[Content]) else error "Missing/duplicate frozen raw archive file"
        in if Binary.Length(Raw)=F[bytes] then Json.Document(Raw) else error "Frozen raw file length drift"),
    Rows=List.Combine(Groups)
in fnPrepareOpenAlexCapturedEnvelope(Rows,Sidecar)'''.replace('SIDECAR',encoded)
    candidate=copy.deepcopy(baseline)
    expr=next(p for p in candidate['definition']['parts'] if p['path']==EXPRESSION)
    original=base64.b64decode(expr['payload'],validate=True).decode()
    if 'expression fnPrepareOpenAlexCapturedEnvelope =' in original or 'RetainedArchiveFiles' not in original:
        raise ValueError('Fresh additive archive-bound source required')
    text=original+'\nexpression fnPrepareOpenAlexCapturedEnvelope =\n'+'\n'.join('\t\t'+line for line in function.splitlines())+'\n'
    text+='\nexpression OpenAlexPendingEnvelopeSnapshot =\n'+'\n'.join('\t\t'+line for line in snapshot.splitlines())+'\n'
    expr['payload']=base64.b64encode(text.encode()).decode()
    model=next(p for p in candidate['definition']['parts'] if p['path']=='definition/model.tmdl')
    model['payload']=base64.b64encode(base64.b64decode(model['payload'])+('\nref table '+TABLE+'\n').encode()).decode()
    table='table '+TABLE+'\n\tisHidden\n'
    for name,kind in [('OpenAlexWorkID','string'),('ChunkIndex','int64'),('ChunkCount','int64'),('MetadataCharacters','int64'),('Encoding','string'),('MetadataChunk','string')]:
        table+='\n\tcolumn '+name+'\n\t\tdataType: '+kind+'\n\t\tsummarizeBy: none\n\t\tsourceColumn: '+name+'\n'
    table+='\n\tpartition '+TABLE+' = m\n\t\tmode: import\n\t\tsource = OpenAlexPendingEnvelopeSnapshot\n'
    candidate['definition']['parts'].append({'path':'definition/tables/'+TABLE+'.tmdl','payloadType':'InlineBase64','payload':base64.b64encode(table.encode()).decode()})
    expected=sha(compact(retained['chunks']))
    proof={'kind':'openalex_pending_stage_candidate_v1','native_written':False,'provider_calls':0,
           'baseline_sha256':BASELINE_SHA,'parts':48,'unchanged_old_parts':45,'expected_chunks':len(retained['chunks']),
           'expected_chunk_rows_sha256':expected,'sidecar_bytes':len(compact(sidecar)),
           'raw_payload_literals':False,'source':'existing RetainedArchiveFiles; no acquisition query evaluation',
           'raw_attempts_preserved_in_archive':True,'pending_only':True,
           'native_gate':'Process only pending table; compare all envelope/chunk bytes and SHA against retained reference before any commit. No native hash function is claimed.'}
    return candidate,sidecar,proof,snapshot


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ['private-root','baseline','capture','retained','archive-manifest','output-directory']:
        parser.add_argument('--'+name,required=True,type=Path)
    parser.add_argument('--archive-acceptance',type=Path)
    args=parser.parse_args(); root=args.private_root.resolve()
    if root.name!='ops' or root.parent.name!='private' or not root.is_dir():raise ValueError('Existing private/ops required')
    paths=[getattr(args,n).resolve() for n in ['baseline','capture','retained','archive_manifest','output_directory']]
    if any(not p.is_relative_to(root) for p in paths):raise ValueError('Private paths required')
    baseline,capture,retained,manifest,out=paths
    acceptance=args.archive_acceptance.resolve() if args.archive_acceptance else None
    if acceptance and not acceptance.is_relative_to(root):raise ValueError('Private acceptance path required')
    candidate,sidecar,proof,snapshot=build(baseline.read_bytes(),json.loads(capture.read_bytes()),json.loads(retained.read_bytes()),json.loads(manifest.read_bytes()),json.loads(acceptance.read_bytes()) if acceptance else None)
    out.mkdir(mode=0o700)
    for name,value in [('candidate-native-private.json',compact(candidate)),('sidecar-private.json',compact(sidecar)),
                       ('proof-private.json',compact(proof)),('snapshot-private.m',snapshot.encode()),('rollback-native-private.json',baseline.read_bytes())]:
        with os.fdopen(os.open(out/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'wb') as f:f.write(value)
    print(json.dumps(proof))


if __name__=='__main__':main()
