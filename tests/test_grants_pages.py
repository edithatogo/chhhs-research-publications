import json
import tempfile
import shutil
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class GrantsPageSurfaceTests(unittest.TestCase):
    def test_native_reconciliation_records_six_to_seven_page_delta(self):
        contract = json.loads((ROOT / "contracts/dashboard.contract.json").read_text())
        reconciliation = contract["native_reconciliation"]
        native = set(reconciliation["native_page_names"])
        local = json.loads((ROOT / "powerbi/CHHHS Research Publications.Report/definition/pages/pages.json").read_text())
        local_names = set(local["pageOrder"])
        self.assertEqual(len(local["pageOrder"]), 7)
        self.assertEqual(len(native), 6)
        self.assertEqual(reconciliation["local_only_pages"], ["FundingCalendar", "MyFundingWatchlist"])
        self.assertEqual(local_names - {"PublicationRegister", "MonthlyPublications", "SourceReconciliation", "ClinicalAnalytics", "FundingOpportunities"}, set(reconciliation["local_only_pages"]))
        self.assertEqual(reconciliation["state"], "delta_open")
        self.assertTrue(reconciliation["update_candidate_blocked_until_disposition"])
        self.assertFalse(reconciliation["native_acceptance"])
        self.assertEqual(reconciliation["target_receipt"], "private/ops/2026-09-25-browseros-powerbi-report-readback.json")
        self.assertNotIn("eb1ebb6b-9389-4d1d-99cf-9e8d082fe957", json.dumps(contract))
        self.assertNotIn("1a73cfcc-e6fb-4ec9-b0bb-246d2f75c851", json.dumps(contract))
        funding = reconciliation["current_funding_readback"]
        self.assertEqual(funding["funding_opportunities_visible_slicers"], 0)
        self.assertEqual(funding["funding_opportunities_visible_rows"], 0)
        self.assertEqual(funding["calendar_watchlist_visible_filter_cards"], 0)
        self.assertEqual(funding["native_query_entity"], "Grants Registry")
        self.assertEqual(funding["local_model_entity"], "GrantsRegistry")
        self.assertFalse(funding["model_entity_identity_reconciled"])
        self.assertFalse(funding["current_visual_queries_reconciled"])

    def test_local_report_contains_three_additive_grants_pages(self):
        pages = json.loads((ROOT / "powerbi/CHHHS Research Publications.Report/definition/pages/pages.json").read_text())
        self.assertEqual(pages["pageOrder"][-3:], ["FundingOpportunities", "FundingCalendar", "MyFundingWatchlist"])

    def test_grants_model_is_empty_safe_and_explicitly_pending_native_readback(self):
        model = json.loads((ROOT / "audit/model.snapshot.json").read_text())["model"]
        grants = next(table for table in model["tables"] if table["name"] == "GrantsRegistry")
        self.assertIn("empty", grants["description"])
        self.assertIn("OpportunityKey", {column["name"] for column in grants["columns"]})
        self.assertIn("COUNTROWS(GrantsRegistry)", " ".join(measure["expression"] for measure in grants["measures"]))

    def test_query_bearing_funding_visuals_reuse_only_canonical_registry(self):
        """Keep local funding pages on the existing registry, not copied tables."""
        report_pages = ROOT / "powerbi/CHHHS Research Publications.Report/definition/pages"
        expected_fields = {
            "FundingOpportunities": {"Title", "Funder", "Source", "Eligibility", "Deadline", "DeadlinePrecision", "Status", "CHHHSRelevance", "ReviewStatus", "URL"},
            "FundingCalendar": {"Deadline", "DeadlinePrecision", "DeadlineTimezone", "DeadlineBrisbaneDate", "DeadlineBrisbaneTime", "DeadlineTemporalStatus", "Title", "Funder", "RoundID", "Status", "CHHHSRelevance", "URL"},
            "MyFundingWatchlist": {"Title", "Funder", "Deadline", "Status", "CHHHSRelevance", "ReviewStatus", "ReviewNotes", "URL"},
        }
        model = json.loads((ROOT / "audit/model.snapshot.json").read_text())["model"]
        registry = next(table for table in model["tables"] if table["name"] == "GrantsRegistry")
        registry_fields = {column["name"] for column in registry["columns"]}

        for page, required in expected_fields.items():
            query_refs = set()
            for visual in (report_pages / page / "visuals").glob("*/visual.json"):
                data = json.loads(visual.read_text())
                for projection in data.get("visual", {}).get("query", {}).get("queryState", {}).get("Values", {}).get("projections", []):
                    query_ref = projection.get("queryRef", "")
                    if query_ref:
                        self.assertTrue(query_ref.startswith("GrantsRegistry."), f"{visual}: {query_ref}")
                        query_refs.add(query_ref.removeprefix("GrantsRegistry."))
            self.assertTrue(required <= query_refs, f"{page}: missing {required - query_refs}")
            self.assertTrue(query_refs <= registry_fields | {"Grant Opportunities", "Open Grant Opportunities", "Grant Opportunities Needing Review"})

    def test_opportunity_page_has_existing_decision_filters_on_canonical_registry(self):
        page = ROOT / "powerbi/CHHHS Research Publications.Report/definition/pages/FundingOpportunities/visuals"
        expected = {
            "grant-status-filter": "Status",
            "grant-relevance-filter": "CHHHSRelevance",
            "grant-review-filter": "ReviewStatus",
            "grant-source-filter": "Source",
            "grant-eligibility-filter": "Eligibility",
            "grant-deadline-filter": "Deadline",
        }
        for visual_name, field_name in expected.items():
            visual = json.loads((page / visual_name / "visual.json").read_text())
            projection = visual["visual"]["query"]["queryState"]["Values"]["projections"][0]
            self.assertEqual(projection["field"]["Column"]["Expression"]["SourceRef"]["Entity"], "GrantsRegistry")
            self.assertEqual(projection["field"]["Column"]["Property"], field_name)
        # Funding opportunities and publication records must remain separate model entities.
        publication = ROOT / "powerbi/CHHHS Research Publications.Report/definition/pages/PublicationRegister/visuals"
        self.assertFalse(any("GrantsRegistry" in path.read_text() for path in publication.glob("*/visual.json")))

    def test_funding_caption_describes_filters_without_claiming_reviewed_only_rows(self):
        page = ROOT / "powerbi/CHHHS Research Publications.Report/definition/pages/FundingOpportunities/visuals/caption/visual.json"
        text = json.loads(page.read_text())["visual"]["objects"]["general"][0]["properties"]["paragraphs"][0]["textRuns"][0]["value"]
        self.assertIn("review state", text)
        self.assertIn("pending native acceptance", text)
        self.assertNotIn("Only reviewed", text)
        import sys
        sys.path.insert(0, str(ROOT / "scripts"))
        from build_report import build
        with tempfile.TemporaryDirectory(dir=ROOT.parent) as temporary:
            candidate = Path(temporary) / "report"
            shutil.copytree(ROOT / "powerbi/CHHHS Research Publications.Report", candidate)
            build(output_dir=candidate, selected_pages=["FundingOpportunities"])
            generated = json.loads((candidate / "definition/pages/FundingOpportunities/visuals/caption/visual.json").read_text())
            generated_text = generated["visual"]["objects"]["general"][0]["properties"]["paragraphs"][0]["textRuns"][0]["value"]
            self.assertEqual(generated_text, text)

    def test_report_generator_keeps_funder_filter_on_existing_grants_page(self):
        import sys
        sys.path.insert(0, str(ROOT / "scripts"))
        from build_report import build

        with tempfile.TemporaryDirectory(dir=ROOT.parent) as temporary:
            candidate = Path(temporary) / "report"
            shutil.copytree(ROOT / "powerbi/CHHHS Research Publications.Report", candidate)
            build(output_dir=candidate, selected_pages=["FundingOpportunities"])
            visual = json.loads((candidate / "definition/pages/FundingOpportunities/visuals/grant-funder-filter/visual.json").read_text())
            self.assertEqual(visual["visual"]["query"]["queryState"]["Values"]["projections"][0]["queryRef"], "GrantsRegistry.Funder")
            self.assertEqual((visual["position"]["x"], visual["position"]["y"]), (32, 304))
            register = json.loads((candidate / "definition/pages/FundingOpportunities/visuals/grant-register/visual.json").read_text())
            self.assertEqual(register["position"]["y"], 408)
            self.assertEqual(register["position"]["height"], 480)

    def test_local_model_does_not_claim_calendar_or_personal_watchlist_bindings(self):
        model = json.loads((ROOT / "audit/model.snapshot.json").read_text())["model"]
        tables = {table["name"] for table in model["tables"]}
        self.assertFalse({"Funding Calendar", "My Funding Watchlist", "Funding Delivery Ledger"} & tables)

    def test_review_kpi_counts_only_records_needing_review(self):
        model = json.loads((ROOT / "audit/model.snapshot.json").read_text())["model"]
        grants = next(table for table in model["tables"] if table["name"] == "GrantsRegistry")
        expression = next(measure["expression"] for measure in grants["measures"]
                          if measure["name"] == "Grant Opportunities Needing Review")
        self.assertIn('GrantsRegistry[ReviewStatus] = "Needs Review"', expression)
        self.assertNotIn('"accepted"', expression)
        tmdl = (ROOT / "powerbi/CHHHS Research Publications.SemanticModel/definition/tables/GrantsRegistry.tmdl").read_text()
        self.assertIn(expression, tmdl)

    def test_source_row_url_is_a_distinct_web_link_on_the_grants_model(self):
        model = json.loads((ROOT / "audit/model.snapshot.json").read_text())["model"]
        grants = next(table for table in model["tables"] if table["name"] == "GrantsRegistry")
        row_url = next(column for column in grants["columns"] if column["name"] == "SourceRowURL")
        self.assertEqual(row_url["dataCategory"], "WebUrl")
        self.assertNotEqual(row_url["lineageTag"], next(
            column["lineageTag"] for column in grants["columns"] if column["name"] == "URL"
        ))
        tmdl = (ROOT / "powerbi/CHHHS Research Publications.SemanticModel/definition/tables/GrantsRegistry.tmdl").read_text()
        self.assertIn("column SourceRowURL", tmdl)
        self.assertIn("sourceColumn: SourceRowURL", tmdl)

    def test_registry_partition_uses_the_canonical_transformed_query(self):
        query = (ROOT / "config/GrantsRegistry.m").read_text().splitlines()
        snapshot = json.loads((ROOT / "audit/model.snapshot.json").read_text())["model"]
        expression = next(item for item in snapshot["expressions"] if item["name"] == "GrantsRegistry")
        self.assertEqual(expression["expression"], query)
        model_tmdl = (ROOT / "powerbi/CHHHS Research Publications.SemanticModel/definition/model.tmdl").read_text()
        expression_body = "\n".join("\t" + line for line in query)
        self.assertIn("expression GrantsRegistry =\n" + expression_body, model_tmdl)
        self.assertIn("lineageTag: " + expression["lineageTag"], model_tmdl)
        registry_tmdl = (ROOT / "powerbi/CHHHS Research Publications.SemanticModel/definition/tables/GrantsRegistry.tmdl").read_text()
        self.assertIn("partition GrantsRegistry = m\n\t\tmode: import\n\t\tsource =\n\t\t\tGrantsRegistry", registry_tmdl)
        self.assertNotIn("SharePoint.Tables(", registry_tmdl)


if __name__ == "__main__":
    unittest.main()
