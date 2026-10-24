import unittest
import json
import tempfile
from pathlib import Path

from scripts.reconcile_pubmed_registry_keys import reconcile, rows


class PubMedRegistryReconciliationTests(unittest.TestCase):
    def test_exact_keys_and_pmid_pass(self):
        model = [{"PMID": "123"}, {"[SourceKey]": "pubmed:456"}]
        registry = [{"SourceKey": "pubmed:123", "PMID": "123"},
                    {"SourceKey": "pubmed:456", "PMID": "456"},
                    {"SourceKey": "dora:other", "PMID": ""}]
        self.assertTrue(reconcile(model, registry)["pass"])

    def test_missing_extra_duplicates_and_rounded_pmid_fail(self):
        model = [{"PMID": "123"}, {"PMID": "123"}, {"PMID": "456"}]
        registry = [{"SourceKey": "pubmed:123", "PMID": "120"},
                    {"SourceKey": "pubmed:789", "PMID": "789"},
                    {"SourceKey": "pubmed:789", "PMID": "789"}]
        result = reconcile(model, registry)
        self.assertFalse(result["pass"])
        self.assertEqual(result["missing_in_registry"], ["pubmed:456"])
        self.assertEqual(result["extra_in_registry"], ["pubmed:789"])
        self.assertEqual(result["model_duplicate_keys"], ["pubmed:123"])
        self.assertEqual(result["registry_duplicate_keys"], ["pubmed:789"])
        self.assertEqual(result["registry_pmid_mismatches"], ["pubmed:123"])

    def test_invalid_identity_fails_closed(self):
        with self.assertRaises(ValueError):
            reconcile([{"PMID": "1.23E7"}], [])

    def test_empty_exports_do_not_pass(self):
        self.assertFalse(reconcile([], [])["pass"])

    def test_bracketed_field_is_used_when_plain_field_is_null(self):
        result = reconcile([{"SourceKey": None, "[SourceKey]": "pubmed:123"}],
                           [{"SourceKey": None, "[SourceKey]": "pubmed:123", "PMID": "123"}])
        self.assertTrue(result["pass"])

    def test_unkeyed_registry_pmid_cannot_be_silently_ignored(self):
        result = reconcile([{"PMID": "123"}],
                           [{"SourceKey": "pubmed:123", "PMID": "123"},
                            {"SourceKey": "", "PMID": "456"}])
        self.assertFalse(result["pass"])
        self.assertEqual(result["registry_unkeyed_pmid_rows"], ["456"])

    def test_noncanonical_source_key_fails_closed(self):
        with self.assertRaises(ValueError):
            reconcile([{"SourceKey": "PubMed:123"}], [])

    def test_conflicting_export_column_forms_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "conflicting SourceKey"):
            reconcile([{"SourceKey": "pubmed:123", "[SourceKey]": "pubmed:456"}],
                      [{"SourceKey": "pubmed:123", "PMID": "123"}])

    def test_input_requires_complete_paginated_export(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "export.json"
            for payload in ([{"PMID": "123"}],
                            {"rows": [{"PMID": "123"}], "complete": False},
                            {"rows": [{"PMID": "123"}], "complete": True,
                             "next_links": ["more"]},
                            {"rows": [{"PMID": "123"}], "complete": True},
                            {"rows": [{"PMID": "123"}], "complete": True,
                             "next_links": None},
                            {"rows": [{"PMID": "123"}], "complete": True,
                             "row_count": 2}):
                path.write_text(json.dumps(payload), encoding="utf-8")
                with self.assertRaises(ValueError):
                    rows(path)
            path.write_text(json.dumps({"rows": [{"PMID": "123"}],
                                        "complete": True, "row_count": 1,
                                        "next_links": []}), encoding="utf-8")
            self.assertEqual(rows(path), [{"PMID": "123"}])

    def test_model_pmid_disagreement_cannot_pass_equal_key_sets(self):
        result = reconcile([{"SourceKey": "pubmed:123", "PMID": "456"}],
                           [{"SourceKey": "pubmed:123", "PMID": "123"}])
        self.assertFalse(result["pass"])
        self.assertEqual(result["model_pmid_mismatches"], ["pubmed:123"])

    def test_key_hashes_are_order_independent_and_multiset_exposes_duplicates(self):
        left = reconcile([{"PMID": "123"}, {"PMID": "456"}],
                         [{"SourceKey": "pubmed:123", "PMID": "123"},
                          {"SourceKey": "pubmed:456", "PMID": "456"}])
        reordered = reconcile([{"PMID": "456"}, {"PMID": "123"}],
                              [{"SourceKey": "pubmed:456", "PMID": "456"},
                               {"SourceKey": "pubmed:123", "PMID": "123"}])
        self.assertEqual(left["model_key_set_sha256"], reordered["model_key_set_sha256"])
        self.assertEqual(left["registry_key_multiset_sha256"],
                         reordered["registry_key_multiset_sha256"])
        duplicate = reconcile([{"PMID": "123"}, {"PMID": "123"}, {"PMID": "456"}],
                              [{"SourceKey": "pubmed:123", "PMID": "123"},
                               {"SourceKey": "pubmed:456", "PMID": "456"}])
        self.assertEqual(left["model_key_set_sha256"], duplicate["model_key_set_sha256"])
        self.assertNotEqual(left["model_key_multiset_sha256"],
                            duplicate["model_key_multiset_sha256"])


if __name__ == "__main__":
    unittest.main()
