"""Extend the owned NIH acquisition qualifier with an existing-parent chain.

Offline preparation only. Preserve the original manual Invoker importer. The
separate grants-only model and existing physical connections must be qualified.
"""
import copy
import hashlib
import json
from uuid import UUID
from scripts.grants_deadline_schedule import require_source_schedule
from scripts.grants_registry import stable_key

HUMAN = {'ReviewNotes','ReviewStatus','CHHHSRelevance'}
CHOICES = {'Status','DeadlinePrecision','DeadlineTemporalStatus','RetrievedTimestampStatus'}


def prepare(document, bindings, context, baseline, *, fault=None):
    if fault not in (None,'before_commit','stale_etag','before_refresh'):
        raise ValueError('Unknown bounded fault')
    require_source_schedule({'Source':'us-grants-gov-nih-pa-25-301','SourceID':'357812','RoundID':'PA-25-301',
        'DeadlineScheduleJSON':context['deadline_schedule_json'],'SourceDateFactsJSON':context['source_date_facts_json'],'SourceAttribution':context['source_attribution']})
    if baseline['OpportunityKey'] != stable_key(baseline) or baseline['SourceID'] != '357812':
        raise ValueError('Exact admitted parent required')
    for key in ('list','workspace','model'): UUID(bindings[key])
    if bindings['model']==bindings.get('protected_model') or type(bindings['item_id']) is not int:
        raise ValueError('Separate model and exact existing item required')
    result=copy.deepcopy(document); props=result['properties']; d=props['definition']; actions=d['actions']
    if 'Processing' in actions or set(d['triggers'])!={'Recurrence'} or actions['Scope']['inputs']['source']!='us-grants-gov-nih-pa-25-301':
        raise ValueError('Unexpected acquisition graph')
    site=bindings['site']; table=bindings['list']; folder=bindings['folder']; key=baseline['OpportunityKey']
    if site != actions['Acquisition']['actions']['Create_folder']['inputs']['parameters']['dataset']:
        raise ValueError('Preserve the qualified acquisition site')
    if "@concat('"+folder+"/nih-acquisition-',workflow()?['run']?['name'])" != actions['Run_folder']['inputs']:
        raise ValueError('Preserve the qualified acquisition archive folder')
    ctx_sha=hashlib.sha256(json.dumps(context,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
    fields=sorted(set(baseline)-HUMAN)
    if len(fields)!=29: raise ValueError('Expected32normalizedfields minus3humanfields')
    initial={f:baseline[f] if baseline[f] is not None else '' for f in fields}
    def action(kind,inputs,after=None):return {'type':kind,'inputs':inputs,'runAfter':{after:['Succeeded']} if after else {}}
    def connector(alias,op,params,after=None):
        return action('OpenApiConnection',{'host':{'apiId':'/providers/Microsoft.PowerApps/apis/'+alias,'connectionName':alias,'operationId':op},'parameters':params,'retryPolicy':{'type':'none'}},after)
    def sp(op,params,after=None):return connector('shared_sharepointonline',op,{'dataset':site,**params},after)
    def guard(expr,after,code):return action('Compose',f"@if({expr},true,json('{code}'))",after)
    def lookup(after=None):return sp('GetItems',{'table':table,'$filter':f"OpportunityKey eq '{key}'",'$top':2},after)
    def save(name,value,after):return sp('CreateFile',{'folderPath':folder,'name':name,'body':f'@base64ToBinary(base64(string(outputs(\'{value}\'))))'},after)
    def read(path,after):return sp('GetFileContentByPath',{'path':path,'inferContentType':False},after)
    def projection(lookup_name):
        base=f"first(body('{lookup_name}')?['value'])";return {f:f"@coalesce({base}?['{f}']"+("?['Value']" if f in CHOICES else '')+",'')" for f in fields}
    def item_value(name):return f"outputs('Projected_row')?['{name}']"
    variables=actions['Initialize_responses']['inputs']['variables']
    variables.extend([{'name':'PreviousSource','type':'object','value':initial},{'name':'ModelMatches','type':'boolean','value':False}])
    process={
      'Find_last_commit':sp('HttpRequest',{'parameters/method':'GET','parameters/uri':"_api/web/GetFolderByServerRelativePath(decodedurl='"+site.split('.com',1)[1]+folder+"')/Files?$select=Name,UniqueId,ETag,Length&$filter=startswith(Name,'nih-chain-commit-')&$orderby=TimeCreated desc&$top=1",'parameters/headers':{'Accept':'application/json;odata=nometadata'}}),
      'Has_previous_commit':{'type':'If','expression':"@greater(length(body('Find_last_commit')?['value']),0)",'runAfter':{'Find_last_commit':['Succeeded']},'actions':{
        'Read_previous_commit':read("@concat('"+folder+"/',first(body('Find_last_commit')?['value'])?['Name'])",None),
        'Previous_commit':action('Compose',"@json(base64ToString(body('Read_previous_commit')?['$content']))",'Read_previous_commit'),
        'Guard_previous_commit':guard("and(equals(outputs('Previous_commit')?['format'],'rims-nih-commit-v1'),equals(outputs('Previous_commit')?['context_sha256'],'"+ctx_sha+"'),equals(outputs('Previous_commit')?['opportunity_key'],'"+key+"'),equals(outputs('Previous_commit')?['register_item_id'],"+str(bindings['item_id'])+"))",'Previous_commit','NIH_PREVIOUS_COMMIT_REJECTED'),
        'Set_previous_source':action('SetVariable',{'name':'PreviousSource','value':"@outputs('Previous_commit')?['source_projection']"},'Guard_previous_commit')},'else':{'actions':{}}},
      'Worker_attachments':{'type':'Select','runAfter':{'Has_previous_commit':['Succeeded']},'inputs':{'from':"@variables('Attachments')",'select':{'folder_id':"@item()?['folder_metadata']?['id']",'content_base64':"@item()?['content_base64']"}}},
      'Worker_input':action('Compose',{'context':context,'observed_utc':"@outputs('Observed_utc')",'responses':"@variables('Responses')",'attachments':"@body('Worker_attachments')"},'Worker_attachments'),
      'Run_worker':connector('shared_excelonlinebusiness','RunScriptProd',{'source':'me','drive':bindings['drive'],'file':bindings['workbook'],'scriptId':bindings['script'],'ScriptParameters/payload':"@string(outputs('Worker_input'))"},'Worker_input'),
      'Worker_output':action('Compose',"@json(body('Run_worker')?['result'])",'Run_worker'),
      'Projected_row':action('Compose',"@outputs('Worker_output')?['row']",'Worker_output'),
      'Read_parent':lookup('Projected_row'),
      'Guard_existing_parent':guard("and(equals(length(body('Read_parent')?['value']),1),equals(first(body('Read_parent')?['value'])?['ID'],"+str(bindings['item_id'])+"),equals(outputs('Projected_row')?['OpportunityKey'],'"+key+"'),not(empty(first(body('Read_parent')?['value'])?['@odata.etag'])),not(equals(first(body('Read_parent')?['value'])?['@odata.etag'],'*')))",'Read_parent','NIH_PARENT_REQUIRES_ADMISSION'),
      'Current_source':action('Compose',projection('Read_parent'),'Guard_existing_parent'),
      'Guard_last_source':guard("equals(outputs('Current_source'),variables('PreviousSource'))",'Current_source','NIH_PRESERVE_UNRECONCILED_SOURCE_EDIT'),
      'Guard_observation':guard("and(equals(outputs('Worker_output')?['format'],'rims-nih-worker-v1'),equals(outputs('Projected_row')?['RetrievedTimestampStatus'],'valid'),greaterOrEquals(ticks(outputs('Projected_row')?['RetrievedUTC']),ticks(outputs('Current_source')?['RetrievedUTC'])))",'Guard_last_source','NIH_OBSERVATION_REJECTED'),
      'Before_commit':guard('false' if fault=='before_commit' else 'true','Guard_observation','NIH_QUALIFICATION_BEFORE_COMMIT'),
    }
    body={f:'@coalesce('+item_value(f)+",'')" for f in fields}
    for f in ('URL','SourceRowURL'):body[f]="@if(empty("+item_value(f)+"),null,setProperty(setProperty(json('{}'),'Url',"+item_value(f)+"),'Description',"+item_value(f)+"))"
    process['Commit_source']=sp('HttpRequest',{'parameters/method':'POST','parameters/uri':f"_api/web/lists(guid'{table}')/items({bindings['item_id']})",'parameters/headers':{'Accept':'application/json;odata=nometadata','Content-Type':'application/json;odata=nometadata','X-HTTP-Method':'MERGE','IF-MATCH':'"0"' if fault=='stale_etag' else "@first(body('Read_parent')?['value'])?['@odata.etag']"},'parameters/body':'@string(outputs(\'Source_write\'))'},'Source_write')
    process['Source_write']=action('Compose',body,'Before_commit')
    process['Read_parent_after']=lookup('Commit_source')
    process['Stored_source']=action('Compose',projection('Read_parent_after'),'Read_parent_after')
    expected={f:'@coalesce('+item_value(f)+",'')" for f in fields}
    process['Expected_source']=action('Compose',expected,'Stored_source')
    human_checks=[f"equals(first(body('Read_parent_after')?['value'])?['{f}'],first(body('Read_parent')?['value'])?['{f}'])" for f in sorted(HUMAN)]
    process['Verify_commit']=guard("and(equals(outputs('Stored_source'),outputs('Expected_source')),"+','.join(human_checks)+")",'Expected_source','NIH_COMMIT_READBACK_OR_REVIEW_DRIFT')
    process['Commit_receipt']=action('Compose',{'format':'rims-nih-commit-v1','context_sha256':ctx_sha,'opportunity_key':key,'register_item_id':bindings['item_id'],'run':"@workflow()?['run']?['name']",'observed_utc':"@outputs('Observed_utc')",'archive_folder':"@outputs('Run_folder')",'source_projection':"@outputs('Stored_source')",'review_fields_written':False},'Verify_commit')
    commit_name="@concat('nih-chain-commit-',workflow()?['run']?['name'],'.json')"
    process['Save_commit_receipt']=save(commit_name,'Commit_receipt','Commit_receipt')
    commit_path="@concat('"+folder+"/nih-chain-commit-',workflow()?['run']?['name'],'.json')"
    process['Read_commit_receipt']=read(commit_path,'Save_commit_receipt')
    process['Verify_commit_receipt']=guard("equals(base64(string(outputs('Commit_receipt'))),body('Read_commit_receipt')?['$content'])",'Read_commit_receipt','NIH_COMMIT_RECEIPT_MISMATCH')
    process['Before_refresh']=guard('false' if fault=='before_refresh' else 'true','Verify_commit_receipt','NIH_QUALIFICATION_BEFORE_REFRESH')
    process['Refresh_grants_model']=connector('shared_powerbi','RefreshDataset',{'groupid':bindings['workspace'],'datasetid':bindings['model']},'Before_refresh')
    query=("EVALUATE ROW(\"MatchingParent\",COUNTROWS(FILTER('Grants Registry','Grants Registry'[OpportunityKey]=\""+key+"\" && 'Grants Registry'[EvidenceHash]=\"@{outputs('Projected_row')?['EvidenceHash']}\")),\"Parents\",COUNTROWS('Grants Registry'),\"Occurrences\",COUNTROWS('Grants Deadline Occurrences'))")
    poll={'Query_current_model':connector('shared_powerbi','ExecuteDatasetQuery',{'groupid':bindings['workspace'],'datasetid':bindings['model'],'specification/query':query,'specification/serializerSettings/includeNulls':True}),
      'Model_row':action('Compose',"@first(coalesce(body('Query_current_model')?['firstTableRows'],body('Query_current_model')?['results']?[0]?['tables']?[0]?['rows']))",'Query_current_model'),
      'Set_model_matches':action('SetVariable',{'name':'ModelMatches','value':"@and(equals(outputs('Model_row')?['[MatchingParent]'],1),equals(outputs('Model_row')?['[Parents]'],1),equals(outputs('Model_row')?['[Occurrences]'],7))"},'Model_row'),
      'Wait_if_stale':{'type':'If','expression':"@not(variables('ModelMatches'))",'runAfter':{'Set_model_matches':['Succeeded']},'actions':{'Wait_for_model':{'type':'Wait','inputs':{'interval':{'count':10,'unit':'Second'}},'runAfter':{}}},'else':{'actions':{}}}}
    process['Until_model_current']={'type':'Until','expression':"@equals(variables('ModelMatches'),true)",'limit':{'count':18,'timeout':'PT5M'},'runAfter':{'Refresh_grants_model':['Succeeded']},'actions':poll}
    process['Guard_model_current']=guard("variables('ModelMatches')",'Until_model_current','NIH_MODEL_DID_NOT_REACH_CURRENT_SOURCE')
    process['Chain_receipt']=action('Compose',{'format':'rims-nih-chain-v1','source':baseline['Source'],'context_sha256':ctx_sha,'run':"@workflow()?['run']?['name']",'archive_folder':"@outputs('Run_folder')",'observed_utc':"@outputs('Observed_utc')",'register_item_id':bindings['item_id'],'evidence_hash':"@outputs('Projected_row')?['EvidenceHash']",'register_updated':True,'model_current_data_visible':True,'model_parent_count':1,'model_occurrence_count':7,'refresh_request_id':"@outputs('Refresh_grants_model')?['headers']?['RequestId']",'notification_delivered':False,'review_fields_written':False,'schedule_vintage_preserved':True,'refresh_terminal_status_polled_in_flow':False},'Guard_model_current')
    process['Save_chain_receipt']=save("@concat('nih-chain-success-',workflow()?['run']?['name'],'.json')",'Chain_receipt','Chain_receipt')
    process['Read_chain_receipt']=read("@concat('"+folder+"/nih-chain-success-',workflow()?['run']?['name'],'.json')",'Save_chain_receipt')
    process['Verify_chain_receipt']=guard("equals(base64(string(outputs('Chain_receipt'))),body('Read_chain_receipt')?['$content'])",'Read_chain_receipt','NIH_CHAIN_RECEIPT_MISMATCH')
    actions['Processing']={'type':'Scope','runAfter':{'Acquisition':['Succeeded']},'actions':process}
    failure={'format':'rims-nih-chain-failure-v1','source':baseline['Source'],'run':"@workflow()?['run']?['name']",'archive_folder':"@outputs('Run_folder')",'observed_utc':"@outputs('Observed_utc')",'actions':"@result('Processing')",'notification_delivered':False,'recovery':'Preserve current records, reviews and model cache. Reconcile conditional commit/receipt before explicit replay; never retry a stale write blindly.'}
    failed={'Chain_failure':action('Compose',failure)}
    failed['Save_chain_failure']=save("@concat('nih-chain-failure-',workflow()?['run']?['name'],'.json')",'Chain_failure','Chain_failure')
    failed['Read_chain_failure']=read("@concat('"+folder+"/nih-chain-failure-',workflow()?['run']?['name'],'.json')",'Save_chain_failure')
    failed['Verify_chain_failure']=guard("equals(base64(string(outputs('Chain_failure'))),body('Read_chain_failure')?['$content'])",'Read_chain_failure','NIH_CHAIN_FAILURE_RECEIPT_MISMATCH')
    failed['Terminate_chain_failure']={'type':'Terminate','runAfter':{'Verify_chain_failure':['Succeeded','Failed','TimedOut','Skipped']},'inputs':{'runStatus':'Failed','runError':{'code':'NihChainRejected','message':'Unattended grants stage failed. Inspect retained stage/commit receipts; preserve human edits and last-good model.'}}}
    actions['Observe_processing_failure']={'type':'Scope','runAfter':{'Processing':['Failed','TimedOut']},'actions':failed}
    for alias,connection in [('shared_excelonlinebusiness',bindings['excel_connection']),('shared_powerbi',bindings['powerbi_connection'])]:
        props['connectionReferences'][alias]={'id':'/providers/Microsoft.PowerApps/apis/'+alias,'connectionName':connection,'source':'Embedded'}
    return result
