import copy
import json
from pathlib import Path
import unittest

from scripts.patch_grants_conditional_commit import patch, HUMAN_FIELDS


class ConditionalCommitTests(unittest.TestCase):
    def setUp(self):
        self.original = json.loads((Path(__file__).parents[1] / 'config/flows/grants-registry-reviewed-import.definition.json').read_text())
        self.candidate = patch(self.original)

    def writes(self, document):
        found = []
        def walk(actions):
            if 'SharePoint_Update_item' in actions:
                found.append(actions)
            for a in actions.values():
                walk(a.get('actions', {}))
                walk(a.get('else', {}).get('actions', {}))
        walk(document['properties']['definition']['actions'])
        return found[0]

    def test_preserves_credentials_identity_and_original(self):
        self.assertEqual(self.candidate['properties']['connectionReferences'], self.original['properties']['connectionReferences'])
        self.assertEqual(json.loads((Path(__file__).parents[1] / 'config/flows/grants-registry-reviewed-import.definition.json').read_text()), self.original)
        self.assertEqual(self.candidate['properties']['definition']['triggers']['manual']['runtimeConfiguration']['concurrency']['runs'], 1)

    def test_one_conditional_source_and_iso_commit(self):
        actions = self.writes(self.candidate)
        self.assertNotIn('SharePoint_Update_item_Preserve_ISO_Text', actions)
        commit = actions['SharePoint_Update_item']['inputs']
        self.assertEqual(commit['host']['operationId'], 'HttpRequest')
        self.assertEqual(commit['retryPolicy'], {'type': 'none'})
        self.assertEqual(commit['parameters']['parameters/headers']['IF-MATCH'], "@first(body('SharePoint_Read_commit_version')?['value'])?['@odata.etag']")
        text = commit['parameters']['parameters/body']
        for name in HUMAN_FIELDS:
            self.assertNotIn(name, text)
        for name in ('RetrievedUTC', 'DeadlineUTCInstant', 'EvidenceHash', 'SourceAttribution', 'DeadlineScheduleJSON'):
            self.assertIn(name, text)

    def test_guard_rejects_missing_duplicate_stale_or_changed_source(self):
        a = self.writes(self.candidate)
        guard = a['Guard_Commit_Source_Unchanged']['inputs']
        for term in ('GRANTS_SOURCE_VERSION_DRIFT', 'length(', "['ID']", "['@odata.etag']", "['EvidenceHash']", "['RetrievedUTC']", "['DeadlineScheduleJSON']"):
            self.assertIn(term, guard)
        self.assertEqual(a['SharePoint_Update_item']['runAfter'], {'Guard_Commit_Source_Unchanged': ['Succeeded']})

    def test_only_existing_update_graph_changes(self):
        left, right = copy.deepcopy(self.original), copy.deepcopy(self.candidate)
        self.writes(left).clear()
        self.writes(right).clear()
        self.assertEqual(left, right)

    def test_unknown_mapping_and_second_application_fail_closed(self):
        changed = copy.deepcopy(self.original)
        self.writes(changed)['SharePoint_Update_item']['inputs']['parameters']['item/Title'] = '@unqualified()'
        with self.assertRaisesRegex(ValueError, 'Unknown source mapping'):
            patch(changed)
        with self.assertRaises(ValueError):
            patch(self.candidate)


if __name__ == '__main__':
    unittest.main()
