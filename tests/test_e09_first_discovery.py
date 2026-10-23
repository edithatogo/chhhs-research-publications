import unittest
import json
import tempfile
from pathlib import Path

from scripts.e09_first_discovery import (
    parse_registry_row, select_catch_up_threads, select_new_threads,
)


def registry_row(**overrides):
    row = {
        "SourceKey": "pubmed:39751157",
        "CanonicalKey": "PUB:0034379c5548ab01",
        "ReviewStatus": "Included",
        "FirstObservedUTC": "2026-10-20T04:13:10.615Z",
        "LastObservedUTC": None,
        "PublicationMonth": "2026-10",
    }
    row.update(overrides)
    return row


class ParseTests(unittest.TestCase):
    def test_included_possible_excluded_tiers(self):
        self.assertEqual(parse_registry_row(registry_row())["tier"], "confirmed")
        self.assertEqual(parse_registry_row(registry_row(
            SourceKey="dora:10037.1/12345", PublicationMonth=None))["tier"], "confirmed")
        possible = parse_registry_row(registry_row(
            SourceKey="pubmed:1", CanonicalKey="PUB:abcd", ReviewStatus="Needs Review"))
        self.assertEqual(possible["tier"], "possible")
        rejected = parse_registry_row(registry_row(
            SourceKey="pubmed:2", CanonicalKey="PUB:dead", ReviewStatus="Excluded"))
        self.assertEqual(rejected["tier"], "rejected")

    def test_first_observed_never_accepted_in_nonzero_or_naive_forms(self):
        with self.assertRaisesRegex(ValueError, "timezone-aware"):
            parse_registry_row(registry_row(FirstObservedUTC="2026-10-20T04:13:10"))
        with self.assertRaisesRegex(ValueError, "zero offset"):
            parse_registry_row(registry_row(FirstObservedUTC="2026-10-20T04:13:10+10:00"))

    def test_last_observed_must_not_predate_first(self):
        with self.assertRaisesRegex(ValueError, "LastObservedUTC must not predate"):
            parse_registry_row(registry_row(
                FirstObservedUTC="2026-10-15T00:00:00Z",
                LastObservedUTC="2026-10-10T00:00:00Z"))

    def test_undocumented_missing_or_malformed_fields_fail(self):
        with self.assertRaisesRegex(ValueError, "undocumented fields"):
            parse_registry_row(registry_row(UnexpectedField="x"))
        sparse = registry_row()
        del sparse["ReviewStatus"]
        with self.assertRaisesRegex(ValueError, "missing selection fields"):
            parse_registry_row(sparse)
        with self.assertRaisesRegex(ValueError, "ReviewStatus must be exactly"):
            parse_registry_row(registry_row(ReviewStatus="Possible"))
        with self.assertRaisesRegex(ValueError, "CanonicalKey"):
            parse_registry_row(registry_row(CanonicalKey="GRANT:123"))
        with self.assertRaisesRegex(ValueError, "PublicationMonth"):
            parse_registry_row(registry_row(PublicationMonth="2026-13"))
        with self.assertRaisesRegex(ValueError, "YYYY-MM"):
            parse_registry_row(registry_row(PublicationMonth="October"))


class SelectionTests(unittest.TestCase):
    rows_for_window = None

    def rows(self):
        return [
            registry_row(SourceKey="pubmed:1", FirstObservedUTC="2026-10-20T01:00:00Z"),
            registry_row(SourceKey="pubmed:2", FirstObservedUTC="2026-10-21T01:00:00Z"),
            registry_row(SourceKey="pubmed:3", FirstObservedUTC="2026-10-19T01:00:00Z"),
            registry_row(SourceKey="pubmed:4", FirstObservedUTC="2026-10-22T01:00:00Z",
                         ReviewStatus="Needs Review"),
            registry_row(SourceKey="pubmed:5", FirstObservedUTC="2026-10-21T01:00:00Z",
                         ReviewStatus="Excluded", CanonicalKey="PUB:ffffff"),
        ]

    def test_window_bounds_and_excluded_preservation(self):
        result = select_new_threads(
            self.rows(), baseline_utc="2026-10-19T12:00:00Z", through_utc="2026-10-21T23:59:59Z")
        keys = [t["publication_key"] for t in result["new_threads"]]
        self.assertEqual(keys, ["pubmed:1", "pubmed:2"])
        tiers = {t["publication_key"]: t["tier"] for t in result["new_threads"]}
        self.assertEqual(tiers["pubmed:1"], "confirmed")
        self.assertEqual(tiers["pubmed:2"], "confirmed")
        self.assertEqual(result["requires_catch_up_tier_counts"],
                         {"confirmed": 1, "possible": 0, "rejected": 0})
        self.assertEqual(result["future_tier_counts"],
                         {"confirmed": 0, "possible": 1, "rejected": 0})
        self.assertEqual(result["in_window_excluded_count"], 1)
        self.assertEqual(result["total_parseable"], 5)
        for thread in result["new_threads"]:
            self.assertEqual(thread["suggested_trigger"], "first_discovery")
            self.assertIn(thread["tier"], {"confirmed", "possible"})

    def test_excluded_never_becomes_a_thread(self):
        result = select_new_threads(
            [registry_row(SourceKey="pubmed:9", FirstObservedUTC="2026-10-20T10:00:00Z",
                          ReviewStatus="Excluded", CanonicalKey="PUB:eeeeeeeeee")],
            baseline_utc="2026-10-25T00:00:00Z", through_utc="2026-10-27T00:00:00Z")
        self.assertEqual(result["new_threads"], [])
        self.assertEqual(result["requires_catch_up_tier_counts"]["rejected"], 1)
        self.assertEqual(result["in_window_excluded_count"], 0)

    def test_future_rows_and_ordering_boundaries(self):
        result = select_new_threads(
            self.rows(), baseline_utc="2026-10-22T01:00:00Z", through_utc="2026-10-22T01:00:00Z")
        self.assertEqual([t["publication_key"] for t in result["new_threads"]], [])
        self.assertEqual(result["requires_catch_up_tier_counts"]["confirmed"], 3)
        self.assertEqual(result["in_window_excluded_count"], 0)

    def test_duplicate_source_keys_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "repeats SourceKey"):
            select_new_threads(
                [registry_row(), registry_row(ReviewStatus="Needs Review")],
                baseline_utc="2026-10-01T00:00:00Z", through_utc="2026-10-30T00:00:00Z")

    def test_misordered_bounds_reject(self):
        with self.assertRaisesRegex(ValueError, "through_utc"):
            select_new_threads(self.rows(),
                               baseline_utc="2026-10-22T00:00:00Z", through_utc="2026-10-20T00:00:00Z")
        with self.assertRaisesRegex(ValueError, "must be a list"):
            select_new_threads(None, baseline_utc="2026-10-01T00:00:00Z",
                               through_utc="2026-10-30T00:00:00Z")


