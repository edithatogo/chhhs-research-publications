"""Prepare same-ID Crossref acquisition with complete pages and durable cutoffs.

Local preparation only. The Microsoft flow retains raw responses before any
affiliation selection; source discovery, DOI lookup and downstream use differ.
"""
import copy
import hashlib
import json
import re
from urllib.parse import urlsplit


def freeze_hedge(hedge, collector, scope):
    if hedge.get('schema_version') != 1 or not hedge.get('revision'):
        raise ValueError('Versioned Crossref hedge required')
    aliases = set(re.findall(r'"([^"\n]+)"\[Affiliation\]', collector['pubmed']['query']))
    covered = set()
    keys = []
    for q in hedge['queries']:
        keys.append(q['key'])
        if not re.fullmatch('[a-z][a-z0-9-]*', q['key']) or not re.fullmatch('[A-Za-z]+', q['anchor']):
            raise ValueError('Safe distinctive single-token query required')
        for alias in q['covers_affiliation_aliases']:
            if q['anchor'].lower() not in alias.lower().split():
                raise ValueError('Query anchor must cover its affiliation alias')
            covered.add(alias)
    if covered != aliases or len(keys) != len(set(keys)):
        raise ValueError('All maintained affiliation aliases need unique query coverage')
    if (hedge.get('rows_per_page') != 500 or hedge.get('overlap_days', 0) < 1
            or hedge.get('full_reconciliation_days', 0) < 1):
        raise ValueError('Bounded page size, overlap and reconciliation required')
    payload = {'policy': scope, 'hedge': hedge}
    payload['scope_sha256'] = hashlib.sha256(json.dumps(payload, sort_keys=True,
        separators=(',', ':')).encode()).hexdigest()
    return payload


