import unittest
import io
import zipfile

from scripts.package_release import build_manifest, source_paths, validate_version, write_stable_entry


class PackageReleaseTests(unittest.TestCase):
    def test_version_requires_semver_with_optional_preview(self):
        self.assertEqual(validate_version("0.3.0-rc1"), "0.3.0-rc1")
        with self.assertRaises(ValueError):
            validate_version("v0.3")

    def test_source_paths_exclude_runtime_archives(self):
        names = {path.as_posix() for path in source_paths()}
        self.assertFalse(any("downloads/canonical_live_artifacts/" in name for name in names))
        self.assertFalse(any(name.endswith((".zip", ".bundle")) for name in names))

    def test_manifest_separates_software_schema_and_batch_identity(self):
        manifest = build_manifest([], "0.3.0-rc1", "publication-platform-v1", "batch-local")
        self.assertEqual(manifest["SoftwareVersion"], "0.3.0-rc1")
        self.assertEqual(manifest["SchemaVersion"], "publication-platform-v1")
        self.assertEqual(manifest["AcceptedBatchID"], "batch-local")
        self.assertIn("DirtyBuild", manifest)
        self.assertFalse(manifest["NativeAcceptance"])

    def test_zip_member_timestamp_is_stable(self):
        first = io.BytesIO()
        second = io.BytesIO()
        for stream in (first, second):
            with zipfile.ZipFile(stream, "w") as archive:
                write_stable_entry(archive, "example.txt", b"content")
        self.assertEqual(first.getvalue(), second.getvalue())


if __name__ == "__main__":
    unittest.main()
