import unittest

from scripts.verify_retained_canary_metadata_values import _check_dora_identity, _date_parts, _dora, _pubmed, query, verify


def node(name, value):
    return {"Name": name, "Namespace": "", "Value": value, "Attributes": []}


class RetainedCanaryMetadataValuesTests(unittest.TestCase):
    def test_pubmed_nested_text_and_raw_date(self):
        payload = [node("MedlineCitation", [node("PMID", "123"), node("Article", [
            node("ArticleTitle", [node("i", "Exact"), node("b", " title")]),
            node("Journal", [node("Title", "Journal"), node("JournalIssue", [node("PubDate", [node("Year", "2020"), node("Month", "Feb")])])]),
            node("AuthorList", [node("Author", [node("ForeName", "A"), node("LastName", "Smith")])]),
            node("Abstract", [node("AbstractText", "First"), node("AbstractText", "Second")]),
        ])])]
        result = _pubmed(payload)
        self.assertEqual(result["Title"], "Exact title")
        self.assertEqual(result["Authors"], "A Smith")
        self.assertEqual(result["Abstract"], "First\nSecond")
        self.assertEqual((result["PublicationDateRaw"], result["PublicationDatePrecision"], result["PublicationYear"]), ("2020 Feb", "month", 2020))

    def test_dora_preserves_missing_and_ordered_distinct_fields(self):
        payload = [{"Field": k, "Value": v} for k, v in [
            ("dc.title", "Title"), ("dc.contributor.author", "A"), ("dc.contributor.author", "A"),
            ("dc.contributor.author", "B"), ("dc.date.issued", "2025"),
            ("dc.identifier.journaltitle", ""), ("dc.relation.ispartof", "Fallback"),
        ]]
        result = _dora(payload)
        self.assertEqual(result["Authors"], "A; B")
        self.assertEqual(result["Journal"], "")
        self.assertIsNone(result["DOI"])
        self.assertEqual(result["PublicationDatePrecision"], "year")

    def test_ambiguous_range_preserved(self):
        self.assertEqual(_date_parts("2020 Jan-Feb"), ("range", 2020))
        self.assertEqual(_date_parts("2020 02 30"), ("unknown", 2020))

    def test_rss_profile_keeps_timestamp_unverified_after_metadata_replay(self):
        fields = [{'Field': 'rims.source.format', 'Value': 'dora_rss_v1'},
                  {'Field': 'dc.title', 'Value': 'RSS title'},
                  {'Field': 'rims.rss.pubDate', 'Value': '2026-10-11'},
                  {'Field': 'dc.date.issued', 'Value': '2026-10-11'}]
        row = _dora(fields)
        self.assertEqual((row['PublicationDateRaw'], row['PublicationDatePrecision'], row['PublicationYear']),
                         ('2026-10-11', 'unknown', None))
        fields[0]['Value'] = 'unqualified-profile'
        with self.assertRaisesRegex(ValueError, 'unsupported'):
            _dora(fields)

    def test_query_uses_projected_columns(self):
        self.assertIn("'RetainedPubMedPublications'[PublicationDateRaw]", query("PubMed"))
        self.assertIn("'RetainedDoraPublications'[DOI]", query("DORA"))

    def test_exact_value_mismatch_is_fail(self):
        expected = {"DORA:x": {"Title": "A", "Authors": "", "Abstract": "", "PublicationDateRaw": "2025", "PublicationDatePrecision": "year", "PublicationYear": 2025, "PMID": None, "DOI": None, "Journal": None}}
        model_row = {f"[{k}]": v for k, v in {"DORAKey": "DORA:x", **expected["DORA:x"]}.items()}
        model_row["[Title]"] = "B"
        payload = {"results": [{"tables": [{"rows": [model_row]}]}]}
        receipt, differences = verify(payload, expected, "DORA")
        self.assertEqual(receipt["status"], "FAIL")
        self.assertEqual(differences[0]["field"], "Title")

    def test_engine_case_and_trailing_spaces_are_classified_only_for_display_text(self):
        fields = {"Title": "Title", "Authors": "de Costa; Study Group ", "Abstract": "", "PublicationDateRaw": "2025", "PublicationDatePrecision": "year", "PublicationYear": 2025, "PMID": None, "DOI": None, "Journal": "ANZ journal of surgery"}
        row = {f"[{k}]": v for k, v in {"DORAKey": "DORA:x", **fields}.items()}
        row["[Authors]"] = "De Costa; Study Group"
        row["[Journal]"] = "ANZ Journal of Surgery"
        receipt, differences = verify({"results": [{"tables": [{"rows": [row]}]}]}, {"DORA:x": fields}, "DORA")
        self.assertEqual(receipt["status"], "PASS_WITH_ENGINE_NORMALIZATION")
        self.assertEqual(receipt["engine_text_normalizations"], 2)
        self.assertEqual({d["kind"] for d in differences}, {"engine_text_normalization"})
        row["[PublicationDateRaw]"] = "2025 "
        receipt, differences = verify({"results": [{"tables": [{"rows": [row]}]}]}, {"DORA:x": fields}, "DORA")
        self.assertEqual(receipt["status"], "FAIL")
        self.assertIn({"source_id": "DORA:x", "field": "PublicationDateRaw", "kind": "value_mismatch"}, differences)

    def test_omitted_blank_property_is_null_but_not_empty_text(self):
        fields = {"Title": "A", "Authors": "", "Abstract": "", "PublicationDateRaw": "2025", "PublicationDatePrecision": "year", "PublicationYear": 2025, "PMID": None, "DOI": None, "Journal": None}
        row = {f"[{k}]": v for k, v in {"DORAKey": "DORA:x", **fields}.items() if v is not None}
        payload = {"results": [{"tables": [{"rows": [row]}]}]}
        receipt, differences = verify(payload, {"DORA:x": fields}, "DORA")
        self.assertEqual((receipt["status"], differences), ("PASS", []))
        del row["[Authors]"]
        receipt, differences = verify(payload, {"DORA:x": fields}, "DORA")
        self.assertEqual(receipt["status"], "FAIL")
        self.assertEqual(differences[0]["field"], "Authors")

    def test_dora_identity_requires_exact_uri_and_title(self):
        url = "https://example.test/handle/1/7"
        summary = {"DORAURL": url}
        metadata = [{"Field": "dc.identifier.uri", "Value": "http://example.test/handle/1/7"}]
        _check_dora_identity("DORA:" + url, summary, metadata, {"Title": "Title"})
        with self.assertRaises(ValueError):
            _check_dora_identity("DORA:" + url, summary, metadata + [{"Field": "dc.identifier.uri", "Value": "https://other.test/7"}], {"Title": "Title"})
        with self.assertRaises(ValueError):
            _check_dora_identity("DORA:" + url, summary, metadata, {"Title": None})


if __name__ == "__main__":
    unittest.main()