def build(document, frozen, doi_target=None):
    result = copy.deepcopy(document)
    p = result['properties']
    if (p.get('state') != 'Stopped' or 'Crossref' not in p.get('displayName', '')
            or frozen['policy'].get('source') != 'crossref'):
        raise ValueError('Stopped Crossref preimage and frozen scope required')
    old = p['definition']['actions']
    site = old['Create_exclusive_folder']['inputs']['parameters']['dataset']
    parent = old['Run_folder']['inputs'].split("@concat('", 1)[1].split('/crossref-source-', 1)[0]
    if not parent.startswith('/Documents/'):
        raise ValueError('Existing accepted archive parent required')
    personal = urlsplit(site).path.rstrip('/')
    host = copy.deepcopy(old['Create_exclusive_folder']['inputs']['host'])
    refs = copy.deepcopy(p['connectionReferences'])
    seeds = list(dict.fromkeys(r['id'].strip().lower() for r in old['Requested_ids']['inputs']))
    hedge = frozen['hedge']

    def compose(value, previous=None):
        return {'type': 'Compose', 'inputs': value,
                'runAfter': {previous: ['Succeeded']} if previous else {}}

    def gate(condition, previous=None):
        return compose('@if(' + condition + ",true,json('CROSSREF_ACQUISITION_REJECTED'))", previous)

    def sp(op, params, previous=None):
        h = copy.deepcopy(host); h['operationId'] = op
        return {'type': 'OpenApiConnection', 'runAfter': {previous: ['Succeeded']} if previous else {},
                'inputs': {'host': h, 'parameters': {'dataset': site, **params},
                           'retryPolicy': {'type': 'none'}}}

    def http(uri, previous=None):
        return {'type': 'Http', 'runAfter': {previous: ['Succeeded']} if previous else {},
                'inputs': {'method': 'GET', 'uri': uri,
                           'headers': {'Accept': 'application/json', 'User-Agent': 'RIMS-source-retention/1.0'},
                           'retryPolicy': {'type': 'exponential', 'count': 3, 'interval': 'PT10S'}}}

    def variable(kind, name, value, previous):
        return {'type': kind, 'runAfter': {previous: ['Succeeded']} if previous else {},
                'inputs': {'name': name, 'value': value}}

    def save_read_verify(actions, key, filename, content, previous, folder="outputs('Run_folder')"):
        folder_value = folder[1:-1] if folder.startswith("'") and folder.endswith("'") else '@' + folder
        actions['Save_' + key] = sp('CreateFile', {'folderPath': folder_value,
            'name': filename, 'body': content}, previous)
        name_expr = filename[1:] if filename.startswith('@') else "'" + filename + "'"
        actions['Read_' + key] = sp('GetFileContentByPath', {
            'path': '@concat(' + folder + ",'/'," + name_expr + ')', 'inferContentType': False}, 'Save_' + key)
        expression = content[1:] if content.startswith('@') else "'" + content + "'"
        actions['Verify_' + key] = gate('equals(base64(' + expression + "),body('Read_" + key + "')?['$content'])", 'Read_' + key)
        return 'Verify_' + key

    a = {'Scope': compose(frozen)}
    a['Cutoff'] = compose("@formatDateTime(addMinutes(utcNow(),-" + str(hedge['snapshot_lag_minutes']) + "),'yyyy-MM-ddTHH:mm:ssZ')", 'Scope')
    a['Find_last_complete'] = sp('HttpRequest', {'parameters/method': 'GET',
        'parameters/uri': "_api/web/GetFolderByServerRelativeUrl('" + personal + parent + "')/Files?$filter=startswith(Name,'crossref-complete-')&$orderby=TimeCreated desc&$top=1&$select=Name,ServerRelativeUrl",
        'parameters/headers': {'Accept': 'application/json;odata=nometadata'}}, 'Cutoff')
    a['Last_marker_name'] = compose("@if(empty(body('Find_last_complete')?['value']),'',first(body('Find_last_complete')?['value'])?['Name'])", 'Find_last_complete')
    a['Initialize_checkpoint'] = {'type': 'InitializeVariable', 'runAfter': {'Last_marker_name': ['Succeeded']},
        'inputs': {'variables': [{'name': 'Checkpoint', 'type': 'object', 'value': {}}]}}
    checkpoint_read = sp('GetFileContentByPath', {'path': "@concat('" + parent + "/',outputs('Last_marker_name'))", 'inferContentType': False})
    a['Has_checkpoint'] = {'type': 'If', 'expression': "@not(empty(outputs('Last_marker_name')))",
        'runAfter': {'Initialize_checkpoint': ['Succeeded']}, 'actions': {
            'Read_checkpoint': checkpoint_read,
            'Parse_checkpoint': variable('SetVariable', 'Checkpoint', "@json(base64ToString(body('Read_checkpoint')?['$content']))", 'Read_checkpoint'),
            'Guard_checkpoint': gate("and(equals(variables('Checkpoint')?['source'],'crossref'),equals(variables('Checkpoint')?['complete'],true),lessOrEquals(ticks(variables('Checkpoint')?['until']),ticks(outputs('Cutoff'))))", 'Parse_checkpoint')},
        'else': {'actions': {}}}
    a['Full_reconciliation'] = compose("@or(empty(variables('Checkpoint')),not(equals(variables('Checkpoint')?['scope_sha256'],outputs('Scope')?['scope_sha256'])),lessOrEquals(ticks(coalesce(variables('Checkpoint')?['baseline_completed_at'],'1900-01-01T00:00:00Z')),ticks(addDays(utcNow(),-" + str(hedge['full_reconciliation_days']) + '))))', 'Has_checkpoint')
    # Index dates move on reindexing, which can remove records mid-baseline.
    # Crossref recommends immutable created-date windows for a stable baseline;
    # the initial cutoff remains the update high-water mark for later catch-up.
    a['Window_filter'] = compose("@if(outputs('Full_reconciliation'),concat('until-created-date:',formatDateTime(outputs('Cutoff'),'yyyy-MM-ddTHH:mm:ss')),concat('from-index-date:',formatDateTime(addDays(variables('Checkpoint')?['until'],-" + str(hedge['overlap_days']) + "),'yyyy-MM-ddTHH:mm:ss'),',until-index-date:',formatDateTime(outputs('Cutoff'),'yyyy-MM-ddTHH:mm:ss')))", 'Full_reconciliation')
    a['Initialize_paging'] = {'type': 'InitializeVariable', 'runAfter': {'Window_filter': ['Succeeded']},
        'inputs': {'variables': [{'name': 'Cursor', 'type': 'string', 'value': '*'},
            {'name': 'Page', 'type': 'integer', 'value': 0}, {'name': 'Received', 'type': 'integer', 'value': 0},
            {'name': 'Expected', 'type': 'integer', 'value': 0}, {'name': 'Done', 'type': 'boolean', 'value': False},
            {'name': 'QueryDOIs', 'type': 'array', 'value': []}, {'name': 'QueryPages', 'type': 'array', 'value': []},
            {'name': 'Queries', 'type': 'array', 'value': []},
            {'name': 'AcquisitionFailed', 'type': 'boolean', 'value': False},
            {'name': 'DoiIndex', 'type': 'integer', 'value': 0},
            {'name': 'DoiEntries', 'type': 'array', 'value': []}]}}
    a['Run_folder'] = compose("@concat('" + parent + "/crossref-discovery-',workflow()?['run']?['name'])", 'Initialize_paging')
    a['Create_exclusive_folder'] = sp('HttpRequest', {'parameters/method': 'POST', 'parameters/uri': '_api/web/folders',
        'parameters/headers': {'Accept': 'application/json;odata=nometadata', 'Content-Type': 'application/json;odata=nometadata'},
        'parameters/body': {'ServerRelativeUrl': "@concat('" + personal + "',outputs('Run_folder'))"}}, 'Run_folder')
    last = save_read_verify(a, 'scope', 'scope.json', "@string(outputs('Scope'))", 'Create_exclusive_folder')
    q = {}
    previous = None
    for name, value in [('Cursor', '*'), ('Page', 0), ('Received', 0), ('Expected', 0), ('Done', False), ('QueryDOIs', []), ('QueryPages', [])]:
        key = 'Reset_' + name; q[key] = variable('SetVariable', name, value, previous); previous = key
    page = {'Request_uri': compose("@concat('https://api.crossref.org/works?query.affiliation=',uriComponent(items('For_each_query')?['anchor']),'&rows=500&cursor=',uriComponent(variables('Cursor')),'&filter=',uriComponent(outputs('Window_filter')))")}
    page['Get_page'] = http("@outputs('Request_uri')", 'Request_uri')
    page['Guard_page'] = gate("and(equals(outputs('Get_page')?['statusCode'],200),equals(body('Get_page')?['status'],'ok'),equals(body('Get_page')?['message-type'],'work-list'),greaterOrEquals(body('Get_page')?['message']?['total-results'],0),lessOrEquals(length(body('Get_page')?['message']?['items']),500))", 'Get_page')
    page['Raw_page'] = compose({'request_url': "@outputs('Request_uri')", 'status_code': "@outputs('Get_page')?['statusCode']",
        'headers': "@outputs('Get_page')?['headers']", 'body': "@body('Get_page')"}, 'Guard_page')
    page_name = "@concat(items('For_each_query')?['key'],'-page-',string(variables('Page')),'.json')"
    last_page = save_read_verify(page, 'page', page_name, "@string(outputs('Raw_page'))", 'Raw_page')
    page['Page_DOIs'] = {'type': 'Select', 'runAfter': {last_page: ['Succeeded']},
        'inputs': {'from': "@body('Get_page')?['message']?['items']", 'select': "@toLower(item()?['DOI'])"}}
    page['Merged_DOIs'] = compose("@union(variables('QueryDOIs'),body('Page_DOIs'))", 'Page_DOIs')
    page['Update_DOIs'] = variable('SetVariable', 'QueryDOIs', "@outputs('Merged_DOIs')", 'Merged_DOIs')
    page['Expected_value'] = compose("@if(equals(variables('Page'),0),body('Get_page')?['message']?['total-results'],variables('Expected'))", 'Update_DOIs')
    page['Set_expected'] = variable('SetVariable', 'Expected', "@outputs('Expected_value')", 'Expected_value')
    page['Guard_total_stable'] = gate("equals(variables('Expected'),body('Get_page')?['message']?['total-results'])", 'Set_expected')
    page['Add_received'] = variable('IncrementVariable', 'Received', "@length(body('Get_page')?['message']?['items'])", 'Guard_total_stable')
    page['Page_checkpoint'] = variable('AppendToArrayVariable', 'QueryPages', {'file': page_name,
        'rows': "@length(body('Get_page')?['message']?['items'])", 'saved_readback_equal': True}, 'Add_received')
    page['Set_done'] = variable('SetVariable', 'Done', "@less(length(body('Get_page')?['message']?['items']),500)", 'Page_checkpoint')
    page['Next_cursor'] = variable('SetVariable', 'Cursor', "@coalesce(body('Get_page')?['message']?['next-cursor'],'')", 'Set_done')
    page['Guard_cursor'] = gate("or(variables('Done'),not(empty(variables('Cursor'))))", 'Next_cursor')
    page['Increment_page'] = variable('IncrementVariable', 'Page', 1, 'Guard_cursor')
    page['Polite_delay'] = {'type': 'Wait', 'runAfter': {'Increment_page': ['Succeeded']}, 'inputs': {'interval': {'count': 5, 'unit': 'Second'}}}
    page['Mark_page_failed'] = variable('SetVariable', 'AcquisitionFailed', True, None)
    page['Mark_page_failed']['runAfter'] = {'Polite_delay': ['Failed', 'TimedOut', 'Skipped']}
    page['Stop_failed_paging'] = variable('SetVariable', 'Done', True, 'Mark_page_failed')
    q['Until_query_complete'] = {'type': 'Until', 'expression': "@equals(variables('Done'),true)",
        'limit': {'count': 5000, 'timeout': 'P1D'}, 'runAfter': {previous: ['Succeeded']}, 'actions': page}
    q['Guard_query_complete'] = gate("and(not(variables('AcquisitionFailed')),variables('Done'),equals(variables('Received'),variables('Expected')),equals(length(variables('QueryDOIs')),variables('Expected')))", 'Until_query_complete')
    q['Query_summary'] = compose({'key': "@items('For_each_query')?['key']", 'anchor': "@items('For_each_query')?['anchor']",
        'expected': "@variables('Expected')", 'received': "@variables('Received')", 'unique_dois': "@length(variables('QueryDOIs'))",
        'pages': "@variables('QueryPages')", 'complete': True}, 'Guard_query_complete')
    last_query = save_read_verify(q, 'query_summary', "@concat(items('For_each_query')?['key'],'-complete.json')", "@string(outputs('Query_summary'))", 'Query_summary')
    q['Append_query'] = variable('AppendToArrayVariable', 'Queries', "@outputs('Query_summary')", last_query)
    q['Mark_query_failed'] = variable('SetVariable', 'AcquisitionFailed', True, None)
    q['Mark_query_failed']['runAfter'] = {'Append_query': ['Failed', 'TimedOut', 'Skipped']}
    a['For_each_query'] = {'type': 'Foreach', 'foreach': "@outputs('Scope')?['hedge']?['queries']",
        'runAfter': {last: ['Succeeded']}, 'runtimeConfiguration': {'concurrency': {'repetitions': 1}},
        'actions': {'Query_may_run': {'type': 'If', 'expression': "@not(variables('AcquisitionFailed'))",
            'runAfter': {}, 'actions': q, 'else': {'actions': {}}}}}
    a['Guard_all_queries'] = gate("and(not(variables('AcquisitionFailed')),equals(length(variables('Queries')),length(outputs('Scope')?['hedge']?['queries'])))", 'For_each_query')
    # Preserve exact historical DOI reconciliation scope while accepting a
    # qualified, read-only current publication source as an additional input.
    a['Seed_DOIs'] = compose(seeds, 'Guard_all_queries')
    doi_input = "@outputs('Seed_DOIs')"; previous = 'Seed_DOIs'
    if doi_target:
        if set(doi_target) != {'site', 'list', 'field'} or doi_target['site'] != site:
            raise ValueError('Qualified same-site DOI source target required')
        field = doi_target['field']
        if not re.fullmatch('[A-Za-z_][A-Za-z0-9_]*', field):
            raise ValueError('Qualified DOI field required')
        a['Get_publication_dois'] = sp('GetItems', {'table': doi_target['list']}, previous)
        a['Get_publication_dois']['runtimeConfiguration'] = {'paginationPolicy': {'minimumItemCount': 100000}}
        a['Read_publication_count'] = sp('HttpRequest', {'parameters/method': 'GET',
            'parameters/uri': "_api/web/lists(guid'" + doi_target['list'] + "')?$select=ItemCount",
            'parameters/headers': {'Accept': 'application/json;odata=nometadata'}}, 'Get_publication_dois')
        a['Guard_publication_paging'] = gate("and(less(length(body('Get_publication_dois')?['value']),100000),equals(length(body('Get_publication_dois')?['value']),body('Read_publication_count')?['ItemCount']))", 'Read_publication_count')
        a['Publication_DOI_fields'] = {'type': 'Select', 'runAfter': {'Guard_publication_paging': ['Succeeded']},
            'inputs': {'from': "@body('Get_publication_dois')?['value']", 'select': {
                'Id': "@item()?['ID']", 'raw_doi': "@item()?['" + field + "']"}}}
        a['Raw_publication_doi_source'] = compose({'list': doi_target['list'], 'field': field,
            'records': "@body('Publication_DOI_fields')", 'count': "@body('Read_publication_count')"}, 'Publication_DOI_fields')
        last_source = save_read_verify(a, 'doi_source', 'publication-doi-source.json',
            "@string(outputs('Raw_publication_doi_source'))", 'Raw_publication_doi_source')
        a['Publication_DOIs'] = {'type': 'Select', 'runAfter': {last_source: ['Succeeded']},
            'inputs': {'from': "@body('Get_publication_dois')?['value']", 'select': "@toLower(trim(coalesce(item()?['" + field + "'],'')))"}}
        doi_shape = "and(startsWith(item(),'10.'),contains(item(),'/'),not(contains(item(),' ')))"
        a['Valid_DOIs'] = {'type': 'Query', 'runAfter': {'Publication_DOIs': ['Succeeded']},
            'inputs': {'from': "@body('Publication_DOIs')", 'where': '@' + doi_shape}}
        a['Invalid_DOI_values'] = {'type': 'Query', 'runAfter': {'Valid_DOIs': ['Succeeded']},
            'inputs': {'from': "@body('Publication_DOIs')", 'where': '@and(not(empty(item())),not(' + doi_shape + '))'}}
        last_invalid = save_read_verify(a, 'doi_exceptions', 'doi-input-exceptions.json',
            "@string(body('Invalid_DOI_values'))", 'Invalid_DOI_values')
        a['All_DOIs'] = compose("@union(outputs('Seed_DOIs'),body('Valid_DOIs'))", last_invalid)
        doi_input = "@outputs('All_DOIs')"; previous = 'All_DOIs'
    d = {'Get_doi': http("@concat('https://api.crossref.org/works/',uriComponent(items('For_each_doi')))")}
    d['Raw_initial_doi'] = compose({'requested_doi': "@items('For_each_doi')",
        'status_code': "@outputs('Get_doi')?['statusCode']",
        'headers': "@outputs('Get_doi')?['headers']", 'body': "@body('Get_doi')"})
    d['Raw_initial_doi']['runAfter'] = {'Get_doi': ['Succeeded', 'Failed']}
    last_initial = save_read_verify(d, 'initial_doi',
        "@concat('doi-',string(variables('DoiIndex')),'-initial.json')",
        "@string(outputs('Raw_initial_doi'))", 'Raw_initial_doi')
    d['Guard_doi_status'] = gate("contains(createArray(200,301,404),outputs('Get_doi')?['statusCode'])", last_initial)
    d['Redirect_location'] = compose("@coalesce(outputs('Get_doi')?['headers']?['Location'],outputs('Get_doi')?['headers']?['location'],'')", 'Guard_doi_status')
    d['Redirect_uri'] = compose("@if(startsWith(outputs('Redirect_location'),'/'),concat('https://api.crossref.org',outputs('Redirect_location')),outputs('Redirect_location'))", 'Redirect_location')
    redirect = {'Guard_redirect_target': gate("and(startsWith(outputs('Redirect_uri'),'https://api.crossref.org/works/'),equals(uriScheme(outputs('Redirect_uri')),'https'),equals(uriHost(outputs('Redirect_uri')),'api.crossref.org'),startsWith(toLower(decodeUriComponent(substring(uriPath(outputs('Redirect_uri')),7))),'10.'),contains(decodeUriComponent(substring(uriPath(outputs('Redirect_uri')),7)),'/'),empty(uriQuery(outputs('Redirect_uri'))),not(contains(outputs('Redirect_uri'),'#')))")}
    redirect['Get_redirect'] = http("@outputs('Redirect_uri')", 'Guard_redirect_target')
    redirect['Raw_redirect'] = compose({'original_doi': "@items('For_each_doi')",
        'uri': "@outputs('Redirect_uri')", 'status_code': "@outputs('Get_redirect')?['statusCode']",
        'headers': "@outputs('Get_redirect')?['headers']", 'body': "@body('Get_redirect')"})
    redirect['Raw_redirect']['runAfter'] = {'Get_redirect': ['Succeeded', 'Failed']}
    last_redirect = save_read_verify(redirect, 'redirect_doi',
        "@concat('doi-',string(variables('DoiIndex')),'-redirect.json')",
        "@string(outputs('Raw_redirect'))", 'Raw_redirect')
    redirect['Guard_redirect_status'] = gate("contains(createArray(200,404),outputs('Get_redirect')?['statusCode'])", last_redirect)
    d['Resolve_redirect'] = {'type': 'If', 'expression': "@equals(outputs('Get_doi')?['statusCode'],301)",
        'runAfter': {'Redirect_uri': ['Succeeded']}, 'actions': redirect, 'else': {'actions': {}}}
    d['Effective_doi_status'] = compose("@if(equals(outputs('Get_doi')?['statusCode'],301),outputs('Get_redirect')?['statusCode'],outputs('Get_doi')?['statusCode'])", 'Resolve_redirect')
    d['Effective_doi_body'] = compose("@if(equals(outputs('Get_doi')?['statusCode'],301),body('Get_redirect'),body('Get_doi'))", 'Effective_doi_status')
    d['Canonical_requested_doi'] = compose("@if(equals(outputs('Get_doi')?['statusCode'],301),toLower(decodeUriComponent(substring(uriPath(outputs('Redirect_uri')),7))),items('For_each_doi'))", 'Effective_doi_body')
    d['Guard_doi_identity'] = gate("if(equals(outputs('Effective_doi_status'),404),true,and(equals(outputs('Effective_doi_body')?['status'],'ok'),equals(toLower(coalesce(outputs('Effective_doi_body')?['message']?['DOI'],'')),outputs('Canonical_requested_doi'))))", 'Canonical_requested_doi')
    d['Raw_doi'] = compose({'requested_doi': "@items('For_each_doi')",
        'canonical_requested_doi': "@outputs('Canonical_requested_doi')",
        'initial_status_code': "@outputs('Get_doi')?['statusCode']",
        'redirect_uri': "@if(equals(outputs('Get_doi')?['statusCode'],301),outputs('Redirect_uri'),null)",
        'status_code': "@outputs('Effective_doi_status')",
        'headers': "@if(equals(outputs('Get_doi')?['statusCode'],301),outputs('Get_redirect')?['headers'],outputs('Get_doi')?['headers'])",
        'body': "@outputs('Effective_doi_body')"}, 'Guard_doi_identity')
    doi_name = "@concat('doi-',string(variables('DoiIndex')),'.json')"
    last_doi = save_read_verify(d, 'doi', doi_name, "@string(outputs('Raw_doi'))", 'Raw_doi')
    d['Append_doi_entry'] = variable('AppendToArrayVariable', 'DoiEntries', {
        'doi': "@items('For_each_doi')", 'file': doi_name,
        'http_status': "@outputs('Effective_doi_status')", 'canonical_doi': "@outputs('Canonical_requested_doi')",
        'initial_response_file': "@concat('doi-',string(variables('DoiIndex')),'-initial.json')",
        'redirect_response_file': "@if(equals(outputs('Get_doi')?['statusCode'],301),concat('doi-',string(variables('DoiIndex')),'-redirect.json'),null)",
        'saved_readback_equal': True}, last_doi)
    d['Increment_doi_index'] = variable('IncrementVariable', 'DoiIndex', 1, 'Append_doi_entry')
    d['Polite_doi_delay'] = {'type': 'Wait', 'runAfter': {'Increment_doi_index': ['Succeeded']}, 'inputs': {'interval': {'count': 5, 'unit': 'Second'}}}
    d['Mark_doi_failed'] = variable('SetVariable', 'AcquisitionFailed', True, None)
    d['Mark_doi_failed']['runAfter'] = {'Polite_doi_delay': ['Failed', 'TimedOut', 'Skipped']}
    a['For_each_doi'] = {'type': 'Foreach', 'foreach': doi_input, 'runAfter': {previous: ['Succeeded']},
        'runtimeConfiguration': {'concurrency': {'repetitions': 1}},
        'actions': {'Doi_may_run': {'type': 'If', 'expression': "@not(variables('AcquisitionFailed'))",
            'runAfter': {}, 'actions': d, 'else': {'actions': {}}}}}
    a['Guard_doi_completion'] = gate("and(not(variables('AcquisitionFailed')),equals(length(variables('DoiEntries')),length(" + doi_input[1:] + ')))', 'For_each_doi')
    a['Manifest'] = compose({'source': 'crossref', 'format': 'rims-crossref-discovery-v1', 'complete': True,
        'scope_sha256': frozen['scope_sha256'], 'until': "@outputs('Cutoff')",
        'window_filter': "@outputs('Window_filter')", 'full_reconciliation': "@outputs('Full_reconciliation')",
        'baseline_completed_at': "@if(outputs('Full_reconciliation'),outputs('Cutoff'),variables('Checkpoint')?['baseline_completed_at'])",
        'queries': "@variables('Queries')", 'doi_lookup_count': '@length(' + doi_input[1:] + ')',
        'doi_lookups': "@variables('DoiEntries')",
        'archive_folder': "@outputs('Run_folder')", 'capture_run': "@workflow()?['run']?['name']",
        'downstream_selection_applied': False}, 'Guard_doi_completion')
    last_manifest = save_read_verify(a, 'manifest', 'manifest.json', "@string(outputs('Manifest'))", 'Manifest')
    # Create an immutable completion marker only after every required raw file.
    # Last-good checkpoints are never edited or replaced; failed runs cannot
    # advance the successful high-water mark.
    marker_name = "@concat('crossref-complete-',workflow()?['run']?['name'],'.json')"
    save_read_verify(a, 'completion', marker_name, "@string(outputs('Manifest'))", last_manifest,
                     folder="'" + parent + "'")
    p['definition']['actions'] = a
    p['connectionReferences'] = refs
    return with_failure_receipt(result)


