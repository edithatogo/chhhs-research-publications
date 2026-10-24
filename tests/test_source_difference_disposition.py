import copy
import unittest
from scripts.dispose_publication_source_differences import disposition


class SourceDispositionTests(unittest.TestCase):
    def setUp(self):
        self.audit={'preserved_semantic_items':[{'id':1,'field':'Title','registry':'A &amp; B','canonical':'A & B'}]}
        self.current={'complete':True,'next_links':[],'independent_count':1,'observed_at':'2026-10-24T00:00:00Z','rows':[{'Id':1,'field_1':'pubmed:1','Title':'A &amp; B','field_18':'approved'}]}
        self.pairs={'source_revision':'fictional-retained','cases':[{'records':[{'record_id':'registry:1','source_key':'pubmed:1'},{'record_id':'canonical-for:1','source_key':'pubmed:1','values':{'Title':'A & B'}}]}]}

    def test_literal_title_equivalence_never_changes_values_or_approves_correction(self):
        before=copy.deepcopy(self.current);r=disposition(self.audit,self.current,self.pairs)
        self.assertEqual(r['disposition_counts'],{'title_presentation_equivalent_preserved':1})
        self.assertEqual(before,self.current);self.assertFalse(r['native_write_performed'])
        self.assertEqual(r['items'][0]['correction_provenance'],'not-established-by-selected-evidence')

    def test_bounded_title_requires_exact_full_source_retention(self):
        value='a'*256;self.audit['preserved_semantic_items'][0].update(registry=value[:255],canonical=value)
        self.current['rows'][0].update(Title=value[:255],SourceFullTitle=value)
        self.pairs['cases'][0]['records'][1]['values']['Title']=value
        self.assertIn('bounded_display_full_source_retained',disposition(self.audit,self.current,self.pairs)['disposition_counts'])
        del self.current['rows'][0]['SourceFullTitle']
        self.assertIn('uncertain_source_difference_preserved',disposition(self.audit,self.current,self.pairs)['disposition_counts'])

    def test_no_fuzzy_author_resolution_or_per_record_approval_queue(self):
        self.audit['preserved_semantic_items'][0].update(field='Authors',registry='J Smith',canonical='John Smith')
        self.current['rows'][0]['field_3']='J Smith';self.pairs['cases'][0]['records'][1]['values']['Authors']='John Smith'
        item=disposition(self.audit,self.current,self.pairs)['items'][0]
        self.assertEqual(item['disposition'],'uncertain_source_difference_preserved')
        self.assertFalse(item['manual_record_approval_required'])

    def test_incomplete_drift_duplicate_or_unbound_source_refused(self):
        for change in ('incomplete','drift','duplicate','source'):
            c=copy.deepcopy(self.current);a=copy.deepcopy(self.audit);p=copy.deepcopy(self.pairs)
            if change=='incomplete':c['next_links']=['next']
            elif change=='drift':c['rows'][0]['Title']='changed'
            elif change=='duplicate':a['preserved_semantic_items']*=2
            else:p['cases'][0]['records'][1]['source_key']='different'
            with self.subTest(change=change),self.assertRaises(ValueError):disposition(a,c,p)
