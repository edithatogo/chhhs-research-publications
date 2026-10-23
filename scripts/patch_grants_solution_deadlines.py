"""Prepare six deadline mappings in one existing consolidated-solution workflow.

Offline only: preserve rollback, require its exact SHA-256 and never import.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import zipfile

if __package__:
    from scripts.compare_solution_release import compare_release
else:
    from compare_solution_release import compare_release

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ('DeadlineTimezone', 'DeadlineLocalTime', 'DeadlineUTCInstant',
          'DeadlineBrisbaneDate', 'DeadlineBrisbaneTime', 'DeadlineTemporalStatus')
COUNT = "@length(body('SharePoint_Get_items')?['value'])"


def patch_definition(document):
    result = copy.deepcopy(document)
    actions = result['properties']['definition']['actions']['Apply_to_each_Reviewed_Row']['actions']
    lookup = actions['SharePoint_Get_items']['inputs']['parameters']
    if lookup.get('$top') != 2 or 'OpportunityKey eq' not in lookup.get('$filter', ''):
        raise ValueError('Unexpected identity lookup')
    branch = actions['Condition_Is_New_Opportunity']
    exact = branch['else']['actions']['Condition_Exactly_One_Opportunity']
    if branch['expression'] != {'equals': [COUNT, 0]} or exact['expression'] != {'equals': [COUNT, 1]}:
        raise ValueError('Unexpected create/update identity guards')
    targets = (branch['actions']['SharePoint_Create_item'], exact['actions']['SharePoint_Update_item'])
    for action, operation in zip(targets, ('PostItem', 'PatchItem')):
        if action['inputs']['host'].get('operationId') != operation:
            raise ValueError('Unexpected SharePoint operation')
        params = action['inputs']['parameters']
        for field in FIELDS:
            key = f'item/{field}'
            value = "@{item()?['" + field + "']}"
            if field == 'DeadlineTemporalStatus':
                value = {'Value': value}
            if key in params and params[key] != value:
                raise ValueError('Existing deadline mapping has drifted')
            params[key] = value
    return result


def patch_package(source: Path, output: Path, workflow: str, expected_sha256: str, *, patcher=None):
    private = (ROOT / 'private').resolve()
    if not source.resolve().is_relative_to(private) or not output.resolve().is_relative_to(private):
        raise ValueError('Packages must remain under private/')
    if source.resolve() == output.resolve() or output.exists():
        raise ValueError('Preserve baseline and existing output')
    if hashlib.sha256(source.read_bytes()).hexdigest() != expected_sha256:
        raise ValueError('Baseline fingerprint mismatch')
    # Validate the baseline format and exact selected entry before constructing output.
    compare_release(source, source, [workflow])
    with zipfile.ZipFile(source) as archive:
        entries = [(info, archive.read(info.filename)) for info in archive.infolist()]
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=output.parent) as folder:
        candidate = Path(folder) / 'candidate.zip'
        with zipfile.ZipFile(candidate, 'w') as archive:
            for info, data in entries:
                if info.filename == workflow:
                    data = json.dumps((patcher or patch_definition)(json.loads(data)), ensure_ascii=False, indent=2).encode()
                archive.writestr(info, data)
        receipt = compare_release(source, candidate, [workflow])
        # Exclusive creation prevents accidental replacement of another agent's output.
        with output.open('xb') as destination:
            destination.write(candidate.read_bytes())
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--workflow', required=True)
    parser.add_argument('--expected-sha256', required=True)
    args = parser.parse_args()
    print(json.dumps(patch_package(args.source, args.output, args.workflow, args.expected_sha256), indent=2))


if __name__ == '__main__':
    main()
