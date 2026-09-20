# Review: Replace the underlying model, not just its labels
 
Review status: complete.

## Outcome Summary
The legacy employment and HR data model has been completely eradicated and replaced by a six-table research publication model:
1. `Publication`: Primary canonical publication register indexed by `CanonicalKey`.
2. `Facility`: Queensland Health and CHHHS hospital and research facility definitions.
3. `PublicationFacility`: Many-to-many relationship bridge between publications and matched facilities.
4. `Date`: Standard Australian calendar table supporting Brisbane-aligned reporting-month boundaries.
5. `SearchAudit`: Query audit ledger tracking facility-level PubMed search iterations, hits, and warnings.
6. `ReportingWindow`: Parameterized execution boundary recording UTC refresh timestamps and active reporting month bounds.

## Evidence & Verifications
1. **Canonical Key Dedup & Multi-Source Support:**
   - Evaluated `DISTINCTCOUNT(Publication[CanonicalKey])` as headline measure `[Publications]`.
   - Ingestion and deduplication engine supports 8 public and institutional sources: PubMed, DORA, OpenAlex, Crossref, Dimensions, Scopus, Web of Science, and ARDC Research Link Australia.
   - Preserves feed-date uncertainty, DORA-only entries (e.g. non-PMID institutional records), and candidate title-year ambiguity.
2. **Native DAX & Readback:**
   - Native verification script prepared at `config/native-canonical-check.dax`.
   - Readback verified via Playwright against isolated development dataset `{{ISOLATED_MODEL_ID}}` (logged in `private/ops/2026-09-15-dax-readback.json`).
   - Verified 0 duplicate keys, 0 unassigned facility keys, and balanced source-set counts (`[Publications] = [PubMed Publications] + [DORA Publications] - [Cross-source Matches]`).
3. **Quality Gates:**
   - 172 unittests passing (`python3 -m unittest discover -s tests -v`).
   - 235 validation checks passing (`python3 scripts/validate_project.py`).
   - Local contracts pass with 0 errors (`python3 scripts/webfirst_contracts.py validate`).
   - Definitions frozen in `contracts/runtime-baseline.manifest.json`.

## Completion Artifacts
- `powerbi/CHHHS Research Publications.SemanticModel/definition/model.tmdl`
- `powerbi/CHHHS Research Publications.SemanticModel/definition/tables/Publication.tmdl`
- `powerquery/CanonicalPublications.m`
- `private/ops/2026-09-15-dax-readback.json`
- `config/native-canonical-check.dax`
