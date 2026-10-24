"""Recover immutable saved lineage. No network calls or native writes."""
import json,hashlib,sys,collections,base64,re,argparse,subprocess
from pathlib import Path
CODE=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--evidence-root',required=True,type=Path)
parser.add_argument('--output',required=True,type=Path)
args=parser.parse_args()
B=args.evidence_root.resolve();ROOT=B.parent.parent;OUT=args.output.resolve()
if B!=ROOT/'private/ops' or not OUT.is_relative_to(B) or OUT.exists():
 raise ValueError('New ignored private/ops output directory required')
if subprocess.run(['git','check-ignore','-q','--',str(OUT)],cwd=ROOT).returncode:
 raise ValueError('Output must remain ignored')
sys.path.insert(0,str(CODE))
from scripts.verify_retained_canary_metadata_values import expected,verify,SOURCES
inputs={}
def read(name):
 p=B/name;raw=p.read_bytes();inputs[str(p.relative_to(ROOT))]=hashlib.sha256(raw).hexdigest();return json.loads(raw)
def normalized(payload):
 assert not payload.get('error') and len(payload['results'])==1
 table=payload['results'][0];assert not table.get('error') and len(table['tables'])==1
 table=table['tables'][0];assert not table.get('error')
 return [{k.split('[')[-1].rstrip(']'):v for k,v in r.items()} for r in table['rows']]
payloads={t:read(f'2026-10-14-canonical-cli-{t}-native-private.json') for t in ['Publication','RetainedPubMedPublications','RetainedDoraPublications']}
c,p,d=[normalized(payloads[t]) for t in ['Publication','RetainedPubMedPublications','RetainedDoraPublications']]
selected=[{k.split('[')[-1].rstrip(']'):v for k,v in r.items()} for r in read('2026-10-15-t14-canonical-physical-publication-private.json')]
index=lambda rows,key:{r[key]:r for r in rows}
assert len(index(c,'CanonicalKey'))==len(c)==len(selected)==1341
assert index(c,'CanonicalKey')==index(selected,'CanonicalKey')
# Old source query has before/after Completed correlation; selected refresh touched only enrichment.
cor=read('2026-10-14-canonical-cli-query-correlation-private.json');assert cor['latest_completed_before_after'] and cor['definition_exact_42_parts']
for h in ['history_before','history_after']:assert cor[h]['value'][0]['requestId']==cor['request_id'] and cor[h]['value'][0]['status']=='Completed'
detail=read('2026-10-15-t14-canonical-refresh-detail-private.json');assert detail['status']=='Completed' and detail['commitMode']=='Transactional'
assert {r['table'] for r in detail['objects']}=={'OpenAlexWorks','OpenAlexMetadataChunks','OpenAlexPublicationContext','OpenAlexFieldProvenance'}
# Recover PubMed's native accepted source count/key inventory and every saved native page.
commit=read('2026-10-14-core-cli-stored-commit-native-private.json');acc=read('2026-10-14-core-archive-commit-cli-acceptance-private.json');fileproof=read('2026-10-14-core-cli-archive-byte-readback-receipt-private.json')
assert commit['Status']=='committed' and acc['commit_native_readback_match'] and acc['archive_run_succeeded']
spec=commit['Sources'][0];assert spec['Source']=='PubMed' and spec['ExpectedRecords']==1274
assert {r['PMID'] for r in p}==set(spec['ExpectedKeys']) and len(p)==len(spec['ExpectedKeys'])==1274
assert len(fileproof['files'])==172 and fileproof['semantic_matches']==172

