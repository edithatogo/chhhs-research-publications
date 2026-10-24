import copy
import json
import unittest
from scripts.flow_deployment import prepare, verify, validate_inputs


class FlowDeploymentTests(unittest.TestCase):
    def setUp(self):
        self.candidate = {'properties': {'connectionReferences': {'sp': {'source': 'Invoker', 'connectionReferenceLogicalName': 'test'}}, 'definition': {'triggers': {'manual': {'type': 'Request', 'kind': 'Button', 'inputs': {'schema': {'type': 'object', 'properties': {'Rows': {'type': 'string'}}, 'required': ['Rows']}}}}, 'actions': {}}}}
        self.snapshot = {'published': {'workflowid': '00000000-0000-0000-0000-000000000001', 'name': 'Synthetic "flow"', 'statecode': 0, 'componentstate': 0, 'clientdata': json.dumps(self.candidate)}, 'draft_checked': True, 'draft': None, 'runs_complete': True, 'active_runs': []}

    def test_prepare_and_exact_saved_definition_comparison(self):
        old = copy.deepcopy(self.snapshot)
        self.candidate['properties']['definition']['actions']['new'] = {'type': 'Compose', 'inputs': 'value'}
        plan, formula = prepare(self.snapshot, self.candidate, {'Rows': '[]'})
        self.assertIn('Synthetic ""flow""', formula)
        self.assertIn('Patch(Processes', formula)
        self.assertFalse(plan['atomic_conditional_write'])
        self.assertEqual(self.snapshot, old)
        with self.assertRaises(ValueError):
            verify(plan, self.candidate, self.snapshot)
        after = copy.deepcopy(self.snapshot)
        after['published']['clientdata'] = json.dumps(self.candidate)
        self.assertFalse(verify(plan, self.candidate, after)['native_runtime_proven'])
        after['published']['name'] = 'different'
        with self.assertRaises(ValueError):
            verify(plan, self.candidate, after)

    def test_unknown_draft_running_and_credential_substitution_refused(self):
        for key, value in [('draft_checked', False), ('draft', {}), ('runs_complete', False), ('active_runs', ['Running'])]:
            snapshot = copy.deepcopy(self.snapshot)
            snapshot[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                prepare(snapshot, self.candidate)
        changed = copy.deepcopy(self.candidate)
        changed['properties']['connectionReferences']['sp']['source'] = 'Embedded'
        with self.assertRaises(ValueError):
            prepare(self.snapshot, changed)

    def test_explicit_inputs_no_coercion_or_silent_omission(self):
        for body in ({}, {'Rows': []}, {'Rows': '[]', 'surprise': 'x'}):
            with self.subTest(body=body), self.assertRaises(ValueError):
                validate_inputs(self.candidate, body)
        self.assertFalse(validate_inputs(self.candidate, {'Rows': '[]'})['invoked'])

    def test_mixed_host_and_public_receipt_outputs_refused(self):
        from scripts.flow_deployment import private_output
        from pathlib import Path
        with self.assertRaises(ValueError):
            private_output(Path('/tmp/public-result.json'))
        changed = copy.deepcopy(self.candidate)
        changed['properties']['definition']['actions']['unsafe'] = {'inputs': {'host': {'connection': {}, 'connectionName': 'sp'}}}
        with self.assertRaises(ValueError):
            prepare(self.snapshot, changed)

    def test_unqualified_schema_constraint_is_not_silently_ignored(self):
        changed = copy.deepcopy(self.candidate)
        changed['properties']['definition']['triggers']['manual']['inputs']['schema']['properties']['Rows']['pattern'] = '^accepted$'
        with self.assertRaises(ValueError):
            validate_inputs(changed, {'Rows': 'rejected'})
