"""Prepare one hidden native raw acquisition table on the accepted reader model.

No native/provider calls. First trial is one pending DOI, with bounded later
batches at most50. Accepted tables, original expressions and source bindings
remain unchanged. Native Anonymous binding/egress qualification stays explicit.
"""
import argparse
import base64
import copy
import hashlib
import json
import os
from pathlib import Path
from enrich_openalex import clean_doi
from prepare_openalex_retention import private_path

ROOT=Path(__file__).resolve().parents[1]
BASELINE_SHA256='adb1012c55cd885c51141d7c028a34317f92214c88319e57f01c5db8e17a3212'
TABLE='OpenAlexRawAcquisition'
EXPRESSION='definition/expressions.tmdl'
COLUMNS={'RequestedDOI':'string','RawResponseIndex':'int64','RawAttempt':'int64','RawEndpoint':'string',
    'RawRequestJSON':'string','RawAcquiredUTC':'string','RawHTTPStatus':'int64','RawStatus':'string',
    'RawByteCount':'int64','RawSchemaByteCount':'int64','RawChunkIndex':'int64','RawChunkCount':'int64',
    'RawPayloadBase64':'string','RawSchemaBase64':'string','RawBudgetHeadersJSON':'string'}


def build(baseline_bytes,records_bytes,retained,limit=1):
    if hashlib.sha256(baseline_bytes).hexdigest()!=BASELINE_SHA256:
        raise ValueError('Exact accepted committed-reader baseline required')
    if type(limit) is not int or not 1<=limit<=50:
        raise ValueError('Bounded one-to-fifty pending DOI scope required')
    records=json.loads(records_bytes)
    if not isinstance(records,list) or any(not isinstance(r,dict) for r in records):
        raise ValueError('Frozen canonical source record list required')
    scope={d.casefold() for r in records if (d:=clean_doi(r.get('DOI')))}
    if retained.get('kind')!='openalex_retention_preparation_v1':
        raise ValueError('Accepted retained outcome scope required')
    outcomes=retained['attempt_statuses'];attempted=[s['RequestedDOI'] for s in outcomes]
    if len(attempted)!=len(set(attempted)) or not set(attempted)<=scope or any(s['Status'] not in ['success','not_found'] for s in outcomes):
        raise ValueError('Complete retained success/not-found outcomes required')
    pending=sorted(scope-set(attempted));chosen=pending[:limit]
    if not chosen:raise ValueError('No pending DOI; preserve accepted source')
    baseline=json.loads(baseline_bytes);parts=baseline['definition']['parts']
    if baseline['definition']['format']!='TMDL' or len(parts)!=46 or len({p['path'] for p in parts})!=46:
        raise ValueError('Exact unique46-part model required')
    part=next(p for p in parts if p['path']==EXPRESSION);text=base64.b64decode(part['payload'],validate=True).decode()
    if 'expression OpenAlexCommittedObservations =' not in text or 'expression fnAcquireOpenAlexRaw =' in text:
        raise ValueError('Unmodified accepted committed-reader expressions required')
    digest=hashlib.sha256(records_bytes).hexdigest()
    encoded=base64.b64encode(json.dumps(chosen,separators=(',',':')).encode()).decode()
    function=(ROOT/'powerquery/fnAcquireOpenAlexRaw.m').read_text().strip()
    text+='\nexpression fnAcquireOpenAlexRaw =\n'+'\n'.join('\t\t'+line for line in function.splitlines())+'\n'
    snapshot='fnAcquireOpenAlexRaw(Json.Document(Binary.FromText("'+encoded+'",BinaryEncoding.Base64)),"'+digest+'")'
    text+='\nexpression OpenAlexRawAcquisitionSnapshot = '+snapshot+'\n'
    table='table '+TABLE+'\n\tisHidden\n'
    for name,kind in COLUMNS.items():
        table+='\n\tcolumn '+name+'\n\t\tdataType: '+kind+'\n\t\tsummarizeBy: none\n\t\tsourceColumn: '+name+'\n'
    table+='\n\tpartition '+TABLE+' = m\n\t\tmode: import\n\t\tsource = OpenAlexRawAcquisitionSnapshot\n'
    candidate=copy.deepcopy(baseline)
    next(p for p in candidate['definition']['parts'] if p['path']==EXPRESSION)['payload']=base64.b64encode(text.encode()).decode()
    model=next(p for p in candidate['definition']['parts'] if p['path']=='definition/model.tmdl')
    original_model=base64.b64decode(model['payload']).decode()
    model['payload']=base64.b64encode((original_model+'\nref table '+TABLE+'\n').encode()).decode()
    candidate['definition']['parts'].append({'path':'definition/tables/'+TABLE+'.tmdl','payloadType':'InlineBase64','payload':base64.b64encode(table.encode()).decode()})
    receipt={'kind':'openalex_raw_acquisition_candidate_v1','native_written':False,'provider_calls':0,
        'baseline_sha256':BASELINE_SHA256,'source_input_sha256':digest,'pending_dois':len(pending),'selected_dois':chosen,
        'excluded_retained_outcomes':len(attempted),'parts':47,'existing_typed_partitions_unchanged':True,
        'original_expression_prefix_exact':True,'existing_model_only_adds_table_reference':True,
        'credential_mode':'Anonymous; native binding and egress not yet qualified','query_cost':'exact singleton only; no list/filter/search',
        'deployment_gate':'Native owner drift/rollback/isolation, Anonymous origin binding, one-table processing and complete raw readback before archive admission.',
        'raw_contract':'Complete binary + recursive Kind/Fields/Items schema + exact UTC/status/request;24000Base64chunks; all retry bodies retained; no undocumented hash API.',
        'next_integration':'Capture only new raw table; reconstruct full bytes and compute private bootstrap SHA; keep failed/not-found raw outcomes; existing raw-stage and commit-last archive; then accepted four-table reader refresh and registry.'}
    return candidate,receipt,snapshot


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--private-root',required=True,type=Path)
    for name in ['baseline','records','retained','output-directory']:parser.add_argument('--'+name,required=True)
    parser.add_argument('--limit',type=int,default=1)
    args=parser.parse_args();root=args.private_root.resolve()
    if root.name!='ops' or root.parent.name!='private' or not root.is_dir():raise ValueError('Existing private/ops required')
    baseline,records,retained,output=[private_path(getattr(args,n),root) for n in ['baseline','records','retained','output_directory']]
    candidate,receipt,snapshot=build(baseline.read_bytes(),records.read_bytes(),json.loads(retained.read_bytes()),args.limit)
    output.mkdir(mode=0o700)
    for name,value in [('candidate-native-private.json',json.dumps(candidate,separators=(',',':'))),
                       ('candidate-receipt-private.json',json.dumps(receipt,indent=2)),('snapshot-private.m',snapshot)]:
        with os.fdopen(os.open(output/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w') as stream:stream.write(value)
    print(json.dumps({k:v for k,v in receipt.items() if k!='selected_dois'}))


if __name__=='__main__':main()
