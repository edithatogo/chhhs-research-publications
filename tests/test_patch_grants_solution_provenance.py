import copy

import pytest

from scripts.patch_grants_solution_identity import patch_definition as guard
from scripts.patch_grants_solution_provenance import patch_definition
from test_patch_grants_solution_identity import baseline as fixture


def baseline():
    result = guard(fixture())
    for action in targets(result):
        action['inputs']['parameters']['item/URL'] = "@{item()?['URL']}"
        action['inputs']['parameters'].pop('item/SourceRowURL', None)
    return result


def targets(document):
    valid = document['properties']['definition']['actions']['Apply_to_each_Reviewed_Row']['actions']['Condition_OpportunityKey_Present']['actions']
    branch = valid['Condition_Conflicting_Source_Identity']['else']['actions']['Condition_Is_New_Opportunity']
    return (branch['actions']['SharePoint_Create_item'],
        branch['else']['actions']['Condition_Exactly_One_Opportunity']['actions']['SharePoint_Update_item'])


def test_only_two_provenance_mappings_change_and_input_is_preserved():
    original = baseline()
    saved = copy.deepcopy(original)
    patched = patch_definition(original)
    assert original == saved
    assert patch_definition(patched) == patched
    for action in targets(patched):
        assert action['inputs']['parameters'].pop('item/SourceRowURL') == "@{item()?['SourceRowURL']}"
    assert patched == original


@pytest.mark.parametrize('field,value', [('item/URL', 'changed'), ('item/SourceRowURL', 'changed')])
def test_mapping_drift_is_rejected(field, value):
    original = baseline()
    targets(original)[1]['inputs']['parameters'][field] = value
    with pytest.raises(ValueError):
        patch_definition(original)


def test_unguarded_definition_is_rejected():
    with pytest.raises(KeyError):
        patch_definition(fixture())
