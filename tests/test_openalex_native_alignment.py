import sys,json,base64,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from build_openalex_native_bootstrap import build as initial,_part
from build_openalex_alignment_model import build,FIELDS
class NativeAlignment(unittest.TestCase):
    def baseline(self):
        parts=[_part('definition/expressions.tmdl','expression Existing = 1\n'),_part('definition/model.tmdl','model Model\n')]+[_part('definition/tables/Old'+str(i)+'.tmdl','unchanged') for i in range(40)]
        stage=json.dumps({'kind':'openalex_retention_preparation_v1','ready_for_native_stage':True,'accepted_commit':False}).encode()
        baseline,_=initial({'definition':{'format':'TMDL','parts':parts}},stage)
        p=next(p for p in baseline['definition']['parts'] if p['path'].endswith('/OpenAlexWorks.tmdl'));s=base64.b64decode(p['payload']).decode().replace('source =\n\t\t\t\tfnProjectRetainedOpenAlex(OpenAlexBootstrapObservations)','source = fnProjectRetainedOpenAlex(OpenAlexBootstrapObservations)');p['payload']=base64.b64encode(s.encode()).decode()
        return baseline
    def qualified(self):return {'physical_schema_verified':True,'schema_sha256':'f'*64,'limits':{f:255 if f=='GrantIDs' else 63999 for f in FIELDS}}
    def test_only_four_owned_parts_change_without_new_tables_or_mapper_replacement(self):
        old=self.baseline();new,receipt=build(old,self.qualified());before={p['path']:p for p in old['definition']['parts']};after={p['path']:p for p in new['definition']['parts']}
        self.assertEqual(set(before),set(after));self.assertEqual(len(after),46)
        self.assertEqual({p for p in before if before[p]!=after[p]},set(receipt['changed_parts']))
        path='definition/expressions.tmdl';self.assertTrue(base64.b64decode(after[path]['payload']).startswith(base64.b64decode(before[path]['payload'])))
        self.assertEqual(receipt['new_tables'],0)
    def test_unqualified_schema_or_bad_limits_cannot_make_deployable_candidate(self):
        q=self.qualified();q['physical_schema_verified']=False
        with self.assertRaises(ValueError):build(self.baseline(),q)
        q=self.qualified();q['limits']['GrantIDs']=0
        with self.assertRaises(ValueError):build(self.baseline(),q)
    def test_drifted_existing_partition_is_not_overwritten(self):
        base=self.baseline();p=next(p for p in base['definition']['parts'] if p['path'].endswith('/OpenAlexWorks.tmdl'));p['payload']=base64.b64encode(b'table OpenAlexWorks\n\tpartition Something = m\n\t\tsource = Changed').decode()
        with self.assertRaises(ValueError):build(base,self.qualified())
