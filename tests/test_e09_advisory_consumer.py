import unittest

from scripts.e09_feed_contracts import stable_thread_id
from scripts.e09_advisory_consumer import (
    MAX_EVIDENCE_URLS,
    MAX_KEYWORDS,
    ADVISORY_KIND,
    consume_advisory_output,
    record_advisory_failure,
    validate_advisory_suggestion,
)


def suggestion(**overrides):
    record = {
        "advisory_id": "adv-1",
        "publication_key": "pubmed:39751157",
        "thread_id": "thread:pubmed:39751157",
        "advisory_kind": ADVISORY_KIND,
        "prompt_revision": 3,
        "source_revision": 7,
        "generated_on": "2026-10-23",
        "evidence_urls": ["https://example.org/evidence/1"],
        "suggested_keywords": ["rotator cuff"],
        "authoritative": False,
    }
    record.update(overrides)
    return record


def failure(**overrides):
    record = {
        "advisory_id": "adv-1",
        "publication_key": "pubmed:39751157",
        "thread_id": "thread:pubmed:39751157",
        "advisory_kind": ADVISORY_KIND,
        "failure_on": "2026-10-23",
        "failure_reason": "ai_outage",
        "failure_detail": "advisory route unavailable; manual operation retained",
        "prompt_revision": None,
        "source_revision": None,
        "manual_operation_required": True,
        "authoritative": False,
    }
    record.update(overrides)
    return record


class SuggestionSchemaTests(unittest.TestCase):
    def test_valid_roundtrip_and_bounded_shape(self):
        parsed = validate_advisory_suggestion(suggestion())
        self.assertEqual(parsed["thread_id"], stable_thread_id("pubmed:39751157"))
        self.assertFalse(parsed["authoritative"])
        self.assertEqual(parsed["advisory_kind"], "evidence_linked_suggestion")

    def test_missing_required_and_foreign_fields_fail_closed(self):
        sparse = suggestion()
        del sparse["prompt_revision"]
        with self.assertRaisesRegex(ValueError, "missing required fields"):
            validate_advisory_suggestion(sparse)
        with self.assertRaisesRegex(ValueError, "outside the bounded schema"):
            validate_advisory_suggestion(suggestion(narration="free text story"))

    def test_evidence_linking_is_mandatory_and_https_only(self):
        with self.assertRaisesRegex(ValueError, "evidence-linked"):
            validate_advisory_suggestion(suggestion(evidence_urls=[]))
        with self.assertRaisesRegex(ValueError, "must use HTTPS"):
            validate_advisory_suggestion(suggestion(evidence_urls=["http://insecure.example/"]))
        self.assertEqual(MAX_EVIDENCE_URLS, 20)
        with self.assertRaisesRegex(ValueError, "bounded to 20"):
            validate_advisory_suggestion(
                suggestion(evidence_urls=[f"https://example.org/{i}" for i in range(21)]))

    def test_keywords_bounded(self):
        with self.assertRaisesRegex(ValueError, "bounded to 20"):
            validate_advisory_suggestion(suggestion(suggested_keywords=[f"k{i}" for i in range(21)]))
        with self.assertRaisesRegex(ValueError, "must be non-empty"):
            validate_advisory_suggestion(suggestion(suggested_keywords=["   "]))
        self.assertEqual(MAX_KEYWORDS, 20)

    def test_authoritative_must_stay_false(self):
        with self.assertRaisesRegex(ValueError, "never becomes a record by itself"):
            validate_advisory_suggestion(suggestion(authoritative=True))
        with self.assertRaisesRegex(ValueError, "thread_id must derive"):
            validate_advisory_suggestion(suggestion(thread_id="thread:pubmed:other"))


class FailureSchemaTests(unittest.TestCase):
    def test_valid_outage_failure_roundtrip(self):
        parsed = record_advisory_failure(failure())
        self.assertTrue(parsed["manual_operation_required"])
        self.assertIsNone(parsed["prompt_revision"])
        self.assertEqual(parsed["failure_reason"], "ai_outage")

    def test_manual_operation_and_reason_enforced(self):
        with self.assertRaisesRegex(ValueError, "manual_operation_required"):
            record_advisory_failure(failure(manual_operation_required=False))
        with self.assertRaisesRegex(ValueError, "failure_reason must be"):
            record_advisory_failure(failure(failure_reason="retry_later"))
        with self.assertRaisesRegex(ValueError, "outside the bounded schema"):
            record_advisory_failure(failure(model_output_raw="huge dumped text"))
        with self.assertRaisesRegex(ValueError, "failure_detail"):
            record_advisory_failure(failure(failure_detail="   "))
        with self.assertRaisesRegex(ValueError, "authoritative must be false"):
            record_advisory_failure(failure(authoritative=True))


