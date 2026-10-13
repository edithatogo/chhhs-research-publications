import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from merge_openalex_context import merge


class OpenAlexContext(unittest.TestCase):
    def row(self, **changes):
        return {'OpenAlexWorkID':'https://openalex.org/W1','DOI':'10.1000/test',
                'CitationCount_OpenAlex':0,'OpenAccessStatus_OpenAlex':'gold',
                'OAUrl_OpenAlex':None,'OpenAlexObservedUTC':'2026-01-01T00:00:00Z',**changes}

    def test_exact_doi_preserves_identity_reviews_and_bibliography(self):
        original=[{'CanonicalKey':'PMID:1','DOI':'https://doi.org/10.1000/TEST',
                   'Title':'Retained title','ReviewStatus':'Excluded','PublicationDateRaw':'uncertain'}]
        rows,proof=merge(original,[self.row()])
        for key in original[0]:self.assertEqual(rows[0][key],original[0][key])
        self.assertEqual(rows[0]['CitationCount_OpenAlex'],0)
        self.assertEqual(len(proof),3)
        self.assertNotIn('CitationCount_OpenAlex',original[0])

    def test_missing_field_keeps_value_and_its_original_time(self):
        original=[{'CanonicalKey':'PMID:1','DOI':'10.1000/test','CitationCount_OpenAlex':7,
                   'CitationCount_OpenAlex_ObservedUTC':'2025-12-01T00:00:00Z'}]
        rows,proof=merge(original,[self.row(CitationCount_OpenAlex=None)])
        self.assertEqual(rows[0]['CitationCount_OpenAlex'],7)
        self.assertEqual(rows[0]['CitationCount_OpenAlex_ObservedUTC'],'2025-12-01T00:00:00Z')
        self.assertEqual(proof[0]['Decision'],'preserve_missing')

    def test_unmatched_provider_work_cannot_add_a_publication(self):
        original=[{'CanonicalKey':'PMID:2','DOI':None,'Title':'No DOI'}]
        rows,proof=merge(original,[self.row()])
        self.assertEqual(rows,original);self.assertEqual(proof,[])

    def test_older_observation_keeps_newer_value(self):
        original=[{'CanonicalKey':'PMID:1','DOI':'10.1000/test','CitationCount_OpenAlex':9,
                   'CitationCount_OpenAlex_ObservedUTC':'2026-01-02T00:00:00Z'}]
        rows,proof=merge(original,[self.row()])
        self.assertEqual(rows[0]['CitationCount_OpenAlex'],9)
        self.assertEqual(proof[0]['Decision'],'preserve_newer')

    def test_duplicate_provider_doi_cannot_multiply_publication_rows(self):
        with self.assertRaises(ValueError):merge([{'CanonicalKey':'PMID:1','DOI':'10.1000/test'}],
            [self.row(),self.row(OpenAlexWorkID='https://openalex.org/W2')])

    def test_same_timestamp_conflict_is_not_silently_overwritten(self):
        with self.assertRaises(ValueError):merge([{'CanonicalKey':'PMID:1','DOI':'10.1000/test',
            'CitationCount_OpenAlex':8,'CitationCount_OpenAlex_ObservedUTC':'2026-01-01T00:00:00Z'}],[self.row()])
