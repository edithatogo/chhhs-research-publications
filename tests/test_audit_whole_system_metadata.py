import unittest
from scripts.audit_whole_system_metadata import date_facets_equal, pair_kind


class SavedMetadataAccountingTests(unittest.TestCase):
    def test_date_components_are_reordered_without_inference(self):
        self.assertTrue(date_facets_equal('Day=07; Month=Apr; Year=2014','2014 Apr 07'))
        self.assertTrue(date_facets_equal('MedlineDate=1998 Dec 7-21','1998 Dec 7-21'))
        for a,b in [('Year=2014','2014 Jan 01'),('Year=2014; Year=2014','2014'),
                    ('Year=2014; Other=unknown','2014'),('Year=2014','2015')]:
            self.assertFalse(date_facets_equal(a,b))

    def test_semantic_disposition_must_bind_both_values_and_current_registry(self):
        pair={'id':1,'field':'Authors','registry':'A','canonical':'B'}
        final={(1,'Authors'):{'retained_value':'A','source_value':'B','disposition':'uncertain_source_difference_preserved'}}
        self.assertEqual(pair_kind(pair,'populated_semantic_difference_preserved',{'field_3':'A'},final),'uncertain_source_difference_preserved')
        with self.assertRaises(ValueError):pair_kind(pair,'populated_semantic_difference_preserved',{'field_3':'changed'},final)
        final[1,'Authors']['source_value']='different source'
        with self.assertRaises(ValueError):pair_kind(pair,'populated_semantic_difference_preserved',{'field_3':'A'},final)

    def test_missing_fill_cannot_approve_a_populated_overwrite(self):
        pair={'id':1,'field':'CHHHSAffiliatedAuthors','registry':'curated','canonical':'source'}
        with self.assertRaises(ValueError):pair_kind(pair,'native_missing_destination_filled',{'field_15':'source'}, {})
        pair['registry']=''
        self.assertEqual(pair_kind(pair,'native_missing_destination_filled',{'field_15':'source'},{}),'native_missing_destination_filled')
        with self.assertRaises(ValueError):pair_kind(pair,'native_missing_destination_filled',{'field_15':'partial'}, {})

    def test_literal_segments_do_not_match_different_people(self):
        pair={'id':1,'field':'CHHHSAffiliatedAuthors','registry':'A Smith; B Jones; A Smith','canonical':'B Jones, A Smith'}
        kind='equal_literal_name_segments_different_delimiters_order_repetition'
        self.assertEqual(pair_kind(pair,kind,{},{}),'literal_segments_equal_not_person_identity')
        pair['canonical']='Adam Smith, B Jones'
        with self.assertRaises(ValueError):pair_kind(pair,kind,{},{})
