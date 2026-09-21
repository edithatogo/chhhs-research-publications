# G07 review

## Conductor review — registry reconciliation identity boundary — 2026-09-22

- **Finding:** exact-key registry readback reconciliation stripped emitted and
  registry `OpportunityKey` values before comparison and could accept a padded
  key as reconciled, unlike the stricter operational evaluator.
- **Fix:** reconciliation now rejects surrounding whitespace separately for
  emitted and registry keys; the regression test confirms padded keys do not
  cross the reconciliation boundary.
- **Verification:** focused relationship/operations tests pass (22); the full
  suite passes 452 tests with 8 skips; project validation passes 460 checks;
  web-first, Conductor and diff validation pass locally.
- **Residual gate:** native duplicate/concurrency, monitoring, operational
  readback, recurrence, delivery and production acceptance remain open.

## Summary

Review status: in progress; local operational guardrails are implemented.

## Synchronized verification — 2026-09-22

The canonical checkout passes 456 tests (8 skipped), 460 project checks,
Conductor validation and source-only CI run `35660297803`. Native duplicate/
concurrency, monitoring, reconciliation, recurrence and delivery evidence
remain open.

`scripts/grants_operations.py` rejects empty batches, missing or duplicate opportunity keys, and any failed source. On rejection it returns the prior accepted records instead of replacing them. Tests cover source failure preservation. Native monitoring, concurrency and schedule/delivery evidence remains open. A controlled authenticated Power Automate replay now proves one synthetic create and one same-key update, with the flow restored Off; see the G03 review and the ignored receipt `private/ops/2026-09-20-grants-flow-import-readback.json`. No unattended schedule, notification or production path was touched.

Review fix applied: `evaluate_run` now rejects missing source health and
records whose source is not represented in the health results. Focused tests
cover both boundaries; prior accepted records remain preserved on rejection.

Review fix applied: the evaluator now rejects blank or duplicate source-health
rows and records without a source identity before accepting a batch.

Additional review fix applied in `91345bf`: health rows now require
non-negative integer counts, and per-source reported counts must exactly match
the records admitted from that source. Mismatches preserve the prior accepted
batch and fail closed.

## Verification Checks

- [x] **Plan Compliance**: Partial - local fail-closed evaluation and controlled DEV replay evidence exist; monitoring, operational reconciliation, delivery and scheduling remain open.
- [x] **Style Compliance**: Pass - the evaluator preserves prior accepted records and fails closed on missing evidence.
- [x] **New Tests**: Yes - missing health, unreported-source, duplicate-health and missing-record-source cases are covered.
- [x] **Test Coverage**: Partial - local run evaluation is covered; native monitoring and unattended delivery are not.
- [x] **Test Results**: Passed - focused G07 tests (13), project validation (438 checks) and canonical-clone full suite (374 tests, 8 skipped).

## Findings

### Medium - native operational acceptance remains open

- **File**: `conductor/tracks/G07_grants_operations/plan.md`
- **Context**: Controlled synthetic create/update runs do not prove monitoring, two successive complete live cycles, exact-key reconciliation, schedule or delivery acceptance.
- **Suggestion**: Keep G07 active until those native operational receipts are captured against an approved target; do not archive based on local evaluation or isolated DEV replay alone.

## Conductor review — identity fail-closed hardening — 2026-09-21

- **Finding:** `evaluate_run` string-coerced malformed source identities and could raise on an unhashable `OpportunityKey`, weakening the operational quarantine boundary.
- **Fix:** non-string source and opportunity identities are now rejected explicitly; duplicate checks only run over validated string keys. Regression coverage proves the malformed batch is rejected without coercion or an incidental exception.
- **Verification:** commit `42833c6` passes the focused relationship/operations suite (13 tests), the full local suite (374 tests, 8 skips), project validation (438 checks), web-first contracts and Conductor validation. Remote source-only CI remains to be recorded against the synchronized documentation commit.
- **Residual gate:** native monitoring, exact-key reconciliation, scheduling and delivery remain open.

## Conductor review — malformed run-object hardening — 2026-09-21

- **Finding:** `evaluate_run` assumed every record and health row was a mapping, so malformed batches could raise an incidental attribute error instead of entering the rejected-run path.
- **Fix:** commit `c174a3a` explicitly classifies non-object record and health rows as invalid, evaluates safe placeholders, and preserves the prior accepted batch.
- **Verification:** the focused relationship/operations suite passes (16 tests); full local and native operational gates remain as documented above.

