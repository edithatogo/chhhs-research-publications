"""Prepare the four-part additive nine-field alignment diff; no native writes."""
import base64,copy,json,re
from pathlib import Path
FIELDS=['FunderNames','GrantIDs','MeSHHeadings','AuthorKeywords','AffiliationsRaw']
META=['SourceObservedUTCRaw','RawResponseSHA256','ProjectionDiagnostics']
ROOT=Path(__file__).resolve().parents[1]

def columns(names,calculated=False,datetime_names=()):
    return ''.join('\tcolumn '+n+'\n\t\tdataType: '+('dateTime' if n in datetime_names else 'string')+'\n\t\tsummarizeBy: none\n\t\tsourceColumn: '+('['+n+']' if calculated else n)+'\n\n' for n in names)

def add_columns(text,names,calculated=False,datetime_names=()):
    marker='\tpartition '
    if text.count(marker)!=1:raise ValueError('Exact single partition required')
    start=text.index(marker)
    return text[:start]+columns(names,calculated,datetime_names)+text[start:]

def build(baseline,qualification):
    if qualification.get('physical_schema_verified') is not True:raise ValueError('Native physical destination schema required')
    if not re.fullmatch(r'[0-9a-f]{64}',qualification.get('schema_sha256','')):raise ValueError('Exact physical schema fingerprint required')
    limits=qualification.get('limits',{})
    if set(limits)!=set(FIELDS) or any(type(v) is not int or v<1 for v in limits.values()):raise ValueError('Five positive qualified physical limits required')
    parts=baseline['definition']['parts']
    if baseline['definition']['format']!='TMDL' or len(parts)!=46 or len({p['path'] for p in parts})!=46:raise ValueError('Exact accepted46-part baseline required')
    texts={p['path']:base64.b64decode(p['payload'],validate=True).decode() for p in parts}
    expression=texts['definition/expressions.tmdl']
    if 'expression fnProjectRetainedOpenAlexAligned =' in expression:raise ValueError('Alignment already installed; read back')
    limits_m='['+','.join(n+'='+str(limits[n]) for n in FIELDS)+']'
    expression+='\nexpression pOpenAlexAlignedFieldLimits = '+limits_m+'\n'
    body=(ROOT/'powerquery/fnProjectRetainedOpenAlexAligned.m').read_text().strip()
    expression+='\nexpression fnProjectRetainedOpenAlexAligned =\n'+'\n'.join('\t\t'+line for line in body.splitlines())+'\n'
    additions=[f+'_OpenAlex' for f in FIELDS]+META
    workpath='definition/tables/OpenAlexWorks.tmdl';works=add_columns(texts[workpath],additions)
    old='source = fnProjectRetainedOpenAlex(OpenAlexBootstrapObservations)'
    if works.count(old)!=1:raise ValueError('Current validated source partition drift')
    works=works.replace(old,'source = fnProjectRetainedOpenAlexAligned(OpenAlexBootstrapObservations,pOpenAlexAlignedFieldLimits)')
    ctxpath='definition/tables/OpenAlexPublicationContext.tmdl'
    dates=[f+'_OpenAlex_ObservedUTC' for f in FIELDS]
    context=add_columns(texts[ctxpath],additions+dates,True,dates)
    anchor='"__At", LOOKUPVALUE(OpenAlexWorks[OpenAlexObservedUTC],OpenAlexWorks[DOI],[__DOI]))'
    if context.count(anchor)!=1:raise ValueError('Context lookup anchor drift')
    lookups=',\n'+',\n'.join('\t\t\t\t    "__'+n+'", LOOKUPVALUE(OpenAlexWorks['+n+'],OpenAlexWorks[DOI],[__DOI])' for n in additions)
    context=context.replace(anchor,anchor[:-1]+lookups+')')
    end='"OAUrl_OpenAlex_ObservedUTC",IF(NOT ISBLANK([__URL]),[__At]))'
    if context.count(end)!=1:raise ValueError('Context existing fields drift')
    selected=',\n'+',\n'.join('\t\t\t\t    "'+n+'",[__'+n+']' for n in additions)
    selected+=',\n'+',\n'.join('\t\t\t\t    "'+f+'_OpenAlex_ObservedUTC",IF(NOT ISBLANK([__'+f+'_OpenAlex]),[__At])' for f in FIELDS)
    context=context.replace(end,end[:-1]+selected+')')
    provpath='definition/tables/OpenAlexFieldProvenance.tmdl';provenance=add_columns(texts[provpath],META,True)
    source_start=provenance.index('\t\t\t\tUNION(')
    union=provenance[source_start:].strip()
    if not union.startswith('UNION(') or not union.endswith(')'):raise ValueError('Provenance union drift')
    branches=[]
    for field,column in [('OpenAlexID','OpenAlexWorkID')]+[(f,f+'_OpenAlex') for f in FIELDS]:
        observed='[OpenAlexObservedUTC]' if field=='OpenAlexID' else '['+column+'_ObservedUTC]'
        branches.append('SELECTCOLUMNS(OpenAlexPublicationContext,"CanonicalKey",[CanonicalKey],"DOI",[DOI],"ProviderWorkID",[OpenAlexWorkID],"Field","'+field+'","Source","OpenAlex","IncomingValue",['+column+'],"SelectedValue",['+column+'],"AttemptObservedUTC",[OpenAlexObservedUTC],"SelectedObservedUTC",'+observed+',"Decision",IF(ISBLANK(['+column+']),"preserve_missing","source_observation"))')
    union=union[:-1]+',\n'+',\n'.join(branches)+'\n)'
    projected='ADDCOLUMNS(\n'+union+',\n'+',\n'.join('"'+n+'",LOOKUPVALUE(OpenAlexWorks['+n+'],OpenAlexWorks[OpenAlexWorkID],[ProviderWorkID])' for n in META)+'\n)'
    provenance=provenance[:source_start]+'\n'.join('\t\t\t\t'+line for line in projected.splitlines())+'\n'
    edits={'definition/expressions.tmdl':expression,workpath:works,ctxpath:context,provpath:provenance}
    result=copy.deepcopy(baseline)
    for p in result['definition']['parts']:
        if p['path'] in edits:p['payload']=base64.b64encode(edits[p['path']].encode()).decode()
    receipt={'kind':'openalex_nine_field_native_alignment_preparation_v1','changed_parts':list(edits),'preserved_parts':42,'parts':46,'existing_expression_prefix_preserved':expression.startswith(texts['definition/expressions.tmdl']),'fields_added':FIELDS,'metadata_added':META,'existing_native_mapper_body_unchanged':True,'new_tables':0,'new_connections':0,'provider_calls':0,'expected_works':48,'expected_context_rows':51,'expected_field_provenance_rows':459,'native_acceptance':False,'qualified_target_schema_sha256':qualification.get('schema_sha256')}
    return result,receipt
