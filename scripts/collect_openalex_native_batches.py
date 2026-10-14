"""Resumable CLI orchestration of the existing Microsoft OpenAlex raw producer.

No Python provider requests. Native actions require an active exact-target lease.
Each batch stays frozen until its native raw archive commit receipt is supplied.
Never repeat a mutation after uncertain transport, or reharvest on query failure.
"""
import argparse
import base64
import copy
import hashlib
import json
import os
import re
import uuid
import time
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from urllib.error import HTTPError

from build_openalex_acquisition_model import COLUMNS, TABLE, EXPRESSION
from enrich_openalex import clean_doi
from prepare_openalex_retention import private_path

INPUT_SHA='7eccc7921e5e42fed39fd2b5004e6d748868cab94feb4e3c96f16c7987d51476'
SNAPSHOT=re.compile(r'(expression OpenAlexRawAcquisitionSnapshot =\s*fnAcquireOpenAlexRaw\(Json.Document\(Binary.FromText\(")(?P<scope>[A-Za-z0-9+/=]+)(",BinaryEncoding.Base64\)\),")(?P<input>[0-9a-f]{64})("\))')


def digest(raw):return hashlib.sha256(raw).hexdigest()
def read(path):return json.loads(path.read_bytes())
def save(path,value):
    raw=json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False).encode()
    temporary=path.with_name(path.name+'.tmp')
    with os.fdopen(os.open(temporary,os.O_WRONLY|os.O_CREAT|os.O_TRUNC,0o600),'wb') as stream:
        stream.write(raw);stream.flush();os.fsync(stream.fileno())
    os.replace(temporary,path)
def parts(document):return {p['path']:base64.b64decode(p['payload'],validate=True) for p in document['definition']['parts']}


def initialise(records_bytes,retained,captured_dois):
    if digest(records_bytes)!=INPUT_SHA:raise ValueError('Frozen canonical input drift')
    scope={d.casefold() for r in json.loads(records_bytes) if (d:=clean_doi(r.get('DOI')))}
    outcomes=retained['attempt_statuses'];excluded=[r['RequestedDOI'] for r in outcomes]
    if (len(excluded)!=50 or len(excluded)!=len(set(excluded)) or
            sum(r['Status']=='success' for r in outcomes)!=48 or sum(r['Status']=='not_found' for r in outcomes)!=2):
        raise ValueError('Accepted48 successes/two not-found outcomes required')
    if not isinstance(captured_dois,list) or len(captured_dois)!=len(set(captured_dois)):
        raise ValueError('Explicit unique captured/uncommitted DOI list required')
    if not set(excluded)<=scope or not set(captured_dois)<=scope-set(excluded):raise ValueError('Foreign or replay DOI scope')
    return {'kind':'openalex_native_collection_v1','source_input_sha256':INPUT_SHA,
        'remaining_dois':sorted(scope-set(excluded)-set(captured_dois)),
        'accepted_outcomes_excluded':excluded,'captured_uncommitted_dois':captured_dois,
        'committed_batches':[],'current':None,'batch_limit':50,'provider_python_calls':0}


def prepare(state,baseline_bytes,expected_sha,limit):
    if state['current'] is not None:raise ValueError('Current batch must be archived before replacement')
    if digest(baseline_bytes)!=expected_sha:raise ValueError('Exact native baseline drift')
    if type(limit) is not int or not 1<=limit<=50:raise ValueError('At most50 pending DOI scope required')
    chosen=state['remaining_dois'][:limit]
    if not chosen:raise ValueError('No pending DOI scope')
    baseline=json.loads(baseline_bytes);old=parts(baseline)
    if len(old)!=47 or 'definition/tables/'+TABLE+'.tmdl' not in old:raise ValueError('Existing repaired47-part producer required')
    text=old[EXPRESSION].decode();matches=list(SNAPSHOT.finditer(text))
    if len(matches)!=1 or matches[0]['input']!=state['source_input_sha256']:raise ValueError('Exact frozen producer snapshot required')
    match=matches[0];literal=base64.b64encode(json.dumps(chosen,separators=(',',':')).encode()).decode()
    text=text[:match.start('scope')]+literal+text[match.end('scope'):]
    candidate=copy.deepcopy(baseline)
    next(p for p in candidate['definition']['parts'] if p['path']==EXPRESSION)['payload']=base64.b64encode(text.encode()).decode()
    for name,value in parts(candidate).items():
        if name!=EXPRESSION and old[name]!=value:raise ValueError('Unleased part changed')
    return candidate,{'source_input_sha256':INPUT_SHA,'selected_dois':chosen,
        'baseline_sha256':expected_sha,'changed_parts':[EXPRESSION],'preserved_parts':46,
        'phase':'prepared','capture_cursor':[-1,-1],'capture_pages':[]}


