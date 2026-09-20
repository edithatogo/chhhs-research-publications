# Review: Implement the three-page publication report
 
Review status: complete.

## Outcome Summary
The Power BI report visual layer has been cleanly reconstructed to implement the approved three-page research specification:
1. **CHHHS Publications (Live Register Page):**
   - KPI headline cards: Total Publications (`[Publications]`), PubMed-indexed, DORA-indexed, Cross-source overlap.
   - Interactive slicers: Publication Year, Primary Source, Review Status, Matched Facility.
   - Flowing full publication register (`tableEx`) with article title, raw date, date precision, authors, journal, DOI/PubMed/DORA hyperlinks, and facility attributions.
2. **Monthly Publications (Printable Prior-Month Report):**
   - Single-month selector (`Date[YearMonth]`) defaulting to the previous complete Brisbane calendar month.
   - Monthly publication volume trend, YoY comparison, and source distribution charts.
   - Dedicated monthly register displaying citations for the active reporting window.
3. **Source Reconciliation (Provenance & Integrity):**
   - Multi-source coverage breakdowns (PubMed only, DORA only, cross-source merged).
   - Ingestion audit: Query warnings count, configured facility searches count, last UTC refresh timestamp.
   - Attribution evidence and deduplication methodology indicators (`DedupMethod`, `AttributionEvidence`).

## Visual Cleansing
- All legacy HR, employee, gender, and workforce visuals, measures, and filter pods were removed.
- Generated via `scripts/build_report.py` and `scripts/build_legacy_report_json.py`.
- Full definition stored at `private/ops/report-definition-updated.json`.
- Visual design specification documented in `docs/THREE_PAGE_REPORT.md`.

## Quality Gates
- Exact three-page scope enforced and verified by `scripts/webfirst_contracts.py`.
- 172 unittests passing.
- 235 validation checks passing in `scripts/validate_project.py`.
