import base64
import copy
import hashlib
import json
import unittest

from scripts.grants_import_originals import prepare, ROLES
from scripts.grants_registry import normalize_opportunity
from scripts.grants_us_gov_api import prepare_snapshot, SOURCE
from scripts.grants_deadline_schedule import NIH_ATTRIBUTION, canonical_object
from tests import test_grants_us_gov_api as fixtures


class ImportOriginalsTests(unittest.TestCase):
    def setUp(self):
        fixture = fixtures.GrantsGovPreparationTests()
        fixture.setUp()
        fixture.detail["data"]["synopsis"]["archiveDateStr"] = "2028-02-12-00-00-00"
        fixture.detail["data"]["synopsisAttachmentFolders"] = []
        self.responses = {r: json.dumps(x, indent=2).encode() + b"\n" for r, x in
                          zip(ROLES, [fixture.search, fixture.detail, fixture.search, fixture.detail])}
        packet = prepare_snapshot(*[json.loads(self.responses[r]) for r in ROLES], retrieved_at="2026-10-24T01:00:00+00:00")
        row = packet["batch"]["records"][0]
        occurrence = {"occurrence_candidate_id": "synthetic-occurrence", "parent_source_id": SOURCE,
            "parent_source_record_id": "357812", "parent_funding_opportunity_number": "PA-25-301",
            "due_date": "2026-11-05", "application_type": "Synthetic",
            "source_due_time": "17:00:00", "source_timezone_rule": "applicant organisation local",
            "iana_timezone": None, "utc_instant": None, "effective_due_date": None}
        row.update(DeadlineScheduleJSON=json.dumps({"schema_version": "grants-deadline-schedule-v1",
            "Source": SOURCE, "SourceID": "357812", "RoundID": "PA-25-301",
            "occurrence_count": 1, "occurrences": [occurrence]}),
            SourceDateFactsJSON=json.dumps(packet["source_date_facts"]), SourceAttribution=NIH_ATTRIBUTION)
        for field in ["DeadlineScheduleJSON", "SourceDateFactsJSON"]:
            row[field] = canonical_object(row[field])
        self.row = normalize_opportunity(row, retrieved_at=row["RetrievedUTC"])

    def test_retains_every_original_byte_and_correct_sha(self):
        envelope = prepare(self.row, self.responses, {})
        self.assertEqual([x["role"] for x in envelope["files"]], list(ROLES))
        for file in envelope["files"]:
            raw = self.responses[file["role"]]
            self.assertEqual(base64.b64decode(file["content_base64"]), raw)
            self.assertEqual(file["sha256"], hashlib.sha256(raw).hexdigest())
            self.assertEqual(file["byte_length"], len(raw))

    def test_missing_response_rejects(self):
        self.responses.pop(ROLES[0])
        with self.assertRaises(ValueError):
            prepare(self.row, self.responses, {})

    def test_wrong_row_or_hash_rejects(self):
        for field, value in [("Title", "Altered"), ("EvidenceHash", "0" * 64), ("SourceID", "other")]:
            with self.subTest(field=field), self.assertRaises(ValueError):
                prepare({**self.row, field: value}, self.responses, {})

    def test_missing_declared_attachment_rejects(self):
        for role in ["detail-current", "detail-replay"]:
            body = json.loads(self.responses[role])
            body["data"]["synopsisAttachmentFolders"] = [{"id": 123}]
            self.responses[role] = json.dumps(body).encode()
        with self.assertRaisesRegex(ValueError, "attachment coverage"):
            prepare(self.row, self.responses, {})

    def test_duplicate_json_property_rejects(self):
        self.responses[ROLES[0]] = b'{"errorcode":0,"errorcode":0}'
        with self.assertRaisesRegex(ValueError, "duplicate JSON"):
            prepare(self.row, self.responses, {})

    def test_date_fact_mismatch_rejects(self):
        row = copy.deepcopy(self.row)
        facts = json.loads(row["SourceDateFactsJSON"])
        facts["archiveDateStr"] = "2099-01-01-00-00-00"
        row["SourceDateFactsJSON"] = json.dumps(facts)
        with self.assertRaisesRegex(ValueError, "date facts"):
            prepare(row, self.responses, {})

    def test_original_observation_spelling_is_preserved_for_hash_binding(self):
        observed = "2026-10-24T01:00:00Z"
        packet = prepare_snapshot(*[json.loads(self.responses[r]) for r in ROLES], retrieved_at=observed)
        raw = packet["batch"]["records"][0]
        raw.update({k: self.row[k] for k in ["DeadlineScheduleJSON", "SourceDateFactsJSON", "SourceAttribution"]})
        row = normalize_opportunity(raw, retrieved_at=observed)
        with self.assertRaisesRegex(ValueError, "evidence hash"):
            prepare(row, self.responses, {})
        self.assertEqual(prepare(row, self.responses, {}, source_observed_at=observed)["EvidenceHash"], row["EvidenceHash"])
