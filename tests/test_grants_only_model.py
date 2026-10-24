import base64
import copy
import unittest
from scripts.prepare_grants_only_model import isolate,fingerprint,TABLE_PATHS


class GrantsOnlyModelTests(unittest.TestCase):
    def setUp(self):
        texts={'definition.pbism':'{}','definition/database.tmdl':'database\n',TABLE_PATHS[0]:"table 'Grants Registry'\n",TABLE_PATHS[1]:"table 'Grants Deadline Occurrences'\n",'definition/relationships.tmdl':"relationship fictional-grants\n\tfromColumn: 'Grants Deadline Occurrences'.OpportunityKey\n\ttoColumn: 'Grants Registry'.OpportunityKey\n\nrelationship fictional-publications\n\tfromColumn: Publication.ID\n\ttoColumn: Other.ID\n",'definition/tables/Publication.tmdl':'table Publication\n','.platform':'preserve outside source deployment'}
        self.d={'format':'TMDL','parts':[{'path':k,'payload':base64.b64encode(v.encode()).decode(),'payloadType':'InlineBase64'} for k,v in texts.items()]}

    def test_exact_grants_parts_reused_without_publication_or_platform(self):
        before=copy.deepcopy(self.d);result=isolate(self.d,expected_sha256=fingerprint(self.d));self.assertEqual(self.d,before)
        self.assertEqual(len(result['parts']),6);paths={p['path'] for p in result['parts']};self.assertNotIn('.platform',paths);self.assertNotIn('definition/tables/Publication.tmdl',paths)
        for path in TABLE_PATHS:self.assertEqual(next(x for x in result['parts'] if x['path']==path),next(x for x in self.d['parts'] if x['path']==path))
        rel=next(x for x in result['parts'] if x['path']=='definition/relationships.tmdl');self.assertNotIn('Publication',base64.b64decode(rel['payload']).decode())

    def test_drift_duplicate_paths_and_missing_relationship_rejected(self):
        with self.assertRaises(ValueError):isolate(self.d,expected_sha256='0'*64)
        self.d['parts'].append(self.d['parts'][0])
        with self.assertRaises(ValueError):isolate(self.d,expected_sha256=fingerprint(self.d))
        self.d['parts'].pop();r=next(x for x in self.d['parts'] if x['path']=='definition/relationships.tmdl');r['payload']=base64.b64encode(b'').decode()
        with self.assertRaises(ValueError):isolate(self.d,expected_sha256=fingerprint(self.d))
