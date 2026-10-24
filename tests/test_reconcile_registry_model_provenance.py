import unittest

from scripts.reconcile_registry_model_provenance import compare, _model_rows, _registry_rows


def registry(source="PubMed", key="pubmed:123", canonical="PUB:durable", pmid="123"):
    return {"Id": 1, "SourceKey": key, "CanonicalKey": canonical, "SourceSet": source,
            "PMID": pmid, "DORAURL": None, "ReviewStatus": "Included"}


def model(source="PubMed"):
    return {"[CanonicalKey]": "PMID:123", "[PMID]": "123", "[SourceSet]": source,
            "[DORAURL]": "https://example.org/dora" if "DORA" in source else None}


class ProvenanceTests(unittest.TestCase):
    def test_exact_primary_classification(self):
        receipt, detail = compare([registry()], [model()])
        self.assertEqual(receipt["status"], "PASS_KEYED_PRIMARY_COVERAGE")
        self.assertEqual(receipt["counts"]["matched_exact_source_classification"], 1)
        self.assertEqual(detail["model_additional_membership"], [])

    def test_derived_co_membership_not_registry_admission(self):
        receipt, detail = compare([registry()], [model("PubMed; DORA")])
        self.assertEqual(receipt["status"], "PASS_KEYED_PRIMARY_COVERAGE")
        self.assertEqual(receipt["counts"]["matched_model_additional_membership"], 1)
        self.assertFalse(detail["model_additional_membership"][0]["registry_dora_url_present"])

    def test_primary_missing_requires_review(self):
        receipt, detail = compare([registry("DORA")], [model("PubMed")])
        self.assertEqual(receipt["status"], "REVIEW_REQUIRED")
        self.assertEqual(detail["primary_missing_from_model"], ["PMID:123"])

    def test_legacy_dora_pub_sentinel_not_coerced(self):
        receipt, detail = compare([registry("DORA", "dora:1/abc", "PUB:durable", "0")], [model()])
        self.assertEqual(receipt["status"], "REVIEW_REQUIRED")
        self.assertEqual(receipt["counts"]["registry_invalid"], 1)
        self.assertEqual(detail["model_only"], ["PMID:123"])

    def test_incomplete_or_projected_inputs_rejected(self):
        payload = {"complete": False, "total_rows": 2, "keyed_total": 1, "keyed_rows": [registry()]}
        with self.assertRaisesRegex(ValueError, "complete registry"):
            _registry_rows(payload)
        payload["complete"] = True
        del payload["keyed_rows"][0]["SourceSet"]
        with self.assertRaisesRegex(ValueError, "missing required fields"):
            _registry_rows(payload)
        with self.assertRaisesRegex(ValueError, "projection"):
            _model_rows({"results": [{"tables": [{"rows": [{"[CanonicalKey]": "PMID:123"}]}]}]})

    def test_duplicate_typed_identity_rejected(self):
        duplicate = registry("PubMed", "pubmed:123", "PUB:other")
        with self.assertRaisesRegex(ValueError, "duplicate"):
            compare([registry(), duplicate], [model()])

    def test_case_only_source_key_collision_rejected_before_unique_migration(self):
        other = registry("PubMed", "PubMed:123", "PUB:other")
        with self.assertRaisesRegex(ValueError, "case-insensitive duplicate registry source/canonical key"):
            compare([registry(), other], [model()])

    def test_case_only_registry_canonical_collision_rejected(self):
        other = registry("DORA", "dora:other", "pub:durable", "")
        with self.assertRaisesRegex(ValueError, "case-insensitive duplicate registry CanonicalKey"):
            compare([registry(), other], [model()])

    def test_non_text_registry_identity_fields_fail_closed(self):
        for field, value in (("Id", True), ("SourceKey", 123),
                             ("CanonicalKey", ["PUB:one"]), ("PMID", 123),
                             ("SourceSet", {"PubMed"}), ("ReviewStatus", 12)):
            row = registry()
            row[field] = value
            with self.subTest(field=field):
                receipt, detail = compare([row], [model()])
                self.assertEqual(receipt["status"], "REVIEW_REQUIRED")
                self.assertEqual(receipt["counts"]["registry_invalid"], 1)
                self.assertEqual(detail["invalid"][0]["side"], "registry")

    def test_non_text_model_identity_fields_fail_closed_without_throwing(self):
        for field, value in (("[CanonicalKey]", 123), ("[PMID]", ["123"]),
                             ("[SourceSet]", {"PubMed"}), ("[DORAURL]", 7)):
            row = model()
            row[field] = value
            with self.subTest(field=field):
                receipt, detail = compare([registry()], [row])
                self.assertEqual(receipt["status"], "REVIEW_REQUIRED")
                self.assertEqual(receipt["counts"]["model_invalid"], 1)


if __name__ == "__main__":
    unittest.main()
