import pytest
from pathlib import Path

# Skip entire module if private/ops evidence files not present
ROOT = Path(__file__).resolve().parents[1]
PRIVATE_OPS_ROOT = ROOT / "private" / "ops"
REQUIRED_EVIDENCE_FILES = [
    "2026-09-28-arc-awards-two-pass-keyset-snapshot-private.json",
    "2026-09-28-grants-finder-contribution-api-reconciliation-private.json",
    "2026-10-07-g02-arc-two-date-row-reconciliation-private.json",
    "2026-10-23-g02-qgip-official-resource-recheck/full-snapshot.json",
    "2026-10-23-g02-qgip-official-resource-recheck/snapshot-comparison.json",
]
if not all((PRIVATE_OPS_ROOT / f).exists() for f in REQUIRED_EVIDENCE_FILES):
    pytest.skip("private/ops evidence files not present; skipping grants solution deadlines tests", allow_module_level=True)

import copy
from scripts.patch_grants_solution_deadlines import COUNT, FIELDS, patch_definition


def fixture():
    def action(operation):
        return {'inputs': {'host': {'operationId': operation, 'connectionName': 'preserved'},
                           'parameters': {'dataset': 'preserved', 'item/Title': 'preserved'}}}
    return {'properties': {'connectionReferences': {'preserved': {}}, 'definition': {'triggers': {'preserved': {}}, 'actions': {
        'Apply_to_each_Reviewed_Row': {'actions': {
            'SharePoint_Get_items': {'inputs': {'parameters': {'$top': 2, '$filter': 'OpportunityKey eq test'}}},
            'Condition_Is_New_Opportunity': {'expression': {'equals': [COUNT, 0]},
                'actions': {'SharePoint_Create_item': action('PostItem')},
                'else': {'actions': {'Condition_Exactly_One_Opportunity': {
                    'expression': {'equals': [COUNT, 1]}, 'actions': {'SharePoint_Update_item': action('PatchItem')}}}}}
        }}}}}}


def params(document):
    branch = document['properties']['definition']['actions']['Apply_to_each_Reviewed_Row']['actions']['Condition_Is_New_Opportunity']
    return (branch['actions']['SharePoint_Create_item']['inputs']['parameters'],
            branch['else']['actions']['Condition_Exactly_One_Opportunity']['actions']['SharePoint_Update_item']['inputs']['parameters'])


def test_only_twelve_mappings_change_and_input_is_preserved():
    original = fixture()
    snapshot = copy.deepcopy(original)
    patched = patch_definition(original)
    assert original == snapshot
    for target in params(patched):
        assert all('item/' + field in target for field in FIELDS)
        assert isinstance(target['item/DeadlineTemporalStatus'], dict)
        for field in FIELDS:
            del target['item/' + field]
    assert patched == original


def test_idempotent_and_conflicting_mapping_rejected():
    patched = patch_definition(fixture())
    assert patch_definition(patched) == patched
    params(patched)[0]['item/DeadlineTimezone'] = 'incorrect'
    with pytest.raises(ValueError):
        patch_definition(patched)


def test_wrong_update_guard_rejected():
    document = fixture()
    branch = document['properties']['definition']['actions']['Apply_to_each_Reviewed_Row']['actions']['Condition_Is_New_Opportunity']
    branch['else']['actions']['Condition_Exactly_One_Opportunity']['expression'] = {'equals': [COUNT, 2]}
    with pytest.raises(ValueError):
        patch_definition(document)


def test_package_preserves_rollback_and_rejects_wrong_hash_or_overwrite(tmp_path, monkeypatch):
    import hashlib
    import json
    import zipfile
    import scripts.patch_grants_solution_deadlines as module
    monkeypatch.setattr(module, 'ROOT', tmp_path)
    private = tmp_path / 'private'
    private.mkdir()
    source, output = private / 'baseline.zip', private / 'candidate.zip'
    workflow = 'Workflows/Grants.json'
    with zipfile.ZipFile(source, 'w') as archive:
        archive.writestr('solution.xml', '<Root><SolutionManifest><Managed>0</Managed><Version>1</Version></SolutionManifest></Root>')
        archive.writestr('customizations.xml', '<Root />')
        archive.writestr('[Content_Types].xml', '<Types />')
        archive.writestr(workflow, json.dumps(fixture()))
    saved = source.read_bytes()
    digest = hashlib.sha256(saved).hexdigest()
    with pytest.raises(ValueError):
        module.patch_package(source, output, workflow, 'wrong')
    assert not output.exists()
    result = module.patch_package(source, output, workflow, digest)
    assert result['changed_workflow_count'] == 1
    assert source.read_bytes() == saved
    with pytest.raises(ValueError):
        module.patch_package(source, output, workflow, digest)
    with pytest.raises(ValueError):
        module.patch_package(source, private / 'other.zip', 'Workflows/Wrong.json', digest)
    assert not (private / 'other.zip').exists()
