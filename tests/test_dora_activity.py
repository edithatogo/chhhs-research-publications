import json
import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from dora_activity import DATASTORE_SEARCH, PACKAGE_SHOW, SOURCE_FIELDS, collect
from export_dora_activity import EXPORT_FIELDS, build_rows


def record(project_id="1001", record_id=7):
    values = {name: f"value-{index}" for index, name in enumerate(SOURCE_FIELDS)}
    values["Project ID"] = project_id
    values["Full Project Title"] = "Synthetic DORA activity"
    return {"_id": record_id, **values}


class DoraActivityTests(unittest.TestCase):
    def fake_fetcher(self, url, params):
        if url == PACKAGE_SHOW:
            return {
                "name": "database-of-research-activity-dora",
                "id": "package-1",
                "title": "Database of Research Activity - DoRA",
                "metadata_modified": "2026-09-08T07:55:39Z",
                "resources": [{
                    "id": "resource-1", "name": "current", "format": "CSV",
                    "last_modified": "2026-09-08T07:55:28Z", "created": "2026-09-08T07:55:28Z",
                    "url": "https://example.invalid/current.csv", "hash": "abc", "datastore_active": True,
                }],
            }
        self.assertEqual(url, DATASTORE_SEARCH)
        fields = [{"id": "_id"}] + [{"id": name} for name in SOURCE_FIELDS]
        if params["offset"] == 0:
            return {"fields": fields, "records": [record("1001", 7), record("1002", 8)], "total": 3}
        return {"fields": fields, "records": [record("1003", 9)], "total": 3}

    def test_collects_all_pages_and_preserves_every_source_field(self):
        with tempfile.TemporaryDirectory() as folder:
            output = collect(Path(folder) / "activity", self.fake_fetcher, page_size=2)
            records = json.loads((output / "records.json").read_text())
            receipt = json.loads((output / "receipt.json").read_text())
        self.assertEqual(len(records), 3)
        self.assertEqual(set(records[0]), {"_id", *SOURCE_FIELDS})
        self.assertEqual(receipt["expected_count"], 3)
        self.assertTrue(receipt["raw_source_fields_preserved"])

    def test_schema_drift_is_rejected(self):
        def drift(url, params):
            result = self.fake_fetcher(url, params)
            if url == DATASTORE_SEARCH:
                result["fields"][-1]["id"] = "Unexpected field"
            return result
        with self.assertRaisesRegex(ValueError, "schema drift"):
            with tempfile.TemporaryDirectory() as folder:
                collect(Path(folder) / "activity", drift, page_size=2)

    def test_export_adds_provenance_without_dropping_source_columns(self):
        envelope = {
            "schema_version": "dora-activity-v1",
            "source_payload": {"resource": {"id": "resource-1", "name": "current", "url": "https://example.invalid/current.csv", "last_modified": "2026-09-08"}},
            "observed_at": "2026-09-20T00:00:00+00:00",
            "retrieved_count": 1,
            "records": [record()],
        }
        rows = build_rows(envelope)
        self.assertEqual(set(rows[0]), set(EXPORT_FIELDS))
        self.assertEqual(rows[0]["Project ID"], "1001")
        self.assertEqual(rows[0]["DORAActivityKey"], "dora-activity:resource-1:7")

    def test_project_id_may_repeat_but_source_id_may_not(self):
        with tempfile.TemporaryDirectory() as folder:
            output = collect(Path(folder) / "activity", lambda url, params: (
                self.fake_fetcher(url, params) if url != DATASTORE_SEARCH else {
                    "fields": [{"id": "_id"}] + [{"id": name} for name in SOURCE_FIELDS],
                    "records": [record("same-project", 7), record("same-project", 8)],
                    "total": 2,
                }
            ), page_size=2)
            rows = json.loads((output / "records.json").read_text())
        self.assertEqual([row["Project ID"] for row in rows], ["same-project", "same-project"])

        def duplicate_source_id(url, params):
            result = self.fake_fetcher(url, params)
            if url == DATASTORE_SEARCH:
                result["records"] = [record("1001", 7), record("1002", 7)]
                result["total"] = 2
            return result
        with self.assertRaisesRegex(ValueError, "source _ids"):
            with tempfile.TemporaryDirectory() as folder:
                collect(Path(folder) / "activity", duplicate_source_id, page_size=2)

    def test_rims_schema_declares_every_source_field(self):
        schema = json.loads((ROOT / "config/dora-activity-registry.schema.json").read_text())
        names = {field["name"] for field in schema["fields"]}
        self.assertTrue(set(SOURCE_FIELDS).issubset(names))
        self.assertIn("DORAActivityKey", names)
        self.assertIn("DORARecordID", names)


if __name__ == "__main__":
    unittest.main()