def page_query(cursor):
    after,index=cursor
    if type(after) is not int or type(index) is not int or after< -1 or index< -1:raise ValueError('Invalid raw cursor')
    columns=','.join(json.dumps(c)+','+TABLE+'['+c+']' for c in COLUMNS)
    return ('EVALUATE VAR Remaining=FILTER('+TABLE+','+TABLE+'[RawResponseIndex]>'+str(after)+' || ('+
        TABLE+'[RawResponseIndex]='+str(after)+' && '+TABLE+'[RawChunkIndex]>'+str(index)+')) '
        'RETURN SELECTCOLUMNS(TOPN(20,Remaining,['+'RawResponseIndex],ASC,[RawChunkIndex],ASC),'+columns+
        ') ORDER BY [RawResponseIndex],[RawChunkIndex]')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['init','prepare','preflight','update','update-poll','readback','refresh','refresh-poll','capture','admit'])
    parser.add_argument('--private-root',required=True,type=Path)
    parser.add_argument('--ledger',required=True)
    for name in ['records','retained','captured-dois','baseline','lease','archive-receipt']:parser.add_argument('--'+name)
    parser.add_argument('--baseline-sha256')
    parser.add_argument('--limit',type=int,default=50)
    args=parser.parse_args();root=args.private_root.resolve()
    if root.name!='ops' or root.parent.name!='private' or not root.is_dir():raise ValueError('Existing ignored private/ops required')
    ledger=private_path(args.ledger,root)
    def path(name):
        value=getattr(args,name.replace('-','_'))
        if not value:raise ValueError('Missing --'+name)
        return private_path(value,root)
    if args.action=='init':
        if ledger.exists():raise ValueError('Do not replace collection ledger')
        state=initialise(path('records').read_bytes(),read(path('retained')),read(path('captured-dois')))
        save(ledger,state);print(json.dumps({'remaining_dois':len(state['remaining_dois']),'native_calls':0}));return
    state=read(ledger)
    if args.action=='prepare':
        candidate,current=prepare(state,path('baseline').read_bytes(),args.baseline_sha256,args.limit)
        batch=ledger.parent/(ledger.stem+'-batch-'+str(len(state['committed_batches'])).zfill(3));batch.mkdir(mode=0o700)
        candidate_path=batch/'candidate-native-private.json';save(candidate_path,candidate)
        current.update(directory=str(batch),candidate_sha256=digest(candidate_path.read_bytes()),baseline_path=str(path('baseline')))
        state['current']=current;save(ledger,state);save(batch/'scope-private.json',current)
        print(json.dumps({'phase':'prepared','dois':len(current['selected_dois']),'changed_parts':1,'native_calls':0}));return
    current=state['current']
    if current is None:raise ValueError('No prepared current batch')
    directory=private_path(current['directory'],root)
    def checkpoint():save(ledger,state)
    if args.action=='admit':
        receipt=read(path('archive-receipt'))
        refresh_ids=[receipt[k] for k in ['producer_refresh_request_id','producer_refresh_id'] if k in receipt]
        if (current['phase']!='captured' or receipt.get('status')!='PASS' or receipt.get('native_commit_exact') is not True or
            receipt.get('raw_native_readback_verified') is not True or receipt.get('source_input_sha256')!=INPUT_SHA or
            not refresh_ids or any(value!=current['refresh_request_id'] for value in refresh_ids) or
            not re.fullmatch(r'[0-9a-f]{64}',receipt.get('manifest_sha256','')) or
            sorted(receipt.get('committed_dois',[]))!=sorted(current['selected_dois'])):
            raise ValueError('Exact native raw archive admission receipt required; batch stays frozen')
        state['remaining_dois']=[d for d in state['remaining_dois'] if d not in current['selected_dois']]
        state['committed_batches'].append({'scope':current['selected_dois'],'archive_receipt':str(path('archive-receipt')),
            'archive_receipt_sha256':digest(path('archive-receipt').read_bytes()),'refresh_request_id':current['refresh_request_id']})
        state['current']=None;checkpoint();print(json.dumps({'phase':'archived','remaining_dois':len(state['remaining_dois'])}));return
    lease=read(path('lease'))
    if lease.get('status')!='active' or lease.get('source_input_sha256')!=INPUT_SHA:raise ValueError('Active frozen-scope native lease required')
    # Load the parent's already-qualified Azure CLI adapter only for native work.
    # Offline preparation does not require that separately owned module.
    from capture_retained_canary_acceptance import _token_for
    workspace=str(uuid.UUID(lease['workspace_id']));model=str(uuid.UUID(lease['semantic_model_id']))
    fabric='https://api.fabric.microsoft.com/v1/workspaces/'+workspace+'/semanticModels/'+model
    powerbi='https://api.powerbi.com/v1.0/myorg/groups/'+workspace+'/datasets/'+model
    def request(url,method='GET',body=None):
        parsed=urlparse(url)
        if parsed.scheme!='https' or parsed.hostname not in ['api.fabric.microsoft.com','api.powerbi.com','wabi-australia-southeast-redirect.analysis.windows.net']:
            raise ValueError('Unqualified Microsoft host')
        is_fabric=url.startswith(fabric) or '/v1/operations/' in url
        headers={'Authorization':'Bearer '+_token_for('https://api.fabric.microsoft.com' if is_fabric else 'https://analysis.windows.net/powerbi/api'),'Content-Type':'application/json'}
        if is_fabric:headers['x-ms-fabric-skill']='semantic-model-authoring'
        try:
            with urlopen(Request(url,data=None if body is None else json.dumps(body).encode(),headers=headers,method=method),timeout=40) as response:
                chunks=[];size=0;deadline=time.monotonic()+120
                while True:
                    if time.monotonic()>deadline:raise TimeoutError('Bounded native read timeout; preserve saved handle')
                    chunk=response.read1(128*1024)
                    if not chunk:break
                    size+=len(chunk)
                    if size>20*1024*1024:raise ValueError('Native readback exceeds bound; preserve handle')
                    chunks.append(chunk)
                raw=b''.join(chunks)
                return {'http':response.status,'headers':{k.lower():v for k,v in response.headers.items() if k.lower() in ['location','x-ms-request-id','x-ms-operation-id','retry-after']},'body':json.loads(raw) if raw else {}}
        except HTTPError as error:
            failure={'http':error.code,'body':json.loads(error.read())};save(directory/'last-native-error-private.json',failure)
            raise RuntimeError('Native HTTP failure; saved receipt, no resubmission') from None
    if args.action=='preflight':
        if current['phase'] not in ['prepared','preflight_pending']:raise ValueError('Prepared source scope required')
        if 'preflight_operation' not in current:
            current['preflight_operation']=request(fabric+'/getDefinition','POST',{});checkpoint()
        operation=current['preflight_operation']
        if operation['http']==202:
            status=request(operation['headers']['location']);save(directory/'preflight-definition-status-private.json',status)
            if status['body'].get('status')!='Succeeded':current['phase']='preflight_pending';checkpoint();print('preflight_pending');return
            result=request(operation['headers']['location']+'/result')
        else:result=operation
        baseline_path=private_path(current['baseline_path'],root)
        if digest(baseline_path.read_bytes())!=current['baseline_sha256'] or parts(result['body'])!=parts(read(baseline_path)):
            raise ValueError('Fresh exact native definition drift')
        schedule=request(powerbi+'/refreshSchedule');history=request(powerbi+'/refreshes?$top=1')
        reports=request('https://api.powerbi.com/v1.0/myorg/groups/'+workspace+'/reports')
        if (schedule['body']['enabled'] is not False or any(r.get('datasetId')==model for r in reports['body']['value']) or
            history['body']['value'][0]['status']!='Completed' or
            history['body']['value'][0]['requestId']!=lease.get('last_completed_request_id')):
            raise ValueError('Fresh isolation/last-completed request guard failed')
        save(directory/'preflight-private.json',{'definition':result,'schedule':schedule,'history':history,'reports':reports})
        current['phase']='preflight_verified';checkpoint()
    elif args.action=='update':
        if current['phase']!='preflight_verified':raise ValueError('Fresh preflight required; resolve prior mutation before resubmit')
        if lease.get('baseline_sha256')!=current['baseline_sha256']:raise ValueError('Lease baseline drift')
        candidate=read(directory/'candidate-native-private.json')
        if digest((directory/'candidate-native-private.json').read_bytes())!=current['candidate_sha256']:raise ValueError('Candidate drift')
        current['phase']='update_uncertain';checkpoint()
        result=request(fabric+'/updateDefinition?updateMetadata=false','POST',{'definition':candidate['definition'],'options':{'allowPurgeData':False}})
        save(directory/'update-submission-private.json',result);current['update']=result;current['phase']='update_submitted';checkpoint()
    elif args.action=='update-poll':
        result=current['update'];result=request(result['headers']['location']) if result['http']==202 else result
        save(directory/'update-status-private.json',result)
        if result['body'].get('status')=='Failed':raise RuntimeError('Saved update failed; inspect cause, do not repeat')
        if result['body'].get('status')=='Succeeded' or result['http']==200 and not result['body']:
            current['phase']='updated';checkpoint()
    elif args.action=='readback':
        if current['phase'] not in ['updated','readback_pending']:raise ValueError('Terminal update required')
        if 'definition_operation' not in current:
            current['definition_operation']=request(fabric+'/getDefinition','POST',{});checkpoint()
        operation=current['definition_operation']
        if operation['http']==202:
            status=request(operation['headers']['location']);save(directory/'definition-status-private.json',status)
            if status['body'].get('status')!='Succeeded':current['phase']='readback_pending';checkpoint();print('readback_pending');return
            result=request(operation['headers']['location']+'/result')
        else:result=operation
        saved=result['body'];actual=parts(saved);expected=parts(read(directory/'candidate-native-private.json'))
        if actual.keys()!=expected.keys():raise ValueError('Native part drift')
        for name in expected:
            if actual[name]!=expected[name]:
                if name!=EXPRESSION or [s for s in actual[name].decode().splitlines() if s.strip()]!=[s for s in expected[name].decode().splitlines() if s.strip()]:
                    raise ValueError('Native definition mismatch')
        save(directory/'saved-definition-private.json',saved);current['phase']='readback_verified';checkpoint()
    elif args.action=='refresh':
        if current['phase']!='readback_verified':raise ValueError('Saved source parity required; no repeated refresh')
        schedule=request(powerbi+'/refreshSchedule');history=request(powerbi+'/refreshes?$top=1')
        reports=request('https://api.powerbi.com/v1.0/myorg/groups/'+workspace+'/reports')
        if schedule['body']['enabled'] is not False or any(r.get('datasetId')==model for r in reports['body']['value']) or history['body']['value'][0]['status']!='Completed':
            raise ValueError('Native isolation/terminal refresh guard failed')
        current['phase']='refresh_uncertain';checkpoint()
        result=request(powerbi+'/refreshes','POST',{'type':'full','commitMode':'transactional','maxParallelism':1,'retryCount':0,'objects':[{'table':TABLE}]})
        save(directory/'refresh-submission-private.json',result);current['refresh']=result
        current['refresh_request_id']=result['headers']['x-ms-request-id'];current['phase']='refresh_submitted';checkpoint()
    elif args.action=='refresh-poll':
        result=request(current['refresh']['headers']['location']);save(directory/'refresh-status-private.json',result)
        body=result['body']
        if body.get('status')=='Completed':
            if body.get('numberOfAttempts')!=1 or len(body['objects'])!=1 or body['objects'][0]['table']!=TABLE or body['objects'][0]['status']!='Completed':raise ValueError('Refresh scope drift')
            current['phase']='refresh_completed';checkpoint()
        elif body.get('status')=='Failed':raise RuntimeError('Producer refresh failed; inspect saved cause, do not repeat')
    elif args.action=='capture':
        if current['phase']!='refresh_completed':raise ValueError('Completed producer refresh required')
        while True:
            page_path=directory/('capture-page-'+str(len(current['capture_pages'])).zfill(4)+'-private.json')
            result=read(page_path) if page_path.exists() else request(powerbi+'/executeQueries','POST',{'queries':[{'query':page_query(current['capture_cursor'])}],'serializerSettings':{'includeNulls':True}})
            rows=result['body']['results'][0]['tables'][0].get('rows',[])
            if len(rows)>20:raise ValueError('Raw capture page bound exceeded')
            save(page_path,result)
            if not rows:
                all_rows=[]
                for name in current['capture_pages']:all_rows.extend(read(private_path(name,root))['body']['results'][0]['tables'][0]['rows'])
                save(directory/'capture-private.json',{'http':200,'body':{'results':[{'tables':[{'rows':all_rows}]}]}})
                current['phase']='captured';checkpoint();break
            indices=[[r['[RawResponseIndex]'],r['[RawChunkIndex]']] for r in rows]
            if indices!=sorted(indices) or len({tuple(x) for x in indices})!=len(indices) or indices[0]<=current['capture_cursor']:raise ValueError('Raw cursor did not advance')
            if any(r['[RequestedDOI]'] not in current['selected_dois'] for r in rows):raise ValueError('Native source scope drift')
            current['capture_pages'].append(str(page_path));current['capture_cursor']=indices[-1];checkpoint()
    print(json.dumps({'phase':current['phase'],'dois':len(current['selected_dois']),'remaining_dois':len(state['remaining_dois'])}))


if __name__=='__main__':main()
