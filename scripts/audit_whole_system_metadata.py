"""Account saved whole-system metadata without changing data or asserting truth.

This deliberately reuses the frozen native receipts and disposition scope. Literal
name segments never establish person identity. All detailed output stays private.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import html
import json
from pathlib import Path
import re
import subprocess
import sys

CODE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(CODE))
from scripts.export_publication_register import EXPORT_FIELDS, verify_written_exports
from scripts.reconcile_full_month_exports import reconcile as export_reconcile
from scripts.reconcile_registry_model_provenance import compare as provenance_compare
from scripts.reconcile_generation import reconcile

FIELDS={'Title':'Title','Authors':'field_3','Journal':'field_4',
        'PublicationYear':'field_5','PublicationMonth':'field_6',
        'PublicationDateRaw':'field_7','PublicationDatePrecision':'field_8',
        'PMID':'field_10','DOI':'field_11','PubMedURL':'field_12',
        'DORAURL':'field_13','MatchedFacilities':'field_14',
        'CHHHSAffiliatedAuthors':'field_15','AttributionEvidence':'field_16'}

def value(v):
    return v.get('Url') if isinstance(v,dict) else v

def decoded(v):
    if not isinstance(v,str):raise ValueError('Literal text required')
    for _ in range(2):v=html.unescape(v)
    return re.sub(r'</?(?:i|b|em|strong|sub|sup)>','',v)

def date_facets_equal(a,b):
    """Reorder complete literal facets; never parse, infer or fill a date."""
    if not isinstance(a,str) or not isinstance(b,str):return False
    try:
        parts=[p.split('=',1) for p in a.split('; ')]
        if any(len(p)!=2 for p in parts) or len({p[0] for p in parts})!=len(parts):return False
        fields=dict(parts)
        if set(fields)=={'MedlineDate'}:return fields['MedlineDate']==b
        return (bool(fields) and set(fields)<= {'Year','Month','Day'}
                and ' '.join(fields[k] for k in ['Year','Month','Day'] if fields.get(k))==b)
    except (ValueError,KeyError):return False

def pair_kind(pair,selected_kind,current,final):
    ident,field=pair['id'],pair['field'];a,b=pair['registry'],pair['canonical']
    if selected_kind=='populated_semantic_difference_preserved':
        verified=final.get((ident,field))
        if not verified or verified['retained_value']!=a or verified['source_value']!=b:
            raise ValueError('Unbound semantic disposition')
        if current.get(FIELDS[field])!=a:raise ValueError('Curated semantic drift')
        return verified['disposition']
    if selected_kind in ('native_exact_stored_range_recovered','native_missing_destination_filled'):
        if value(current.get(FIELDS[field]))!=b:raise ValueError('Native fill/range no longer exact')
        if selected_kind=='native_missing_destination_filled' and a not in (None,''):
            raise ValueError('A populated value is not a missing-value fill')
        return selected_kind
    if selected_kind=='equal_literal_name_segments_different_delimiters_order_repetition':
        segments=lambda v:{s.strip() for s in re.split('[;,]',decoded(v)) if s.strip()}
        if field!='CHHHSAffiliatedAuthors' or segments(a)!=segments(b):raise ValueError('Literal segment proof failed')
        return 'literal_segments_equal_not_person_identity'
    if selected_kind=='exact_decoded_text_representation_equivalent':
        if decoded(a)!=decoded(b):raise ValueError('Literal decoded-text proof failed')
        return selected_kind
    if selected_kind=='case_only_representation_equivalent':
        if decoded(a).casefold()!=decoded(b).casefold():raise ValueError('Case proof failed')
        return selected_kind
    if selected_kind is not None:raise ValueError('Unknown saved disposition')
    if b is None or isinstance(b,str) and not b.strip():return 'source_unknown_existing_retained'
    if field=='AttributionEvidence':return 'raw_affiliation_statements_vs_source_method_evidence_preserved'
    if field=='DORAURL' and a in (None,''):
        if value(current.get('field_13'))!=b:raise ValueError('Native URL fill no longer exact')
        return 'native_missing_link_now_filled'
    if field=='DOI' and isinstance(a,str) and isinstance(b,str) and a.casefold()==b.casefold():return 'doi_case_equivalent'
    if field=='PublicationDateRaw' and date_facets_equal(a,b):return 'exact_date_facet_representation_equivalent'
    if isinstance(a,str) and isinstance(b,str) and a.casefold()==b.casefold():return 'display_case_equivalent'
    raise ValueError('Difference lacks a verified disposition')

def audit(base,output):
    fingerprints={}
    def read(name):
        p=base/name;raw=p.read_bytes();fingerprints[name]=hashlib.sha256(raw).hexdigest();return json.loads(raw)
    packet_root='2026-10-24-reconciliation-links/accepted-v2/'
    packet=read(packet_root+'packet.json');old_oracle=read(packet_root+'result.json')
    if reconcile(packet)!=old_oracle or old_oracle['blockers']:raise ValueError('Key/month packet drift')
    cross=read(packet_root+'registry-crosswalk.json')
    snapshot=read('2026-10-15-registry-source-metadata-list-preimage-private.json')
    latest=read('2026-10-24-reader-disposition/before-items.json')
    independent=read('2026-10-24-reader-disposition/before-list.json')
    for capture in [snapshot['items'],latest]:
        if any(k.endswith('nextLink') for k in capture):raise ValueError('Incomplete registry capture')
    before={r['Id']:r for r in snapshot['items']['value']};now={r['Id']:r for r in latest['value']}
    if len(before)!=1648 or len(now)!=independent['ItemCount'] or len(now)!=1651 or not before.keys()<=now.keys():raise ValueError('Registry identity/count drift')
    for ident,row in before.items():
        for field in ['field_1','field_2','field_17','field_18','field_19']:
            if row.get(field)!=now[ident].get(field):raise ValueError('Identity, human review or first-observed drift')
    full=read('2026-10-15-t14-accepted-generation/full.json');monthly=read('2026-10-15-t14-accepted-generation/monthly.json')
    export_receipt=export_reconcile(full,monthly)
    model={r['CanonicalKey']:r for p in full['pages'] for r in p['records']}
    for name,envelope in [('full-register',full),('monthly-register',monthly)]:
        rows=[r for p in envelope['pages'] for r in p['records']]
        folder=base/'2026-10-15-t14-accepted-generation'/name
        manifest=read('2026-10-15-t14-accepted-generation/'+name+'/manifest.json')
        for file in ['publications.csv','publications.html']:
            raw=(folder/file).read_bytes();fingerprints[str((folder/file).relative_to(base))]=hashlib.sha256(raw).hexdigest()
            if fingerprints[str((folder/file).relative_to(base))]!=manifest['files'][file]:raise ValueError('Saved export bytes drift')
        verify_written_exports(rows,folder)
    original=read('2026-10-14-canonical-registry-field-differences-private.json')
    roles=read('2026-10-15-registry-source-metadata-difference-disposition-private.json')
    v3=read('2026-10-15-registry-current-source-disposition-v3-private.json')
    final_receipt=read('2026-10-24-source-difference-disposition/disposition-result.json')
    final={(r['item_id'],r['field']):r for r in final_receipt['items']}
    selected={(r['id'],r['field']):r['kind'] for r in v3['classified_items']}
    if len(selected)!=617 or len(final)!=147:raise ValueError('Disposition coverage drift')
    originals={(r['id'],r['field']):r for r in original['differences']}
    if len(originals)!=4638 or set(selected)!={(r['id'],r['field']) for r in roles['remaining_items']}:raise ValueError('Original partition drift')
    keyed={r['item_id']:r for r in cross};groups=defaultdict(list)
    for row in cross:groups[row['key']].append(row)
    details=[];counts=Counter();older=Counter()
    for pair,key in [(p,(p['id'],p['field'])) for p in original['differences']]:
        ident,field=key;canonical=model[keyed[ident]['key']]
        if value(before[ident].get(FIELDS[field]))!=pair['registry'] or canonical.get(field)!=pair['canonical']:raise ValueError('Original pair does not bind this lineage')
        kind=pair_kind(pair,selected.get(key),now[ident],final)
        counts[kind]+=1
        if key not in selected:older[kind]+=1
        details.append({**pair,'disposition':kind,'current_retained_value':value(now[ident].get(FIELDS[field]))})
    if dict(older)!=v3['previous_other_categories']:raise ValueError('Historical role accounting drift')
    allowed_changes={(r['id'],FIELDS[r['field']]) for r in details
                     if r['disposition'] in ('native_missing_link_now_filled',
                        'native_exact_stored_range_recovered','native_missing_destination_filled')}
    observed_changes=Counter()
    for ident,row in before.items():
        for field in set(FIELDS.values())|{'field_9'}:
            if value(row.get(field))!=value(now[ident].get(field)):
                if (ident,field) not in allowed_changes:raise ValueError('Unexplained later metadata change')
                observed_changes[field]+=1
    for (ident,field),pair in final.items():
        if pair['disposition']=='bounded_display_full_source_retained':
            full_title=pair['source_value']
            if (field!='Title' or not isinstance(full_title,str) or len(full_title)<=255
                    or now[ident].get('SourceFullTitle')!=full_title
                    or now[ident]['Title']!=full_title[:255]):raise ValueError('Full-title retention proof drift')
    # Verify every shared field, including exact cells omitted from the exception receipts.
    matrix=Counter();primary=[];secondary=[]
    normalization={(r['id'],r['field']):r for r in original['representation_normalizations']}
    for key,rows in groups.items():
        choices=[r for r in rows if r['source_key'].startswith('pubmed:')]
        if len(rows)>1 and len(choices)!=1:raise ValueError('Primary/secondary identity ambiguity')
        rep=choices[0] if choices else rows[0];ident=rep['item_id'];r=before[ident];m=model[key]
        secondary.extend(x for x in rows if x is not rep)
        primary.append({'Id':ident,'SourceKey':r['field_1'],'CanonicalKey':r['field_2'],
                        'SourceSet':r['field_9'],'PMID':r.get('field_10'),'DORAURL':value(r.get('field_13')),'ReviewStatus':r.get('field_17')})
        for field,internal in FIELDS.items():
            a,b=value(r.get(internal)),m.get(field);pair=(ident,field)
            if pair in originals:matrix['disposition_accounted']+=1
            elif pair in normalization:
                n=normalization[pair]
                if field!='PublicationYear' or type(a) not in (int,float) or type(b) not in (int,float) or a!=b or a!=n['registry'] or b!=n['canonical']:raise ValueError('Numeric representation drift')
                matrix['numeric_year_representation']+=1
            elif a==b:matrix['exact']+=1
            elif a in(None,'') and b in(None,''):matrix['null_empty_representation']+=1
            else:raise ValueError('Shared metadata field has unaccounted difference')
    provenance,provenance_details=provenance_compare(primary,[{'['+k+']':v for k,v in r.items()} for r in model.values()])
    if provenance['status']!='PASS_KEYED_PRIMARY_COVERAGE' or len(secondary)!=4:raise ValueError('Primary source coverage or secondary accounting failed')
    if sum(matrix.values())!=1341*len(FIELDS):raise ValueError('Shared-field coverage incomplete')
    report={'kind':'whole_system_saved_metadata_accounting_v1','status':'PASS_ACCOUNTED_WITH_EXPLICIT_UNCERTAINTY',
            'historical_generation_only':True,'canonical_publications':len(model),'shared_registry_fields':len(FIELDS),'shared_field_cells':sum(matrix.values()),'shared_field_accounting':dict(matrix),
            'original_exception_pairs':len(originals),'exception_dispositions':dict(counts),'registry_primary_rows':len(primary),'preserved_secondary_rows':len(secondary),'preserved_placeholder_rows':sum(not r.get('field_1') for r in before.values()),
            'later_keyed_additions_outside_selected_generation':sum(bool(now[i].get('field_1')) for i in now.keys()-before.keys()),
            'registry_human_reviews_first_observed_and_durable_keys_preserved':True,
            'later_shared_field_changes_all_match_accepted_fills_or_range_recovery':dict(observed_changes),
            'provenance':provenance,'export_records':1341+14,'export_fields_per_record':len(EXPORT_FIELDS),'export_cells_per_format':(1341+14)*len(EXPORT_FIELDS),'csv_and_html_all_fields_verified':True,
            'unknown_months_preserved':export_receipt['unknown_month_count'],'semantic_pairs_uncertain':counts['uncertain_source_difference_preserved'],
            'explained_title_pairs':counts['title_presentation_equivalent_preserved']+counts['bounded_display_full_source_retained'],
            'native_mutations':0,'new_native_runs':0,'operational_acceptance':False,
            'boundary':'Historical saved-generation accounting with a separately dated later registry checkpoint; no new source harvest, semantic adjudication, person matching, native uncertainty-field propagation, schedule or delivery acceptance.'}
    if report['semantic_pairs_uncertain']!=144 or report['explained_title_pairs']!=3:raise ValueError('Retained uncertainty scope changed')
    output.mkdir()
    for name,payload in [('summary.json',report),('field-pairs.json',details),('source-provenance-details.json',provenance_details),('preserved-secondary-rows.json',secondary),('input-hashes.json',fingerprints)]:
        with (output/name).open('x') as stream:json.dump(payload,stream,ensure_ascii=False,indent=2);stream.write('\n')
        (output/name).chmod(0o600)
    return report

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence-root',required=True,type=Path);parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args();base=args.evidence_root.resolve();output=args.output.resolve()
    if base!=base.parent.parent/'private/ops' or not output.is_relative_to(base) or output.exists():parser.error('Use a new ignored private/ops output directory')
    if subprocess.run(['git','check-ignore','-q','--',str(output)],cwd=base.parent.parent).returncode:parser.error('Output must be ignored')
    print(json.dumps(audit(base,output),indent=2))

if __name__=='__main__':main()
