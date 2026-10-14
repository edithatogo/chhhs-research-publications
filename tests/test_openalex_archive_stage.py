import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from prepare_openalex_archive_stage import build, build_stage_fragment
from prepare_openalex_retention import build as retain
import test_openalex_retention as retention_fixture


class ArchiveStage(unittest.TestCase):
    def setUp(self):
        fixture = retention_fixture.OpenAlexRetention()
        fixture.setUp()
        self.prepared = retain(fixture.frozen, fixture.candidate)
        self.records = json.loads(fixture.frozen) + [{'DOI': '10.1000/not-requested'}]

    def test_pages_reconstruct_all_original_chunks_without_commit_marker(self):
        files, receipt = build(self.prepared, self.records, 'openalex-fixed')
        restored = [{k[1:-1]: v for k, v in row.items()}
                    for raw in files.values() for row in json.loads(raw)]
        self.assertEqual(restored, self.prepared['chunks'])
        self.assertTrue(all(len(json.loads(raw)) <= 2 for raw in files.values()))
        self.assertFalse(any(name.startswith('commit-') for name in files))
        self.assertFalse(receipt['accepted_commit'])
        self.assertEqual(receipt['remaining_doi_batches'], [['10.1000/not-requested']])

    def test_foreign_source_and_failed_pass_cannot_enter_archive(self):
        with self.assertRaises(ValueError):
            build(self.prepared, [{'DOI': '10.1000/foreign'}], 'openalex-fixed')
        self.prepared['attempt_statuses'].append({'RequestedDOI': '10.1000/not-requested',
                                                 'Status': 'unavailable'})
        with self.assertRaises(ValueError):
            build(self.prepared, self.records, 'openalex-fixed')

    def test_fragment_reuses_connection_and_keeps_manifest_and_commit_gates(self):
        import copy
        host = {'connectionName': 'shared_onedriveforbusiness', 'apiId': 'existing'}
        flow = {'properties': {'definition': {
            'triggers': {'manual': {'inputs': {'schema': {'required': ['text']}}}},
            'actions': {
                'Compose': {'inputs': 'text'},
                'Read': {'type': 'OpenApiConnection', 'inputs': {
                    'host': {**host, 'operationId': 'GetFileContentByPath'},
                    'parameters': {'path': 'old', 'inferContentType': True}}},
                'Write': {'type': 'OpenApiConnection', 'inputs': {
                    'host': {**host, 'operationId': 'CreateFile'},
                    'parameters': {'folderPath': '/DEV/01 Source archive'}}}}}}}
        original = copy.deepcopy(flow)
        files, receipt = build(self.prepared, self.records, 'openalex-fixed')
        fragment = build_stage_fragment(flow, files, receipt)
        self.assertEqual(flow, original)
        self.assertFalse(fragment['commit_marker_emitted'])
        loop = fragment['actions']['OpenAlex_Archive_Pages']
        self.assertEqual(loop['runtimeConfiguration']['concurrency']['repetitions'], 1)
        self.assertEqual(loop['runAfter'], {'Require_OpenAlex_generation': ['Succeeded']})
        self.assertIn('404', loop['actions']['OpenAlex_Page_Exists']['else']['actions']
                      ['Require_OpenAlex_page_absent']['inputs'])
        self.assertIn('ARCHIVE_CONFLICT', loop['actions']['Require_OpenAlex_page_exact']['inputs'])
        flow['properties']['definition']['triggers']['manual']['inputs']['schema']['required'] = []
        with self.assertRaises(ValueError):
            build_stage_fragment(flow, files, receipt)


if __name__ == '__main__':
    unittest.main()
