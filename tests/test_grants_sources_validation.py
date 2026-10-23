import json
import copy
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from scripts.grants_sources import load_catalogue


ROOT = Path(__file__).resolve().parents[1]
QUALIFICATION = {
    "observed_at": "2026-10-23T10:00:00+10:00",
    **{
        field: {
            "status": "verified",
            "evidence_refs": ["https://example.org/schema"],
            **({"decision": "public"} if field == "access" else {}),
            **({"decision": "permitted"} if field == "reuse_terms" else {}),
        }
        for field in ("access", "response_schema", "bounded_sample", "complete_pagination", "replay_keyset",
                      "stable_identity", "round_semantics", "lifecycle_semantics", "reuse_terms",
                      "entity_reconciliation")
    },
}


class GrantsSourceCatalogueValidationTests(unittest.TestCase):
    def _load_with_change(self, changes):
        rows = json.loads((ROOT / "config/grants-sources.json").read_text(encoding="utf-8"))
        reconciliation = changes.get("reconciliation")
        generic_opportunity = (
            isinstance(reconciliation, dict)
            and reconciliation.get("admission") == "opportunity"
        )
        if generic_opportunity:
            candidate = copy.deepcopy(rows[0])
            candidate["source_id"] = "test-opportunity-api"
            candidate.update(changes)
            rows.append(candidate)
        else:
            rows[0].update(changes)
        with TemporaryDirectory() as directory:
            path = Path(directory) / "catalogue.json"
            path.write_text(json.dumps(rows), encoding="utf-8")
            return load_catalogue(path)

    def _load_with_url(self, field, value):
        return self._load_with_change({field: value})

    def test_official_catalogue_urls_still_validate(self):
        rows = load_catalogue(ROOT / "config/grants-sources.json")
        self.assertEqual(len(rows), 4)
        rgs = next(row for row in rows if row["source_id"] == "arc-rgs-awards-api")
        self.assertFalse(rgs["enabled"])
        self.assertEqual(rgs["reconciliation"]["admission"], "context_only")
        qgip = next(row for row in rows if row["source_id"] == "queensland-health-qgip-review-candidates-api")
        self.assertEqual(qgip["qualification"]["stable_identity"]["status"], "partial")
        self.assertEqual(qgip["qualification"]["lifecycle_semantics"]["status"], "unverified")

    def test_enabled_state_must_be_explicit_boolean(self):
        for value in (None, "true", 1):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "boolean enabled state"):
                self._load_with_change({"enabled": value})

    def test_grants_finder_contribution_index_stays_metadata_only(self):
        rows = load_catalogue(ROOT / "config/grants-sources.json")
        source = next(row for row in rows if row["source_id"] == "queensland-grants-finder-catalogue-api")
        index = source["contribution_resource_index"]
        self.assertEqual(index["records_observed"], 25)
        self.assertEqual(index["source_id_path"], "result.records[].Resource")
        self.assertEqual(index["admission"], "metadata_only")
        self.assertEqual(source["reconciliation"]["admission"], "metadata_only")
        self.assertEqual(
            index["resource_id"],
            "cca41845-9898-4efe-9ca0-17fbd44a3321",
        )

    def test_canonical_awards_and_catalogue_sources_cannot_be_reclassified(self):
        rows = json.loads((ROOT / "config/grants-sources.json").read_text(encoding="utf-8"))
        arc = next(row for row in rows if row["source_id"] == "arc-awards-api")
        arc["reconciliation"].update({"entity": "opportunity", "admission": "opportunity"})
        arc["official_row_hosts"] = ["arc.gov.au"]
        arc["qualification"] = QUALIFICATION
        with TemporaryDirectory() as directory:
            path = Path(directory) / "catalogue.json"
            path.write_text(json.dumps(rows), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "immutable non-opportunity entity class"):
                load_catalogue(path)

        rows = json.loads((ROOT / "config/grants-sources.json").read_text(encoding="utf-8"))
        finder = next(
            row for row in rows
            if row["source_id"] == "queensland-grants-finder-catalogue-api"
        )
        finder["record_kind"] = "opportunity"
        finder["reconciliation"].update({"entity": "opportunity", "admission": "opportunity"})
        finder["official_row_hosts"] = ["data.qld.gov.au"]
        finder["qualification"] = QUALIFICATION
        with TemporaryDirectory() as directory:
            path = Path(directory) / "catalogue.json"
            path.write_text(json.dumps(rows), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "immutable non-opportunity entity class"):
                load_catalogue(path)

    def test_catalogue_rejects_malformed_or_credentialed_https_urls(self):
        invalid = (
            "https://www.arc.gov.au@attacker.test/grants",
            "https://user:secret@dataportal.arc.gov.au/grants",
            "https://dataportal.arc.gov.au:444/grants",
            "https://dataportal.arc.gov.au:bad/grants",
            "https://dataportal.arc.gov.au /grants",
            "https:///missing-host",
        )
        for value in invalid:
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "HTTPS"):
                    self._load_with_url("api_url", value)

    def test_catalogue_does_not_coerce_source_identity_or_title_types(self):
        for changes, error in (
            ({"source_id": 42}, "source_id must be text"),
            ({"title": ["official source"]}, "HTTPS authority_url and title"),
            ({"authority_url": 42}, "HTTPS authority_url and title"),
            ({"api_url": ["https://dataportal.arc.gov.au/api"]}, "HTTPS api_url"),
        ):
            with self.subTest(changes=changes), self.assertRaisesRegex(ValueError, error):
                self._load_with_change(changes)

    def test_catalogue_rejects_blank_or_padded_source_ids(self):
        for source_id in ("", " ", " arc-awards-api", "arc-awards-api "):
            with self.subTest(source_id=source_id), self.assertRaisesRegex(
                ValueError, "source_id must be nonempty unpadded text"
            ):
                self._load_with_change({"source_id": source_id})

    def test_catalogue_rejects_blank_or_padded_stable_key_prefixes(self):
        for prefix in ("", " ", " arc:", "arc: "):
            with self.subTest(prefix=prefix), self.assertRaisesRegex(
                ValueError, "nonempty unpadded reconciliation stable_key_prefix"
            ):
                self._load_with_change({"reconciliation": {
                    "source_id_path": "data[].id",
                    "stable_key_prefix": prefix,
                    "admission": "context_only",
                    "entity": "test_context",
                }})

    def test_catalogue_identity_path_syntax_must_match_intake(self):
        for intake, path in (("api", " result.id"),
                             ("api", "result..id"),
                             ("rss", "entry[].id"),
                             ("atom", "channel.item[].guid"),
                             ("rss", "channel.item[].")):
            with self.subTest(intake=intake, path=path):
                with self.assertRaisesRegex(ValueError, "invalid reconciliation source_id_path"):
                    self._load_with_change({"intake": intake,
                                            "feed_url": "https://example.org/feed.xml",
                                            "reconciliation": {
                                                "source_id_path": path,
                                                "stable_key_prefix": "test:",
                                                "admission": "context_only",
                                                "entity": "test_context",
                                            }})

    def test_opportunity_admission_requires_opportunity_entity_and_row_hosts(self):
        for changes, error in (
            ({"reconciliation": {"source_id_path": "data[].id", "stable_key_prefix": "arc:",
                                  "admission": "opportunity", "entity": "awarded_grant"},
              "official_row_hosts": ["arc.gov.au"]}, "mismatched opportunity entity"),
            ({"reconciliation": {"source_id_path": "data[].id", "stable_key_prefix": "arc:",
                                  "admission": "opportunity", "entity": "opportunity"}},
             "official_row_hosts"),
            ({"reconciliation": {"source_id_path": "data[].id", "stable_key_prefix": "arc:",
                                  "admission": "opportunity", "entity": "opportunity"},
              "official_row_hosts": ["arc.gov.au@attacker.test"]}, "official_row_hosts"),
        ):
            with self.subTest(error=error), self.assertRaisesRegex(ValueError, error):
                self._load_with_change(changes)

    def test_opportunity_catalogue_admission_requires_all_source_proof(self):
        valid = self._load_with_change({
            "official_row_hosts": ["example.org"],
            "reconciliation": {"source_id_path": "data[].id", "stable_key_prefix": "opportunity:",
                               "admission": "opportunity", "entity": "opportunity"},
            "qualification": dict(QUALIFICATION),
        })
        self.assertEqual(valid[-1]["reconciliation"]["admission"], "opportunity")
        for field in QUALIFICATION:
            qualification = dict(QUALIFICATION)
            if field == "observed_at":
                qualification[field] = "2026-10-23T10:00:00"
            else:
                qualification[field] = {"status": "unverified", "evidence_refs": []}
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "source_qualification"):
                self._load_with_change({
                    "official_row_hosts": ["example.org"],
                    "reconciliation": {"source_id_path": "data[].id", "stable_key_prefix": "opportunity:",
                                       "admission": "opportunity", "entity": "opportunity"},
                    "qualification": qualification,
                })

    def test_bounded_sample_qualification_is_mandatory(self):
        qualification = json.loads(json.dumps(QUALIFICATION))
        del qualification["bounded_sample"]
        with self.assertRaisesRegex(ValueError, "source_qualification_status_invalid"):
            self._load_with_change({"qualification": qualification})

    def test_opportunity_catalogue_requires_per_field_evidence_references(self):
        for field in QUALIFICATION:
            if field == "observed_at":
                continue
            qualification = {**QUALIFICATION, field: {"status": "verified", "evidence_refs": []}}
            with self.subTest(field=field), self.assertRaisesRegex(
                ValueError, "source_qualification_evidence_invalid"
            ):
                self._load_with_change({
                    "official_row_hosts": ["example.org"],
                    "reconciliation": {"source_id_path": "data[].id", "stable_key_prefix": "opportunity:",
                                       "admission": "opportunity", "entity": "opportunity"},
                    "qualification": qualification,
                })

    def test_opportunity_admission_requires_permitted_reuse_decision(self):
        for decision in ("restricted", "not_permitted", "unresolved", "not_applicable"):
            qualification = json.loads(json.dumps(QUALIFICATION))
            qualification["reuse_terms"]["decision"] = decision
            with self.subTest(decision=decision), self.assertRaisesRegex(
                ValueError, "source_qualification_incomplete"
            ):
                self._load_with_change({
                    "official_row_hosts": ["example.org"],
                    "reconciliation": {"source_id_path": "data[].id", "stable_key_prefix": "opportunity:",
                                       "admission": "opportunity", "entity": "opportunity"},
                    "qualification": qualification,
                })

    def test_opportunity_admission_requires_qualified_access_decision(self):
        for decision in ("restricted", "unavailable", "unresolved", "not_applicable"):
            qualification = json.loads(json.dumps(QUALIFICATION))
            qualification["access"]["decision"] = decision
            with self.subTest(decision=decision), self.assertRaisesRegex(
                ValueError, "source_qualification_incomplete"
            ):
                self._load_with_change({
                    "official_row_hosts": ["example.org"],
                    "reconciliation": {"source_id_path": "data[].id", "stable_key_prefix": "opportunity:",
                                       "admission": "opportunity", "entity": "opportunity"},
                    "qualification": qualification,
                })

        qualification = json.loads(json.dumps(QUALIFICATION))
        qualification["access"]["decision"] = "existing_authorized"
        rows = self._load_with_change({
            "official_row_hosts": ["example.org"],
            "reconciliation": {"source_id_path": "data[].id", "stable_key_prefix": "opportunity:",
                               "admission": "opportunity", "entity": "opportunity"},
            "qualification": qualification,
        })
        self.assertEqual(rows[-1]["reconciliation"]["admission"], "opportunity")

    def test_access_decision_is_required_and_verified_for_public_access(self):
        for decision in (None, [], {}):
            qualification = json.loads(json.dumps(QUALIFICATION))
            if decision is None:
                del qualification["access"]["decision"]
            else:
                qualification["access"]["decision"] = decision
            with self.subTest(access_decision=decision), self.assertRaisesRegex(
                ValueError, "source_qualification_access_decision_invalid"
            ):
                self._load_with_change({"qualification": qualification})

        qualification = json.loads(json.dumps(QUALIFICATION))
        qualification["access"]["status"] = "unverified"
        with self.assertRaisesRegex(ValueError, "source_qualification_access_decision_invalid"):
            self._load_with_change({"qualification": qualification})

    def test_reuse_decision_is_required_and_must_use_known_value(self):
        for decision in (None, "approved", "yes", True, [], {}):
            qualification = json.loads(json.dumps(QUALIFICATION))
            if decision is None:
                del qualification["reuse_terms"]["decision"]
            else:
                qualification["reuse_terms"]["decision"] = decision
            with self.subTest(decision=decision), self.assertRaisesRegex(
                ValueError, "source_qualification_reuse_decision_invalid"
            ):
                self._load_with_change({"qualification": qualification})

        qualification = json.loads(json.dumps(QUALIFICATION))
        qualification["reuse_terms"]["status"] = "unverified"
        with self.assertRaisesRegex(ValueError, "source_qualification_reuse_decision_invalid"):
            self._load_with_change({"qualification": qualification})

    def test_evidence_references_must_be_safe_https_or_repository_relative_paths(self):
        for reference in (
            "../private/ops/source.json",
            "/private/ops/source.json",
            "private\\ops\\source.json",
            "private/ops/does-not-exist.json",
            "file:///etc/passwd",
            "https://user:secret@example.org/schema",
            "https://example.org:444/schema",
        ):
            qualification = json.loads(json.dumps(QUALIFICATION))
            qualification["stable_identity"]["evidence_refs"] = [reference]
            with self.subTest(reference=reference), self.assertRaisesRegex(
                ValueError, "source_qualification_evidence_invalid"
            ):
                self._load_with_change({
                    "official_row_hosts": ["example.org"],
                    "reconciliation": {"source_id_path": "data[].id", "stable_key_prefix": "opportunity:",
                                       "admission": "opportunity", "entity": "opportunity"},
                    "qualification": qualification,
                })

    def test_existing_repository_file_is_a_valid_local_evidence_reference(self):
        qualification = json.loads(json.dumps(QUALIFICATION))
        qualification["stable_identity"]["evidence_refs"] = [
            "tests/test_grants_sources_validation.py"
        ]
        rows = self._load_with_change({
            "official_row_hosts": ["example.org"],
            "reconciliation": {"source_id_path": "data[].id", "stable_key_prefix": "opportunity:",
                               "admission": "opportunity", "entity": "opportunity"},
            "qualification": qualification,
        })
        self.assertEqual(rows[-1]["qualification"]["stable_identity"]["evidence_refs"],
                         ["tests/test_grants_sources_validation.py"])

    def test_every_catalogue_source_requires_a_complete_status_record(self):
        with self.assertRaisesRegex(ValueError, "source_qualification_missing"):
            self._load_with_change({"qualification": None})
        for status in ("", "unknown", True, None, [], {}):
            with self.subTest(status=status), self.assertRaisesRegex(
                ValueError, "source_qualification_status_invalid"
            ):
                self._load_with_change({
                    "qualification": {
                        **json.loads(json.dumps(QUALIFICATION)),
                        "stable_identity": {"status": status, "evidence_refs": ["https://example.org/id"]},
                    }
                })


if __name__ == "__main__":
    unittest.main()
