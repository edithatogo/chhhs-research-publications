import base64
import gzip
import json
import re
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from build_openalex_native_bootstrap import build, _part, TABLES

class BootstrapPreservation(unittest.TestCase):
    def baseline(self):
        return {'definition':{'format':'TMDL','parts':[
            _part('definition/expressions.tmdl','expression Existing = 1\n'),
            _part('definition/model.tmdl','model Model\n'),
            *[_part('definition/tables/Existing'+str(i)+'.tmdl','unchanged '+str(i)) for i in range(40)]]}}
    def prepared(self):
        return json.dumps({'kind':'openalex_retention_preparation_v1','ready_for_native_stage':True,
            'accepted_commit':False,'expected_keys':['W1'],'chunks':[{'unknown':None,'unicode':'é'}]}).encode()
    def test_lossless_bootstrap_and_existing_parts_unchanged(self):
        base=self.baseline();raw=self.prepared();result,receipt=build(base,raw)
        before={p['path']:p for p in base['definition']['parts']};after={p['path']:p for p in result['definition']['parts']}
        for path in before:
            if path not in receipt['changed_existing_parts']:self.assertEqual(before[path],after[path])
            else:self.assertTrue(base64.b64decode(after[path]['payload']).startswith(base64.b64decode(before[path]['payload'])))
        text=base64.b64decode(after['definition/expressions.tmdl']['payload']).decode()
        encoded=re.search(r'Binary.FromText\("([A-Za-z0-9+/=]+)"',text)[1]
        self.assertEqual(gzip.decompress(base64.b64decode(encoded)),raw)
        self.assertEqual(receipt['provider_calls'],0)
        for table in TABLES:self.assertIn('definition/tables/'+table+'.tmdl',after)
    def test_rejects_wrong_baseline_or_duplicate_stage(self):
        base=self.baseline();base['definition']['parts'].pop()
        with self.assertRaises(ValueError):build(base,self.prepared())
        base=self.baseline();base['definition']['parts'][2]=_part('definition/tables/OpenAlexWorks.tmdl','existing')
        with self.assertRaises(ValueError):build(base,self.prepared())
