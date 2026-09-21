# Track Review: E01 Power Automate Ingestion Canonicalization and Recurrence Scheduling

## Synchronized verification — 2026-09-22

The canonical checkout passes 444 tests (8 skipped), 460 project checks,
Conductor validation and source-only CI run `35655033968`. This is local and
source-only evidence. The QLD Health null-date branch was explored but not
saved after the authenticated browser session was lost; no native Flow
Checker/readback or replay is claimed, and the canonical flow remains Off.

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
JSON parsing, and the full unittest suite pass. This is still
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
- [x] Test Results: Passed — canonical-clone full suite (374 tests, 8 skipped), 438 project checks and Conductor validation passed; the prior live corrected run succeeded.

### Findings

One local packaging defect was found and fixed in commit `b6cc2e9`: the private publication target loader now requires a concrete HTTPS site URL and non-empty, placeholder-free field mappings before a package can be built. Two regression tests cover those fail-closed cases. The documented native acceptance gates remain substantive, not review defects, so E01 is not eligible for archive.

## Conductor review — local builder and flow-contract execution evidence — 2026-09-21

- **Verification:** 16 focused publication-platform contract tests passed, with 8 tests correctly skipped because the private live package is absent from the source-only clone; `validate_publication_platform_contract.py` passed against the tracked definition.
- **Boundary:** local loop scope, connector/action safeguards and target-loader checks are covered. Native flow execution, replay/update, failure safety, reconciliation and schedule acceptance remain open.

## Conductor review recheck — 2026-09-22

### Summary

Local publication-flow contracts, package hardening and regression coverage
remain sound. The native QLD Health acceptance gate is still incomplete and
the track must remain active.

### Verification Checks

- [x] Plan Compliance: Partial — the source definition and validator cover the
  required branch graph; native replay/update, failure-safe reconciliation and
  unattended scheduling remain open.
- [x] Style Compliance: Pass — the flow remains SharePoint-list-backed,
  current-user scoped and fail-closed.
- [x] New Tests: No new source test was required for this browser-only retry;
  the existing validator and regression suite remain applicable.
- [x] Test Coverage: Partial — local contracts and prior native non-null
  execution are covered; native null-date acceptance is not.
- [x] Test Results: Passed — 444 tests passed with 8 skips, 460 project
  checks passed, and Conductor validation reported 0 structural errors.

### Findings

#### Medium — native null-date branch cannot yet be authored through the tenant UI

- **Evidence:** the QLD Health classic designer allowed an unsaved Condition
  shell to be inserted in the existing `Condition Is New Calendar Row` yes
  branch, but rejected the explicit current-item null expression and then
  stalled while reopening dynamic content. The draft was discarded by reload;
  no Save operation occurred.
- **Impact:** the tracked null-preserving definition is locally valid, but it
  is not a native implementation receipt. The flow remains the sole canonical
  target and native null/non-null create/update/readback remains open.
- **Action:** retain the native gate as `[~]`; retry only through a responsive
  QLD Health route or a successfully parsed/importable package. Do not archive
  E01 or claim tenant acceptance from this attempt.

## Conductor review — duplicate-write fail-closed correction — 2026-09-21

## Local flow validator coverage — 2026-09-21

The publication definition continues to pass its standalone structural
validator, and the source-only workflow now runs both canonical flow
validators on every push and pull request. This closes the local CI coverage
gap for tracked flow definitions; it does not replace native replay, list
readback, reconciliation or schedule evidence.

The CI test now asserts that both validator commands remain present, preventing
future workflow drift from silently dropping flow-contract coverage.

- **Finding:** the publication flow diagnosed duplicate `SourceKey` matches but its update branch could still be reached for a lookup result larger than one row.
- **Fix:** commit `22b5df1` adds an exact-one-match update condition; duplicate matches cannot reach the SharePoint update action. The validator and regression tests enforce the guard.
- **Verification:** focused publication-contract tests pass (17, with 8 private-package cases skipped); the full local suite remains 374 tests with 8 skips. The corrected definition requires isolated native re-import/readback before E01 acceptance can advance.

## Conductor review — publication target uniqueness contract — 2026-09-21

### Summary

The publication target template now declares `source_key` as its sole unique
field, and the private package builder rejects concrete targets that omit or
alter that contract. This aligns package admission with the flow's duplicate
`SourceKey` lookup and protects the idempotent registry identity locally. Code
commit: `71912c7a41bfd05084ef75eedb4cf4dd4bd4db8e`.

### Verification Checks

- **Plan Compliance:** Partial — local target/flow identity coupling is
  implemented; native target readback, replay/update and unattended acceptance
  remain open.
- **Style Compliance:** Pass — the existing SharePoint field mapping and
  canonical list design are preserved.