def with_bounded_total_drift_restart(document, max_restarts=1):
    """Add a fresh-cursor retry for Crossref total drift without rebuilding the graph.

    Every attempt gets disjoint page/summary names. Only pages from a stable
    attempt enter QueryPages and DOI reconciliation; rejected attempt pages and
    summaries remain in the same run archive for diagnosis. Other action groups,
    including raw PubMed/DoRA DOI producers, are retained byte-for-byte.
    """
    if type(max_restarts) is not int or not 1 <= max_restarts <= 2:
        raise ValueError('One or two finite total-drift restarts required')
    result = copy.deepcopy(document)
    p = result['properties']
    if (p.get('state') != 'Stopped' or 'Crossref' not in p.get('displayName', '')
            or p.get('isManaged') is True):
        raise ValueError('Stopped unmanaged Crossref preimage required')
    a = p['definition']['actions']
    scope = a['Scope']['inputs']
    hedge = scope.get('hedge')
    if (scope.get('policy', {}).get('source') != 'crossref'
            or not isinstance(hedge, dict)
            or a.get('Manifest', {}).get('inputs', {}).get('format') != 'rims-crossref-discovery-v1'):
        raise ValueError('Exact Crossref acquisition graph required')
    if 'total_drift_max_restarts' in hedge or 'Until_query_attempt' in str(a['For_each_query']):
        raise ValueError('Reconcile existing retry policy before another edit')

    # Freeze the retry budget in the acquisition scope. A changed policy hash
    # forces the next run through the existing full-reconciliation path.
    hedge['total_drift_max_restarts'] = max_restarts
    scope_payload = {'policy': scope['policy'], 'hedge': hedge}
    scope['scope_sha256'] = hashlib.sha256(json.dumps(scope_payload, sort_keys=True,
        separators=(',', ':')).encode()).hexdigest()

    variables = a['Initialize_paging']['inputs']['variables']
    required = {v['name'] for v in variables}
    if not {'Cursor', 'Page', 'Received', 'Expected', 'Done', 'QueryDOIs',
            'QueryPages', 'Queries', 'AcquisitionFailed'} <= required:
        raise ValueError('Expected paging variables missing')
    new_variables = [
        {'name': 'QueryAttempt', 'type': 'integer', 'value': 0},
        {'name': 'QueryAccepted', 'type': 'boolean', 'value': False},
        {'name': 'QueryTotalDrift', 'type': 'boolean', 'value': False},
        {'name': 'AttemptPages', 'type': 'array', 'value': []},
        {'name': 'AttemptSummaries', 'type': 'array', 'value': []}]
    variables.extend(v for v in new_variables if v['name'] not in required)

    loop = a['For_each_query']['actions']['Query_may_run']['actions']
    reset_names = ('Cursor', 'Page', 'Received', 'Expected', 'Done', 'QueryDOIs', 'QueryPages')
    if any('Reset_' + name not in loop for name in reset_names):
        raise ValueError('Expected exact paging reset actions missing')
    if 'Until_query_complete' not in loop or 'Guard_total_stable' not in loop['Until_query_complete']['actions']:
        raise ValueError('Expected fail-closed total guard missing')

    page = loop['Until_query_complete']['actions']
    for key in ('Verify_page', 'Save_page', 'Read_page', 'Guard_total_stable',
                'Add_received', 'Page_checkpoint', 'Set_done', 'Next_cursor',
                'Guard_cursor', 'Increment_page', 'Polite_delay',
                'Mark_page_failed', 'Stop_failed_paging'):
        if key not in page:
            raise ValueError('Unexpected Crossref page graph')
    page_name = "@concat(items('For_each_query')?['key'],'-attempt-',string(variables('QueryAttempt')),'-page-',string(variables('Page')),'.json')"
    old_page_name = "@concat(items('For_each_query')?['key'],'-page-',string(variables('Page')),'.json')"
    if page['Save_page']['inputs']['parameters']['name'] != old_page_name:
        raise ValueError('Unexpected raw page naming; reconcile before edit')
    page['Save_page']['inputs']['parameters']['name'] = page_name
    old_page_fragment = old_page_name[1:]
    if old_page_fragment not in page['Read_page']['inputs']['parameters']['path']:
        raise ValueError('Unexpected raw page readback path')
    page['Read_page']['inputs']['parameters']['path'] = page['Read_page']['inputs']['parameters']['path'].replace(old_page_fragment, page_name[1:])
    if old_page_name not in page['Page_checkpoint']['inputs']['value']['file']:
        raise ValueError('Unexpected accepted-page manifest naming')
    page['Page_checkpoint']['inputs']['value']['file'] = page['Page_checkpoint']['inputs']['value']['file'].replace(old_page_name, page_name)
    page['Append_attempt_page'] = {
        'type': 'AppendToArrayVariable', 'runAfter': {'Verify_page': ['Succeeded']},
        'inputs': {'name': 'AttemptPages', 'value': {
            'file': page_name,
            'rows': "@length(body('Get_page')?['message']?['items'])",
            'provider_total': "@body('Get_page')?['message']?['total-results']",
            'saved_readback_equal': True}}}
    page['Page_DOIs']['runAfter'] = {'Append_attempt_page': ['Succeeded']}

    # Replace the throwing guard with a branch. The mismatch branch stops only
    # the current query attempt; the outer loop decides whether to restart.
    stable = page.pop('Guard_total_stable')
    if stable.get('inputs') is None:
        raise ValueError('Total guard definition missing')
    true_names = ('Add_received', 'Page_checkpoint', 'Set_done', 'Next_cursor',
                  'Guard_cursor', 'Increment_page', 'Polite_delay',
                  'Mark_page_failed', 'Stop_failed_paging')
    true_actions = {name: page.pop(name) for name in true_names}
    true_actions['Add_received']['runAfter'] = {}
    page['If_total_stable'] = {
        'type': 'If',
        'expression': "@equals(variables('Expected'),body('Get_page')?['message']?['total-results'])",
        'runAfter': {'Set_expected': ['Succeeded']},
        'actions': true_actions,
        'else': {'actions': {
            'Mark_total_drift': {'type': 'SetVariable', 'runAfter': {},
                'inputs': {'name': 'QueryTotalDrift', 'value': True}},
            'Stop_drifted_attempt': {'type': 'SetVariable',
                'runAfter': {'Mark_total_drift': ['Succeeded']},
                'inputs': {'name': 'Done', 'value': True}}}}}

    # The page Until loop restarts at '*' on every attempt. Initial reset actions
    # move inside the attempt loop so no state leaks between attempts.
    for name in reset_names:
        loop.pop('Reset_' + name)
    attempt_actions = {'Increment_query_attempt': {
        'type': 'IncrementVariable', 'runAfter': {},
        'inputs': {'name': 'QueryAttempt', 'value': 1}}}
    previous = 'Increment_query_attempt'
    for name, value in [('Cursor', '*'), ('Page', 0), ('Received', 0),
                        ('Expected', 0), ('Done', False), ('QueryDOIs', []),
                        ('QueryPages', []), ('AttemptPages', []),
                        ('QueryTotalDrift', False)]:
        action_name = 'Attempt_reset_' + name
        attempt_actions[action_name] = {
            'type': 'SetVariable', 'runAfter': {previous: ['Succeeded']},
            'inputs': {'name': name, 'value': value}}
        previous = action_name
    attempt_actions['Until_query_complete'] = loop.pop('Until_query_complete')
    attempt_actions['Until_query_complete']['runAfter'] = {previous: ['Succeeded']}
    attempt_actions['Set_query_accepted'] = {
        'type': 'SetVariable', 'runAfter': {'Until_query_complete': ['Succeeded']},
        'inputs': {'name': 'QueryAccepted', 'value': "@and(not(variables('AcquisitionFailed')),not(variables('QueryTotalDrift')),variables('Done'),equals(variables('Received'),variables('Expected')),equals(length(variables('QueryDOIs')),variables('Expected')))"}}
    attempt_actions['Query_attempt_summary'] = {
        'type': 'Compose', 'runAfter': {'Set_query_accepted': ['Succeeded']},
        'inputs': {
            'key': "@items('For_each_query')?['key']",
            'attempt': "@variables('QueryAttempt')",
            'complete': "@variables('QueryAccepted')",
            'total_drift': "@variables('QueryTotalDrift')",
            'expected': "@variables('Expected')",
            'received': "@variables('Received')",
            'unique_dois': "@length(variables('QueryDOIs'))",
            'pages': "@variables('AttemptPages')"}}
    summary_name = "@concat(items('For_each_query')?['key'],'-attempt-',string(variables('QueryAttempt')),'-summary.json')"
    save = copy.deepcopy(loop['Save_query_summary'])
    save['runAfter'] = {'Query_attempt_summary': ['Succeeded']}
    save['inputs']['parameters']['name'] = summary_name
    save['inputs']['parameters']['body'] = "@string(outputs('Query_attempt_summary'))"
    attempt_actions['Save_attempt_summary'] = save
    read = copy.deepcopy(loop['Read_query_summary'])
    read['runAfter'] = {'Save_attempt_summary': ['Succeeded']}
    read['inputs']['parameters']['path'] = "@concat(outputs('Run_folder'),'/'," + summary_name[1:] + ')'
    attempt_actions['Read_attempt_summary'] = read
    verify = copy.deepcopy(loop['Verify_query_summary'])
    verify['runAfter'] = {'Read_attempt_summary': ['Succeeded']}
    verify['inputs'] = "@if(equals(base64(string(outputs('Query_attempt_summary'))),body('Read_attempt_summary')?['$content']),true,json('CROSSREF_ACQUISITION_REJECTED'))"
    attempt_actions['Verify_attempt_summary'] = verify
    attempt_actions['Append_attempt_summary'] = {
        'type': 'AppendToArrayVariable', 'runAfter': {'Verify_attempt_summary': ['Succeeded']},
        'inputs': {'name': 'AttemptSummaries', 'value': "@outputs('Query_attempt_summary')"}}
    loop['Initialize_query_attempt'] = {
        'type': 'SetVariable', 'runAfter': {},
        'inputs': {'name': 'QueryAttempt', 'value': 0}}
    loop['Initialize_query_acceptance'] = {
        'type': 'SetVariable', 'runAfter': {'Initialize_query_attempt': ['Succeeded']},
        'inputs': {'name': 'QueryAccepted', 'value': False}}
    loop['Initialize_query_drift'] = {
        'type': 'SetVariable', 'runAfter': {'Initialize_query_acceptance': ['Succeeded']},
        'inputs': {'name': 'QueryTotalDrift', 'value': False}}
    loop['Until_query_attempt'] = {
        'type': 'Until',
        'expression': "@or(variables('QueryAccepted'),greaterOrEquals(variables('QueryAttempt')," + str(1 + max_restarts) + "),and(greater(variables('QueryAttempt'),0),not(variables('QueryTotalDrift'))))",
        'limit': {'count': 3, 'timeout': 'P1D'},
        'runAfter': {'Initialize_query_drift': ['Succeeded']},
        'actions': attempt_actions}
    loop['Guard_query_complete']['runAfter'] = {'Until_query_attempt': ['Succeeded']}
    loop['Guard_query_complete']['inputs'] = "@if(and(not(variables('AcquisitionFailed')),variables('QueryAccepted'),variables('Done'),equals(variables('Received'),variables('Expected')),equals(length(variables('QueryDOIs')),variables('Expected'))),true,json('CROSSREF_ACQUISITION_REJECTED'))"
    loop['Query_summary']['inputs']['accepted_attempt'] = "@variables('QueryAttempt')"
    loop['Query_summary']['inputs']['attempt_count'] = "@variables('QueryAttempt')"

    a['Manifest']['inputs']['query_attempts'] = "@variables('AttemptSummaries')"
    observer = a.get('Observe_failed_generation', {}).get('actions', {})
    receipt = observer.get('Failure_receipt')
    if receipt and isinstance(receipt.get('inputs'), dict):
        receipt['inputs']['query_attempts'] = "@variables('AttemptSummaries')"
    return result


