import unittest

from scripts.e09_feed_contracts import validate_subscription_preference
from scripts.e09_subscription_editions import (
    EDITION_FIELDS, build_first_discovery_editions, enum_empty_windows,
)


def preference(**overrides):
    record = {
        "subscription_id": "sub-1",
        "subscriber_urn": "urn:rims:subscriber:1",
        "cadence": "weekly",
        "status": "active",
        "enrolled_on": "2026-10-19",
        "revised_on": "2026-10-19",
        "revision": 1,
        "contact_route": "authorised_list",
        "delivery_authority_active": False,
        "delivery_authority_reference": None,
    }
    record.update(overrides)
    if "enrolled_on" in overrides and "revised_on" not in overrides:
        record["revised_on"] = record["enrolled_on"]
    return record


def discovered(**overrides):
    record = {
        "publication_key": "pubmed:1",
        "canonical_key": "PUB:aaa1",
        "tier": "confirmed",
        "review_status": "Included",
        "discovered_on": "2026-10-20",
        "suggested_trigger": "first_discovery",
    }
    record.update(overrides)
    return record


class EditionTests(unittest.TestCase):
    def test_weekly_grouping_spans_brisbane_monday_week(self):
        result = build_first_discovery_editions(
            preference(),
            [
                discovered(**{"publication_key": "pubmed:1"}),
                discovered(**{"publication_key": "pubmed:2", "discovered_on": "2026-10-24"}),
                discovered(**{"publication_key": "pubmed:3", "discovered_on": "2026-10-27"}),
            ])
        self.assertEqual(len(result["editions"]), 2)
        first, second = result["editions"]
        # 2026-10-20..24 is the week of Monday 2026-10-19 (Brisbane, fixed +10).
        self.assertEqual((first["window_start"], first["window_end"]), ("2026-10-19", "2026-10-25"))
        self.assertEqual(first["publication_count"], 2)
        self.assertEqual((second["window_start"], second["window_end"]), ("2026-10-26", "2026-11-01"))
        self.assertEqual([p["publication_key"] for p in first["publications"]],
                         ["pubmed:1", "pubmed:2"])

    def test_daily_grouping_and_cadence_distinction(self):
        result = build_first_discovery_editions(
            preference(cadence="daily"),
            [
                discovered(**{"publication_key": "pubmed:1"}),
                discovered(**{"publication_key": "pubmed:2", "discovered_on": "2026-10-20"}),
                discovered(**{"publication_key": "pubmed:3", "discovered_on": "2026-10-21"}),
            ])
        self.assertEqual(len(result["editions"]), 2)
        day_one, day_two = result["editions"]
        self.assertEqual(day_one["window_start"], "2026-10-20")
        self.assertEqual(day_one["window_end"], "2026-10-20")
        self.assertEqual(day_one["publication_count"], 2)
        self.assertTrue(all(e["cadence"] == "daily" for e in result["editions"]))
        self.assertEqual(day_two["window_start"], "2026-10-21")

    def test_enrolment_boundary_inclusive_no_retroactive_backfill(self):
        result = build_first_discovery_editions(
            preference(enrolled_on="2026-10-20"),
            [
                discovered(**{"publication_key": "pubmed:0", "discovered_on": "2026-10-19"}),
                discovered(**{"publication_key": "pubmed:1", "discovered_on": "2026-10-20"}),
                discovered(**{"publication_key": "pubmed:2", "discovered_on": "2026-10-21"}),
            ])
        self.assertEqual(
            [p["publication_key"] for p in result["editions"][0]["publications"]],
            ["pubmed:1", "pubmed:2"])
        self.assertEqual(result["skip_counts"]["enrolment_boundary"], 1)

    def test_off_paused_and_withdrawn_record_explicit_empty_outcomes(self):
        offs = build_first_discovery_editions(preference(cadence="off"), [discovered()])
        self.assertEqual(offs["editions"], [])
        self.assertEqual(offs["skip_counts"]["cadence_off"], 1)
        paused = build_first_discovery_editions(preference(status="paused"), [discovered()])
        self.assertEqual(paused["editions"], [])
        self.assertEqual(paused["skip_counts"]["subscription_paused_or_withdrawn"], 1)
        withdrawn = build_first_discovery_editions(preference(status="withdrawn"), [discovered()])
        self.assertEqual(withdrawn["skip_counts"]["subscription_paused_or_withdrawn"], 1)