class CatchUpTests(unittest.TestCase):
    def rows(self):
        return [
            registry_row(SourceKey="pubmed:11", FirstObservedUTC="2026-09-01T09:00:00Z"),
            registry_row(SourceKey="pubmed:12", FirstObservedUTC="2026-09-05T09:00:00Z",
                         ReviewStatus="Needs Review", CanonicalKey="PUB:aaaa"),
            registry_row(SourceKey="pubmed:13", FirstObservedUTC="2026-09-10T09:00:00Z",
                         ReviewStatus="Excluded", CanonicalKey="PUB:bbbb"),
            registry_row(SourceKey="pubmed:14", FirstObservedUTC="2026-10-02T09:00:00Z"),
        ]

    def test_inclusive_window_backfill_excludes_rejected(self):
        selected = select_catch_up_threads(
            self.rows(), catch_up_from_utc="2026-09-05T09:00:00Z", catch_up_to_utc="2026-09-10T09:00:00Z")
        self.assertEqual([t["publication_key"] for t in selected], ["pubmed:12"])
        self.assertEqual(selected[0]["suggested_trigger"], "catch_up")
        self.assertEqual(selected[0]["tier"], "possible")

    def test_boundary_inclusive_and_outside_rows_skipped(self):
        selected = select_catch_up_threads(
            self.rows(), catch_up_from_utc="2026-09-01T09:00:00Z", catch_up_to_utc="2026-09-01T09:00:00Z")
        self.assertEqual([t["publication_key"] for t in selected], ["pubmed:11"])
        empty = select_catch_up_threads(
            self.rows(), catch_up_from_utc="2026-10-01T00:00:00Z", catch_up_to_utc="2026-10-01T08:00:00Z")
        self.assertEqual(empty, [])

    def test_bad_window_and_duplicates_reject(self):
        with self.assertRaisesRegex(ValueError, "catch_up_to_utc"):
            select_catch_up_threads(self.rows(), catch_up_from_utc="2026-09-10T00:00:00Z",
                                    catch_up_to_utc="2026-09-01T00:00:00Z")


class BatchVehicleTests(unittest.TestCase):
    def test_selected_threads_feed_the_delivery_receipt_contract(self):
        from scripts.e09_feed_contracts import validate_contract_batch
        selected = select_catch_up_threads(
            [registry_row(SourceKey="pubmed:21",
                          FirstObservedUTC="2026-09-02T10:00:00Z")],
            catch_up_from_utc="2026-09-01T00:00:00Z",
            catch_up_to_utc="2026-09-05T00:00:00Z")
        receipts = [{
            "receipt_id": "rcpt-test-1",
            "publication_key": thread["publication_key"],
            "thread_id": f"thread:{thread['publication_key']}",
            "trigger": thread["suggested_trigger"],
            "intended_outcome": "no_send",
            "outcome": "recorded_only",
            "discovered_on": thread["discovered_on"],
            "recorded_at": "2026-09-03T10:00:00+10:00",
            "delivery_authority_reference": None,
            "suppression_reason": None,
            "post_reference": None,
            "reconciliation_required": False,
            "revision": 1,
        } for thread in selected]
        validated = validate_contract_batch("delivery_receipt", receipts)
        self.assertEqual(validated[0]["trigger"], "catch_up")


if __name__ == "__main__":
    unittest.main()
