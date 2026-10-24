import json
import unittest
from scripts.prepare_disposition_reader import prepare


class ReaderTests(unittest.TestCase):
    def setUp(self):
        self.result={'items':[{'item_id':1,'field':'Authors','source_key':'pubmed:1','retained_value':'A','source_value':'B','disposition':'uncertain_source_difference_preserved'}],'difference_count':1,'record_count':1}
        self.rows=[{'Id':1,'field_1':'pubmed:1','field_3':'A'}]
        self.args=({'Id':'synthetic-view','Title':'Old reader'},'https://example.test/site','/site/reports',{'csv':'https://example.test/old.csv','json':'https://example.test/old.json','uncertainty':'https://example.test/unknown'})

    def test_current_values_preserved_and_historical_links_remain(self):
        files,patch,info=prepare(self.result,self.rows,*self.args)
        self.assertEqual(self.rows[0]['field_3'],'A')
        self.assertEqual(info['counts']['uncertain_semantic_pairs'],1)
        self.assertIn('https://example.test/old.csv',patch['CustomFormatter'])
        self.assertEqual(set(patch),{'Title','ViewQuery','CustomFormatter'})
        self.assertEqual(len(files),4)
        self.assertIn('<Value Type="Counter">1</Value>',patch['ViewQuery'])
        prior=json.loads(next(v for k,v in files.items() if k.endswith('-prior-reader.json')))
        self.assertEqual(prior,self.args[0])

    def test_drift_or_missing_pair_is_refused(self):
        self.rows[0]['field_3']='curated change'
        with self.assertRaises(ValueError):prepare(self.result,self.rows,*self.args)
        self.rows=[]
        with self.assertRaises(ValueError):prepare(self.result,self.rows,*self.args)

    def test_non_title_explanation_and_external_folder_refused(self):
        self.result['items'][0]['disposition']='title_presentation_equivalent_preserved'
        with self.assertRaises(ValueError):prepare(self.result,self.rows,*self.args)
        self.result['items'][0]['disposition']='uncertain_source_difference_preserved'
        bad=list(self.args);bad[2]='/another-site/reports'
        with self.assertRaises(ValueError):prepare(self.result,self.rows,*bad)

    def test_title_explanations_use_loaded_source_key_and_require_full_title(self):
        self.result['items'][0].update(field='Title',retained_value='A &amp; B',source_value='A & B',disposition='title_presentation_equivalent_preserved')
        self.rows[0]['Title']='A &amp; B'
        _,patch,info=prepare(self.result,self.rows,*self.args)
        self.assertEqual(info['counts']['explained_title_pairs'],1)
        formatter=json.loads(patch['CustomFormatter'])
        badge=formatter['rowFormatter']['children'][3]['txtContent']
        self.assertIn("[$field_1] == 'pubmed:1'",badge)
        self.assertIn('Explained title: presentation only',badge)
        full='A'*256
        self.result['items'][0].update(retained_value=full[:255],source_value=full,disposition='bounded_display_full_source_retained')
        self.rows[0]['Title']=full[:255]
        with self.assertRaises(ValueError):prepare(self.result,self.rows,*self.args)
        self.rows[0]['SourceFullTitle']=full
        _,patch,_=prepare(self.result,self.rows,*self.args)
        self.assertIn('Explained title: full source retained',patch['CustomFormatter'])
