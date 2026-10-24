import copy
import hashlib
import json
from pathlib import Path
import unittest
from scripts.crossref_targeted_policy import validate, normalize_doi, precision, doi_queue, DISABLED
from scripts.prepare_crossref_targeted import prepare
from scripts.prepare_crossref_discovery_collection import build, with_bounded_total_drift_restart, with_created_date_partitions
from scripts.crossref_definition import fingerprint


class TargetedPolicyTests(unittest.TestCase):
    def setUp(self):
        self.hedge = json.loads(Path('config/crossref-acquisition-hedge.json').read_text())
        self.collector = json.loads(Path('config/collector.json').read_text())

    def test_alias_gaps_are_explicit_and_broad_tokens_cannot_reenter(self):
        validate(self.hedge, self.collector)
        self.assertTrue(any(r['alias'] == 'Tropical Public Health Services' and r['independent_discovery_gap'] for r in self.hedge['alias_routes']))
        bad = copy.deepcopy(self.hedge); bad['queries'].append(bad['disabled_queries'][0])
        with self.assertRaises(ValueError): validate(bad, self.collector)
        bad = copy.deepcopy(self.hedge); bad['alias_routes'].pop()
        with self.assertRaises(ValueError): validate(bad, self.collector)

    def test_precision_rejects_drift_and_does_not_attribute_unmatched_records(self):
        raw = json.dumps({'request_url': 'https://api.crossref.org/works?query.affiliation=Cairns', 'status_code': 200,
            'body': {'message-type': 'work-list', 'message': {'items': [
                {'DOI': '10.1234/one', 'author': [{'affiliation': [{'name': 'Unit, Cairns Hospital, Australia'}]}]},
                {'DOI': '10.1234/two', 'author': [{'affiliation': [{'name': 'University of Tropical Medicine'}]}]}]}}}).encode()
        proof = {'id': 'native-id', 'etag': 'version-1', 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest(), 'file': 'raw.json'}
        report = precision([('cairns', 'Cairns', raw, proof)], ['Cairns Hospital'])
        self.assertEqual(report['queries'][0]['explicit_alias_match_dois'], 1)
        self.assertEqual(report['queries'][0]['unresolved_dois'], 1)
        self.assertEqual([r['doi'] for r in report['observations']], ['10.1234/one'])
        with self.assertRaises(ValueError): precision([('cairns', 'Cairns', raw + b' ', proof)], ['Cairns Hospital'])
        with self.assertRaises(ValueError): precision([('other', 'Other', raw, proof)], ['Cairns Hospital'])

    def test_doi_queue_preserves_provenance_and_reuses_only_fresh_identity_matched_bytes(self):
        records = [{'doi': 'https://doi.org/10.1234/ABC', 'source': 'pubmed', 'source_record': 'pmid:1', 'accepted': True, 'evidence': {'sha256': 'source-proof'}},
                   {'doi': 'doi:10.1234/abc', 'source': 'dora_publications', 'source_record': 'dora:2', 'accepted': True, 'evidence': {'sha256': 'other-proof'}}]
        raw = json.dumps({'requested_doi': '10.1234/abc', 'status_code': 200, 'body': {'message': {'DOI': '10.1234/abc'}}}).encode()
        cached = {'raw': raw, 'observed_utc': '2026-10-23T00:00:00Z', 'evidence': {'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw), 'id': 'raw-id', 'etag': 'raw-v1'}}
        q = doi_queue(records, {'10.1234/abc': [cached]}, now='2026-10-24T00:00:00Z')
        self.assertEqual(len(q['entries']), 1); self.assertEqual(len(q['entries'][0]['provenance']), 2)
        self.assertEqual(q['entries'][0]['action'], 'reuse')
        changed = [dict(records[0], refresh_required=True)]
        self.assertEqual(doi_queue(changed, {'10.1234/abc': [cached]}, now='2026-10-24T00:00:00Z')['entries'][0]['action'], 'fetch')
        self.assertEqual(doi_queue(records, {'10.1234/abc': [cached]}, now='2026-12-24T00:00:00Z')['entries'][0]['action'], 'fetch')
        bad = copy.deepcopy(cached); bad['raw'] += b' '
        with self.assertRaises(ValueError): doi_queue(records, {'10.1234/abc': [bad]}, now='2026-10-24T00:00:00Z')
        bad_record = dict(records[0], source='crossref_verified_discovery')
        with self.assertRaises(ValueError): doi_queue([bad_record], {}, now='2026-10-24T00:00:00Z')
        self.assertIsNone(normalize_doi('not a doi')); self.assertEqual(normalize_doi('doi:10.1234/A%2FB'), '10.1234/a/b')

    def test_bootstrap_does_not_accept_or_drop_existing_dois(self):
        from scripts.prepare_crossref_bootstrap import prepare as bootstrap
        checkpoint = {'source': 'crossref', 'complete': True, 'scope_sha256': 'old', 'doi_lookups': [{'doi': '10.1234/one'}]}
        prefix = {'source_run': 'run', 'until': '2026-10-23T00:00:00Z', 'scope_sha256': 'old-scope', 'queries': []}
        inputs = {'source_run': 'run', 'until': prefix['until'], 'files': []}
        scope = {'scope_sha256': 'new', 'hedge': {'queries': []}}
        packet = bootstrap(checkpoint, prefix, inputs, {'entries': [{'doi': '10.1234/one'}]}, scope)
        self.assertFalse(packet['accepted']); self.assertFalse(packet['complete'])
        self.assertFalse(packet['native_terminal_gate_satisfied'])
        self.assertEqual(packet['accepted_dois_preserved'], 1)
        from scripts.prepare_crossref_bootstrap import stage_bundle
        bundle = stage_bundle(packet, dict(prefix, archive_folder='/Documents/archive/crossref-discovery-old'), inputs, {'files': []}, scope)
        self.assertFalse(bundle['progress']['accepted'])
        self.assertEqual(bundle['native_writes'], 0)
        self.assertEqual(bundle['donor_windows'], 0)
        with self.assertRaises(ValueError): bootstrap(checkpoint, prefix, inputs, {'entries': []}, scope)
        with self.assertRaises(ValueError): bootstrap(checkpoint, prefix, inputs, {'entries': []}, dict(scope, scope_sha256='old'))

    def test_page_yield_cannot_complete_query_and_preserves_original_inputs(self):
        # Synthetic envelope exercises the real compiler without any tenant data.
        original = {'name': 'existing-id', 'properties': {'state': 'Stopped', 'displayName': 'RIMS Crossref',
            'connectionReferences': {'existing': {'connectionName': 'preserved'}}, 'definition': {
                'triggers': {'manual': {'type': 'Request', 'kind': 'Button'}}, 'actions': {
                    'Run_folder': {'inputs': "@concat('/Documents/archive/crossref-source-',workflow()?['run']?['name'])"},
                    'Requested_ids': {'inputs': [{'id': '10.1234/example'}]},
                    'Create_exclusive_folder': {'inputs': {'host': {'connectionName': 'existing'},
                        'parameters': {'dataset': 'https://example.sharepoint.com/sites/research'}}}}}}}
        frozen = {'policy': {'source': 'crossref'}, 'scope_sha256': 'old', 'hedge': {
            'snapshot_lag_minutes': 10, 'full_reconciliation_days': 28, 'overlap_days': 7,
            'queries': [{'key': 'tropical', 'anchor': 'Tropical'}]}}
        baseline = with_created_date_partitions(with_bounded_total_drift_restart(build(original, frozen)))
        # The production preimage already has qualified sequential initializers.
        actions = baseline['properties']['definition']['actions']
        initial = actions['Initialize_paging']['inputs']['variables']
        previous = next(iter(actions['Initialize_paging']['runAfter']))
        for variable in initial[:-1]:
            key = 'Initialize_paging_' + variable['name']
            actions[key] = {'type': 'InitializeVariable', 'runAfter': {previous: ['Succeeded']}, 'inputs': {'variables': [variable]}}
            previous = key
        actions['Initialize_paging']['inputs']['variables'] = [initial[-1]]
        actions['Initialize_paging']['runAfter'] = {previous: ['Succeeded']}
        # Production includes publication producer reads; the fixture keeps a seed-only input.
        actions['All_DOIs'] = {'type': 'Compose', 'runAfter': {'Seed_DOIs': ['Succeeded']}, 'inputs': "@outputs('Seed_DOIs')"}
        actions['For_each_doi']['runAfter'] = {'All_DOIs': ['Succeeded']}
        before = copy.deepcopy(baseline)
        result = prepare(baseline, self.hedge, self.collector, {'source': 'crossref'}, expected_definition_sha256=fingerprint(baseline['properties']['definition']))
        self.assertEqual(before, baseline)
        daily = result['incremental']; self.assertEqual(daily['name'], 'existing-id')
        self.assertEqual(daily['properties']['connectionReferences'], baseline['properties']['connectionReferences'])
        self.assertEqual(daily['properties']['definition']['triggers'], baseline['properties']['definition']['triggers'])
        a = daily['properties']['definition']['actions']
        self.assertFalse(DISABLED.intersection(q['key'] for q in a['Scope']['inputs']['hedge']['queries']))
        q = a['For_each_query']['actions']['Query_may_run']['actions']
        self.assertIn('BatchYield', q['Until_query_attempt']['actions']['Until_query_complete']['expression'])
        self.assertNotIn('Query_summary', q)
        self.assertEqual(q['Batch_window_complete']['expression'], "@variables('QueryAccepted')")
        self.assertEqual(a['Batch_progress']['inputs']['format'], 'rims-crossref-progress-incremental-v2')
        self.assertFalse(a['Batch_progress']['inputs']['accepted'])
        self.assertIn('PendingWindow', a['Batch_progress']['inputs']['pending_window'])
        self.assertIn('Batch_verify_pending_pages', a['Batch_started']['runAfter'])
        self.assertEqual(result['baseline_worker']['properties']['state'], 'Stopped')
        self.assertEqual(a['Scope']['inputs']['hedge']['created_date_partition']['query_keys'], [])
        self.assertEqual(a['Scope']['inputs']['scope_sha256'], result['baseline_worker']['properties']['definition']['actions']['B_Scope']['inputs']['scope_sha256'])
        bootstrap = a['Bootstrap_if_needed']['actions']
        self.assertIn("?['complete'],true", bootstrap['Bootstrap_guard_baseline']['inputs'])
        self.assertIn('scope_sha256', bootstrap['Bootstrap_guard_baseline']['inputs'])
        self.assertIn('scope_sha256', a['Progress_load']['actions']['Progress_is_obsolete']['expression'])
        self.assertIn('Batch_verify_completed_pages', a['Batch_verify_prefix']['actions'])
        cache = a['Batch_finalize']['actions']['For_each_doi']['actions']['Doi_may_run']['actions']
        self.assertFalse(any(card['type'] == 'Query' for card in cache.values()))
        self.assertIn('BatchChangedDOIs', cache['Doi_cache_or_fetch']['expression'])
        self.assertIn('Doi_checkpoint_cache_index', a['Batch_finalize']['actions'])
        self.assertIn('_bootstrap.json', bootstrap['Bootstrap_save']['inputs']['parameters']['name'])
        self.assertEqual(bootstrap['Bootstrap_set_marker']['runAfter'], {'Bootstrap_verify': ['Succeeded']})
        self.assertLess('crossref-complete-run.json', 'crossref-complete-run_bootstrap.json')


if __name__ == '__main__': unittest.main()
