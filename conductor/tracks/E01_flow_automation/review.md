# Track Review: E01 Power Automate Ingestion Canonicalization and Recurrence Scheduling

## Implementation Summary
1. **Flow Definition Canonicalized:**
   - File: `config/flows/publication-registry-upsert.definition.json`
   - Name: `CHHHS Research Publications - Daily Ingestion & Enrichment`
   - Trigger: `Recurrence` daily at 20:00 UTC (06:00 AEST).
2. **Manifest Template Canonicalized:**
   - File: `config/flows/manifest.template.json`
   - Name: `CHHHS Research Publications - Daily Ingestion & Enrichment`
3. **Build Script & Deployable Package:**
   - Generator: `scripts/build_sharepoint_upsert_package.py` updated to inject the recurrence trigger.
   - Package: `private/ops/flow-packages/sharepoint-upsert.zip` generated and verified.
4. **Platform Handshake:**
   - The flow runs 1 hour prior to the dataset refresh at 07:00 AEST, ensuring the Power BI model consumes the latest daily SharePoint upserts.

## Native DEV flow test — 2026-09-20

The current Power Automate environment was inspected through authenticated
Playwright UI readback. The active history-commit DEV flow completed all six
actions successfully after changing both text failure markers from `int(...)` to
plain text. Flow Checker returned zero errors and zero warnings. The manual
ingestion DEV flow completed its Power BI query, SharePoint `Get items`,
new-publication condition and the True-branch `SharePoint Create item`
successfully; the False-branch update was skipped for the new row. Its list
action read back HTTP 200 from the configured `Publication Registry` list. That
flow was restored to Off after the manual test. The private run evidence is
`private/ops/2026-09-20-powerautomate-publication-flow-tests.json`.

This closes current DEV/manual execution evidence only. It does not close the
recurrence deployment, unattended schedule, full registry reconciliation or
production release gates.

The controlled replay also succeeded but again took the Create branch and skipped
Update. The observed blank SourceKey filter means this is not idempotency proof;
duplicate prevention and a nonblank-key update readback remain open.

## Review remediation — 2026-09-20

The first source-only review found that the tracked JSON definition and generated
package were not the same action graph. The readiness query returned a single
summary row, while the loop treated it as a publication; this explains the
blank `SourceKey` filter observed in the native replay. The tracked definition
and builder now share the corrected graph: readiness, a dedicated canonical
`Publication` rows query, a serial upsert loop, duplicate-key fail-closed
handling, and the protected update allowlist.

Local verification: `python3 scripts/validate_publication_platform_contract.py`,
JSON parsing, and the full unittest suite (283 tests) pass. This is still
source-only evidence. The isolated tenant deployment and create/replay/update,
duplicate, failed-batch, recurrence and reconciliation readback tasks remain
open, so the track remains in progress and must not be archived yet.

The corrected package was subsequently imported and read back on the retained
canonical DEV scheduled-flow identity. Both Power BI actions use the same
isolated model. Power Automate readback showed the canonical flow name, the
`Recurrence -> readiness -> publication rows -> Apply to each Publication`
chain, Flow Checker `Errors (0)` and `Warnings (0)`, and the flow Disabled. The
redundant disabled manual duplicate was removed, leaving one canonical flow
identity.
The actual recurrence run remains gated because activation requires explicit
approval.

## Current native status readback — 2026-09-20

The canonical flow details page was re-read through the authenticated Power
Automate UI. The flow is currently **Off**. Flow Checker reports **0 errors**
and **1 warning**; the warning is the expected inactive-flow warning, not a
proof of action correctness. The visible 28-day history contains 2 succeeded,
1 test-failed and 3 failed runs. This mixed history does not establish
consecutive-cycle, unattended, recurrence or release acceptance.

No edit, enable, run, list write or schedule activation was performed during
this readback. The evidence is recorded in the ignored private receipt
`private/ops/2026-09-20-powerautomate-publication-flow-tests.json`. Native
execution, replay/update and reconciliation gates therefore remain open.

## Current live retest correction — 2026-09-21

The authenticated Power Automate UI was used to run the retained canonical
scheduled DEV flow after isolating the prior failure. The original
`Run publication rows query` returned HTTP 400 `DatasetExecuteQueriesError`,
so the SharePoint loop was skipped. `EVALUATE TOPN(1, Publication)` succeeded,
proving the dataset and `Publication` table were reachable. The rows query was
then changed to a bounded `TOPN(100)` plus `SELECTCOLUMNS` projection, removing
the redundant nested readiness filter.

The corrected run read back `Succeeded` for the recurrence, readiness query,
publication rows query and 100-record `Apply to each Publication` loop. The
inspected `SharePoint Get items` action also succeeded against the
`Publication Registry` list. Flow Checker read back 0 errors and 0 warnings;
the flow was left On, matching its prior scheduled state. Run IDs and the
private list readback are recorded in
`private/ops/2026-09-20-powerautomate-publication-flow-tests.json`.

This closes the current DEV flow execution blocker. It does not prove
organisation-wide target ownership, unattended consecutive cycles, complete
registry reconciliation, or production acceptance; those gates remain open.

## Review Report: E01 Flow Automation — 2026-09-21

### Summary

The corrected publication rows query is consistent between the tracked flow definition and package builder, and the authenticated DEV retest proves the intended Power BI-to-SharePoint action path. The track remains in progress because the broader native operational acceptance contract is not complete.

### Verification Checks

- [x] Plan Compliance: Partial — the corrected-query retest is complete; replay/update, duplicate, failed-batch, reconciliation and unattended-cycle tasks remain open.
- [x] Style Compliance: Pass — the definition remains SharePoint-list-backed and preserves the existing serial, fail-closed graph.
- [x] New Tests: Yes — bounded-projection contract coverage was added.
- [x] Test Coverage: Partial — local contracts and live DEV execution are covered; full native operational acceptance is not.
- [x] Test Results: Passed — canonical-clone full suite (338 tests, 8 skipped), 438 project checks and Conductor validation passed; the prior live corrected run succeeded.

### Findings

No new implementation findings. The documented open acceptance gates are substantive, not review defects, so E01 is not eligible for archive.
