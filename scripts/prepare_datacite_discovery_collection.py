"""Prepare complete institutional and publication-related DataCite acquisition.

Local-only builder. Preserve full public metadata before any output selection.
Native deployment requires fresh drift/readback and publication-input acceptance.
"""
import copy
import hashlib
import json
import re
from datetime import datetime
from urllib.parse import urlsplit


def quote_query(value):
    return '"' + value.replace('\\', '\\\\').replace('"', '\\"') + '"'


def freeze_hedge(collector, policy):
    if policy.get('source') != 'datacite':
        raise ValueError('Selected DataCite source policy required')
    query = collector['pubmed']['query']
    quoted = r'"([^"\n]+)"\s*\[Affiliation\]'
    aliases = list(dict.fromkeys(x for x in re.findall(quoted, query, flags=re.I)
                                if x.casefold() not in {'queensland', 'australia', 'qld'}))
    remainder = re.sub(quoted, '', query, flags=re.I)
    remainder = re.sub(r'\b(?:Queensland|Australia|QLD)\s*\[Affiliation\]', '', remainder, flags=re.I)
    if re.search(r'\[Affiliation\]', remainder, flags=re.I):
        raise ValueError('Unrecognised affiliation terms need explicit hedge mapping')
    if not aliases:
        raise ValueError('Maintained institutional affiliation aliases required')
    queries = []
    for index in range(0, len(aliases), 4):
        group = aliases[index:index + 4]
        terms = ' OR '.join(quote_query(alias) for alias in group)
        queries.append({'key': 'institutional-' + str(index // 4), 'kind': 'institutional',
            'aliases': group, 'query': '(creators.affiliation.name:(' + terms
                + ') OR contributors.affiliation.name:(' + terms + '))'})
    frozen = {'policy': policy, 'institutional_queries': queries,
        'hedge_version': collector.get('facility_query_version'),
        'rows_per_page': 250, 'related_dois_per_query': 20,
        'full_metadata_options': {'detail': 'true', 'affiliation': 'true', 'publisher': 'true'}}
    frozen['scope_sha256'] = hashlib.sha256(json.dumps(frozen, sort_keys=True,
        separators=(',', ':')).encode()).hexdigest()
    return frozen


def build(document, frozen, doi_target):
    result = copy.deepcopy(document)
    p = result['properties']
    if (p.get('state') != 'Stopped' or p.get('isManaged') is True
            or 'DataCite' not in p.get('displayName', '')
            or frozen.get('policy', {}).get('source') != 'datacite'):
        raise ValueError('Stopped DataCite preimage and selected frozen scope required')
    old = p['definition']['actions']
    site = old['Create_exclusive_folder']['inputs']['parameters']['dataset']
    folder = old['Run_folder']['inputs']
    if not folder.startswith("@concat('") or '/datacite-source-' not in folder:
        raise ValueError('Accepted DataCite archive preimage required')
    parent = folder.split("@concat('", 1)[1].split('/datacite-source-', 1)[0]
    personal = urlsplit(site).path.rstrip('/')
    host = copy.deepcopy(old['Create_exclusive_folder']['inputs']['host'])
    if (doi_target.get('site') != site or not doi_target.get('population_kind')
            or not re.fullmatch('[A-Za-z_][A-Za-z0-9_]*', doi_target.get('field', ''))
            or not re.fullmatch('[0-9a-fA-F-]{36}', doi_target.get('list', ''))):
        raise ValueError('Qualified same-site publication DOI source required')
    field = doi_target['field']
    seeds = list(dict.fromkeys(x['doi'].strip().lower() for x in old['Requested_ids']['inputs']))

    def compose(value, previous=None):
        return {'type': 'Compose', 'inputs': value,
                'runAfter': {previous: ['Succeeded']} if previous else {}}

    def gate(condition, previous=None):
        return compose('@if(' + condition + ",true,json('DATACITE_ACQUISITION_REJECTED'))", previous)

    def var(kind, name, value, previous=None):
        return {'type': kind, 'inputs': {'name': name, 'value': value},
                'runAfter': {previous: ['Succeeded']} if previous else {}}

    def sp(operation, params, previous=None):
        h = copy.deepcopy(host); h['operationId'] = operation
        return {'type': 'OpenApiConnection', 'runAfter': {previous: ['Succeeded']} if previous else {},
                'inputs': {'host': h, 'parameters': {'dataset': site, **params}, 'retryPolicy': {'type': 'none'}}}

    def save(actions, key, name, expression, previous, folder_expr="outputs('Run_folder')"):
        folder_value = folder_expr[1:-1] if folder_expr.startswith("'") else '@' + folder_expr
        name_expr = name[1:] if name.startswith('@') else "'" + name + "'"
        actions['Save_' + key] = sp('CreateFile', {'folderPath': folder_value, 'name': name,
            'body': '@base64ToBinary(base64(' + expression + '))'}, previous)
        actions['Read_' + key] = sp('GetFileContentByPath', {'path': '@concat(' + folder_expr + ",'/'," + name_expr + ')',
            'inferContentType': False}, 'Save_' + key)
        actions['Verify_' + key] = gate('equals(base64(' + expression + "),body('Read_" + key + "')?['$content'])", 'Read_' + key)
        return 'Verify_' + key

    a = {'Scope': compose(frozen)}
    a['Cutoff'] = compose("@formatDateTime(addMinutes(utcNow(),-10),'yyyy-MM-ddTHH:mm:ssZ')", 'Scope')
    a['Find_checkpoint'] = sp('HttpRequest', {'parameters/method': 'GET',
        'parameters/uri': "_api/web/GetFolderByServerRelativeUrl('" + personal + parent + "')/Files?$filter=startswith(Name,'datacite-discovery-complete-')&$orderby=TimeCreated desc&$top=1&$select=Name,ETag",
        'parameters/headers': {'Accept': 'application/json;odata=nometadata'}}, 'Cutoff')
    a['Initialize'] = {'type': 'InitializeVariable', 'runAfter': {'Find_checkpoint': ['Succeeded']},
        'inputs': {'variables': [{'name': 'Checkpoint', 'type': 'object', 'value': {}},
            {'name': 'Queries', 'type': 'array', 'value': frozen['institutional_queries']},
            {'name': 'Completions', 'type': 'array', 'value': []},
            {'name': 'Cursor', 'type': 'string', 'value': '1'}, {'name': 'Page', 'type': 'integer', 'value': 0},
            {'name': 'Expected', 'type': 'integer', 'value': 0}, {'name': 'Received', 'type': 'integer', 'value': 0},
            {'name': 'IDs', 'type': 'array', 'value': []}, {'name': 'Pages', 'type': 'array', 'value': []},
            {'name': 'Done', 'type': 'boolean', 'value': False}, {'name': 'Failed', 'type': 'boolean', 'value': False}]}}
    a['Has_checkpoint'] = {'type': 'If', 'expression': "@not(empty(body('Find_checkpoint')?['value']))",
        'runAfter': {'Initialize': ['Succeeded']}, 'actions': {
            'Read_checkpoint': sp('GetFileContentByPath', {'path': "@concat('" + parent + "/',first(body('Find_checkpoint')?['value'])?['Name'])", 'inferContentType': False}),
            'Parse_checkpoint': var('SetVariable', 'Checkpoint', "@json(base64ToString(body('Read_checkpoint')?['$content']))", 'Read_checkpoint'),
            'Guard_checkpoint': gate("and(equals(variables('Checkpoint')?['source'],'datacite'),equals(variables('Checkpoint')?['complete'],true),lessOrEquals(ticks(variables('Checkpoint')?['until']),ticks(outputs('Cutoff'))))", 'Parse_checkpoint')},
        'else': {'actions': {}}}
    a['Full_reconciliation'] = compose("@or(empty(variables('Checkpoint')),not(equals(variables('Checkpoint')?['scope_sha256'],outputs('Scope')?['scope_sha256'])),lessOrEquals(ticks(coalesce(variables('Checkpoint')?['baseline_completed_at'],'1900-01-01T00:00:00Z')),ticks(addDays(utcNow(),-28))))", 'Has_checkpoint')
    a['Get_publication_dois'] = sp('GetItems', {'table': doi_target['list']}, 'Full_reconciliation')
    a['Get_publication_dois']['runtimeConfiguration'] = {'paginationPolicy': {'minimumItemCount': 100000}}
    a['Read_publication_count'] = sp('HttpRequest', {'parameters/method': 'GET',
        'parameters/uri': "_api/web/lists(guid'" + doi_target['list'] + "')?$select=ItemCount",
        'parameters/headers': {'Accept': 'application/json;odata=nometadata'}}, 'Get_publication_dois')
    a['Guard_publication_paging'] = gate("and(less(length(body('Get_publication_dois')?['value']),100000),equals(length(body('Get_publication_dois')?['value']),body('Read_publication_count')?['ItemCount']))", 'Read_publication_count')
    a['Raw_doi_fields'] = {'type': 'Select', 'runAfter': {'Guard_publication_paging': ['Succeeded']},
        'inputs': {'from': "@body('Get_publication_dois')?['value']", 'select': {
            'Id': "@coalesce(item()?['ID'],item()?['Id'])", 'raw_doi': "@item()?['" + field + "']"}}}
    a['Normalised_dois'] = {'type': 'Select', 'runAfter': {'Raw_doi_fields': ['Succeeded']},
        'inputs': {'from': "@body('Raw_doi_fields')", 'select': "@toLower(trim(coalesce(item()?['raw_doi'],'')))"}}
    shape = "and(startsWith(item(),'10.'),contains(item(),'/'),not(contains(item(),' ')))"
    a['Valid_dois'] = {'type': 'Query', 'runAfter': {'Normalised_dois': ['Succeeded']},
        'inputs': {'from': "@body('Normalised_dois')", 'where': '@' + shape}}
    a['Invalid_doi_values'] = {'type': 'Query', 'runAfter': {'Valid_dois': ['Succeeded']},
        'inputs': {'from': "@body('Normalised_dois')", 'where': '@and(not(empty(item())),not(' + shape + '))'}}
    a['Seed_dois'] = compose(seeds, 'Invalid_doi_values')
    a['All_dois'] = compose("@union(body('Valid_dois'),outputs('Seed_dois'),coalesce(variables('Checkpoint')?['publication_dois'],json('[]')))", 'Seed_dois')
    a['Quoted_dois'] = {'type': 'Select', 'runAfter': {'All_dois': ['Succeeded']},
        'inputs': {'from': "@outputs('All_dois')", 'select': r"""@concat('"',replace(replace(item(),'\','\\'),'"','\"'),'"')"""}}
    a['For_each_doi_batch'] = {'type': 'Foreach',
        'foreach': "@range(0,div(add(length(body('Quoted_dois')),19),20))",
        'runAfter': {'Quoted_dois': ['Succeeded']}, 'runtimeConfiguration': {'concurrency': {'repetitions': 1}},
        'actions': {'Append_related_query': var('AppendToArrayVariable', 'Queries', {
            'key': "@concat('related-',string(items('For_each_doi_batch')))", 'kind': 'related',
            'query': "@concat('relatedIdentifiers.relatedIdentifier:(',join(take(skip(body('Quoted_dois'),mul(items('For_each_doi_batch'),20)),20),' OR '),')')"})}}
    a['Run_folder'] = compose("@concat('" + parent + "/datacite-discovery-',workflow()?['run']?['name'])", 'For_each_doi_batch')
    a['Create_exclusive_folder'] = sp('HttpRequest', {'parameters/method': 'POST', 'parameters/uri': '_api/web/folders',
        'parameters/headers': {'Accept': 'application/json;odata=nometadata', 'Content-Type': 'application/json;odata=nometadata'},
        'parameters/body': {'ServerRelativeUrl': "@concat('" + personal + "',outputs('Run_folder'))"}}, 'Run_folder')
    last = save(a, 'scope', 'scope.json', "string(outputs('Scope'))", 'Create_exclusive_folder')
    a['Doi_source_snapshot'] = compose({'population_kind': doi_target['population_kind'], 'list': doi_target['list'],
        'field': field, 'rows': "@body('Raw_doi_fields')", 'source_count': "@body('Read_publication_count')?['ItemCount']",
        'invalid_values': "@body('Invalid_doi_values')", 'publication_dois': "@outputs('All_dois')",
        'queries': "@variables('Queries')", 'observed_utc': "@utcNow()"}, last)
    last = save(a, 'doi_source', 'publication-doi-source.json', "string(outputs('Doi_source_snapshot'))", 'Doi_source_snapshot')
    q = {}; previous = None
    for name, value in [('Cursor', '1'), ('Page', 0), ('Expected', 0), ('Received', 0), ('IDs', []), ('Pages', []), ('Done', False)]:
        key = 'Reset_' + name; q[key] = var('SetVariable', name, value, previous); previous = key
    q['Query_with_window'] = compose("@concat('(',items('For_each_query')?['query'],') AND ',if(and(not(outputs('Full_reconciliation')),equals(items('For_each_query')?['kind'],'institutional')),concat('updated:[\"',formatDateTime(addDays(variables('Checkpoint')?['until'],-7),'yyyy-MM-ddTHH:mm:ssZ'),'\" TO \"',outputs('Cutoff'),'\"]'),concat('created:[* TO \"',outputs('Cutoff'),'\"]')))", previous)
    params = {'query': "@outputs('Query_with_window')", 'page[size]': 250,
        'page[cursor]': "@variables('Cursor')", 'detail': 'true', 'affiliation': 'true', 'publisher': 'true'}
    page = {'Get_page': {'type': 'Http', 'runAfter': {}, 'inputs': {'method': 'GET',
        'uri': 'https://api.datacite.org/dois', 'queries': params,
        'headers': {'Accept': 'application/json', 'User-Agent': 'RIMS-source-retention/1.0 (https://github.com/edithatogo/careops-rims)'},
        'retryPolicy': {'type': 'exponential', 'count': 3, 'interval': 'PT10S'}}}}
    page['Guard_page'] = gate("and(equals(outputs('Get_page')?['statusCode'],200),greaterOrEquals(body('Get_page')?['meta']?['total'],0),lessOrEquals(length(body('Get_page')?['data']),250))", 'Get_page')
    page['Raw_page'] = compose({'uri': 'https://api.datacite.org/dois', 'parameters': params,
        'http_status': "@outputs('Get_page')?['statusCode']", 'headers': "@outputs('Get_page')?['headers']",
        'body': "@body('Get_page')"}, 'Guard_page')
    page_name = "@concat(items('For_each_query')?['key'],'-page-',string(variables('Page')),'.json')"
    last_page = save(page, 'page', page_name, "string(outputs('Raw_page'))", 'Raw_page')
    page['Read_page_metadata'] = sp('GetFileMetadataByPath', {
        'path': "@concat(outputs('Run_folder'),'/'," + page_name[1:] + ')'}, 'Guard_page')
    page['Guard_page_metadata'] = gate(
        "not(empty(outputs('Read_page_metadata')?['body']?['ETag']))", 'Read_page_metadata')
    page['Page_ids'] = {'type': 'Select', 'runAfter': {'Guard_page_metadata': ['Succeeded']},
        'inputs': {'from': "@body('Get_page')?['data']", 'select': "@toLower(item()?['id'])"}}
    page['Attribute_dois'] = {'type': 'Select', 'runAfter': {'Page_ids': ['Succeeded']},
        'inputs': {'from': "@body('Get_page')?['data']", 'select': "@toLower(item()?['attributes']?['doi'])"}}
    page['Guard_ids'] = gate("equals(body('Page_ids'),body('Attribute_dois'))", 'Attribute_dois')
    page['Expected_value'] = compose("@if(equals(variables('Page'),0),body('Get_page')?['meta']?['total'],variables('Expected'))", 'Guard_ids')
    page['Set_expected'] = var('SetVariable', 'Expected', "@outputs('Expected_value')", 'Expected_value')
    page['Guard_total'] = gate("equals(variables('Expected'),body('Get_page')?['meta']?['total'])", 'Set_expected')
    page['Merged_ids'] = compose("@union(variables('IDs'),body('Page_ids'))", 'Guard_total')
    page['Set_ids'] = var('SetVariable', 'IDs', "@outputs('Merged_ids')", 'Merged_ids')
    page['Add_received'] = var('IncrementVariable', 'Received', "@length(body('Page_ids'))", 'Set_ids')
    page['Set_done'] = var('SetVariable', 'Done', "@empty(body('Get_page')?['links']?['next'])", 'Add_received')
    next_link = "body('Get_page')?['links']?['next']"
    page['Guard_next_location'] = gate("if(variables('Done'),true,and(equals(uriScheme(" + next_link + "),'https'),equals(uriHost(" + next_link + "),'api.datacite.org'),equals(uriPath(" + next_link + "),'/dois')))", 'Set_done')
    page['Next_parameters'] = compose("@if(variables('Done'),json('[]'),split(substring(uriQuery(" + next_link + "),1),'&'))", 'Guard_next_location')
    page['Cursor_parameters'] = {'type': 'Query', 'runAfter': {'Next_parameters': ['Succeeded']},
        'inputs': {'from': "@outputs('Next_parameters')", 'where': "@equals(toLower(decodeUriComponent(first(split(item(),'=')))),'page[cursor]')"}}
    page['Guard_cursor_parameter'] = gate("if(variables('Done'),true,equals(length(body('Cursor_parameters')),1))", 'Cursor_parameters')
    page['Set_cursor'] = var('SetVariable', 'Cursor', "@if(variables('Done'),'',decodeUriComponent(substring(first(body('Cursor_parameters')),add(indexOf(first(body('Cursor_parameters')),'='),1))))", 'Guard_cursor_parameter')
    page['Page_receipt'] = var('AppendToArrayVariable', 'Pages', {'file': page_name,
        'rows': "@length(body('Page_ids'))", 'saved_content_equal': True,
        'etag': "@outputs('Read_page_metadata')?['body']?['ETag']",
        'archive_folder': "@outputs('Run_folder')"}, 'Set_cursor')
    page['Increment_page'] = var('IncrementVariable', 'Page', 1, 'Page_receipt')
    page['Polite_delay'] = {'type': 'Wait', 'runAfter': {'Increment_page': ['Succeeded']},
        'inputs': {'interval': {'count': 1, 'unit': 'Second'}}}
    page['Mark_failed'] = var('SetVariable', 'Failed', True)
    page['Mark_failed']['runAfter'] = {'Polite_delay': ['Failed', 'TimedOut', 'Skipped']}
    page['Stop_failed_paging'] = var('SetVariable', 'Done', True, 'Mark_failed')
    q['Until_complete'] = {'type': 'Until', 'expression': "@equals(variables('Done'),true)",
        'limit': {'count': 5000, 'timeout': 'P1D'}, 'runAfter': {'Query_with_window': ['Succeeded']}, 'actions': page}
    q['Guard_query_complete'] = gate("and(not(variables('Failed')),variables('Done'),equals(variables('Expected'),variables('Received')),equals(variables('Expected'),length(variables('IDs'))))", 'Until_complete')
    q['Query_summary'] = compose({'key': "@items('For_each_query')?['key']", 'kind': "@items('For_each_query')?['kind']",
        'query': "@outputs('Query_with_window')", 'provider_total': "@variables('Expected')",
        'received': "@variables('Received')", 'unique_dois': "@length(variables('IDs'))",
        'scope_sha256': "@outputs('Scope')?['scope_sha256']",
        'pages': "@variables('Pages')", 'complete': True,
        'archive_folder': "@outputs('Run_folder')"}, 'Guard_query_complete')
    last_query = save(q, 'query', "@concat(items('For_each_query')?['key'],'-complete.json')", "string(outputs('Query_summary'))", 'Query_summary')
    q['Append_completion'] = var('AppendToArrayVariable', 'Completions', "@outputs('Query_summary')", last_query)
    q['Mark_query_failed'] = var('SetVariable', 'Failed', True)
    q['Mark_query_failed']['runAfter'] = {'Append_completion': ['Failed', 'TimedOut', 'Skipped']}
    a['For_each_query'] = {'type': 'Foreach', 'foreach': "@variables('Queries')", 'runAfter': {last: ['Succeeded']},
        'runtimeConfiguration': {'concurrency': {'repetitions': 1}}, 'actions': {
            'Query_may_run': {'type': 'If', 'expression': "@not(variables('Failed'))", 'runAfter': {},
                'actions': q, 'else': {'actions': {}}}}}
    a['Guard_complete'] = gate("and(not(variables('Failed')),equals(length(variables('Queries')),length(variables('Completions'))))", 'For_each_query')
    a['Manifest'] = compose({'source': 'datacite', 'format': 'rims-datacite-discovery-v1', 'complete': True,
        'scope_sha256': frozen['scope_sha256'], 'until': "@outputs('Cutoff')",
        'full_reconciliation': "@outputs('Full_reconciliation')",
        'baseline_completed_at': "@if(outputs('Full_reconciliation'),outputs('Cutoff'),variables('Checkpoint')?['baseline_completed_at'])",
        'publication_doi_population_kind': doi_target['population_kind'],
        'publication_doi_snapshot': 'publication-doi-source.json', 'publication_dois': "@outputs('All_dois')",
        'queries': "@variables('Completions')", 'archive_folder': "@outputs('Run_folder')",
        'capture_run': "@workflow()?['run']?['name']", 'full_metadata_options': frozen['full_metadata_options'],
        'downstream_selection_applied': False}, 'Guard_complete')
    last = save(a, 'manifest', 'manifest.json', "string(outputs('Manifest'))", 'Manifest')
    save(a, 'completion', "@concat('datacite-discovery-complete-',workflow()?['run']?['name'],'.json')",
         "string(outputs('Manifest'))", last, folder_expr="'" + parent + "'")
    p['definition']['actions'] = a
    return with_failure_receipt(with_runtime_page_retention(result))


def with_weekly_updates(document):
    result = copy.deepcopy(document)
    p = result['properties']
    scope = p['definition']['actions'].get('Scope', {}).get('inputs', {})
    if (p.get('state') != 'Stopped' or p.get('isManaged') is True
            or scope.get('policy', {}).get('source') != 'datacite'
            or scope.get('policy', {}).get('scope', {}).get('cadence') != 'weekly'
            or 'Verify_completion' not in p['definition']['actions']):
        raise ValueError('Stopped complete-scope DataCite definition required')
    # Recurrence saves use the platform's 5,000-item pagination ceiling.
    # Count equality and a strict boundary guard remain mandatory: a capped
    # population is a failed acquisition, never a smaller accepted scope.
    actions = p['definition']['actions']
    actions['Get_publication_dois']['runtimeConfiguration']['paginationPolicy']['minimumItemCount'] = 5000
    actions['Guard_publication_paging']['inputs'] = actions['Guard_publication_paging']['inputs'].replace('100000', '5000')
    p['definition']['triggers'] = {'Recurrence': {'type': 'Recurrence',
        'recurrence': {'frequency': 'Week', 'interval': 1, 'timeZone': 'E. Australia Standard Time',
            'schedule': {'weekDays': ['Thursday'], 'hours': [5], 'minutes': [0]}},
        'runtimeConfiguration': {'concurrency': {'runs': 1}}}}
    return result


def with_runtime_page_retention(document):
    """Repair the observed Consumption delay and retain rejected raw responses.

    Only raw evidence storage may precede validation. IDs, counts, pagination,
    accepted manifests and the last-good marker remain downstream of the guard.
    """
    result = copy.deepcopy(document)
    actions = result['properties']['definition']['actions']
    if actions.get('Manifest', {}).get('inputs', {}).get('format') != 'rims-datacite-discovery-v1':
        raise ValueError('Qualified DataCite discovery graph required')
    page = actions['For_each_query']['actions']['Query_may_run']['actions']['Until_complete']['actions']
    if (page['Raw_page'].get('runAfter') not in (
            {'Guard_page': ['Succeeded']}, {'Get_page': ['Succeeded', 'Failed', 'TimedOut']})
            or page['Guard_page'].get('runAfter') not in (
                {'Get_page': ['Succeeded']}, {'Verify_page': ['Succeeded']})
            or page['Page_ids'].get('runAfter') not in (
                {'Verify_page': ['Succeeded']}, {'Guard_page': ['Succeeded']},
                {'Guard_page_metadata': ['Succeeded']})
            or page['Polite_delay']['inputs'].get('interval') not in (
                {'count': 1, 'unit': 'Second'}, {'count': 5, 'unit': 'Second'})):
        raise ValueError('DataCite page dependency or pacing drift; reconcile before repair')
    page['Raw_page']['runAfter'] = {'Get_page': ['Succeeded', 'Failed', 'TimedOut']}
    page['Raw_page']['inputs']['request_outcome'] = "@actions('Get_page')?['status']"
    page['Raw_page']['inputs']['transport_error'] = "@outputs('Get_page')?['error']"
    page['Guard_page']['runAfter'] = {'Verify_page': ['Succeeded']}
    page['Page_ids']['runAfter'] = {'Guard_page_metadata': ['Succeeded']}
    page['Polite_delay']['inputs']['interval']['count'] = 5
    return result


def with_failure_receipt(document):
    """Retain rejected-generation diagnostics without accepting its checkpoint."""
    result = copy.deepcopy(document)
    actions = result['properties']['definition']['actions']
    if actions.get('Manifest', {}).get('inputs', {}).get('format') != 'rims-datacite-discovery-v1':
        raise ValueError('Qualified DataCite discovery graph required')
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
    diagnostic = {'Failure_receipt': {
        'type': 'Compose', 'runAfter': {},
        'inputs': {'format': 'rims-datacite-failure-v2', 'recovery_protocol': 1,
            'source': 'datacite',
            'complete': False, 'accepted': False, 'status': 'failed-or-timed-out',
            'capture_run': "@workflow()?['run']?['name']", 'observed_at_utc': '@utcNow()',
            'scope_sha256': "@outputs('Scope')?['scope_sha256']", 'until': "@outputs('Cutoff')",
            'archive_folder': "@outputs('Run_folder')",
            'previous_checkpoint': {
                'source': "@variables('Checkpoint')?['source']",
                'complete': "@variables('Checkpoint')?['complete']",
                'scope_sha256': "@variables('Checkpoint')?['scope_sha256']",
                'until': "@variables('Checkpoint')?['until']",
                'baseline_completed_at': "@variables('Checkpoint')?['baseline_completed_at']",
                'capture_run': "@variables('Checkpoint')?['capture_run']",
                'archive_folder': "@variables('Checkpoint')?['archive_folder']",
                'etag': "@first(body('Find_checkpoint')?['value'])?['ETag']"},
            # Preserve only fully archived query summaries. A recovery may reuse
            # this contiguous prefix, but must still verify each saved page and
            # the original checkpoint before creating a new generation.
            'complete_query_prefix': "@variables('Completions')",
            'full_reconciliation': "@outputs('Full_reconciliation')",
            'publication_input_guard': "@actions('Guard_publication_paging')?['status']",
            'query_stage': "@actions('For_each_query')?['status']",
            'query_guard': "@actions('Guard_complete')?['status']",
            'completion_write': "@actions('Save_completion')?['status']",
            'completion_readback': "@actions('Verify_completion')?['status']",
            'checkpoint_disposition': 'unverified-inspect-completion-write-and-readback'}}}
    save['runAfter'] = {'Failure_receipt': ['Succeeded']}
    save['inputs']['parameters']['name'] = "@concat('datacite-failed-',workflow()?['run']?['name'],'.json')"
    save['inputs']['parameters']['body'] = "@base64ToBinary(base64(string(outputs('Failure_receipt'))))"
    diagnostic['Save_failure_receipt'] = save
    read['runAfter'] = {'Save_failure_receipt': ['Succeeded']}
    read['inputs']['parameters']['path'] = "@concat('" + folder + "/datacite-failed-',workflow()?['run']?['name'],'.json')"
    diagnostic['Read_failure_receipt'] = read
    verify['runAfter'] = {'Read_failure_receipt': ['Succeeded']}
    verify['inputs'] = "@if(equals(base64(string(outputs('Failure_receipt'))),body('Read_failure_receipt')?['$content']),true,json('DATACITE_FAILURE_RECEIPT_MISMATCH'))"
    diagnostic['Verify_failure_receipt'] = verify
    diagnostic['Terminate_failed_generation'] = {
        'type': 'Terminate',
        'runAfter': {'Verify_failure_receipt': ['Succeeded', 'Failed', 'TimedOut', 'Skipped']},
        'inputs': {'runStatus': 'Failed', 'runError': {
            'code': 'DataCiteGenerationRejected',
            'message': 'Acquisition or completion readback failed; inspect retained raw archive and failure receipt. Reconcile any completed marker write before recovery.'}}}
    actions['Observe_failed_generation'] = {
        'type': 'Scope', 'runAfter': {'Verify_completion': ['Failed', 'TimedOut', 'Skipped']},
        'actions': diagnostic}
    return result


def prepare_recovery_provenance(document, *, expected_definition_sha256):
    """Upgrade the exact normal DataCite flow to emit reusable provenance.

    This does not load or consume failure receipts. It adds SharePoint ETags to
    complete page references and binds a v2 failure receipt to the checkpoint
    that existed before the failed generation. The automatic reader is a
    separate change and must reject older receipts without these fields.
    """
    result = copy.deepcopy(document)
    props = result.get('properties', {})
    definition = props.get('definition', {})
    actions = definition.get('actions', {})
    fingerprint = hashlib.sha256(json.dumps(
        definition, sort_keys=True, separators=(',', ':'), ensure_ascii=False
    ).encode()).hexdigest()
    if (not re.fullmatch(r'[0-9a-f]{64}', expected_definition_sha256 or '')
            or fingerprint != expected_definition_sha256):
        raise ValueError('Definition drift; reconcile before recovery provenance repair')
    if (result.get('id') != '/providers/Microsoft.Flow/environments/Default-0b65b008-95d7-4abc-bafc-3ffc20c039c0/flows/47f4378d-a752-49be-ab6b-a8b4491a574a'
            or props.get('state') != 'Stopped' or props.get('isManaged') is not False
            or 'DataCite' not in props.get('displayName', '')
            or set(definition.get('triggers', {})) != {'Recurrence'}
            or len(actions) != 50):
        raise ValueError('Exact stopped unmanaged DataCite weekly preimage required')
    find_uri = actions['Find_checkpoint']['inputs']['parameters']['parameters/uri']
    suffix = '&$select=Name'
    if not find_uri.endswith(suffix):
        raise ValueError('Checkpoint listing drift; reconcile before provenance repair')
    if 'Read_page_metadata' in actions['For_each_query']['actions']['Query_may_run']['actions']['Until_complete']['actions']:
        raise ValueError('Page metadata provenance already installed; reconcile exact graph')
    failure_actions = actions['Observe_failed_generation']['actions']
    if failure_actions['Failure_receipt']['inputs'].get('format') != 'rims-datacite-failure-v1':
        raise ValueError('Expected v1 failure receipt preimage required')

    actions['Find_checkpoint']['inputs']['parameters']['parameters/uri'] = find_uri + ',ETag,TimeCreated'
    page = actions['For_each_query']['actions']['Query_may_run']['actions']['Until_complete']['actions']
    old_page_receipt = page['Page_receipt']
    values = old_page_receipt['inputs']['value']
    if (not {'file', 'rows', 'saved_content_equal'}.issubset(values)
            or set(values) - {'file', 'rows', 'saved_content_equal', 'archive_folder'}):
        raise ValueError('Page receipt fields drifted; reconcile before provenance repair')
    metadata = copy.deepcopy(page['Read_page'])
    metadata['runAfter'] = {'Guard_page': ['Succeeded']}
    metadata['inputs']['host']['operationId'] = 'GetFileMetadataByPath'
    metadata['inputs']['parameters'] = {
        'dataset': metadata['inputs']['parameters']['dataset'],
        'path': metadata['inputs']['parameters']['path']}
    page['Read_page_metadata'] = metadata
    page['Guard_page_metadata'] = {
        'type': 'Compose', 'runAfter': {'Read_page_metadata': ['Succeeded']},
        'inputs': "@if(not(empty(outputs('Read_page_metadata')?['body']?['ETag'])),true,json('DATACITE_PAGE_ETAG_MISSING'))"}
    page['Page_ids']['runAfter'] = {'Guard_page_metadata': ['Succeeded']}
    values.setdefault('archive_folder', "@outputs('Run_folder')")
    values['etag'] = "@outputs('Read_page_metadata')?['body']?['ETag']"

    receipt = failure_actions['Failure_receipt']['inputs']
    receipt['format'] = 'rims-datacite-failure-v2'
    receipt['recovery_protocol'] = 1
    receipt['previous_checkpoint'] = {
        'file': "@first(body('Find_checkpoint')?['value'])?['Name']",
        'source': "@variables('Checkpoint')?['source']",
        'complete': "@variables('Checkpoint')?['complete']",
        'scope_sha256': "@variables('Checkpoint')?['scope_sha256']",
        'until': "@variables('Checkpoint')?['until']",
        'baseline_completed_at': "@variables('Checkpoint')?['baseline_completed_at']",
        'capture_run': "@variables('Checkpoint')?['capture_run']",
        'archive_folder': "@variables('Checkpoint')?['archive_folder']",
        'etag': "@first(body('Find_checkpoint')?['value'])?['ETag']"}
    # A later run can compare the exact dynamic query plan, including DOI-derived
    # related queries, before reusing any completed prefix.
    receipt['planned_queries'] = "@variables('Queries')"
    return result


def prepare_automatic_failure_prefix_reader(document, *, expected_definition_sha256):
    """Add fail-closed reuse of complete, unchanged DataCite query prefixes.

    The exact native flow is the source preimage. A candidate receipt is ignored
    when a newer accepted completion exists or its query plan changed. A current
    v2 receipt with an uncertain checkpoint fails before acquisition. Reused
    pages must retain their saved ETags and byte-verification flags.
    """
    result = copy.deepcopy(document)
    props = result.get('properties', {})
    definition = props.get('definition', {})
    actions = definition.get('actions', {})
    fingerprint = hashlib.sha256(json.dumps(
        definition, sort_keys=True, separators=(',', ':'), ensure_ascii=False
    ).encode()).hexdigest()
    expected_flow = '/providers/Microsoft.Flow/environments/Default-0b65b008-95d7-4abc-bafc-3ffc20c039c0/flows/47f4378d-a752-49be-ab6b-a8b4491a574a'
    if (fingerprint != expected_definition_sha256
            or not re.fullmatch(r'[0-9a-f]{64}', expected_definition_sha256 or '')):
        raise ValueError('Definition drift; reconcile before automatic recovery repair')
    if (result.get('id') != expected_flow or props.get('state') != 'Stopped'
            or props.get('isManaged') is not False
            or set(definition.get('triggers', {})) != {'Recurrence'}
            or len(actions) != 50):
        raise ValueError('Exact stopped unmanaged DataCite weekly preimage required')
    failure = actions.get('Observe_failed_generation', {}).get('actions', {}).get('Failure_receipt', {}).get('inputs', {})
    page = actions.get('For_each_query', {}).get('actions', {}).get('Query_may_run', {}).get('actions', {}).get('Until_complete', {}).get('actions', {})
    checkpoint_uri = actions.get('Find_checkpoint', {}).get('inputs', {}).get('parameters', {}).get('parameters/uri', '')
    if (failure.get('format') != 'rims-datacite-failure-v2'
            or failure.get('recovery_protocol') != 1
            or 'planned_queries' not in failure
            or not checkpoint_uri.endswith('$select=Name,ETag,TimeCreated')
            or not {'Read_page_metadata', 'Guard_page_metadata'}.issubset(page)
            or not page.get('Page_receipt', {}).get('inputs', {}).get('value', {}).get('etag')):
        raise ValueError('Native v2 checkpoint and page provenance required')
    if any(name in actions for name in (
            'Find_failure_receipt', 'Has_failure_receipt', 'Consider_recovery',
            'Qualify_recovery_prefix', 'For_each_recovery_query')):
        raise ValueError('Automatic recovery reader already present; reconcile exact graph')

    def setvar(name, value, previous=None):
        return {'type': 'SetVariable', 'inputs': {'name': name, 'value': value},
                'runAfter': {previous: ['Succeeded']} if previous else {}}

    def compose(value, previous=None):
        return {'type': 'Compose', 'inputs': value,
                'runAfter': {previous: ['Succeeded']} if previous else {}}

    def guard(condition, previous=None, code='DATACITE_RECOVERY_REJECTED'):
        return compose('@if(' + condition + ",true,json('" + code + "'))", previous)

    # Read only the newest receipt. Its creation time is compared with the
    # latest accepted checkpoint before any source request can begin.
    find = copy.deepcopy(actions['Find_checkpoint'])
    find['runAfter'] = {'Cutoff': ['Succeeded']}
    find['inputs'].pop('authentication', None)
    uri = find['inputs']['parameters']['parameters/uri']
    if "startswith(Name,'datacite-discovery-complete-')" not in uri:
        raise ValueError('Completion listing drift; reconcile before recovery edit')
    uri = uri.replace("startswith(Name,'datacite-discovery-complete-')",
                      "startswith(Name,'datacite-failed-')")
    uri = uri.replace('$select=Name,ETag,TimeCreated', '$select=Name,TimeCreated')
    find['inputs']['parameters']['parameters/uri'] = uri
    actions['Find_failure_receipt'] = find

    initialize = actions['Initialize']
    if initialize.get('runAfter') != {'Find_checkpoint': ['Succeeded']}:
        raise ValueError('Initialization dependencies drifted')
    initialize['runAfter'] = {
        'Find_checkpoint': ['Succeeded'],
        'Find_failure_receipt': ['Succeeded']}
    variables = initialize['inputs']['variables']
    existing = {v.get('name') for v in variables}
    additions = [
        {'name': 'RecoveryReceipt', 'type': 'object', 'value': {}},
        {'name': 'RecoveryPrefix', 'type': 'array', 'value': []},
        {'name': 'RecoveryCutoff', 'type': 'string', 'value': "@outputs('Cutoff')"},
        {'name': 'RecoveryFull', 'type': 'boolean', 'value': False},
        {'name': 'RecoveryCandidate', 'type': 'boolean', 'value': False},
        {'name': 'CompletedKeys', 'type': 'array', 'value': []},
        {'name': 'CurrentRecoveryQuery', 'type': 'object', 'value': {}},
        {'name': 'CurrentPlanQuery', 'type': 'object', 'value': {}},
        {'name': 'PrefixPageRows', 'type': 'integer', 'value': 0},
    ]
    if existing.intersection(v['name'] for v in additions):
        raise ValueError('Recovery variables already exist; reconcile exact graph')
    variables.extend(additions)

    parent_path = actions['Has_checkpoint']['actions']['Read_checkpoint']['inputs']['parameters']['path']
    parent_path = parent_path.replace("body('Find_checkpoint')", "body('Find_failure_receipt')")
    parent_path = parent_path.replace("?['Name'])", "?['Name'])")
    read_failure = copy.deepcopy(actions['Has_checkpoint']['actions']['Read_checkpoint'])
    read_failure['inputs'].pop('authentication', None)
    read_failure['inputs']['parameters']['path'] = parent_path
    parse_failure = setvar('RecoveryReceipt',
        "@json(base64ToString(body('Read_auto_failure_receipt')?['$content']))",
        'Read_auto_failure_receipt')
    actions['Has_failure_receipt'] = {
        'type': 'If',
        'expression': "@not(empty(body('Find_failure_receipt')?['value']))",
        'runAfter': {'Initialize': ['Succeeded']},
        'actions': {'Read_auto_failure_receipt': read_failure,
                    'Parse_auto_failure_receipt': parse_failure},
        'else': {'actions': {}}}

    # Establish normal-run defaults before considering any recovery receipt.
    actions['Set_recovery_defaults'] = setvar('RecoveryFull',
        "@outputs('Full_reconciliation')", 'Full_reconciliation')
    actions['Set_recovery_default_cutoff'] = setvar('RecoveryCutoff',
        "@outputs('Cutoff')", 'Set_recovery_defaults')
    scope_expr = "equals(variables('RecoveryReceipt')?['scope_sha256'],outputs('Scope')?['scope_sha256'])"
    newer_receipt = "greater(ticks(coalesce(first(body('Find_failure_receipt')?['value'])?['TimeCreated'],'1900-01-01T00:00:00Z')),ticks(coalesce(first(body('Find_checkpoint')?['value'])?['TimeCreated'],'1900-01-01T00:00:00Z')))"
    receipt_run_name = "equals(first(body('Find_failure_receipt')?['value'])?['Name'],concat('datacite-failed-',variables('RecoveryReceipt')?['capture_run'],'.json'))"
    recent_v2 = "and(not(empty(body('Find_failure_receipt')?['value'])),equals(variables('RecoveryReceipt')?['format'],'rims-datacite-failure-v2'),equals(variables('RecoveryReceipt')?['recovery_protocol'],1),equals(variables('RecoveryReceipt')?['source'],'datacite')," + scope_expr + "," + receipt_run_name + "," + newer_receipt + ")"
    actions['Guard_recovery_completion_disposition'] = guard(
        'or(not(' + recent_v2 + '),and(equals(variables(\'RecoveryReceipt\')?[\'completion_write\'],\'Skipped\'),equals(variables(\'RecoveryReceipt\')?[\'completion_readback\'],\'Skipped\')))',
        'Set_recovery_default_cutoff', 'DATACITE_RECOVERY_UNCERTAIN_COMPLETION')
    checkpoint_fields = ('source', 'complete', 'scope_sha256', 'until',
                         'baseline_completed_at', 'capture_run', 'archive_folder')
    exact_checkpoint = [
        "equals(variables('RecoveryReceipt')?['previous_checkpoint']?['file'],first(body('Find_checkpoint')?['value'])?['Name'])",
        "equals(variables('RecoveryReceipt')?['previous_checkpoint']?['etag'],first(body('Find_checkpoint')?['value'])?['ETag'])",
    ]
    exact_checkpoint.extend(
        "equals(variables('RecoveryReceipt')?['previous_checkpoint']?['" + k + "'],variables('Checkpoint')?['" + k + "'])"
        for k in checkpoint_fields)
    no_checkpoint = "and(empty(variables('RecoveryReceipt')?['previous_checkpoint']?['file']),empty(body('Find_checkpoint')?['value']),empty(variables('Checkpoint')))"
    checkpoint_match = (
        "or(" + no_checkpoint
        + ",and(not(empty(variables('RecoveryReceipt')?['previous_checkpoint']?['file'])),"
        + "not(empty(body('Find_checkpoint')?['value'])),"
        + ','.join(exact_checkpoint) + '))')
    actions['Guard_recovery_checkpoint_identity'] = guard(
        'or(not(' + recent_v2 + '),' + checkpoint_match + ')',
        'Guard_recovery_completion_disposition', 'DATACITE_RECOVERY_CHECKPOINT_DRIFT')

    set_prefix = setvar('RecoveryPrefix',
        "@if(" + recent_v2 + ",coalesce(variables('RecoveryReceipt')?['complete_query_prefix'],json('[]')),json('[]'))",
        None)
    set_cutoff = setvar('RecoveryCutoff',
        "@if(" + recent_v2 + ",variables('RecoveryReceipt')?['until'],outputs('Cutoff'))",
        'Set_recovery_prefix')
    set_full = setvar('RecoveryFull',
        "@if(" + recent_v2 + ",variables('RecoveryReceipt')?['full_reconciliation'],outputs('Full_reconciliation'))",
        'Set_recovery_cutoff')
    set_candidate = setvar('RecoveryCandidate', '@' + recent_v2, 'Set_recovery_full')
    actions['Consider_recovery'] = {
        'type': 'Scope',
        'runAfter': {
            'Has_failure_receipt': ['Succeeded'],
            'Set_recovery_default_cutoff': ['Succeeded'],
            'Guard_recovery_checkpoint_identity': ['Succeeded']},
        'actions': {
            'Set_recovery_prefix': set_prefix,
            'Set_recovery_cutoff': set_cutoff,
            'Set_recovery_full': set_full,
            'Set_recovery_candidate': set_candidate}}

    # Compare the evaluated dynamic DOI query plan, including related DOI
    # batches, with the exact plan frozen in the failed run receipt.
    select_prefix = {
        'type': 'Select', 'runAfter': {'For_each_doi_batch': ['Succeeded']},
        'inputs': {'from': "@coalesce(variables('RecoveryPrefix'),json('[]'))",
                   'select': {'key': "@item()?['key']", 'kind': "@item()?['kind']"}}}
    select_planned = {
        'type': 'Select', 'runAfter': {'Select_recovery_prefix_identity': ['Succeeded']},
        'inputs': {'from': "@take(variables('Queries'),length(variables('RecoveryPrefix'))) ",
                   'select': {'key': "@item()?['key']", 'kind': "@item()?['kind']"}}}
    actions['Select_recovery_prefix_identity'] = select_prefix
    actions['Select_current_prefix_identity'] = select_planned
    actions['Recovery_plan_matches'] = compose(
        "@and(variables('RecoveryCandidate'),equals(string(variables('Queries')),string(variables('RecoveryReceipt')?['planned_queries'])),lessOrEquals(length(variables('RecoveryPrefix')),length(variables('Queries'))),equals(string(body('Select_recovery_prefix_identity')),string(body('Select_current_prefix_identity'))))",
        'Select_current_prefix_identity')

    # Sequential ETag verification. The current query/page variables are safe
    # because both loops are explicitly serial.
    query_actions = {
        'Set_current_recovery_query': setvar('CurrentRecoveryQuery',
            "@first(skip(variables('RecoveryPrefix'),items('For_each_recovery_query')))"),
        'Set_current_plan_query': setvar('CurrentPlanQuery',
            "@first(skip(variables('Queries'),items('For_each_recovery_query')))",
            'Set_current_recovery_query'),
    }
    query_window = actions['For_each_query']['actions']['Query_may_run']['actions']['Query_with_window']['inputs']
    expected_query = query_window.replace("items('For_each_query')?['query']", "variables('CurrentPlanQuery')?['query']")
    expected_query = expected_query.replace("items('For_each_query')?['kind']", "variables('CurrentPlanQuery')?['kind']")
    expected_query = expected_query.replace("outputs('Full_reconciliation')", "variables('RecoveryFull')")
    expected_query = expected_query.replace("outputs('Cutoff')", "variables('RecoveryCutoff')")
    query_actions['Expected_recovery_query'] = compose(expected_query,
        'Set_current_plan_query')
    run_folder_input = actions['Run_folder'].get('inputs', '')
    run_marker = 'datacite-discovery-'
    if run_marker not in run_folder_input or "@concat('" not in run_folder_input:
        raise ValueError('Qualified DataCite run folder expression required')
    archive_parent = run_folder_input.split(run_marker, 1)[0].split("@concat('", 1)[1]
    expected_archive = "concat('" + archive_parent + run_marker + "',variables('RecoveryReceipt')?['capture_run'])"
    valid_query = "and(equals(variables('CurrentRecoveryQuery')?['key'],variables('CurrentPlanQuery')?['key']),equals(variables('CurrentRecoveryQuery')?['kind'],variables('CurrentPlanQuery')?['kind']),equals(variables('CurrentRecoveryQuery')?['complete'],true),equals(variables('CurrentRecoveryQuery')?['scope_sha256'],outputs('Scope')?['scope_sha256']),equals(variables('CurrentRecoveryQuery')?['query'],outputs('Expected_recovery_query')),equals(variables('CurrentRecoveryQuery')?['provider_total'],variables('CurrentRecoveryQuery')?['received']),equals(variables('CurrentRecoveryQuery')?['received'],variables('CurrentRecoveryQuery')?['unique_dois']),greaterOrEquals(coalesce(variables('CurrentRecoveryQuery')?['received'],-1),0),not(empty(variables('CurrentRecoveryQuery')?['pages'])),equals(variables('CurrentRecoveryQuery')?['archive_folder'],variables('RecoveryReceipt')?['archive_folder']),equals(variables('CurrentRecoveryQuery')?['archive_folder']," + expected_archive + "),startsWith(variables('CurrentRecoveryQuery')?['archive_folder'],'/Documents/'),not(contains(variables('CurrentRecoveryQuery')?['archive_folder'],'..')))"
    query_actions['Guard_recovery_query'] = guard(valid_query,
        'Expected_recovery_query', 'DATACITE_RECOVERY_QUERY_INVALID')
    query_actions['Reset_prefix_page_rows'] = setvar('PrefixPageRows', 0,
        'Guard_recovery_query')
    page_read = copy.deepcopy(page['Read_page_metadata'])
    page_read['inputs'].pop('authentication', None)
    page_read['runAfter'] = {'Guard_recovery_page': ['Succeeded']}
    page_read['inputs']['parameters']['path'] = "@concat(variables('CurrentRecoveryQuery')?['archive_folder'],'/',outputs('Current_recovery_page')?['file'])"
    page_actions = {
        'Current_recovery_page': compose("@first(skip(variables('CurrentRecoveryQuery')?['pages'],items('For_each_recovery_page')))"),
    }
    valid_page = "and(equals(outputs('Current_recovery_page')?['file'],concat(variables('CurrentRecoveryQuery')?['key'],'-page-',string(items('For_each_recovery_page')),'.json')),equals(outputs('Current_recovery_page')?['saved_content_equal'],true),not(empty(outputs('Current_recovery_page')?['etag'])),equals(outputs('Current_recovery_page')?['archive_folder'],variables('CurrentRecoveryQuery')?['archive_folder']),greaterOrEquals(coalesce(outputs('Current_recovery_page')?['rows'],-1),0),if(equals(items('For_each_recovery_page'),sub(length(variables('CurrentRecoveryQuery')?['pages']),1)),lessOrEquals(outputs('Current_recovery_page')?['rows'],250),equals(outputs('Current_recovery_page')?['rows'],250)))"
    page_actions['Guard_recovery_page'] = guard(valid_page,
        'Current_recovery_page', 'DATACITE_RECOVERY_PAGE_INVALID')
    page_actions['Read_recovery_page_metadata'] = page_read
    page_actions['Guard_recovery_page_etag'] = guard(
        "equals(outputs('Read_recovery_page_metadata')?['body']?['ETag'],outputs('Current_recovery_page')?['etag'])",
        'Read_recovery_page_metadata', 'DATACITE_RECOVERY_PAGE_ETAG_DRIFT')
    page_actions['Add_prefix_page_rows'] = {
        'type': 'IncrementVariable',
        'runAfter': {'Guard_recovery_page_etag': ['Succeeded']},
        'inputs': {'name': 'PrefixPageRows', 'value': "@outputs('Current_recovery_page')?['rows']"}}
    query_actions['For_each_recovery_page'] = {
        'type': 'Foreach', 'foreach': "@range(0,length(variables('CurrentRecoveryQuery')?['pages']))",
        'runAfter': {'Reset_prefix_page_rows': ['Succeeded']},
        'runtimeConfiguration': {'concurrency': {'repetitions': 1}},
        'actions': page_actions}
    query_actions['Guard_recovery_page_total'] = guard(
        "and(equals(variables('PrefixPageRows'),variables('CurrentRecoveryQuery')?['received']),equals(variables('CurrentRecoveryQuery')?['received'],variables('CurrentRecoveryQuery')?['provider_total']),equals(variables('CurrentRecoveryQuery')?['received'],variables('CurrentRecoveryQuery')?['unique_dois']))",
        'For_each_recovery_page', 'DATACITE_RECOVERY_PAGE_TOTAL_MISMATCH')
    recovery_queries = {
        'type': 'Foreach', 'foreach': "@range(0,length(variables('RecoveryPrefix'))) ",
        'runAfter': {'Guard_recovery_prefix_order': ['Succeeded']},
        'runtimeConfiguration': {'concurrency': {'repetitions': 1}},
        'actions': query_actions}

    valid_prefix_order = "equals(string(body('Select_recovery_prefix_identity')),string(body('Select_current_prefix_identity')))"
    actions['Qualify_recovery_prefix'] = {
        'type': 'If', 'expression': "@outputs('Recovery_plan_matches')",
        'runAfter': {'Recovery_plan_matches': ['Succeeded']},
        'actions': {
            'Guard_recovery_prefix_order': guard(valid_prefix_order,
                code='DATACITE_RECOVERY_PREFIX_ORDER_INVALID'),
            'For_each_recovery_query': recovery_queries,
            'Set_recovery_completions': setvar('Completions',
                "@variables('RecoveryPrefix')", 'For_each_recovery_query')},
        'else': {'actions': {
            'Reset_recovery_candidate': setvar('RecoveryCandidate', False),
            'Reset_recovery_prefix': setvar('RecoveryPrefix', [], 'Reset_recovery_candidate'),
            'Reset_recovery_cutoff': setvar('RecoveryCutoff', "@outputs('Cutoff')", 'Reset_recovery_prefix'),
            'Reset_recovery_full': setvar('RecoveryFull', "@outputs('Full_reconciliation')", 'Reset_recovery_cutoff'),
            'Reset_completions': setvar('Completions', [], 'Reset_recovery_full')}}}

    actions['Select_completed_query_keys'] = {
        'type': 'Select', 'runAfter': {'Qualify_recovery_prefix': ['Succeeded']},
        'inputs': {'from': "@variables('Completions')", 'select': "@item()?['key']"}}
    actions['Set_completed_query_keys'] = setvar('CompletedKeys',
        "@body('Select_completed_query_keys')", 'Select_completed_query_keys')

    # A recovered complete-query prefix must carry the exact acquisition scope
    # that produced it. Without this field, the reader's scope guard can never
    # accept a genuine summary written by this same graph.
    query_summary = actions['For_each_query']['actions']['Query_may_run']['actions'].get('Query_summary')
    if not isinstance(query_summary, dict) or not isinstance(query_summary.get('inputs'), dict):
        raise ValueError('Native complete-query summary action required')
    query_summary['inputs']['scope_sha256'] = "@outputs('Scope')?['scope_sha256']"

    # Reused complete-query summaries are pre-seeded; only remaining queries run.
    actions['For_each_query']['actions']['Query_may_run']['expression'] = (
        "@and(not(variables('Failed')),not(contains(variables('CompletedKeys'),items('For_each_query')?['key'])))")
    actions['Run_folder']['runAfter'] = {'Set_completed_query_keys': ['Succeeded']}
    actions['Manifest']['inputs']['until'] = "@variables('RecoveryCutoff')"
    actions['Manifest']['inputs']['full_reconciliation'] = "@variables('RecoveryFull')"
    actions['Manifest']['inputs']['baseline_completed_at'] = (
        "@if(variables('RecoveryFull'),variables('RecoveryCutoff'),variables('Checkpoint')?['baseline_completed_at'])")
    failure['until'] = "@variables('RecoveryCutoff')"
    failure['full_reconciliation'] = "@variables('RecoveryFull')"
    # Make receipt generation wait for the new variables and fail-closed reader.
    actions['For_each_doi_batch']['runAfter'] = {
        'Quoted_dois': ['Succeeded'], 'Consider_recovery': ['Succeeded']}
    actions['Full_reconciliation']['runAfter'] = {'Has_checkpoint': ['Succeeded']}
    return result


def prepare_query_continuation(document, receipt, *, expected_definition_sha256):
    """Prepare manual recovery from a verified complete DataCite query prefix.

    Complete queries keep immutable archive pointers. An interrupted query is
    always reset to provider cursor 1; cursors are never reused across runs.
    """
    result = copy.deepcopy(document)
    evidence = copy.deepcopy(receipt)
    try:
        props = result['properties']
        definition = props['definition']
        fingerprint = hashlib.sha256(json.dumps(
            definition, sort_keys=True, separators=(',', ':'), ensure_ascii=False
        ).encode()).hexdigest()
        if fingerprint != expected_definition_sha256 or not re.fullmatch(
                r'[0-9a-f]{64}', expected_definition_sha256 or ''):
            raise ValueError('Definition drift; reconcile before recovery')
        triggers = definition['triggers']
        if (props.get('state') != 'Stopped' or props.get('isManaged') is True
                or set(triggers) != {'manual'} or triggers['manual'].get('type') != 'Request'
                or triggers['manual'].get('kind') != 'Button'):
            raise ValueError('Stopped unmanaged manual-only preimage required')
        actions = definition['actions']
        scope = actions['Scope']['inputs']
        manifest = actions['Manifest']['inputs']
        if (scope.get('policy', {}).get('source') != 'datacite'
                or manifest.get('format') != 'rims-datacite-discovery-v1'
                or any(k in manifest for k in ('recovery', 'extension'))):
            raise ValueError('Normal qualified DataCite collector required')
        if (evidence.get('status') != 'VERIFIED_FAILED_DATACITE_RECOVERY_INPUTS'
                or evidence.get('source_terminal_status') not in {'Failed', 'TimedOut', 'Cancelled'}
                or evidence.get('scope_sha256') != scope.get('scope_sha256')):
            raise ValueError('Verified terminal failed-run evidence for this exact scope required')
        source_run = evidence.get('source_run')
        if not isinstance(source_run, str) or not re.fullmatch(r'[A-Za-z0-9_-]+', source_run):
            raise ValueError('Exact source run required')
        parent = evidence.get('archive_parent')
        source_folder = evidence.get('archive_folder')
        if (not isinstance(parent, str) or not parent.startswith('/Documents/')
                or '..' in parent.split('/')
                or source_folder != parent + '/datacite-discovery-' + source_run):
            raise ValueError('Failed run archive must match the selected DataCite collector')
        cutoff = evidence.get('until')
        parsed_cutoff = datetime.fromisoformat(cutoff.replace('Z', '+00:00'))
        if parsed_cutoff.utcoffset() is None or not cutoff.endswith('Z'):
            raise ValueError('Original UTC source cutoff required')
        full = evidence.get('full_reconciliation')
        if type(full) is not bool:
            raise ValueError('Explicit original full/delta mode required')
        if not full:
            checkpoint = evidence.get('previous_checkpoint', {})
            if (checkpoint.get('source') != 'datacite' or checkpoint.get('complete') is not True
                    or checkpoint.get('scope_sha256') != scope['scope_sha256']
                    or checkpoint.get('until') != evidence.get('previous_until')
                    or checkpoint.get('baseline_completed_at') != evidence.get('baseline_completed_at')):
                raise ValueError('Verified last-good DataCite checkpoint required')
            old_until = datetime.fromisoformat(checkpoint['until'].replace('Z', '+00:00'))
            baseline = datetime.fromisoformat(checkpoint['baseline_completed_at'].replace('Z', '+00:00'))
            if (old_until.utcoffset() is None or baseline.utcoffset() is None
                    or not checkpoint['until'].endswith('Z')
                    or not checkpoint['baseline_completed_at'].endswith('Z')
                    or not baseline <= old_until <= parsed_cutoff):
                raise ValueError('Original checkpoint chronology required')
            for field in ('until', 'baseline_completed_at'):
                value = checkpoint[field]
                if "'" in value:
                    raise ValueError('Checkpoint identity cannot be safely encoded')
        checkpoint = evidence.get('previous_checkpoint')
        if checkpoint is not None:
            if (checkpoint.get('source') != 'datacite' or checkpoint.get('complete') is not True
                    or checkpoint.get('until') != evidence.get('previous_until')
                    or checkpoint.get('baseline_completed_at') != evidence.get('baseline_completed_at')):
                raise ValueError('Exact pre-run checkpoint identity required')
            checks = [
                "equals(variables('Checkpoint')?['source'],'datacite')",
                "equals(variables('Checkpoint')?['complete'],true)",
            ]
            for field in ('scope_sha256', 'until', 'baseline_completed_at', 'capture_run', 'archive_folder'):
                value = checkpoint.get(field)
                if value is not None:
                    if not isinstance(value, str) or "'" in value:
                        raise ValueError('Checkpoint identity cannot be safely encoded')
                    checks.append("equals(variables('Checkpoint')?['" + field + "'],'" + value + "')")
            checkpoint_guard = '@if(and(' + ','.join(checks) + "),true,json('DATACITE_RECOVERY_CHECKPOINT_DRIFT'))"
        else:
            if not evidence.get('checkpoint_absent'):
                raise ValueError('Exact prior checkpoint or verified absence required')
            checkpoint_guard = "@if(empty(variables('Checkpoint')),true,json('DATACITE_RECOVERY_CHECKPOINT_APPEARED'))"
        actions['Guard_recovery_checkpoint'] = {
            'type': 'Compose', 'runAfter': {'Has_checkpoint': ['Succeeded']},
            'inputs': checkpoint_guard}
        queries = evidence.get('queries')
        planned = scope['institutional_queries']
        keys = [q['key'] for q in planned]
        if (not isinstance(queries, list) or not 0 < len(queries) < len(keys)
                or [q.get('key') for q in queries] != keys[:len(queries)]):
            raise ValueError('A consecutive complete-query prefix is required')
        page_count = 0
        for expected, query in zip(planned, queries):
            if (query.get('complete') is not True or query.get('kind') != expected['kind']
                    or query.get('scope_sha256') != scope['scope_sha256']
                    or any(type(query.get(k)) is not int or query[k] < 0
                           for k in ('provider_total', 'received', 'unique_dois'))
                    or not query['provider_total'] == query['received'] == query['unique_dois']):
                raise ValueError('Only complete same-scope query archives can be reused')
            pages = query.get('pages')
            if not isinstance(pages, list) or not pages:
                raise ValueError('Independent page readbacks required, including empty query pages')
            for index, page in enumerate(pages):
                if (page.get('file') != query['key'] + '-page-' + str(index) + '.json'
                        or page.get('saved_content_equal') is not True
                        or type(page.get('rows')) is not int or page['rows'] < 0
                        or not re.fullmatch(r'[0-9a-f]{64}', page.get('sha256', ''))
                        or (index < len(pages) - 1 and page['rows'] != 250)):
                    raise ValueError('Exact contiguous DataCite page readbacks required')
            if (pages[-1]['rows'] > 250
                    or sum(p['rows'] for p in pages) != query['received']):
                raise ValueError('Complete terminal page and reconciled row count required')
            query['archive_folder'] = source_folder
            page_count += len(pages)
        if evidence.get('saved_page_readback_count') != page_count:
            raise ValueError('Independent saved-page readback coverage required')

        variables = actions['Initialize']['inputs']['variables']
        query_var = next(v for v in variables if v['name'] == 'Queries')
        query_var['value'] = copy.deepcopy(queries) + copy.deepcopy(planned[len(queries):])
        completion_var = next(v for v in variables if v['name'] == 'Completions')
        completion_var['value'] = copy.deepcopy(queries)
        loop = actions['For_each_query']['actions']['Query_may_run']
        if loop['expression'] != "@not(variables('Failed'))":
            raise ValueError('Existing DataCite query failure gate changed')
        if actions['For_each_query']['runtimeConfiguration']['concurrency']['repetitions'] != 1:
            raise ValueError('Serial query processing required')
        loop['expression'] = ("@and(not(variables('Failed')),not(contains(json('"
                              + json.dumps(keys[:len(queries)], separators=(',', ':'))
                              + "'),items('For_each_query')?['key'])))")
        if actions['Full_reconciliation']['runAfter'] != {'Has_checkpoint': ['Succeeded']}:
            raise ValueError('Normal DataCite checkpoint dependency changed')
        actions['Full_reconciliation']['runAfter'] = {'Guard_recovery_checkpoint': ['Succeeded']}
        actions['Cutoff']['inputs'] = cutoff
        actions['Full_reconciliation']['inputs'] = full
        manifest['recovery'] = {'kind': 'verified_complete_query_prefix',
            'source_run': source_run, 'archive_folder': source_folder,
            'reused_queries': len(queries), 'incomplete_query_cursor_reused': False,
            'full_reconciliation': full, 'until': cutoff}
    except (KeyError, TypeError, AttributeError, OverflowError) as error:
        raise ValueError('Incomplete or unexpected DataCite recovery input') from error
    return result
