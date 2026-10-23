"""Bounded official-source preparation checks; fixtures are not live acceptance."""
import copy
import unittest

from scripts.grants_us_gov_api import FON, OFFICIAL_NOFO, OPPORTUNITY_ID, prepare_snapshot


class GrantsGovPreparationTests(unittest.TestCase):
    def setUp(self):
        self.search = {"errorcode": 0, "data": {
            "searchParams": {"oppNum": FON, "oppStatuses": "forecasted|posted|closed|archived"},
            "hitCount": 1, "startRecord": 0,
            "oppHits": [{"id": str(OPPORTUNITY_ID), "number": FON, "oppStatus": "posted",
                         "closeDate": "01/07/2028"}]}}
        self.detail = {"errorcode": 0, "data": {
            "id": OPPORTUNITY_ID, "opportunityNumber": FON, "listed": "L",
            "ost": "POSTED", "docType": "synopsis", "draftMode": "N",
            "opportunityTitle": "Synthetic source title", "opportunityHistoryDetails": [],
            "synopsis": {"opportunityId": OPPORTUNITY_ID,
                         "fundingDescLinkDesc": OFFICIAL_NOFO,
                         "responseDateStr": "2028-01-07-00-00-00",
                         "agencyName": "Synthetic agency", "synopsisDesc": "Synthetic purpose",
                         "applicantEligibilityDesc": "Synthetic eligibility",
                         "applicantTypes": [{"id": "01", "description": "A"},
                                            {"id": "02", "description": "B"}]}}}

    def prepare(self, search=None, detail=None, replay=None):
        return prepare_snapshot(search or self.search, detail or self.detail,
                                search or self.search, replay or detail or self.detail,
                                retrieved_at="2026-10-23T12:00:00Z")

    def test_prepare_keeps_window_date_out_of_actionable_deadline(self):
        result = self.prepare()
        row = result["normalization_preview"][0]
        self.assertFalse(result["source_admitted"])
        self.assertFalse(result["native_submission_allowed"])
        self.assertEqual(row["ReviewStatus"], "Needs Review")
        self.assertIsNone(row["Deadline"])
        self.assertEqual(row["DeadlinePrecision"], "unknown")
        self.assertEqual(row["DeadlineUTCInstant"], "")
        self.assertEqual(row["DeadlineRaw"], "")
        self.assertEqual(result["source_date_facts"]["responseDateStr"], "2028-01-07-00-00-00")
        self.assertEqual(result["source_date_facts"]["response_date"], "2028-01-07")
        self.assertEqual(result["source_date_facts"]["search_close_date"], "01/07/2028")
        self.assertFalse(result["source_date_facts"]["mapped_to_actionable_deadline"])
        self.assertNotIn("ReviewStatus", result["batch"]["records"][0])
        self.assertEqual(result["batch"]["records"][0]["Deadline"], "")

    def test_category_reordering_does_not_mutate_retained_payload(self):
        replay = copy.deepcopy(self.detail)
        replay["data"]["synopsis"]["applicantTypes"].reverse()
        self.prepare(replay=replay)
        self.assertEqual(replay["data"]["synopsis"]["applicantTypes"][0]["id"], "02")

    def test_changed_category_description_rejects_replay(self):
        replay = copy.deepcopy(self.detail)
        replay["data"]["synopsis"]["applicantTypes"][0]["description"] = "changed"
        with self.assertRaisesRegex(ValueError, "changed_between_reads"):
            self.prepare(replay=replay)

    def test_missing_duplicate_and_truncated_results_reject(self):
        for count, hits in [(0, []), (2, self.search["data"]["oppHits"]),
                            (1, self.search["data"]["oppHits"] * 2)]:
            with self.subTest(count=count, hits=len(hits)):
                search = copy.deepcopy(self.search)
                search["data"].update(hitCount=count, oppHits=hits)
                with self.assertRaisesRegex(ValueError, "incomplete_or_wrong"):
                    self.prepare(search=search)

    def test_wrong_id_and_api_error_reject(self):
        for key, value in [("id", 1), ("opportunityNumber", "OTHER"), ("listed", "U")]:
            with self.subTest(key=key):
                detail = copy.deepcopy(self.detail)
                detail["data"][key] = value
                with self.assertRaisesRegex(ValueError, "wrong_or_unpublished"):
                    self.prepare(detail=detail)
        detail = copy.deepcopy(self.detail)
        detail["errorcode"] = False
        with self.assertRaisesRegex(ValueError, "malformed_api"):
            self.prepare(detail=detail)

    def test_duplicate_categories_and_non_midnight_date_reject(self):
        detail = copy.deepcopy(self.detail)
        detail["data"]["synopsis"]["applicantTypes"] *= 2
        with self.assertRaisesRegex(ValueError, "invalid_applicant"):
            self.prepare(detail=detail)
        detail = copy.deepcopy(self.detail)
        detail["data"]["synopsis"]["responseDateStr"] = "2028-01-07-17-00-00"
        with self.assertRaisesRegex(ValueError, "unsupported_source_closing_date"):
            self.prepare(detail=detail)

    def test_mismatched_search_close_and_detail_response_dates_reject(self):
        search = copy.deepcopy(self.search)
        search["data"]["oppHits"][0]["closeDate"] = "02/01/2028"
        with self.assertRaisesRegex(ValueError, "search_close_response_date_mismatch"):
            self.prepare(search=search)


if __name__ == "__main__":
    unittest.main()
