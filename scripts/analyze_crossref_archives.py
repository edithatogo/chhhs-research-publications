"""Analyse pinned local Crossref archives and prepare a provenance DOI queue.

Read-only inputs; outputs are local evidence, never accepted checkpoints.
"""
from __future__ import annotations
import argparse
import json
import hashlib
import re
from pathlib import Path
from scripts.crossref_targeted_policy import precision, doi_queue, normalize_doi


def analyze(directory, hedge, accepted_checkpoint, *, now, cache=None):
    directory = Path(directory)
    inputs = json.loads((directory / 'archive-inputs.json').read_text())
    original = Path(accepted_checkpoint).read_bytes(); checkpoint = json.loads(original)
    if checkpoint.get('complete') is not True or checkpoint.get('source') != 'crossref':
        raise ValueError('Accepted Crossref checkpoint with source provenance required')
    evidence = {'checkpoint_sha256': hashlib.sha256(original).hexdigest(),
                'checkpoint_file': Path(accepted_checkpoint).name,
                'source_run': checkpoint['capture_run']}
    records = []
    for source, capture in checkpoint['raw_publication_producer_inputs'].items():
        if source not in {'pubmed', 'dora_publications'} or capture['checkpoint']['complete'] is not True:
            raise ValueError('Accepted complete publication producer required')
        c = capture['checkpoint']
        for i, raw in enumerate(c['publication_doi_values']):
            records.append({'doi': raw, 'source': source, 'source_record': capture['checkpoint_file'] + ':doi:' + str(i),
                'accepted': True, 'evidence': {**evidence, 'producer_checkpoint': capture['checkpoint_file'],
                                            'producer_scope_sha256': c['scope_sha256']}})
    inventory = json.loads((directory.parent / '2026-10-23-e01-current-state' /
        'crossref-recovery-extension-251-inventory.json').read_text())
    metadata = {row['name']: row for row in inventory['files']}
    def pages():
        for f in inputs['files']:
            native = metadata[f['file']]
            if native['bytes'] != f['proof']['bytes']:
                raise ValueError('Inventory and page proof differ')
            for key in ('id', 'etag'):
                if f['proof'].get(key) and f['proof'][key] != native[key]:
                    raise ValueError('Native identity drift')
            yield f['key'], f['anchor'], (directory / 'raw' / f['file']).read_bytes(), {
                **f['proof'], 'file': f['file'], 'id': native['id'], 'etag': native['etag']}
    report = precision(pages(), [r['alias'] for r in hedge['alias_routes']],
                       [r['doi'] for r in records])
    report.update(source_run=inputs['source_run'], frozen_until=inputs['until'],
        verified_prefix_only=True, windows=251, provider_recollection=0,
        known_source_checkpoint_sha256=evidence['checkpoint_sha256'])
    queue = doi_queue(records + report['observations'], cache or {}, now=now)
    return report, queue


def load_cache(directory, receipt):
    if receipt.get('status') != 'INDEPENDENT_ACCEPTED_DOI_ARCHIVE_BYTES_VERIFIED':
        raise ValueError('Accepted immutable DOI archive receipt required')
    result = {}
    for e in receipt['entries']:
        if not re.fullmatch(r'doi-\d+\.json', e['file']):
            raise ValueError('Unsafe raw cache filename')
        result.setdefault(e['doi'], []).append({
            'raw': (Path(directory) / 'doi-raw' / e['file']).read_bytes(),
            'observed_utc': e['observed_utc'], 'canonical_doi': e['canonical_doi'],
            'file': e['file'], 'archive_folder': e['archive_folder'],
            'evidence': {k: e[k] for k in ('sha256', 'bytes', 'id', 'etag')}})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, required=True)
    parser.add_argument('--hedge', type=Path, default=Path('config/crossref-acquisition-hedge.json'))
    parser.add_argument('--accepted-checkpoint', type=Path, required=True)
    parser.add_argument('--now', required=True)
    parser.add_argument('--doi-cache', type=Path)
    args = parser.parse_args()
    cache = load_cache(args.directory, json.loads(args.doi_cache.read_text())) if args.doi_cache else {}
    report, queue = analyze(args.directory, json.loads(args.hedge.read_text()), args.accepted_checkpoint, now=args.now, cache=cache)
    for name, value in [('precision.json', report), ('doi-queue.json', queue)]:
        (args.directory / name).write_text(json.dumps(value, indent=2) + '\n')
    print(json.dumps({'queries': report['queries'], 'doi_queue': len(queue['entries']),
                      'invalid_doi_values': len(queue['invalid_doi_records'])}))


if __name__ == '__main__':
    main()
