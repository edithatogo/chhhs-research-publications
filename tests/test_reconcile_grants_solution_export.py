import copy
import json
from pathlib import Path
import tempfile
import unittest
from zipfile import ZipFile

from scripts.reconcile_grants_solution_export import TEMPLATE, actions, reconcile


class GrantsExportReconciliationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        definition = json.loads(TEMPLATE.read_text())['properties']['definition']
        text = json.dumps(definition).replace('{{SHAREPOINT_SITE_URL}}', 'https://example.sharepoint.com/sites/test')
        text = text.replace('{{SHAREPOINT_LIST_ID}}', '00000000-0000-4000-8000-000000000001')
        self.definition = json.loads(text)
        self.definition['triggers']['manual']['metadata'] = {
            'operationMetadataId': '00000000-0000-4000-8000-000000000002'}

    def archive(self, definition=None, managed='0', references=True, runtime_source='invoker'):
        document = {'properties': {'definition': definition or self.definition,
            'connectionReferences': {'shared_sharepointonline': {
                'runtimeSource': runtime_source, 'api': {'name': 'shared_sharepointonline'},
                'connection': {'connectionReferenceLogicalName': 'test_sharepoint_reference'}}}}}
        path = self.folder / 'fixture.zip'
        with ZipFile(path, 'w') as zipped:
            zipped.writestr('solution.xml', '<ImportExportXml><SolutionManifest>'
                '<UniqueName>CHHHSRIMSPlatform</UniqueName><Version>1.0.0.0</Version>'
                f'<Managed>{managed}</Managed></SolutionManifest></ImportExportXml>')
            zipped.writestr('customizations.xml', '<ImportExportXml>' + (
                '<connectionreference connectionreferencelogicalname="test_sharepoint_reference" />'
                if references else '') + '</ImportExportXml>')
            zipped.writestr('Workflows/CHHHSRIMSGrantsReviewedimportupsert-fixture.json', json.dumps(document))
        return path

    def test_exact_graph_accepts_only_target_and_generated_id_normalization(self):
        result = reconcile(self.archive())
        self.assertEqual(result['status'], 'PASS_EXPORT_SOURCE_PARITY')
        self.assertEqual(result['workflow_count'], 1)
        self.assertFalse(result['native_acceptance'])

    def test_old_authentication_is_not_normalized_away(self):
        changed = copy.deepcopy(self.definition)
        graph = dict(actions(changed['actions']))
        graph['SharePoint_Create_item']['inputs']['authentication'] = {"type": "Raw", "value": "@parameters('$authentication')"}
        with self.assertRaisesRegex(ValueError, 'differs'):
            reconcile(self.archive(changed))

    def test_changed_deadline_guard_is_rejected(self):
        changed = copy.deepcopy(self.definition)
        graph = dict(actions(changed['actions']))
        graph['Condition_Observation_Not_Older']['expression'] = True
        with self.assertRaisesRegex(ValueError, 'differs'):
            reconcile(self.archive(changed))

    def test_unknown_metadata_is_not_silently_ignored(self):
        changed = copy.deepcopy(self.definition)
        changed['triggers']['manual']['metadata']['authoredBehavior'] = 'changed'
        with self.assertRaisesRegex(ValueError, 'metadata'):
            reconcile(self.archive(changed))

    def test_split_action_targets_are_rejected(self):
        changed = copy.deepcopy(self.definition)
        graph = dict(actions(changed['actions']))
        graph['SharePoint_Update_item']['inputs']['parameters']['table'] = '00000000-0000-4000-8000-000000000003'
        with self.assertRaisesRegex(ValueError, 'target differs'):
            reconcile(self.archive(changed))

    def test_missing_connection_reference_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'reference'):
            reconcile(self.archive(references=False))

    def test_runtime_source_drift_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'reference'):
            reconcile(self.archive(runtime_source='embedded'))

    def test_managed_package_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'managed'):
            reconcile(self.archive(managed='1'))

    def test_unsafe_entry_is_rejected_without_extraction(self):
        path = self.archive()
        with ZipFile(path, 'a') as zipped:
            zipped.writestr('../unsafe', 'fixture')
        with self.assertRaisesRegex(ValueError, 'unsafe'):
            reconcile(path)


if __name__ == '__main__':
    unittest.main()
