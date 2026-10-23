import unittest
import tempfile
import json
from pathlib import Path

from scripts.e09_feed_contracts import (
    CONTRIBUTION_FIELDS,
    DELIVERY_RECEIPT_FIELDS,
    SUBSCRIPTION_FIELDS,
    stable_thread_id,
    validate_contract_batch,
    validate_contribution_record,
    validate_delivery_receipt,
    validate_subscription_preference,
)


def contribution_record(**overrides):
    record = {
        "contribution_id": "contrib-0001",
        "publication_key": "pubmed:39751157",
        "thread_id": "thread:pubmed:39751157",
        "submitted_on": "2026-10-20",
        "contributor_id_kind": "declared",
        "contributor_urn": "subscriber:opaque-a",
        "identity_verification_ref": None,
        "evidence": "Collaboration visible on the co-author's lab page.",
        "evidence_urls": ["https://example.org/lab-page"],
        "suggested_keywords": ["tropical-health"],
        "status": "submitted",
        "source_revision": 1,
        "submitted_at_project_revision": 187,
        "curator_decision_on": None,
        "curated_record_reference": None,
        "authoritative": False,
    }
    record.update(overrides)
    return record


def subscription_record(**overrides):
    record = {
        "subscription_id": "subs-0001",
        "subscriber_urn": "subscriber:opaque-a",
        "cadence": "weekly",
        "status": "active",
        "enrolled_on": "2026-10-20",
        "revised_on": "2026-10-20",
        "revision": 1,
        "contact_route": "authorised_list",
        "delivery_authority_active": False,
        "delivery_authority_reference": None,
    }
    record.update(overrides)
    return record


def delivery_receipt_record(**overrides):
    record = {
        "receipt_id": "rcpt-0001",
        "publication_key": "pubmed:39751157",
        "thread_id": "thread:pubmed:39751157",
        "trigger": "first_discovery",
        "intended_outcome": "no_send",
        "outcome": "recorded_only",
        "discovered_on": "2026-10-19",
        "recorded_at": "2026-10-20T09:00:00+10:00",
        "delivery_authority_reference": None,
        "suppression_reason": None,
        "post_reference": None,
        "reconciliation_required": False,
        "revision": 1,
    }
    record.update(overrides)
    return record


class StableThreadIdentityTests(unittest.TestCase):
    def test_thread_id_derives_from_registry_source_key_shape(self):
        self.assertEqual(stable_thread_id("pubmed:39751157"), "thread:pubmed:39751157")
        with self.assertRaises(ValueError):
            stable_thread_id("PUBMED:39751157")
        with self.assertRaises(ValueError):
            stable_thread_id("pubmed|39751157")
        with self.assertRaises(ValueError):
            stable_thread_id("  pubmed:39751157")
        with self.assertRaises(ValueError):
            stable_thread_id("")


