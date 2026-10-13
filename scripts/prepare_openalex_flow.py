"""Add bounded missing-only OpenAlex context to an existing registry flow.

No invocation/activation or schema changes. Deployment adapter must verify exact
native lease, connection refs and source-only model acceptance independently.
"""
import copy

FIELDS={'OpenAlexID':'OpenAlexWorkID','CitationCount_OpenAlex':'CitationCount_OpenAlex',
        'OpenAccessStatus':'OpenAccessStatus_OpenAlex','OAUrl':'OAUrl_OpenAlex'}
QUERY='''EVALUATE
VAR Ready = COUNTROWS(OpenAlexWorks)>0 && COUNTROWS(OpenAlexPublicationContext)>0 && COUNTROWS(OpenAlexPublicationContext)=DISTINCTCOUNT(OpenAlexPublicationContext[CanonicalKey])
RETURN SELECTCOLUMNS(FILTER(OpenAlexPublicationContext,IF(Ready,TRUE(),ERROR("OPENALEX_CONTEXT_NOT_READY"))),
"CanonicalKey",[CanonicalKey],"OpenAlexWorkID",[OpenAlexWorkID],
"CitationCount_OpenAlex",[CitationCount_OpenAlex],"OpenAccessStatus_OpenAlex",[OpenAccessStatus_OpenAlex],"OAUrl_OpenAlex",[OAUrl_OpenAlex],
"OpenAlexObservedUTC",[OpenAlexObservedUTC],"CitationCount_OpenAlex_ObservedUTC",[CitationCount_OpenAlex_ObservedUTC],
"OpenAccessStatus_OpenAlex_ObservedUTC",[OpenAccessStatus_OpenAlex_ObservedUTC],"OAUrl_OpenAlex_ObservedUTC",[OAUrl_OpenAlex_ObservedUTC])'''

def missing(value):return value is None or isinstance(value,str) and not value.strip()
def fill(existing,candidate):
    """Reference decision: unknown-age existing values cannot be overwritten."""
    result=copy.deepcopy(existing)
    work=candidate.get('OpenAlexWorkID')
    if not missing(existing.get('OpenAlexID')) and work!=existing['OpenAlexID']:
        return result,'work_id_conflict'
    for field,source in FIELDS.items():
        if missing(result.get(field)) and not missing(candidate.get(source)):result[field]=candidate[source]
    return result,'missing_only'

def build(definition):
    d=copy.deepcopy(definition);a=d['actions'];loop=a['Apply_to_each_Publication'];nested=loop['actions']
    if 'Run_OpenAlex_Context_Query' in a:raise ValueError('OpenAlex integration already exists')
    assert loop['runtimeConfiguration']['concurrency']['repetitions']==1
    query=copy.deepcopy(a['Run_publication_rows_query']);query.pop('metadata',None)
    query['inputs']['parameters']['specification/query']=QUERY
    query['runAfter']={'Run_publication_rows_query':['Succeeded']}
    a['Run_OpenAlex_Context_Query']=query
    loop['runAfter']['Run_OpenAlex_Context_Query']=['Succeeded']
    nested['Filter_OpenAlex_Context']={'type':'Query','inputs':{
        'from':"@body('Run_OpenAlex_Context_Query')?['results'][0]?['tables'][0]?['rows']",
        'where':"@equals(item()?['[CanonicalKey]'],items('Apply_to_each_Publication')?['[CanonicalKey]'])"},
        'runAfter':{'Condition_Duplicate_SourceKey':['Succeeded']}}
    nested['Compose_OpenAlex_Context']={'type':'Compose',
        'inputs':"@if(greater(length(body('Filter_OpenAlex_Context')),1),json('OPENALEX_DUPLICATE_CONTEXT'),if(equals(length(body('Filter_OpenAlex_Context')),1),first(body('Filter_OpenAlex_Context')),json('{}')))",
        'runAfter':{'Filter_OpenAlex_Context':['Succeeded']}}
    old="first(body('SharePoint_Get_items')?['value'])?"
    work="outputs('Compose_OpenAlex_Context')?['[OpenAlexWorkID]']"
    conflict="and(not(empty(trim(string("+old+"['OpenAlexID'])))),not(equals("+old+"['OpenAlexID'],"+work+")))"
    nested['Compose_OpenAlex_Fill_Decision']={'type':'Compose','inputs':"@if(empty("+work+"),'no_context',if("+conflict+",'work_id_conflict','missing_only'))",
        'runAfter':{'Compose_OpenAlex_Context':['Succeeded']}}
    condition=nested['Condition_Is_New_Publication'];condition['runAfter']={'Compose_OpenAlex_Fill_Decision':['Succeeded']}
    create=condition['actions']['SharePoint_Create_item']['inputs']['parameters']
    update=condition['else']['actions']['SharePoint_Update_item']['inputs']['parameters']
    for field,source in FIELDS.items():
        value="outputs('Compose_OpenAlex_Context')?['["+source+"]']"
        create['item/'+field]='@'+value
        target=old+"['"+field+"']"
        blank="equals("+target+",null)" if field=='CitationCount_OpenAlex' else "empty(trim(string("+target+")))"
        present="not(equals("+value+",null))" if field=='CitationCount_OpenAlex' else "not(empty(trim(string("+value+"))))"
        update['item/'+field]="@if(and(equals(outputs('Compose_OpenAlex_Fill_Decision'),'missing_only'),"+blank+","+present+"),"+value+","+target+")"
    return d

def transport_definition(definition):
    """Omit only the service-injected auth expression for native submission."""
    d=copy.deepcopy(definition)
    def visit(node):
        if not isinstance(node,dict):return
        inputs=node.get('inputs')
        if isinstance(inputs,dict) and 'authentication' in inputs:
            if inputs['authentication']!="@parameters('$authentication')":
                raise ValueError('Unexpected authentication cannot be normalised')
            del inputs['authentication']
        for collection in ['actions','triggers']:
            for child in node.get(collection,{}).values():visit(child)
        if 'else' in node:visit(node['else'])
        for case in node.get('cases',{}).values():visit(case)
        if 'default' in node:visit(node['default'])
    visit(d)
    return d