## Conductor review — exact registry reconciliation — 2026-09-21

- **Finding:** the local evaluator checked source health counts but had no exact-key comparison between an emitted cycle and the subsequent registry readback.
- **Fix:** commit `994dc05` adds `reconcile_registry_keys`, which rejects malformed/duplicate keys, reports missing or unexpected registry identities, and preserves the prior accepted batch on mismatch.
- **Verification:** focused relationship/operations tests pass (18); full local suite passes (374 tests, 8 skips). This is a local reconciliation contract; native list readback, monitoring and scheduling remain open.

## Conductor review — selected-field readback reconciliation — 2026-09-21

- **Finding:** exact key-set equality did not detect a partial SharePoint update where a selected field value differed or was absent.
- **Fix:** `reconcile_registry_records` now requires an explicit unique field allowlist, checks every emitted key’s selected field values against registry readback, and preserves the prior accepted batch on any mismatch.
- **Verification:** focused relationship/operations tests pass (20); the full suite passes 383 tests with 8 skips and project validation passes 438 checks.
- **Residual gate:** this is a local reconciliation contract; native list readback, monitoring, scheduling and delivery remain open.

## Conductor review — reconciliation field allowlist hardening — 2026-09-21

- **Finding:** a single string field allowlist was iterated character-by-character, and surrounding whitespace was not canonicalized before selected-field comparison.
- **Fix:** commit `0eef31a` requires a collection-shaped allowlist, trims field names before uniqueness checks, and adds regression coverage.
- **Verification:** focused relationship/operations tests pass (20); the full suite passes 387 tests with 8 skips; project validation passes 438 checks; web-first, Conductor, Power Platform tooling and visual standards checks pass locally.
- **Residual gate:** native list readback, monitoring, scheduling and delivery remain open.

## Conductor review — operational identity whitespace boundary — 2026-09-21

- **Finding:** operational evaluation stripped source and opportunity identity
  values for comparisons but could accept and retain the original
  whitespace-bearing values.
- **Fix:** commit `1ac3d52` rejects whitespace-divergent record sources,
  health sources and opportunity keys, with regression coverage.
- **Verification:** focused relationships/operations tests pass (22); the full
  suite passes 426 tests with 8 skips; 438 project checks, Conductor,
  web-first, Power Platform, visual and canonical flow validators pass locally.
- **Residual gate:** native list readback, monitoring, exact-key operational
  reconciliation, scheduling and delivery remain open.

## Conductor review — normalized opportunity-key duplicate boundary — 2026-09-21

- **Finding:** operational duplicate detection compared raw opportunity-key
  strings, so keys differing only by surrounding whitespace could bypass the
  batch duplicate guard even though reconciliation canonicalizes them.
- **Fix:** commit `206588cffca8e6b6effedea19594219a56903bf3` compares the
  trimmed non-empty key set and adds regression coverage for the whitespace
  variant.
- **Verification:** focused relationship/operations tests pass (21); the full
  suite passes 416 tests with 8 skips, 438 project checks pass, and web-first,
  Conductor, Power Platform, visual and canonical flow validators pass
  locally.
- **Residual gate:** native list readback, monitoring, exact-key operational
  reconciliation, scheduling and delivery remain open.
## Conductor review recheck — 2026-09-22

The authenticated QLD Health details page confirms one canonical
`CHHHS Research Grants - Reviewed Import Upsert` flow
(`acf866e4-e4a2-4113-bce4-d2dd9e2f22d6`). It is owner-only,
SharePoint-connected and Off. Flow Checker reports Errors 0 and one warning
limited to the inactive state; the visible history contains succeeded and
test-succeeded runs.

This strengthens the isolated native execution evidence, but does not prove
duplicate/concurrency handling, failed-batch preservation, exact-key
reconciliation or unattended monitoring/delivery. G07 remains active and is
not eligible for archive. Receipt:
`private/ops/2026-09-22-powerautomate-g07-flow-readback.json`.

## Native malformed-batch test boundary — 2026-09-22

### Summary

The current-user manual test route accepted the malformed input field, but
Power Automate rejected execution before submission because the sole canonical
Grants flow is Off. No run ID was issued and no SharePoint write was observed.

### Verification checks

