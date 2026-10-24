import json
import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.reconcile_publication_sources import membership_rows, reconcile, retained_rows, reconcile_automatic


def member(source, source_id, key):
    return {"Source": source, "SourceID": source_id, "Disposition": "admitted", "CanonicalSourceKey": key,
            "ReviewStatus": "Reviewed", "ReviewEvidenceRef": "private/review/item-1"}


def not_admitted(source, source_id):
    return {"Source": source, "SourceID": source_id, "Disposition": "not_admitted",
            "DispositionReason": "Outside reviewed registry scope",
            "ReviewStatus": "Reviewed", "ReviewEvidenceRef": "private/review/item-2"}


def envelope(rows, digest="a" * 64):
    return {"kind": "reviewed_archive_member_dispositions_v2", "complete": True,
            "next_links": [], "row_count": len(rows), "rows": rows,
            "review_provenance": {"reviewer": "reviewer-1", "reviewed_at_utc": "2026-09-25T00:00:00Z",
                                  "evidence_ref": "private/review/batch-1",
                                  "retained_export_sha256": digest}}


def archive(rows):
    return {"kind": "committed_archive_source_members_v1", "complete": True,
            "next_links": [], "row_count": len(rows),
            "rows": [{"Source": row["Source"], "SourceID": row["SourceID"]} for row in rows]}


