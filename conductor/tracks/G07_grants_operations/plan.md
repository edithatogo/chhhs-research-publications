# Implementation plan

- [x] Record scope and acceptance requirements.
- [x] Inspect current inputs, dependencies and relevant platform objects. Reused G04 source health and G01 stable keys; no operational tenant object was changed.
- [x] Implement: Add a local fail-closed run evaluator for empty/duplicate/key-missing/failed-source batches and last-accepted preservation.
- [~] Verify: Local controlled-failure checks pass; one controlled native synthetic create and one same-key update are now evidenced with the flow restored Off. Native monitoring, concurrency, exact-key operational reconciliation and delivery/scheduling remain open.
- [x] Record local and live evidence separately before closure.

## Phase: Review fixes
- [x] Task: Apply review corrections for the controlled native replay and preserve the remaining acceptance boundary (0536b98).
- [x] Task: Reject runs without source health or with records from unreported sources (aad9d4a).
- [x] Task: Reject incomplete or duplicate source-health rows and records without source identity (2165c70).
- [x] Task: Reconcile non-negative per-source health counts to admitted record counts and reject mismatches (91345bf).
