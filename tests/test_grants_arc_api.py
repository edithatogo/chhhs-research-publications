import unittest
import io
import json
import urllib.error
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch

from scripts.grants_arc_api import (
    ARCAPIHTTPError, ARCPageValidationError, ARCSnapshotFetchError, parse_award_page,
    fetch_award_page, fetch_award_snapshot,
    _exact_meta, main,
)


class GrantsArcApiTests(unittest.TestCase):
    @staticmethod
    def snapshot_opener(pages):
        calls = []
        class Response:
            headers = {"Content-Type": "application/json"}
            def __init__(self, payload): self.payload = payload
            def getcode(self): return 200
            def read(self, _limit): return __import__("json").dumps(self.payload).encode()
            def __enter__(self): return self
            def __exit__(self, *args): return False
        def opener(request, timeout):
            calls.append(request.full_url)
            return Response(pages[len(calls) - 1])
        return opener, calls

    @staticmethod
    def page(number, ids, *, total=3, size=2):
        return {"meta": {"requested-page-number": number,
                         "requested-page-size": size, "actual-page-size": len(ids),
                         "total-pages": 2, "total-size": total},
                "data": [{"id": value, "attributes": {"code": value},
                          "links": {"self": "https://dataportal.arc.gov.au/NCGP/API/grants/" + value}}
                         for value in ids]}

    def test_complete_snapshot_replays_all_pages(self):
        first = self.page(1, ["A", "B"])
        second = self.page(2, ["C"])
        opener, calls = self.snapshot_opener([first, second, first, second])
        result = fetch_award_snapshot(page_size=2, retrieved_at="2026-09-25T00:00:00Z", opener=opener)
        self.assertTrue(result["snapshot_complete"])
        self.assertEqual(result["source_total"], 3)
        self.assertEqual([row["SourceID"] for row in result["records"]], ["A", "B", "C"])
        self.assertEqual(len(calls), 4)
        self.assertEqual(result["record_kind"], "awards_only")
        self.assertFalse(result["canonical_opportunity_admission"])

    def test_snapshot_fails_closed_when_replay_exceeds_aggregate_raw_byte_cap(self):
        first = self.page(1, ["A", "B"])
        second = self.page(2, ["C"])
        encoded_pages = [json.dumps(page).encode() for page in (first, second, first, second)]
        aggregate_bytes = sum(len(body) for body in encoded_pages)
        opener, calls = self.snapshot_opener([first, second, first, second])
        with patch("scripts.grants_arc_api.MAX_TOTAL_RESPONSE_BYTES", aggregate_bytes - 1):
            with self.assertRaisesRegex(ValueError, "aggregate byte limit"):
                fetch_award_snapshot(
                    page_size=2, retrieved_at="2026-09-25T00:00:00Z", opener=opener
                )
        self.assertEqual(len(calls), 4)

    def test_snapshot_retains_complete_unknown_fields_and_exact_bodies_both_passes(self):
        import base64, hashlib
        first = self.page(1, ["A", "B"])
        second = self.page(2, ["C"])
        first["data"][0]["attributes"]["future-field"] = {"nested": [False, 0, None, "café"]}
        first["data"][0]["relationships"] = {"unknown": {"data": [{"id": "R"}]}}
        first["future-metadata"] = ["RETAINED_RAW_SENTINEL"]
        opener, calls = self.snapshot_opener([first, second, first, second])
        result = fetch_award_snapshot(page_size=2, retrieved_at="2026-09-25T00:00:00Z", opener=opener)
        responses = result["raw_source"]["http_responses"]
        self.assertEqual(len(responses), 4)
        for receipt, expected, url in zip(responses, [first, second, first, second], calls):
            raw = base64.b64decode(receipt["body_base64"], validate=True)
            self.assertEqual(raw, json.dumps(expected).encode())
            self.assertEqual(len(raw), receipt["bytes"])
            self.assertEqual(hashlib.sha256(raw).hexdigest(), receipt["sha256"])
            self.assertEqual(receipt["request_url"], url)
            self.assertEqual(receipt["status"], 200)
        self.assertFalse(result["raw_source"]["candidate_filter_applied"])
        self.assertNotIn("future-field", result["records"][0])
        self.assertEqual(result["record_kind"], "awards_only")

    def test_sample_retains_raw_body_without_changing_typed_award(self):
        import base64
        page = self.page(1, ["A"], total=1, size=1)
        page["links"] = {"future": "https://example.invalid/unknown"}
        opener, _ = self.snapshot_opener([page])
        result = fetch_award_page(page_size=1, retrieved_at="2026-09-25T00:00:00Z", opener=opener)
        self.assertEqual(json.loads(base64.b64decode(result["raw_source"]["http_responses"][0]["body_base64"])), page)
        self.assertEqual(result["records"], parse_award_page(page, retrieved_at="2026-09-25T00:00:00Z"))

    def test_retained_arc_bodies_never_reach_cli_stdout(self):
        output = io.StringIO()
        result = {"records": [], "raw_source": {"http_responses": [{"body_base64": "PRIVATE_BODY_SENTINEL"}]}}
        with redirect_stdout(output):
            self.assertEqual(main(["--sample"], sample_fetcher=Mock(return_value=result)), 0)
        self.assertNotIn("PRIVATE_BODY_SENTINEL", output.getvalue())
        self.assertNotIn("raw_source", output.getvalue())

    def test_disabled_arc_source_blocks_page_and_snapshot_before_network(self):
        root = Path(__file__).parents[1]
        catalogue = json.loads((root / "config/grants-sources.json").read_text())
        next(row for row in catalogue if row["source_id"] == "arc-awards-api")["enabled"] = False
        with TemporaryDirectory() as directory:
            path = Path(directory) / "catalogue.json"
            path.write_text(json.dumps(catalogue))
            for fetch in (fetch_award_page, fetch_award_snapshot):
                with self.subTest(fetch=fetch.__name__), self.assertRaisesRegex(ValueError, "source_disabled"):
                    fetch(catalogue_path=path,
                          opener=lambda *_args, **_kwargs: self.fail("network called"))

    def test_arc_cli_default_prints_help_without_fetching(self):
        sample = Mock(side_effect=AssertionError("unexpected network fetch"))
        snapshot = Mock(side_effect=AssertionError("unexpected network fetch"))
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(main([], sample_fetcher=sample, snapshot_fetcher=snapshot), 0)
        self.assertIn("--sample", output.getvalue())
        self.assertIn("--snapshot", output.getvalue())
        sample.assert_not_called()
        snapshot.assert_not_called()

    def test_arc_cli_disabled_source_exits_before_fetch(self):
        root = Path(__file__).parents[1]
        catalogue = json.loads((root / "config/grants-sources.json").read_text())
        next(row for row in catalogue if row["source_id"] == "arc-awards-api")["enabled"] = False
        sample = Mock(side_effect=AssertionError("disabled source must not fetch"))
        with TemporaryDirectory() as directory:
            path = Path(directory) / "catalogue.json"
            path.write_text(json.dumps(catalogue))
            with self.assertRaises(SystemExit) as raised:
                main(["--sample", "--catalogue", str(path)], sample_fetcher=sample)
        self.assertEqual(raised.exception.code, 2)
        sample.assert_not_called()

    def test_arc_cli_snapshot_failure_emits_safe_page_metadata_and_nonzero_status(self):
        snapshot = Mock(side_effect=ARCSnapshotFetchError(
            pass_number=2, page_number=7, completed_pages=6, total_pages=70,
            failure_kind="network_request_failure"))
        output = io.StringIO()
        with TemporaryDirectory() as directory:
            private_ops = Path(directory) / "private" / "ops"
            with patch("scripts.grants_arc_api.PRIVATE_OPS_ROOT", private_ops), redirect_stdout(output):
                status = main(["--snapshot", "--out", str(private_ops / "snapshot.json")],
                              snapshot_fetcher=snapshot)

        payload = json.loads(output.getvalue())
        self.assertEqual(status, 1)
        self.assertFalse(payload["snapshot_complete"])
        self.assertEqual(payload["failure_metadata"]["page_number"], 7)
        self.assertEqual(payload["failure_metadata"]["completed_pages_in_pass"], 6)
        self.assertNotIn("dataportal.arc.gov.au", output.getvalue())
        snapshot.assert_called_once()

    def test_arc_cli_snapshot_requires_private_output_before_fetch(self):
        snapshot = Mock(side_effect=AssertionError("must not fetch without private output"))
        stderr = io.StringIO()
        with redirect_stderr(stderr), self.assertRaises(SystemExit) as raised:
            main(["--snapshot"], snapshot_fetcher=snapshot)
        self.assertEqual(raised.exception.code, 2)
        self.assertIn("--snapshot requires --out", stderr.getvalue())
        snapshot.assert_not_called()

    def test_arc_cli_sample_prints_only_summary_and_saves_rows_privately_on_request(self):
        sample = Mock(return_value={
            "source": "arc", "record_kind": "awards_only",
            "api_url": "https://dataportal.arc.gov.au/secret-query",
            "meta": {"requested-page-number": 1, "requested-page-size": 1,
                     "actual-page-size": 1, "total-pages": 20, "total-size": 20},
            "records": [{"SourceID": "PRIVATE-AWARD-ID", "Title": "Private row detail"}],
        })
        with TemporaryDirectory() as directory:
            private_ops = Path(directory) / "private" / "ops"
            target = private_ops / "arc-sample.json"
            output = io.StringIO()
            with patch("scripts.grants_arc_api.PRIVATE_OPS_ROOT", private_ops), redirect_stdout(output):
                status = main(["--sample", "--out", str(target)], sample_fetcher=sample)
            summary = json.loads(output.getvalue())
            self.assertEqual(status, 0)
            self.assertEqual(summary["record_count"], 1)
            self.assertTrue(summary["private_output_saved"])
            self.assertEqual(summary["page_metadata"]["total-size"], 20)
            self.assertNotIn("PRIVATE-AWARD-ID", output.getvalue())
            self.assertNotIn("Private row detail", output.getvalue())
            self.assertNotIn("secret-query", output.getvalue())
            self.assertIn("PRIVATE-AWARD-ID", target.read_text())
            self.assertEqual(target.stat().st_mode & 0o777, 0o600)
            sample.assert_called_once()

    def test_arc_cli_snapshot_prints_summary_and_keeps_records_in_private_file(self):
        snapshot = Mock(return_value={
            "source": "arc", "record_kind": "awards_only", "snapshot_complete": True,
            "source_total": 1, "page_count": 1, "page_size": 500, "snapshot_hash": "a" * 64,
            "replay_passes": 2, "authoritative_lifecycle_semantics_proven": False,
            "canonical_opportunity_admission": False,
            "records": [{"SourceID": "SNAPSHOT-AWARD-ID", "Title": "Private snapshot row"}],
        })
        with TemporaryDirectory() as directory:
            private_ops = Path(directory) / "private" / "ops"
            target = private_ops / "arc-snapshot.json"
            output = io.StringIO()
            with patch("scripts.grants_arc_api.PRIVATE_OPS_ROOT", private_ops), redirect_stdout(output):
                status = main(["--snapshot", "--out", str(target)], snapshot_fetcher=snapshot)
            summary = json.loads(output.getvalue())
            self.assertEqual(status, 0)
            self.assertTrue(summary["snapshot_complete"])
            self.assertEqual(summary["source_total"], 1)
            self.assertEqual(summary["record_count"], 1)
            self.assertFalse(summary["canonical_opportunity_admission"])
            self.assertNotIn("SNAPSHOT-AWARD-ID", output.getvalue())
            self.assertNotIn("Private snapshot row", output.getvalue())
            self.assertIn("SNAPSHOT-AWARD-ID", target.read_text())
            snapshot.assert_called_once()

    def test_arc_cli_refuses_overwrite_and_non_private_output_before_fetch(self):
        sample = Mock(side_effect=AssertionError("must not fetch for invalid output"))
        with TemporaryDirectory() as directory:
            private_ops = Path(directory) / "private" / "ops"
            private_ops.mkdir(parents=True)
            target = private_ops / "existing.json"
            target.write_text("existing receipt")
            stderr = io.StringIO()
            with patch("scripts.grants_arc_api.PRIVATE_OPS_ROOT", private_ops), \
                    redirect_stderr(stderr), self.assertRaises(SystemExit) as raised:
                main(["--sample", "--out", str(target)], sample_fetcher=sample)
            self.assertEqual(raised.exception.code, 2)
            self.assertIn("refuses to overwrite", stderr.getvalue())
            sample.assert_not_called()

            stderr = io.StringIO()
            outside = Path(directory) / "outside.json"
            with patch("scripts.grants_arc_api.PRIVATE_OPS_ROOT", private_ops), \
                    redirect_stderr(stderr), self.assertRaises(SystemExit) as raised:
                main(["--sample", "--out", str(outside)], sample_fetcher=sample)
            self.assertEqual(raised.exception.code, 2)
            self.assertIn("inside the repository's ignored private/ops", stderr.getvalue())
            sample.assert_not_called()

    def test_arc_cli_sample_validation_failure_is_sanitized(self):
        sample = Mock(side_effect=ValueError("private response detail and URL"))
        output = io.StringIO()
        with redirect_stdout(output):
            status = main(["--sample"], sample_fetcher=sample)

        payload = json.loads(output.getvalue())
        self.assertEqual(status, 1)
        self.assertEqual(payload["failure"], "sample_validation_failed")
        self.assertEqual(payload["failure_metadata"], {"failure_class": "ValueError"})
        self.assertNotIn("private response detail", output.getvalue())
        self.assertNotIn("dataportal.arc.gov.au", output.getvalue())
        sample.assert_called_once()

    def test_sample_validation_failure_reports_safe_stage_without_exception_context(self):
        malformed_record = {"meta": {}, "data": [{"id": "award-1"}]}
        opener, _ = self.snapshot_opener([malformed_record])
        with self.assertRaises(ARCPageValidationError) as raised:
            fetch_award_page(page_size=1, retrieved_at="2026-09-25T00:00:00Z", opener=opener)
        self.assertEqual(raised.exception.metadata, {
            "stage": "award_record_validation", "failure_class": "ValueError"})
        self.assertIsNone(raised.exception.__context__)
        self.assertNotIn("award-1", str(raised.exception))

        class InvalidJsonResponse:
            headers = {"Content-Type": "application/json"}
            def getcode(self): return 200
            def read(self, _limit): return b"private invalid payload"
            def __enter__(self): return self
            def __exit__(self, *args): return False

        with self.assertRaises(ARCPageValidationError) as raised:
            fetch_award_page(page_size=1, opener=lambda *_args, **_kwargs: InvalidJsonResponse())
        self.assertEqual(raised.exception.metadata, {
            "stage": "response_validation", "failure_class": "ValueError"})
        self.assertIsNone(raised.exception.__context__)
        self.assertNotIn("private invalid payload", str(raised.exception))

    def test_arc_cli_sample_http_failure_emits_only_safe_http_metadata(self):
        sample = Mock(side_effect=ARCAPIHTTPError(429, {"Retry-After": "60"}))
        output = io.StringIO()
        with redirect_stdout(output):
            status = main(["--sample"], sample_fetcher=sample)
        payload = json.loads(output.getvalue())
        self.assertEqual(status, 1)
        self.assertEqual(payload["failure"], "sample_request_failed")
        self.assertEqual(payload["failure_metadata"], {
            "http": {"status": 429, "retry_after": "60"}})
        self.assertNotIn("dataportal.arc.gov.au", output.getvalue())
        sample.assert_called_once()

    def test_snapshot_rejects_duplicate_truncation_and_content_drift(self):
        first = self.page(1, ["A", "B"])
        second = self.page(2, ["C"])
        changed = self.page(2, ["C"])
        changed["data"][0]["attributes"]["grant-status"] = "Changed"
        cases = ([first, self.page(2, ["A"])],
                 [first, self.page(2, [])],
                 [first, second, first, changed])
        for pages in cases:
            with self.subTest(pages=pages), self.assertRaises(ValueError):
                fetch_award_snapshot(page_size=2, retrieved_at="2026-09-25T00:00:00Z",
                                     opener=self.snapshot_opener(pages)[0])

    def test_snapshot_rejects_changed_totals_and_page_bound(self):
        first = self.page(1, ["A", "B"])
        changed_total = self.page(2, ["C"], total=4)
        with self.assertRaisesRegex(ValueError, "pagination metadata|total changed"):
            fetch_award_snapshot(page_size=2, opener=self.snapshot_opener([first, changed_total])[0])
        huge = self.page(1, ["A"], total=1001, size=1)
        huge["meta"]["total-pages"] = 1001
        with self.assertRaisesRegex(ValueError, "pagination metadata"):
            fetch_award_snapshot(page_size=1, opener=self.snapshot_opener([huge])[0])

    def test_http_403_is_sanitized_without_retry_or_response_body(self):
        calls = []

        def denied(request, timeout):
            calls.append(request.full_url)
            raise urllib.error.HTTPError(
                request.full_url, 403, "Forbidden", {
                    "Date": "Mon, 05 Oct 2026 02:00:00 GMT",
                    "X-Private": "must not be retained",
                }, io.BytesIO(b"private response body"),
            )

        with self.assertRaises(ARCAPIHTTPError) as raised:
            fetch_award_page(opener=denied)

        self.assertEqual(raised.exception.metadata, {
            "status": 403,
            "date": "Mon, 05 Oct 2026 02:00:00 GMT",
        })
        self.assertEqual(len(calls), 1)
        self.assertNotIn("dataportal.arc.gov.au", str(raised.exception))
        self.assertNotIn("private response body", str(raised.exception))
        self.assertIsNone(raised.exception.__context__)
        self.assertNotIn("must not be retained", repr(raised.exception.metadata))

    def test_http_429_keeps_only_bounded_retry_metadata_and_does_not_retry(self):
        calls = []

        def throttled(request, timeout):
            calls.append(request.full_url)
            raise urllib.error.HTTPError(
                request.full_url, 429, "Too Many Requests", {
                    "Retry-After": "120",
                    "Date": "Mon, 05 Oct 2026 02:00:00 GMT",
                    "X-Private": "must not be retained",
                }, io.BytesIO(b"private response body"),
            )

        with self.assertRaises(ARCAPIHTTPError) as raised:
            fetch_award_page(opener=throttled)

        self.assertEqual(raised.exception.metadata, {
            "status": 429,
            "retry_after": "120",
            "date": "Mon, 05 Oct 2026 02:00:00 GMT",
        })
        self.assertEqual(len(calls), 1)
        self.assertNotIn("dataportal.arc.gov.au", str(raised.exception))
        self.assertNotIn("private response body", str(raised.exception))
        self.assertIsNone(raised.exception.__context__)
        self.assertNotIn("must not be retained", repr(raised.exception.metadata))

    def test_mid_snapshot_http_failure_discards_partial_records_without_retry(self):
        calls = []
        first_page = self.page(1, ["A", "B"])

        def interrupted(request, timeout):
            calls.append(request.full_url)
            if len(calls) == 1:
                response = self.snapshot_opener([first_page])[0](request, timeout)
                return response
            raise urllib.error.HTTPError(
                request.full_url, 429, "Too Many Requests",
                {"Retry-After": "60"}, io.BytesIO(b"private response body"),
            )

        with self.assertRaises(ARCSnapshotFetchError) as raised:
            fetch_award_snapshot(page_size=2, retrieved_at="2026-09-25T00:00:00Z",
                                 opener=interrupted)

        self.assertEqual(raised.exception.metadata, {
            "pass_number": 1,
            "page_number": 2,
            "completed_pages_in_pass": 1,
            "declared_total_pages": 2,
            "failure_kind": "http_failure",
            "http": {"status": 429, "retry_after": "60"},
        })
        self.assertEqual(len(calls), 2)
        self.assertFalse(hasattr(raised.exception, "records"))
        self.assertNotIn("private response body", str(raised.exception))

    def test_snapshot_timeout_reports_bounded_page_progress_without_rows_or_retry(self):
        first_page = self.page(1, ["A", "B"])
        second_page = self.page(2, ["C"])
        calls = []

        def interrupted(request, timeout):
            calls.append(request.full_url)
            if len(calls) == 4:
                raise urllib.error.URLError("timed out")
            payload = first_page if len(calls) in (1, 3) else second_page
            return self.snapshot_opener([payload])[0](request, timeout)

        with self.assertRaises(ARCSnapshotFetchError) as raised:
            fetch_award_snapshot(page_size=2, retrieved_at="2026-09-25T00:00:00Z",
                                 opener=interrupted)

        self.assertEqual(raised.exception.metadata, {
            "pass_number": 2,
            "page_number": 2,
            "completed_pages_in_pass": 1,
            "declared_total_pages": 2,
            "failure_kind": "network_request_failure",
        })
        self.assertEqual(len(calls), 4)
        self.assertFalse(hasattr(raised.exception, "records"))
        self.assertNotIn("dataportal.arc.gov.au", str(raised.exception))
        self.assertIsNone(raised.exception.__cause__)

    def test_live_scale_metadata_fits_default_bound_and_total_cap(self):
        page = {"meta": {"requested-page-number": 1, "requested-page-size": 500,
                         "actual-page-size": 500, "total-pages": 70, "total-size": 34960},
                "data": [{} for _ in range(500)]}
        self.assertEqual(_exact_meta(page, 1, 500), (34960, 70))
        page["meta"]["total-size"] = 50001
        page["meta"]["total-pages"] = 101
        with self.assertRaisesRegex(ValueError, "pagination metadata"):
            _exact_meta(page, 1, 500)

    def test_awards_are_typed_and_not_opportunities(self):
        records = parse_award_page({"data": [{
            "id": "FT260100001",
            "attributes": {
                "code": "FT260100001",
                "scheme-name": "ARC Future Fellowships",
                "grant-summary": "Award summary",
                "current-funding-amount": 100,
                "grant-status": "Active",
            },
            "links": {"self": "https://dataportal.arc.gov.au/NCGP/API/grants/FT260100001"},
        }]}, retrieved_at="2026-09-20T03:36:00+00:00")
        self.assertEqual(records[0]["RecordKind"], "Award")
        self.assertEqual(records[0]["SourceID"], "FT260100001")
        self.assertNotIn("OpportunityKey", records[0])

    def test_self_link_must_be_official_and_reconcile_to_record_identity(self):
        base = {
            "id": "api-id",
            "attributes": {"code": "award-code", "grant-summary": "Award summary"},
        }
        for link in (
            "https://attacker.test/NCGP/API/grants/award-code",
            "http://attacker.test/NCGP/API/grants/award-code",
            "https://dataportal.arc.gov.au/NCGP/API/grants/other-award",
            "https://dataportal.arc.gov.au/NCGP/API/grants/award-code?redirect=https://attacker.test",
        ):
            with self.subTest(link=link), self.assertRaisesRegex(ValueError, "official API host"):
                parse_award_page({"data": [{**base, "links": {"self": link}}]},
                                 retrieved_at="2026-09-20T03:36:00+00:00")

    def test_official_http_self_link_is_upgraded_to_https(self):
        record = {"id": "FT260100001", "attributes": {"code": "FT260100001"},
                  "links": {"self": "http://dataportal.arc.gov.au/NCGP/API/grants/FT260100001"}}
        result = parse_award_page({"data": [record]},
                                  retrieved_at="2026-09-25T00:00:00+00:00")
        self.assertEqual(result[0]["URL"],
                         "https://dataportal.arc.gov.au/NCGP/API/grants/FT260100001")

    def test_official_slash_containing_award_id_is_validated_as_full_suffix(self):
        award_id = "AR04/00252"
        record = {"id": award_id, "attributes": {"code": award_id},
                  "links": {"self": "http://dataportal.arc.gov.au/NCGP/API/grants/" + award_id}}
        result = parse_award_page({"data": [record]}, retrieved_at="2026-09-25T00:00:00Z")
        self.assertEqual(result[0]["SourceID"], award_id)
        self.assertEqual(result[0]["URL"],
                         "https://dataportal.arc.gov.au/NCGP/API/grants/" + award_id)
        for suffix in ("AR04//00252", "AR04/../00252", "AR04/%2E%2E/00252",
                       "AR04/00252/", "AR04/%00/00252", "AR04/00253"):
            with self.subTest(suffix=suffix), self.assertRaisesRegex(ValueError, "official API host"):
                parse_award_page({"data": [{**record, "links": {"self":
                    "https://dataportal.arc.gov.au/NCGP/API/grants/" + suffix}}]},
                    retrieved_at="2026-09-25T00:00:00Z")

    def test_self_link_may_reconcile_through_api_id_when_code_is_distinct(self):
        record = {
            "id": "api-id",
            "attributes": {"code": "award-code", "grant-summary": "Award summary"},
            "links": {"self": "https://dataportal.arc.gov.au/NCGP/API/grants/api-id"},
        }
        result = parse_award_page({"data": [record]},
                                  retrieved_at="2026-09-20T03:36:00+00:00")
        self.assertEqual(result[0]["SourceID"], "api-id")
        self.assertEqual(result[0]["AwardCode"], "award-code")

    def test_missing_or_duplicate_api_ids_cannot_change_award_identity(self):
        def item(api_id, code):
            return {"id": api_id, "attributes": {"code": code},
                    "links": {"self": f"https://dataportal.arc.gov.au/NCGP/API/grants/{code}"}}
        with self.assertRaisesRegex(ValueError, r"data\[\]\.id must be nonblank"):
            parse_award_page({"data": [item(None, "award-code")]},
                             retrieved_at="2026-09-20T03:36:00+00:00")
        with self.assertRaisesRegex(ValueError, r"duplicate data\[\]\.id"):
            parse_award_page({"data": [item("api-id", "one"), item("api-id", "two")]},
                             retrieved_at="2026-09-20T03:36:00+00:00")

    def test_fetch_uses_bounded_page_and_preserves_meta(self):
        class Response:
            headers = {"Content-Type": "application/json"}
            def getcode(self): return 200
            def read(self, limit):
                self.limit = limit
                return b'{"meta":{"total-size":1},"data":[]}'
            def __enter__(self): return self
            def __exit__(self, *args): return False

        calls = []
        def opener(request, timeout):
            calls.append((request.full_url, timeout))
            return Response()

        result = fetch_award_page(page_size=1, retrieved_at="2026-09-20T03:36:00+00:00", opener=opener)
        self.assertEqual(result["record_kind"], "awards_only")
        self.assertEqual(result["meta"]["total-size"], 1)
        self.assertIn("page%5Bsize%5D=1", result["api_url"])
        self.assertEqual(calls[0][1], 20)

    def test_invalid_page_size_fails_closed(self):
        for invalid in (1001, True, 1.0):
            with self.subTest(page_size=invalid), self.assertRaises(ValueError):
                fetch_award_page(page_size=invalid, opener=lambda *_args, **_kwargs: None)

    def test_identity_timestamp_and_self_link_types_are_strict(self):
        record = {"id": " award-1", "attributes": {"code": "award-1"},
                  "links": {"self": "https://dataportal.arc.gov.au/NCGP/API/grants/award-1"}}
        with self.assertRaisesRegex(ValueError, r"data\[\]\.id must be nonblank unpadded"):
            parse_award_page({"data": [record]}, retrieved_at="2026-09-25T00:00:00Z")
        record["id"] = "award-1"
        for link in ({"href": "https://dataportal.arc.gov.au/NCGP/API/grants/award-1"},
                     " https://dataportal.arc.gov.au/NCGP/API/grants/award-1"):
            with self.subTest(link=link), self.assertRaisesRegex(ValueError, "self-link"):
                parse_award_page({"data": [{**record, "links": {"self": link}}]},
                                 retrieved_at="2026-09-25T00:00:00Z")
        for timestamp in ([], {"value": "2026-09-25T00:00:00Z"}, "2026-09-25T00:00:00"):
            with self.subTest(timestamp=timestamp), self.assertRaisesRegex(ValueError, "retrieved_at"):
                parse_award_page({"data": []}, retrieved_at=timestamp)

    def test_award_fact_fields_reject_wrong_shapes_but_keep_numeric_amounts(self):
        base = {"id": "award-1", "attributes": {"code": "award-1",
                "grant-summary": "Summary", "scheme-name": "Scheme",
                "current-funding-amount": 0, "grant-status": "Active"},
                "links": {"self": "https://dataportal.arc.gov.au/NCGP/API/grants/award-1"}}
        row = parse_award_page({"data": [base]}, retrieved_at="2026-09-25T00:00:00Z")[0]
        self.assertEqual(row["Amount"], "0")
        for field, value in (("code", None), ("code", ""), ("code", " award-1"),
                             ("code", 1), ("grant-summary", {"text": "Summary"}),
                             ("scheme-name", ["Scheme"]),
                             ("grant-status", {"value": "Active"}),
                             ("current-funding-amount", {"amount": 100}),
                             ("current-funding-amount", True),
                             ("current-funding-amount", float("nan"))):
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                attrs = {**base["attributes"], field: value}
                parse_award_page({"data": [{**base, "attributes": attrs}]},
                                 retrieved_at="2026-09-25T00:00:00Z")

    def test_oversized_response_is_rejected(self):
        class Response:
            headers = {"Content-Type": "application/json"}
            def getcode(self): return 200
            def read(self, limit): return b"x" * limit
            def __enter__(self): return self
            def __exit__(self, *args): return False

        with self.assertRaises(ARCPageValidationError) as raised:
            fetch_award_page(page_size=1, retrieved_at="2026-09-20T03:36:00+00:00",
                             opener=lambda *_args, **_kwargs: Response())
        self.assertEqual(raised.exception.metadata, {
            "stage": "response_validation", "failure_class": "ValueError"})


if __name__ == "__main__":
    unittest.main()
