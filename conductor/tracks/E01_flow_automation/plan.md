# Implementation Plan: E01 Power Automate Ingestion Canonicalization and Recurrence Scheduling

## Phase 1: Trigger & Nomenclature Canonicalization
- [x] Task 1.1: Refactor `config/flows/publication-registry-upsert.definition.json` to replace the manual button trigger with a 20:00 UTC (06:00 AEST) daily recurrence trigger.
- [x] Task 1.2: Update flow display name from `"CHHHS Publications - DEV manual ingestion validation"` to `"CHHHS Research Publications - Daily Ingestion & Enrichment"`.
- [x] Task 1.3: Update `config/flows/manifest.template.json` to enforce canonical naming across all root and child resource definitions.

## Phase 2: Package Build Automation
- [x] Task 2.1: Update `scripts/build_sharepoint_upsert_package.py` to bake recurrence trigger and canonical name directly into deployable zip files.
- [x] Task 2.2: Execute `python3 scripts/build_sharepoint_upsert_package.py` to generate `private/ops/flow-packages/sharepoint-upsert.zip`.
- [x] Task 2.3: Verify zip contents via inspection script to ensure definition and manifest integrity.

## Phase 3: Verification & Downstream Handshake
- [x] Task 3.1: Confirm timing alignment with Power BI dataset `{{ISOLATED_MODEL_ID}}` daily 07:00 AEST scheduled refresh.
- [x] Task 3.2: Confirm local validation contracts pass with zero errors (`validate_project.py` and `webfirst_contracts.py`).
## Reopened acceptance audit — 2026-09-20

Earlier checked tasks describe historical implementation. They do not close current operational acceptance.

- [ ] Verify remaining native execution, replay/readback and reconciliation against current private receipts.
- [ ] Record release and schedule status separately from local test/package completion.

## Phase 4: Local flow defect remediation
- [x] Separate the Power BI readiness summary query from the publication-row query consumed by the SharePoint upsert loop; add a nonblank `SourceKey` contract and regression test.
- [~] Re-deploy the corrected definition only to the approved isolated/manual route and capture create, replay/update, duplicate and failed-batch readback. The 2026-09-21 live retest proves corrected readiness/query/loop execution and SharePoint lookup; create/replay/update, duplicate, failed-batch, reconciliation and unattended-cycle evidence remain open.

## Phase: Live query retest evidence — 2026-09-21

- [x] Re-test the retained canonical DEV scheduled flow after the `DatasetExecuteQueriesError`; bounded `TOPN(100)`/`SELECTCOLUMNS` publication projection succeeded through the serial loop and SharePoint `Get items`.
- [x] Record the current run IDs and connector/list boundary in the ignored private receipt; retain the organisation-wide target, replay/update, duplicate, failed-batch, reconciliation and unattended-schedule gates as open.

## Phase: Conductor review — 2026-09-21

- [x] Review the corrected flow definition, builder, live retest evidence and local regression results; retain E01 as in progress because native operational acceptance is incomplete.

## Phase: Target-package hardening — 2026-09-21

- [x] Harden `load_target` to reject non-HTTPS site targets and empty or unresolved field mappings before package generation (`b6cc2e9`).
- [x] Add regression coverage for malformed site URLs and empty mappings; the latest local verification reports 354 tests with 8 skips.
