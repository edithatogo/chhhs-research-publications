import copy
import json
from pathlib import Path
import unittest

from scripts.prepare_datacite_discovery_collection import build, freeze_hedge, quote_query, with_weekly_updates, with_runtime_page_retention, with_failure_receipt, prepare_query_continuation, prepare_recovery_provenance, prepare_automatic_failure_prefix_reader
import hashlib


class DataCiteDiscoveryTests(unittest.TestCase):
    def recovery_fixture(self):
        definition = {'triggers': {'manual': {'type': 'Request', 'kind': 'Button'}},
            'actions': {'Scope': {'inputs': {'policy': {'source': 'datacite'},
                    'scope_sha256': 'a' * 64, 'institutional_queries': [
                        {'key': 'institutional-0', 'kind': 'institutional', 'query': 'first'},
                        {'key': 'institutional-1', 'kind': 'institutional', 'query': 'second'}]}},
                'Manifest': {'inputs': {'format': 'rims-datacite-discovery-v1'}},
                'Cutoff': {'inputs': '@formatDateTime(utcNow())'},
                'Full_reconciliation': {'inputs': 'dynamic', 'runAfter': {'Has_checkpoint': ['Succeeded']}},
                'Has_checkpoint': {'type': 'If'},
                'Initialize': {'inputs': {'variables': [
                    {'name': 'Queries', 'type': 'array', 'value': []},
                    {'name': 'Completions', 'type': 'array', 'value': []}]}},
                'For_each_query': {'runtimeConfiguration': {'concurrency': {'repetitions': 1}},
                    'actions': {'Query_may_run': {'expression': "@not(variables('Failed'))"}}}}}
        document = {'properties': {'state': 'Stopped', 'isManaged': False,
            'definition': definition}}
        page = {'file': 'institutional-0-page-0.json', 'rows': 0,
            'saved_content_equal': True, 'sha256': hashlib.sha256(b'empty').hexdigest()}
        query = {'key': 'institutional-0', 'kind': 'institutional', 'complete': True,
            'scope_sha256': 'a' * 64, 'provider_total': 0, 'received': 0,
            'unique_dois': 0, 'pages': [page]}
        receipt = {'status': 'VERIFIED_FAILED_DATACITE_RECOVERY_INPUTS',
            'source_terminal_status': 'Failed', 'scope_sha256': 'a' * 64,
            'source_run': 'failed-run-1', 'archive_parent': '/Documents/DataCite',
            'archive_folder': '/Documents/DataCite/datacite-discovery-failed-run-1',
            'until': '2026-10-20T00:00:00Z', 'full_reconciliation': True,
            'checkpoint_absent': True, 'queries': [query], 'saved_page_readback_count': 1}
        fingerprint = hashlib.sha256(json.dumps(definition, sort_keys=True,
            separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()
        return document, receipt, fingerprint

    def test_datacite_query_continuation_pins_window_and_reuses_only_complete_prefix(self):
        document, receipt, fingerprint = self.recovery_fixture()
        result = prepare_query_continuation(document, receipt,
            expected_definition_sha256=fingerprint)
        actions = result['properties']['definition']['actions']
        variables = {v['name']: v['value'] for v in actions['Initialize']['inputs']['variables']}
        self.assertEqual([q['key'] for q in variables['Queries']],
            ['institutional-0', 'institutional-1'])
        self.assertEqual([q['key'] for q in variables['Completions']], ['institutional-0'])
        self.assertEqual(actions['Cutoff']['inputs'], receipt['until'])
        self.assertIs(actions['Full_reconciliation']['inputs'], True)
        self.assertIn("contains(json('[\"institutional-0\"]')",
            actions['For_each_query']['actions']['Query_may_run']['expression'])
        self.assertIn('DATACITE_RECOVERY_CHECKPOINT_APPEARED',
            actions['Guard_recovery_checkpoint']['inputs'])
        self.assertEqual(document['properties']['definition']['actions']['Manifest']['inputs'],
            {'format': 'rims-datacite-discovery-v1'})

    def test_datacite_query_continuation_refuses_drift_and_unread_prefix(self):
        document, receipt, fingerprint = self.recovery_fixture()
        drifted = copy.deepcopy(document)
        drifted['properties']['definition']['actions']['Cutoff']['inputs'] = 'changed'
        with self.assertRaisesRegex(ValueError, 'Definition drift'):
            prepare_query_continuation(drifted, receipt,
                expected_definition_sha256=fingerprint)
        incomplete = copy.deepcopy(receipt)
        incomplete['queries'][0]['pages'][0].pop('sha256')
        with self.assertRaisesRegex(ValueError, 'Exact contiguous DataCite page readbacks'):
            prepare_query_continuation(document, incomplete,
                expected_definition_sha256=fingerprint)

    def test_complete_terminal_page_may_contain_exact_page_size(self):
        document, receipt, fingerprint = self.recovery_fixture()
        query = receipt['queries'][0]
        query.update(provider_total=250, received=250, unique_dois=250)
        query['pages'][0]['rows'] = 250
        result = prepare_query_continuation(document, receipt,
            expected_definition_sha256=fingerprint)
        queries = next(v['value'] for v in result['properties']['definition']['actions']['Initialize']['inputs']['variables']
                       if v['name'] == 'Queries')
        self.assertEqual(queries[0]['pages'][0]['rows'], 250)

    def test_recovery_provenance_upgrade_binds_page_and_checkpoint_etags(self):
        flow_id = '/providers/Microsoft.Flow/environments/Default-0b65b008-95d7-4abc-bafc-3ffc20c039c0/flows/47f4378d-a752-49be-ab6b-a8b4491a574a'
        uri = "_api/web/GetFolderByServerRelativeUrl('/Documents/DataCite')/Files?$filter=startswith(Name,'datacite-discovery-complete-')&$orderby=TimeCreated desc&$top=1&$select=Name"
        document = {'id': flow_id, 'properties': {'state': 'Stopped', 'isManaged': False,
            'displayName': 'DataCite weekly collector', 'definition': {
                'triggers': {'Recurrence': {'type': 'Recurrence'}}, 'actions': {
                    'Find_checkpoint': {'inputs': {'parameters': {'parameters/uri': uri}}},
                    'For_each_query': {'actions': {'Query_may_run': {'actions': {
                        'Until_complete': {'actions': {
                            'Read_page': {'runAfter': {'Save_page': ['Succeeded']}, 'inputs': {
                                'host': {'operationId': 'GetFileContentByPath'},
                                'parameters': {'dataset': 'https://example.sharepoint.com',
                                    'path': "@concat(outputs('Run_folder'),'/',outputs('Page_name'))",
                                    'inferContentType': False}}},
                            'Verify_page': {'type': 'Compose'},
                            'Page_ids': {'runAfter': {'Guard_page': ['Succeeded']}},
                            'Page_receipt': {'inputs': {'name': 'Pages', 'value': {
                                'file': 'page.json', 'rows': 0, 'saved_content_equal': True,
                                'archive_folder': '/Documents/DataCite/run'}}}}}}}}},
                    'Observe_failed_generation': {'actions': {'Failure_receipt': {'inputs': {
                        'format': 'rims-datacite-failure-v1'}}}}}}}}
        # The upgrade is intentionally pinned to the known native component and
        # its current action-count contract.
        for n in range(50 - len(document['properties']['definition']['actions'])):
            document['properties']['definition']['actions'][f'Unrelated_{n}'] = {}
        original = copy.deepcopy(document)
        fingerprint = hashlib.sha256(json.dumps(document['properties']['definition'],
            sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()
        result = prepare_recovery_provenance(document,
            expected_definition_sha256=fingerprint)
        self.assertEqual(document, original)
        actions = result['properties']['definition']['actions']
        self.assertTrue(actions['Find_checkpoint']['inputs']['parameters']['parameters/uri'].endswith('&$select=Name,ETag,TimeCreated'))
        page = actions['For_each_query']['actions']['Query_may_run']['actions']['Until_complete']['actions']
        self.assertEqual(page['Read_page_metadata']['inputs']['host']['operationId'], 'GetFileMetadataByPath')
        self.assertEqual(page['Read_page_metadata']['runAfter'], {'Guard_page': ['Succeeded']})
        self.assertEqual(page['Page_ids']['runAfter'], {'Guard_page_metadata': ['Succeeded']})
        self.assertIn('Read_page_metadata', page['Page_receipt']['inputs']['value']['etag'])
        receipt = actions['Observe_failed_generation']['actions']['Failure_receipt']['inputs']
        self.assertEqual(receipt['format'], 'rims-datacite-failure-v2')
        self.assertIn("['ETag']", receipt['previous_checkpoint']['etag'])
        self.assertIn("['Name']", receipt['previous_checkpoint']['file'])
        self.assertEqual(receipt['planned_queries'], "@variables('Queries')")
        with self.assertRaisesRegex(ValueError, 'Definition drift'):
            prepare_recovery_provenance(document, expected_definition_sha256='0' * 64)

    def test_recovery_provenance_accepts_live_page_receipt_without_archive_folder(self):
        flow_id = '/providers/Microsoft.Flow/environments/Default-0b65b008-95d7-4abc-bafc-3ffc20c039c0/flows/47f4378d-a752-49be-ab6b-a8b4491a574a'
        uri = "_api/web/GetFolderByServerRelativeUrl('/Documents/DataCite')/Files?$filter=startswith(Name,'datacite-discovery-complete-')&$orderby=TimeCreated desc&$top=1&$select=Name"
        document = {'id': flow_id, 'properties': {'state': 'Stopped', 'isManaged': False,
            'displayName': 'DataCite weekly collector', 'definition': {
                'triggers': {'Recurrence': {'type': 'Recurrence'}}, 'actions': {
                    'Find_checkpoint': {'inputs': {'parameters': {'parameters/uri': uri}}},
                    'For_each_query': {'actions': {'Query_may_run': {'actions': {
                        'Until_complete': {'actions': {
                            'Read_page': {'runAfter': {'Save_page': ['Succeeded']}, 'inputs': {
                                'host': {'operationId': 'GetFileContentByPath'},
                                'parameters': {'dataset': 'https://example.sharepoint.com',
                                    'path': "@concat(outputs('Run_folder'),'/',outputs('Page_name'))",
                                    'inferContentType': False}}},
                            'Verify_page': {'type': 'Compose'},
                            'Page_ids': {'runAfter': {'Guard_page': ['Succeeded']}},
                            'Page_receipt': {'inputs': {'name': 'Pages', 'value': {
                                'file': 'page.json', 'rows': 0, 'saved_content_equal': True}}}}}}}}},
                    'Observe_failed_generation': {'actions': {'Failure_receipt': {'inputs': {
                        'format': 'rims-datacite-failure-v1'}}}}}}}}
        for n in range(50 - len(document['properties']['definition']['actions'])):
            document['properties']['definition']['actions'][f'Unrelated_{n}'] = {}
        fingerprint = hashlib.sha256(json.dumps(document['properties']['definition'],
            sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()
        result = prepare_recovery_provenance(document,
            expected_definition_sha256=fingerprint)
        actions = result['properties']['definition']['actions']
        values = actions['For_each_query']['actions']['Query_may_run']['actions']['Until_complete']['actions']['Page_receipt']['inputs']['value']
        self.assertEqual(values['archive_folder'], "@outputs('Run_folder')")
        self.assertIn('etag', values)

    def test_automatic_failure_prefix_reader_is_checkpoint_and_page_etag_gated(self):
        flow_id = '/providers/Microsoft.Flow/environments/Default-0b65b008-95d7-4abc-bafc-3ffc20c039c0/flows/47f4378d-a752-49be-ab6b-a8b4491a574a'
        site = 'https://example.sharepoint.com/sites/rims'
        uri = "_api/web/GetFolderByServerRelativeUrl('/sites/rims/Shared Documents/Source')/Files?$filter=startswith(Name,'datacite-discovery-complete-')&$orderby=TimeCreated desc&$top=1&$select=Name,ETag,TimeCreated"
        sp = lambda op, params: {'type': 'OpenApiConnection', 'inputs': {
            'host': {'apiId': '/providers/Microsoft.PowerApps/apis/shared_sharepointonline',
                'connectionName': 'shared_sharepointonline', 'operationId': op},
            'parameters': {'dataset': site, **params}}}
        page = {'Read_page_metadata': sp('GetFileMetadataByPath', {'path': 'page.json'}),
            'Guard_page_metadata': {'type': 'Compose'},
            'Page_receipt': {'inputs': {'name': 'Pages', 'value': {
                'file': 'page.json', 'rows': 0, 'saved_content_equal': True,
                'archive_folder': '/Shared Documents/Source/run', 'etag': '@etag'}}}}
        receipt = {'format': 'rims-datacite-failure-v2', 'recovery_protocol': 1,
            'planned_queries': '@variables(\'Queries\')'}
        actions = {
            'Cutoff': {'type': 'Compose', 'inputs': '@utcNow()'},
            'Find_checkpoint': {**sp('HttpRequest', {'parameters/uri': uri}),
                'runAfter': {'Cutoff': ['Succeeded']}},
            'Initialize': {'type': 'InitializeVariable', 'runAfter': {'Find_checkpoint': ['Succeeded']},
                'inputs': {'variables': [{'name': 'Checkpoint', 'type': 'object', 'value': {}},
                    {'name': 'Queries', 'type': 'array', 'value': []},
                    {'name': 'Completions', 'type': 'array', 'value': []}]}},
            'Has_checkpoint': {'type': 'If', 'actions': {'Read_checkpoint': sp('GetFileContentByPath', {
                'path': "@concat('/Shared Documents/Source/',first(body('Find_checkpoint')?['value'])?['Name'])"})}},
            'Full_reconciliation': {'type': 'Compose', 'inputs': True},
            'Run_folder': {'type': 'Compose', 'runAfter': {'For_each_doi_batch': ['Succeeded']},
                'inputs': "@concat('/Shared Documents/Source/datacite-discovery-',workflow()?['run']?['name'])"},
            'For_each_doi_batch': {'type': 'Foreach', 'runAfter': {'Quoted_dois': ['Succeeded']},
                'actions': {}},
            'Quoted_dois': {'type': 'Compose', 'inputs': []},
            'For_each_query': {'type': 'Foreach', 'runAfter': {'Verify_doi_source': ['Succeeded']},
                'actions': {'Query_may_run': {'type': 'If', 'expression': "@not(variables('Failed'))",
                    'actions': {'Query_with_window': {'type': 'Compose', 'inputs':
                        "@concat('(',items('For_each_query')?['query'],') AND ',if(and(not(outputs('Full_reconciliation')),equals(items('For_each_query')?['kind'],'institutional')),concat('updated:[\"',formatDateTime(addDays(variables('Checkpoint')?['until'],-7),'yyyy-MM-ddTHH:mm:ssZ'),'\" TO \"',outputs('Cutoff'),'\"]'),concat('created:[* TO \"',outputs('Cutoff'),'\"]')))",
                        'runAfter': {'Reset_Done': ['Succeeded']}},
                        'Query_summary': {'type': 'Compose', 'inputs': {'complete': True,
                            'key': "@items('For_each_query')?['key']", 'pages': "@variables('Pages')"}}}}}},
            'Verify_doi_source': {'type': 'Compose', 'inputs': True},
            'Manifest': {'type': 'Compose', 'inputs': {'until': '@outputs(\'Cutoff\')',
                'full_reconciliation': '@outputs(\'Full_reconciliation\')',
                'baseline_completed_at': '@outputs(\'Cutoff\')'}},
            'Observe_failed_generation': {'type': 'Scope', 'actions': {'Failure_receipt': {
                'type': 'Compose', 'inputs': receipt}}}
        }
        actions['For_each_query']['actions']['Query_may_run']['actions']['Until_complete'] = {
            'type': 'Until', 'actions': page}
        for n in range(50 - len(actions)):
            actions[f'Unrelated_{n}'] = {}
        document = {'id': flow_id, 'properties': {'state': 'Stopped', 'isManaged': False,
            'displayName': 'DataCite', 'connectionReferences': {'shared_sharepointonline': {}},
            'definition': {'triggers': {'Recurrence': {'type': 'Recurrence'}}, 'actions': actions}}}
        fingerprint = hashlib.sha256(json.dumps(document['properties']['definition'],
            sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()
        original = copy.deepcopy(document)
        result = prepare_automatic_failure_prefix_reader(document,
            expected_definition_sha256=fingerprint)
        self.assertEqual(document, original)
        prepared = result['properties']['definition']['actions']
        self.assertEqual(len(prepared), 63)
        self.assertIn("startswith(Name,'datacite-failed-')",
            prepared['Find_failure_receipt']['inputs']['parameters']['parameters/uri'])
        self.assertIn('TimeCreated',
            prepared['Find_failure_receipt']['inputs']['parameters']['parameters/uri'])
        self.assertIn('DATACITE_RECOVERY_CHECKPOINT_DRIFT',
            prepared['Guard_recovery_checkpoint_identity']['inputs'])
        self.assertTrue(prepared['Consider_recovery']['actions']['Set_recovery_candidate']['inputs']['value'].startswith('@and('))
        self.assertIn('DATACITE_RECOVERY_PAGE_ETAG_DRIFT',
            str(prepared['Qualify_recovery_prefix']))
        self.assertIn('lessOrEquals(outputs(\'Current_recovery_page\')?[',
            str(prepared['Qualify_recovery_prefix']))
        self.assertIn('CompletedKeys',
            prepared['For_each_query']['actions']['Query_may_run']['expression'])
        self.assertEqual(prepared['Run_folder']['runAfter'],
            {'Set_completed_query_keys': ['Succeeded']})
        self.assertEqual(prepared['For_each_query']['actions']['Query_may_run']['actions']['Query_summary']['inputs']['scope_sha256'],
            "@outputs('Scope')?['scope_sha256']")
        drifted = copy.deepcopy(document)
        drifted['properties']['definition']['actions']['Cutoff']['inputs'] = 'changed'
        with self.assertRaisesRegex(ValueError, 'Definition drift'):
            prepare_automatic_failure_prefix_reader(drifted,
                expected_definition_sha256=fingerprint)

    def test_every_institutional_alias_is_retained_and_unknown_hedge_syntax_fails(self):
        collector = {'facility_query_version': 'fixture', 'pubmed': {'query':
            '("Cairns Hospital"[Affiliation] OR "Tully Hospital" [Affiliation]) AND Australia[Affiliation]'}}
        frozen = freeze_hedge(collector, {'source': 'datacite'})
        self.assertEqual(frozen['institutional_queries'][0]['aliases'], ['Cairns Hospital', 'Tully Hospital'])
        self.assertIn('contributors.affiliation.name:', frozen['institutional_queries'][0]['query'])
        collector['pubmed']['query'] += ' OR Unmapped[Affiliation]'
        with self.assertRaises(ValueError): freeze_hedge(collector, {'source': 'datacite'})

    def test_query_values_cannot_escape_their_phrase(self):
        self.assertEqual(quote_query('A" OR *:* \\B'), '"A\\" OR *:* \\\\B"')

    def test_preparation_preserves_native_identity_and_active_preimages_are_refused(self):
        doc = {'properties': {'state': 'Stopped', 'displayName': 'RIMS DataCite collection',
            'connectionReferences': {'existing': {'connectionName': 'preserved'}},
            'definition': {'parameters': {'existing': True},
                'triggers': {'manual': {'type': 'Request', 'kind': 'Button'}},
                'actions': {'Run_folder': {'inputs': "@concat('/Documents/archive/datacite-source-',workflow()?['run']?['name'])"},
                    'Requested_ids': {'inputs': [{'doi': '10.5555/example'}]},
                    'Create_exclusive_folder': {'inputs': {'host': {'connectionName': 'existing'},
                        'parameters': {'dataset': 'https://example.sharepoint.com/sites/research'}}}}}}}
        frozen = freeze_hedge(json.loads(Path('config/collector.json').read_text()), {'source': 'datacite', 'scope': {'cadence': 'weekly'}})
        target = {'site': 'https://example.sharepoint.com/sites/research',
            'list': '11111111-2222-3333-4444-555555555555', 'field': 'DOI', 'population_kind': 'fixture'}
        before = copy.deepcopy(doc); result = build(doc, frozen, target)
        self.assertEqual(doc, before)
        for key in ['state', 'displayName', 'connectionReferences']:
            self.assertEqual(result['properties'][key], before['properties'][key])
        for key in ['parameters', 'triggers']:
            self.assertEqual(result['properties']['definition'][key], before['properties']['definition'][key])
        page = result['properties']['definition']['actions']['For_each_query']['actions']['Query_may_run']['actions']['Until_complete']['actions']
        self.assertEqual(page['Raw_page']['runAfter'], {'Get_page': ['Succeeded', 'Failed', 'TimedOut']})
        self.assertEqual(page['Guard_page']['runAfter'], {'Verify_page': ['Succeeded']})
        self.assertEqual(page['Read_page_metadata']['inputs']['host']['operationId'], 'GetFileMetadataByPath')
        self.assertEqual(page['Read_page_metadata']['runAfter'], {'Guard_page': ['Succeeded']})
        self.assertEqual(page['Guard_page_metadata']['runAfter'], {'Read_page_metadata': ['Succeeded']})
        self.assertEqual(page['Page_ids']['runAfter'], {'Guard_page_metadata': ['Succeeded']})
        self.assertIn("outputs('Read_page_metadata')?['body']?['ETag']", page['Page_receipt']['inputs']['value']['etag'])
        self.assertEqual(page['Polite_delay']['inputs']['interval'], {'count': 5, 'unit': 'Second'})
        self.assertIn("outputs('Get_page')?['error']", page['Raw_page']['inputs']['transport_error'])
        # Capture is not admission: failed pages still cannot reach IDs, cursor
        # advancement, totals or completion without the unchanged strict guard.
        self.assertIn("equals(outputs('Get_page')?['statusCode'],200)", page['Guard_page']['inputs'])
        self.assertEqual(with_runtime_page_retention(result), result)
        drift = copy.deepcopy(result)
        drift['properties']['definition']['actions']['For_each_query']['actions']['Query_may_run']['actions']['Until_complete']['actions']['Polite_delay']['inputs']['interval']['count'] = 2
        with self.assertRaises(ValueError): with_runtime_page_retention(drift)
        scheduled = with_weekly_updates(result)
        actions = scheduled['properties']['definition']['actions']
        self.assertEqual(actions['Get_publication_dois']['runtimeConfiguration']['paginationPolicy']['minimumItemCount'], 5000)
        self.assertIn("less(length(body('Get_publication_dois')?['value']),5000)", actions['Guard_publication_paging']['inputs'])
        self.assertIn("body('Read_publication_count')?['ItemCount']", actions['Guard_publication_paging']['inputs'])
        self.assertEqual(actions['Raw_doi_fields'], result['properties']['definition']['actions']['Raw_doi_fields'])
        self.assertEqual(actions['For_each_query'], result['properties']['definition']['actions']['For_each_query'])
        # A failure handler must not turn an accepted generation into Failed:
        # Terminate belongs inside a scope eligible only on rejected completion.
        diagnostic = actions['Observe_failed_generation']
        self.assertNotIn('Succeeded', diagnostic['runAfter']['Verify_completion'])
        self.assertNotIn('Terminate_failed_generation', actions)
        failure = diagnostic['actions']
        self.assertEqual(failure['Terminate_failed_generation']['inputs']['runStatus'], 'Failed')
        self.assertEqual(set(failure['Terminate_failed_generation']['runAfter']['Verify_failure_receipt']),
                         {'Succeeded', 'Failed', 'TimedOut', 'Skipped'})
        receipt = failure['Failure_receipt']['inputs']
        self.assertEqual(receipt['format'], 'rims-datacite-failure-v2')
        self.assertEqual(receipt['recovery_protocol'], 1)
        self.assertIn("first(body('Find_checkpoint')?['value'])?['ETag']",
            receipt['previous_checkpoint']['etag'])
        self.assertFalse(receipt['accepted'])
        self.assertFalse(receipt['complete'])
        # A saved marker followed by failed verification is an uncertain effect,
        # so retain both outcomes instead of asserting the checkpoint unchanged.
        self.assertIn('Save_completion', receipt['completion_write'])
        self.assertIn('Verify_completion', receipt['completion_readback'])
        self.assertEqual(receipt['complete_query_prefix'], "@variables('Completions')")
        self.assertEqual(receipt['full_reconciliation'], "@outputs('Full_reconciliation')")
        self.assertNotIn('last_good_checkpoint_advanced', receipt)
        self.assertIn('Read_failure_receipt', failure['Verify_failure_receipt']['inputs'])
        before_repeat = copy.deepcopy(result)
        with self.assertRaises(ValueError): with_failure_receipt(result)
        self.assertEqual(result, before_repeat)
        doc['properties']['state'] = 'Started'
        with self.assertRaises(ValueError): build(doc, frozen, target)


if __name__ == '__main__':
    unittest.main()
