import copy
import json
import unittest

from scripts.prepare_nih_acquisition_flow import prepare as acquisition
from scripts.prepare_nih_unattended_flow import prepare, HUMAN
from tests import test_nih_office_worker as fixtures


class UnattendedChainTests(unittest.TestCase):
    def setUp(self):
        f=fixtures.OfficeWorkerTests();f.setUp();self.context=f.context;self.baseline=f.expected()
        self.doc={'properties':{'definition':acquisition('https://example.sharepoint.com/sites/test'),'connectionReferences':{'shared_sharepointonline':{'connectionName':'fictional-sharepoint','source':'Embedded'}}}}
        self.bindings=dict(site='https://example.sharepoint.com/sites/test',list='00000000-0000-0000-0000-000000000001',workspace='00000000-0000-0000-0000-000000000002',model='00000000-0000-0000-0000-000000000003',protected_model='00000000-0000-0000-0000-000000000004',item_id=14,folder='/Documents/CHHHS Research System - DEV/01 Source archive',drive='fictional',workbook='fictional',script='fictional',excel_connection='fictional-excel',powerbi_connection='fictional-powerbi')
        self.candidate=prepare(self.doc,self.bindings,self.context,self.baseline)
        self.actions=self.candidate['properties']['definition']['actions']['Processing']['actions']

    def test_acquisition_and_original_connection_remain_unchanged(self):
        for name in ['Acquisition','Observe_failure','Scope','Observed_utc','Run_folder']:
            self.assertEqual(self.doc['properties']['definition']['actions'][name],self.candidate['properties']['definition']['actions'][name])
        self.assertEqual(self.doc['properties']['connectionReferences']['shared_sharepointonline'],self.candidate['properties']['connectionReferences']['shared_sharepointonline'])
        self.assertNotIn('Processing',self.doc['properties']['definition']['actions'])

    def test_actual_archival_attachment_shape_is_adapted_explicitly(self):
        self.assertEqual(self.actions['Worker_attachments']['inputs']['select']['folder_id'], "@item()?['folder_metadata']?['id']")
        self.assertEqual(self.actions['Worker_input']['inputs']['attachments'], "@body('Worker_attachments')")

    def test_one_atomic_existing_parent_commit_excludes_all_human_fields(self):
        body=self.actions['Source_write']['inputs'];self.assertEqual(len(body),29)
        self.assertFalse(HUMAN.intersection(body))
        commit=self.actions['Commit_source']['inputs'];self.assertEqual(commit['retryPolicy'],{'type':'none'})
        self.assertEqual(commit['parameters']['parameters/headers']['IF-MATCH'],"@first(body('Read_parent')?['value'])?['@odata.etag']")
        self.assertIn("['RetrievedUTC']",body['RetrievedUTC']);self.assertIn("['DeadlineUTCInstant']",body['DeadlineUTCInstant'])
        self.assertNotIn('PostItem',json.dumps(self.actions))

    def test_source_baseline_and_version_drift_fail_before_commit(self):
        self.assertIn('NIH_PRESERVE_UNRECONCILED_SOURCE_EDIT',self.actions['Guard_last_source']['inputs'])
        self.assertIn('NIH_PARENT_REQUIRES_ADMISSION',self.actions['Guard_existing_parent']['inputs'])
        self.assertIn("['@odata.etag']",self.actions['Guard_existing_parent']['inputs'])
        self.assertEqual(self.actions['Source_write']['runAfter'],{'Before_commit':['Succeeded']})

    def test_verified_commit_receipt_precedes_refresh(self):
        self.assertEqual(self.actions['Before_refresh']['runAfter'],{'Verify_commit_receipt':['Succeeded']})
        self.assertEqual(self.actions['Refresh_grants_model']['runAfter'],{'Before_refresh':['Succeeded']})
        receipt=self.actions['Commit_receipt']['inputs'];self.assertFalse(receipt['review_fields_written'])
        self.assertNotIn('ReviewNotes',json.dumps(receipt))

    def test_only_grants_model_and_current_hash_can_pass_reader_gate(self):
        refresh=self.actions['Refresh_grants_model']['inputs']['parameters'];self.assertEqual(refresh['datasetid'],self.bindings['model'])
        poll=self.actions['Until_model_current'];self.assertEqual(poll['limit'],{'count':18,'timeout':'PT5M'})
        query=poll['actions']['Query_current_model']['inputs']['parameters']['specification/query'];self.assertIn('EvidenceHash',query);self.assertIn('Grants Deadline Occurrences',query)
        self.assertFalse(self.actions['Chain_receipt']['inputs']['notification_delivered'])
        self.assertFalse(self.actions['Chain_receipt']['inputs']['refresh_terminal_status_polled_in_flow'])

    def test_failure_preserves_commit_uncertainty_and_no_outbound_send(self):
        failure=self.candidate['properties']['definition']['actions']['Observe_processing_failure']
        self.assertEqual(failure['runAfter'],{'Processing':['Failed','TimedOut']})
        text=json.dumps(failure);self.assertIn('conditional commit/receipt',text);self.assertNotIn('SendEmail',text)
        self.assertFalse(failure['actions']['Chain_failure']['inputs']['notification_delivered'])

    def test_foreign_site_and_archive_bindings_are_rejected(self):
        for field,value in [('site','https://foreign.sharepoint.com/sites/test'),('folder','/Documents/foreign')]:
            with self.subTest(field=field), self.assertRaises(ValueError):
                prepare(self.doc,{**self.bindings,field:value},self.context,self.baseline)

    def test_faults_are_explicit_and_protected_model_refused(self):
        with self.assertRaises(ValueError):prepare(self.doc,self.bindings,self.context,self.baseline,fault='unbounded')
        b={**self.bindings,'model':self.bindings['protected_model']}
        with self.assertRaises(ValueError):prepare(self.doc,b,self.context,self.baseline)
        c=prepare(self.doc,self.bindings,self.context,self.baseline,fault='stale_etag')
        commit=c['properties']['definition']['actions']['Processing']['actions']['Commit_source']
        self.assertEqual(commit['inputs']['parameters']['parameters/headers']['IF-MATCH'],'"0"')