class NoSendContractTests(unittest.TestCase):
    def test_editions_carry_no_send_intent_and_no_fabricated_authority(self):
        result = build_first_discovery_editions(preference(), [discovered()])
        for edition in result["editions"]:
            self.assertEqual(edition["intended_outcome"], "no_send")
            self.assertIsNone(edition["delivery_authority_reference"])
            self.assertEqual(edition["edition_kind"], "first_discovery_feed")

    def test_subscription_contract_rejections_propagate(self):
        with self.assertRaises(ValueError):
            build_first_discovery_editions(
                preference(cadence="hourly", delivery_authority_active=False), [discovered()])
        with self.assertRaisesRegex(ValueError, "delivery_authority"):
            build_first_discovery_editions(
                preference(delivery_authority_active=True, delivery_authority_reference=None),
                [discovered()])

    def test_already_delivered_skipped_with_explicit_count(self):
        result = build_first_discovery_editions(
            preference(),
            [discovered(**{"publication_key": "pubmed:1"}),
             discovered(**{"publication_key": "pubmed:2"})],
            already_delivered=["pubmed:1"])
        self.assertEqual(
            [p["publication_key"] for p in result["editions"][0]["publications"]], ["pubmed:2"])
        self.assertEqual(result["skip_counts"]["already_delivered"], 1)

    def test_repeated_keys_in_batch_fail_closed_idempotently(self):
        with self.assertRaisesRegex(ValueError, "repeats publication_key"):
            build_first_discovery_editions(
                preference(), [discovered(), discovered(**{"publication_key": "pubmed:1"})])

    def test_validated_preference_passes_through_shape_check(self):
        validated = validate_subscription_preference(preference())
        result = build_first_discovery_editions(validated, [discovered()])
        self.assertEqual(result["editions"][0]["subscriber_urn"], "urn:rims:subscriber:1")


class DeterminismAndWindowTests(unittest.TestCase):
    def test_identical_inputs_render_identical_editions(self):
        first = build_first_discovery_editions(preference(), [discovered(), discovered(**{"publication_key": "pubmed:2", "discovered_on": "2026-10-21"})])
        second = build_first_discovery_editions(preference(), [discovered(), discovered(**{"publication_key": "pubmed:2", "discovered_on": "2026-10-21"})])
        self.assertEqual(first, second)

    def test_empty_window_enumeration_lets_silence_be_distinguished(self):
        weekly = enum_empty_windows("weekly", "2026-10-19", "2026-11-01")
        self.assertEqual([w["start"] for w in weekly], ["2026-10-19", "2026-10-26"])
        daily = enum_empty_windows("daily", "2026-10-19", "2026-10-21")
        self.assertEqual(len(daily), 3)
        with self.assertRaisesRegex(ValueError, "weekly and daily"):
            enum_empty_windows("off", "2026-10-19", "2026-10-21")
        with self.assertRaisesRegex(ValueError, "must not predate"):
            enum_empty_windows("daily", "2026-10-21", "2026-10-19")


class SelectionShapeTests(unittest.TestCase):
    def test_rejected_and_foreign_fields_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "not thread-eligible"):
            build_first_discovery_editions(
                preference(), [discovered(tier="rejected", review_status="Excluded")])
        with self.assertRaisesRegex(ValueError, "outside the selection shape"):
            build_first_discovery_editions(preference(), [discovered(Title="extra")])
        with self.assertRaisesRegex(ValueError, "must be a real YYYY-MM-DD"):
            build_first_discovery_editions(preference(), [discovered(discovered_on="October")])
        with self.assertRaisesRegex(ValueError, "list of first-discovery"):
            build_first_discovery_editions(preference(), None)
        with self.assertRaisesRegex(ValueError, "already_delivered"):
            build_first_discovery_editions(preference(), [discovered()], already_delivered=None)


class PreparationSchemaParityTests(unittest.TestCase):
    def test_edition_fields_match_schema_definition(self):
        import json
        from pathlib import Path
        path = Path(__file__).parents[1] / "contracts/e09-feed-preparation.schema.json"
        if not path.exists():
            self.skipTest("preparation schema file is absent")
        definition = (json.loads(path.read_text(encoding="utf-8"))["$defs"]["first_discovery_edition"])
        self.assertEqual(set(definition["required"]), EDITION_FIELDS)
        self.assertEqual(set(definition["properties"]), EDITION_FIELDS)

    def test_build_editions_conform_when_jsonschema_installed(self):
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
        definition = {"$schema": schema["$schema"], "$ref": "#/$defs/first_discovery_edition",
                      "$defs": schema["$defs"]}
        result = build_first_discovery_editions(
            preference(),
            [discovered(**{"publication_key": "pubmed:1"}),
             discovered(**{"publication_key": "pubmed:2", "discovered_on": "2026-10-24"}),
             discovered(**{"publication_key": "pubmed:3", "discovered_on": "2026-10-27"})])
        for edition in result["editions"]:
            jsonschema.validate(edition, definition)


if __name__ == "__main__":
    unittest.main()
