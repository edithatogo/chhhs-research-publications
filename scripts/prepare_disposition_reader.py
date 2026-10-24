"""Prepare create-only disposition downloads and one existing-view patch.

No network, data mutation, sharing or permission changes.
"""
import csv
import hashlib
import io
import json
from urllib.parse import quote, urlsplit
from scripts.dispose_publication_source_differences import FIELDS
from scripts.export_publication_register import safe_cell


def prepare(result, current_rows, prior_view, site_url, server_folder, old_links):
    rows={r['Id']:r for r in current_rows}
    if len(rows)!=len(current_rows):raise ValueError('Duplicate current registry identity')
    pairs=result['items'];seen=set()
    labels={'uncertain_source_difference_preserved','title_presentation_equivalent_preserved','bounded_display_full_source_retained'}
    for pair in pairs:
        ident,field=pair['item_id'],pair['field']
        if type(ident) is not int or ident<=0 or field not in FIELDS or (ident,field) in seen:
            raise ValueError('Invalid/duplicate retained pair')
        seen.add((ident,field));row=rows.get(ident)
        if row is None or row.get('field_1')!=pair['source_key'] or row.get(FIELDS[field])!=pair['retained_value']:
            raise ValueError('Current retained value/source identity changed')
        if pair['disposition'] not in labels:raise ValueError('Unknown disposition')
        if pair['disposition']!='uncertain_source_difference_preserved' and field!='Title':
            raise ValueError('Explained-title category cannot resolve another field')
        if pair['disposition']=='bounded_display_full_source_retained':
            full=pair['source_value']
            if not isinstance(full,str) or len(full)<=255 or row.get('SourceFullTitle')!=full or row['Title']!=full[:255]:
                raise ValueError('Full-source title retention proof drift')
    ids=sorted({p['item_id'] for p in pairs})
    if len(pairs)!=result['difference_count'] or len(ids)!=result['record_count']:
        raise ValueError('Incomplete result coverage')
    uncertain=sum(p['disposition']=='uncertain_source_difference_preserved' for p in pairs)
    explained=len(pairs)-uncertain
    digest=hashlib.sha256(json.dumps(result,sort_keys=True,ensure_ascii=False).encode()).hexdigest()[:12]
    prefix='publication-disposition-20261024-'+digest
    payloads={prefix+'.json':(json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode()}
    table=io.StringIO(newline='');columns=['RegistryItemID','SourceKey','Field','RetainedValueJSON','SourceValueJSON','Disposition','CorrectionStatus']
    writer=csv.DictWriter(table,fieldnames=columns);writer.writeheader()
    for p in pairs:
        row=dict(RegistryItemID=p['item_id'],SourceKey=p['source_key'],Field=p['field'],RetainedValueJSON=json.dumps(p['retained_value'],ensure_ascii=False),SourceValueJSON=json.dumps(p['source_value'],ensure_ascii=False),Disposition=p['disposition'],CorrectionStatus='No correction applied; curated value preserved')
        writer.writerow({k:safe_cell(v) for k,v in row.items()})
    payloads[prefix+'.csv']=b'\xef\xbb\xbf'+table.getvalue().encode()
    payloads[prefix+'-prior-reader.json']=(json.dumps(prior_view,ensure_ascii=False,indent=2)+'\n').encode()
    origin=urlsplit(site_url)
    if origin.scheme!='https' or not server_folder.startswith(origin.path.rstrip('/')+'/'):
        raise ValueError('Use the existing same-site reporting folder')
    link=lambda name:origin.scheme+'://'+origin.netloc+quote(server_folder+'/'+name,safe='/')
    csv_url,json_url=link(prefix+'.csv'),link(prefix+'.json')
    text=lambda s:{'elmType':'div','txtContent':s}
    anchor=lambda label,url:{'elmType':'a','attributes':{'href':url,'target':'_blank','rel':'noopener noreferrer'},'txtContent':label}
    expression="'Uncertain source/curation difference'"
    for p in reversed(pairs):
        if p['disposition']=='title_presentation_equivalent_preserved':label='Explained title: presentation only'
        elif p['disposition']=='bounded_display_full_source_retained':label='Explained title: full source retained'
        else:continue
        if any(c in p['source_key'] for c in ("'", '\\', '\n', '\r')):
            raise ValueError('Unsupported source key in view expression')
        expression=f"if([$field_1] == '{p['source_key']}', '{label}', {expression})"
    formatter={'$schema':'https://developer.microsoft.com/json-schemas/sp/v2/view-formatting.schema.json','hideColumnHeader':True,'rowFormatter':{'elmType':'div','style':{'display':'flex','flex-direction':'column','padding':'10px','border-bottom':'1px solid #ddd'},'children':[
        text('Verified retained difference disposition | 24 October 2026'),
        text(f'{uncertain} uncertain semantic pairs | {explained} explained title differences'),
        text(f'{len(pairs)} field pairs across {len(ids)} records. Curated values preserved; no corrections applied.'),
        text('='+expression),
        {'elmType':'button','customRowAction':{'action':'defaultClick'},'txtContent':'[$Title]','style':{'text-align':'left','font-weight':'600'}},
        text("='Current retained month: ' + if([$field_6] == '', 'unknown', [$field_6]) + ' | Precision: ' + [$field_8]"),
        anchor('Verified disposition - all 147 pairs (CSV)' if len(pairs)==147 else 'Verified disposition (CSV)',csv_url),
        anchor('Retained and source values with dispositions (JSON)',json_url),
        anchor('Historical 15 October comparisons (CSV)',old_links['csv']),
        anchor('Historical 15 October values (JSON)',old_links['json']),
        anchor('Unknown publication months',old_links['uncertainty']),
        text('Source proposals belong to the retained 15 October generation. Paired registry values verified 24 October; no new source harvest or author identity decision.')]}}
    query='<Where><In><FieldRef Name="ID"/><Values>'+''.join(f'<Value Type="Counter">{i}</Value>' for i in ids)+'</Values></In></Where><OrderBy><FieldRef Name="ID" Ascending="TRUE"/></OrderBy>'
    patch={'Title':'Source differences | Verified disposition','ViewQuery':query,'CustomFormatter':json.dumps(formatter,ensure_ascii=False,separators=(',',':'))}
    manifest={'kind':'publication_disposition_reader_v1','uncertain_semantic_pairs':uncertain,'explained_title_pairs':explained,'field_pairs':len(pairs),'records':len(ids),'native_values_changed':False,'files':{name:{'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()} for name,raw in payloads.items()}}
    payloads[prefix+'-manifest.json']=(json.dumps(manifest,indent=2)+'\n').encode()
    return payloads,patch,{'csv':csv_url,'json':json_url,'expected_ids':ids,'counts':manifest}
