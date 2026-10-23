import unittest
from unittest import mock

from scripts.e09_feed_contracts import stable_thread_id
from scripts.e09_first_discovery import (
    parse_registry_row, select_catch_up_threads, select_new_threads,
)
from scripts.e09_post_content import POST_BODY_FIELDS, render_post_body


def selected(**overrides):
    record = {
        "publication_key": "pubmed:39751157",
        "canonical_key": "PUB:0034379c5548ab01",
        "tier": "confirmed",
        "review_status": "Included",
        "discovered_on": "2026-10-20",
        "suggested_trigger": "first_discovery",
        "Title": "A CHHHS research publication",
    }
    record.update(overrides)
    return record


class RenderTests(unittest.TestCase):
    def test_thread_id_reuses_the_shared_identity(self):
        rendered = render_post_body(selected())
        self.assertEqual(rendered["thread_id"], stable_thread_id("pubmed:39751157"))
        self.assertEqual(rendered["thread_id"], "thread:pubmed:39751157")

    def test_confirmed_and_possible_wording_distinctions(self):
        confirmed = render_post_body(selected())
        self.assertIn("A CHHHS research publication\n", confirmed["plain_text"])
        possible = render_post_body(selected(
            publication_key="pubmed:2", canonical_key="PUB:aaaa", tier="possible",
            review_status="Needs Review"))
        self.assertIn("possible CHHHS research publication (needs review)", possible["plain_text"])

    def test_verified_month_included_and_unknown_month_omitted(self):
        self.assertIn("Publication month (verified): 2026-10",
                      render_post_body(selected(PublicationMonth="2026-10"))["plain_text"])
        self.assertNotIn("month", render_post_body(selected())["plain_text"])

    def test_excluded_tier_never_renders(self):
        with self.assertRaisesRegex(ValueError, "never open threads"):
            render_post_body(selected(tier="rejected", review_status="Excluded"))
        with self.assertRaisesRegex(ValueError, "no approved wording"):
            render_post_body(selected(tier="unknown"))

    def test_allowlist_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "outside the no-send allowlist"):
            render_post_body(selected(AffiliatedAuthorLabels="Dr Someone"))
        sparse = selected()
        del sparse["discovered_on"]
        with self.assertRaisesRegex(ValueError, "missing selection fields"):
            render_post_body(sparse)
        with self.assertRaisesRegex(ValueError, "Title"):
            render_post_body(selected(Title="   "))
        with self.assertRaisesRegex(ValueError, "suggested_trigger"):
            render_post_body(selected(suggested_trigger="scheduled_send"))

    def test_hostile_title_text_is_escaped_in_html(self):
        rendered = render_post_body(selected(Title="<script>alert('x')</script> Research"))
        self.assertNotIn("<script>", rendered["body"]["content"])
        self.assertIn("&lt;script&gt;", rendered["body"]["content"])
        self.assertIn("<script>", rendered["plain_text"])

    def test_deterministic_replay_stable_render(self):
        first = render_post_body(selected())
        second = render_post_body(selected())
        self.assertEqual(first, second)
        # No generated timestamp: only the registry-derived production date appears.
        self.assertNotIn("2026-10-23", first["plain_text"])
        self.assertNotIn("T0", first["body"]["content"])

    def test_catch_up_trigger_wording(self):
        rendered = render_post_body(selected(suggested_trigger="catch_up"))
        self.assertIn("Selected in catch-up backfill", rendered["plain_text"])

    def test_registry_title_flows_from_real_selection_shape(self):
        row = parse_registry_row({
            "SourceKey": "pubmed:5001",
            "CanonicalKey": "PUB:beefbeef",
            "ReviewStatus": "Included",
            "FirstObservedUTC": "2026-10-18T22:05:00Z",
            "LastObservedUTC": None,
            "PublicationMonth": "2026-09",
            "Title": "Late-discovered publication",
        })
        rendered = render_post_body({
            "publication_key": "pubmed:5001",
            "canonical_key": "PUB:beefbeef",
            "tier": "confirmed",
            "review_status": "Included",
            "discovered_on": "2026-10-18",
            "suggested_trigger": "catch_up",
            "Title": row.get("Title", "Late-discovered publication"),
            "PublicationMonth": row["publication_month"],
        })
        self.assertIn("Late-discovered publication", rendered["plain_text"])
        self.assertIn("2026-09", rendered["plain_text"])