class ContributionContractTests(unittest.TestCase):
    def test_valid_submission_and_curator_transitions(self):
        submitted = validate_contribution_record(contribution_record())
        self.assertFalse(submitted["authoritative"])
        accepted = validate_contribution_record(contribution_record(
            contribution_id="contrib-2", status="curator_accepted",
            source_revision=2, curator_decision_on="2026-10-21",
            curated_record_reference="pub:ref-1"))
        self.assertEqual(accepted["status"], "curator_accepted")
        rejected = validate_contribution_record(contribution_record(
            contribution_id="contrib-3", status="curator_rejected",
            contributor_id_kind="anonymous", contributor_urn=None,
            source_revision=3, curator_decision_on="2026-10-21"))
        self.assertIsNone(rejected["curated_record_reference"])

    def test_unknown_missing_or_padded_fields_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "unsupported fields"):
            validate_contribution_record(contribution_record(extra_field=1))
        sparse = contribution_record()
        del sparse["evidence"]
        with self.assertRaisesRegex(ValueError, "missing fields"):
            validate_contribution_record(sparse)
        with self.assertRaisesRegex(ValueError, "surrounding whitespace"):
            validate_contribution_record(contribution_record(contribution_id=" padded"))

    def test_thread_id_must_match_derived_identity(self):
        with self.assertRaisesRegex(ValueError, "derive exactly"):
            validate_contribution_record(contribution_record(thread_id="thread:pubmed:0"))

    def test_identity_kinds_govern_verification_references(self):
        valid = validate_contribution_record(contribution_record(
            contributor_id_kind="authenticated",
            identity_verification_ref="ref/identity-verification.json"))
        self.assertEqual(valid["contributor_id_kind"], "authenticated")
        with self.assertRaisesRegex(ValueError, "verified references"):
            validate_contribution_record(contribution_record(
                contributor_id_kind="authenticated", identity_verification_ref=None))
        with self.assertRaisesRegex(ValueError, "contributor_urn must be null"):
            validate_contribution_record(contribution_record(
                contributor_id_kind="anonymous", contributor_urn="subscriber:x"))

    def test_curator_state_cross_guards(self):
        with self.assertRaisesRegex(ValueError, "curator_decision_on"):
            validate_contribution_record(contribution_record(
                status="curator_accepted", curator_decision_on="2026-10-19",
                curated_record_reference="pub:ref-1"))
        with self.assertRaisesRegex(ValueError, "curated_record_reference must be null"):
            validate_contribution_record(contribution_record(
                status="curator_rejected", curator_decision_on="2026-10-21",
                curated_record_reference="pub:ref-1"))
        with self.assertRaisesRegex(ValueError, "curator_decision_on must be null"):
            validate_contribution_record(contribution_record(curator_decision_on="2026-10-21"))

    def test_contributions_stay_non_authoritative_and_revision_positive(self):
        with self.assertRaisesRegex(ValueError, "authoritative"):
            validate_contribution_record(contribution_record(authoritative=True))
        with self.assertRaisesRegex(ValueError, "source_revision"):
            validate_contribution_record(contribution_record(source_revision=0))

    def test_evidence_urls_require_https_shape(self):
        with self.assertRaisesRegex(ValueError, "HTTPS"):
            validate_contribution_record(contribution_record(evidence_urls=["http://example.org"]))


class SubscriptionContractTests(unittest.TestCase):
    def test_valid_active_pref_and_cadence_values(self):
        active = validate_subscription_preference(subscription_record())
        self.assertEqual(active["cadence"], "weekly")
        validate_subscription_preference(subscription_record(
            subscription_id="s2", cadence="daily", revision=2, revised_on="2026-10-21"))
        paused = validate_subscription_preference(subscription_record(
            subscription_id="s3", cadence="off", status="paused",
            revision=3, revised_on="2026-10-22"))
        self.assertEqual(paused["status"], "paused")
        withdraw = validate_subscription_preference(subscription_record(
            subscription_id="s4", status="withdrawn",
            revision=4, revised_on="2026-10-23"))
        self.assertEqual(withdraw["status"], "withdrawn")

    def test_bad_enumerations_and_chronology_reject(self):
        with self.assertRaisesRegex(ValueError, "cadence"):
            validate_subscription_preference(subscription_record(cadence="hourly"))
        with self.assertRaisesRegex(ValueError, "status"):
            validate_subscription_preference(subscription_record(status="pending"))
        with self.assertRaisesRegex(ValueError, "revised_on must not predate"):
            validate_subscription_preference(subscription_record(
                enrolled_on="2026-10-21", revised_on="2026-10-20"))
        with self.assertRaisesRegex(ValueError, "real YYYY-MM-DD"):
            validate_subscription_preference(subscription_record(enrolled_on="2026-13-40"))

    def test_delivery_authority_reference_follows_authority_flag(self):
        validate_subscription_preference(subscription_record(
            delivery_authority_active=True, delivery_authority_reference="ref/send-authority.json"))
        with self.assertRaisesRegex(ValueError, "delivery_authority_reference"):
            validate_subscription_preference(subscription_record(
                delivery_authority_active=True, delivery_authority_reference=None))
        with self.assertRaisesRegex(ValueError, "delivery_authority_reference must be null"):
            validate_subscription_preference(subscription_record(
                delivery_authority_reference="ref/send-authority.json"))


