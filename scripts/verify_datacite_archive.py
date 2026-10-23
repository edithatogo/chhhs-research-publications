"""Reconcile downloaded native DataCite pages without fetching or changing data."""
import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
import re
from urllib.parse import parse_qs, urlsplit


def verify(folder, completion, expected_scope, prior=None, *, archive_root=None, page_hashes=None):
    folder = Path(folder)
    archive_root = Path(archive_root) if archive_root is not None else folder

    def page_archive(page_folder):
        """Resolve a local or native SharePoint archive pointer under its root."""
        if not isinstance(page_folder, str) or not page_folder:
            raise ValueError('Unsafe DataCite page archive pointer')
        native_prefix = '/Documents/'
        if page_folder.startswith(native_prefix):
            # The current manifest's folder is the root passed to verify(); prior
            # run archives are retained below archive_root using the complete
            # path relative to the Documents library.
            if page_folder == manifest.get('archive_folder'):
                return folder.resolve()
            relative = page_folder[len(native_prefix):]
        else:
            relative = page_folder
        parts = relative.split('/')
        if (any(part in {'', '.', '..'} for part in parts)
                or any(not re.fullmatch(r'[A-Za-z0-9 _-]+', part) for part in parts)
                or not re.fullmatch(r'datacite-discovery-[A-Za-z0-9_-]+', parts[-1])):
            raise ValueError('Unsafe DataCite page archive pointer')
        resolved = (archive_root.joinpath(*parts)).resolve()
        root = archive_root.resolve()
        if resolved != root and root not in resolved.parents:
            raise ValueError('DataCite page archive pointer escaped its archive root')
        return resolved

    def read(name):
        if not re.fullmatch(r'[A-Za-z0-9_-]+\.json', name):
            raise ValueError('Unsafe archive filename')
        return json.loads((folder / name).read_text())

    manifest = read('manifest.json')
    if (manifest != completion or manifest.get('complete') is not True
            or manifest.get('source') != 'datacite'
            or manifest.get('scope_sha256') != expected_scope['scope_sha256']
            or read('scope.json') != expected_scope):
        raise ValueError('Native completion, manifest and frozen scope must agree')
    inputs = read('publication-doi-source.json')
    dois = inputs['publication_dois']
    if (len(dois) != len(set(dois)) or inputs['source_count'] != len(inputs['rows'])
            or manifest['publication_dois'] != dois):
        raise ValueError('Publication input snapshot differs from manifest')
    full = manifest.get('full_reconciliation')
    if full not in (True, False) or not isinstance(full, bool):
        raise ValueError('Explicit full-reconciliation flag required')
    if not full:
        if (not prior or prior.get('complete') is not True
                or prior.get('source') != 'datacite'
                or prior.get('scope_sha256') != manifest['scope_sha256']
                or not prior.get('baseline_completed_at')
                or prior.get('baseline_completed_at') != manifest.get('baseline_completed_at')
                or not set(prior['publication_dois']).issubset(dois)):
            raise ValueError('Accepted prior scope, baseline and retained publication DOI population required')
        previous_until = datetime.fromisoformat(prior['until'].replace('Z', '+00:00'))
        until = datetime.fromisoformat(manifest['until'].replace('Z', '+00:00'))
        if previous_until.utcoffset() is None or until.utcoffset() is None or until <= previous_until:
            raise ValueError('Update cutoff must advance the accepted prior cutoff')
        overlap = (previous_until.astimezone(timezone.utc) - timedelta(days=7)).strftime('%Y-%m-%dT%H:%M:%SZ')
    expected = {q['key']: q for q in expected_scope['institutional_queries']}
    for i in range(0, len(dois), 20):
        expected['related-' + str(i // 20)] = {'kind': 'related', 'dois': dois[i:i + 20]}
    queries = manifest['queries']
    if len(queries) != len(expected) or {q['key'] for q in queries} != set(expected):
        raise ValueError('All institutional and related queries must be present exactly once')
    total_rows, union = 0, set()
    for query in queries:
        key = query['key']
        if query['complete'] is not True or query['kind'] != expected[key]['kind']:
            raise ValueError('Incomplete query or changed query purpose')
        query_folder = query.get('archive_folder', manifest.get('archive_folder'))
        if query_folder is None:
            raise ValueError('DataCite query archive pointer required')
        query_path = page_archive(query_folder) / (key + '-complete.json')
        if query != json.loads(query_path.read_text()):
            raise ValueError('Saved query receipt differs from final manifest')
        if query['kind'] == 'institutional':
            base_query = expected[key]['query']
        else:
            quoted = ['"' + d.replace('\\', '\\\\').replace('"', '\\"') + '"'
                      for d in expected[key]['dois']]
            base_query = 'relatedIdentifiers.relatedIdentifier:(' + ' OR '.join(quoted) + ')'
        window = 'created:[* TO "' + manifest['until'] + '"]'
        if not full and query['kind'] == 'institutional':
            window = 'updated:["' + overlap + '" TO "' + manifest['until'] + '"]'
        wanted = '(' + base_query + ') AND ' + window
        if query['query'] != wanted:
            raise ValueError('Query scope or acquisition window differs from selected operation')
        ids, rows, cursor = [], 0, '1'
        pages = query['pages']
        if not pages:
            raise ValueError('Even an empty result requires a retained response')
        for index, receipt in enumerate(pages):
            expected_file = key + '-page-' + str(index) + '.json'
            if receipt.get('file') != expected_file:
                raise ValueError('Missing or reordered query page')
            page_path = page_archive(query_folder) / expected_file
            raw_page = page_path.read_bytes()
            page = json.loads(raw_page)
            if receipt.get('saved_content_equal') is not True:
                raise ValueError('Native exact-byte page readback required')
            if page_hashes is not None:
                expected_hash = page_hashes.get(query_folder + '/' + expected_file)
                if (not isinstance(expected_hash, str)
                        or not re.fullmatch(r'[0-9a-f]{64}', expected_hash)
                        or expected_hash != hashlib.sha256(raw_page).hexdigest()):
                    raise ValueError('Independent exact-byte page hash differs')
            elif query_folder != manifest.get('archive_folder'):
                raise ValueError('Cross-run page reuse requires independent byte-hash evidence')
            params, body = page['parameters'], page['body']
            if (page['http_status'] != 200 or params['query'] != query['query']
                    or params['page[cursor]'] != cursor
                    or any(params.get(k) != 'true' for k in ('detail', 'affiliation', 'publisher'))
                    or body['meta']['total'] != query['provider_total']
                    or receipt['rows'] != len(body['data'])):
                raise ValueError('Saved response request, metadata flags or count differs')
            for record in body['data']:
                doi = record['id'].lower()
                if doi != record['attributes']['doi'].lower() or not record['attributes'].get('xml'):
                    raise ValueError('Complete XML metadata and matching DOI required')
                ids.append(doi)
            rows += len(body['data'])
            link = body.get('links', {}).get('next')
            if index == len(pages) - 1:
                if link:
                    raise ValueError('Terminal saved page still has a continuation')
            else:
                u = urlsplit(link or '')
                values = parse_qs(u.query).get('page[cursor]', [])
                if u.scheme != 'https' or u.hostname != 'api.datacite.org' or u.path != '/dois' or len(values) != 1:
                    raise ValueError('Canonical provider continuation required')
                cursor = values[0]
        if not (rows == len(set(ids)) == query['received'] == query['unique_dois'] == query['provider_total']):
            raise ValueError('Provider, saved row and unique DOI counts differ')
        total_rows += rows
        union.update(ids)
    return {'status': 'PASS_COMPLETE_NATIVE_DATACITE_ARCHIVE', 'queries': len(queries),
            'reconciliation_kind': 'full_baseline' if full else 'overlap_update',
            'publication_dois': len(dois), 'raw_rows_including_query_overlap': total_rows,
            'unique_datacite_dois': len(union),
            'manifest_sha256': hashlib.sha256((folder / 'manifest.json').read_bytes()).hexdigest(),
            'regular_updates_inferred': False}
