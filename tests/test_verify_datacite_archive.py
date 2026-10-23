import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from scripts.verify_datacite_archive import verify


class DataCiteArchiveTests(unittest.TestCase):
    def fixture(self, folder):
        scope = {'scope_sha256': 'fixture', 'institutional_queries': [
            {'key': 'institutional-0', 'kind': 'institutional', 'query': 'creators.affiliation.name:"Example"'}]}
        cutoff = '2026-10-18T00:00:00Z'
        query = '(creators.affiliation.name:"Example") AND created:[* TO "' + cutoff + '"]'
        page_receipts = []
        summary = {'key': 'institutional-0', 'kind': 'institutional', 'query': query,
                   'complete': True, 'provider_total': 2, 'received': 2, 'unique_dois': 2,
                   'scope_sha256': 'fixture', 'archive_folder': 'run/datacite-discovery-run',
                   'pages': page_receipts}
        manifest = {'source': 'datacite', 'complete': True, 'scope_sha256': 'fixture',
                    'full_reconciliation': True, 'until': cutoff, 'baseline_completed_at': cutoff,
                    'publication_dois': [], 'queries': [summary],
                    'archive_folder': 'run/datacite-discovery-run'}
        files = {'manifest.json': manifest, 'scope.json': scope,
                 'publication-doi-source.json': {'publication_dois': [], 'source_count': 0, 'rows': []}}
        for i in range(2):
            doi = '10.5555/example' + str(i)
            files['institutional-0-page-' + str(i) + '.json'] = {
                'http_status': 200, 'parameters': {'query': query, 'page[cursor]': '1' if i == 0 else 'next',
                    'detail': 'true', 'affiliation': 'true', 'publisher': 'true'},
                'body': {'meta': {'total': 2}, 'data': [{'id': doi, 'attributes': {'doi': doi, 'xml': '<resource/>'}}],
                    'links': {'next': 'https://api.datacite.org/dois?page%5Bcursor%5D=next' if i == 0 else None}}}
            raw = json.dumps(files['institutional-0-page-' + str(i) + '.json']).encode()
            page_receipts.append({'file': 'institutional-0-page-' + str(i) + '.json', 'rows': 1,
                'saved_content_equal': True, 'sha256': hashlib.sha256(raw).hexdigest(),
                'archive_folder': summary['archive_folder']})
        files['institutional-0-complete.json'] = copy.deepcopy(summary)
        for name, value in files.items():
            (folder / name).write_text(json.dumps(value))
        return manifest, scope, files

    def write_archive(self, root, manifest, scope, files, folder='run/datacite-discovery-run'):
        archive = root / folder
        archive.mkdir(parents=True, exist_ok=True)
        for name, value in files.items():
            (archive / name).write_text(json.dumps(value))
        return archive

    def test_complete_cursor_chain_and_full_metadata_reconcile(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            manifest, scope, _ = self.fixture(folder)
            files = {name: json.loads((folder / name).read_text()) for name in
                     ('manifest.json', 'scope.json', 'publication-doi-source.json',
                      'institutional-0-complete.json', 'institutional-0-page-0.json',
                      'institutional-0-page-1.json')}
            self.write_archive(folder, manifest, scope, files)
            result = verify(folder, manifest, scope)
            self.assertEqual(result['unique_datacite_dois'], 2)
            self.assertFalse(result['regular_updates_inferred'])

    def test_query_pages_can_resolve_to_prior_run_with_exact_hashes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest, scope, files = self.fixture(root)
            old = root / 'run-old/datacite-discovery-old'
            old.mkdir(parents=True)
            current = root / 'run-new/datacite-discovery-new'
            current.mkdir(parents=True)
            manifest['archive_folder'] = 'run-new/datacite-discovery-new'
            manifest['queries'][0]['archive_folder'] = 'run-old/datacite-discovery-old'
            for receipt in manifest['queries'][0]['pages']:
                receipt['archive_folder'] = 'run-old/datacite-discovery-old'
            prior_files = {name: value for name, value in files.items()
                           if name.startswith('institutional-0-')}
            for name, value in prior_files.items():
                (old / name).write_text(json.dumps(value))
            (old / 'institutional-0-complete.json').write_text(
                json.dumps(manifest['queries'][0]))
            (current / 'manifest.json').write_text(json.dumps(manifest))
            (current / 'scope.json').write_text(json.dumps(scope))
            (current / 'publication-doi-source.json').write_text(
                json.dumps(files['publication-doi-source.json']))
            hashes = {manifest['queries'][0]['archive_folder'] + '/' + name:
                hashlib.sha256((old / name).read_bytes()).hexdigest()
                for name in ('institutional-0-page-0.json', 'institutional-0-page-1.json')}
            result = verify(current, manifest, scope, archive_root=root, page_hashes=hashes)
            self.assertEqual(result['unique_datacite_dois'], 2)
            manifest['queries'][0]['archive_folder'] = '../escape'
            with self.assertRaises(ValueError):
                verify(current, manifest, scope, archive_root=root)

    def test_native_sharepoint_archive_paths_resolve_under_library_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            current = root / 'current-local'
            current.mkdir()
            manifest, scope, files = self.fixture(current)
            library_prefix = '/Documents/CHHHS Research System - DEV/01 Source archive/'
            current_pointer = library_prefix + 'datacite-discovery-current'
            prior_pointer = library_prefix + 'datacite-discovery-prior'
            manifest['archive_folder'] = current_pointer
            summary = manifest['queries'][0]
            summary['archive_folder'] = prior_pointer
            for receipt in summary['pages']:
                receipt['archive_folder'] = prior_pointer
            prior = root / 'CHHHS Research System - DEV' / '01 Source archive' / 'datacite-discovery-prior'
            prior.mkdir(parents=True)
            for name, value in files.items():
                if name.startswith('institutional-0-page-'):
                    (prior / name).write_text(json.dumps(value))
            (prior / 'institutional-0-complete.json').write_text(json.dumps(summary))
            # Current-generation manifest inputs remain at the selected local
            # folder; only complete query/page evidence points to the prior run.
            (current / 'manifest.json').write_text(json.dumps(manifest))
            (current / 'scope.json').write_text(json.dumps(scope))
            (current / 'publication-doi-source.json').write_text(
                json.dumps(files['publication-doi-source.json']))
            hashes = {prior_pointer + '/' + name:
                hashlib.sha256((prior / name).read_bytes()).hexdigest()
                for name in ('institutional-0-page-0.json', 'institutional-0-page-1.json')}
            result = verify(current, manifest, scope, archive_root=root, page_hashes=hashes)
            self.assertEqual(result['unique_datacite_dois'], 2)

    def test_duplicate_page_records_and_lost_xml_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            manifest, scope, files = self.fixture(folder)
            self.write_archive(folder, manifest, scope, files)
            name = 'institutional-0-page-1.json'
            changed = copy.deepcopy(files[name])
            changed['body']['data'] = files['institutional-0-page-0.json']['body']['data']
            (folder / name).write_text(json.dumps(changed))
            with self.assertRaises(ValueError):
                self.write_archive(folder, manifest, scope, {**files, name: changed})
                verify(folder, manifest, scope)
            changed = copy.deepcopy(files[name])
            changed['body']['data'][0]['attributes'].pop('xml')
            (folder / name).write_text(json.dumps(changed))
            with self.assertRaises(ValueError):
                self.write_archive(folder, manifest, scope, {**files, name: changed})
                verify(folder, manifest, scope)

    def test_completion_cannot_omit_a_selected_query(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            manifest, scope, _ = self.fixture(folder)
            manifest['queries'] = []
            (folder / 'manifest.json').write_text(json.dumps(manifest))
            with self.assertRaises(ValueError):
                verify(folder, manifest, scope)

    def test_update_preserves_prior_dois_and_related_queries_remain_full(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            manifest, scope, files = self.fixture(folder)
            prior = copy.deepcopy(manifest)
            manifest['full_reconciliation'] = False
            manifest['until'] = '2026-10-18T01:00:00Z'
            institution = '(creators.affiliation.name:"Example") AND updated:["2026-10-11T00:00:00Z" TO "2026-10-18T01:00:00Z"]'
            manifest['queries'][0]['query'] = institution
            for name in ('institutional-0-page-0.json', 'institutional-0-page-1.json'):
                files[name]['parameters']['query'] = institution
                raw = json.dumps(files[name]).encode()
                receipt_index = 0 if name.endswith('-0.json') else 1
                manifest['queries'][0]['pages'][receipt_index]['sha256'] = hashlib.sha256(raw).hexdigest()
            manifest['publication_dois'] = ['10.5555/publication']
            files['publication-doi-source.json']['publication_dois'] = manifest['publication_dois']
            related = '(relatedIdentifiers.relatedIdentifier:("10.5555/publication")) AND created:[* TO "2026-10-18T01:00:00Z"]'
            summary = {'key': 'related-0', 'kind': 'related', 'query': related,
                'complete': True, 'provider_total': 0, 'received': 0, 'unique_dois': 0,
                'scope_sha256': 'fixture', 'archive_folder': 'run/datacite-discovery-run', 'pages': []}
            related_page = {'http_status': 200,
                'parameters': {'query': related, 'page[cursor]': '1', 'detail': 'true', 'affiliation': 'true', 'publisher': 'true'},
                'body': {'meta': {'total': 0}, 'data': [], 'links': {'next': None}}}
            related_raw = json.dumps(related_page).encode()
            summary['pages'] = [{'file': 'related-0-page-0.json', 'rows': 0, 'saved_content_equal': True,
                'sha256': hashlib.sha256(related_raw).hexdigest(), 'archive_folder': summary['archive_folder']}]
            manifest['queries'].append(summary)
            files['related-0-complete.json'] = summary
            files['related-0-page-0.json'] = related_page
            for name, value in files.items():
                (folder / name).write_text(json.dumps(value))
            files['institutional-0-complete.json'] = copy.deepcopy(manifest['queries'][0])
            files['related-0-complete.json'] = copy.deepcopy(summary)
            self.write_archive(folder, manifest, scope, files)
            with self.assertRaises(ValueError):
                verify(folder, manifest, scope)
            self.assertEqual(verify(folder, manifest, scope, prior)['reconciliation_kind'], 'overlap_update')
            prior['publication_dois'] = ['10.5555/lost']
            with self.assertRaises(ValueError):
                verify(folder, manifest, scope, prior)
            prior['publication_dois'] = []
            summary['query'] = related.replace('created:[* TO', 'updated:[* TO')
            files['related-0-page-0.json']['parameters']['query'] = summary['query']
            for name, value in files.items():
                (folder / name).write_text(json.dumps(value))
            with self.assertRaises(ValueError):
                verify(folder, manifest, scope, prior)
