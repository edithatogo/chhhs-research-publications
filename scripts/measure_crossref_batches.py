"""Measure existing Crossref evidence; no network, provider calls or native effects."""
from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path


def _time(value):
    return datetime.fromisoformat(value.replace('Z', '+00:00'))


def measure(directory):
    directory = Path(directory)
    files = []

    def load(name):
        path = directory / name
        files.append({'file': name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
        return json.loads(path.read_text())

    receipt = load('crossref-recovery-staged-inputs.json')
    rows, page_bytes = defaultdict(int), defaultdict(int)
    for path in sorted(directory.glob('crossref-recovery-page-batch-*.json')):
        for page in load(path.name)['proofs']:
            if page['frozen_request_contract_equal'] is not True:
                raise ValueError('Verified saved page evidence required')
            page_bytes[page['query_window_key']] += page['bytes']
            rows[page['query_window_key']] += page['rows']
    windows = receipt['queries']
    if set(page_bytes) != {q['query_window_key'] for q in windows}:
        raise ValueError('Complete prefix and page evidence differ')
    for q in windows:
        if q['complete'] is not True or q['received'] != rows[q['query_window_key']]:
            raise ValueError('Window totals differ from independently read pages')
    # Native repetition identities retain the original query ordinal. Use the
    # actual frozen scope, never infer order from alphabetical window names.
    native = load('crossref-stall-current-service.json')
    keys = [q['key'] for q in native['properties']['definition']['actions']['Scope']['inputs']['hedge']['queries']]
    starts, ends, active_seconds = {}, {}, defaultdict(float)
    for action in ('Get_page', 'Verify_query_summary'):
        evidence = load('crossref-stall-' + action + '-repetitions.json')
        for item in evidence['value']:
            parts = item['name'].split('-')
            if len(parts) < 2:
                raise ValueError('Qualified partition repetition identity required')
            key = keys[int(parts[0])] + '-window-' + str(int(parts[1]))
            if key not in page_bytes:
                continue
            props = item['properties']
            if props.get('status') != 'Succeeded':
                continue
            start, end = _time(props['startTime']), _time(props['endTime'])
            if action == 'Get_page':
                starts[key] = min(starts.get(key, start), start)
                active_seconds[key] += (end - start).total_seconds()
            else:
                ends[key] = max(ends.get(key, end), end)
    samples = []
    for q in windows:
        key = q['query_window_key']
        samples.append({'window': key, 'archive_bytes': page_bytes[key],
            'rows': rows[key], 'provider_http_seconds': active_seconds[key],
            'elapsed_seconds': (ends[key] - starts[key]).total_seconds()
                if key in starts and key in ends else None})
    simulations = []
    for byte_cap in (16_000_000, 24_000_000, 32_000_000):
        for window_cap in (50, 100):
            batches = []; count = volume = 0; elapsed = 0.0
            for sample in samples:
                if count >= window_cap or volume >= byte_cap or elapsed >= 1200:
                    batches.append({'windows': count, 'bytes': volume, 'elapsed_seconds': elapsed})
                    count = volume = 0; elapsed = 0.0
                count += 1; volume += sample['archive_bytes']
                elapsed += sample['elapsed_seconds'] or 0
            if count:
                batches.append({'windows': count, 'bytes': volume, 'elapsed_seconds': elapsed})
            simulations.append({'byte_cap': byte_cap, 'window_cap': window_cap,
                'elapsed_admission_seconds': 1200, 'observed_prefix_batches': len(batches),
                'largest_batch_bytes': max(b['bytes'] for b in batches),
                'caveat': 'Historical old-graph wall times including pauses; no prediction for new monthly Cairns partitions or low-copy graph'})
    sizes = sorted(page_bytes.values())
    history = load('crossref-content-throughput-evidence.json')
    progress = load('crossref-latest-progress-diagnosis.json')
    return {'status': 'MEASURED_HISTORICAL_PREFIX_NEW_GRAPH_RUNTIME_PENDING',
        'measured_at': datetime.now(timezone.utc).isoformat(),
        'source_run': receipt['source_run'], 'observed_windows': len(samples),
        'archive_bytes': sum(sizes), 'rows': sum(rows.values()),
        'window_bytes': {'p50': sizes[len(sizes) // 2], 'p95': sizes[int(len(sizes) * .95)],
            'max': max(sizes)}, 'largest_windows': sorted(samples, key=lambda x: x['archive_bytes'], reverse=True)[:5],
        'provider_http_seconds': sum(active_seconds.values()),
        'observed_window_elapsed_seconds': sum(s['elapsed_seconds'] or 0 for s in samples),
        'observed_history_bytes_five_page_actions': history['sum_observed_bytes'],
        'historical_checkpoint_lag_hours_at_observation': (
            _time(progress['observed_at']) - _time(receipt['until'])).total_seconds() / 3600,
        'lag_observation_utc': progress['observed_at'],
        'lag_caveat': 'Age of unfinished generation cutoff; not measured daily delta catch-up delay',
        'simulation': simulations, 'window_samples': samples, 'inputs': files,
        'limitations': ['Only 210 completed windows/247 saved pages independently read; 313-window total is incomplete',
            'No measured runtime of new low-copy, batch or separate-lane candidates',
            'No measured daily incremental byte/action budget or verified catch-up SLA',
            'Historical wall-time pauses are not provider processing time; shared usage is not isolated',
            'Cairns monthly split preserves bounds but actual monthly sizes remain unmeasured'],
        'native_effects': 0, 'provider_requests': 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence-directory', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = measure(args.evidence_directory)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ('status', 'observed_windows', 'archive_bytes',
                                          'window_bytes', 'provider_http_seconds')}))


if __name__ == '__main__':
    main()