- **New Tests:** Yes — 18 focused publication-contract tests, including missing
  unique-target metadata; 8 private-package tests remain correctly skipped when
  the ignored live package is absent.
- **Test Results:** Passed — full suite (407 passed, 8 skipped), 438 project
  checks, Conductor validation (0 errors), web-first `PASS_LOCAL_ONLY`, Power
  Platform tooling preflight, visual standards, both canonical flow validators
  and `git diff --check`.

### Findings

- **Fixed:** the target template and loader did not machine-check that
  `SourceKey` was unique, despite the flow relying on that invariant.
- **Residual acceptance:** native SharePoint uniqueness/schema readback,
  organisation-wide target ownership, replay/update, reconciliation and
  unattended scheduling remain unproven. No tenant mutation was made.

The companion architecture documentation now states the same `SourceKey`
uniqueness requirement as the machine-readable target contract; this is a
documentation alignment only and does not constitute native schema readback.

## Conductor review — configured SourceKey lookup binding — 2026-09-21

### Summary

The publication SharePoint package builder now derives the lookup `$filter`
from the configured `source_key` internal field mapping instead of hardcoding
`field_1`. This keeps target injection and idempotent lookup aligned for
non-default SharePoint schemas. Code commit: `996d1f3036b7b36b5eafa776770a1b47b79a4804`.

### Verification Checks

- **Plan Compliance:** Partial — local package generation and contract coverage
  are improved; native import, replay/update, list readback and unattended
  acceptance remain open.
- **Style Compliance:** Pass — the existing target contract and SharePoint
  operation model are preserved.
- **New Tests:** Yes — a synthetic package test verifies that a custom
  `SourceKeyInternal` mapping is used in the generated lookup filter.
- **Test Results:** Passed — full suite (414 passed, 8 skipped), 438 project
  checks, Conductor validation (0 errors), web-first `PASS_LOCAL_ONLY`, Power
  Platform tooling preflight, visual standards, canonical flow validators and
  `git diff --check`.

### Findings

- **Fixed:** generated publication packages could look up `field_1` even when
  the configured SourceKey internal field had another name.
- **Residual acceptance:** native SharePoint schema/row readback, replay,
  complete reconciliation and unattended scheduling remain unproven. No
  tenant mutation was made.

## Conductor review — publication projection fail-closed columns — 2026-09-21

### Summary

The SharePoint-backed publication projection now uses `MissingField.Error`
instead of `MissingField.UseNull`, preventing missing registry columns from
being silently converted to nulls during bibliography ingestion. Code commit:
`a1d33051c2a31c2dc47a5cd44ee1ee0da659a5fc`.

### Verification Checks

- **Plan Compliance:** Partial — local publication schema-drift handling is
  hardened; native list/readback and complete reconciliation remain open.
- **Style Compliance:** Pass — the existing publication field projection and
  review-state semantics are unchanged.
- **New Tests:** Yes — a Power Query contract test asserts fail-closed missing
  column behavior.
- **Test Results:** Passed — full suite (413 passed, 8 skipped), 438 project
  checks, Conductor validation (0 errors), web-first `PASS_LOCAL_ONLY`, Power
  Platform tooling preflight, visual standards, canonical flow validators and
  `git diff --check`.

### Findings

- **Fixed:** missing publication columns could previously appear as valid null
  values, weakening complete registry reconciliation.
- **Residual acceptance:** native SharePoint schema/row readback, replay,
  complete key-set reconciliation and unattended scheduling remain unproven.
  No tenant mutation was made.

## Conductor review — publication target type boundary — 2026-09-21

### Summary

The publication target loader now validates target identifiers and field
mappings as strings before trimming, GUID parsing or package generation. This
prevents malformed configuration values from being silently coerced into a
native-looking target. Code commit: `7a3216519062c4fec266f866b86741c1579c62bb`.

### Verification Checks

- **Plan Compliance:** Partial — local target admission and package contract
  coverage are hardened; native import, replay/update, list readback and
  unattended acceptance remain open.
- **Style Compliance:** Pass — the SharePoint-only target and configured
  SourceKey binding remain unchanged.
- **New Tests:** Yes — publication contract tests cover non-string site/list/
  model identifiers and field mappings.
- **Test Results:** Passed — full suite (419 tests passed, 8 skipped), 438
  project checks, Conductor validation (0 errors), web-first, Power Platform,
  visual standards and both canonical flow validators.

### Findings

- **Fixed:** non-string target values could previously be stringified before
  validation, weakening the private target admission boundary.
- **Residual acceptance:** native SharePoint schema/row readback, replay,
  complete reconciliation and unattended scheduling remain unproven. No
  tenant mutation was made.