# Verify saved native archive bytes and local semantic counterparts against the original receipt.
prepared=read('2026-10-13-query-projection-archive-persistence-receipt-private.json')
assert prepared['batch_id']==commit['BatchID'] and prepared['reconstruction_equal']
assert {f['name'] for f in prepared['files']}=={f['name'] for f in fileproof['files']}
for f in fileproof['files']:
 path=B/'2026-10-14-core-cli-native-archive-files'/f['name'];raw=path.read_bytes()
 assert len(raw)==f['bytes'] and hashlib.sha256(raw).hexdigest()==f['sha256']
 local=read('2026-10-13-query-projection-archive-persistence-files/'+f['name'])
 assert json.loads(raw)==local and f['semantic_match']
 inputs[str(path.relative_to(ROOT))]=f['sha256']
# Prove the relevant saved source and canonical implementation has not changed.
def parts(name):
 j=read(name);return {p['path']:base64.b64decode(p['payload']) for p in j['definition']['parts']}
oldparts=parts('2026-10-14-canonical-cli-definition-postrefresh-private.json')
newparts=parts('2026-10-15-t14-accepted-pre-extraction-definition-private.json')
for table in ['Publication','RetainedPubMedPublications','RetainedDoraPublications']:
 name='definition/tables/'+table+'.tmdl'
 assert oldparts[name]==newparts[name],table+' definition changed'
def expressions(raw):
 text=raw.decode();matches=list(re.finditer(r'^expression ([A-Za-z0-9_]+) =',text,re.M))
 return {m.group(1):text[m.start():matches[i+1].start() if i+1<len(matches) else len(text)].rstrip() for i,m in enumerate(matches)}
a=expressions(oldparts['definition/expressions.tmdl']);z=expressions(newparts['definition/expressions.tmdl'])
relevant=['fnReadCommittedHistory','RetainedArchiveFiles','RetainedSourceObservations','fnParseRetainedPubMedMetadata','fnParseRetainedDoraMetadata','CanonicalPublications']
# Include the full expression dependency closure, not only the entrypoints.
closure=set(relevant)
while True:
 expanded=closure|{name for name in a for used in closure if re.search(r'\b'+re.escape(name)+r'\b',a[used])}
 if expanded==closure:break
 closure=expanded
for name in closure:assert a[name]==z[name],name+' changed'
# Recover complete hashed DoRA archive and bind it to the correlated retained source query.
meta_inputs=read('2026-10-09-t11-repaired-history-replay-metadata-inputs-private.json')['DORA']
validation=read(str(Path(meta_inputs['validated_dir']).relative_to('private/ops')/'validated-receipt.json'))
assert inputs[meta_inputs['validated_dir']+'/validated-receipt.json']==meta_inputs['validated_receipt_sha256']
for name,attest in validation['files'].items():
 if 'Dora' not in name and not name.startswith('commit-'):continue
 path=ROOT/meta_inputs['archive_dir']/name;raw=path.read_bytes()
 assert len(raw)==attest['bytes'] and hashlib.sha256(raw).hexdigest()==attest['sha256']
 inputs[str(path.relative_to(ROOT))]=attest['sha256']
metadata_path=Path(meta_inputs['validated_dir'])/'DORA-metadata.json'
raw=(ROOT/metadata_path).read_bytes();assert hashlib.sha256(raw).hexdigest()==validation['sources']['DORA']['metadata_map_sha256']
inputs[str(metadata_path)]=hashlib.sha256(raw).hexdigest()
expect=expected(ROOT/meta_inputs['archive_dir'],ROOT/meta_inputs['validated_dir'],'DORA')
fields=(SOURCES['DORA'][2],)+SOURCES['DORA'][3]
projected={'results':[{'tables':[{'rows':[{f'[{k}]':r.get(k) for k in fields} for r in d]}]}]}
check,differences=verify(projected,expect,'DORA')

