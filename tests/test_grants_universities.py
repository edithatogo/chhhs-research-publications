import unittest
import json
import tempfile
from pathlib import Path

from scripts.grants_universities import load_universities


class GrantsUniversityTests(unittest.TestCase):
    def test_required_university_sources_are_explicitly_manual_until_access_proven(self):
        rows = load_universities(Path(__file__).parents[1] / "config/grants-universities.json")
        self.assertEqual({row["institution_id"] for row in rows}, {"jcu", "uq", "qut", "griffith"})
        self.assertTrue(all(row["intake"] == "manual_review" for row in rows))

    def test_unknown_university_lead_times_are_not_invented(self):
        rows = load_universities(Path(__file__).parents[1] / "config/grants-universities.json")
        by_id = {row["institution_id"]: row for row in rows}
        self.assertIsNone(by_id["qut"]["internal_lead_time"])
        self.assertIsNone(by_id["griffith"]["internal_lead_time"])
        self.assertEqual(by_id["jcu"]["internal_lead_time"]["major_schemes"], 20)

    def test_invalid_known_lead_time_is_rejected(self):
        rows = json.loads((Path(__file__).parents[1] / "config/grants-universities.json").read_text())
        rows[0]["internal_lead_time"]["major_schemes"] = -1
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json") as handle:
            json.dump(rows, handle)
            handle.flush()
            with self.assertRaisesRegex(ValueError, "invalid lead-time value"):
                load_universities(handle.name)


if __name__ == "__main__":
    unittest.main()
