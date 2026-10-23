import unittest

from scripts.grants_mrff_download import _resource_kind


class MrffResourceKindTests(unittest.TestCase):
    def test_classifies_current_resource_filenames(self):
        cases = {
            "medical-research-future-fund-mrff-grant-recipients_0.xlsx": "awarded_grant_recipients",
            "medical_research_future_fund_grant_recipients_-_summary_as_at_10_july_2026.xlsx": "awarded_grants_summary",
            "medical_research_future_fund_funded_rates_as_at_10_july_2026.xlsx": "opportunity_funded_rates_summary",
        }
        for filename, expected in cases.items():
            with self.subTest(filename=filename):
                self.assertEqual(_resource_kind("generic Excel attachment", f"https://www.health.gov.au/{filename}"), expected)

    def test_rejects_unrecognized_attachment(self):
        with self.assertRaisesRegex(ValueError, "unrecognized MRFF Excel attachment"):
            _resource_kind("generic Excel attachment", "https://www.health.gov.au/unknown.xlsx")


if __name__ == "__main__":
    unittest.main()
