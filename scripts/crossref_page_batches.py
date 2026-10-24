"""Install page-boundary admission and unaccepted partial-window continuation.

Transform freshly prepared local batch graphs only. Native parity remains a
separate deployment gate. Cursors retain the exact original request parameters; actual provider rejection
requires evidenced recovery of the unfinished window. No elapsed-time reset.
"""
from __future__ import annotations
import copy


def compose(value, previous=None):
    return {'type': 'Compose', 'inputs': value,
            'runAfter': {previous: ['Succeeded']} if previous else {}}


def setvar(name, value, previous=None):
    c = compose(None, previous); c['type'] = 'SetVariable'
    c['inputs'] = {'name': name, 'value': value}; return c


def install(document, *, max_pages=50, max_archive_bytes=32_000_000, max_minutes=20):
    if type(max_pages) is not int or not 1 <= max_pages <= 100:
        raise ValueError('Conservative positive page budget required')
    a = document['properties']['definition']['actions']
    previous = 'Initialize_paging'
    for name, kind, value in [('BatchPages', 'integer', 0), ('BatchYield', 'boolean', False),
            ('PendingWindow', 'object', "@coalesce(variables('BatchProgress')?['pending_window'],json('{}'))"),
            ('LastPageUTC', 'string', ''),
            ('BatchChangedDOIs', 'array', "@coalesce(variables('BatchProgress')?['changed_dois'],json('[]'))")]:
        key = 'Batch_initialize_' + name
        a[key] = {'type': 'InitializeVariable', 'runAfter': {previous: ['Succeeded']},
                  'inputs': {'variables': [{'name': name, 'type': kind, 'value': value}]}}
        previous = key
    a['Batch_initialize_BatchNewWindows']['runAfter'] = {previous: ['Succeeded']}
    p = a['Progress_load']['actions']
    p['Progress_schema']['inputs']['schema']['properties']['format']['enum'] = ['rims-crossref-progress-v2']
    p['Progress_schema']['inputs']['schema']['required'].extend(['pending_window', 'changed_dois'])
    p['Progress_schema']['inputs']['schema']['properties']['changed_dois'] = {'type': 'array', 'items': {'type': 'string'}}
    p['Progress_schema']['inputs']['schema']['properties']['pending_window'] = {'type': 'object'}
    guard = p['Progress_is_obsolete']['else']['actions']['Progress_guard']
    guard['inputs'] = guard['inputs'].replace('rims-crossref-progress-v1', 'rims-crossref-progress-v2')
    pending = "variables('PendingWindow')"
    expected = "variables('BatchWindowPlan')[length(variables('Queries'))]"
    fields = ('query_window_key', 'key', 'anchor', 'window_filter', 'window_index', 'created_from', 'created_until')
    checks = [f"equals({pending}?['{k}'],{expected}?['{k}'])" for k in fields]
    checks += ["equals(variables('PendingWindow')?['scope_sha256'],outputs('Scope')?['scope_sha256'])",
               "equals(variables('PendingWindow')?['until'],outputs('Generation_cutoff'))",
               "not(empty(variables('PendingWindow')?['cursor']))",
               "greater(variables('PendingWindow')?['attempt'],0)",
               "lessOrEquals(variables('PendingWindow')?['attempt'],20)",
               "equals(length(variables('PendingWindow')?['pages']),variables('PendingWindow')?['page'])",
               "lessOrEquals(variables('PendingWindow')?['received'],variables('PendingWindow')?['expected'])",
               "equals(length(variables('PendingWindow')?['dois']),variables('PendingWindow')?['received'])"]
    # Lazy if keeps plan indexing out of the empty/fully completed branch.
    a['Batch_guard_pending'] = compose("@if(empty(" + pending + "),true,if(less(length(variables('Queries')),length(variables('BatchWindowPlan'))),if(and(" + ','.join(checks) + "),true,json('CROSSREF_PENDING_DRIFT')),json('CROSSREF_PENDING_AFTER_PLAN')))", 'Batch_guard_prefix')
    a['Batch_started']['runAfter'] = {'Batch_guard_pending': ['Succeeded']}
    # Continue writing the unfinished window in its original exclusive folder.
    folder = a['Run_folder']['inputs'][1:]
    a['Run_folder']['inputs'] = "@if(empty(variables('PendingWindow'))," + folder + ",variables('PendingWindow')?['archive_folder'])"
    existing = copy.deepcopy(a['Read_scope']); existing['runAfter'] = {}
    existing['inputs']['parameters']['path'] = "@concat(outputs('Run_folder'),'/scope.json')"
    scope_guard = compose("@if(equals(base64(string(outputs('Scope'))),body('Batch_read_existing_scope')?['$content']),true,json('CROSSREF_PENDING_SCOPE_DRIFT'))", 'Batch_read_existing_scope')
    # Folder root must retain the original qualified archive parent.
    parent = a['Save_completion']['inputs']['parameters']['folderPath']
    a['Batch_guard_folder'] = compose("@if(startsWith(outputs('Run_folder'),'" + parent + "/crossref-discovery-'),true,json('CROSSREF_PENDING_FOLDER_DRIFT'))", 'Run_folder')
    names = ('Create_exclusive_folder', 'Save_scope', 'Read_scope', 'Verify_scope')
    cards = {k: a.pop(k) for k in names}; cards['Create_exclusive_folder']['runAfter'] = {}
    a['Batch_prepare_folder'] = {'type': 'If', 'runAfter': {'Batch_guard_folder': ['Succeeded']},
        'expression': "@empty(variables('PendingWindow'))", 'actions': cards,
        'else': {'actions': {'Batch_read_existing_scope': existing, 'Batch_guard_existing_scope': scope_guard}}}
    for card in a.values():
        if 'Verify_scope' in card.get('runAfter', {}):
            card['runAfter']['Batch_prepare_folder'] = card['runAfter'].pop('Verify_scope')
    q = a['For_each_query']['actions']['Query_may_run']['actions']
    a['For_each_query']['actions']['Query_may_run']['expression'] = a['For_each_query']['actions']['Query_may_run']['expression'].replace('@and(', "@and(not(variables('BatchYield')),", 1)
    usable = "and(not(empty(variables('PendingWindow'))),equals(variables('PendingWindow')?['query_window_key'],items('For_each_query')?['query_window_key']),not(empty(variables('PendingWindow')?['cursor'])))"
    q['Batch_resume_usable'] = compose("@if(empty(variables('PendingWindow')),false," + usable + ')', 'Created_window_filter')
    q['Initialize_query_attempt']['runAfter'] = {'Batch_resume_usable': ['Succeeded']}
    q['Initialize_query_attempt']['inputs']['value'] = "@if(empty(variables('PendingWindow')),0,if(outputs('Batch_resume_usable'),sub(variables('PendingWindow')?['attempt'],1),variables('PendingWindow')?['attempt']))"
    q['Batch_attempt_ceiling'] = compose("@add(variables('QueryAttempt'),2)", 'Initialize_query_drift')
    at = q['Until_query_attempt']; at['runAfter'] = {'Batch_attempt_ceiling': ['Succeeded']}
    at['expression'] = at['expression'].replace('@or(', "@or(variables('BatchYield'),", 1).replace("greaterOrEquals(variables('QueryAttempt'),2)", "greaterOrEquals(variables('QueryAttempt'),outputs('Batch_attempt_ceiling'))")
    attempt = at['actions']
    restore = {'Cursor': 'cursor', 'Page': 'page', 'Received': 'received', 'Expected': 'expected',
               'QueryDOIs': 'dois', 'QueryPages': 'pages', 'AttemptPages': 'attempt_pages'}
    # Only the first attempt may adopt pending state. A total-drift retry resets.
    can_restore = "and(outputs('Batch_resume_usable'),equals(variables('QueryAttempt'),variables('PendingWindow')?['attempt']))"
    for name, field in restore.items():
        card = attempt['Attempt_reset_' + name]; default = card['inputs']['value']
        import json
        fallback = "'" + default + "'" if isinstance(default, str) else ('json(\'[]\')' if default == [] else json.dumps(default))
        card['inputs']['value'] = f"@if({can_restore},variables('PendingWindow')?['{field}'],{fallback})"
    until = attempt['Until_query_complete']; until['expression'] = "@or(variables('Done'),variables('BatchYield'))"
    # Partial attempts have no complete attempt-summary filename yet.
    attempt_tail = ('Query_attempt_summary', 'Save_attempt_summary', 'Read_attempt_summary',
                    'Verify_attempt_summary', 'Append_attempt_summary')
    tail = {k: attempt.pop(k) for k in attempt_tail}
    tail['Query_attempt_summary']['runAfter'] = {}
    attempt['Batch_attempt_finished'] = {'type': 'If',
        'expression': "@or(variables('QueryAccepted'),not(variables('BatchYield')))",
        'runAfter': {'Set_query_accepted': ['Succeeded']}, 'actions': tail, 'else': {'actions': {}}}
    page = until['actions']
    page['Batch_count_pages'] = {'type': 'IncrementVariable', 'runAfter': {'Verify_page': ['Succeeded']}, 'inputs': {'name': 'BatchPages', 'value': 1}}
    page['Batch_count_page_bytes']['runAfter'] = {'Batch_count_pages': ['Succeeded']}
    page['Batch_merge_changed_dois'] = compose("@union(variables('BatchChangedDOIs'),body('Page_DOIs'))", 'Page_DOIs')
    page['Batch_set_changed_dois'] = setvar('BatchChangedDOIs', "@outputs('Batch_merge_changed_dois')", 'Batch_merge_changed_dois')
    page['Merged_DOIs']['runAfter'] = {'Batch_set_changed_dois': ['Succeeded']}
    stable = page['If_total_stable']['actions']
    stable['Batch_last_page_utc'] = setvar('LastPageUTC', '@utcNow()', 'Increment_page')
    stable['Polite_delay']['runAfter'] = {'Batch_last_page_utc': ['Succeeded']}
    stable['Batch_check_admission'] = setvar('BatchYield',
        "@or(greaterOrEquals(variables('BatchPages')," + str(max_pages) + "),greaterOrEquals(variables('BatchArchiveBytes')," + str(max_archive_bytes) + "),greaterOrEquals(ticks(utcNow()),ticks(addMinutes(outputs('Batch_started')," + str(max_minutes) + '))))', 'Polite_delay')
    # Save only metadata references in the progress prefix. Re-read them on resume.
    meta = copy.deepcopy(a['Find_last_complete']); meta['runAfter'] = {'Save_page': ['Succeeded']}
    name = page['Save_page']['inputs']['parameters']['name'][1:]
    meta['inputs']['parameters']['parameters/uri'] = "@concat('_api/web/GetFileByServerRelativePath(decodedurl=''',uriPath('" + meta['inputs']['parameters']['dataset'] + "'),outputs('Run_folder'),'/'," + name + ",''')?$select=UniqueId,ETag,Length')"
    page['Batch_page_metadata'] = meta
    page['Read_page']['runAfter'] = {'Batch_page_metadata': ['Succeeded']}
    for entry in (stable['Page_checkpoint']['inputs']['value'], page['Append_attempt_page']['inputs']['value']):
        entry.update(id="@body('Batch_page_metadata')?['UniqueId']", etag="@body('Batch_page_metadata')?['ETag']", bytes="@int(body('Batch_page_metadata')?['Length'])", archive_folder="@outputs('Run_folder')")
    # Pin immutable partial page metadata before restoring its cursor/counters.
    read_meta = copy.deepcopy(meta); read_meta['runAfter'] = {}
    read_meta['inputs']['parameters']['parameters/uri'] = "@concat('_api/web/GetFileByServerRelativePath(decodedurl=''',uriPath('" + meta['inputs']['parameters']['dataset'] + "'),variables('PendingWindow')?['archive_folder'],'/',items('Batch_verify_pending_pages')?['file'],''')?$select=UniqueId,ETag,Length')"
    a['Batch_verify_pending_pages'] = {'type': 'Foreach', 'foreach': "@coalesce(variables('PendingWindow')?['pages'],json('[]'))", 'runAfter': {'Batch_guard_pending': ['Succeeded']},
        'runtimeConfiguration': {'concurrency': {'repetitions': 1}}, 'actions': {
            'Batch_pending_page_metadata': read_meta,
            'Batch_guard_pending_page_metadata': compose("@if(and(equals(body('Batch_pending_page_metadata')?['UniqueId'],items('Batch_verify_pending_pages')?['id']),equals(body('Batch_pending_page_metadata')?['ETag'],items('Batch_verify_pending_pages')?['etag']),equals(int(body('Batch_pending_page_metadata')?['Length']),items('Batch_verify_pending_pages')?['bytes'])),true,json('CROSSREF_PENDING_PAGE_DRIFT'))", 'Batch_pending_page_metadata')}}
    a['Batch_started']['runAfter'] = {'Batch_verify_pending_pages': ['Succeeded']}
    # A clean page-boundary yield is successful progress, never a complete query.
    finish = ('Guard_query_complete', 'Query_summary', 'Save_query_summary', 'Read_query_summary',
              'Verify_query_summary', 'Append_query', 'Mark_query_failed', 'Batch_increment_windows')
    final = {k: q.pop(k) for k in finish}; final['Guard_query_complete']['runAfter'] = {}
    final['Batch_clear_pending'] = setvar('PendingWindow', {}, 'Batch_increment_windows')
    snapshot = {'query_window_key': "@items('For_each_query')?['query_window_key']",
        **{k: "@items('For_each_query')?['" + k + "']" for k in ('key', 'anchor', 'window_filter', 'window_index', 'created_from', 'created_until')},
        'scope_sha256': "@outputs('Scope')?['scope_sha256']", 'until': "@outputs('Generation_cutoff')",
        'archive_folder': "@outputs('Run_folder')", 'attempt': "@variables('QueryAttempt')",
        'cursor': "@variables('Cursor')", 'page': "@variables('Page')", 'received': "@variables('Received')",
        'expected': "@variables('Expected')", 'dois': "@variables('QueryDOIs')", 'pages': "@variables('QueryPages')",
        'attempt_pages': "@variables('AttemptPages')", 'last_page_utc': "@variables('LastPageUTC')"}
    q['Batch_window_complete'] = {'type': 'If', 'expression': "@variables('QueryAccepted')", 'runAfter': {'Until_query_attempt': ['Succeeded']}, 'actions': final,
        'else': {'actions': {'Batch_guard_clean_yield': compose("@if(and(variables('BatchYield'),not(variables('AcquisitionFailed')),not(variables('QueryTotalDrift')),not(variables('Done'))),true,json('CROSSREF_INCOMPLETE_WINDOW_NOT_YIELD'))"),
                             'Batch_set_pending': setvar('PendingWindow', snapshot, 'Batch_guard_clean_yield')}}}
    a['Batch_progress']['inputs'].update(format='rims-crossref-progress-v2', pending_window="@variables('PendingWindow')", new_pages="@variables('BatchPages')", changed_dois="@variables('BatchChangedDOIs')")
    a['Batch_progress']['inputs']['admission_limits']['pages'] = max_pages
    a['Manifest']['inputs']['batch_progress_format'] = 'rims-crossref-progress-v2'
    return document
