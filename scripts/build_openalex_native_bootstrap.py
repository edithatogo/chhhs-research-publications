"""Build an additive native OpenAlex bootstrap from qualified frozen responses.

Local preparation only. Reuses the existing isolated model, complete raw chunk
contract and loaded Publication table; no provider calls/connection changes.
"""
from __future__ import annotations
import argparse
import base64
import copy
import gzip
import hashlib
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TABLES = ('OpenAlexMetadataChunks', 'OpenAlexWorks', 'OpenAlexPublicationContext', 'OpenAlexFieldProvenance')


def _part(path, text):
    return {'path': path, 'payloadType': 'InlineBase64', 'payload': base64.b64encode(text.encode()).decode()}


def _table(name, columns, source, calculated=False):
    lines = [f'table {name}', '\tisHidden', '']
    for column, datatype in columns:
        lines += [f'\tcolumn {column}', f'\t\tdataType: {datatype}', '\t\tsummarizeBy: none',
                  '\t\tsourceColumn: ' + ('['+column+']' if calculated else column), '']
    lines += [f'\tpartition {name} = '+('calculated' if calculated else 'm'), '\t\tmode: import',
              '\t\tsource =', *['\t\t\t\t'+line for line in source.splitlines()], '']
    return '\n'.join(lines)


CONTEXT_DAX = '''
VAR Matched =
    ADDCOLUMNS(
        SELECTCOLUMNS(Publication, "CanonicalKey", Publication[CanonicalKey], "DOI", Publication[DOI]),
        "__DOI", VAR D=LOWER(TRIM([DOI])) RETURN
            IF(LEFT(D,16)="https://doi.org/",MID(D,17,LEN(D)),
            IF(LEFT(D,15)="http://doi.org/",MID(D,16,LEN(D)),
            IF(LEFT(D,19)="https://dx.doi.org/",MID(D,20,LEN(D)),
            IF(LEFT(D,18)="http://dx.doi.org/",MID(D,19,LEN(D)),
            IF(LEFT(D,4)="doi:",TRIM(MID(D,5,LEN(D))),D)))))
    )
VAR Linked = ADDCOLUMNS(Matched,
    "__Work", LOOKUPVALUE(OpenAlexWorks[OpenAlexWorkID],OpenAlexWorks[DOI],[__DOI]),
    "__Count", LOOKUPVALUE(OpenAlexWorks[CitationCount_OpenAlex],OpenAlexWorks[DOI],[__DOI]),
    "__Status", LOOKUPVALUE(OpenAlexWorks[OpenAccessStatus_OpenAlex],OpenAlexWorks[DOI],[__DOI]),
    "__URL", LOOKUPVALUE(OpenAlexWorks[OAUrl_OpenAlex],OpenAlexWorks[DOI],[__DOI]),
    "__At", LOOKUPVALUE(OpenAlexWorks[OpenAlexObservedUTC],OpenAlexWorks[DOI],[__DOI]))
RETURN SELECTCOLUMNS(FILTER(Linked,NOT ISBLANK([__Work])),
    "CanonicalKey",[CanonicalKey],"DOI",[__DOI],"OpenAlexWorkID",[__Work],
    "CitationCount_OpenAlex",[__Count],"OpenAccessStatus_OpenAlex",[__Status],"OAUrl_OpenAlex",[__URL],
    "OpenAlexObservedUTC",[__At],
    "CitationCount_OpenAlex_ObservedUTC",IF(NOT ISBLANK([__Count]),[__At]),
    "OpenAccessStatus_OpenAlex_ObservedUTC",IF(NOT ISBLANK([__Status]),[__At]),
    "OAUrl_OpenAlex_ObservedUTC",IF(NOT ISBLANK([__URL]),[__At]))'''.strip()


