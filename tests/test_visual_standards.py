"""Unit tests for visual geometry validation and WCAG AA contrast standards."""
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from validate_visual_standards import (
    calculate_contrast_ratio,
    check_wcag_compliance,
    audit_visual_geometry,
    audit_all_report_visuals,
)


class TestVisualStandards(unittest.TestCase):
    def test_wcag_contrast_black_white(self):
        ratio = calculate_contrast_ratio("#000000", "#FFFFFF")
        self.assertAlmostEqual(ratio, 21.0, places=1)

    def test_wcag_contrast_theme_palette(self):
        # Neutral Primary against White
        ratio, passed = check_wcag_compliance("#201F1E", "#FFFFFF")
        self.assertTrue(passed)
        self.assertGreaterEqual(ratio, 4.5)

        # Theme Teal against White
        ratio, passed = check_wcag_compliance("#00828A", "#FFFFFF")
        self.assertTrue(passed)
        self.assertGreaterEqual(ratio, 4.5)

    def test_report_visual_geometries_on_8px_grid(self):
        audits = audit_all_report_visuals()
        self.assertGreater(len(audits), 0)
        for visual in audits:
            self.assertTrue(
                visual["valid_grid_8px"],
                f"Visual {visual['name']} ({visual['file']}) failed 8px grid: {visual['violations']}"
            )


if __name__ == "__main__":
    unittest.main()
