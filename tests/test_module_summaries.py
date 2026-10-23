import re
import unittest
from pathlib import Path


SUMMARY = Path(__file__).parents[1] / "docs" / "RIMS_MODULE_SUMMARIES.md"


class ModuleSummaryDocumentationTests(unittest.TestCase):
    def test_all_rims_modules_have_requirements_design_and_mermaid(self):
        text = SUMMARY.read_text(encoding="utf-8")
        expected = [
            "Publications registry",
            "DORA activity registry",
            "Author and organisation enrichment",
            "Grants and funding opportunities",
            "RIMS dashboard and user experience",
            "Platform operations, versioning and CI/CD",
        ]
        sections = re.split(r"(?m)^## ", text)[1:]
        headings = [section.splitlines()[0] for section in sections]
        self.assertEqual(
            headings,
            ["Horizontal and vertical schema — 13 October 2026"]
            + [f"{index}. {name}" for index, name in enumerate(expected, 1)],
        )
        for index, section in enumerate(sections):
            with self.subTest(section=headings[index]):
                if index:
                    self.assertRegex(section, r"(?m)^Requirements: ")
                    self.assertRegex(section, r"(?m)^Design: ")
                blocks = re.findall(r"```mermaid\n(.*?)\n```", section, flags=re.DOTALL)
                self.assertEqual(len(blocks), 1)
                self.assertEqual(section.count("\n```"), 2)
                self.assertRegex(blocks[0], r"(?m)^flowchart (LR|TD|RL|BT)\s*$")
                self.assertGreaterEqual(len(re.findall(r"(?m)^\s*\S+.*-->.*$", blocks[0])), 2)

        self.assertIn("## Horizontal and vertical schema", text)

        blocks = re.findall(r"```mermaid\n(.*?)\n```", text, flags=re.DOTALL)
        self.assertEqual(len(blocks), len(expected) + 1)
        for block in blocks:
            self.assertRegex(block, r"(?m)^flowchart (LR|TD|RL|BT)\s*$")
            self.assertGreaterEqual(len(re.findall(r"(?m)^\s*\S+.*-->.*$", block)), 2)

        self.assertEqual(text.count("\n```"), (len(expected) + 1) * 2)


if __name__ == "__main__":
    unittest.main()
