"""Cross-runtime producer contracts; synthetic fixtures never establish native admission."""
import base64
import copy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import unittest

from scripts.grants_registry import normalize_opportunity
from scripts.grants_us_gov_api import prepare_snapshot
from tests import test_grants_import_originals as fixtures

ROOT = Path(__file__).parents[1]
NODE = shutil.which('node')
CAPABLE = bool(NODE and subprocess.run([NODE, '-e', "if(typeof require('node:module').stripTypeScriptTypes!=='function')process.exit(1)"], capture_output=True).returncode == 0)
HARNESS = """const fs=require('node:fs'),vm=require('node:vm'),{stripTypeScriptTypes}=require('node:module');
const c={};vm.runInNewContext(stripTypeScriptTypes(fs.readFileSync(process.argv[1],'utf8')),c);
const i=JSON.parse(fs.readFileSync(0,'utf8'));let o;
try {o=i.operation==='hash'?i.values.map(s=>c.sha256(c.bytes(s))):i.operation==='repr'?i.values.map(s=>c.pyrepr(s)):JSON.parse(c.main(undefined,JSON.stringify(i.payload)));}
catch(e){o={error:e.message};}process.stdout.write(JSON.stringify(o));"""


@unittest.skipUnless(CAPABLE, 'Requires installed Node with built-in TypeScript stripping; native Office Scripts is a separate gate')
class OfficeWorkerTests(unittest.TestCase):
    def run_worker(self, **packet):
        r = subprocess.run([NODE, '-e', HARNESS, str(ROOT/'scripts/office/nih_grants_worker.ts')], input=json.dumps(packet), text=True, capture_output=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        return json.loads(r.stdout)

    def setUp(self):
        f = fixtures.ImportOriginalsTests(); f.setUp()
        schedule=json.loads(f.row['DeadlineScheduleJSON']);schedule['occurrence_count']=7
        schedule['occurrences']=[{**schedule['occurrences'][0], 'occurrence_candidate_id':f'synthetic:{i}', 'due_date':f'2027-0{i+1}-05'} for i in range(7)]
        self.context={'schema':'rims-nih-admitted-context-v1', 'deadline_schedule_json':json.dumps(schedule,sort_keys=True,separators=(',',':')),
            'source_date_facts_json':f.row['SourceDateFactsJSON'], 'source_attribution':f.row['SourceAttribution'],
            'attachment_folders':[], 'attachment_pins':[]}
        self.packet={'context':self.context, 'observed_utc':'2026-10-24T05:00:00.1234567Z',
            'responses':[{'role':role,'http_status':200,'response':json.loads(b),'content_base64':base64.b64encode(b).decode()} for role,b in f.responses.items()], 'attachments':[]}

    def expected(self):
        a=self.packet
        raw=prepare_snapshot(*(e['response'] for e in a['responses']),retrieved_at=a['observed_utc'])['batch']['records'][0]
        raw.update(DeadlineScheduleJSON=self.context['deadline_schedule_json'],SourceDateFactsJSON=self.context['source_date_facts_json'],SourceAttribution=self.context['source_attribution'])
        return normalize_opportunity(raw,retrieved_at=a['observed_utc'])

    def replace_response(self, index, change):
        e=self.packet['responses'][index];change(e['response']);e['content_base64']=base64.b64encode(json.dumps(e['response'],ensure_ascii=False).encode()).decode()

    def test_all_32_fields_and_python_evidence_hash_match(self):
        self.assertEqual(self.run_worker(payload=self.packet)['row'], self.expected())

    def test_sha256_standard_vectors_block_boundaries_and_unicode(self):
        values=['','abc','a'*55,'a'*56,'a'*64,'a'*10000,'é — 🧬','\x00\n\t']
        self.assertEqual(self.run_worker(operation='hash',values=values),[hashlib.sha256(s.encode()).hexdigest() for s in values])

    def test_python_repr_quote_control_and_unicode_rules(self):
        values=['plain',"single'",'double"',"both'\"",'é — 🧬','\n\r\t\x0b\x00','\u00a0\u200b\U000f0000']
        self.assertEqual(self.run_worker(operation='repr',values=values),[repr(s) for s in values])

    def test_changed_title_changes_projection_and_fingerprint(self):
        before=self.run_worker(payload=self.packet)['row']
        for i in [1,3]: self.replace_response(i,lambda d:d['data'].update(opportunityTitle='Changed synthetic title'))
        after=self.run_worker(payload=self.packet)['row'];self.assertEqual(after,self.expected());self.assertNotEqual(after['EvidenceHash'],before['EvidenceHash'])

    def test_reordered_categories_pass_without_rewriting_original_hash(self):
        self.replace_response(3,lambda d:d['data']['synopsis']['applicantTypes'].reverse())
        self.assertEqual(self.run_worker(payload=self.packet)['row'],self.expected())

    def test_incomplete_or_wrong_response_bytes_fail_closed(self):
        self.packet['responses'][0]['content_base64']=base64.b64encode(b'{}').decode()
        self.assertIn('error',self.run_worker(payload=self.packet))
        self.packet['responses'].pop();self.assertEqual(self.run_worker(payload=self.packet)['error'],'NIH_INCOMPLETE_RESPONSES')

    def test_changed_deadline_context_cannot_silently_advance(self):
        for i in [1,3]: self.replace_response(i,lambda d:d['data']['synopsis'].update(responseDateStr='2029-01-01-00-00-00'))
        self.assertEqual(self.run_worker(payload=self.packet)['error'],'NIH_DATE_FACT_CHANGE_REQUIRES_ADMISSION')

    def test_changed_attachment_scope_and_timestamp_reject(self):
        for i in [1,3]: self.replace_response(i,lambda d:d['data'].update(synopsisAttachmentFolders=[{'id':1}]))
        self.assertEqual(self.run_worker(payload=self.packet)['error'],'NIH_ATTACHMENT_SCOPE_CHANGED')
        self.packet['observed_utc']='2026-10-24T05:00:00';self.assertEqual(self.run_worker(payload=self.packet)['error'],'NIH_INVALID_OBSERVATION')

    def test_no_workbook_network_or_delivery_side_effects(self):
        s=(ROOT/'scripts/office/nih_grants_worker.ts').read_text()
        for forbidden in ['workbook.', 'fetch(', 'XMLHttpRequest', 'require(', 'sendMail', '.setValue']:
            self.assertNotIn(forbidden,s)