def with_created_date_partitions(document, windowed_query_keys=('tropical',), months_per_window=1,
                                first_unbounded_until='2002-12-31'):
    """Partition selected full-reconciliation queries into contiguous created-date windows.

    The first window has no lower bound, preserving all earlier records and
    future backfills. Subsequent windows are inclusive calendar-month ranges.
    Incremental runs keep the existing bounded index-date filter and execute
    exactly one window per query. Only the selected high-volume query is
    partitioned; its raw pages, attempt summaries, and query summaries retain
    the window identity.
    """
    if type(months_per_window) is not int or not 1 <= months_per_window <= 12:
        raise ValueError('Created-date partition width must be 1 to 12 months')
    keys = tuple(windowed_query_keys)
    if not keys or len(keys) != len(set(keys)):
        raise ValueError('Unique nonempty query keys required')
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', first_unbounded_until):
        raise ValueError('First unbounded date ceiling must be an ISO calendar date')

    result = copy.deepcopy(document)
    p = result['properties']
    if (p.get('state') != 'Stopped' or 'Crossref' not in p.get('displayName', '')
            or p.get('isManaged') is True):
        raise ValueError('Stopped unmanaged Crossref preimage required')
    a = p['definition']['actions']
    scope = a['Scope']['inputs']
    hedge = scope.get('hedge')
    if (scope.get('policy', {}).get('source') != 'crossref'
            or not isinstance(hedge, dict)
            or 'total_drift_max_restarts' not in hedge
            or 'Until_query_attempt' not in str(a.get('For_each_query'))):
        raise ValueError('Crossref bounded-restart graph required')
    if hedge.get('created_date_partition') or 'Until_created_windows' in str(a['For_each_query']):
        raise ValueError('Existing created-date partition policy must be reconciled before editing')
    by_key = {q.get('key'): q for q in hedge.get('queries', [])}
    if not set(keys) <= set(by_key):
        raise ValueError('Every partitioned query must exist in the frozen scope')
    for key in keys:
        if by_key[key].get('created_date_window_months') is not None:
            raise ValueError('Query already has a created-date window policy')

    # Freeze the targeted partition policy into the scope hash. The first
    # unbounded prefix window prevents the observed minimum from becoming a
    # coverage cutoff for records deposited later with older created dates.
    hedge['created_date_partition'] = {
        'strategy': 'full-reconciliation-only-inclusive-created-date-windows-v1',
        'query_keys': list(keys),
        'months_per_window': months_per_window,
        'first_unbounded_until': first_unbounded_until,
        'next_window_starts': 'day-after-first-ceiling; contiguous calendar intervals',
        'incremental_runs': 'existing from-index-date/until-index-date filter unchanged'}
    for key in keys:
        by_key[key]['created_date_window_months'] = months_per_window
    scope_payload = {'policy': scope['policy'], 'hedge': hedge}
    scope['scope_sha256'] = hashlib.sha256(json.dumps(scope_payload, sort_keys=True,
        separators=(',', ':')).encode()).hexdigest()

    variables = a['Initialize_paging']['inputs']['variables']
    names = {v['name'] for v in variables}
    additions = [
        {'name': 'CreatedWindowIndex', 'type': 'integer', 'value': 0},
        {'name': 'CreatedWindowStart', 'type': 'string', 'value': '2003-01-01T00:00:00Z'},
        {'name': 'CreatedWindowEnd', 'type': 'string', 'value': ''},
        {'name': 'CreatedWindowDone', 'type': 'boolean', 'value': False},
        {'name': 'ExpectedQueryWindowCount', 'type': 'integer', 'value': 0}]
    if names.intersection(v['name'] for v in additions):
        raise ValueError('Created-date partition variables already exist')
    variables.extend(additions)

    loop = a['For_each_query']['actions']['Query_may_run']['actions']
    required = {'Initialize_query_attempt', 'Initialize_query_acceptance', 'Initialize_query_drift',
        'Until_query_attempt', 'Guard_query_complete', 'Query_summary',
        'Save_query_summary', 'Read_query_summary', 'Verify_query_summary', 'Append_query', 'Mark_query_failed'}
    if not required <= set(loop):
        raise ValueError('Expected bounded query-attempt graph missing')
    attempt_actions = loop['Until_query_attempt']['actions']
    if not {'Query_attempt_summary', 'Save_attempt_summary', 'Read_attempt_summary',
            'Verify_attempt_summary', 'Append_attempt_summary'} <= set(attempt_actions):
        raise ValueError('Expected bounded attempt-summary graph missing')
    page = attempt_actions['Until_query_complete']['actions']
    for key in ('Save_page', 'Read_page', 'Append_attempt_page', 'Request_uri'):
        if key not in page:
            raise ValueError('Expected bounded attempt page graph missing')
    if 'Page_checkpoint' not in page.get('If_total_stable', {}).get('actions', {}):
        raise ValueError('Accepted page checkpoint must remain inside the stable-total branch')

    # Add a window component to every archive name so a cursor restart in one
    # month cannot overwrite another month's pages or summaries.
    old_page_name = page['Save_page']['inputs']['parameters']['name']
    page_name = "@concat(items('For_each_query')?['key'],'-window-',string(variables('CreatedWindowIndex')),'-attempt-',string(variables('QueryAttempt')),'-page-',string(variables('Page')),'.json')"
    if '-attempt-' not in old_page_name or "variables('CreatedWindowIndex')" in old_page_name:
        raise ValueError('Unexpected page filename policy')
    page['Save_page']['inputs']['parameters']['name'] = page_name
    old_name_core = old_page_name[1:]
    read_path = page['Read_page']['inputs']['parameters']['path']
    if old_name_core not in read_path:
        raise ValueError('Unexpected page readback path')
    page['Read_page']['inputs']['parameters']['path'] = read_path.replace(old_name_core, page_name[1:])
    checkpoint_file = page['If_total_stable']['actions']['Page_checkpoint']['inputs']['value']['file']
    if old_page_name not in checkpoint_file:
        raise ValueError('Unexpected accepted page receipt filename')
    page['If_total_stable']['actions']['Page_checkpoint']['inputs']['value']['file'] = checkpoint_file.replace(old_page_name, page_name)
    page['Request_uri']['inputs'] = page['Request_uri']['inputs'].replace("outputs('Window_filter')", "outputs('Created_window_filter')")

    # Annotate each attempt and accepted query summary with its exact bounded
    # interval and filter so the final manifest reconciles every range.
    attempt_summary = attempt_actions['Query_attempt_summary']['inputs']
    attempt_summary['window_index'] = "@variables('CreatedWindowIndex')"
    attempt_summary['window_filter'] = "@outputs('Created_window_filter')"
    attempt_summary['created_from'] = "@if(and(outputs('Full_reconciliation'),greater(int(coalesce(items('For_each_query')?['created_date_window_months'],0)),0),greater(variables('CreatedWindowIndex'),0)),variables('CreatedWindowStart'),null)"
    attempt_summary['created_until'] = "@if(and(outputs('Full_reconciliation'),greater(int(coalesce(items('For_each_query')?['created_date_window_months'],0)),0)),variables('CreatedWindowEnd'),null)"
    summary_name = "@concat(items('For_each_query')?['key'],'-window-',string(variables('CreatedWindowIndex')),'-attempt-',string(variables('QueryAttempt')),'-summary.json')"
    attempt_actions['Save_attempt_summary']['inputs']['parameters']['name'] = summary_name
    attempt_actions['Read_attempt_summary']['inputs']['parameters']['path'] = "@concat(outputs('Run_folder'),'/'," + summary_name[1:] + ')'
    query_summary = loop['Query_summary']['inputs']
    query_summary['window_index'] = "@variables('CreatedWindowIndex')"
    query_summary['window_filter'] = "@outputs('Created_window_filter')"
    query_summary['created_from'] = attempt_summary['created_from']
    query_summary['created_until'] = attempt_summary['created_until']
    query_summary['query_window_key'] = "@concat(items('For_each_query')?['key'],'-window-',string(variables('CreatedWindowIndex')))"
    query_summary_name = "@concat(items('For_each_query')?['key'],'-window-',string(variables('CreatedWindowIndex')),'-complete.json')"
    loop['Save_query_summary']['inputs']['parameters']['name'] = query_summary_name
    loop['Read_query_summary']['inputs']['parameters']['path'] = "@concat(outputs('Run_folder'),'/'," + query_summary_name[1:] + ')'

    # Build one sequential created-date window loop per logical query. Delta
    # runs and unpartitioned anchors use a single iteration with Window_filter.
    query_may_run = a['For_each_query']['actions']['Query_may_run']
    original = copy.deepcopy(loop)
    query_may_run['actions'] = {
        'Reset_created_window_index': {'type': 'SetVariable', 'runAfter': {},
            'inputs': {'name': 'CreatedWindowIndex', 'value': 0}},
        'Reset_created_window_start': {'type': 'SetVariable', 'runAfter': {'Reset_created_window_index': ['Succeeded']},
            'inputs': {'name': 'CreatedWindowStart', 'value': '2003-01-01T00:00:00Z'}},
        'Reset_created_window_done': {'type': 'SetVariable', 'runAfter': {'Reset_created_window_start': ['Succeeded']},
            'inputs': {'name': 'CreatedWindowDone', 'value': False}},
        'Until_created_windows': {'type': 'Until', 'expression': "@equals(variables('CreatedWindowDone'),true)",
            'limit': {'count': 5000, 'timeout': 'P1D'},
            'runAfter': {'Reset_created_window_done': ['Succeeded']}, 'actions': {}}}
    window_actions = query_may_run['actions']['Until_created_windows']['actions']
    window_actions['Increment_expected_query_windows'] = {'type': 'IncrementVariable', 'runAfter': {},
        'inputs': {'name': 'ExpectedQueryWindowCount', 'value': 1}}
    month_interval = "int(coalesce(items('For_each_query')?['created_date_window_months'],1))"
    end_expr = ("@if(equals(variables('CreatedWindowIndex'),0),"
        "if(greater(ticks(concat('" + first_unbounded_until + "T23:59:59Z')),ticks(outputs('Cutoff'))),outputs('Cutoff'),concat('" + first_unbounded_until + "T23:59:59Z')),"
        "if(greater(ticks(addSeconds(addToTime(variables('CreatedWindowStart')," + month_interval + ",'Month'),-1)),ticks(outputs('Cutoff'))),"
        "outputs('Cutoff'),addSeconds(addToTime(variables('CreatedWindowStart')," + month_interval + ",'Month'),-1)))")
    window_actions['Set_created_window_end'] = {'type': 'SetVariable', 'runAfter': {'Increment_expected_query_windows': ['Succeeded']},
        'inputs': {'name': 'CreatedWindowEnd', 'value': end_expr}}
    upper_string = "if(equals(ticks(variables('CreatedWindowEnd')),ticks(outputs('Cutoff'))),formatDateTime(outputs('Cutoff'),'yyyy-MM-ddTHH:mm:ss'),formatDateTime(variables('CreatedWindowEnd'),'yyyy-MM-dd'))"
    filter_expr = ("@if(and(outputs('Full_reconciliation'),greater(int(coalesce(items('For_each_query')?['created_date_window_months'],0)),0)),"
        "if(equals(variables('CreatedWindowIndex'),0),concat('until-created-date:'," + upper_string + "),"
        "concat('from-created-date:',formatDateTime(variables('CreatedWindowStart'),'yyyy-MM-dd'),',until-created-date:'," + upper_string + ")),outputs('Window_filter'))")
    window_actions['Created_window_filter'] = {'type': 'Compose', 'runAfter': {'Set_created_window_end': ['Succeeded']},
        'inputs': filter_expr}
    for name, action in original.items():
        window_actions[name] = action
    window_actions['Initialize_query_attempt']['runAfter'] = {'Created_window_filter': ['Succeeded']}

    # Append_query success advances to the next month; a failed/omitted summary
    # marks the acquisition failed and terminates this query's window loop.
    index_next = {'type': 'IncrementVariable', 'runAfter': {},
        'inputs': {'name': 'CreatedWindowIndex', 'value': 1}}
    start_next = {'type': 'SetVariable', 'runAfter': {'Increment_created_window_index': ['Succeeded']},
        'inputs': {'name': 'CreatedWindowStart', 'value': "@formatDateTime(addToTime('2003-01-01T00:00:00Z',sub(variables('CreatedWindowIndex'),1),'Month'),'yyyy-MM-ddTHH:mm:ssZ')"}}
    done_next = {'type': 'SetVariable', 'runAfter': {'Set_created_window_start': ['Succeeded']},
        'inputs': {'name': 'CreatedWindowDone', 'value': "@or(variables('AcquisitionFailed'),not(and(outputs('Full_reconciliation'),greater(int(coalesce(items('For_each_query')?['created_date_window_months'],0)),0),lessOrEquals(ticks(variables('CreatedWindowStart')),ticks(outputs('Cutoff'))))))"}}
    window_actions['Advance_created_window'] = {'type': 'Scope', 'runAfter': {'Append_query': ['Succeeded']},
        'actions': {'Increment_created_window_index': index_next,
            'Set_created_window_start': start_next, 'Set_created_window_done': done_next}}
    window_actions['Stop_created_windows_after_failure'] = {'type': 'SetVariable',
        'runAfter': {'Mark_query_failed': ['Succeeded']},
        'inputs': {'name': 'CreatedWindowDone', 'value': True}}

    a['Guard_all_queries']['inputs'] = "@if(and(not(variables('AcquisitionFailed')),equals(length(variables('Queries')),variables('ExpectedQueryWindowCount'))),true,json('CROSSREF_ACQUISITION_REJECTED'))"
    a['Manifest']['inputs']['scope_sha256'] = scope['scope_sha256']
    a['Manifest']['inputs']['query_window_count'] = "@variables('ExpectedQueryWindowCount')"
    a['Manifest']['inputs']['created_date_partition'] = hedge['created_date_partition']
    a['Manifest']['inputs']['query_attempts'] = "@variables('AttemptSummaries')"
    observer = a.get('Observe_failed_generation', {}).get('actions', {})
    receipt = observer.get('Failure_receipt')
    if receipt and isinstance(receipt.get('inputs'), dict):
        receipt['inputs']['query_attempts'] = "@variables('AttemptSummaries')"

    # Validate local action dependency references in the transformed query tree.
    def check_dependencies(actions, location):
        for name, action in actions.items():
            for dependency in action.get('runAfter', {}):
                if dependency not in actions:
                    raise ValueError(f'{location}/{name} depends on missing {dependency}')
            if 'actions' in action:
                check_dependencies(action['actions'], f'{location}/{name}/actions')
            if 'else' in action:
                check_dependencies(action['else'].get('actions', {}), f'{location}/{name}/else/actions')
    check_dependencies(a['For_each_query']['actions'], 'For_each_query/actions')
    return result


