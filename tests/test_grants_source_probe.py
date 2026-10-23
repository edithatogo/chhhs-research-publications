import json
import contextlib
import io
import sys
import tempfile
import urllib.error
import unittest
from unittest.mock import patch
from pathlib import Path
from scripts.grants_source_probe import (
    MAX_BYTES, _probe_row, collect_private_probe_evidence, main, probe_catalogue,
)
from scripts.grants_sources import load_catalogue

ROOT = Path(__file__).resolve().parents[1]
PRIVATE_OPS_ROOT = ROOT / "private" / "ops"
REQUIRED_EVIDENCE_FILES = [
    "2026-09-28-arc-awards-two-pass-keyset-snapshot-private.json",
    "2026-09-28-grants-finder-contribution-api-reconciliation-private.json",
    "2026-10-07-g02-arc-two-date-row-reconciliation-private.json",
    "2026-10-23-g02-qgip-official-resource-recheck/full-snapshot.json",
    "2026-10-23-g02-qgip-official-resource-recheck/snapshot-comparison.json",
]

@unittest.skipUnless(
    all((PRIVATE_OPS_ROOT / f).exists() for f in REQUIRED_EVIDENCE_FILES),
    "private/ops evidence files not present; skipping grants source probe tests"
)


class _Response:
    def __init__(self, body, status=200, url="https://example.test/api", content_type="application/json"):
        self.body = body
        self.status = status
        self.url = url
        self.headers = {"Content-Type": content_type}
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def read(self, size=-1): return self.body if size < 0 else self.body[:size]
    def getcode(self): return self.status
    def geturl(self): return self.url


