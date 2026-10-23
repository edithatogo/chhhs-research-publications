"""Add source-row provenance to the existing guarded grants solution offline."""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

if __package__:
    from scripts.patch_grants_solution_deadlines import COUNT, patch_package
else:
    from patch_grants_solution_deadlines import COUNT, patch_package


def patch_definition(document):
    result = copy.deepcopy(document)
    actions = result['properties']['definition']['actions']
    loop = actions['Apply_to_each_Reviewed_Row']
    if loop.get('runtimeConfiguration', {}).get('concurrency', {}).get('repetitions') != 1:
        raise ValueError('Serial guarded loop required')
    valid = loop['actions']['Condition_OpportunityKey_Present']['actions']
    lookup = valid['SharePoint_Get_items']['inputs']['parameters']
    if lookup.get('$top') != 2 or 'OpportunityKey eq' not in lookup.get('$filter', ''):
        raise ValueError('Unexpected identity lookup')
    branch = valid['Condition_Conflicting_Source_Identity']['else']['actions']['Condition_Is_New_Opportunity']
    exact = branch['else']['actions']['Condition_Exactly_One_Opportunity']
    if branch['expression'] != {'equals': [COUNT, 0]} or exact['expression'] != {'equals': [COUNT, 1]}:
        raise ValueError('Unexpected create/update guards')
    targets = (branch['actions']['SharePoint_Create_item'], exact['actions']['SharePoint_Update_item'])
    for action, operation in zip(targets, ('PostItem', 'PatchItem')):
        if action['inputs']['host'].get('operationId') != operation:
            raise ValueError('Unexpected SharePoint operation')
        params = action['inputs']['parameters']
        if params.get('item/URL') != "@{item()?['URL']}":
            raise ValueError('Existing opportunity URL mapping drifted')
        value = "@{item()?['SourceRowURL']}"
        if 'item/SourceRowURL' in params and params['item/SourceRowURL'] != value:
            raise ValueError('Existing source-row URL mapping drifted')
        params['item/SourceRowURL'] = value
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--workflow', required=True)
    parser.add_argument('--expected-sha256', required=True)
    args = parser.parse_args()
    print(json.dumps(patch_package(args.source, args.output, args.workflow,
        args.expected_sha256, patcher=patch_definition), indent=2))


if __name__ == '__main__':
    main()