def resume_completed_hedge(document, receipt):
    """Prepare additive DOI recovery from an explicitly verified failed archive.

    The caller supplies native saved-readback evidence. This does not infer
    acceptance from local filenames, fetch files, deploy or resubmit a run.
    """
    result = copy.deepcopy(document)
    receipt = copy.deepcopy(receipt)
    p = result['properties']
    a = p['definition']['actions']
    scope = a['Scope']['inputs']
    queries = receipt['queries']
    dois = receipt['publication_dois']
    prefix = receipt['doi_entries']
    old_folder = receipt['archive_folder']
    current_prefix = a['Run_folder']['inputs'].split("@concat('", 1)[1].split("',workflow()", 1)[0]
    if (p.get('state') != 'Stopped' or receipt.get('status') != 'VERIFIED_FAILED_RUN_RECOVERY_INPUTS'
            or receipt['scope_sha256'] != scope['scope_sha256']
            or old_folder != current_prefix + receipt['source_run']
            or receipt.get('saved_page_readback_count') != sum(len(q['pages']) for q in queries)
            or receipt.get('saved_doi_readback_count') != len(prefix)
            or len(dois) != len(set(dois)) or not 0 <= len(prefix) < len(dois)):
        raise ValueError('Stopped graph and verified exact failed-run archive inputs required')
    expected = {q['key'] for q in scope['hedge']['queries']}
    if len(queries) != len(expected) or {q['key'] for q in queries} != expected:
        raise ValueError('Every frozen hedge query must be retained')
    for q in queries:
        if (q.get('complete') is not True
                or not q['expected'] == q['received'] == q['unique_dois']
                or sum(page['rows'] for page in q['pages']) != q['received']
                or any(page.get('saved_readback_equal') is not True for page in q['pages'])):
            raise ValueError('Incomplete hedge query cannot be reused')
        q['archive_folder'] = old_folder
    for index, entry in enumerate(prefix):
        if (entry['doi'] != dois[index] or entry['file'] != 'doi-' + str(index) + '.json'
                or entry['http_status'] not in (200, 404)
                or entry.get('saved_readback_equal') is not True):
            raise ValueError('Only a verified consecutive DOI prefix can be reused')
        entry['archive_folder'] = old_folder
    # Receipt objects must not be mutated while preparing the candidate.
    queries, prefix = copy.deepcopy(queries), copy.deepcopy(prefix)
    a['Cutoff']['inputs'] = receipt['until']
    a['Full_reconciliation']['inputs'] = True
    a['Window_filter']['inputs'] = receipt['window_filter']
    if receipt['window_filter'] != 'until-created-date:' + receipt['until'].removesuffix('Z'):
        raise ValueError('Recovery must preserve the original full-baseline cutoff')
    for var in a['Initialize_paging']['inputs']['variables']:
        if var['name'] == 'Queries': var['value'] = queries
        elif var['name'] == 'DoiEntries': var['value'] = prefix
        elif var['name'] == 'DoiIndex': var['value'] = len(prefix)
    a['For_each_query'] = {'type': 'Compose', 'inputs': queries,
                          'runAfter': a['For_each_query']['runAfter']}
    a['Recovery_expected_dois'] = {'type': 'Compose', 'inputs': dois,
                                 'runAfter': {'All_DOIs': ['Succeeded']}}
    a['Guard_recovery_dois'] = {'type': 'Compose', 'runAfter': {'Recovery_expected_dois': ['Succeeded']},
        'inputs': "@if(equals(outputs('All_DOIs'),outputs('Recovery_expected_dois')),true,json('CROSSREF_RECOVERY_INPUT_DRIFT'))"}
    a['For_each_doi']['foreach'] = "@skip(outputs('All_DOIs')," + str(len(prefix)) + ')'
    a['For_each_doi']['runAfter'] = {'Guard_recovery_dois': ['Succeeded']}
    a['Manifest']['inputs']['recovery'] = {'source_run': receipt['source_run'],
        'archive_folder': old_folder, 'retained_hedge_queries': len(queries),
        'retained_doi_prefix': len(prefix)}
    return result


