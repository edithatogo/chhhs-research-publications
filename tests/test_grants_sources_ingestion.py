import unittest
from pathlib import Path

from scripts.grants_ingestion import MAX_XML_BYTES, ingest_batches, parse_feed
from scripts.grants_sources import load_catalogue


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


class GrantsSourceTests(unittest.TestCase):
    def _catalogue(self):
        return [{"source_id": "good", "intake": "api", "official_row_hosts": ["example.org"],
                 "qualification": dict(QUALIFICATION),
                 "reconciliation": {"admission": "opportunity", "entity": "opportunity",
                                    "source_id_path": "result.records[].id"}}]

    def _batch(self, **changes):
        batch = {"source": "good", "retrieved_at": "2026-09-20T00:00:00Z",
                 "pagination": {"total_pages": 1, "pages_received": [1], "complete": True},
                 "records": [{"SourceID": "g1", "Title": "Good", "URL": "https://example.org/g"}]}
        batch.update(changes)
        return batch

    def test_catalogue_has_only_official_machine_reconciled_sources(self):
        rows = load_catalogue(Path(__file__).parents[1] / "config/grants-sources.json")
        self.assertEqual({row["source_id"] for row in rows}, {
            "arc-awards-api", "queensland-grants-finder-catalogue-api",
            "queensland-health-qgip-review-candidates-api",
            "arc-rgs-awards-api",
        })
        self.assertTrue(all(row["intake"] in {"rss", "atom", "api"} for row in rows))
        self.assertTrue(all(row["health_status"] == "verified_sample" for row in rows))
        self.assertTrue(all(row["authority_url"].startswith("https://") for row in rows))
        self.assertTrue(all((row["api_url"] if row["intake"] == "api" else row["feed_url"]).startswith("https://") for row in rows))
        self.assertTrue(all(row["reconciliation"]["source_id_path"] for row in rows))

    def test_arc_public_api_is_awarded_grant_context_only(self):
        rows = load_catalogue(Path(__file__).parents[1] / "config/grants-sources.json")
        arc = next(row for row in rows if row["source_id"] == "arc-awards-api")
        self.assertEqual(arc["record_kind"], "awarded_grant_context")
        self.assertEqual(arc["reconciliation"]["source_id_path"], "data[].id")
        self.assertEqual(arc["reconciliation"]["admission"], "context_only")

    def test_queensland_catalogue_api_is_metadata_only(self):
        rows = load_catalogue(Path(__file__).parents[1] / "config/grants-sources.json")
        finder = next(row for row in rows if row["source_id"] == "queensland-grants-finder-catalogue-api")
        self.assertEqual(finder["record_kind"], "source_metadata_only")
        self.assertEqual(finder["reconciliation"]["source_id_path"], "result.id")
        self.assertEqual(finder["reconciliation"]["admission"], "metadata_only")

    def test_direct_ingestion_cannot_reclassify_canonical_award_or_metadata_sources(self):
        cases = (
            ("arc-awards-api", "opportunity", "arc.gov.au"),
            ("queensland-grants-finder-catalogue-api", "opportunity", "data.qld.gov.au"),
        )
        for source_id, record_kind, host in cases:
            source = {
                "source_id": source_id,
                "enabled": True,
                "intake": "api",
                "record_kind": record_kind,
                "official_row_hosts": [host],
                "qualification": dict(QUALIFICATION),
                "reconciliation": {
                    "admission": "opportunity", "entity": "opportunity",
                    "source_id_path": "data[].id",
                },
            }
            result = ingest_batches(
                [self._batch(source=source_id, records=[{
                    "SourceID": "row-1", "Title": "Not an opportunity row",
                    "URL": f"https://{host}/row-1",
                }])],
                catalogue=[source],
            )
            with self.subTest(source_id=source_id):
                self.assertEqual(result["records"], [])
                self.assertFalse(result["accepted"])
                self.assertIn("invalid_catalogue_row", result["health"][0]["error"])

    def test_qgip_catalogue_is_review_only_and_identity_unproven(self):
        rows = load_catalogue(Path(__file__).parents[1] / "config/grants-sources.json")
        qgip = next(row for row in rows if row["source_id"] == "queensland-health-qgip-review-candidates-api")
        self.assertEqual(qgip["record_kind"], "opportunity_candidate")
        self.assertEqual(qgip["reconciliation"]["admission"], "candidate_only")
        self.assertEqual(qgip["reconciliation"]["entity"], "opportunity_candidate")
        self.assertIn("not proof", qgip["identity_semantics"])
        self.assertEqual(qgip["source_license"], "CC-BY-3.0")

    def test_rgs_api_is_disabled_award_context_only(self):
        rows = load_catalogue(Path(__file__).parents[1] / "config/grants-sources.json")
        rgs = next(row for row in rows if row["source_id"] == "arc-rgs-awards-api")
        self.assertFalse(rgs["enabled"])
        self.assertEqual(rgs["record_kind"], "awarded_grant_context")
        self.assertEqual(rgs["reconciliation"]["source_id_path"], "data[].id")
        self.assertEqual(rgs["reconciliation"]["admission"], "context_only")

    def test_qgip_candidate_only_cannot_enter_canonical_opportunity_intake(self):
        source = {"source_id": "qld-qgip", "intake": "api", "official_row_hosts": ["health.qld.gov.au"],
                  "reconciliation": {"admission": "candidate_only", "entity": "opportunity_candidate",
                                     "source_id_path": "result.records[].Service ID"}}
        batch = self._batch(source="qld-qgip", records=[{
            "SourceID": "candidate-1", "Title": "Review only", "URL": "https://www.health.qld.gov.au/funding",
        }])
        result = ingest_batches([batch], catalogue=[source])
        self.assertEqual(result["records"], [])
        self.assertIn("wrong_entity_kind", result["health"][0]["error"])

    def test_disabled_source_batch_is_rejected_with_stable_reason(self):
        source = {**self._catalogue()[0], "enabled": False}
        result = ingest_batches([self._batch()], catalogue=[source])
        self.assertEqual(result["records"], [])
        self.assertIn("source_disabled", result["health"][0]["error"])

    def test_opportunity_intake_fails_closed_without_complete_source_qualification(self):
        source = self._catalogue()[0]
        del source["qualification"]
        result = ingest_batches([self._batch()], catalogue=[source])
        self.assertEqual(result["records"], [])
        self.assertIn("invalid_catalogue_row", result["health"][0]["error"])

    def test_direct_opportunity_intake_requires_bounded_sample_qualification(self):
        source = self._catalogue()[0]
        del source["qualification"]["bounded_sample"]
        result = ingest_batches([self._batch()], catalogue=[source])
        self.assertEqual(result["records"], [])
        self.assertFalse(result["accepted"])

    def test_opportunity_intake_requires_every_qualification_gate(self):
        for field in QUALIFICATION:
            qualification = dict(QUALIFICATION)
            if field == "observed_at":
                qualification[field] = "2026-10-23T10:00:00"
            else:
                qualification[field] = {"status": "unverified", "evidence_refs": []}
            source = {**self._catalogue()[0], "qualification": qualification}
            with self.subTest(field=field):
                result = ingest_batches([self._batch()], catalogue=[source])
                self.assertEqual(result["records"], [])
                self.assertFalse(result["accepted"])

    def test_opportunity_intake_requires_evidence_for_each_qualification_gate(self):
        for field in ("response_schema", "bounded_sample", "complete_pagination", "replay_keyset",
                      "stable_identity", "lifecycle_semantics", "reuse_terms",
                      "entity_reconciliation"):
            qualification = {**QUALIFICATION, field: {"status": "verified", "evidence_refs": []}}
            source = {**self._catalogue()[0], "qualification": qualification}
            with self.subTest(field=field):
                result = ingest_batches([self._batch()], catalogue=[source])
                self.assertEqual(result["records"], [])
                self.assertFalse(result["accepted"])

    def test_opportunity_intake_requires_permitted_reuse_decision(self):
        for decision in ("restricted", "not_permitted", "unresolved", "not_applicable"):
            qualification = {**QUALIFICATION,
                             "reuse_terms": {**QUALIFICATION["reuse_terms"],
                                             "decision": decision}}
            source = {**self._catalogue()[0], "qualification": qualification}
            with self.subTest(decision=decision):
                result = ingest_batches([self._batch()], catalogue=[source])
                self.assertEqual(result["records"], [])
                self.assertFalse(result["accepted"])

    def test_opportunity_intake_requires_qualified_access_decision(self):
        for decision in ("restricted", "unavailable", "unresolved", "not_applicable", [], {}):
            qualification = {**QUALIFICATION,
                             "access": {**QUALIFICATION["access"],
                                        "decision": decision}}
            source = {**self._catalogue()[0], "qualification": qualification}
            with self.subTest(decision=decision):
                result = ingest_batches([self._batch()], catalogue=[source])
                self.assertEqual(result["records"], [])
                self.assertFalse(result["accepted"])

    def test_existing_authorized_access_is_accepted_when_its_evidence_is_verified(self):
        source = self._catalogue()[0]
        source["qualification"]["access"]["decision"] = "existing_authorized"
        result = ingest_batches([self._batch()], catalogue=[source])
        self.assertTrue(result["accepted"])
        self.assertEqual(len(result["records"]), 1)

    def test_atom_and_rss_shapes_are_preserved_as_canonical_records(self):
        rss = """<rss><channel><item><guid>r1</guid><title>Call</title><link>https://example.org/call/</link><description>Summary</description><deadline>2027-04</deadline></item></channel></rss>"""
        atom = """<feed xmlns='http://www.w3.org/2005/Atom'><entry><id>a1</id><title>Call</title><link href='https://example.org/call'/><summary>Summary</summary></entry></feed>"""
        a = parse_feed(rss, source="R", retrieved_at="2026-09-20T00:00:00+10:00",
                       source_id_path="channel.item[].guid", intake="rss")[0]
        b = parse_feed(atom, source="A", retrieved_at="2026-09-20T00:00:00+10:00",
                       source_id_path="entry[].id", intake="atom")[0]
        self.assertEqual(a["DeadlinePrecision"], "month")
        self.assertEqual(a["URL"], "https://example.org/call")
        self.assertEqual(b["Title"], "Call")
        self.assertEqual(a["RetrievedTimestampStatus"], "valid")

    def test_atom_prefers_alternate_opportunity_page_over_self_api_link(self):
        atom = """<feed xmlns='http://www.w3.org/2005/Atom'><entry>
          <id>a1</id><title>Call</title>
          <link rel='self' href='https://example.org/api/calls/a1'/>
          <link rel='alternate' href='https://example.org/funding/call-a1'/>
        </entry></feed>"""
        row = parse_feed(atom, source="A", retrieved_at="2026-09-20T00:00:00Z",
                         source_id_path="entry[].id", intake="atom")[0]
        self.assertEqual(row["URL"], "https://example.org/funding/call-a1")

    def test_feed_source_id_uses_declared_path_not_first_matching_alias(self):
        feed = """<rss><channel><item><guid>display-guid</guid><id>stable-id</id>
          <title>Call</title><link>https://example.org/call</link></item></channel></rss>"""
        row = parse_feed(feed, source="R", retrieved_at="2026-09-20T00:00:00Z",
                         source_id_path="channel.item[].id", intake="rss")[0]
        self.assertEqual(row["SourceID"], "stable-id")

    def test_feed_identity_contract_must_match_feed_envelope(self):
        feed = "<rss><channel><item><guid>id-1</guid><title>Call</title><link>https://example.org/call</link></item></channel></rss>"
        with self.assertRaisesRegex(ValueError, "feed_envelope_does_not_match_catalogue_intake"):
            parse_feed(feed, source="R", retrieved_at="2026-09-20T00:00:00Z",
                       source_id_path="entry[].id", intake="atom")

    def test_catalogue_identity_path_drives_feed_ingestion(self):
        source = {"source_id": "good", "intake": "rss", "official_row_hosts": ["example.org"],
                  "qualification": dict(QUALIFICATION),
                  "reconciliation": {"admission": "opportunity", "entity": "opportunity",
                                     "source_id_path": "channel.item[].id"}}
        batch = self._batch(records=[], xml="""<rss><channel><item><guid>alias</guid><id>stable-1</id>
          <title>Call</title><link>https://example.org/call</link></item></channel></rss>""")
        result = ingest_batches([batch], catalogue=[source])
        self.assertTrue(result["accepted"])
        self.assertEqual(result["records"][0]["SourceID"], "stable-1")

    def test_direct_feed_parser_rejects_coerced_source_and_timestamp(self):
        feed = "<rss><channel><item><guid>1</guid><title>Call</title><link>https://example.org/call</link></item></channel></rss>"
        for kwargs, expected in (
            ({"source": {"id": "A"}, "retrieved_at": "2026-09-20T00:00:00Z",
              "source_id_path": "channel.item[].guid", "intake": "rss"},
             "invalid_source_identity"),
            ({"source": "A", "retrieved_at": {"timestamp": "2026-09-20T00:00:00Z"},
              "source_id_path": "channel.item[].guid", "intake": "rss"},
             "invalid_observation_time"),
        ):
            with self.subTest(kwargs=kwargs), self.assertRaisesRegex(ValueError, expected):
                parse_feed(feed, **kwargs)

    def test_feed_rejects_padded_source_and_xml_identity(self):
        feed = "<rss><channel><item><guid>g1</guid><title>Call</title><link>https://example.org/call</link></item></channel></rss>"
        with self.assertRaisesRegex(ValueError, "invalid_source_identity"):
            parse_feed(feed, source=" R ", retrieved_at="2026-09-20T00:00:00Z",
                       source_id_path="channel.item[].guid", intake="rss")
        padded_id = feed.replace("<guid>g1</guid>", "<guid> g1</guid>")
        with self.assertRaisesRegex(ValueError, "padded reconciliation identity"):
            parse_feed(padded_id, source="R", retrieved_at="2026-09-20T00:00:00Z",
                       source_id_path="channel.item[].guid", intake="rss")

    def test_feed_source_identity_preserves_internal_whitespace_exactly(self):
        feed = "<rss><channel><item><guid>scheme  round 1</guid><title>Call</title><link>https://example.org/call</link></item></channel></rss>"
        row = parse_feed(feed, source="R", retrieved_at="2026-09-20T00:00:00Z",
                         source_id_path="channel.item[].guid", intake="rss")[0]
        self.assertEqual(row["SourceID"], "scheme  round 1")

    def test_direct_feed_parser_requires_strict_offset_timestamp(self):
        feed = "<rss><channel><item><guid>1</guid><title>Call</title><link>https://example.org/call</link></item></channel></rss>"
        for timestamp in ("2026-09-20T12:00:00Z", "2026-09-20 12:00:00+10:00",
                          "2026-09-20T12:00+10:00", "2026-09-20T12:00:00"):
            with self.subTest(timestamp=timestamp):
                if timestamp.endswith("Z"):
                    self.assertEqual(parse_feed(feed, source="R", retrieved_at=timestamp,
                                                source_id_path="channel.item[].guid", intake="rss")[0]["RetrievedTimestampStatus"], "valid")
                else:
                    with self.assertRaisesRegex(ValueError, "invalid_observation_time"):
                        parse_feed(feed, source="R", retrieved_at=timestamp,
                                   source_id_path="channel.item[].guid", intake="rss")

    def test_feed_rejects_non_feed_envelope_and_nested_items(self):
        row = "<item><guid>g1</guid><title>Call</title><link>https://example.org/call</link></item>"
        with self.assertRaisesRegex(ValueError, "feed_envelope_does_not_match_catalogue_intake"):
            parse_feed(f"<response>{row}</response>", source="R",
                       retrieved_at="2026-09-20T00:00:00Z",
                       source_id_path="channel.item[].guid", intake="rss")
        with self.assertRaisesRegex(ValueError, "feed contains no RSS items"):
            parse_feed(f"<rss><channel><metadata>{row}</metadata></channel></rss>", source="R",
                       retrieved_at="2026-09-20T00:00:00Z",
                       source_id_path="channel.item[].guid", intake="rss")
        rdf = f"<rdf:RDF xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#'>{row}</rdf:RDF>"
        self.assertEqual(parse_feed(rdf, source="R", retrieved_at="2026-09-20T00:00:00Z",
                                    source_id_path="item[].guid", intake="rss")[0]["SourceID"], "g1")

    def test_oversized_feed_fails_closed_without_discarding_another_source(self):
        oversized = "<rss>" + "x" * MAX_XML_BYTES + "</rss>"
        with self.assertRaisesRegex(ValueError, "feed_xml_payload_too_large"):
            parse_feed(oversized, source="rss", retrieved_at="2026-09-20T00:00:00Z",
                       source_id_path="channel.item[].guid", intake="rss")
        with self.assertRaisesRegex(ValueError, "feed_xml_payload_too_large"):
            parse_feed("é" * (MAX_XML_BYTES // 2 + 1), source="rss",
                       retrieved_at="2026-09-20T00:00:00Z",
                       source_id_path="channel.item[].guid", intake="rss")
        rss_catalogue = {**self._catalogue()[0], "source_id": "rss", "intake": "rss",
                         "reconciliation": {"admission": "opportunity", "entity": "opportunity",
                                            "source_id_path": "channel.item[].guid"}}
        result = ingest_batches([
            self._batch(),
            self._batch(source="rss", records=[], xml=oversized),
        ], catalogue=[*self._catalogue(), rss_catalogue])
        self.assertEqual([row["Source"] for row in result["records"]], ["good"])
        self.assertIn("feed_xml_payload_too_large", result["health"][1]["error"])
        self.assertFalse(result["accepted"])

    def test_bad_source_does_not_discard_successful_batch(self):
        result = ingest_batches([
            self._batch(),
            {"source": "bad", "retrieved_at": "2026-09-20T00:00:00Z", "xml": "<broken"},
        ], catalogue=self._catalogue())
        self.assertEqual(len(result["records"]), 1)
        self.assertEqual([item["status"] for item in result["health"]], ["succeeded", "failed"])
        self.assertFalse(result["accepted"])

    def test_machine_api_cannot_assign_internal_review_or_relevance(self):
        record = {"SourceID": "g1", "Title": "Good", "URL": "https://example.org/g",
                  "ReviewStatus": "Reviewed", "ReviewNotes": "forged reviewer note",
                  "CHHHSRelevance": "High"}
        result = ingest_batches([self._batch(records=[record])], catalogue=self._catalogue())
        self.assertTrue(result["accepted"])
        row = result["records"][0]
        self.assertEqual(row["ReviewStatus"], "Needs Review")
        self.assertEqual(row["ReviewNotes"], "")
        self.assertEqual(row["CHHHSRelevance"], "Unknown")

    def test_api_identity_and_deadline_values_must_be_text(self):
        for field, value in (("SourceID", {"id": "g1"}), ("Title", 12),
                             ("URL", ["https://example.org/g"]), ("Deadline", 2027),
                             ("DeadlineTimezone", ["Australia/Sydney"]),
                             ("deadline_timezone", ["Australia/Sydney"])):
            with self.subTest(field=field):
                result = ingest_batches([self._batch(records=[{
                    "SourceID": "g1", "Title": "Good", "URL": "https://example.org/g", field: value,
                }])], catalogue=self._catalogue())
                self.assertEqual(result["records"], [])
                self.assertIn(f"API record {field} must be text or null", result["health"][0]["error"])

    def test_api_preserves_documented_deadline_timezone_projection(self):
        result = ingest_batches([self._batch(records=[{
            "SourceID": "g1", "Title": "Good", "URL": "https://example.org/g",
            "Deadline": "2026-01-15T12:00:00", "DeadlineTimezone": "Australia/Sydney",
        }])], catalogue=self._catalogue())
        row = result["records"][0]
        self.assertEqual(row["DeadlineTimezone"], "Australia/Sydney")
        self.assertEqual(row["DeadlineUTCInstant"], "2026-01-15T01:00:00Z")
        self.assertEqual(row["DeadlineBrisbaneTime"], "11:00:00")
        self.assertEqual(row["DeadlineTemporalStatus"], "zone_resolved")

        snake_case = ingest_batches([self._batch(records=[{
            "SourceID": "g2", "Title": "Good", "URL": "https://example.org/g2",
            "Deadline": "2026-01-15T12:00:00", "deadline_timezone": "Australia/Sydney",
        }])], catalogue=self._catalogue())
        self.assertEqual(snake_case["records"][0]["DeadlineTimezone"], "Australia/Sydney")
        self.assertEqual(snake_case["records"][0]["DeadlineUTCInstant"], "2026-01-15T01:00:00Z")

    def test_api_preserves_distinct_source_row_url_and_rejects_unadmitted_host(self):
        row = {"SourceID": "g1", "Title": "Good", "URL": "https://example.org/opportunity/g1",
               "SourceRowURL": "https://example.org/list#row-g1"}
        result = ingest_batches([self._batch(records=[row])], catalogue=self._catalogue())
        self.assertTrue(result["accepted"])
        self.assertEqual(result["records"][0]["SourceRowURL"], row["SourceRowURL"])
        bad = {**row, "SourceRowURL": "https://unapproved.example/list#row-g1"}
        result = ingest_batches([self._batch(records=[bad])], catalogue=self._catalogue())
        self.assertEqual(result["records"], [])
        self.assertIn("invalid_identity", result["health"][0]["error"])

    def test_api_optional_source_facts_must_not_be_stringified(self):
        for field, value in (("Status", {"value": "Open"}), ("Amount", 1000),
                             ("Funder", ["Agency"]), ("Eligibility", {"text": "Eligible"})):
            with self.subTest(field=field):
                record = {**self._batch()["records"][0], field: value}
                result = ingest_batches([self._batch(records=[record])], catalogue=self._catalogue())
                self.assertEqual(result["records"], [])
                self.assertIn(f"API record {field} must be text or null", result["health"][0]["error"])

    def test_malformed_batch_is_diagnostic_and_does_not_crash_other_sources(self):
        result = ingest_batches([None, self._batch()], catalogue=self._catalogue())
        self.assertEqual(len(result["records"]), 1)
        self.assertEqual(result["health"][0]["error"], "batch_not_object")
        self.assertEqual(result["health"][1]["status"], "succeeded")
        self.assertFalse(result["accepted"])

    def test_non_iterable_inputs_return_fail_closed_diagnostics(self):
        batch_result = ingest_batches(None, catalogue=self._catalogue())
        catalogue_result = ingest_batches([self._batch()], catalogue=None)
        self.assertEqual(batch_result["records"], [])
        self.assertEqual(batch_result["health"][0]["error"], "batches_not_iterable")
        self.assertEqual(catalogue_result["records"], [])
        self.assertEqual(catalogue_result["health"][0]["error"], "catalogue_not_iterable")

    def test_batch_iterator_failure_rejects_partial_snapshot_without_raising(self):
        def broken_batches():
            yield self._batch()
            raise RuntimeError("source adapter interrupted")

        result = ingest_batches(broken_batches(), catalogue=self._catalogue())

        self.assertEqual(result["records"], [])
        self.assertFalse(result["accepted"])
        self.assertEqual(result["health"][-1], {
            "source": "intake", "status": "failed", "count": 0,
            "error": "batch_iteration_failed",
        })

    def test_catalogue_iterator_failure_returns_diagnostic_without_raising(self):
        def broken_catalogue():
            yield self._catalogue()[0]
            raise RuntimeError("catalogue read interrupted")

        result = ingest_batches([self._batch()], catalogue=broken_catalogue())

        self.assertEqual(result["records"], [])
        self.assertFalse(result["accepted"])
        self.assertEqual(result["health"][0]["error"], "catalogue_not_iterable")

    def test_non_object_catalogue_row_rejects_source_batch(self):
        result = ingest_batches([self._batch()], catalogue=[*self._catalogue(), None])
        self.assertEqual(result["records"], [])
        self.assertIn("catalogue_row_not_object", result["health"][0]["error"])

    def test_catalogue_source_identity_and_admission_fields_are_not_coerced(self):
        for field, value, expected in (
            ("source_id", 7, "invalid_catalogue_row"),
            ("source_id", {"value": "good"}, "invalid_catalogue_row"),
            ("source_id", " good ", "invalid_catalogue_row"),
            ("intake", ["api"], "invalid_catalogue_row"),
            ("official_row_hosts", [None], "invalid_catalogue_row"),
            ("official_row_hosts", [" example.org "], "invalid_catalogue_row"),
            ("reconciliation", "opportunity", "invalid_catalogue_row"),
            ("reconciliation", {"admission": "opportunity", "entity": "opportunity"},
             "invalid_catalogue_row"),
            ("reconciliation", {"admission": "opportunity", "entity": "opportunity",
                                "source_id_path": " result.records[].id"},
             "invalid_catalogue_row"),
        ):
            with self.subTest(field=field, value=value):
                catalogue = [{**self._catalogue()[0], field: value}]
                result = ingest_batches([self._batch()], catalogue=catalogue)
                self.assertEqual(result["records"], [])
                self.assertIn(expected, result["health"][0]["error"])

    def test_source_batch_and_api_identity_padding_is_rejected(self):
        padded_source = ingest_batches([self._batch(source=" good ")], catalogue=self._catalogue())
        self.assertEqual(padded_source["records"], [])
        self.assertEqual(padded_source["health"][0]["error"], "invalid_source_identity")

        padded_id = ingest_batches([self._batch(records=[{
            "SourceID": " g1 ", "Title": "Good", "URL": "https://example.org/g",
        }])], catalogue=self._catalogue())
        self.assertEqual(padded_id["records"], [])
        self.assertIn("API record SourceID must be unpadded text", padded_id["health"][0]["error"])

    def test_batch_source_and_observation_identity_are_not_coerced(self):
        result = ingest_batches([self._batch(source={"value": "good"})], catalogue=self._catalogue())
        self.assertEqual(result["records"], [])
        self.assertEqual(result["health"][0]["error"], "invalid_source_identity")
        for field, value, expected in (
            ("retrieved_at", {"timestamp": "2026-09-20T00:00:00Z"}, "invalid_observation_time"),
            ("prior_observed_at", ["2026-09-19T00:00:00Z"], "invalid_prior_observation_time"),
        ):
            with self.subTest(field=field):
                result = ingest_batches([self._batch(**{field: value})], catalogue=self._catalogue())
                self.assertEqual(result["records"], [])
                self.assertIn(expected, result["health"][0]["error"])

    def test_snapshot_ordering_rejects_malformed_offsets_and_permissive_forms(self):
        for field, value, expected in (
            ("retrieved_at", "2026-09-20T12:00:00+1000", "invalid_observation_time"),
            ("retrieved_at", "2026-09-20 12:00:00+10:00", "invalid_observation_time"),
            ("prior_observed_at", "2026-09-19T12:00:00+1000", "invalid_prior_observation_time"),
        ):
            with self.subTest(field=field, value=value):
                result = ingest_batches([self._batch(**{field: value})], catalogue=self._catalogue())
                self.assertEqual(result["records"], [])
                self.assertIn(expected, result["health"][0]["error"])

    def test_catalogue_context_source_cannot_enter_opportunity_intake(self):
        source = {"source_id": "good", "intake": "api", "official_row_hosts": ["example.org"],
                  "reconciliation": {"admission": "context_only", "entity": "awarded_grant",
                                     "source_id_path": "data[].id"}}
        result = ingest_batches([self._batch()], catalogue=[source])
        self.assertEqual(result["records"], [])
        self.assertIn("wrong_entity_kind", result["health"][0]["error"])

    def test_duplicate_catalogue_identity_cannot_be_shadowed_into_opportunity_admission(self):
        # The first row is metadata-only. A later conflicting row with the same
        # source identity must not shadow it and turn that identity into an
        # approved opportunity source.
        metadata_only = {"source_id": "good", "intake": "api", "official_row_hosts": ["example.org"],
                         "reconciliation": {"admission": "metadata_only", "entity": "source_catalogue",
                                            "source_id_path": "result.id"}}
        shadow_opportunity = {"source_id": "good", "intake": "api", "official_row_hosts": ["example.org"],
                              "qualification": dict(QUALIFICATION),
                              "reconciliation": {"admission": "opportunity", "entity": "opportunity",
                                                 "source_id_path": "result.records[].id"}}
        result = ingest_batches([self._batch()], catalogue=[metadata_only, shadow_opportunity])
        self.assertEqual(result["records"], [])
        self.assertIn("duplicate_catalogue_source_id", result["health"][0]["error"])

    def test_malformed_batches_emit_zero_rows_with_diagnostics(self):
        cases = [
            (self._batch(records=[{"SourceID": "g1", "Title": "Good", "URL": "https://example.org@evil.test/g"}]), "invalid_identity"),
            (self._batch(records=[{"SourceID": "", "Title": "Good", "URL": "https://example.org/g"}]), "invalid_identity"),
            (self._batch(retrieved_at="2026-09-20T00:00:00"), "invalid_observation_time"),
            (self._batch(records=[{"SourceID": "g1", "Title": "Good", "URL": "https://example.org/g", "Deadline": "2027-02-30"}]), "invalid_deadline"),
            (self._batch(pagination={"total_pages": 2, "pages_received": [2, 1], "complete": True}), "incomplete_pagination"),
            (self._batch(prior_observed_at="2026-09-21T00:00:00Z"), "older_observation"),
        ]
        for batch, error in cases:
            with self.subTest(error=error):
                result = ingest_batches([batch], catalogue=self._catalogue())
                self.assertEqual(result["records"], [])
                self.assertIn(error, result["health"][0]["error"])

    def test_pagination_receipt_requires_exact_integer_page_numbers(self):
        for page in (True, 1.0, "1"):
            with self.subTest(page=page):
                result = ingest_batches(
                    [self._batch(pagination={"total_pages": 1, "pages_received": [page], "complete": True})],
                    catalogue=self._catalogue(),
                )
                self.assertEqual(result["records"], [])
                self.assertIn("incomplete_pagination", result["health"][0]["error"])

    def test_duplicate_key_rejects_complete_source_batch(self):
        row = self._batch()["records"][0]
        result = ingest_batches([self._batch(records=[row, dict(row)])], catalogue=self._catalogue())
        self.assertEqual(result["records"], [])
        self.assertIn("duplicate_opportunity_key", result["health"][0]["error"])

    def test_repeated_source_snapshot_rejects_all_of_that_source(self):
        other = {**self._catalogue()[0], "source_id": "other"}
        other_batch = self._batch(source="other", records=[
            {"SourceID": "o1", "Title": "Other", "URL": "https://example.org/other"}])
        result = ingest_batches([self._batch(), other_batch,
                                 self._batch(records=[{"SourceID": "g2", "Title": "Again",
                                                       "URL": "https://example.org/again"}])],
                                catalogue=[*self._catalogue(), other])
        self.assertEqual([row["Source"] for row in result["records"]], ["other"])
        self.assertEqual({item["source"]: item["status"] for item in result["health"]},
                         {"good": "failed", "other": "succeeded"})
        self.assertEqual(next(item for item in result["health"] if item["source"] == "good")["error"],
                         "duplicate_source_batch")
        self.assertFalse(result["accepted"])


if __name__ == "__main__":
    unittest.main()
