"""Stream frozen native pages through the existing archive, without payload literals.

Local artifact preparation only. Exact native preflight and captured stored-byte
acceptance are required before the collector may advance its frozen generation.
"""
import copy
import hashlib
import json
import re
from datetime import datetime, timezone

from prepare_openalex_archive_stage import encode


def build(native, capture, prepared, acceptance, batch_id, *, stage_only=True,
          raw_only=False, definition_sha=None, replace_branch_sha=None,
          pending_acceptance=None, raw_acceptance=None):
    if raw_only and not stage_only:
        raise ValueError('Raw-only storage cannot admit a consumer commit')
    if not stage_only:
        if not pending_acceptance or not raw_acceptance:
            raise ValueError('Exact pending-envelope and raw-storage acceptance required')
        for receipt in (pending_acceptance, raw_acceptance):
            if receipt.get('source_input_sha256') != prepared['input_sha256'] or receipt.get('prepared_sha256') != hashlib.sha256(encode(prepared)).hexdigest():
                raise ValueError('Acceptance must fingerprint this exact prepared generation')
            if receipt.get('raw_refresh_request_id') != acceptance['refresh_request_id']:
                raise ValueError('Acceptance generation drift')
        if (pending_acceptance.get('status') != 'PASS_PENDING_ONLY' or
                pending_acceptance.get('native_chunks_envelope_bytes_sha_exact') is not True or
                pending_acceptance.get('recursive_schema_original_utc_exact') is not True or
                pending_acceptance.get('raw_producer_unchanged') is not True or
                pending_acceptance.get('old_five_tables_all_values_preserved') is not True or
                raw_acceptance.get('status') != 'PASS' or
                raw_acceptance.get('native_stage_marker_exact') is not True or
                raw_acceptance.get('raw_native_readback_verified') is not True):
            raise ValueError('Native pending parity and durable raw storage required')
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,95}', batch_id):
        raise ValueError('Safe immutable batch identity required')
    if acceptance.get('scope') != 1:
        raise ValueError('Qualify pending native envelope staging before expanding the streamed trial scope')
    if acceptance.get('status') != 'PASS_CAPTURE_ONLY' or capture.get('http') != 200:
        raise ValueError('Accepted complete frozen native capture required')
    rows = capture['body']['results'][0]['tables'][0]['rows']
    def normalized(row):
        return {f'[{key[key.rfind("[")+1:-1]}]': value for key, value in row.items()}
    raw = [normalized(row) for row in rows]
    if not raw or len({(r['[RawResponseIndex]'], r['[RawChunkIndex]']) for r in raw}) != len(raw):
        raise ValueError('Unique complete raw chunk keys required')
    raw.sort(key=lambda r: (r['[RawResponseIndex]'], r['[RawChunkIndex]']))
    metadata = [{f'[{key}]': value for key, value in r.items()} for r in prepared['chunks']]
    metadata.sort(key=lambda r: (r['[OpenAlexWorkID]'], r['[ChunkIndex]']))
    descriptors, files = [], {}
    page_specs = [
        ('OpenAlexRawAcquisition', raw, ['RawResponseIndex', 'RawChunkIndex'], ['RawPayloadBase64', 'RawSchemaBase64']),
        ('OpenAlexMetadataChunks', metadata, ['OpenAlexWorkID', 'ChunkIndex'], ['MetadataChunk']),
    ]
    if raw_only:
        page_specs = page_specs[:1]
    for logical_table, page_rows, keys, payload_columns in page_specs:
        table = ('OpenAlexPendingEnvelopeChunks' if not stage_only and logical_table == 'OpenAlexMetadataChunks' else logical_table)
        if not page_rows:
            continue
        columns = [key[1:-1] for key in page_rows[0]]
        for offset in range(0, len(page_rows), 2):
            page = page_rows[offset:offset+2]
            predicate = ' || '.join('('+' && '.join(table+'['+key+']='+json.dumps(row['['+key+']']) for key in keys)+')' for row in page)
            def projection(selected):
                return ','.join(json.dumps(col)+','+('"source-utc:" &' if col == 'RawAcquiredUTC' else '')+table+'['+col+']' for col in selected)
            order = ','.join('['+key+']' for key in keys)
            headers = [col for col in columns if col not in payload_columns]
            expected = [{key: ('source-utc:'+value if key == '[RawAcquiredUTC]' else value)
                         for key,value in row.items() if key[1:-1] in headers} for row in page]
            name = f'uncommitted-{batch_id}-{logical_table}-{offset//2}.json'
            content = encode(page); files[name] = content
            descriptors.append({'name':name, 'query':'EVALUATE SELECTCOLUMNS(FILTER('+table+','+predicate+'),'+projection(columns)+') ORDER BY '+order,
                                'header_query':'EVALUATE SELECTCOLUMNS(FILTER('+table+','+predicate+'),'+projection(headers)+') ORDER BY '+order,
                                'expected_headers':expected})
    candidate = copy.deepcopy(native)
    graph = candidate['properties']['definition']['actions']
    if 'Condition_OpenAlex_paged_capture' in graph:
        existing = hashlib.sha256(encode(graph['Condition_OpenAlex_paged_capture'])).hexdigest()
        if replace_branch_sha != existing:
            raise ValueError('Exact existing streamed branch fingerprint required for replacement')
    original = graph['Condition_OpenAlex_native_capture']['actions']
    manifest = copy.deepcopy(original['NativeCapture_Acq_expected_manifest']['inputs'])
    if definition_sha is None:
        if raw_only or not stage_only or sorted(prepared['expected_keys']) != sorted(manifest['Sources'][0]['ExpectedKeys']):
            raise ValueError('Current frozen native definition fingerprint required')
        definition_sha = manifest['Provenance']['NativeDefinitionSHA256']
    if not re.fullmatch(r'[0-9a-f]{64}', definition_sha):
        raise ValueError('Exact native definition SHA256 required')
    old_batch = manifest['BatchID']; manifest['BatchID'] = batch_id
    manifest.update(Status='staged' if stage_only else 'committed',
                    Generation=acceptance['refresh_request_id'], RefreshRequestID=acceptance['refresh_request_id'],
                    ObservedAtUTC=datetime.now(timezone.utc).isoformat(),
                    ObservationKind='Frozen native raw storage' if raw_only else 'Frozen native envelope storage')
    manifest['Provenance'] = {'NativeDefinitionSHA256':definition_sha,
        'InputSHA256':prepared['input_sha256'], 'PreparedSHA256':hashlib.sha256(encode(prepared)).hexdigest()}
    manifest['AttemptStatuses'] = copy.deepcopy(prepared['attempt_statuses'])
    metadata_pages = sum('-OpenAlexMetadataChunks-' in name for name in files)
    manifest['Sources'] = ([{'Source':'OpenAlex','ChunkTable':'OpenAlexMetadataChunks',
        'KeyColumn':'OpenAlexWorkID','PageCount':metadata_pages,
        'ExpectedRecords':len(prepared['expected_keys']),'ExpectedKeys':prepared['expected_keys']}]
        if metadata_pages else [])
    manifest['Validation'] = {'Keysets':not raw_only,'Metadata':not raw_only,'RefreshGeneration':True}
    manifest['Files'] = [{'name':name,'rows':len(json.loads(content)), 'bytes':len(content),
                          'sha256':hashlib.sha256(content).hexdigest()} for name,content in files.items()]
    manifest['AcquisitionRaw'] = {'Format':'native-OpenAlexRawAcquisition-query-rows-v1',
        'Files':[entry for entry in manifest['Files'] if '-OpenAlexRawAcquisition-' in entry['name']],
        'AllCapturedAttemptsIncluded':True}
    manifest['PageTransport'] = 'Native fixed-key SELECTCOLUMNS; source-utc prefix removed only from serialized clock property; no payload literals'
    # Clone the proven create-if-absent/readback/commit-last path. Guard each
    # exact page header, then compare complete stored bytes to its native body.
    actions = copy.deepcopy(original)
    actions['NativeCapture_Acq_expected_manifest']['inputs'] = manifest
    actions['NativeCapture_Acq_expected_raw']['inputs'] = 'Streamed page header guards replace inline raw literals'
    actions['NativeCapture_Require_OpenAlex_generation']['inputs'] = 'Frozen generation preflight and serial page guards required'
    del actions['NativeCapture_Acq_read_native_raw']
    actions['NativeCapture_Require_OpenAlex_generation']['runAfter'] = {'NativeCapture_Acq_expected_raw':['Succeeded']}
    actions['NativeCapture_OpenAlex_Page_payloads']['inputs'] = descriptors
    loop = actions['NativeCapture_OpenAlex_Archive_Pages']; nested = loop['actions']
    query = copy.deepcopy(original['NativeCapture_Acq_read_native_raw'])
    query['runAfter'] = {}; query['inputs']['parameters']['specification/query'] = "@items('NativeCapture_OpenAlex_Archive_Pages')['header_query']"
    nested['NativeCapture_Read_page_headers'] = query
    nested['NativeCapture_Require_page_headers'] = {'type':'Compose','runAfter':{'NativeCapture_Read_page_headers':['Succeeded']},
        'inputs':"@if(equals(body('NativeCapture_Read_page_headers')['results'][0]['tables'][0]['rows'],items('NativeCapture_OpenAlex_Archive_Pages')['expected_headers']),'EXACT_FROZEN_HEADERS',int('RAW_GENERATION_DRIFT'))"}
    full = copy.deepcopy(query);full['runAfter'] = {'NativeCapture_Require_page_headers':['Succeeded']}
    full['inputs']['parameters']['specification/query'] = "@items('NativeCapture_OpenAlex_Archive_Pages')['query']"
    nested['NativeCapture_Read_full_page'] = full
    content = "replace(string(body('NativeCapture_Read_full_page')['results'][0]['tables'][0]['rows']),'\"[RawAcquiredUTC]\":\"source-utc:','\"[RawAcquiredUTC]\":\"')"
    header_keys = list(dict.fromkeys(key for descriptor in descriptors for key in descriptor['expected_headers'][0]))
    for descriptor in descriptors:
        descriptor['expected_full_headers'] = [{key:row.get(key) for key in header_keys} for row in descriptor['expected_headers']]
    nested['NativeCapture_Headers_from_full_page'] = {'type':'Select', 'runAfter':{'NativeCapture_Read_full_page':['Succeeded']},
        'inputs':{'from':"@body('NativeCapture_Read_full_page')['results'][0]['tables'][0]['rows']",
                  'select':{key:"@item()?['"+key+"']" for key in header_keys}}}
    nested['NativeCapture_Require_full_page_headers'] = {'type':'Compose', 'runAfter':{'NativeCapture_Headers_from_full_page':['Succeeded']},
        'inputs':"@if(equals(body('NativeCapture_Headers_from_full_page'),items('NativeCapture_OpenAlex_Archive_Pages')['expected_full_headers']),'EXACT_FULL_PAGE_HEADERS',int('RAW_PAGE_DRIFT'))"}
    nested['NativeCapture_OpenAlex_Page_Existing']['runAfter'] = {'NativeCapture_Require_full_page_headers':['Succeeded']}
    nested['NativeCapture_OpenAlex_Page_Exists']['else']['actions']['NativeCapture_OpenAlex_Page_Write']['inputs']['parameters']['body'] = '@'+content
    nested['NativeCapture_Require_OpenAlex_page_exact']['inputs'] = "@if(equals(base64ToString(body('NativeCapture_OpenAlex_Page_Readback')['$content']),"+content+"),'VERIFIED',int('ARCHIVE_CONFLICT'))"
    serialized = json.dumps(actions).replace('commit-'+old_batch+'.json',('stage-' if stage_only else 'commit-')+batch_id+'.json')
    serialized = serialized.replace('NativeCapture_', 'PagedCapture_')
    actions = json.loads(serialized)
    graph['Condition_OpenAlex_paged_capture'] = {'type':'If','runAfter':{},
        'expression':"@equals(json(triggerBody()['text'])['BatchID'],'"+batch_id+"')",'actions':actions,'else':{'actions':{}}}
    graph['Condition_OpenAlex_native_capture']['runAfter'] = {'Condition_OpenAlex_paged_capture':['Succeeded']}
    # The remaining old branch is rollback-only. No other graph/input/ref changes.
    proof = {'kind':'openalex_streamed_page_archive_candidate_v1','native_written':False,
        'pages':len(files),'payload_literals_in_new_branch':False,'serial_pages':True,
        'native_stored_full_bytes_compared':True,'header_clock_text_exact':True,
        'collector_advance_requires_frozen_SHA_readback_acceptance':True,
        'generation_preflight_required':True,'raw_only':raw_only,
        'metadata_query_table':'OpenAlexPendingEnvelopeChunks' if not stage_only else 'OpenAlexMetadataChunks','marker_last':True,'consumer_commit':not stage_only,'absent_only':True,
        'prior_capture_branch_preserved_except_entry_dependency':True}
    return candidate,manifest,files,proof
