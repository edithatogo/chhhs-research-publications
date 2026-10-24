"""Compare a private native solution export with the portable grants source.

Read-only: never import, activate or publish. Only the exact SharePoint target
bindings and generated trigger operation ID are normalized. Unknown metadata,
authentication, expressions and all other authored content must match.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit
from uuid import UUID
import xml.etree.ElementTree as ET
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / 'config/flows/grants-registry-reviewed-import.definition.json'
PREFIX = 'workflows/chhhsrimsgrantsreviewedimportupsert-'


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def actions(document):
    for name, action in document.items():
        yield name, action
        yield from actions(action.get('actions', {}))
        yield from actions(action.get('else', {}).get('actions', {}))


def portable(definition, site, list_id):
    result = json.loads(json.dumps(definition))
    trigger = result.get('triggers', {}).get('manual', {})
    metadata = trigger.get('metadata')
    if metadata is not None:
        if set(metadata) != {'operationMetadataId'}:
            raise ValueError('Unexpected trigger metadata')
        UUID(metadata['operationMetadataId'])
        del trigger['metadata']

    def replace(value):
        if isinstance(value, dict):
            return {key: replace(item) for key, item in value.items()}
        if isinstance(value, list):
            return [replace(item) for item in value]
        if isinstance(value, str):
            return value.replace(site, '{{SHAREPOINT_SITE_URL}}').replace(list_id, '{{SHAREPOINT_LIST_ID}}')
        return value
    return replace(result)


def reconcile(archive: Path, template: Path = TEMPLATE):
    with ZipFile(archive) as zipped:
        names = zipped.namelist()
        if len(names) != len(set(names)) or any(
                PurePosixPath(name).is_absolute() or '..' in PurePosixPath(name).parts
                or '\\' in name for name in names):
            raise ValueError('Duplicate or unsafe package entry')
        if zipped.testzip() is not None:
            raise ValueError('Package CRC mismatch')
        manifest = ET.fromstring(zipped.read('solution.xml')).find('SolutionManifest')
        if (manifest is None or manifest.findtext('UniqueName') != 'CHHHSRIMSPlatform'
                or manifest.findtext('Managed') != '0'):
            raise ValueError('Wrong solution identity or managed package')
        workflows = sorted(name for name in names if name.startswith('Workflows/') and name.endswith('.json'))
        selected = [name for name in workflows if name.lower().startswith(PREFIX)]
        if len(selected) != 1:
            raise ValueError('Expected exactly one grants workflow')
        exported = json.loads(zipped.read(selected[0]))
        customizations = ET.fromstring(zipped.read('customizations.xml'))
        references = {node.get('connectionreferencelogicalname')
                      for node in customizations.findall('.//connectionreference')}
        reference = exported['properties']['connectionReferences']['shared_sharepointonline']
        if (reference.get('runtimeSource') != 'invoker'
                or reference.get('api', {}).get('name') != 'shared_sharepointonline'
                or reference.get('connection', {}).get('connectionReferenceLogicalName') not in references):
            raise ValueError('Grants invoker connection reference is absent or changed')
        definition = exported['properties']['definition']
        graph = dict(actions(definition['actions']))
        lookup = graph['SharePoint_Get_items']['inputs']['parameters']
        site, list_id = lookup['dataset'], lookup['table']
        parsed = urlsplit(site)
        if (parsed.scheme != 'https' or not (parsed.hostname or '').endswith('.sharepoint.com')
                or parsed.username or parsed.query or parsed.fragment):
            raise ValueError('Unexpected SharePoint binding')
        UUID(list_id)
        for name in ('SharePoint_Create_item', 'SharePoint_Update_item', 'SharePoint_Get_source_identity'):
            parameters = graph[name]['inputs']['parameters']
            if parameters['dataset'] != site or parameters['table'] != list_id:
                raise ValueError('Grants action target differs')
        source = json.loads(template.read_text())['properties']['definition']
        native = portable(definition, site, list_id)
        source = portable(source, site, list_id)
        if native != source:
            raise ValueError('Native grants definition differs from portable source')
        return {
            'schema': 1, 'status': 'PASS_EXPORT_SOURCE_PARITY',
            'solution_unique_name': manifest.findtext('UniqueName'),
            'solution_version': manifest.findtext('Version'), 'managed': False,
            'workflow_count': len(workflows), 'connection_reference_count': len(references),
            'workflow_membership_sha256': digest(workflows),
            'archive_sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
            'portable_grants_definition_sha256': digest(source),
            'normalization': ['exact SharePoint site/list bindings', 'generated manual trigger operationMetadataId'],
            'native_acceptance': False,
            'boundary': 'Export/source comparison only; runtime and isolated-model acceptance have separate receipts.',
        }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = reconcile(args.archive)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(result['status'])


if __name__ == '__main__':
    main()
