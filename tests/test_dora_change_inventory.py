import unittest

from scripts.dora_change_inventory import inventory, select_work


class DoRAChangeInventoryTests(unittest.TestCase):
    def xml(self, nodes):
        return '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + nodes + '</urlset>'

    def node(self, key, stamp='2026-10-24T16:00:00Z'):
        return f'<url><loc>https://dora.health.qld.gov.au/qldresearchjspui/handle/1/{key}</loc><lastmod>{stamp}</lastmod></url>'

    def test_scope_gaps_and_opaque_stamp(self):
        result = inventory(self.xml(self.node('1') + self.node('3')), ['1', '2'])
        self.assertEqual(result['missing'], ['2'])
        self.assertEqual(result['versions']['1']['source_stamp'], '2026-10-24T16:00:00Z')
        self.assertFalse(result['utc_cutoff_proven'])

    def test_duplicate_and_entity_rejection(self):
        for xml in [self.xml(self.node('1') * 2), '<!DOCTYPE urlset>' + self.xml(self.node('1'))]:
            with self.assertRaises(ValueError):
                inventory(xml, ['1'])

    def test_no_reuse_without_external_qualification_or_exact_raw_proof(self):
        versions = inventory(self.xml(self.node('1')), ['1'])['versions']
        entry = dict(versions['1'], native_id='id', etag='etag', bytes=10,
                     sha256='a' * 64, archive_folder='/archive', file='raw.html')
        self.assertEqual(select_work(versions, {'1': entry})['fetch'], ['1'])
        self.assertEqual(len(select_work(versions, {'1': entry}, version_contract_qualified=True)['reuse']), 1)
        for field in ['native_id', 'etag', 'sha256', 'source_stamp', 'file']:
            bad = dict(entry)
            bad[field] = ''
            self.assertEqual(select_work(versions, {'1': bad}, version_contract_qualified=True)['fetch'], ['1'])