def extend_verified_capture(document, receipt):
    """Acquire only newly added DOI inputs after a verified complete capture.

    The preceding source window and checkpoint time are preserved. This frozen
    operator definition must be replaced by the normal collector before daily
    activation. No files, service state, or input receipts are changed here.
    """
    result = copy.deepcopy(document)
    receipt = copy.deepcopy(receipt)
    p = result['properties']; a = p['definition']['actions']
    scope = a['Scope']['inputs']; queries = receipt['queries']
    dois = receipt['publication_dois']; prefix = receipt['doi_entries']
    folder = receipt['archive_folder']
    expected_folder = a['Run_folder']['inputs'].split("@concat('", 1)[1].split("',workflow()", 1)[0]
    if (p.get('state') != 'Stopped'
            or receipt.get('status') != 'VERIFIED_COMPLETE_CAPTURE_INPUT_EXPANSION'
            or a['Manifest']['inputs'].get('source') != 'crossref'
            or any(k in a['Manifest']['inputs'] for k in ('recovery', 'extension'))
            or receipt['scope_sha256'] != scope['scope_sha256']
            or folder != expected_folder + receipt['source_run']
            or type(receipt.get('full_reconciliation')) is not bool
            or not receipt.get('until', '').endswith('Z')
            or not receipt.get('window_filter', '').startswith(('until-created-date:', 'from-index-date:'))
            or receipt.get('saved_page_readback_count') != sum(len(q['pages']) for q in queries)
            or receipt.get('saved_doi_readback_count') != len(prefix)
            or len(dois) != len(set(dois)) or not 0 < len(prefix) < len(dois)):
        raise ValueError('Verified complete capture and strictly additive DOI input required')
    expected = {q['key'] for q in scope['hedge']['queries']}
    if len(queries) != len(expected) or {q['key'] for q in queries} != expected:
        raise ValueError('Every frozen hedge query must be retained')
    for q in queries:
        if (q.get('complete') is not True
                or not q['expected'] == q['received'] == q['unique_dois']
                or sum(page['rows'] for page in q['pages']) != q['received']
                or any(page.get('saved_readback_equal') is not True for page in q['pages'])
                or q.get('archive_folder', folder) != folder):
            raise ValueError('Incomplete or differently located query cannot be reused')
        q['archive_folder'] = folder
    for index, entry in enumerate(prefix):
        if (entry['doi'] != dois[index] or entry['file'] != 'doi-' + str(index) + '.json'
                or entry['http_status'] not in (200, 404)
                or entry.get('saved_readback_equal') is not True
                or entry.get('archive_folder', folder) != folder):
            raise ValueError('Only the exact verified consecutive DOI prefix can be reused')
        entry['archive_folder'] = folder
    a['Cutoff']['inputs'] = receipt['until']
    a['Full_reconciliation']['inputs'] = receipt['full_reconciliation']
    a['Window_filter']['inputs'] = receipt['window_filter']
    for variable in a['Initialize_paging']['inputs']['variables']:
        if variable['name'] == 'Queries': variable['value'] = queries
        elif variable['name'] == 'DoiEntries': variable['value'] = prefix
        elif variable['name'] == 'DoiIndex': variable['value'] = len(prefix)
    a['For_each_query'] = {'type': 'Compose', 'inputs': queries,
                          'runAfter': a['For_each_query']['runAfter']}
    a['Extension_expected_dois'] = {'type': 'Compose', 'inputs': dois,
                                  'runAfter': {'All_DOIs': ['Succeeded']}}
    a['Guard_extension_dois'] = {'type': 'Compose',
        'runAfter': {'Extension_expected_dois': ['Succeeded']},
        'inputs': "@if(equals(outputs('All_DOIs'),outputs('Extension_expected_dois')),true,json('CROSSREF_EXTENSION_INPUT_DRIFT'))"}
    a['For_each_doi']['foreach'] = '@skip(outputs(\'All_DOIs\'),' + str(len(prefix)) + ')'
    a['For_each_doi']['runAfter'] = {'Guard_extension_dois': ['Succeeded']}
    a['Manifest']['inputs']['extension'] = {'source_run': receipt['source_run'],
        'archive_folder': folder, 'retained_hedge_queries': len(queries),
        'retained_doi_prefix': len(prefix), 'checkpoint_time_preserved': True,
        'new_doi_inputs': len(dois) - len(prefix)}
    return result


