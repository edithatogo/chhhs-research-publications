"""Prepare revised targeted independent lanes from the exact historical preimage.

No native save, bootstrap checkpoint, activation, authentication or provider run.
"""
from __future__ import annotations
import argparse
import copy
import json
from pathlib import Path
from scripts.prepare_crossref_discovery_collection import freeze_hedge
from scripts.prepare_crossref_lanes import prepare as lanes
from scripts.crossref_targeted_policy import digest


def prepare(document, hedge, collector, policy, *, expected_definition_sha256,
            discovery_records=(), doi_cache_entries=()):
    # Qualification belongs to the policy, never the old running scope.
    hedge = copy.deepcopy(hedge)
    hedge['created_date_partition'] = {'strategy': 'full-reconciliation-only-inclusive-created-date-windows-v1',
        'query_keys': [], 'months_per_window': 1,
        'first_unbounded_until': '2002-12-31',
        'incremental_runs': 'bounded index-date overlap unchanged'}
    for q in hedge['queries']:
        q.pop('created_date_window_months', None)
    frozen = freeze_hedge(hedge, collector, policy)
    result = lanes(document, expected_definition_sha256=expected_definition_sha256,
                   baseline_monthly_keys=(), frozen_scope=frozen,
                   page_level=True, discovery_records=discovery_records, doi_cache_entries=doi_cache_entries)
    from scripts.crossref_scope_bootstrap import install
    from scripts.crossref_prefix_reuse import install as reuse_prefix
    install(result['incremental'])
    reuse_prefix(result['incremental'], '')
    reuse_prefix(result['baseline_worker'], 'B_')
    for component in result.values():
        component['properties']['description'] = ('Targeted institutional discovery + accepted-source DOI reuse. '
            'Local candidate: exact native readback, revised-scope bootstrap and runtime qualification pending.')
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input', type=Path, required=True)
    p.add_argument('--expected-definition-sha256', required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--discovery-records', type=Path)
    p.add_argument('--doi-cache', type=Path)
    args = p.parse_args()
    policy = json.loads(Path('config/source-acquisition-scopes.json').read_text())
    policy = {'source': 'crossref', 'scope_revision': policy['revision'],
              'scope': next(s for s in policy['sources'] if s['source'] == 'crossref')}
    records = json.loads(args.discovery_records.read_text())['observations'] if args.discovery_records else []
    cache = json.loads(args.doi_cache.read_text())['entries'] if args.doi_cache else []
    result = prepare(json.loads(args.input.read_text()), json.loads(Path('config/crossref-acquisition-hedge.json').read_text()),
        json.loads(Path('config/collector.json').read_text()), policy,
        expected_definition_sha256=args.expected_definition_sha256, discovery_records=records, doi_cache_entries=cache)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': 'LOCAL_TARGETED_CANDIDATES_NATIVE_PENDING',
        'sha256': digest(result)}))


if __name__ == '__main__':
    main()
