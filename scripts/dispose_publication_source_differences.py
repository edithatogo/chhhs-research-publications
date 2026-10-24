"""Classify retained source differences against a complete current registry readback.

Read-only: no corrections, identity merges or native labels are written.
"""
from collections import Counter
import hashlib
import html
import json
import re

FIELDS = {'Title':'Title','Authors':'field_3','PublicationMonth':'field_6',
          'PublicationDateRaw':'field_7','PublicationDatePrecision':'field_8',
          'CHHHSAffiliatedAuthors':'field_15','MatchedFacilities':'field_14'}


def fingerprint(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()


def disposition(audit, current, pairs):
    if current.get('complete') is not True or current.get('next_links') != []:
        raise ValueError('Complete current paging required')
    rows=current['rows']
    if type(current.get('independent_count')) is not int or len(rows)!=current['independent_count']:
        raise ValueError('Independent current count required')
    index={r['Id']:r for r in rows}
    if len(index)!=len(rows):raise ValueError('Duplicate current item identity')
    if not current.get('observed_at') or not pairs.get('source_revision'):
        raise ValueError('Current capture time and retained source revision required')
    caseindex={}
    for case in pairs['cases']:
        registry=[r for r in case['records'] if r['record_id'].startswith('registry:')]
        if len(registry)!=1:raise ValueError('Exact retained case required')
        row=registry[0];ident=int(row['record_id'].split(':')[1])
        source=[r for r in case['records'] if r['record_id']==f'canonical-for:{ident}']
        if len(source)!=1 or source[0]['source_key']!=row['source_key'] or ident in caseindex:
            raise ValueError('Ambiguous case/source identity')
        caseindex[ident]=(row['source_key'],source[0]['values'])
    items=audit['preserved_semantic_items'];seen=set();out=[]
    for item in items:
        ident,field=item['id'],item['field'];identity=(ident,field)
        if identity in seen or field not in FIELDS:raise ValueError('Duplicate/unsupported difference')
        seen.add(identity)
        if ident not in index or ident not in caseindex:raise ValueError('Missing current item or source pair')
        row=index[ident];sourcekey,source=caseindex[ident]
        if row.get('field_1')!=sourcekey or field not in source or source[field]!=item['canonical']:
            raise ValueError('Retained source/identity drift')
        retained,proposed=item['registry'],item['canonical']
        if row.get(FIELDS[field])!=retained:raise ValueError('Current curated value drift; rebaseline explicitly')
        label='uncertain_source_difference_preserved'
        if retained==proposed:raise ValueError('Equal pair is not a difference')
        # Only literal formatting equivalence for titles, never name/person matching.
        if field=='Title' and isinstance(retained,str) and isinstance(proposed,str):
            def presentation(value):
                for _ in range(2):value=html.unescape(value)
                return re.sub(r'</?(?:i|b|em|strong|sub|sup)>','',value)
            if presentation(retained)==presentation(proposed):label='title_presentation_equivalent_preserved'
            elif len(proposed)>255 and retained==proposed[:255] and row.get('SourceFullTitle')==proposed:
                label='bounded_display_full_source_retained'
        out.append({'item_id':ident,'source_key':sourcekey,'field':field,
                    'retained_value':retained,'source_value':proposed,'disposition':label,
                    'correction_provenance':'not-established-by-selected-evidence',
                    'write_authorized':False,'manual_record_approval_required':False})
    return {'kind':'publication_source_disposition_readonly_v1','observed_at':current['observed_at'],
            'source_revision':pairs['source_revision'],'source_scope':'retained named generation; no new source harvest',
            'input_fingerprints':{'audit':fingerprint(audit),'current':fingerprint(current),'pairs':fingerprint(pairs)},
            'difference_count':len(out),'record_count':len({r['item_id'] for r in out}),
            'disposition_counts':dict(Counter(r['disposition'] for r in out)),
            'uncertain_field_counts':dict(Counter(r['field'] for r in out if r['disposition']=='uncertain_source_difference_preserved')),
            'all_current_curated_values_preserved':True,'native_write_performed':False,
            'native_uncertainty_labels_deployed':False,'semantic_values_adjudicated':False,
            'items':out}
