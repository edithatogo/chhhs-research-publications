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
        for heading in expected:
            self.assertIn("## ", text)
            self.assertRegex(text, rf"## \d+\. {re.escape(heading)}")

        # The document also has a top-level horizontal/vertical overview diagram.
        # Count the six numbered module diagrams below, not that overview.
        module_summaries = text.split("## 1. Publications registry", 1)[1]
        blocks = re.findall(r"```mermaid\n(.*?)\n```", module_summaries, flags=re.DOTALL)
        self.assertEqual(len(blocks), len(expected))
        for block in blocks:
            self.assertRegex(block, r"(?m)^flowchart (LR|TD|RL|BT)\s*$")
            self.assertGreaterEqual(len(re.findall(r"(?m)^\s*\S+.*-->.*$", block)), 2)

        self.assertEqual(module_summaries.count("\n```"), len(expected) * 2)


if __name__ == "__main__":
    unittest.main()
