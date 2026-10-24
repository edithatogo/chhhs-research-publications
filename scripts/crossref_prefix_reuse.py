"""Permit qualified original-scope donor pages via new saved summary overlays.

Every completed page's native immutable metadata is checked before reuse. The
new summary overlay must match the entire progress entry byte for byte. Raw
originals and original summary files are never rewritten.
"""
from __future__ import annotations
import copy
from scripts.prepare_crossref_lanes import _cards


def install(component, prefix):
    root = component['properties']['definition']['actions']
    by_name = dict(_cards(root))
    cache_path = by_name[prefix + 'Doi_cache_guard_path']
    cache_path['inputs'] = cache_path['inputs'].replace('/crossref-discovery-' + ('baseline-' if prefix else 'incremental-'), '/crossref-discovery-')
    obsolete = by_name[prefix + 'Progress_is_obsolete']
    lane = 'baseline' if prefix else 'incremental'
    obsolete['expression'] = "@and(equals(variables('" + prefix + "BatchProgress')?['until'],variables('" + prefix + "Checkpoint')?['until']),equals(variables('" + prefix + "BatchProgress')?['scope_sha256'],variables('" + prefix + "Checkpoint')?['scope_sha256']),equals(variables('" + prefix + "Checkpoint')?['collection_lane'],'" + lane + "'))"
    verify = by_name[prefix + 'Batch_verify_prefix']
    cards = verify['actions']; index = "items('" + prefix + "Batch_verify_prefix')"
    query = "variables('" + prefix + "Queries')[" + index + ']'
    read = cards[prefix + 'Batch_read_summary']
    read['inputs']['parameters']['path'] = "@concat(coalesce(" + query + "?['summary_folder']," + query + "?['archive_folder']), '/'," + query + "?['query_window_key'],'-complete.json')"
    window_guard = cards[prefix + 'Batch_guard_window']
    # Cross-lane reuse is explicitly read-only. The new overlay/Scope still
    # belongs to the destination lane; old raw IDs/ETags are pinned below.
    window_guard['inputs'] = window_guard['inputs'].replace('/crossref-discovery-' + ('baseline-' if prefix else 'incremental-'), '/crossref-discovery-')
    scope_folder = by_name[prefix + 'Save_completion']['inputs']['parameters']['folderPath']
    summary_path_guard = "startsWith(coalesce(" + query + "?['summary_folder']," + query + "?['archive_folder']),'" + scope_folder + "/crossref-discovery-')"
    window_guard['inputs'] = window_guard['inputs'].replace('@if(and(', '@if(and(' + summary_path_guard + ',', 1)
    metadata = copy.deepcopy(by_name[prefix + 'Find_last_complete']); metadata['runAfter'] = {prefix + 'Reuse_guard_path': ['Succeeded']}
    page = "items('" + prefix + "Batch_verify_completed_pages')"
    folder = "coalesce(" + page + "?['archive_folder']," + query + "?['archive_folder'])"
    site = metadata['inputs']['parameters']['dataset']
    metadata['inputs']['parameters']['parameters/uri'] = "@concat('_api/web/GetFileByServerRelativePath(decodedurl=''',uriPath('" + site + "')," + folder + ",'/'," + page + "?['file'],''')?$select=UniqueId,ETag,Length')"
    guard_path = {'type': 'Compose', 'runAfter': {}, 'inputs': "@if(and(startsWith(" + folder + ",'" + scope_folder + "/crossref-discovery-'),not(contains(" + page + "?['file'],'/')),not(contains(" + page + "?['file'],decodeUriComponent('%27'))),endsWith(" + page + "?['file'],'.json')),true,json('CROSSREF_REUSE_PAGE_PATH_DRIFT'))"}
    output = "body('" + prefix + "Reuse_page_metadata')"
    guard = {'type': 'Compose', 'runAfter': {prefix + 'Reuse_page_metadata': ['Succeeded']},
        'inputs': "@if(and(equals(" + output + "?['UniqueId']," + page + "?['id']),equals(" + output + "?['ETag']," + page + "?['etag']),equals(int(" + output + "?['Length'])," + page + "?['bytes'])),true,json('CROSSREF_REUSE_PAGE_VERSION_DRIFT'))"}
    cards[prefix + 'Batch_verify_completed_pages'] = {'type': 'Foreach',
        'runAfter': {prefix + 'Batch_guard_summary': ['Succeeded']}, 'foreach': '@' + query + "?['pages']",
        'runtimeConfiguration': {'concurrency': {'repetitions': 1}},
        'actions': {prefix + 'Reuse_guard_path': guard_path,
                    prefix + 'Reuse_page_metadata': metadata, prefix + 'Reuse_guard_metadata': guard}}
    return component
