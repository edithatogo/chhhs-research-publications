"""Prepare native DOI reuse from immutable entries in accepted checkpoints.

Historical entries lacking native metadata remain cache misses. Never invent
freshness or reuse an unverified provider response. No native effects here.
"""
from __future__ import annotations
import copy
from scripts.crossref_page_batches import compose, setvar


def install(document, *, discovery_records=(), cache_entries=()):
    from scripts.crossref_targeted_policy import normalize_doi
    a = document['properties']['definition']['actions']
    # Before lane namespacing/finalization so both components get the same logic.
    discovered = {normalize_doi(r['doi']) for r in discovery_records}
    if None in discovered:
        raise ValueError('Invalid accepted discovery DOI')
    for r in discovery_records:
        if r.get('accepted') is not True or r.get('institutional_match') != 'explicit-affiliation-alias' or not r.get('evidence'):
            raise ValueError('Verified explicit discovery provenance required')
    a['Accepted_discovery_dois'] = compose(sorted(discovered))
    a['Accepted_discovery_dois']['runAfter'] = copy.deepcopy(a['All_DOIs']['runAfter'])
    a['All_DOIs']['inputs'] = "@union(" + a['All_DOIs']['inputs'][1:] + ",outputs('Accepted_discovery_dois'))"
    for entry in cache_entries:
        if (entry.get('saved_readback_equal') is not True or not entry.get('id')
                or not entry.get('etag') or not entry.get('sha256')
                or not entry.get('observed_utc') or not entry.get('archive_folder')):
            raise ValueError('Independently verified accepted DOI cache entry required')
    cache_index = {e['doi']: e for e in cache_entries}
    if len(cache_index) != len(cache_entries):
        raise ValueError('Duplicate bootstrap DOI cache identity')
    a['Bootstrap_doi_cache_index'] = compose(cache_index, 'Accepted_discovery_dois')
    a['Doi_checkpoint_cache_keys'] = {'type': 'Select', 'runAfter': {'Bootstrap_doi_cache_index': ['Succeeded']},
        'inputs': {'from': "@coalesce(variables('Checkpoint')?['doi_lookups'],json('[]'))", 'select': "@item()?['doi']"}}
    a['Doi_checkpoint_cache_unique'] = compose("@if(equals(length(body('Doi_checkpoint_cache_keys')),length(union(body('Doi_checkpoint_cache_keys'),body('Doi_checkpoint_cache_keys')))),true,json('CROSSREF_DUPLICATE_CHECKPOINT_DOI'))", 'Doi_checkpoint_cache_keys')
    pair = "string(addProperty(json('{}'),item()?['doi'],item()))"
    a['Doi_checkpoint_cache_pairs'] = {'type': 'Select', 'runAfter': {'Doi_checkpoint_cache_unique': ['Succeeded']},
        'inputs': {'from': "@coalesce(variables('Checkpoint')?['doi_lookups'],json('[]'))",
                   'select': "@substring(" + pair + ",1,sub(length(" + pair + "),2))"}}
    a['Doi_checkpoint_cache_index'] = compose("@json(concat('{',join(body('Doi_checkpoint_cache_pairs'),','),'}'))", 'Doi_checkpoint_cache_pairs')
    a['All_DOIs']['runAfter'] = {'Doi_checkpoint_cache_index': ['Succeeded']}
    a['Manifest']['inputs']['accepted_discovery_provenance'] = list(discovery_records)
    a['Manifest']['inputs']['doi_cache_policy'] = {'freshness_days': 28,
        'reuse_requires': 'accepted entry; native ID/ETag/length before and after read; exact requested/canonical DOI',
        'historical_missing_metadata': 'fetch; no fabricated cache authority'}
    d = a['For_each_doi']['actions']['Doi_may_run']['actions']
    new_meta = copy.deepcopy(a['Find_last_complete']); new_meta['runAfter'] = {'Save_doi': ['Succeeded']}
    site = new_meta['inputs']['parameters']['dataset']
    filename = d['Save_doi']['inputs']['parameters']['name'][1:]
    new_meta['inputs']['parameters']['parameters/uri'] = "@concat('_api/web/GetFileByServerRelativePath(decodedurl=''',uriPath('" + site + "'),outputs('Run_folder'),'/'," + filename + ",''')?$select=UniqueId,ETag,Length')"
    d['Doi_archive_metadata'] = new_meta
    d['Read_doi']['runAfter'] = {'Doi_archive_metadata': ['Succeeded']}
    d['Append_doi_entry']['inputs']['value'].update(archive_folder="@outputs('Run_folder')",
        id="@body('Doi_archive_metadata')?['UniqueId']", etag="@body('Doi_archive_metadata')?['ETag']",
        bytes="@int(body('Doi_archive_metadata')?['Length'])", observed_utc='@utcNow()')
    cached = "outputs('Doi_cache_entry')"
    uri = "@concat('_api/web/GetFileByServerRelativePath(decodedurl=''',uriPath('" + site + "')," + cached + "?['archive_folder'],'/'," + cached + "?['file'],''')?$select=UniqueId,ETag,Length')"
    meta = copy.deepcopy(new_meta); meta['runAfter'] = {}; meta['inputs']['parameters']['parameters/uri'] = uri
    read = copy.deepcopy(d['Read_doi']); read['runAfter'] = {'Doi_cache_guard_before': ['Succeeded']}
    read['inputs']['parameters']['path'] = "@concat(" + cached + "?['archive_folder'],'/'," + cached + "?['file'])"
    parent = a['Save_completion']['inputs']['parameters']['folderPath']
    guard_path = compose("@if(and(startsWith(" + cached + "?['archive_folder'],'" + parent + "/crossref-discovery-'),startsWith(" + cached + "?['file'],'doi-'),endsWith(" + cached + "?['file'],'.json'),not(contains(" + cached + "?['file'],'/')),not(contains(" + cached + "?['file'],decodeUriComponent('%27')))),true,json('CROSSREF_CACHE_PATH_DRIFT'))")
    meta['runAfter'] = {'Doi_cache_guard_path': ['Succeeded']}
    def guard(action, previous):
        checks = [f"equals(body('{action}')?['{native}'],{cached}?['{key}'])" for native, key in [('UniqueId', 'id'), ('ETag', 'etag')]]
        checks.append(f"equals(int(body('{action}')?['Length']),{cached}?['bytes'])")
        return compose("@if(and(" + ','.join(checks) + "),true,json('CROSSREF_CACHE_METADATA_DRIFT'))", previous)
    after = copy.deepcopy(meta); after['runAfter'] = {'Doi_cache_guard_content': ['Succeeded']}
    content = "json(base64ToString(body('Doi_cache_read')?['$content']))"
    reused = {'Doi_cache_guard_path': guard_path, 'Doi_cache_metadata_before': meta,
        'Doi_cache_guard_before': guard('Doi_cache_metadata_before', 'Doi_cache_metadata_before'),
        'Doi_cache_read': read,
        'Doi_cache_guard_content': compose("@if(and(equals(" + content + "?['requested_doi'],items('For_each_doi')),equals(" + content + "?['status_code'],200),equals(toLower(" + content + "?['body']?['message']?['DOI'])," + cached + "?['canonical_doi'])),true,json('CROSSREF_CACHE_DOI_DRIFT'))", 'Doi_cache_read'),
        'Doi_cache_metadata_after': after,
        'Doi_cache_guard_after': guard('Doi_cache_metadata_after', 'Doi_cache_metadata_after'),
        'Doi_cache_append': {'type': 'AppendToArrayVariable', 'runAfter': {'Doi_cache_guard_after': ['Succeeded']},
            'inputs': {'name': 'DoiEntries', 'value': '@' + cached}},
        'Doi_cache_increment_index': {'type': 'IncrementVariable', 'runAfter': {'Doi_cache_append': ['Succeeded']},
            'inputs': {'name': 'DoiIndex', 'value': 1}}}
    checkpoint_entry = "outputs('Doi_checkpoint_cache_index')?[items('For_each_doi')]"
    bootstrap_entry = "outputs('Bootstrap_doi_cache_index')?[items('For_each_doi')]"
    def fresh(entry):
        return ("and(equals(" + entry + "?['doi'],items('For_each_doi')),equals(" + entry + "?['http_status'],200),"
            "equals(" + entry + "?['saved_readback_equal'],true),not(empty(" + entry + "?['id'])),"
            "not(empty(" + entry + "?['etag'])),not(empty(" + entry + "?['archive_folder'])),"
            "greaterOrEquals(ticks(coalesce(" + entry + "?['observed_utc'],'1900-01-01T00:00:00Z')),ticks(addDays(utcNow(),-28))),"
            "lessOrEquals(ticks(coalesce(" + entry + "?['observed_utc'],'1900-01-01T00:00:00Z')),ticks(utcNow())))")
    a['For_each_doi']['actions']['Doi_may_run']['actions'] = {
        'Doi_cache_entry': compose('@if(' + fresh(checkpoint_entry) + ',' + checkpoint_entry + ',' + bootstrap_entry + ')'),
        'Doi_cache_or_fetch': {'type': 'If', 'runAfter': {'Doi_cache_entry': ['Succeeded']},
            'expression': "@and(not(and(not(outputs('Full_reconciliation')),contains(variables('BatchChangedDOIs'),items('For_each_doi'))))," + fresh(cached) + ')',
            'actions': reused, 'else': {'actions': d}},
        'Doi_cache_mark_failed': {'type': 'SetVariable', 'runAfter': {'Doi_cache_or_fetch': ['Failed', 'TimedOut', 'Skipped']},
            'inputs': {'name': 'AcquisitionFailed', 'value': True}}}
    return document