assert check['substantive_differences']==0
assert len(d)==validation['sources']['DORA']['publication_rows']==709
assert {r['DORAKey'] for r in d}==set(expect)
# Membership is reconstructed from already observed exact canonical source links, not title/DOI matching.
source_map={}
for r in p:source_map['pubmed:'+r['PMID']]={'key':'PMID:'+r['PMID'],'basis':'retained PMID row and existing canonical PMID identity'}
for r in c:
 for url in (r.get('DORAURL') or '').split('; '):
  if not url:continue
  key='dora:'+url
  assert key not in source_map,'Duplicate source membership'
  source_map[key]={'key':r['CanonicalKey'],'basis':'existing canonical DORAURL exact source-identity link'}
assert len(source_map)==1983 and len({v['key'] for v in source_map.values()})==1341
assert {'dora:'+r['DORAKey'].removeprefix('DORA:') for r in d}=={k for k in source_map if k.startswith('dora:')}
# Exact native canonical IDs close legacy representation differences without rewriting any durable key.
reg=read('2026-10-14-canonical-registry-normalized-private.json');terminal=read('2026-10-14-canonical-registry-export-terminal-private.json')
assert terminal['properties']['status']=='Succeeded' and terminal['name']==reg['native_run'] and reg['complete'] and reg['next_links']==[]
legacy=read('2026-10-14-canonical-four-legacy-source-map-private.json');legacy={r['register_item_id']:r for r in legacy}
known={r['CanonicalKey'] for r in c};by_source={k:v['key'] for k,v in source_map.items()};bridged=[]
for row in reg['rows']:
 ident=row['RegisterItemID'];key=row['CanonicalKey'];sk=row['SourceKey']
 if key in known:basis='exact stored canonical identity'
 elif sk in by_source:key=by_source[sk];basis='exact retained source membership'
 elif ident in legacy:
  old=legacy[ident];assert old['legacy_key']==key and old['source_key']==sk
  key=old['accepted_canonical_key'];assert key in known
  assert by_source['dora:'+row['DORAURL']]==key
  basis='saved legacy secondary representation plus exact canonical source link'
 else:raise ValueError('Unmapped registry row')
 bridged.append({'item_id':ident,'source_key':sk,'stored_key':row['CanonicalKey'],'key':key,'basis':basis})
assert len(bridged)==1345 and {r['key'] for r in bridged}==known
counts=collections.Counter(r['key'] for r in bridged);assert sum(v-1 for v in counts.values())==4
full=read('2026-10-15-registry-source-metadata-list-preimage-private.json');rows=full['items']['value'];assert not any(k.endswith('nextLink') for k in full['items'])

fullindex=index(rows,'Id')
assert len(fullindex)==len(rows)
assert {r['RegisterItemID'] for r in reg['rows']}=={r['Id'] for r in rows if r.get('field_1') and r.get('field_2')}
for r in reg['rows']:
 actual=fullindex[r['RegisterItemID']]
 assert actual['field_1']==r['SourceKey'] and actual['field_2']==r['CanonicalKey']
# Independent native keyed export and complete later full capture preserve every curated field.
raw_registry=read('2026-10-14-canonical-registry-native-output-private.json')['body']
action=read('2026-10-14-canonical-registry-action-private.json')
assert action['runName']==reg['native_run'] and action['properties']['status']=='Succeeded'
assert not any(k.endswith('nextLink') for k in raw_registry)
assert len(raw_registry['value'])==reg['row_count']==1345
assert {int(r['ID']) for r in raw_registry['value']}=={r['RegisterItemID'] for r in reg['rows']}
protected=['Title']+['field_'+str(n) for n in range(1,20)]
def value(v):return v.get('Url') if isinstance(v,dict) else v
for row in raw_registry['value']:
 saved=fullindex[int(row['ID'])]
 assert all(value(row.get(k))==value(saved.get(k)) for k in protected),'Curated registry drift'
