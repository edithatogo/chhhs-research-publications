"""Versioned targeted Crossref policy, archive precision and provenance DOI queue.

Pure functions only. No provider, SharePoint, model or checkpoint writes.
"""
from __future__ import annotations
from collections import defaultdict
from functools import lru_cache
from datetime import datetime, timedelta, timezone
import hashlib
import json
import re
from urllib.parse import unquote

DISABLED = frozenset({'tropical', 'cow', 'mission', 'edmonton', 'georgetown',
                      'smithfield', 'croydon', 'liz'})
SOURCES = frozenset({'pubmed', 'dora_publications', 'publication_register',
                     'crossref_verified_discovery'})


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                     ensure_ascii=False).encode()).hexdigest()


@lru_cache(maxsize=100000)
def affiliation_key(value):
    return ' '.join(re.findall(r'[^\W_]+', value.casefold().replace('&', ' and ')))


def normalize_doi(value):
    if not isinstance(value, str):
        return None
    value = re.sub(r'^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)', '', value.strip(), flags=re.I)
    value = unquote(value).strip().lower()
    return value if re.fullmatch(r'10\.\d{4,9}/[^\s\x00-\x1f]+', value) else None


def validate(hedge, collector):
    if hedge.get('schema_version') != 2 or not hedge.get('revision'):
        raise ValueError('Versioned targeted policy required')
    aliases = set(re.findall(r'"([^"\n]+)"\[Affiliation\]', collector['pubmed']['query']))
    queries = hedge['queries']; keys = [q['key'] for q in queries]
    if not keys or len(set(keys)) != len(keys) or DISABLED.intersection(keys):
        raise ValueError('Nonempty unique targeted query keys; broad queries disabled')
    if any(not re.fullmatch('[a-z][a-z0-9-]*', q['key']) or
           not re.fullmatch('[A-Za-z]+', q['anchor']) or q['anchor'].casefold() in DISABLED
           for q in queries):
        raise ValueError('Safe qualified targeted anchors required')
    candidates = {q['key']: q for q in hedge.get('candidate_queries', [])}
    if any(q['key'] in candidates and candidates[q['key']].get('state') != 'qualified' for q in queries):
        raise ValueError('Candidate search has not passed bounded qualification')
    routes = hedge['alias_routes']
    if len(routes) != len({r['alias'] for r in routes}) or {r['alias'] for r in routes} != aliases:
        raise ValueError('Every maintained alias needs exactly one explicit route')
    for row in routes:
        if row['route'] not in {'discovery', 'doi_evidence', 'coverage_gap'} or not row.get('reason'):
            raise ValueError('Explicit route and reason required')
        if row['route'] == 'discovery':
            query = next((q for q in queries if q['key'] == row.get('query_key')), None)
            if not query or row['alias'] not in query['covers_affiliation_aliases']:
                raise ValueError('Discovery route refers to absent query/alias')
        elif row.get('query_key') is not None:
            raise ValueError('DOI/gap route cannot claim an enabled discovery query')
    for q in queries:
        for alias in q['covers_affiliation_aliases']:
            if alias not in aliases or not any(r['alias'] == alias and r['route'] == 'discovery'
                                              and r.get('query_key') == q['key'] for r in routes):
                raise ValueError('Query coverage and route map differ')
    if hedge.get('doi_cache_freshness_days') != 28:
        raise ValueError('Explicit 28-day DOI freshness policy required')
    if (hedge.get('rows_per_page') != 500 or hedge.get('overlap_days') != 7 or
            hedge.get('snapshot_lag_minutes') != 10 or hedge.get('full_reconciliation_days') != 28):
        raise ValueError('Qualified cadence/window defaults required')


