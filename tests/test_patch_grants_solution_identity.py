import copy
import json
import pytest
from scripts.patch_grants_solution_identity import CONTRACT, COUNT, patch_definition


def baseline():
    document = json.loads(CONTRACT.read_text())
    root = document['properties']['definition']['actions']
    loop = root['Apply_to_each_Reviewed_Row']
    valid = loop['actions']['Condition_OpportunityKey_Present']['actions']
    allowed = valid['Condition_Conflicting_Source_Identity']['else']['actions']
    duplicate = allowed['Condition_Duplicate_OpportunityKey']
    del duplicate['actions']['Increment_Duplicate_Key_Failure_Count']
    duplicate['runAfter'] = {'SharePoint_Get_items': ['Succeeded']}
    branch = allowed['Condition_Is_New_Opportunity']
    exact = branch['else']['actions']['Condition_Exactly_One_Opportunity']
    if 'Condition_Observation_Time_Known' in exact['actions']:
        exact['actions'] = exact['actions']['Condition_Observation_Time_Known']['actions']['Condition_Observation_Not_Older']['actions']
    branch['expression'] = {'equals': [COUNT, 0]}
    branch['else']['actions']['Condition_Exactly_One_Opportunity']['expression'] = {'equals': [COUNT, 1]}
    loop['actions'] = {'SharePoint_Get_items': valid['SharePoint_Get_items'], **allowed}
    loop['runAfter'] = {'Parse_Reviewed_Rows': ['Succeeded']}
    del root['Initialize_Row_Failure_Count'], root['Condition_Any_Row_Failures']
    return document


def rows(document):
    return document['properties']['definition']['actions']['Apply_to_each_Reviewed_Row']['actions']


def test_preserves_native_writes_bindings_triggers_and_all_deadline_fields():
    original = baseline()
    snapshot = copy.deepcopy(original)
    updated = patch_definition(original)
    assert original == snapshot
    for field in ('connectionReferences',):
        assert updated['properties'][field] == original['properties'][field]
    assert updated['properties']['definition']['triggers'] == original['properties']['definition']['triggers']
    valid = rows(updated)['Condition_OpportunityKey_Present']['actions']
    allowed = valid['Condition_Conflicting_Source_Identity']['else']['actions']
    assert allowed['Condition_Is_New_Opportunity'] == rows(original)['Condition_Is_New_Opportunity']
    source = valid['SharePoint_Get_source_identity']['inputs']
    native = rows(original)['SharePoint_Get_items']['inputs']
    assert source['host'] == native['host']
    assert source['authentication'] == native['authentication']
    assert source['parameters']['dataset'] == native['parameters']['dataset']
    assert source['parameters']['table'] == native['parameters']['table']
    assert source['parameters']['$top'] == 1


def test_invalid_and_conflicting_identity_branches_have_no_connector_writes():
    updated = patch_definition(baseline())
    wrapper = rows(updated)['Condition_OpportunityKey_Present']
    # All four identity components must have a trimmed nonblank predicate.
    predicates = wrapper['expression']['and']
    assert len(predicates) == 4
    for field, predicate in zip(('OpportunityKey', 'Source', 'SourceID', 'EvidenceHash'), predicates):
        expression, empty = predicate['not']['equals']
        assert expression == "@trim(string(coalesce(item()?['" + field + "'], '')))"
        assert empty == ''
    def types(value):
        if isinstance(value, dict):
            return ([value['type']] if 'type' in value else []) + [t for child in value.values() for t in types(child)]
        if isinstance(value, list):
            return [t for child in value for t in types(child)]
        return []
    assert 'OpenApiConnection' not in types(wrapper['else']['actions'])
    conflict = wrapper['actions']['Condition_Conflicting_Source_Identity']
    assert 'OpenApiConnection' not in types(conflict['actions'])
    assert conflict['runAfter'] == {'SharePoint_Get_source_identity': ['Succeeded']}
    assert wrapper['actions']['SharePoint_Get_source_identity']['runAfter'] == {'SharePoint_Get_items': ['Succeeded']}
    assert updated['properties']['definition']['actions']['Condition_Any_Row_Failures']['actions']['Terminate_Row_Failures']['inputs']['runStatus'] == 'Failed'


@pytest.mark.parametrize('mutation', ['parallel', 'filter', 'extra', 'guard'])
def test_rejects_drift(mutation):
    document = baseline()
    if mutation == 'parallel':
        document['properties']['definition']['actions']['Apply_to_each_Reviewed_Row']['runtimeConfiguration']['concurrency']['repetitions'] = 2
    elif mutation == 'filter':
        rows(document)['SharePoint_Get_items']['inputs']['parameters']['$filter'] = 'wrong'
    elif mutation == 'extra':
        rows(document)['Unexpected'] = {'type': 'Compose'}
    else:
        rows(document)['Condition_Is_New_Opportunity']['expression'] = {'equals': [COUNT, 2]}
    with pytest.raises(ValueError):
        patch_definition(document)
