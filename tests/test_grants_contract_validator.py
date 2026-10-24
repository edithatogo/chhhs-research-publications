"""Keep the CI contract aligned with the qualified native connector format."""
import json
from pathlib import Path
import unittest

from scripts.validate_grants_flow_contract import validate


class GrantsContractValidatorTests(unittest.TestCase):
    def setUp(self):
        root = Path(__file__).parents[1]
        self.definition = json.loads((root / 'config/flows/grants-registry-reviewed-import.definition.json').read_text())['properties']['definition']
        loop = self.definition['actions']['Apply_to_each_Reviewed_Row']
        self.valid = loop['actions']['Condition_OpportunityKey_Present']['actions']
        self.create = self.valid['Condition_Conflicting_Source_Identity']['else']['actions']['Condition_Is_New_Opportunity']['actions']['SharePoint_Create_item']

    def test_qualified_reference_only_definition_passes(self):
        self.assertEqual(validate(self.definition), [])
        self.assertNotIn('authentication', self.create['inputs'])

    def test_rejected_auth_annotations_fail_on_lookup_and_create(self):
        for action in [self.valid['SharePoint_Get_items'], self.create]:
            with self.subTest(action=action['inputs']['host']['operationId']):
                action['inputs']['authentication'] = {'type': 'Raw', 'value': "@parameters('$authentication')"}
                self.assertTrue(any('rejected authentication annotations' in x for x in validate(self.definition)))
                del action['inputs']['authentication']

    def test_create_cannot_silently_switch_connection_alias(self):
        self.create['inputs']['host']['connectionName'] = 'unqualified_reference'
        self.assertIn('create action must preserve the lookup connection reference alias', validate(self.definition))