def precision(pages, aliases, known_dois=()):
    """pages: (query key, anchor, exact raw bytes, immutable file proof) tuples."""
    normalized = [(a, affiliation_key(a)) for a in aliases]
    known = {normalize_doi(d) for d in known_dois}; known.discard(None)
    groups = {}; all_dois = set(); matched_by_query = defaultdict(set); observations = []
    for key, anchor, raw, proof in pages:
        if len(raw) != proof['bytes'] or hashlib.sha256(raw).hexdigest() != proof['sha256']:
            raise ValueError('Archive byte proof mismatch')
        if not proof.get('id') or not proof.get('etag'):
            raise ValueError('Immutable native identity/ETag required')
        envelope = json.loads(raw); body = envelope['body']
        if envelope['status_code'] != 200 or body.get('message-type') != 'work-list':
            raise ValueError('Successful Crossref work-list archive required')
        from urllib.parse import urlsplit, parse_qs
        request = urlsplit(envelope['request_url'])
        if request.hostname != 'api.crossref.org' or parse_qs(request.query).get('query.affiliation') != [anchor]:
            raise ValueError('Archived query identity differs')
        g = groups.setdefault(key, {'anchor': anchor, 'pages': 0, 'bytes': 0, 'rows': 0,
                                   'dois': set(), 'matched': set(), 'unresolved': set()})
        g['pages'] += 1; g['bytes'] += len(raw)
        for item in body['message']['items']:
            g['rows'] += 1; doi = normalize_doi(item.get('DOI'))
            if not doi:
                raise ValueError('Invalid DOI in archived discovery')
            g['dois'].add(doi); all_dois.add(doi)
            affiliations = [af.get('name', '') for a in item.get('author', [])
                            for af in a.get('affiliation', []) if isinstance(af, dict)]
            texts = [' ' + affiliation_key(text) + ' ' for text in affiliations]
            matched = sorted({a for a, norm in normalized
                              if any((' ' + norm + ' ') in text for text in texts)})
            if matched:
                g['matched'].add(doi); matched_by_query[key].add(doi)
                observations.append({'doi': doi, 'source': 'crossref_verified_discovery',
                    'source_record': key + ':' + doi, 'accepted': True,
                    'institutional_match': 'explicit-affiliation-alias', 'aliases': matched,
                    'evidence': {k: proof[k] for k in ('id', 'etag', 'sha256', 'bytes')},
                    'file': proof['file']})
            else:
                g['unresolved'].add(doi)
    rows = []
    for key, g in groups.items():
        others = set().union(*(v for k, v in matched_by_query.items() if k != key))
        rows.append({'key': key, 'anchor': g['anchor'], 'pages': g['pages'], 'bytes': g['bytes'],
            'records': g['rows'], 'unique_dois': len(g['dois']),
            'duplicate_doi_observations': g['rows'] - len(g['dois']),
            'explicit_alias_match_dois': len(g['matched']),
            'unresolved_dois': len(g['unresolved'] - g['matched']),
            'useful_unique_discovery_dois': len(g['matched'] - others - known),
            'match_fraction': len(g['matched']) / len(g['dois']) if g['dois'] else None})
    return {'queries': rows, 'distinct_dois': len(all_dois),
            'known_doi_comparison_supplied': bool(known), 'observations': observations,
            'caveat': 'Unmatched affiliation is unresolved, not proven irrelevant. Prefix-only analysis is not full-query precision.'}


def doi_queue(records, cache, *, now, freshness_days=28):
    """Retain all accepted provenance; cache entries must be independently byte verified.

    cache entries include raw bytes and native immutable identity. No transitive
    citation expansion or automatic institutional attribution is performed.
    """
    observed = datetime.fromisoformat(now.replace('Z', '+00:00'))
    if observed.tzinfo is None or type(freshness_days) is not int or freshness_days < 1:
        raise ValueError('Timezone-aware cutoff and positive freshness required')
    grouped = defaultdict(list); rejected = []
    for record in records:
        doi = normalize_doi(record.get('doi'))
        if not doi:
            rejected.append(record); continue
        if (record.get('source') not in SOURCES or record.get('accepted') is not True or
                not record.get('source_record') or not record.get('evidence')):
            raise ValueError('Accepted source record and provenance required')
        if record['source'] == 'crossref_verified_discovery' and record.get('institutional_match') != 'explicit-affiliation-alias':
            raise ValueError('Discovery DOI requires explicit institutional evidence')
        if record not in grouped[doi]:
            grouped[doi].append(record)
    entries = []
    for doi, provenance in sorted(grouped.items()):
        valid = []
        for candidate in cache.get(doi, []):
            raw = candidate['raw']; evidence = candidate['evidence']
            if (hashlib.sha256(raw).hexdigest() != evidence['sha256'] or len(raw) != evidence['bytes']
                    or not evidence.get('id') or not evidence.get('etag')):
                raise ValueError('Reusable archive differs from native byte proof')
            envelope = json.loads(raw)
            body = envelope.get('body')
            if envelope.get('status_code') != 200 or not isinstance(body, dict) or not isinstance(body.get('message'), dict):
                continue
            response_doi = normalize_doi(body['message'].get('DOI'))
            canonical = normalize_doi(candidate.get('canonical_doi', doi))
            if normalize_doi(envelope.get('requested_doi')) != doi or response_doi != canonical:
                continue
            at = datetime.fromisoformat(candidate['observed_utc'].replace('Z', '+00:00'))
            if at.tzinfo is None or at > observed:
                raise ValueError('Invalid cache observation time')
            if at >= observed - timedelta(days=freshness_days):
                valid.append(candidate)
        force_refresh = any(r.get('refresh_required') is True for r in provenance)
        reusable = max(valid, key=lambda c: datetime.fromisoformat(c['observed_utc'].replace('Z', '+00:00'))) if valid and not force_refresh else None
        entries.append({'doi': doi, 'provenance': provenance, 'action': 'reuse' if reusable else 'fetch',
                        'archive': {k: v for k, v in reusable.items() if k != 'raw'} if reusable else None})
    return {'format': 'rims-crossref-doi-queue-v1', 'cutoff': now,
            'freshness_days': freshness_days, 'entries': entries, 'invalid_doi_records': rejected,
            'scope_sha256': digest({'records': records, 'freshness_days': freshness_days})}
