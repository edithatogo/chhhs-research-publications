# G07 review

Review status: in progress; local operational guardrails are implemented.

`scripts/grants_operations.py` rejects empty batches, missing or duplicate opportunity keys, and any failed source. On rejection it returns the prior accepted records instead of replacing them. Tests cover source failure preservation. Native monitoring, concurrency and schedule/delivery evidence remains open. A controlled authenticated Power Automate replay now proves one synthetic create and one same-key update, with the flow restored Off; see the G03 review and the ignored receipt `private/ops/2026-09-20-grants-flow-import-readback.json`. No unattended schedule, notification or production path was touched.

Review fix applied: `evaluate_run` now rejects missing source health and
records whose source is not represented in the health results. Focused tests
cover both boundaries; prior accepted records remain preserved on rejection.

## Verification Checks

- [x] **Plan Compliance**: Partial - local fail-closed evaluation and controlled DEV replay evidence exist; monitoring, operational reconciliation, delivery and scheduling remain open.
- [x] **Style Compliance**: Pass - the evaluator preserves prior accepted records and fails closed on missing evidence.
- [x] **New Tests**: Yes - missing health and unreported-source cases are covered.
- [x] **Test Coverage**: Partial - local run evaluation is covered; native monitoring and unattended delivery are not.
- [x] **Test Results**: Passed - focused G07 tests (7) and project validation (438 checks); full-suite rerun required after the review fix.

## Findings

### Medium - native operational acceptance remains open

- **File**: `conductor/tracks/G07_grants_operations/plan.md`
- **Context**: Controlled synthetic create/update runs do not prove monitoring, two successive complete live cycles, exact-key reconciliation, schedule or delivery acceptance.
- **Suggestion**: Keep G07 active until those native operational receipts are captured against an approved target; do not archive based on local evaluation or isolated DEV replay alone.