- [x] Canonical flow identity re-read: `acf866e4-e4a2-4113-bce4-d2dd9e2f22d6`.
- [x] Details page re-read: owner Dylan Mordaunt, SharePoint-connected, Status
  Off.
- [x] Test dialog readback: `ReviewedRowsJson=not-json` was present, followed
  by the explicit inactive-flow warning before submission.
- [x] Flow left Off; no enable, run, or data mutation was attempted.
- [ ] Native malformed-batch failure-safe run and list readback.

### Findings

This is a clean safety boundary, not a successful failure-path test. G07
remains active because native failed-batch preservation, duplicate/concurrency
handling, exact-key operational reconciliation and unattended monitoring or
delivery still require an approved execution cycle against the isolated
current-user target.

Receipt:
`private/ops/2026-09-22-powerautomate-g07-malformed-test-boundary.json`.

## Conductor review recheck — native malformed-batch execution — 2026-09-22

### Summary

The previously blocked failure-safe test was completed in a bounded
current-user cycle. The canonical flow was temporarily enabled, the malformed
payload was submitted, the run failed during JSON parsing before the loop, and
the flow was restored Off.

### Verification checks

- [x] Canonical flow identity: `acf866e4-e4a2-4113-bce4-d2dd9e2f22d6`.
- [x] Run ID: `08584115886238763797828484917CU13`.
- [x] Failure action: `Parse_Reviewed_Rows`.
- [x] Error: `json('not-json')` rejected with an invalid JSON
  `InvalidTemplate` error.
- [x] `Apply_to_each_Reviewed_Row` was not entered.
- [x] SharePoint `Grants Registry` readback returned an empty Atom feed.
- [x] Flow status was read back as Off after restoration.
- [ ] Native duplicate/concurrency and exact-key operational reconciliation.

### Findings

The native failed-batch preservation boundary is now evidenced for malformed
JSON with no registry mutation. G07 remains active for the remaining native
operational gates and is not eligible for archive.

Receipt:
`private/ops/2026-09-22-powerautomate-g07-malformed-test.json`.

## Conductor review recheck — native exact-key create/update/cleanup — 2026-09-22

### Summary

The canonical QLD Health Grants flow was temporarily enabled for a controlled
current-user cycle, then restored Off. One synthetic reviewed row was created,
the same `OpportunityKey` was updated in place, and the exact synthetic item
was removed. The final Grants Registry readback is empty.

### Verification checks

- [x] Canonical flow identity: `acf866e4-e4a2-4113-bce4-d2dd9e2f22d6`.
- [x] Create run succeeded: `08584115882832862098741138474CU12`.
- [x] Update run succeeded: `08584115882008512967727243474CU27`.
- [x] Same-key readback showed one item, ID 6, etag `"2"`, with the updated
  title; no second synthetic key was observed.
- [x] Exact cleanup readback returned an empty Atom feed.
- [x] Flow status was read back as Off after the cycle.
- [ ] Duplicate/concurrency, unattended monitoring/delivery and production
  acceptance.

### Findings

Native exact-key create/update/cleanup is now evidenced for the isolated
current-user DEV target. This does not prove duplicate/concurrency protection,
unattended monitoring, schedule or delivery acceptance. G07 remains active and
is not eligible for archive.

Receipt:
`private/ops/2026-09-22-powerautomate-g07-exact-key-cycle.json`.

## Conductor review recheck — native official reviewed-row replay — 2026-09-22

### Summary

One explicitly reviewed Queensland opportunity was replayed through the same
canonical Grants flow used by G07. The real canonical key was created and read
back, then the exact item was removed and the flow restored Off.

### Verification checks

- [x] Run `08584115872127113780695944024CU04` succeeded for
  `metro-south-innovate-grants-2027`.
- [x] SharePoint readback returned exactly one item, ID 8, for the key.
- [x] Exact cleanup returned HTTP 200; final readback was an empty Atom feed.
- [x] Final canonical flow status was Off.
- [ ] Duplicate/concurrency, unattended monitoring/delivery, recurrence and
  production acceptance.

### Findings

The bounded reviewed-row execution path is now natively evidenced alongside
malformed-input failure safety and exact-key create/update behaviour. G07
remains active because the outstanding operational gates are broader than a
single manual replay.

Receipt:
`private/ops/2026-09-22-powerautomate-g02-g04-metro-south-reviewed-row.json`.
