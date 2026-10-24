import copy
import unittest
from scripts.reconcile_generation import reconcile, STAGES


class GenerationReconciliationTests(unittest.TestCase):
    def setUp(self):
        self.packet = {'schema_version':1,'generation_id':'fictional-generation','source_snapshot_id':'fictional-source','identity_contract_sha256':'a'*64,'reporting_month':'2026-09','stages':{}}
        for name in STAGES:
            stage={k:self.packet[k] for k in ('generation_id','source_snapshot_id','identity_contract_sha256')}
            stage.update(model_refresh_correlation='synthetic-operation',extraction_contract_sha256='c'*64,artifact_sha256='b'*64,accepted_commit=True,complete=True,next_links=[],data_kind='native_readback',terminal_status='Succeeded',operation_ref='synthetic-operation',evidence_ref='synthetic-evidence',query_version='test-v1',independent_expected_count=1,rows=[{'key':'PMID:1','publication_month':'2026-09'}])
            if name=='source':stage['rows']=[{'key':'pubmed:1'}]
            if name=='canonical':stage['rows'][0].update(source_keys=['pubmed:1'],identity_evidence_ref='synthetic-mapping')
            if name=='monthly_export':stage['reporting_month']='2026-09'
            self.packet['stages'][name]=stage

    def test_equal_counts_different_keys_report_private_differences(self):
        self.packet['stages']['registry']['rows'][0]['key']='PMID:2'
        result=reconcile(self.packet)
        self.assertEqual(result['status'],'BLOCKED')
        self.assertEqual(result['differences']['canonical_to_registry'],{'missing':['PMID:1'],'unexpected':['PMID:2']})

    def test_supplied_parity_never_native_acceptance(self):
        result=reconcile(self.packet)
        self.assertEqual(result['status'],'PASS_SUPPLIED_KEY_PARITY_ONLY')
        self.assertFalse(result['native_acceptance'])

    def test_partial_mixed_incomplete_nonterminal_duplicate_and_count_fail_closed(self):
        cases=[('generation_id','other'),('complete',False),('next_links',['next']),('terminal_status','Running'),('data_kind','synthetic'),('independent_expected_count',True),('rows',[{'key':'x'},{'key':'x'}])]
        for key,value in cases:
            packet=copy.deepcopy(self.packet);packet['stages']['registry'][key]=value
            with self.subTest(key=key):self.assertEqual(reconcile(packet)['status'],'BLOCKED')
        del self.packet['stages']['model']
        self.assertIn('model: missing capture',reconcile(self.packet)['blockers'])

    def test_ambiguous_source_identity_cannot_be_silently_merged(self):
        row=self.packet['stages']['canonical']['rows'][0]
        row['source_keys'].append('pubmed:1')
        with self.assertRaises(ValueError):reconcile(self.packet)

    def test_wrong_period_and_date_metadata_mismatch_block(self):
        self.packet['stages']['monthly_export']['reporting_month']='2026-08'
        self.packet['stages']['full_export']['rows'][0]['publication_month']=None
        result=reconcile(self.packet)
        self.assertEqual(result['status'],'BLOCKED')
        self.assertIn('full_export: date metadata differs',result['blockers'])

    def test_empty_month_is_valid_and_unknown_dates_stay_outside_it(self):
        for name in ('canonical','model','full_export'):
            self.packet['stages'][name]['rows'][0]['publication_month']=None
        stage=self.packet['stages']['monthly_export']
        stage['rows']=[];stage['independent_expected_count']=0
        result=reconcile(self.packet)
        self.assertEqual(result['status'],'PASS_SUPPLIED_KEY_PARITY_ONLY')
        self.assertEqual(result['unknown_month_keys'],['PMID:1'])

    def test_staged_uncommitted_source_cannot_pass(self):
        self.packet['stages']['source']['accepted_commit']=False
        self.assertEqual(reconcile(self.packet)['status'],'BLOCKED')

    def test_exports_cannot_reference_a_different_model_refresh(self):
        self.packet['stages']['full_export']['model_refresh_correlation']='unrelated-refresh'
        self.assertIn('full_export: wrong model refresh correlation',reconcile(self.packet)['blockers'])
