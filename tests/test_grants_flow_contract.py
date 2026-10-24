import json
import re
import unittest
from datetime import datetime
from pathlib import Path


class GrantsFlowContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = Path(__file__).parents[1] / "config/flows/grants-registry-reviewed-import.definition.json"
        cls.definition = json.loads(path.read_text(encoding="utf-8"))
        cls.actions = cls.definition["properties"]["definition"]["actions"]

    def reviewed_row_actions(self):
        return self.actions["Apply_to_each_Reviewed_Row"]["actions"]["Condition_OpportunityKey_Present"]["actions"]

    def upsert_actions(self):
        return self.reviewed_row_actions()["Condition_Conflicting_Source_Identity"]["else"]["actions"]

    def evaluate_guard(self, expression, incoming, stored):
        """Evaluate the limited WDL guard vocabulary against connector-shaped rows."""
        if isinstance(expression, str) and expression.startswith("@"):
            fields = re.findall(r"\?\['([^']+)'\]", expression)
            from_list = "first(body('SharePoint_Get_items')" in expression
            row = stored if from_list else incoming
            field = fields[1] if from_list else fields[0]
            value = row.get(field)
            if "Value" in fields:
                value = (value or {}).get("Value")
            if expression.startswith("@ticks("):
                return datetime.fromisoformat(value.replace("Z", "+00:00"))
            value = "" if value is None else str(value)
            if expression.startswith("@trim("):
                return value.strip()
            if expression.startswith("@substring("):
                if not value:
                    raise ValueError("WDL substring rejects start index zero on an empty string")
                return value[:10]
            if expression.startswith("@take("):
                return value[:10]
            self.assertTrue(expression.startswith("@string(coalesce("))
            return value
        if not isinstance(expression, dict):
            return expression
        operation, arguments = next(iter(expression.items()))
        if operation == "not":
            return not self.evaluate_guard(arguments, incoming, stored)
        values = [self.evaluate_guard(v, incoming, stored) for v in arguments]
        if operation == "and":
            return all(values)
        if operation == "or":
            return any(values)
        if operation == "equals":
            return values[0] == values[1]
        self.assertEqual(operation, "greater")
        return values[0] > values[1]

    def test_native_identity_guard_accepts_reviewed_round_only_rows(self):
        from scripts.grants_reviewed_import import import_reviewed_rows

        row = import_reviewed_rows([{
            "Source": "fixture", "SourceID": "", "RoundID": "round-2026",
            "Title": "Fixture", "URL": "https://example.org/call",
            "RetrievedUTC": "2026-10-23T10:00:00Z",
            "ReviewStatus": "Reviewed", "ReviewNotes": "Offline fixture",
        }], official_hosts=["example.org"])[0]
        guard = self.actions["Apply_to_each_Reviewed_Row"]["actions"]["Condition_OpportunityKey_Present"]["expression"]
        self.assertTrue(self.evaluate_guard(guard, row, {}))
        self.assertFalse(self.evaluate_guard(guard, {**row, "RoundID": ""}, {}))
        query = self.reviewed_row_actions()["SharePoint_Get_source_identity"]["inputs"]["parameters"]["$filter"]
        self.assertIn("RoundID eq ", query)
        self.assertIn("SourceID eq null", query)
        self.assertIn("RoundID eq null", query)

    def test_equal_time_replay_requires_identical_authority_facts(self):
        branch = self.upsert_actions()["Condition_Is_New_Opportunity"]["else"]["actions"]["Condition_Exactly_One_Opportunity"]["actions"]["Condition_Observation_Time_Known"]["actions"]["Condition_Observation_Not_Older"]
        fields = (
            "Title", "Funder", "Source", "SourceID", "RoundID", "URL", "SourceRowURL",
            "Description", "Eligibility", "Geography", "Amount", "Deadline",
            "DeadlineRaw", "DeadlinePrecision", "DeadlineTimezone", "DeadlineLocalTime",
            "DeadlineUTCInstant", "DeadlineBrisbaneDate", "DeadlineBrisbaneTime",
            "DeadlineTemporalStatus", "Status", "Contact",
        )
        choices = {"DeadlinePrecision", "DeadlineTemporalStatus", "Status"}
        incoming = {field: "" for field in fields}
        incoming.update(Title="Fixture", Deadline="2026-12-01", Status="Open",
                        RetrievedUTC="2026-10-23T10:00:00Z")
        stored = dict(incoming)
        for field in choices:
            stored[field] = {"Value": incoming[field]}
        stored["Deadline"] = "2026-12-01T00:00:00Z"
        self.assertTrue(self.evaluate_guard(branch["expression"], incoming, stored))
        # Native WDL substring(empty, 0, 0) fails; take must accept unknown dates.
        self.assertTrue(self.evaluate_guard(branch["expression"],
                        {**incoming, "Deadline": None}, {**stored, "Deadline": None}))
        self.assertTrue(self.evaluate_guard(branch["expression"],
                        {**incoming, "Deadline": ""}, {**stored, "Deadline": ""}))
        for field in fields:
            changed = {**stored, field: {"Value": "Changed"} if field in choices else "Changed"}
            with self.subTest(field=field):
                self.assertFalse(self.evaluate_guard(branch["expression"], incoming, changed))
        self.assertTrue(self.evaluate_guard(branch["expression"], {**incoming, "ReviewNotes": "Re-reviewed", "EvidenceHash": "different"}, stored))
        self.assertTrue(self.evaluate_guard(branch["expression"], {**incoming, "Title": "Newer", "RetrievedUTC": "2026-10-23T11:00:00Z"}, stored))
        self.assertFalse(self.evaluate_guard(branch["expression"], {**incoming, "RetrievedUTC": "2026-10-23T09:00:00Z"}, stored))
        diagnostic = branch["else"]["actions"]["Compose_Older_Observation_Failure"]["inputs"]
        self.assertIn("CONFLICTING_SAME_TIME_GRANTS_OBSERVATION", diagnostic)

    def test_manual_reviewed_import_contract_is_sharepoint_only(self):
        text = json.dumps(self.definition)
        self.assertIn("ReviewedRowsJson", text)
        self.assertIn("shared_sharepointonline", text)
        self.assertNotIn("shared_onedriveforbusiness", text)
        self.assertNotIn("OneDrive", text)

    def test_serial_loop_and_key_guard_are_required(self):
        loop = self.actions["Apply_to_each_Reviewed_Row"]
        self.assertEqual(loop["runtimeConfiguration"]["concurrency"]["repetitions"], 1)
        key_guard = loop["actions"]["Condition_OpportunityKey_Present"]
        self.assertEqual(len(key_guard["expression"]["and"]), 4)
        self.assertEqual(
            list(key_guard["else"]["actions"]),
        ["Compose_Invalid_Source_Identity_Failure", "Increment_Invalid_Identity_Failure_Count"],
        )
        nested = key_guard["actions"]
        self.assertIn("SharePoint_Get_items", nested)
        self.assertIn("SharePoint_Get_source_identity", nested)
        identity_lookup = nested["SharePoint_Get_source_identity"]["inputs"]["parameters"]
        self.assertEqual(identity_lookup["$top"], 1)
        self.assertIn("SourceID eq ", identity_lookup["$filter"])
        self.assertIn("Source eq ", identity_lookup["$filter"])
        self.assertIn("EvidenceHash eq ", identity_lookup["$filter"])
        self.assertIn("OpportunityKey ne ", identity_lookup["$filter"])
        conflict = nested["Condition_Conflicting_Source_Identity"]
        self.assertEqual(conflict["runAfter"], {"SharePoint_Get_source_identity": ["Succeeded"]})
        self.assertEqual(
            set(conflict["actions"]),
            {"Compose_Conflicting_Source_Identity_Failure", "Increment_Conflicting_Identity_Failure_Count"},
        )
        self.assertEqual(list(conflict["else"]["actions"]), ["Condition_Duplicate_OpportunityKey", "Condition_Is_New_Opportunity", "Archive_NIH_Update"])
        upsert = conflict["else"]["actions"]
        self.assertEqual(upsert["Condition_Is_New_Opportunity"]["runAfter"], {"Archive_NIH_Update": ["Succeeded"]})
        self.assertEqual(upsert["Archive_NIH_Update"]["runAfter"], {"Condition_Duplicate_OpportunityKey": ["Succeeded"]})
        duplicate = upsert["Condition_Duplicate_OpportunityKey"]
        self.assertNotIn("SharePoint_Create_item", conflict["actions"])
        self.assertNotIn("SharePoint_Update_item", conflict["actions"])
        failure_actions = duplicate["actions"]
        self.assertEqual(list(failure_actions), ["Compose_Duplicate_OpportunityKey_Failure", "Increment_Duplicate_Key_Failure_Count"])
        diagnostic = failure_actions["Compose_Duplicate_OpportunityKey_Failure"]
        self.assertEqual(diagnostic["type"], "Compose")
        self.assertIn("DUPLICATE_OPPORTUNITY_KEY", diagnostic["inputs"])
        is_new = upsert["Condition_Is_New_Opportunity"]
        lookup_count = "@length(body('SharePoint_Get_items')?['value'])"
        self.assertEqual(is_new["expression"]["and"][0], {"equals": [lookup_count, 0]})
        self.assertEqual(list(is_new["actions"]), [
            "SharePoint_Create_item", "SharePoint_Create_item_Preserve_ISO_Text", "Guard_NIH_Parent_Already_Admitted"])
        literal_write = is_new["actions"]["SharePoint_Create_item_Preserve_ISO_Text"]
        self.assertEqual(literal_write["runAfter"], {"SharePoint_Create_item": ["Succeeded"]})
        self.assertEqual(is_new["actions"]["SharePoint_Create_item"]["runAfter"], {"Guard_NIH_Parent_Already_Admitted": ["Succeeded"]})
        self.assertEqual(is_new["runAfter"], {"Archive_NIH_Update": ["Succeeded"]})
        self.assertEqual(literal_write["inputs"]["host"]["operationId"], "HttpRequest")
        self.assertIn("'RetrievedUTC'", literal_write["inputs"]["parameters"]["parameters/body"])
        self.assertIn("'DeadlineUTCInstant'", literal_write["inputs"]["parameters"]["parameters/body"])
        exactly_one = is_new["else"]["actions"]["Condition_Exactly_One_Opportunity"]
        self.assertEqual(exactly_one["expression"]["and"][0], {"equals": [lookup_count, 1]})
        self.assertEqual(list(exactly_one["actions"]), ["Condition_Observation_Time_Known"])
        self.assertEqual(exactly_one["else"]["actions"], {})

        # SharePoint Get items is capped at two rows. This is enough to
        # distinguish a unique match from two-or-more only if the cap stays
        # >= 2; a cap of 1 would silently make duplicates look unique.
        lookup = nested["SharePoint_Get_items"]["inputs"]["parameters"]
        self.assertGreaterEqual(int(lookup["$top"]), 2)

        # Evaluate the real conditions in execution order. The duplicate
        # diagnostic is followed by the new/existing guards, so count > 1
        # must reach neither write action even though the diagnostic succeeds.
        duplicate_condition = upsert["Condition_Duplicate_OpportunityKey"]
        self.assertEqual(
            duplicate_condition["expression"], {"greater": [lookup_count, 1]}
        )
        self.assertEqual(
            list(duplicate_condition["actions"]),
            ["Compose_Duplicate_OpportunityKey_Failure", "Increment_Duplicate_Key_Failure_Count"],
        )
        diagnostic = duplicate_condition["actions"][
            "Compose_Duplicate_OpportunityKey_Failure"
        ]
        self.assertEqual(diagnostic["type"], "Compose")
        self.assertIn("DUPLICATE_OPPORTUNITY_KEY", diagnostic["inputs"])

        def evaluate(expression, count):
            operator, operands = next(iter(expression.items()))
            left, right = operands
            self.assertEqual(left, lookup_count)
            return count > right if operator == "greater" else count == right

        for count, expected in ((0, (False, True, False)),
                                (1, (False, False, True)),
                                (2, (True, False, False)),
                                (3, (True, False, False))):
            with self.subTest(match_count=count):
                duplicate_diagnostic_runs = evaluate(
                    duplicate_condition["expression"], count
                )
                create_runs = evaluate(is_new["expression"]["and"][0], count)
                update_runs = evaluate(exactly_one["expression"]["and"][0], count)
                self.assertEqual(
                    (duplicate_diagnostic_runs, create_runs, update_runs), expected
                )
                self.assertFalse(create_runs and update_runs)
                self.assertFalse(duplicate_diagnostic_runs and (create_runs or update_runs))

    def test_executable_upsert_semantics_protect_review_fields_and_duplicates(self):
        """Exercise write outcomes rather than only inspecting flow expressions."""
        loop = self.upsert_actions()
        branches = loop["Condition_Is_New_Opportunity"]
        create_params = branches["actions"]["SharePoint_Create_item"]["inputs"]["parameters"]
        exactly_one = branches["else"]["actions"]["Condition_Exactly_One_Opportunity"]
        update_params = exactly_one["actions"]["Condition_Observation_Time_Known"]["actions"]["Condition_Observation_Not_Older"]["actions"]["SharePoint_Update_item"]["inputs"]["parameters"]
        key = "pub:gov:go-123"
        incoming = {"Title": "Updated title", "ReviewStatus": "Reviewed", "ReviewNotes": "Human note"}

        def apply(matches):
            rows = [dict(row) for row in matches]
            if len(rows) == 0:
                rows.append({
                    "OpportunityKey": key,
                    "Title": incoming["Title"],
                    "ReviewStatus": "Needs Review",
                    "ReviewNotes": "",
                })
                return rows, "created"
            if len(rows) == 1:
                row = rows[0]
                # Mirror fields that the real Update action sends. Review fields
                # are deliberately omitted from its contract.
                for parameter in update_params:
                    if parameter.startswith("item/"):
                        field = parameter.removeprefix("item/")
                        if field in incoming:
                            row[field] = incoming[field]
                return rows, "updated"
            return rows, "duplicate_no_write"

        cases = [
            ([], "created", 1),
            ([{"OpportunityKey": key, "Title": "Old", "ReviewStatus": "Reviewed", "ReviewNotes": "Keep"}], "updated", 1),
            ([{"OpportunityKey": key}, {"OpportunityKey": key}], "duplicate_no_write", 2),
        ]
        for rows, expected_action, expected_count in cases:
            with self.subTest(expected_action=expected_action):
                after, action = apply(rows)
                self.assertEqual(action, expected_action)
                self.assertEqual(len(after), expected_count)
                if expected_action == "created":
                    self.assertEqual(after[0]["ReviewStatus"], "Needs Review")
                    self.assertEqual(after[0]["ReviewNotes"], "")
                    self.assertIn("item/ReviewStatus", create_params)
                elif expected_action == "updated":
                    self.assertEqual(after[0]["Title"], incoming["Title"])
                    self.assertEqual(after[0]["ReviewStatus"], "Reviewed")
                    self.assertEqual(after[0]["ReviewNotes"], "Keep")
                    self.assertNotIn("item/ReviewStatus", update_params)
                    self.assertNotIn("item/ReviewNotes", update_params)
                else:
                    self.assertEqual(after, rows)

    def test_update_action_target_parameters_match_get_items_target(self):
        loop = self.upsert_actions()
        get_items = self.reviewed_row_actions()["SharePoint_Get_items"]["inputs"]["parameters"]
        branches = loop["Condition_Is_New_Opportunity"]
        create = branches["actions"]["SharePoint_Create_item"]["inputs"]["parameters"]
        update = branches["else"]["actions"]["Condition_Exactly_One_Opportunity"]["actions"]["Condition_Observation_Time_Known"]["actions"]["Condition_Observation_Not_Older"]["actions"]["SharePoint_Update_item"]["inputs"]["parameters"]
        for name, params in (("create", create), ("update", update)):
            with self.subTest(action=name):
                self.assertEqual(params["dataset"], get_items["dataset"])
                self.assertEqual(params["table"], get_items["table"])
                self.assertEqual(params["dataset"], "{{SHAREPOINT_SITE_URL}}")
                self.assertEqual(params["table"], "{{SHAREPOINT_LIST_ID}}")

    def test_update_does_not_overwrite_manual_review_fields(self):
        update = self.upsert_actions()["Condition_Is_New_Opportunity"]["else"]["actions"]["Condition_Exactly_One_Opportunity"]["actions"]["Condition_Observation_Time_Known"]["actions"]["Condition_Observation_Not_Older"]["actions"]["SharePoint_Update_item"]
        params = update["inputs"]["parameters"]
        self.assertNotIn("item/ReviewStatus", params)
        self.assertNotIn("item/ReviewNotes", params)

    def test_placeholders_are_explicit(self):
        text = json.dumps(self.definition)
        self.assertIn("{{SHAREPOINT_SITE_URL}}", text)
        self.assertIn("{{SHAREPOINT_LIST_ID}}", text)

    def test_sharepoint_write_fields_match_the_single_registry_schema(self):
        """Catch display-name drift before a native internal-name readback."""
        root = Path(__file__).parents[1]
        schema = json.loads((root / "config/grants-registry.schema.json").read_text(encoding="utf-8"))
        expected = {field["display_name"] for field in schema["fields"]}
        branches = self.upsert_actions()["Condition_Is_New_Opportunity"]
        create = branches["actions"]["SharePoint_Create_item"]["inputs"]["parameters"]
        update = branches["else"]["actions"]["Condition_Exactly_One_Opportunity"]["actions"]["Condition_Observation_Time_Known"]["actions"]["Condition_Observation_Not_Older"]["actions"]["SharePoint_Update_item"]["inputs"]["parameters"]
        create_fields = {name.removeprefix("item/") for name in create if name.startswith("item/")}
        update_fields = {name.removeprefix("item/") for name in update if name.startswith("item/")}
        self.assertEqual(create_fields, expected)
        self.assertEqual(update_fields, expected - {"ReviewStatus", "ReviewNotes"})
        self.assertEqual(create["item/SourceRowURL"], "@if(empty(item()?['SourceRowURL']), null, item()?['SourceRowURL'])")
        self.assertEqual(update["item/SourceRowURL"], "@if(empty(item()?['SourceRowURL']), null, item()?['SourceRowURL'])")
        lookup = self.reviewed_row_actions()["SharePoint_Get_items"]
        self.assertTrue(lookup["inputs"]["parameters"]["$filter"].startswith("OpportunityKey eq "))


if __name__ == "__main__":
    unittest.main()
