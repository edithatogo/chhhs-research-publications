# Review: Export every citation and stage the monthly workflow
 
Review status: in progress; local export generation and contract checks are complete, while current native and operational acceptance gates remain open.

## Synchronized verification — 2026-09-22

The canonical checkout passes 450 tests (8 skipped), 460 project checks,
Conductor validation and source-only CI run `35657921400`. Native refresh,
complete export readback, consecutive-cycle preservation and delivery remain
unproven.

## Outcome Summary
1. **Full Bibliography Export Engine:**
   - Implemented `scripts/export_publication_register.py` ensuring every expected canonical record is exported with complete metadata (authors, title, journal, raw date, date precision, identifiers, and hyperlinks) without truncation.
   - Formula safety: Protects against CSV injection by escaping leading formula triggers (`=`, `+`, `-`, `@`).
   - HTML rendering: Escapes user inputs and produces print-ready citation layouts.
2. **Automated Monthly Word (DOCX) Report Generation:**
   - Developed `scripts/export_monthly_docx.py` generating executive Word reports styled to Queensland Health Clinical Research branding (Deep Teal `#005C8A`, Slate `#2B3E50`, Emerald `#107C41`).
   - Summary KPI cards: Total publications, Peer-reviewed count, Open Access percentage, Primary HHS affiliation count.
   - Facility and Source distribution breakdown tables.
   - Complete bibliography with live PubMed and DOI links.
   - Verified runs: `reports/CHHHS-Publications-Monthly-2026-08.docx` (9 records), `reports/CHHHS-Publications-Monthly-2026-07.docx` (9 records), `reports/CHHHS-Publications-Monthly-2026-06.docx` (15 records).
3. **Power Automate Monthly Architecture & Packages:**
   - Designed declarative monthly ingestion and upsert flow: `config/flows/publication-registry-upsert.definition.json`.
   - Exported deployment package: `private/ops/flow-packages/sharepoint-upsert.zip`.
   - Monthly blueprints: `config/monthly-flow.blueprint.json` and `docs/MONTHLY_AUTOMATION.md`.

## Quality Gates
- 18 export policy unit tests passing in `tests/test_webfirst.py` (`ExportPolicyTests`).
- Validated against `contracts/publication-export.contract.json`.
- 172 total unit tests and 235 project validation checks passing cleanly.

## Reopened acceptance review — 2026-09-21

The historical local outcome above remains valid as implementation evidence,
but it is not a current tenant acceptance certificate. The automatic-update
plan still requires a manual native cloud-flow cycle, consecutive-cycle
retention/replay evidence, current refresh/export reconciliation, and a
separate schedule/delivery decision. The trigger remains disabled and no
recipient or schedule has been activated. T14 remains active and is not
eligible for archive.

### Review Report

- Plan compliance: Partial — local exports, dry-run/failure contracts and
  blueprints are present; native cycle and consecutive-cycle gates are open.
- Style/safety: Pass — no delivery or recipient activation is implied by the
  local artefacts.
- Tests: Passed locally; native acceptance remains unproven.

## Local contract hardening — 2026-09-21

The review found that paged export reconciliation accepted `True` as a count
of one and allowed blank independent keys. Commit `dfb71f6` now rejects
non-negative-integer violations and blank keys before a batch can reconcile.

### Verification Checks

- [x] Plan Compliance: Partial — local export and reconciliation contracts are hardened; native cycle, retention and delivery gates remain open.
- [x] Style Compliance: Pass — the change is fail-closed and preserves the canonical-key contract.
- [x] New Tests: Yes — explicit invalid-count and blank-key regression cases.
- [x] Test Coverage: Partial — local batch validation is covered; native refresh/export/SharePoint readback is not.
- [x] Test Results: Passed — canonical-clone full suite (374 tests, 8 skipped) and 438 project checks.

### Findings

The local reconciliation issue is fixed. T14 remains in progress because its
manual native cycle, consecutive-cycle history, refresh correlation and
delivery decisions are not currently evidenced.

## Conductor review — local export-fidelity execution evidence — 2026-09-21

- **Verification:** 64 web-first export-policy tests and 5 publication-batch contract tests passed. Coverage includes multi-page scope, long/Unicode fields, DORA-only/no PMID, formula-safe CSV, duplicate/missing keys, uncertain months and date-boundary behaviour.
- **Boundary:** this closes the local execution checklist item only. Correlated native refresh, complete file readback, consecutive replay and delivery remain open.