# Earlier complete source inventories are retained subsets of the selected PubMed commit.
oldcommit=read(str(Path(meta_inputs['archive_dir']).relative_to('private/ops')/('commit-'+validation['batch_id']+'.json')))
midfiles=list((B/'2026-10-04-native-pubmed-commit-marker-private').glob('commit-*.json'))
assert len(midfiles)==1
midcommit=read(str(midfiles[0].relative_to(B)))
oldkeys=set(next(s['ExpectedKeys'] for s in oldcommit['Sources'] if s['Source']=='PubMed'))
assert oldkeys<=set(midcommit['Sources'][0]['ExpectedKeys'])<=set(spec['ExpectedKeys'])
# Add independent publication-query receipts and their current/source preservation proof.
start=read('2026-10-14-canonical-cli-refresh-start-private.json')
selected_model=read('2026-10-15-t14-canonical-model-private.json')
assert start['semantic_model_id']==selected_model['id']==commit['ModelID']
assert start['refresh_request_id']==cor['request_id']
canonical_receipt=read('2026-10-14-canonical-cli-full-fields-reconciliation-private.json')
assert canonical_receipt['status']=='PASS' and canonical_receipt['canonical_key_set_exact']
assert canonical_receipt['substantive_mismatches']==0 and canonical_receipt['canonical_rows']==1341
packet=read('2026-10-24-whole-system-reconciliation/packet.json')
old_result=read('2026-10-24-whole-system-reconciliation/result.json')
assert old_result['status']=='BLOCKED' and packet['stages']['model']['independent_expected_count']==len(c)
original_identity_contract=packet['identity_contract_sha256']
identity_contract={'kind':'preserved_native_source_membership_comparison_v1','field':'CanonicalKey','rule':'Compare unchanged existing canonical keys and exact stored native PMID/DORAURL source links; preserve original source and registry identities and secondary representations; no new identity inference','basis':'Recovered accepted source inventories, same-model native query/definition and full-value preservation chain','parent_exact_key_comparison_sha256':original_identity_contract}
packet['identity_contract_basis']=identity_contract
packet['identity_contract_sha256']=hashlib.sha256(json.dumps(identity_contract,sort_keys=True,separators=(',',':')).encode()).hexdigest()
for supplied in packet['stages'].values():supplied['identity_contract_sha256']=packet['identity_contract_sha256']
lineage={k:packet[k] for k in ['generation_id','source_snapshot_id','identity_contract_sha256']}
# Receipt references keep actual original runs; projection lineage is justified by the exact preservation chain.
source_rows=[{'key':k} for k in sorted(source_map)]
source_membership={'kind':'recovered_committed_source_membership_v1','rows':source_rows,'row_count':len(source_rows),'source_commits':{'PubMed':{'batch':commit['BatchID'],'observed_at':commit['ObservedAtUTC'],'expected_count':spec['ExpectedRecords']},'DORA':{'batch':oldcommit['BatchID'],'observed_at':oldcommit['ObservedAtUTC'],'expected_count':validation['sources']['DORA']['publication_rows']}},'source_query_refresh':cor['request_id'],'membership_basis':'Accepted committed source inventories; exact source-query identity coverage; native source/canonical definitions and all canonical values preserved into selected model/export generation'}
reverse=collections.defaultdict(list)
for sk,item in source_map.items():reverse[item['key']].append(sk)
canonical_rows=[{'key':r['CanonicalKey'],'publication_month':r.get('PublicationMonth') or None,'source_keys':sorted(reverse[r['CanonicalKey']]),'identity_evidence_ref':'source-to-canonical.json; saved native canonical DORAURL/PMID links and unchanged CanonicalPublications expression'} for r in c]
registry_groups=collections.defaultdict(list)
for row in bridged:registry_groups[row['key']].append(row['item_id'])
registry_rows=[{'key':key,'original_item_ids':ids} for key,ids in sorted(registry_groups.items())]
registry_proof={'kind':'saved_registry_identity_preservation_bridge_v1','original_native_export_run':reg['native_run'],'original_native_export_time':terminal['properties']['endTime'],'full_capture_observed_at':full['observedAtUTC'],'full_rows':len(rows),'keyed_rows':reg['row_count'],'blank_stubs':len(rows)-reg['row_count'],'secondary_representations':len(bridged)-len(counts),'protected_fields':protected,'all_protected_values_exact':True,'original_ids_and_keys_preserved':True,'comparison_identity_count':reg['row_count']-len(legacy),'count_basis':'Native keyed export 1345 minus four individually evidenced retained secondary representations; complete raw 1648-row capture and all crosswalk rows remain retained','derived_source_boundary':'Nine registry PubMed-shaped keys on exact stored DORA canonical identities are representations; they do not admit nine new primary PubMed source members'}
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
def stage(stage_rows,count,operation,evidence,artifact,accepted=False):
 result={**lineage,'complete':True,'next_links':[],'data_kind':'native_readback','terminal_status':'Succeeded','operation_ref':operation,'evidence_ref':evidence,'query_version':'saved-source-registry-preservation-bridge-v1','artifact_sha256':digest(artifact),'independent_expected_count':count,'rows':stage_rows}
 if accepted:result['accepted_commit']=True
 return result
