import json
import tempfile
import unittest
import uuid
import zipfile
from pathlib import Path

from scripts.build_dora_activity_flow_package import build_package


class DoraActivityFlowPackageTests(unittest.TestCase):
    def test_private_package_injects_target_without_placeholders(self):
        private_root = Path(__file__).parents[1] / "private"
        private_root.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=private_root) as folder:
            output = Path(folder) / "dora.zip"
            build_package(output, site_url="https://example.sharepoint.com/personal/dev", list_id=str(uuid.uuid4()), flow_id=str(uuid.uuid4()), connection_display_name="DEV SharePoint")
            with zipfile.ZipFile(output) as archive:
                names = set(archive.namelist())
                self.assertIn("manifest.json", names)
                definition = json.loads(archive.read(next(n for n in names if n.endswith("/definition.json"))))
                text = json.dumps(definition)
                self.assertNotIn("{{", text)
                self.assertIn("shared_sharepointonline", text)
                self.assertNotIn("shared_onedriveforbusiness", text)
                self.assertIn("item/DORAActivityKey", text)
                self.assertIn("item/PI Email", text)

    def test_rejects_invalid_target_or_connection(self):
        private_root = Path(__file__).parents[1] / "private"
        private_root.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=private_root) as folder:
            with self.assertRaises(ValueError):
                build_package(Path(folder) / "bad.zip", site_url="http://example.org", list_id=str(uuid.uuid4()), flow_id=str(uuid.uuid4()), connection_display_name="DEV")
            with self.assertRaises(ValueError):
                build_package(Path(folder) / "bad.zip", site_url="https://example.org", list_id="bad", flow_id=str(uuid.uuid4()), connection_display_name="DEV")
            with self.assertRaises(ValueError):
                build_package(Path(folder) / "bad.zip", site_url="https://example.org", list_id=str(uuid.uuid4()), flow_id=str(uuid.uuid4()), connection_display_name=False)


if __name__ == "__main__":
    unittest.main()