class PublicationSourceReconciliationTests(unittest.TestCase):
    def test_cli_requires_reviewed_membership_and_writes_private_receipt(self):
        root = Path(__file__).resolve().parent.parent
        (root / "private").mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=root / "private") as directory:
            folder = Path(directory)
            membership = folder / "membership.json"
            retained = folder / "retained.json"
            registry = folder / "registry.json"
            receipt = folder / "receipt.json"
            members = [
                member("PubMed", "123", "pubmed:123"),
                member("DORA", "DORA:https://example.org/one", "pubmed:123"),
                member("DORA", "DORA:https://example.org/two", "dora:two"),
            ]
            retained.write_text(json.dumps(archive(members)))
            digest = hashlib.sha256(retained.read_bytes()).hexdigest()
            membership.write_text(json.dumps(envelope(members, digest)))
            registry.write_text(json.dumps({"complete": True, "next_links": [], "row_count": 3,
                                            "rows": [{"SourceKey": "pubmed:123"},
                                                     {"SourceKey": "dora:two"},
                                                     {"SourceKey": "pubmed:456"}]}))
            command = [sys.executable, str(root / "scripts/reconcile_publication_sources.py"),
                       "--membership", str(membership), "--registry", str(registry),
                       "--retained", str(retained),
                       "--output", str(receipt)]
            result = subprocess.run(command, cwd=root, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("PASS_ARCHIVE_SUBSET_ONLY", result.stdout)
            report = json.loads(receipt.read_text())
            self.assertTrue(report["pass"])
            self.assertEqual(report["disposition_rows"], 3)
            self.assertEqual(report["admitted_canonical_keys"], 2)
            self.assertEqual(report["admitted_multi_member_keys"], ["pubmed:123"])
            self.assertEqual(report["archive_source_rows"], 3)
            self.assertEqual(report["retained_export_sha256"], digest)
            old_cli = subprocess.run([sys.executable, str(root / "scripts/reconcile_publication_sources.py"),
                                      "--retained", str(membership), "--registry", str(registry),
                                      "--output", str(receipt)], cwd=root, capture_output=True, text=True)
            self.assertNotEqual(old_cli.returncode, 0)

    def test_raw_retained_rows_and_unreviewed_mapping_rejected(self):
        row = member("DORA", "DORA:https://example.org/one", "dora:one")
        for payload in (
            {"complete": True, "next_links": [], "row_count": 1, "rows": [row]},
            {**envelope([row]), "review_provenance": {}},
            envelope([{**row, "ReviewStatus": "Candidate"}]),
        ):
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                selected = membership_rows(payload)
                reconcile(selected, [{"SourceKey": "dora:one"}], retained_rows(archive([row])))

    def test_many_to_one_and_blank_registry_stub(self):
        members = [member("PubMed", "123", "pubmed:123"),
                   member("DORA", "DORA:https://example.org/one", "pubmed:123")]
        report = reconcile(membership_rows(envelope(members)),
                           [{"SourceKey": "pubmed:123"}, {"SourceKey": ""}], retained_rows(archive(members)))
        self.assertTrue(report["pass"])
        self.assertEqual(report["blank_registry_rows"], 1)

    def test_duplicate_member_and_guessed_dora_identity_rejected(self):
        row = member("DORA", "DORA:https://example.org/one", "dora:one")
        for members in ([row, row], [member("DORA", "https://example.org/one", "dora:one")]):
            with self.subTest(members=members), self.assertRaises(ValueError):
                reconcile(membership_rows(envelope(members)), [{"SourceKey": "dora:one"}], retained_rows(archive(members)))

    def test_canonical_gap_and_duplicate_registry_fail(self):
        members = [member("PubMed", "123", "pubmed:123"),
                   member("DORA", "DORA:https://example.org/one", "dora:one")]
        report = reconcile(membership_rows(envelope(members)),
                           [{"SourceKey": "pubmed:123"}, {"SourceKey": "dora:two"},
                            {"SourceKey": "dora:two"}], retained_rows(archive(members)))
        self.assertFalse(report["pass"])
        self.assertEqual(report["by_namespace"]["dora"]["missing_in_registry"], ["dora:one"])
        self.assertEqual(report["registry_duplicate_keys"], ["dora:two"])

    def test_review_must_cover_exact_archive_members(self):
        reviewed = [member("PubMed", "123", "pubmed:123")]
        archive_members = reviewed + [member("DORA", "DORA:https://example.org/one", "pubmed:123")]
        report = reconcile(membership_rows(envelope(reviewed)),
                           [{"SourceKey": "pubmed:123"}], retained_rows(archive(archive_members)))
        self.assertFalse(report["pass"])
        self.assertEqual(report["unreviewed_archive_members"], [("DORA", "DORA:https://example.org/one")])

    def test_explicit_exclusion_preserves_archive_coverage_and_registry_boundary(self):
        members = [member("PubMed", "123", "pubmed:123"),
                   not_admitted("DORA", "DORA:https://example.org/not-admitted")]
        report = reconcile(membership_rows(envelope(members)),
                           [{"SourceKey": "pubmed:123"}, {"SourceKey": "pubmed:456"}],
                           retained_rows(archive(members)))
        self.assertTrue(report["pass"])
        self.assertEqual(report["archive_source_rows"], 2)
        self.assertEqual(report["admitted_member_rows"], 1)
        self.assertEqual(report["not_admitted_member_rows"], 1)
        self.assertEqual(report["by_namespace"]["pubmed"]["registry_not_in_committed_archive"], ["pubmed:456"])
        self.assertTrue(report["archive_disposition_coverage_pass"])
        self.assertTrue(report["committed_archive_to_registry_pass"])
        self.assertTrue(report["registry_not_in_committed_archive_requires_provenance"])
        self.assertEqual(report["status"], "PASS_ARCHIVE_SUBSET_ONLY")

    def test_excluded_direct_identity_in_registry_fails_for_both_sources(self):
        for excluded, direct_key in (
            (not_admitted("PubMed", "456"), "pubmed:456"),
            (not_admitted("DORA", "DORA:https://example.org/one"), "dora:https://example.org/one"),
        ):
            members = [member("PubMed", "123", "pubmed:123"), excluded]
            with self.subTest(excluded=excluded):
                report = reconcile(membership_rows(envelope(members)),
                                   [{"SourceKey": "pubmed:123"}, {"SourceKey": direct_key}],
                                   retained_rows(archive(members)))
                self.assertTrue(report["archive_disposition_coverage_pass"])
                self.assertFalse(report["committed_archive_to_registry_pass"])
                self.assertEqual(report["status"], "FAIL")
                self.assertEqual(report["not_admitted_direct_keys_in_registry"],
                                 [(excluded["Source"], excluded["SourceID"], direct_key)])

    def test_exclusion_requires_reason_and_forbids_canonical_key(self):
        row = not_admitted("DORA", "DORA:https://example.org/one")
        for invalid in ({**row, "DispositionReason": ""},
                        {**row, "CanonicalSourceKey": "dora:one"},
                        {**row, "ReviewEvidenceRef": ""},
                        {**row, "Disposition": "pending"}):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                reconcile(membership_rows(envelope([invalid])),
                          [{"SourceKey": "pubmed:456"}], retained_rows(archive([row])))

    def test_cli_rejects_review_bound_to_different_archive_export(self):
        root = Path(__file__).resolve().parent.parent
        (root / "private").mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=root / "private") as directory:
            folder = Path(directory)
            item = member("PubMed", "123", "pubmed:123")
            membership, retained, registry, receipt = (folder / name for name in
                ("membership.json", "retained.json", "registry.json", "receipt.json"))
            membership.write_text(json.dumps(envelope([item])))
            retained.write_text(json.dumps(archive([item])))
            registry.write_text(json.dumps({"complete": True, "next_links": [], "row_count": 1,
                                            "rows": [{"SourceKey": "pubmed:123"}]}))
            result = subprocess.run([sys.executable, str(root / "scripts/reconcile_publication_sources.py"),
                                     "--membership", str(membership), "--retained", str(retained),
                                     "--registry", str(registry), "--output", str(receipt)],
                                    cwd=root, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("digest differs", result.stderr)
            self.assertFalse(receipt.exists())

    def test_retained_export_rejects_incomplete_and_duplicate_members(self):
        member_row = member("PubMed", "123", "pubmed:123")
        with self.assertRaises(ValueError):
            retained_rows({**archive([member_row]), "complete": False})
        with self.assertRaises(ValueError):
            reconcile(membership_rows(envelope([member_row])), [{"SourceKey": "pubmed:123"}],
                      retained_rows(archive([member_row, member_row])))


if __name__ == "__main__":
    unittest.main()


class AutomaticPublicationReconciliationTests(unittest.TestCase):
    def test_cli_defaults_to_automatic_without_review_overlay(self):
        root = Path(__file__).resolve().parents[1]
        (root / "private").mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=root / "private") as directory:
            folder = Path(directory)
            retained, registry, output = (folder / n for n in ("archive.json", "registry.json", "receipt.json"))
            retained.write_text(json.dumps(archive([member("PubMed", "123", "pubmed:123")])))
            registry.write_text(json.dumps({"complete": True, "next_links": [], "rows": [{"SourceKey": "pubmed:123", "ReviewStatus": "Needs Review"}]}))
            run = subprocess.run([sys.executable, str(root / "scripts/reconcile_publication_sources.py"), "--retained", str(retained), "--registry", str(registry), "--output", str(output)], cwd=root, capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            report = json.loads(output.read_text())
            self.assertEqual(report["status"], "PASS_AUTOMATIC_SOURCE_KEY_PARITY")
            self.assertFalse(report["manual_record_approval_required"])
            self.assertFalse(report["native_acceptance"])

    def test_corroborated_sources_remain_separate_identities(self):
        retained = [{"Source": "PubMed", "SourceID": "123"}, {"Source": "DORA", "SourceID": "DORA:https://example.org/one"}]
        report = reconcile_automatic([{"SourceKey": "pubmed:123", "DORAURL": "https://example.org/one"}], retained)
        self.assertFalse(report["pass"])
        self.assertEqual(report["missing_in_registry"], ["dora:https://example.org/one"])
        report = reconcile_automatic([{"SourceKey": "pubmed:123"}, {"SourceKey": "dora:https://example.org/one"}], retained)
        self.assertTrue(report["pass"])

    def test_missing_extra_duplicate_and_blank_rows_fail_full_parity(self):
        retained = [{"Source": "PubMed", "SourceID": "123"}]
        for registry in ([], [{"SourceKey": "pubmed:123"}, {"SourceKey": "pubmed:456"}], [{"SourceKey": "pubmed:123"}] * 2, [{"SourceKey": "pubmed:123"}, {}]):
            with self.subTest(registry=registry):
                self.assertFalse(reconcile_automatic(registry, retained)["pass"])

    def test_malformed_keys_and_duplicate_archive_members_rejected(self):
        retained = [{"Source": "PubMed", "SourceID": "123"}]
        for key in (" pubmed:123", "pubmed:123 ", 123, "PubMed:123"):
            with self.subTest(key=key), self.assertRaises(ValueError):
                reconcile_automatic([{"SourceKey": key}], retained)
        with self.assertRaises(ValueError):
            reconcile_automatic([{"SourceKey": "pubmed:123"}], retained * 2)
