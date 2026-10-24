import copy
import unittest

from scripts.verify_nih_observation_freshness import verify


class ObservationFreshnessTests(unittest.TestCase):
    def setUp(self):
        self.manifest = {"run": "synthetic-run", "observed_utc": "2026-10-24T01:00:01Z",
                         "responses": [{"role": str(i), "response": {"data": {"synopsis": {
                             "lastUpdatedDate": "Jun 02, 2026"}}}} for i in range(4)]}
        self.run = {"name": "synthetic-run", "properties": {"status": "Succeeded",
                    "startTime": "2026-10-24T01:00:00Z", "endTime": "2026-10-24T01:00:10Z",
                    "trigger": {"name": "Recurrence", "status": "Succeeded",
                                "originHistoryName": "synthetic-run", "scheduledTime": "2026-10-24T01:00:00Z"}}}
        self.repetitions = {"action": "Fetch_response", "truncated": False, "count": 4,
                             "repetitions": [{"runName": "synthetic-run", "actionName": "Fetch_response", "properties": {
            "status": "Succeeded", "repetitionIndexes": [{"itemIndex": i}],
            "startTime": "2026-10-24T01:00:02Z", "endTime": "2026-10-24T01:00:03Z"}} for i in range(4)]}
        self.outputs = [{"statusCode": 200, "body": x["response"], "headers": {
            "Date": "Sat, 24 Oct 2026 01:00:02 GMT"}} for x in self.manifest["responses"]]

    def check(self, checked_at="2026-10-24T01:00:20Z"):
        return verify(self.manifest, self.run, self.repetitions, self.outputs, checked_at=checked_at)

    def test_fresh_observation_does_not_relabel_provider_vintage(self):
        result = self.check()
        self.assertTrue(result["scheduled_observation_verified"])
        self.assertEqual(result["provider_last_updated_raw"], "Jun 02, 2026")
        self.assertFalse(result["source_change_inferred"])
        self.assertFalse(result["model_freshness_qualified"])

    def test_stale_or_future_observation_rejected(self):
        for clock in ["2026-10-24T01:06:00Z", "2026-10-24T00:59:59Z"]:
            with self.assertRaisesRegex(ValueError, "stale_or_future"):
                self.check(clock)

    def test_resubmission_does_not_count_as_actual_scheduled_tick(self):
        self.run["properties"]["trigger"]["originHistoryName"] = "earlier-run"
        with self.assertRaisesRegex(ValueError, "scheduled_observation"):
            self.check()

    def test_incomplete_action_evidence_rejected(self):
        self.repetitions["truncated"] = True
        with self.assertRaisesRegex(ValueError, "incomplete_http"):
            self.check()

    def test_archived_body_must_match_actual_http_body(self):
        self.outputs = copy.deepcopy(self.outputs)
        self.outputs[0]["body"] = {"changed": True}
        with self.assertRaisesRegex(ValueError, "archive_mismatch"):
            self.check()

    def test_action_receipt_from_another_run_rejected(self):
        self.repetitions["repetitions"][0]["runName"] = "other-run"
        with self.assertRaisesRegex(ValueError, "archive_mismatch"):
            self.check()

    def test_provider_clock_and_missing_date_rejected(self):
        for headers in [{}, {"date": "Fri, 23 Oct 2026 01:00:00 GMT"}]:
            self.outputs[0]["headers"] = headers
            with self.assertRaises(ValueError):
                self.check()


if __name__ == "__main__":
    unittest.main()