def build(baseline, prepared_bytes):
    prepared = json.loads(prepared_bytes)
    if (prepared.get('kind') != 'openalex_retention_preparation_v1'
            or not prepared.get('ready_for_native_stage') or prepared.get('accepted_commit') is not False):
        raise ValueError('Bounded uncommitted OpenAlex preparation required')
    before = baseline.get('definition', {})
    parts = before.get('parts')
    if before.get('format') != 'TMDL' or not isinstance(parts, list) or len(parts) != 42:
        raise ValueError('Transferred exact42-part TMDL baseline required')
    texts = {p['path']: base64.b64decode(p['payload'], validate=True).decode() for p in parts}
    if len(texts) != len(parts) or any(p['payloadType'] != 'InlineBase64' for p in parts):
        raise ValueError('Duplicate or unsupported definition parts')
    expressions = texts['definition/expressions.tmdl']
    names = re.findall(r'^expression (.+?) =', expressions, re.M)
    additions = ['OpenAlexBootstrapDocument','OpenAlexBootstrapObservations','fnProjectRetainedOpenAlex','fnMergeOpenAlexPublicationContext']
    if set(names) & set(additions) or any('definition/tables/'+n+'.tmdl' in texts for n in TABLES):
        raise ValueError('OpenAlex integration already exists; read back instead of duplicating')
    compressed = gzip.compress(prepared_bytes, mtime=0)
    assert gzip.decompress(compressed) == prepared_bytes
    encoded = base64.b64encode(compressed).decode()
    # Full responses/schema survive losslessly; compression avoids repeating
    # provider calls or adding a new storage/credential dependency for bootstrap.
    document_m = f'Json.Document(Binary.Decompress(Binary.FromText("{encoded}",BinaryEncoding.Base64),Compression.GZip))'
    observations_m = '''let
    D=OpenAlexBootstrapDocument,
    Chunks=Table.FromRecords(D[chunks]),
    Raw=fnReconstructMetadata(Chunks,"OpenAlexWorkID"),
    Keys=Raw[SourceID], Expected=D[expected_keys],
    Complete=List.Sort(Keys)=List.Sort(Expected) and List.Count(List.Distinct(Expected))=List.Count(Expected),
    Result=Table.AddColumn(Raw,"Source",each "OpenAlex",type text)
in if Complete then Result else error "OpenAlex bootstrap reconstruction drift"'''
    bodies = {'OpenAlexBootstrapDocument': document_m, 'OpenAlexBootstrapObservations': observations_m,
              'fnProjectRetainedOpenAlex': (ROOT/'powerquery/fnProjectRetainedOpenAlex.m').read_text().strip(),
              'fnMergeOpenAlexPublicationContext': (ROOT/'powerquery/fnMergeOpenAlexPublicationContext.m').read_text().strip()}
    for name, body in bodies.items():
        expressions += '\nexpression '+name+' =\n'+ '\n'.join('\t\t'+line for line in body.splitlines())
        expressions += '\n'
    chunk_columns = [('OpenAlexWorkID','string'),('ChunkIndex','int64'),('ChunkCount','int64'),
                     ('MetadataCharacters','int64'),('Encoding','string'),('MetadataChunk','string')]
    work_columns = [('OpenAlexWorkID','string'),('DOI','string'),('CitationCount_OpenAlex','int64'),
                    ('OpenAccessStatus_OpenAlex','string'),('OAUrl_OpenAlex','string'),('OpenAlexObservedUTC','dateTime')]
    context_columns = [('CanonicalKey','string'),*work_columns,
                       ('CitationCount_OpenAlex_ObservedUTC','dateTime'),
                       ('OpenAccessStatus_OpenAlex_ObservedUTC','dateTime'),('OAUrl_OpenAlex_ObservedUTC','dateTime')]
    provenance_columns = [('CanonicalKey','string'),('DOI','string'),('ProviderWorkID','string'),('Field','string'),
                          ('Source','string'),('IncomingValue','string'),('SelectedValue','string'),
                          ('AttemptObservedUTC','dateTime'),('SelectedObservedUTC','dateTime'),('Decision','string')]
    fields = [('CitationCount_OpenAlex','FORMAT([CitationCount_OpenAlex],"0")'),
              ('OpenAccessStatus_OpenAlex','[OpenAccessStatus_OpenAlex]'),('OAUrl_OpenAlex','[OAUrl_OpenAlex]')]
    branches=[]
    for field, value in fields:
        branches.append('SELECTCOLUMNS(OpenAlexPublicationContext,"CanonicalKey",[CanonicalKey],"DOI",[DOI],'
                        '"ProviderWorkID",[OpenAlexWorkID],"Field","'+field+'","Source","OpenAlex",'
                        '"IncomingValue",'+value+',"SelectedValue",'+value+',"AttemptObservedUTC",[OpenAlexObservedUTC],'
                        '"SelectedObservedUTC",['+field+'_ObservedUTC],"Decision",IF(ISBLANK(['+field+']),"preserve_missing","source_observation"))')
    table_texts = {
        TABLES[0]:_table(TABLES[0],chunk_columns,'Table.FromRecords(OpenAlexBootstrapDocument[chunks])'),
        TABLES[1]:_table(TABLES[1],work_columns,'fnProjectRetainedOpenAlex(OpenAlexBootstrapObservations)'),
        TABLES[2]:_table(TABLES[2],context_columns,CONTEXT_DAX,True),
        TABLES[3]:_table(TABLES[3],provenance_columns,'UNION(\n'+',\n'.join(branches)+'\n)',True)}
    candidate=copy.deepcopy(baseline)
    for p in candidate['definition']['parts']:
        if p['path']=='definition/expressions.tmdl':p.update(_part(p['path'],expressions))
        if p['path']=='definition/model.tmdl':
            p.update(_part(p['path'],texts[p['path']]+'\n'+'\n'.join('ref table '+n for n in TABLES)+'\n'))
    candidate['definition']['parts'] += [_part('definition/tables/'+name+'.tmdl',body) for name,body in table_texts.items()]
    modified=['definition/expressions.tmdl','definition/model.tmdl']
    assert all(p['payload']==next(q['payload'] for q in candidate['definition']['parts'] if q['path']==p['path'])
               for p in parts if p['path'] not in modified)
    receipt={'kind':'openalex_native_bootstrap_candidate_v1','base_parts':42,'candidate_parts':46,
             'changed_existing_parts':modified,'added_tables':list(TABLES),'preserved_existing_parts':40,
             'existing_expression_prefix_preserved':expressions.startswith(texts['definition/expressions.tmdl']),
             'prepared_sha256':hashlib.sha256(prepared_bytes).hexdigest(),'prepared_bytes':len(prepared_bytes),
             'compressed_bytes':len(compressed),'provider_calls':0,'native_acceptance':False,
             'bootstrap_scope':'Frozen3-response source context; no live acquisition/recurrence/Publication write'}
    return candidate, receipt


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--private-root',type=Path,required=True)
    for name in ['baseline','prepared','output','receipt']:p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();root=a.private_root.resolve()
    paths=[getattr(a,n).resolve() for n in ['baseline','prepared','output','receipt']]
    if any(not path.is_relative_to(root) for path in paths):raise ValueError('Private paths required')
    candidate,receipt=build(json.loads(paths[0].read_bytes()),paths[1].read_bytes())
    data=json.dumps(candidate,ensure_ascii=False,separators=(',',':')).encode()
    receipt['candidate_sha256']=hashlib.sha256(data).hexdigest()
    for path,raw in [(paths[2],data),(paths[3],json.dumps(receipt,indent=2).encode())]:
        with os.fdopen(os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'wb') as f:f.write(raw)
    print(json.dumps(receipt))


if __name__=='__main__':main()