class ConsumeTests(unittest.TestCase):
    def consume(self, payload, **kwargs):
        kwargs.setdefault("expected_prompt_revision", 3)
        kwargs.setdefault("expected_source_revision", 7)
        kwargs.setdefault("advisory_id", "adv-1")
        kwargs.setdefault("publication_key", "pubmed:39751157")
        kwargs.setdefault("failure_on", "2026-10-23")
        return consume_advisory_output(payload, **kwargs)

    def test_valid_payload_bound_to_expected_revisions(self):
        result = self.consume(suggestion())
        self.assertEqual(result["outcome"], "advisory_only")
        self.assertFalse(result["record"]["authoritative"])
        self.assertTrue(result["curator_decision_required"])
        self.assertTrue(result["manual_operation_required"])

    def test_stale_prompt_revision_falls_back_to_manual(self):
        result = self.consume(suggestion(prompt_revision=2))
        self.assertEqual(result["outcome"], "fallback_manual")
        self.assertEqual(result["record"]["failure_reason"], "stale_advisory")
        self.assertTrue(result["record"]["manual_operation_required"])

    def test_stale_source_revision_falls_back_to_manual(self):
        result = self.consume(suggestion(source_revision=8))
        self.assertEqual(result["record"]["failure_reason"], "stale_advisory")
        self.assertEqual(result["record"]["source_revision"], 8)

    def test_malformed_payload_falls_back_invalid_output(self):
        result = self.consume({"unexpected": "shape"})
        self.assertEqual(result["record"]["failure_reason"], "invalid_output")
        result = self.consume(None)
        self.assertEqual(result["record"]["failure_reason"], "invalid_output")

    def test_preannotated_outage_failure_passes_through_validated(self):
        result = self.consume(failure())
        self.assertEqual(result["outcome"], "fallback_manual")
        self.assertEqual(result["record"]["failure_reason"], "ai_outage")

    def test_mismatched_publication_target_falls_back(self):
        result = self.consume(
            suggestion(publication_key="pubmed:999",
                       thread_id=stable_thread_id("pubmed:999")))
        self.assertEqual(result["record"]["failure_reason"], "stale_advisory")

    def test_fallback_records_fail_closed_on_corrupt_revision_integers(self):
        payload = suggestion()
        payload["prompt_revision"] = "three"
        result = self.consume(payload)
        self.assertEqual(result["record"]["failure_reason"], "invalid_output")


class PreparationSchemaParityTests(unittest.TestCase):
    """Field-for-field parity with contracts/e09-feed-preparation.schema.json."""

    def _schema(self):
        import json
        from pathlib import Path
        path = Path(__file__).parents[1] / "contracts/e09-feed-preparation.schema.json"
        if not path.exists():
            self.skipTest("preparation schema file is absent")
        return json.loads(path.read_text(encoding="utf-8"))

    def test_field_sets_match_runtime_when_schema_present(self):
        from scripts.e09_advisory_consumer import ADVISORY_FIELDS, FAILURE_FIELDS
        schema = self._schema()
        definitions = schema.get("$defs") or {}
        mapping = {
            "advisory suggestion": (ADVISORY_FIELDS, definitions.get("advisory_suggestion")),
            "advisory failure": (FAILURE_FIELDS, definitions.get("advisory_failure")),
        }
        for name, (fields, definition) in mapping.items():
            self.assertIsNotNone(definition, f"schema definition {name} missing")
            self.assertEqual(set(definition.get("required", [])), fields, f"required drift for {name}")
            self.assertEqual(set(definition.get("properties", {})), fields, f"properties drift for {name}")

    def test_fixtures_conform_when_jsonschema_installed(self):
        try:
            import jsonschema
        except ImportError:
            self.skipTest("jsonschema not installed")
        schema = self._schema()
        for name, records in (
            ("advisory_suggestion", [suggestion()]),
            ("advisory_failure", [failure(), failure(failure_reason="stale_advisory",
                                                  prompt_revision=3, source_revision=7)]),
        ):
            definition = {
                "$schema": schema["$schema"],
                "$ref": f"#/$defs/{name}",
                "$defs": schema["$defs"],
            }
            for record in records:
                jsonschema.validate(record, definition)


if __name__ == "__main__":
    unittest.main()
