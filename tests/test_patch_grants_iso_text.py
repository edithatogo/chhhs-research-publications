import copy
import unittest

from scripts.patch_grants_iso_text import patch


class ISOTextWriteRepairTests(unittest.TestCase):
    def fixture(self):
        def action(operation):
            return {'type': 'OpenApiConnection', 'inputs': {
                'host': {'operationId': operation, 'connectionName': 'existing'},
                'parameters': {'dataset': 'https://example.sharepoint.com/sites/test',
                               'table': '00000000-0000-4000-8000-000000000001',
                               'item/RetrievedUTC': "@{item()?['RetrievedUTC']}",
                               'item/DeadlineUTCInstant': "@{item()?['DeadlineUTCInstant']}"}}}
        return {'properties': {'connectionReferences': {'existing': {'source': 'Invoker'}},
                               'definition': {'actions': {
                                   'SharePoint_Create_item': action('PostItem'),
                                   'nested': {'actions': {'SharePoint_Update_item': action('PatchItem')}}}}}}

    def test_preserves_existing_graph_and_binds_each_literal_write_to_its_item(self):
        before = self.fixture()
        after = patch(before)
        stripped = copy.deepcopy(after)
        create = stripped['properties']['definition']['actions'].pop('SharePoint_Create_item_Preserve_ISO_Text')
        update = stripped['properties']['definition']['actions']['nested']['actions'].pop('SharePoint_Update_item_Preserve_ISO_Text')
        self.assertEqual(stripped, before)
        for name, action in [('SharePoint_Create_item', create), ('SharePoint_Update_item', update)]:
            self.assertEqual(action['runAfter'], {name: ['Succeeded']})
            self.assertEqual(action['inputs']['host']['connectionName'], 'existing')
            self.assertEqual(action['inputs']['host']['operationId'], 'HttpRequest')
            self.assertIn('setProperty', action['inputs']['parameters']['parameters/body'])
            self.assertNotIn('formatDateTime', action['inputs']['parameters']['parameters/body'])
        self.assertIn("body('SharePoint_Create_item')?['ID']", create['inputs']['parameters']['parameters/uri'])
        self.assertIn("first(body('SharePoint_Get_items')", update['inputs']['parameters']['parameters/uri'])

    def test_rejects_repeated_repair_or_unrecognised_write(self):
        with self.assertRaisesRegex(ValueError, 'already exists'):
            patch(patch(self.fixture()))
        source = self.fixture()
        source['properties']['definition']['actions']['SharePoint_Create_item']['inputs']['host']['operationId'] = 'DeleteItem'
        with self.assertRaisesRegex(ValueError, 'Unexpected'):
            patch(source)