class FocusedBehaviourTests(unittest.TestCase):
    """Task 3 local checks: duplicates, late/unknown dates, repeats, interruption, corrections."""

    def rows(self):
        return [
            {"SourceKey": "pubmed:1", "CanonicalKey": "PUB:aaa1", "ReviewStatus": "Included",
             "FirstObservedUTC": "2026-10-20T01:00:00Z", "LastObservedUTC": None,
             "Title": "Late unknown month publication", "PublicationMonth": ""},
            {"SourceKey": "pubmed:2", "CanonicalKey": "PUB:bbb2", "ReviewStatus": "Included",
             "FirstObservedUTC": "2026-10-21T01:00:00Z", "LastObservedUTC": None,
             "PublicationMonth": "2026-10"},
            {"SourceKey": "pubmed:3", "CanonicalKey": "PUB:ccc3", "ReviewStatus": "Needs Review",
             "FirstObservedUTC": "2026-10-21T02:00:00Z", "LastObservedUTC": None},
        ]

    def test_late_unknown_publication_month_flows_through(self):
        result = select_new_threads(
            self.rows(), baseline_utc="2026-10-19T00:00:00Z", through_utc="2026-10-22T00:00:00Z")
        self.assertEqual([t["publication_key"] for t in result["new_threads"]],
                         ["pubmed:1", "pubmed:2", "pubmed:3"])

    def test_repeated_inputs_are_deterministic(self):
        baseline, through = "2026-10-19T00:00:00Z", "2026-10-22T00:00:00Z"
        first = select_new_threads(self.rows(), baseline_utc=baseline, through_utc=through)
        second = select_new_threads(self.rows(), baseline_utc=baseline, through_utc=through)
        self.assertEqual(first, second)

    def test_interrupted_batch_fails_closed_with_nothing_selected(self):
        rows = self.rows()
        rows.insert(1, self.rows()[0])  # duplicate mid-batch
        with self.assertRaisesRegex(ValueError, "repeats SourceKey 'pubmed:1'"):
            select_new_threads(rows, baseline_utc="2026-10-19T00:00:00Z",
                               through_utc="2026-10-22T00:00:00Z")
        invalid = self.rows()
        invalid[1]["ReviewStatus"] = "Maybe"
        with self.assertRaisesRegex(ValueError, "ReviewStatus"):
            select_new_threads(invalid, baseline_utc="2026-10-19T00:00:00Z",
                               through_utc="2026-10-22T00:00:00Z")

    def test_correction_between_reads_reclassifies_not_merges(self):
        selected_before = select_new_threads(
            self.rows(), baseline_utc="2026-10-19T00:00:00Z", through_utc="2026-10-22T00:00:00Z")
        corrected = self.rows()
        corrected[2]["ReviewStatus"] = "Excluded"
        corrected[1]["ReviewStatus"] = "Needs Review"
        selected_after = select_new_threads(
            corrected, baseline_utc="2026-10-19T00:00:00Z", through_utc="2026-10-22T00:00:00Z")
        keys_before = [t["publication_key"] for t in selected_before["new_threads"]]
        keys_after = [t["publication_key"] for t in selected_after["new_threads"]]
        self.assertIn("pubmed:3", keys_before)
        self.assertNotIn("pubmed:3", keys_after)
        self.assertIn("pubmed:2", keys_after)
        tiers_after = {t["publication_key"]: t["tier"] for t in selected_after["new_threads"]}
        self.assertEqual(tiers_after["pubmed:2"], "possible")
        self.assertEqual(selected_after["in_window_excluded_count"], 1)

    def test_cross_source_duplicate_identity_still_fails_closed_locally(self):
        # A same-publication duplicate seen through different sources resolves to
        # one canonical key; identity remains per registry SourceKey until the
        # native reconciliation path runs, so the batch still fails closed.
        rows = self.rows()
        rows.append({
            "SourceKey": "pubmed:1", "CanonicalKey": "PUB:aaa1", "ReviewStatus": "Included",
            "FirstObservedUTC": "2026-10-20T05:00:00Z", "LastObservedUTC": None,
            "PublicationMonth": "2026-10",
        })
        with self.assertRaisesRegex(ValueError, "repeats SourceKey"):
            select_new_threads(rows, baseline_utc="2026-10-19T00:00:00Z",
                               through_utc="2026-10-22T00:00:00Z")


class ReceiptBindingTests(unittest.TestCase):
    def test_selected_record_renders_and_binds_to_no_send_receipt(self):
        from scripts.e09_feed_contracts import validate_contract_batch
        rendered = render_post_body(selected())
        validated = validate_contract_batch("delivery_receipt", [{
            "receipt_id": "rcpt-post-1",
            "publication_key": selected()["publication_key"],
            "thread_id": rendered["thread_id"],
            "trigger": selected()["suggested_trigger"],
            "intended_outcome": "no_send",
            "outcome": "recorded_only",
            "discovered_on": selected()["discovered_on"],
            "recorded_at": "2026-10-20T10:00:00+10:00",
            "delivery_authority_reference": None,
            "suppression_reason": None,
            "post_reference": None,
            "reconciliation_required": False,
            "revision": 1,
        }])
        self.assertEqual(validated[0]["thread_id"], rendered["thread_id"])


class PreparationSchemaParityTests(unittest.TestCase):
    def test_post_body_fields_match_schema_definition(self):
        import json
        from pathlib import Path
        path = Path(__file__).parents[1] / "contracts/e09-feed-preparation.schema.json"
        if not path.exists():
            self.skipTest("preparation schema file is absent")
        definition = (json.loads(path.read_text(encoding="utf-8"))["$defs"]["no_send_post_body"])
        self.assertEqual(set(definition["required"]), POST_BODY_FIELDS)
        self.assertEqual(set(definition["properties"]), POST_BODY_FIELDS)

    def test_rendered_body_conforms_when_jsonschema_installed(self):
        import json
        from pathlib import Path
        try:
            import jsonschema
        except ImportError:
            self.skipTest("jsonschema not installed")
        path = Path(__file__).parents[1] / "contracts/e09-feed-preparation.schema.json"
        if not path.exists():
            self.skipTest("preparation schema file is absent")
        schema = json.loads(path.read_text(encoding="utf-8"))
        definition = {"$schema": schema["$schema"], "$ref": "#/$defs/no_send_post_body",
                      "$defs": schema["$defs"]}
        jsonschema.validate(render_post_body(selected()), definition)


if __name__ == "__main__":
    unittest.main()
