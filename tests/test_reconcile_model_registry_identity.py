import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.reconcile_model_registry_identity import _rows, compare


def model(key="PMID:123", pmid="123"):
    is_dora = key.startswith("DORA:")
    return {"[CanonicalKey]": key, "[PMID]": pmid,
            "[DORAURL]": "https://example.org/source" if is_dora else None,
            "[SourceSet]": "DORA" if is_dora else "PubMed"}


def registry(key="PUB:durable-one", pmid="123", source="pubmed:123", status="Included"):
    return {"Id": "1", "CanonicalKey": key, "PMID": pmid, "SourceKey": source, "ReviewStatus": status}


class TypedIdentityTests(unittest.TestCase):
    def test_typed_crosswalk_preserves_durable_pub_key_and_exact_dora(self):
        m = [model(), model("DORA:https://example.org/one", None),
             model("DORA:https://example.org/two", "789")]
        r = [registry(), registry("DORA:https://example.org/one", None, "dora:one"),
             registry("DORA:https://example.org/two", "789", "pubmed:789"),
             registry("", None, "")]
        receipt, differences = compare(m, r)
        self.assertEqual(receipt["status"], "PASS")
        self.assertEqual(receipt["counts"]["matched_typed_identities"], 3)
        self.assertEqual(receipt["counts"]["matched_exact_canonical_keys"], 2)
        self.assertEqual(receipt["counts"]["matched_different_canonical_representations"], 1)
        self.assertEqual(receipt["counts"]["model_pubmed_only_rows"], 1)
        self.assertEqual(receipt["counts"]["model_dora_rows"], 2)
        self.assertEqual(receipt["counts"]["registry_blank_sourcekey_rows"], 1)
        self.assertEqual(differences, {"model_only": [], "registry_only": [], "invalid": []})
        self.assertEqual(r[0]["CanonicalKey"], "PUB:durable-one")

    def test_review_only_gap_and_sentinel_fail_without_coercion(self):
        receipt, differences = compare(
            [model()], [registry(), registry("PMID:456", "456", "pubmed:456", "Needs Review"),
                        registry("PUB:old-dora-alias", "0", "dora:1/1")])
        self.assertEqual(receipt["status"], "FAIL")
        self.assertEqual(receipt["counts"]["registry_only_typed_identities"], 1)
        self.assertEqual(receipt["counts"]["registry_invalid_rows"], 1)
        self.assertEqual(differences["registry_only"][0]["TypedIdentity"], "PMID:456")
        self.assertEqual(differences["invalid"][0]["row"]["CanonicalKey"], "PUB:old-dora-alias")

    def test_duplicates_fail_closed(self):
        cases = [([model(), model()], [registry()]),
                 ([model()], [registry(), registry("PUB:other", "123", "pubmed:123")]),
                 ([model()], [registry(), registry("PUB:durable-one", "456", "pubmed:456")]),
                 ([model("DORA:x", None), model("DORA:x", None)], [registry("DORA:x", None, "dora:x")])]
        for m, r in cases:
            with self.subTest(m=m, r=r), self.assertRaisesRegex(ValueError, "duplicate"):
                compare(m, r)

    def test_malformed_positive_pmid_and_dora_identity_fail(self):
        bad_model = [model("PMID:01", "01"), model("DORA:bad key", None), model("PMID:123", "456")]
        bad_registry = [registry("PUB:one", "01", "pubmed:01"),
                        registry("DORA:bad key", None, "dora:x"),
                        registry("PUB:two", "0", "pubmed:0")]
        receipt, differences = compare(bad_model, bad_registry)
        self.assertEqual(receipt["status"], "FAIL")
        self.assertEqual(receipt["counts"]["model_invalid_rows"], 3)
        self.assertEqual(receipt["counts"]["registry_invalid_rows"], 3)
        self.assertEqual(len(differences["invalid"]), 6)

    def test_model_provenance_must_agree_with_identity_and_dora_url(self):
        cases = [
            (dict(model(), **{"[SourceSet]": "PubMed; DORA"}), "PubMed source provenance mismatch"),
            (dict(model(), **{"[DORAURL]": "https://example.org/source"}), "PubMed source provenance mismatch"),
            (dict(model("DORA:x", None), **{"[DORAURL]": None}), "DORA source provenance mismatch"),
            (dict(model("DORA:x", None), **{"[SourceSet]": "PubMed"}), "DORA source provenance mismatch"),
        ]
        for row, reason in cases:
            with self.subTest(reason=reason, row=row):
                receipt, differences = compare([row], [registry()])
                self.assertEqual(receipt["status"], "FAIL")
                self.assertEqual(differences["invalid"][0]["reason"], reason)
        both = dict(model(), **{"[SourceSet]": "PubMed; DORA", "[DORAURL]": "https://example.org/source"})
        receipt, differences = compare([both], [registry()])
        self.assertEqual(receipt["status"], "PASS")
        self.assertEqual(receipt["counts"]["model_pubmed_dora_rows"], 1)
        self.assertEqual(differences["invalid"], [])

    def test_incomplete_or_failed_exports_rejected(self):
        for payload in ({"complete": False, "next_links": [], "rows": [registry()]},
                        {"complete": True, "next_links": ["more"], "rows": [registry()]}):
            with self.assertRaisesRegex(ValueError, "complete registry"):
                _rows(payload, "registry")
        with self.assertRaisesRegex(ValueError, "successful model"):
            _rows({"error": {"code": "failed"}, "results": []}, "model")

    def test_cli_writes_aggregate_and_opt_in_private_detail(self):
        root = Path(__file__).resolve().parent.parent
        (root / "private").mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=root / "private") as directory:
            folder = Path(directory)
            model_path, registry_path, out_path, details = [folder / name for name in
                ("model.json", "registry.json", "receipt.json", "details.json")]
            model_path.write_text(json.dumps({"results": [{"tables": [{"rows": [model()]}]}]}))
            registry_path.write_text(json.dumps({"complete": True, "next_links": [], "rows": [
                registry(), registry("PMID:456", "456", "pubmed:456", "Needs Review")]}))
            command = [sys.executable, str(root / "scripts/reconcile_model_registry_identity.py"),
                       "--model", str(model_path), "--registry", str(registry_path),
                       "--output", str(out_path)]
            run = subprocess.run(command, cwd=root, capture_output=True, text=True)
            self.assertEqual(run.returncode, 1, run.stderr)
            aggregate = json.loads(out_path.read_text())
            self.assertEqual(aggregate["status"], "FAIL")
            self.assertNotIn("456", out_path.read_text())
            self.assertFalse(details.exists())
            run = subprocess.run(command + ["--differences", str(details)], cwd=root,
                                 capture_output=True, text=True)
            self.assertEqual(run.returncode, 1, run.stderr)
            self.assertEqual(json.loads(details.read_text())["registry_only"][0]["TypedIdentity"], "PMID:456")
            with tempfile.TemporaryDirectory() as outside:
                unsafe = Path(outside) / "differences.json"
                run = subprocess.run(command + ["--differences", str(unsafe)], cwd=root,
                                     capture_output=True, text=True)
                self.assertEqual(run.returncode, 2)
                self.assertFalse(unsafe.exists())


if __name__ == "__main__":
    unittest.main()