def with_daily_updates(document):
    """Prepare daily Brisbane polling with the same selected acquisition scope.

    Apply only after terminal baseline reconciliation. Native enablement,
    scheduler execution and successful checkpoint catch-up remain effect gates.
    """
    result = copy.deepcopy(document)
    p = result['properties']
    scope = p['definition']['actions'].get('Scope', {}).get('inputs', {})
    if (p.get('state') != 'Stopped' or 'Crossref' not in p.get('displayName', '')
            or scope.get('policy', {}).get('source') != 'crossref'
            or scope.get('policy', {}).get('scope', {}).get('cadence') != 'daily'
            or any(k in p['definition']['actions'].get('Manifest', {}).get('inputs', {})
                   for k in ('recovery', 'extension'))
            or 'Verify_completion' not in p['definition']['actions']):
        raise ValueError('Stopped complete-scope Crossref definition required')
    actions = p['definition']['actions']
    if 'Get_publication_dois' in actions:
        actions['Get_publication_dois']['runtimeConfiguration']['paginationPolicy']['minimumItemCount'] = 5000
        actions['Guard_publication_paging']['inputs'] = actions['Guard_publication_paging']['inputs'].replace('100000', '5000')
    p['definition']['triggers'] = {'Recurrence': {'type': 'Recurrence',
        'recurrence': {'frequency': 'Day', 'interval': 1,
                       'timeZone': 'E. Australia Standard Time',
                       'schedule': {'hours': [3], 'minutes': [30]}},
        'runtimeConfiguration': {'concurrency': {'runs': 1}}}}
    return result