class GrantsSourceProbeTests(unittest.TestCase):
    def test_machine_endpoint_readback_requires_configured_ids(self):
        def opener(request, timeout):
            if "dataportal.arc.gov.au" in request.full_url:
                return _Response(json.dumps({"data": [{"id": "FT260100001"}]}).encode(),
                                 url=request.full_url)
            if "03db77e8-d6af-46db-8c39-724d4c8c140c" in request.full_url:
                return _Response(json.dumps({"result": {"records": [{"Service ID": "64001"}]}}).encode(),
                                 url=request.full_url)
            return _Response(json.dumps({"result": {"id": "1d72cbb9"}}).encode(),
                             url=request.full_url)
        result = collect_private_probe_evidence(ROOT / "config/grants-sources.json", opener=opener)
        self.assertEqual(len(result["results"]), len(load_catalogue(ROOT / "config/grants-sources.json")))
        self.assertTrue(result["endpoint_probe_complete"])
        self.assertFalse(result["opportunity_intake_accepted"])
        self.assertEqual(result["admitted_opportunity_sources"], [])
        self.assertTrue(all(row["reconciled"] for row in result["results"] if row["source_id"] != "arc-rgs-awards-api"))
        rgs = next(row for row in result["results"] if row["source_id"] == "arc-rgs-awards-api")
        self.assertFalse(rgs["reconciled"])
        self.assertEqual(rgs["error"], "source_disabled")

    def test_missing_machine_identity_is_not_reconciled(self):
        result = collect_private_probe_evidence(ROOT / "config/grants-sources.json", opener=lambda *args, **kwargs: _Response(b"{}"))
        self.assertFalse(result["endpoint_probe_complete"])
        self.assertFalse(result["opportunity_intake_accepted"])
        self.assertTrue(all(row["reconciled"] is False for row in result["results"]))

    def test_complete_probe_does_not_admit_even_configured_opportunity_source(self):
        row = {
            "source_id": "candidate-api",
            "enabled": True,
            "intake": "api",
            "api_url": "https://example.test/api",
            "reconciliation": {
                "source_id_path": "result.id",
                "admission": "opportunity",
            },
        }
        with patch("scripts.grants_source_probe.load_catalogue", return_value=[row]):
            result = collect_private_probe_evidence(
                "unused-catalogue.json",
                opener=lambda *args, **kwargs: _Response(b'{"result":{"id":"call-1"}}'),
            )
        self.assertTrue(result["endpoint_probe_complete"])
        self.assertFalse(result["opportunity_intake_accepted"])
        self.assertEqual(result["admitted_opportunity_sources"], [])

    def test_disabled_catalogue_source_is_skipped_without_network_call(self):
        row = {"source_id": "disabled-api", "enabled": False, "intake": "api",
               "api_url": "https://example.test/api",
               "reconciliation": {"source_id_path": "result.id"}}
        with patch("scripts.grants_source_probe.load_catalogue", return_value=[row]):
            result = collect_private_probe_evidence("unused-catalogue.json", opener=lambda *args, **kwargs: self.fail("network called"))
        self.assertFalse(result["endpoint_probe_complete"])
        self.assertEqual(result["enabled_source_count"], 0)
        self.assertEqual(result["disabled_source_ids"], ["disabled-api"])
        self.assertEqual(result["results"][0]["error"], "source_disabled")

    def test_api_identity_in_html_error_page_is_not_reconciled(self):
        row = {"source_id": "official-api-test", "intake": "api",
               "api_url": "https://example.test/api",
               "reconciliation": {"source_id_path": "result.id"}}
        response = _Response(b'{"result":{"id":"looks-valid"}}', content_type="text/html")
        result = _probe_row(row, opener=lambda *args, **kwargs: response)
        self.assertFalse(result["reconciled"])
        self.assertEqual(result["error"], "endpoint_readback_failed")
        self.assertEqual(result["reason"], "endpoint API response is not JSON")

    def test_json_suffix_media_type_is_accepted(self):
        row = {"source_id": "official-api-test", "intake": "api",
               "api_url": "https://example.test/api",
               "reconciliation": {"source_id_path": "result.id"}}
        response = _Response(b'{"result":{"id":"stable-1"}}',
                             content_type="application/problem+json")
        result = _probe_row(row, opener=lambda *args, **kwargs: response)
        self.assertTrue(result["reconciled"])

    def test_api_media_type_must_be_json_not_contain_incidental_json_text(self):
        row = {"source_id": "official-api-test", "intake": "api",
               "api_url": "https://example.test/api",
               "reconciliation": {"source_id_path": "result.id"}}
        for content_type in ("text/plain; note=json", "application/not-json",
                             "application/jsonp"):
            with self.subTest(content_type=content_type):
                response = _Response(b'{"result":{"id":"stable-1"}}',
                                     content_type=content_type)
                result = _probe_row(row, opener=lambda *args, **kwargs: response)
                self.assertFalse(result["reconciled"])
                self.assertEqual(result["reason"], "endpoint API response is not JSON")

    def test_api_response_over_hard_byte_limit_is_not_reconciled(self):
        row = {"source_id": "official-api-test", "intake": "api",
               "api_url": "https://example.test/api",
               "reconciliation": {"source_id_path": "result.id"}}
        response = _Response(b" " * (MAX_BYTES + 1))
        result = _probe_row(row, opener=lambda *args, **kwargs: response)
        self.assertFalse(result["reconciled"])
        self.assertEqual(result["reason"], "endpoint response exceeds bounded readback")

    def test_duplicate_api_id_fails_closed_with_diagnostic(self):
        row = {
            "source_id": "official-api-test",
            "intake": "api",
            "api_url": "https://example.test/api",
            "reconciliation": {"source_id_path": "data[].id"},
        }
        body = b'{"data":[{"id":"round-1"},{"id":"round-1"}]}'
        result = _probe_row(row, opener=lambda *args, **kwargs: _Response(body))
        self.assertFalse(result["reconciled"])
        self.assertEqual(result["error"], "duplicate_reconciliation_identity")
        self.assertEqual(result["duplicate_reconciliation_ids"], ["round-1"])

    def test_api_batch_with_one_missing_or_invalid_id_is_not_reconciled(self):
        row = {
            "source_id": "official-api-test", "intake": "api",
            "api_url": "https://example.test/api",
            "reconciliation": {"source_id_path": "data[].id"},
        }
        invalid_records = ({}, {"id": None}, {"id": True},
                           {"id": {"nested": "id"}}, {"id": "  "},
                           {"id": " padded "})
        for bad in invalid_records:
            with self.subTest(bad=bad):
                body = json.dumps({"data": [{"id": "valid"}, bad]}).encode()
                result = _probe_row(row, opener=lambda *args, **kwargs: _Response(body))
                self.assertFalse(result["reconciled"])
                self.assertEqual(result["error"], "endpoint_readback_failed")

    def test_redirect_away_from_catalogued_official_host_is_not_reconciled(self):
        row = {
            "source_id": "official-api-test",
            "intake": "api",
            "api_url": "https://data.qld.gov.au/api/grants",
            "reconciliation": {"source_id_path": "result.id"},
        }
        response = _Response(b'{"result":{"id":"looks-valid"}}',
                            url="https://unrelated.example/api/grants")
        result = _probe_row(row, opener=lambda *args, **kwargs: response)
        self.assertFalse(result["reconciled"])
        self.assertEqual(result["error"], "endpoint_readback_failed")
        self.assertEqual(result["reason"], "endpoint_redirected_outside_official_host")

    def test_error_response_with_matching_identity_is_not_reconciled(self):
        row = {
            "source_id": "official-api-test",
            "intake": "api",
            "api_url": "https://example.test/api",
            "reconciliation": {"source_id_path": "result.id"},
        }
        for status in (302, 403, 429, 500):
            with self.subTest(status=status):
                response = _Response(b'{"result":{"id":"looks-valid"}}', status=status)
                result = _probe_row(row, opener=lambda *args, **kwargs: response)
                self.assertFalse(result["reconciled"])
                self.assertEqual(result["status"], status)
                self.assertEqual(result["error"], "endpoint_http_status_not_success")

    def test_malformed_feed_http_denial_and_throttling_are_preserved_as_failures(self):
        row = {
            "source_id": "official-rss-test",
            "intake": "rss",
            "feed_url": "https://example.test/grants.rss",
            "reconciliation": {"source_id_path": "channel.item[].guid"},
        }
        malformed = _probe_row(row, opener=lambda *args, **kwargs: _Response(b"<rss><channel>"))
        self.assertFalse(malformed["reconciled"])
        self.assertEqual(malformed["error"], "endpoint_readback_failed")

        for status, message in ((403, "Forbidden"), (429, "Too Many Requests")):
            with self.subTest(status=status):
                def denied(*args, **kwargs):
                    headers = {"Retry-After": "120", "Date": "Mon, 28 Sep 2026 05:17:27 GMT"} if status == 429 else {}
                    raise urllib.error.HTTPError("https://example.test/grants.rss", status, message, headers, None)
                limited = _probe_row(row, opener=denied)
                self.assertFalse(limited["reconciled"])
                self.assertEqual(limited["status"], status)
                self.assertEqual(limited["error"], "endpoint_readback_failed")
                if status == 429:
                    self.assertEqual(limited["retry_after"], "120")
                    self.assertEqual(limited["response_date"], "Mon, 28 Sep 2026 05:17:27 GMT")

    def test_rss_identity_is_read_from_explicit_structural_path(self):
        row = {
            "source_id": "official-rss-test",
            "intake": "rss",
            "feed_url": "https://example.test/grants.rss",
            "reconciliation": {"source_id_path": "channel.item[].guid"},
        }
        response = _Response(b"<rss><channel><item><guid>GO123</guid></item></channel></rss>")
        result = _probe_row(row, opener=lambda *args, **kwargs: response)
        self.assertTrue(result["reconciled"])
        self.assertEqual(result["reconciliation_ids"], ["GO123"])

    def test_atom_identity_is_read_from_explicit_structural_path(self):
        row = {
            "source_id": "official-atom-test",
            "intake": "atom",
            "feed_url": "https://example.test/grants.atom",
            "reconciliation": {"source_id_path": "entry[].id"},
        }
        response = _Response(b"<feed xmlns='http://www.w3.org/2005/Atom'><entry><id>call-42</id></entry></feed>")
        result = _probe_row(row, opener=lambda *args, **kwargs: response)
        self.assertTrue(result["reconciled"])
        self.assertEqual(result["reconciliation_ids"], ["call-42"])

    def test_feed_with_one_unidentified_entry_is_not_reconciled(self):
        cases = (
            ("rss", "channel.item[].guid", b"<rss><channel><item><guid>one</guid></item><item><title>Missing</title></item></channel></rss>"),
            ("atom", "entry[].id", b"<feed><entry><id>one</id></entry><entry><title>Missing</title></entry></feed>"),
            ("rss", "channel.item[].guid", b"<rss><channel><item><guid>one</guid></item><item><guid> </guid></item></channel></rss>"),
        )
        for intake, path, body in cases:
            with self.subTest(intake=intake, body=body):
                row = {"source_id": "official-feed-test", "intake": intake,
                       "feed_url": "https://example.test/grants.xml",
                       "reconciliation": {"source_id_path": path}}
                result = _probe_row(row, opener=lambda *args, **kwargs: _Response(body))
                self.assertFalse(result["reconciled"])
                self.assertEqual(result["error"], "endpoint_readback_failed")

    def test_feed_identity_tags_inside_non_feed_response_do_not_reconcile(self):
        row = {"source_id": "official-rss-test", "intake": "rss",
               "feed_url": "https://example.test/grants.xml",
               "reconciliation": {"source_id_path": "channel.item[].guid"}}
        body = b"<html><channel><item><guid>one</guid></item></channel></html>"
        result = _probe_row(row, opener=lambda *args, **kwargs: _Response(body))
        self.assertFalse(result["reconciled"])
        self.assertEqual(result["error"], "endpoint_readback_failed")

    def test_cli_stdout_contains_classification_but_not_response_identities(self):
        raw = {
            "status": "observed", "observed_at": "2026-10-03T00:00:00+00:00",
            "catalogue": "/Users/example/private/catalogue-secret.json", "max_bytes": MAX_BYTES,
            "results": [{"source_id": "test-source", "endpoint_url": "https://example.test/api?token=secret",
                         "final_url": "https://example.test/api?token=secret", "status": 200,
                         "content_type": "application/json", "bytes_read": 12,
                         "body_sha256": "body-hash", "reconciliation_ids": ["PRIVATE-RECORD-ID"],
                         "reconciliation_count": 1, "reconciled": True}],
            "endpoint_probe_complete": True, "enabled_source_count": 1,
            "disabled_source_ids": [], "opportunity_intake_accepted": False,
            "admitted_opportunity_sources": [],
        }
        output = io.StringIO()
        with patch.object(sys, "argv", ["grants_source_probe.py", "catalogue.json"]), \
                patch("scripts.grants_source_probe.collect_private_probe_evidence", return_value=raw), \
                contextlib.redirect_stdout(output):
            main()
        self.assertNotIn("PRIVATE-RECORD-ID", output.getvalue())
        self.assertNotIn("token=secret", output.getvalue())
        self.assertNotIn("catalogue-secret", output.getvalue())
        visible = json.loads(output.getvalue())
        self.assertTrue(visible["endpoint_probe_complete"])
        self.assertEqual(visible["catalogue_source_count"], 1)
        self.assertEqual(visible["results"][0]["reconciliation_count"], 1)
        self.assertTrue(visible["raw_response_identities_omitted"])

    def test_library_probe_returns_only_classification_not_raw_evidence(self):
        row = {"source_id": "official-api-test", "enabled": True, "intake": "api",
               "api_url": "https://example.test/api?token=secret",
               "reconciliation": {"source_id_path": "result.id"}}
        with patch("scripts.grants_source_probe.load_catalogue", return_value=[row]):
            result = probe_catalogue(
                "catalogue.json",
                opener=lambda *args, **kwargs: _Response(b'{"result":{"id":"PRIVATE-ROW"}}',
                                                        url="https://example.test/api?token=secret"),
            )
        serialized = json.dumps(result)
        self.assertNotIn("PRIVATE-ROW", serialized)
        self.assertNotIn("token=secret", serialized)
        self.assertEqual(result["results"][0]["reconciliation_count"], 1)

    def test_cli_restricts_full_evidence_output_to_private_ops(self):
        with tempfile.TemporaryDirectory() as outside:
            output = io.StringIO()
            with patch.object(sys, "argv", ["grants_source_probe.py", "catalogue.json",
                                             "--out", str(Path(outside) / "raw.json")]), \
                    contextlib.redirect_stderr(output), self.assertRaises(SystemExit) as raised:
                main()
            self.assertEqual(raised.exception.code, 2)
            self.assertIn("inside the repository's ignored private/ops", output.getvalue())


if __name__ == "__main__":
    unittest.main()
