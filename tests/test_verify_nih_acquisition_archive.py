import base64
import copy
import io
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from scripts.verify_nih_acquisition_archive import ROLES, verify
from tests import test_grants_us_gov_api as fixture_data


class VerifyNihArchiveTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        fixture = fixture_data.GrantsGovPreparationTests()
        fixture.setUp()
        content = b"Synthetic attachment only"
        binary = io.BytesIO()
        with zipfile.ZipFile(binary, "w") as z:
            z.writestr("fixture.html", content)
        self.zip = binary.getvalue()
        self.folder = {"id": 123, "opportunityId": 357812, "zipLobSize": len(self.zip),
                       "synopsisAttachments": [{"fileName": "fixture.html", "fileLobSize": len(content),
                                                "opportunityId": 357812}]}
        detail = copy.deepcopy(fixture.detail)
        detail["data"]["synopsisAttachmentFolders"] = [self.folder]
        self.manifest = {"format": "rims-nih-acquisition-v1", "source": "us-grants-gov-nih-pa-25-301",
                         "acquisition_complete": True, "accepted": False, "register_updated": False,
                         "model_refreshed": False, "end_to_end_qualified": False,
                         "attachment_files_retained": True, "run": "synthetic-run",
                         "observed_utc": "2026-10-24T01:00:00Z",
                         "scope": {"representation": "synthetic decoded JSON"}, "responses": [],
                         "attachment_folders": [{"folder_metadata": self.folder,
                                                 "content_base64": base64.b64encode(self.zip).decode()}]}
        for role, obj in zip(ROLES, [fixture.search, detail, fixture.search, detail]):
            raw = json.dumps(obj).encode()
            (self.root / (role + ".json")).write_bytes(raw)
            self.manifest["responses"].append({"role": role, "http_status": 200, "response": obj,
                                               "content_base64": base64.b64encode(raw).decode()})
        (self.root / "attachment-folder-123.zip").write_bytes(self.zip)
        self.save()

    def save(self):
        (self.root / "acquisition.json").write_text(json.dumps(self.manifest))

    def test_complete_bytes_values_source_replay_and_zip_members(self):
        result = verify(self.root)
        self.assertEqual(len(result["files"]), 5)
        self.assertEqual(result["attachment_members"][0]["name"], "fixture.html")
        self.assertFalse(result["end_to_end_qualified"])

    def test_source_file_byte_changes_reject_even_equivalent_json(self):
        path = self.root / "search-current.json"
        path.write_bytes(path.read_bytes() + b"\n")
        with self.assertRaisesRegex(ValueError, "response_bytes"):
            verify(self.root)

    def test_omitted_attachment_folder_rejects(self):
        self.manifest["attachment_folders"] = []
        self.save()
        with self.assertRaisesRegex(ValueError, "folder_coverage"):
            verify(self.root)

    def test_attachment_binary_changes_reject(self):
        (self.root / "attachment-folder-123.zip").write_bytes(self.zip + b"x")
        with self.assertRaisesRegex(ValueError, "attachment_binary"):
            verify(self.root)

    def test_unproven_downstream_claim_rejects(self):
        self.manifest["model_refreshed"] = True
        self.save()
        with self.assertRaisesRegex(ValueError, "manifest"):
            verify(self.root)

    def test_missing_response_rejects(self):
        self.manifest["responses"].pop()
        self.save()
        with self.assertRaisesRegex(ValueError, "manifest"):
            verify(self.root)


if __name__ == "__main__":
    unittest.main()