def with_failure_receipt(document):
    """Add durable failed-generation visibility without advancing last-good state.

    This changes only the existing collector graph. A receipt is diagnostic,
    never a successful acquisition marker, and cannot turn failure into success.
    """
    result = copy.deepcopy(document)
    actions = result['properties']['definition']['actions']
    if actions.get('Manifest', {}).get('inputs', {}).get('format') != 'rims-crossref-discovery-v1':
        raise ValueError('Qualified Crossref discovery graph required')
    names = ('Failure_receipt', 'Save_failure_receipt', 'Read_failure_receipt',
             'Verify_failure_receipt', 'Terminate_failed_generation')
    if 'Observe_failed_generation' in actions or any(name in actions for name in names):
        raise ValueError('Failure receipt already present; reconcile exact graph first')
    save = copy.deepcopy(actions['Save_completion'])
    read = copy.deepcopy(actions['Read_completion'])
    verify = copy.deepcopy(actions['Verify_completion'])
    folder = save['inputs']['parameters']['folderPath']
    if not isinstance(folder, str) or not folder.startswith('/Documents/'):
        raise ValueError('Qualified existing completion archive folder required')
    filename = "@concat('crossref-failed-',workflow()?['run']?['name'],'.json')"
    actions['Failure_receipt'] = {
        'type': 'Compose', 'runAfter': {'Verify_completion': ['Failed', 'TimedOut', 'Skipped']},
        'inputs': {'format': 'rims-crossref-failure-v1', 'source': 'crossref',
                   'complete': False, 'accepted': False,
                   'status': 'failed-or-timed-out',
                   'capture_run': "@workflow()?['run']?['name']",
                   'observed_at_utc': '@utcNow()',
                   'scope_sha256': "@outputs('Scope')?['scope_sha256']",
                   'until': "@outputs('Cutoff')",
                   'archive_folder': "@outputs('Run_folder')",
                   'query_stage': "@actions('For_each_query')?['status']",
                   'query_guard': "@actions('Guard_all_queries')?['status']",
                   'doi_stage': "@actions('For_each_doi')?['status']",
                   'doi_guard': "@actions('Guard_doi_completion')?['status']",
                   'completion_readback': "@actions('Verify_completion')?['status']",
                   'completion_write': "@actions('Save_completion')?['status']",
                   'checkpoint_disposition': 'unverified-inspect-completion-write-and-readback'}}
    save['runAfter'] = {'Failure_receipt': ['Succeeded']}
    save['inputs']['parameters']['name'] = filename
    save['inputs']['parameters']['body'] = "@base64ToBinary(base64(string(outputs('Failure_receipt'))))"
    actions['Save_failure_receipt'] = save
    read['runAfter'] = {'Save_failure_receipt': ['Succeeded']}
    read['inputs']['parameters']['path'] = "@concat('" + folder + "/crossref-failed-',workflow()?['run']?['name'],'.json')"
    actions['Read_failure_receipt'] = read
    verify['runAfter'] = {'Read_failure_receipt': ['Succeeded']}
    verify['inputs'] = "@if(equals(base64(string(outputs('Failure_receipt'))),body('Read_failure_receipt')?['$content']),true,json('CROSSREF_FAILURE_RECEIPT_MISMATCH'))"
    actions['Verify_failure_receipt'] = verify
    actions['Terminate_failed_generation'] = {
        'type': 'Terminate',
        'runAfter': {'Verify_failure_receipt': ['Succeeded', 'Failed', 'TimedOut', 'Skipped']},
        'inputs': {'runStatus': 'Failed', 'runError': {
            'code': 'CrossrefGenerationRejected',
            'message': 'Acquisition or completion readback failed; inspect retained raw archive and failure receipt. Successful checkpoint acceptance is unproved; reconcile any completed marker write before recovery.'}}}
    # Scope the terminal failure to the rejected path. A top-level Terminate
    # accepting Skipped would otherwise also run after a successful generation.
    diagnostic = {name: actions.pop(name) for name in names}
    diagnostic['Failure_receipt']['runAfter'] = {}
    actions['Observe_failed_generation'] = {
        'type': 'Scope',
        'runAfter': {'Verify_completion': ['Failed', 'TimedOut', 'Skipped']},
        'actions': diagnostic}
    return result