class DeliveryReceiptContractTests(unittest.TestCase):
    def test_no_send_first_receipts_record_only(self):
        recorded = validate_delivery_receipt(delivery_receipt_record())
        self.assertFalse(recorded["reconciliation_required"])
        suppressed = validate_delivery_receipt(delivery_receipt_record(
            receipt_id="rcpt-2", outcome="suppressed_policy",
            suppression_reason="no delivery authority is active"))
        self.assertIsNone(suppressed["post_reference"])

    def test_sent_outcome_requires_authority_and_post_reference(self):
        sent = validate_delivery_receipt(delivery_receipt_record(
            trigger="revision_update", intended_outcome="team_post", outcome="sent",
            discovered_on="2026-10-18", revision=2,
            delivery_authority_reference="ref/send-authority.json",
            post_reference="teams:message-ref-1"))
        self.assertEqual(sent["outcome"], "sent")
        with self.assertRaisesRegex(ValueError, "delivery_authority_reference"):
            validate_delivery_receipt(delivery_receipt_record(
                intended_outcome="team_post", outcome="sent", post_reference=None))
        with self.assertRaisesRegex(ValueError, "no-send intended outcome"):
            validate_delivery_receipt(delivery_receipt_record(
                intended_outcome="no_send", outcome="sent",
                delivery_authority_reference="ref/send-authority.json",
                post_reference="teams:message-ref-1"))

    def test_uncertain_outcomes_require_reconciliation(self):
        with self.assertRaisesRegex(ValueError, "reconciliation_required"):
            validate_delivery_receipt(delivery_receipt_record(
                receipt_id="rcpt-3", outcome="failed_uncertain",
                reconciliation_required=False))
        validate_delivery_receipt(delivery_receipt_record(
            receipt_id="rcpt-4", outcome="failed_uncertain",
            reconciliation_required=True))

    def test_chronology_and_derived_identity_guards(self):
        with self.assertRaisesRegex(ValueError, "recorded_at must not predate"):
            validate_delivery_receipt(delivery_receipt_record(
                discovered_on="2026-10-25"))
        with self.assertRaisesRegex(ValueError, "must be a timezone-aware"):
            validate_delivery_receipt(delivery_receipt_record(
                recorded_at="2026-10-20T09:00:00"))
        with self.assertRaisesRegex(ValueError, "derive exactly"):
            validate_delivery_receipt(delivery_receipt_record(thread_id="thread:other"))


class BatchTests(unittest.TestCase):
    def test_batch_rejects_duplicate_stable_ids(self):
        result = validate_contract_batch("contribution", [
            contribution_record(),
            contribution_record(contribution_id="contrib-2", source_revision=2),
        ])
        self.assertEqual([row["contribution_id"] for row in result], ["contrib-0001", "contrib-2"])
        with self.assertRaisesRegex(ValueError, "repeats contribution_id"):
            validate_contract_batch("contribution", [
                contribution_record(), contribution_record(source_revision=2)])
        with self.assertRaisesRegex(ValueError, "must be a list"):
            validate_contract_batch("subscription", None)
        with self.assertRaisesRegex(ValueError, "batch must be a list"):
            validate_contract_batch("delivery_receipt", delivery_receipt_record())


class SchemaParityTests(unittest.TestCase):
    def test_schema_field_sets_match_runtime_when_schema_present(self):
        schema_path = Path(__file__).parents[1] / "contracts/e09-feed-storage.schema.json"
        if not schema_path.exists():
            self.skipTest("storage schema file is absent")
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        definitions = schema.get("$defs") or schema.get("definitions") or {}
        mapping = {
            "contribution": (CONTRIBUTION_FIELDS, definitions.get("contribution_record")),
            "subscription": (SUBSCRIPTION_FIELDS, definitions.get("subscription_preference")),
            "delivery_receipt": (DELIVERY_RECEIPT_FIELDS, definitions.get("delivery_receipt")),
        }
        for name, (fields, definition) in mapping.items():
            self.assertIsNotNone(definition, f"schema definition {name} missing")
            required = set(definition.get("required", []))
            properties = set(definition.get("properties", {}))
            self.assertEqual(properties, fields, f"schema properties drift for {name}")
            self.assertEqual(required, fields, f"schema required-field drift for {name}")

    def test_fixtures_conform_to_schema_when_jsonschema_installed(self):
        schema_path = Path(__file__).parents[1] / "contracts/e09-feed-storage.schema.json"
        if not schema_path.exists():
            self.skipTest("storage schema file is absent")
        try:
            from jsonschema import Draft202012Validator
        except ImportError:
            self.skipTest("jsonschema is an optional test extra")
        validator = Draft202012Validator(schema=json.loads(schema_path.read_text(encoding="utf-8")))
        for record in (contribution_record(), subscription_record(), delivery_receipt_record()):
            validator.validate(record)
        for name, broken in (
            ("contribution", contribution_record(authoritative=True)),
            ("subscription", subscription_record(cadence="hourly")),
            ("delivery_receipt", delivery_receipt_record(outcome="unknown")),
        ):
            with self.assertRaises(Exception):
                validator.validate(broken)


if __name__ == "__main__":
    unittest.main()
