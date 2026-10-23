import unittest
from unittest.mock import MagicMock, patch

from scripts.enrich_crossref import fetch_crossref_work_by_doi


class CrossrefRequestTests(unittest.TestCase):
    def test_missing_polite_email_omits_empty_mailto_parameter_and_header(self):
        response = MagicMock(status=404)
        with patch('scripts.enrich_crossref.urllib.request.urlopen', return_value=response) as open_url:
            fetch_crossref_work_by_doi('10.1000/example', email='')
        request = open_url.call_args.args[0]
        self.assertNotIn('mailto=', request.full_url)
        self.assertEqual(request.get_header('User-agent'), 'CHHHS-Research-Registry/1.0')

    def test_explicit_polite_email_is_encoded_and_identified(self):
        response = MagicMock(status=404)
        with patch('scripts.enrich_crossref.urllib.request.urlopen', return_value=response) as open_url:
            fetch_crossref_work_by_doi('10.1000/example', email='contact+research@example.org')
        request = open_url.call_args.args[0]
        self.assertIn('mailto=contact%2Bresearch%40example.org', request.full_url)
        self.assertEqual(request.get_header('User-agent'),
                         'CHHHS-Research-Registry/1.0 (mailto:contact+research@example.org)')


if __name__ == '__main__':
    unittest.main()
