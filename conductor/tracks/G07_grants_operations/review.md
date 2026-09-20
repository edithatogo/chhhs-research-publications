# G07 review

## Summary

Review status: in progress; local operational guardrails are implemented.

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
- [x] **Test Results**: Passed - focused G07 tests (13), project validation (438 checks) and canonical-clone full suite (373 tests, 8 skipped).

## Findings

### Medium - native operational acceptance remains open

- **File**: `conductor/tracks/G07_grants_operations/plan.md`
- **Context**: Controlled synthetic create/update runs do not prove monitoring, two successive complete live cycles, exact-key reconciliation, schedule or delivery acceptance.
- **Suggestion**: Keep G07 active until those native operational receipts are captured against an approved target; do not archive based on local evaluation or isolated DEV replay alone.

## Conductor review — identity fail-closed hardening — 2026-09-21

- **Finding:** `evaluate_run` string-coerced malformed source identities and could raise on an unhashable `OpportunityKey`, weakening the operational quarantine boundary.
- **Fix:** non-string source and opportunity identities are now rejected explicitly; duplicate checks only run over validated string keys. Regression coverage proves the malformed batch is rejected without coercion or an incidental exception.
- **Verification:** commit `42833c6` passes the focused relationship/operations suite (13 tests), the full local suite (373 tests, 8 skips), project validation (438 checks), web-first contracts and Conductor validation. Remote source-only CI remains to be recorded against the synchronized documentation commit.
- **Residual gate:** native monitoring, exact-key reconciliation, scheduling and delivery remain open.

## Conductor review — malformed run-object hardening — 2026-09-21

- **Finding:** `evaluate_run` assumed every record and health row was a mapping, so malformed batches could raise an incidental attribute error instead of entering the rejected-run path.
- **Fix:** commit `c174a3a` explicitly classifies non-object record and health rows as invalid, evaluates safe placeholders, and preserves the prior accepted batch.
- **Verification:** the focused relationship/operations suite passes (16 tests); full local and native operational gates remain as documented above.

## Conductor review — exact registry reconciliation — 2026-09-21

- **Finding:** the local evaluator checked source health counts but had no exact-key comparison between an emitted cycle and the subsequent registry readback.
- **Fix:** commit `994dc05` adds `reconcile_registry_keys`, which rejects malformed/duplicate keys, reports missing or unexpected registry identities, and preserves the prior accepted batch on mismatch.
- **Verification:** focused relationship/operations tests pass (18); full local suite passes (373 tests, 8 skips). This is a local reconciliation contract; native list readback, monitoring and scheduling remain open.