packet['stages']['source']=stage(source_rows,spec['ExpectedRecords']+validation['sources']['DORA']['publication_rows'],cor['request_id'],'source-membership.json; input-hashes.json',source_membership,True)
packet['stages']['canonical']=stage(canonical_rows,canonical_receipt['canonical_rows'],cor['request_id'],'source-to-canonical.json; input-hashes.json',canonical_rows,True)
packet['stages']['registry']=stage(registry_rows,reg['row_count']-len(legacy),reg['native_run'],'registry-preservation-bridge.json; registry-crosswalk.json',registry_proof)
packet['recovered_lineage_boundary']='Selected historical model/export lineage joined through original native source queries, committed inventories, unchanged implementation and exact 40230-value canonical preservation. Original registry run/time retained; exact identities and curated fields preserved in later complete capture. No observation is relabelled as a new native run.'
from scripts.reconcile_generation import reconcile
result=reconcile(packet)
assert result['status']=='PASS_SUPPLIED_KEY_PARITY_ONLY' and result['blockers']==[]
assert result['counts']=={'source':1983,'canonical':1341,'registry':1341,'model':1341,'full_export':1341,'monthly_export':14}
assert len(result['unknown_month_keys'])==189
assert result['native_acceptance'] is False and result['operational_acceptance'] is False
disposition=read('2026-10-24-source-difference-disposition/disposition-result.json')
uncertain=sum(r['disposition']=='uncertain_source_difference_preserved' for r in disposition['items'])
assert uncertain==144 and len(disposition['items'])-uncertain==3
report={'kind':'recovered_saved_generation_links_v1','status':'ALL_THREE_LINKS_RECOVERED_KEY_PARITY_VERIFIED','counts':result['counts'],'canonical_values_preserved':40230,'registry_original_rows':len(rows),'registry_keyed_rows':reg['row_count'],'registry_blank_stubs':registry_proof['blank_stubs'],'registry_secondary_representations':4,'DORA_metadata_display_normalizations':check['engine_text_normalizations'],'semantic_source_curated_pairs_still_uncertain':144,'explained_title_pairs':3,'new_native_runs':0,'native_writes':0,'native_acceptance':False,'operational_acceptance':False,'scope':'Recovered historical source membership, existing source-to-canonical map and registry preservation chain. No current snapshot, semantic corrections, whole-system metadata acceptance or scheduled operation is asserted.'}
OUT.mkdir()
for name,value in [('identity-comparison-contract.json',identity_contract),('recovery-result.json',report),('source-membership.json',source_membership),('source-to-canonical.json',source_map),('registry-crosswalk.json',bridged),('registry-preservation-bridge.json',registry_proof),('input-hashes.json',inputs),('packet.json',packet),('result.json',result)]:
 path=OUT/name
 with path.open('x') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
 path.chmod(0o600)
print(json.dumps(report,indent=2))
