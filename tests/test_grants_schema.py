import json
import re
import unittest
from pathlib import Path

from scripts.grants_registry import normalize_opportunity, sharepoint_field_map


class GrantsSchemaTests(unittest.TestCase):
    def test_schema_matches_sharepoint_mapping_and_has_single_identity(self):
        root = Path(__file__).parents[1]
        schema = json.loads((root / "config/grants-registry.schema.json").read_text())
        names = [field["display_name"] for field in schema["fields"]]
        mapped = set(sharepoint_field_map(normalize_opportunity({"Title": "T", "URL": "https://x"})))
        self.assertEqual(schema["list_name"], "Grants Registry")
        self.assertEqual(schema["identity_field"], "OpportunityKey")
        self.assertEqual(set(names), mapped)
        self.assertEqual(names.count("OpportunityKey"), 1)
        identity = next(field for field in schema["fields"] if field["display_name"] == schema["identity_field"])
        self.assertEqual(identity["type"], "text")
        self.assertIs(identity["required"], True)
        self.assertIs(identity["indexed"], True)
        self.assertIs(identity["unique"], True)
        source_id = next(field for field in schema["fields"] if field["display_name"] == "SourceID")
        self.assertEqual(source_id["type"], "text")
        self.assertIs(source_id["indexed"], True)
        source_row_url = next(field for field in schema["fields"] if field["display_name"] == "SourceRowURL")
        self.assertEqual(source_row_url["type"], "url")
        self.assertNotIn("required", source_row_url)

    def test_model_query_projection_and_types_match_registry_contract(self):
        """Catch local source-shape drift without treating labels as identity proof."""
        root = Path(__file__).parents[1]
        schema = json.loads((root / "config/grants-registry.schema.json").read_text())
        query = (root / "config/GrantsRegistry.m").read_text()

        registry = re.search(r'Source\{\[Title\s*=\s*"([^"]+)"\]\}\[Items\]', query)
        self.assertIsNotNone(registry, "GrantsRegistry M must bind one explicit list selector")
        self.assertEqual(registry.group(1), schema["list_name"])

        selected = re.search(r"Selected\s*=\s*Table\.SelectColumns\(Registry,\s*\{(.*?)\},\s*MissingField\.UseNull\)", query, re.S)
        self.assertIsNotNone(selected, "M query must retain its explicit projection")
        projected = re.findall(r'"([^"]+)"', selected.group(1))
        expected = [field["display_name"] for field in schema["fields"]]
        self.assertEqual(projected, expected, "M projection must match the canonical registry schema and order")

        typed = re.search(r"Typed\s*=\s*Table\.TransformColumnTypes\(Selected,\s*\{(.*?)\}\)", query, re.S)
        self.assertIsNotNone(typed, "M query must explicitly type every projected field")
        type_pairs = re.findall(r'\{"([^"]+)",\s*type\s+(\w+)\}', typed.group(1))
        self.assertEqual([name for name, _ in type_pairs], expected)
        self.assertTrue(all(kind == "text" for _, kind in type_pairs),
                        "registry retains source-stated dates and amounts as text")

        # The checked-in connection target is deliberately a placeholder. Its
        # list title is a local schema selector, not proof of native list GUID.
        self.assertIn('https://<tenant>.sharepoint.com/sites/<site>', query)
        self.assertNotRegex(query, r'https://(?!<tenant>)[^" ]+')

    def test_schema_preserves_partial_deadline_as_text_contract(self):
        schema = json.loads((Path(__file__).parents[1] / "config/grants-registry.schema.json").read_text())
        types = {field["display_name"]: field["type"] for field in schema["fields"]}
        self.assertEqual(types["Deadline"], "text")
        self.assertEqual(types["DeadlineRaw"], "text")
        for field in (
            "DeadlineTimezone", "DeadlineLocalTime", "DeadlineUTCInstant",
            "DeadlineBrisbaneDate", "DeadlineBrisbaneTime",
        ):
            self.assertEqual(types[field], "text")
        temporal_status = next(
            field for field in schema["fields"] if field["display_name"] == "DeadlineTemporalStatus"
        )
        self.assertEqual(temporal_status["type"], "choice")
        self.assertIn("ambiguous_local_time", temporal_status["choices"])
        self.assertIn("nonexistent_local_time", temporal_status["choices"])

    def test_temporal_status_choice_covers_unresolved_and_conflicting_zone_cases(self):
        root = Path(__file__).parents[1]
        schema = json.loads((root / "config/grants-registry.schema.json").read_text())
        field = next(item for item in schema["fields"]
                     if item["display_name"] == "DeadlineTemporalStatus")
        self.assertEqual(field["type"], "choice")
        self.assertIn("timezone_conflict", field["choices"])
        self.assertIn("ambiguous_local_time", field["choices"])
        self.assertIn("nonexistent_local_time", field["choices"])


if __name__ == "__main__":
    unittest.main()
