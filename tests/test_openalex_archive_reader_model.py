import base64
import hashlib
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from build_openalex_archive_reader_model import build, EXPRESSIONS, CHUNKS, WORKS
from prepare_openalex_archive_stage import build as stage
from prepare_openalex_retention import build as retain
import test_openalex_retention as fixture_module


class ArchiveReaderModel(unittest.TestCase):
    def setUp(self):
        fixture = fixture_module.OpenAlexRetention()
        fixture.setUp()
        self.prepared = retain(fixture.frozen, fixture.candidate)
        self.files, receipt = stage(self.prepared, json.loads(fixture.frozen), 'fixture-openalex')
        self.manifest = json.dumps({'SchemaVersion': 1, 'Status': 'committed', 'BatchID': 'fixture-openalex',
            'Validation': {'Keysets': True, 'Metadata': True, 'RefreshGeneration': True},
            'Preservation': {'UnchangedSources': ['PubMed', 'DORA'], 'ChangedSources': ['OpenAlex']},
            'Sources': [receipt['source_spec']], 'Files': receipt['files']}).encode()
        texts = {EXPRESSIONS: 'expression RetainedArchiveFiles = fixture\n'
                 'expression fnReadCommittedHistory =\n(Files as table, SourceName as text) as table => fixture\n',
                 CHUNKS: 'column preserved\nsource = Table.FromRecords(OpenAlexBootstrapDocument[chunks])',
                 WORKS: 'column preserved\nsource = fnProjectRetainedOpenAlexAligned(OpenAlexBootstrapObservations,pOpenAlexAlignedFieldLimits)'}
        texts.update({f'definition/fixture-{i}.tmdl': 'preserved fixture' for i in range(43)})
        self.baseline = json.dumps({'definition': {'format': 'TMDL', 'parts': [
            {'path': name, 'payload': base64.b64encode(text.encode()).decode(), 'payloadType': 'InlineBase64'}
            for name, text in texts.items()]}}).encode()
        self.sha = hashlib.sha256(self.baseline).hexdigest()

    def test_only_two_partition_sources_and_append_only_expressions_change(self):
        candidate, receipt, expressions = build(self.baseline, self.manifest, self.prepared, self.files,
                                                expected_baseline_sha256=self.sha)
        original = {p['path']: p for p in json.loads(self.baseline)['definition']['parts']}
        changed = []
        for part in candidate['definition']['parts']:
            if part != original[part['path']]:
                changed.append(part['path'])
        self.assertEqual(set(changed), {EXPRESSIONS, CHUNKS, WORKS})
        appended = base64.b64decode(next(p['payload'] for p in candidate['definition']['parts'] if p['path'] == EXPRESSIONS))
        self.assertTrue(appended.startswith(base64.b64decode(original[EXPRESSIONS]['payload'])))
        self.assertIn('fnReadCommittedHistory(RetainedArchiveFiles,"OpenAlex")', expressions['OpenAlexCommittedObservations'])
        self.assertIn('R[MetadataJSON]', expressions['OpenAlexCommittedMetadataChunks'])
        self.assertNotIn('Json.FromValue', expressions['OpenAlexCommittedMetadataChunks'])
        self.assertFalse(receipt['native_archive_accepted'])

    def test_drifted_baseline_or_incomplete_archive_cannot_switch_consumer(self):
        with self.assertRaises(ValueError):
            build(self.baseline + b' ', self.manifest, self.prepared, self.files, expected_baseline_sha256=self.sha)
        damaged = dict(self.files)
        damaged.pop(next(iter(damaged)))
        with self.assertRaises(ValueError):
            build(self.baseline, self.manifest, self.prepared, damaged, expected_baseline_sha256=self.sha)


if __name__ == '__main__':
    unittest.main()
