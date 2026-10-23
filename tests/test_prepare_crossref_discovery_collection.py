import copy
import json
from pathlib import Path
import unittest

from scripts.prepare_crossref_discovery_collection import freeze_hedge, build, resume_completed_hedge, with_bounded_total_drift_restart, with_created_date_partitions, with_daily_updates


class CrossrefDiscoveryTests(unittest.TestCase):
    def test_hedge_edit_cannot_silently_drop_a_pubmed_affiliation(self):
        hedge = json.loads(Path('config/crossref-acquisition-hedge.json').read_text())
        collector = json.loads(Path('config/collector.json').read_text())
        original = copy.deepcopy(hedge)
        frozen = freeze_hedge(hedge, collector, {'source': 'crossref'})
        hedge['queries'].pop()
        with self.assertRaises(ValueError):
            freeze_hedge(hedge, collector, {'source': 'crossref'})
        altered = copy.deepcopy(original); altered['revision'] += '-edited'
        self.assertNotEqual(frozen['scope_sha256'],
                            freeze_hedge(altered, collector, {'source': 'crossref'})['scope_sha256'])

    def test_completion_cannot_advance_before_full_pages_and_saved_readback(self):
        original = {'properties': {'state': 'Stopped', 'displayName': 'RIMS Crossref',
            'connectionReferences': {'existing': {'connectionName': 'preserved'}},
            'definition': {'triggers': {'manual': {'type': 'Request', 'kind': 'Button'}},
                'actions': {'Run_folder': {'inputs': "@concat('/Documents/archive/crossref-source-',workflow()?['run']?['name'])"},
                    'Requested_ids': {'inputs': [{'id': '10.5555/example'}]},
                    'Create_exclusive_folder': {'inputs': {'host': {'connectionName': 'existing'},
                        'parameters': {'dataset': 'https://example.sharepoint.com/sites/research'}}}}}}}
        frozen = {'policy': {'source': 'crossref'}, 'scope_sha256': 'fixture',
            'hedge': {'snapshot_lag_minutes': 10, 'full_reconciliation_days': 28, 'overlap_days': 7}}
        before = copy.deepcopy(original)
        result = build(original, frozen)
        self.assertEqual(original, before)
        self.assertEqual(result['properties']['connectionReferences'], original['properties']['connectionReferences'])
        a = result['properties']['definition']['actions']
        self.assertIn("concat('until-created-date:'", a['Window_filter']['inputs'])
        self.assertIn("concat('from-index-date:'", a['Window_filter']['inputs'])
        self.assertEqual(a['Save_completion']['runAfter'], {'Verify_manifest': ['Succeeded']})
        q = a['For_each_query']['actions']['Query_may_run']['actions']
        self.assertEqual(q['Query_summary']['runAfter'], {'Guard_query_complete': ['Succeeded']})
        self.assertIn("length(variables('QueryDOIs')),variables('Expected')", q['Guard_query_complete']['inputs'])
        page = q['Until_query_complete']['actions']
        self.assertEqual(page['Page_DOIs']['runAfter'], {'Verify_page': ['Succeeded']})
        self.assertEqual(page['Get_page']['inputs']['uri'], "@outputs('Request_uri')")
        self.assertNotIn('select=', page['Request_uri']['inputs'])
        self.assertEqual(page['Mark_page_failed']['runAfter'], {'Polite_delay': ['Failed', 'TimedOut', 'Skipped']})
        # Native Consumption runtime rejects delays shorter than five seconds.
        self.assertEqual(page['Polite_delay']['inputs']['interval'], {'count': 5, 'unit': 'Second'})
        self.assertEqual(a['For_each_doi']['actions']['Doi_may_run']['actions']['Polite_doi_delay']['inputs']['interval'], {'count': 5, 'unit': 'Second'})
        self.assertTrue(page['Stop_failed_paging']['inputs']['value'])
        self.assertEqual(a['For_each_query']['actions']['Query_may_run']['expression'], "@not(variables('AcquisitionFailed'))")
        doi = a['For_each_doi']['actions']['Doi_may_run']['actions']
        self.assertEqual(doi['Guard_doi_status']['runAfter'], {'Verify_initial_doi': ['Succeeded']})
        redirect = doi['Resolve_redirect']['actions']
        self.assertIn("https://api.crossref.org/works/", redirect['Guard_redirect_target']['inputs'])
        self.assertEqual(redirect['Get_redirect']['runAfter'], {'Guard_redirect_target': ['Succeeded']})
        self.assertEqual(redirect['Guard_redirect_status']['runAfter'], {'Verify_redirect_doi': ['Succeeded']})
        self.assertNotIn('301', redirect['Guard_redirect_status']['inputs'])
        self.assertIn("outputs('Canonical_requested_doi')", doi['Guard_doi_identity']['inputs'])
        self.assertEqual(doi['Raw_doi']['inputs']['requested_doi'], "@items('For_each_doi')")
        self.assertIn('canonical_requested_doi', doi['Raw_doi']['inputs'])

    def test_total_drift_restart_is_finite_and_preserves_unrelated_native_inputs(self):
        original = {'properties': {'state': 'Stopped', 'displayName': 'RIMS Crossref',
            'connectionReferences': {'existing': {'connectionName': 'preserved'}},
            'definition': {'triggers': {'manual': {'type': 'Request', 'kind': 'Button'}},
                'actions': {'Run_folder': {'inputs': "@concat('/Documents/archive/crossref-source-',workflow()?['run']?['name'])"},
                    'Requested_ids': {'inputs': [{'id': '10.5555/example'}]},
                    'Create_exclusive_folder': {'inputs': {'host': {'connectionName': 'existing'},
                        'parameters': {'dataset': 'https://example.sharepoint.com/sites/research'}}}}}}}
        frozen = {'policy': {'source': 'crossref'}, 'scope_sha256': 'fixture',
            'hedge': {'snapshot_lag_minutes': 10, 'full_reconciliation_days': 28,
                'overlap_days': 7, 'queries': [{'key': 'example', 'anchor': 'Example'}]}}
        baseline = build(original, frozen)
        actions = baseline['properties']['definition']['actions']
        actions['Raw_dora_input'] = {'type': 'Compose', 'inputs': ['10.1234/dora']}
        actions['All_DOIs'] = {'type': 'Compose', 'runAfter': {'Raw_dora_input': ['Succeeded']},
            'inputs': "@union(outputs('Seed_DOIs'),body('Valid_DOIs'))"}
        actions['All_DOIs']['inputs'] = "@union(outputs('Seed_DOIs'),body('Valid_DOIs'))"
        actions['All_DOIs']['runAfter'] = {'Raw_dora_input': ['Succeeded']}
        actions['Manifest']['inputs']['raw_publication_producer_inputs'] = {'dora': 'retained'}
        before = copy.deepcopy(baseline)

        candidate = with_bounded_total_drift_restart(baseline)
        self.assertEqual(baseline, before)
        a = candidate['properties']['definition']['actions']
        self.assertEqual(candidate['properties']['connectionReferences'], baseline['properties']['connectionReferences'])
        self.assertEqual(a['Raw_dora_input'], baseline['properties']['definition']['actions']['Raw_dora_input'])
        self.assertEqual(a['All_DOIs']['inputs'], "@union(outputs('Seed_DOIs'),body('Valid_DOIs'))")
        self.assertEqual(a['Manifest']['inputs']['raw_publication_producer_inputs'], {'dora': 'retained'})
        self.assertEqual(a['Scope']['inputs']['hedge']['total_drift_max_restarts'], 1)
        self.assertNotEqual(a['Scope']['inputs']['scope_sha256'], 'fixture')
        q = a['For_each_query']['actions']['Query_may_run']['actions']
        self.assertNotIn('Reset_Cursor', q)
        self.assertEqual(q['Until_query_attempt']['limit']['count'], 3)
        self.assertIn('not(variables(\'QueryTotalDrift\'))', q['Until_query_attempt']['expression'])
        attempt = q['Until_query_attempt']['actions']
        self.assertEqual(attempt['Attempt_reset_Cursor']['inputs']['value'], '*')
        self.assertEqual(attempt['Attempt_reset_Done']['inputs']['value'], False)
        page = attempt['Until_query_complete']['actions']
        self.assertIn("-attempt-'", page['Save_page']['inputs']['parameters']['name'])
        self.assertIn("-attempt-'", page['Read_page']['inputs']['parameters']['path'])
        self.assertIn('If_total_stable', page)
        stable = page['If_total_stable']['actions']
        self.assertIn('Page_checkpoint', stable)
        self.assertNotIn('Page_checkpoint', page['If_total_stable']['else']['actions'])
        self.assertEqual(a['Manifest']['inputs']['query_attempts'], "@variables('AttemptSummaries')")
        self.assertIn("variables('QueryAccepted')", q['Guard_query_complete']['inputs'])
        def assert_local_run_after(actions, location='actions'):
            for name, action in actions.items():
                for dependency in action.get('runAfter', {}):
                    self.assertIn(dependency, actions, f'{location}/{name} depends on missing {dependency}')
                if 'actions' in action:
                    assert_local_run_after(action['actions'], f'{location}/{name}/actions')
                if 'else' in action:
                    assert_local_run_after(action['else'].get('actions', {}), f'{location}/{name}/else/actions')
        assert_local_run_after(a)
        with self.assertRaises(ValueError):
            with_bounded_total_drift_restart(candidate)
        with self.assertRaises(ValueError):
            with_bounded_total_drift_restart(baseline, 0)

    def test_created_date_partitions_are_contiguous_scoped_and_window_identity_is_preserved(self):
        original = {'properties': {'state': 'Stopped', 'displayName': 'RIMS Crossref',
            'connectionReferences': {'existing': {'connectionName': 'preserved'}},
            'definition': {'triggers': {'manual': {'type': 'Request', 'kind': 'Button'}},
                'actions': {'Run_folder': {'inputs': "@concat('/Documents/archive/crossref-source-',workflow()?['run']?['name'])"},
                    'Requested_ids': {'inputs': [{'id': '10.5555/example'}]},
                    'Create_exclusive_folder': {'inputs': {'host': {'connectionName': 'existing'},
                        'parameters': {'dataset': 'https://example.sharepoint.com/sites/research'}}}}}}}
        frozen = {'policy': {'source': 'crossref', 'scope': {'cadence': 'daily'}}, 'scope_sha256': 'fixture',
            'hedge': {'snapshot_lag_minutes': 10, 'full_reconciliation_days': 28,
                'overlap_days': 7, 'queries': [{'key': 'tropical', 'anchor': 'Tropical'}]}}
        baseline = with_bounded_total_drift_restart(build(original, frozen))
        baseline['properties']['definition']['actions']['Raw_dora_input'] = {
            'type': 'Compose', 'inputs': ['10.1234/dora']}
        before = copy.deepcopy(baseline)

        candidate = with_created_date_partitions(baseline, ('tropical',), 1, '2002-12-31')
        self.assertEqual(baseline, before)
        a = candidate['properties']['definition']['actions']
        self.assertEqual(candidate['properties']['connectionReferences'], baseline['properties']['connectionReferences'])
        self.assertEqual(a['Raw_dora_input'], baseline['properties']['definition']['actions']['Raw_dora_input'])
        self.assertNotEqual(a['Scope']['inputs']['scope_sha256'], baseline['properties']['definition']['actions']['Scope']['inputs']['scope_sha256'])
        hedge = a['Scope']['inputs']['hedge']
        self.assertEqual(hedge['created_date_partition']['months_per_window'], 1)
        self.assertEqual(hedge['created_date_partition']['first_unbounded_until'], '2002-12-31')
        self.assertEqual(hedge['queries'][0]['created_date_window_months'], 1)
        variables = {v['name']: v for v in a['Initialize_paging']['inputs']['variables']}
        self.assertEqual(variables['ExpectedQueryWindowCount']['value'], 0)
        self.assertEqual(variables['CreatedWindowDone']['value'], False)
        self.assertEqual(a['Manifest']['inputs']['scope_sha256'], a['Scope']['inputs']['scope_sha256'])
        self.assertEqual(a['Manifest']['inputs']['query_window_count'], "@variables('ExpectedQueryWindowCount')")
        self.assertEqual(a['Guard_all_queries']['inputs'].count("ExpectedQueryWindowCount"), 1)

        query_loop = a['For_each_query']['actions']['Query_may_run']['actions']['Until_created_windows']
        self.assertEqual(query_loop['limit']['count'], 5000)
        actions = query_loop['actions']
        self.assertIn("2002-12-31T23:59:59Z", actions['Set_created_window_end']['inputs']['value'])
        self.assertIn("concat('2002-12-31T23:59:59Z')),if(greater(ticks(addSeconds", actions['Set_created_window_end']['inputs']['value'])
        self.assertIn("until-created-date:", actions['Created_window_filter']['inputs'])
        self.assertIn("from-created-date:", actions['Created_window_filter']['inputs'])
        self.assertIn("outputs('Window_filter')", actions['Created_window_filter']['inputs'])
        self.assertEqual(actions['Initialize_query_attempt']['runAfter'], {'Created_window_filter': ['Succeeded']})
        attempt = actions['Until_query_attempt']['actions']
        page = attempt['Until_query_complete']['actions']
        self.assertIn("-window-'", page['Save_page']['inputs']['parameters']['name'])
        self.assertIn("-window-'", page['Read_page']['inputs']['parameters']['path'])
        self.assertIn("outputs('Created_window_filter')", page['Request_uri']['inputs'])
        self.assertIn('window_index', attempt['Query_attempt_summary']['inputs'])
        self.assertIn('-window-', actions['Save_query_summary']['inputs']['parameters']['name'])
        self.assertIn('-window-', actions['Read_query_summary']['inputs']['parameters']['path'])
        self.assertEqual(actions['Advance_created_window']['runAfter'], {'Append_query': ['Succeeded']})
        self.assertEqual(actions['Stop_created_windows_after_failure']['runAfter'], {'Mark_query_failed': ['Succeeded']})

        def assert_local_run_after(tree, location='actions'):
            for name, action in tree.items():
                for dependency in action.get('runAfter', {}):
                    self.assertIn(dependency, tree, f'{location}/{name} depends on missing {dependency}')
                if 'actions' in action:
                    assert_local_run_after(action['actions'], f'{location}/{name}/actions')
                if 'else' in action:
                    assert_local_run_after(action['else'].get('actions', {}), f'{location}/{name}/else/actions')
        assert_local_run_after(a)
        with self.assertRaises(ValueError):
            with_created_date_partitions(candidate, ('tropical',))
        with self.assertRaises(ValueError):
            with_created_date_partitions(baseline, ('missing',))
        with self.assertRaises(ValueError):
            with_created_date_partitions(baseline, ('tropical',), 0)

    def test_recovery_reuses_verified_prefix_without_mutating_receipt_or_scheduling_it(self):
        query = {'key': 'example', 'complete': True, 'expected': 1, 'received': 1,
                 'unique_dois': 1, 'pages': [{'file': 'example-page-0.json', 'rows': 1, 'saved_readback_equal': True}]}
        receipt = {'status': 'VERIFIED_FAILED_RUN_RECOVERY_INPUTS', 'source_run': 'old-run',
            'scope_sha256': 'fixture', 'archive_folder': '/Documents/archive/crossref-discovery-old-run',
            'until': '2026-10-18T00:00:00Z', 'window_filter': 'until-created-date:2026-10-18T00:00:00',
            'saved_page_readback_count': 1, 'saved_doi_readback_count': 1, 'queries': [query],
            'publication_dois': ['10.5555/first', '10.5555/second'],
            'doi_entries': [{'doi': '10.5555/first', 'file': 'doi-0.json', 'http_status': 200, 'saved_readback_equal': True}]}
        actions = {'Scope': {'inputs': {'scope_sha256': 'fixture', 'policy': {'source': 'crossref', 'scope': {'cadence': 'daily'}}, 'hedge': {'queries': [{'key': 'example'}]}}},
            'Run_folder': {'inputs': "@concat('/Documents/archive/crossref-discovery-',workflow()?['run']?['name'])"},
            'Initialize_paging': {'inputs': {'variables': [{'name': n, 'value': []} for n in ('Queries', 'DoiEntries', 'DoiIndex')]}},
            'For_each_query': {'runAfter': {'Verify_scope': ['Succeeded']}}, 'For_each_doi': {},
            'Cutoff': {}, 'Window_filter': {}, 'Full_reconciliation': {}, 'Manifest': {'inputs': {}}, 'Verify_completion': {}}
        doc = {'properties': {'state': 'Stopped', 'displayName': 'RIMS Crossref', 'definition': {'actions': actions}}}
        before, original = copy.deepcopy(receipt), copy.deepcopy(doc)
        candidate = resume_completed_hedge(doc, receipt)
        self.assertEqual(receipt, before)
        self.assertEqual(doc, original)
        a = candidate['properties']['definition']['actions']
        self.assertEqual(a['For_each_query']['type'], 'Compose')
        self.assertEqual(a['For_each_doi']['foreach'], "@skip(outputs('All_DOIs'),1)")
        self.assertEqual(a['For_each_doi']['runAfter'], {'Guard_recovery_dois': ['Succeeded']})
        self.assertEqual(a['Manifest']['inputs']['recovery']['archive_folder'], receipt['archive_folder'])
        with self.assertRaises(ValueError): with_daily_updates(candidate)
        receipt['doi_entries'][0]['doi'] = '10.5555/wrong'
        with self.assertRaises(ValueError): resume_completed_hedge(doc, receipt)


if __name__ == '__main__':
    unittest.main()
