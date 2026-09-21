# Implementation plan

**Access scope:** current-user manual operation against isolated DEV data; no
cross-user monitoring, delivery or unattended schedule is part of this tranche.

- [x] Record scope and acceptance requirements.
- [x] Inspect current inputs, dependencies and relevant platform objects. Reused G04 source health and G01 stable keys; no operational tenant object was changed.
- [x] Implement: Add a local fail-closed run evaluator for empty/duplicate/key-missing/failed-source batches and last-accepted preservation.
- [~] Verify: Local controlled-failure checks pass; one controlled native synthetic create and one same-key update are now evidenced with the flow restored Off. Current-user manual monitoring, concurrency and exact-key operational reconciliation remain open; cross-user delivery and unattended scheduling are future extensions.
- [x] Review fix: reject whitespace-divergent source and opportunity identity values before operational acceptance (`1ac3d52`).
- [x] Record local and live evidence separately before closure.

## Phase: Review fixes
- [x] Task: Apply review corrections for the controlled native replay and preserve the remaining acceptance boundary (0536b98).
- [x] Task: Reject runs without source health or with records from unreported sources (aad9d4a).
- [x] Task: Reject incomplete or duplicate source-health rows and records without source identity (2165c70).
- [x] Task: Reconcile non-negative per-source health counts to admitted record counts and reject mismatches (91345bf).
- [x] Task: Reject non-string source and opportunity identities without coercion, including unhashable malformed keys.
- [x] Task: Reject non-object run records and health rows without incidental exceptions (c174a3a).
- [x] Task: Add exact emitted-to-registry key-set reconciliation with fail-closed preservation (994dc05).
- [x] Task: Add selected-field registry readback reconciliation with fail-closed prior-batch preservation (`1b0c91b`).
- [x] Task: Reject string-shaped reconciliation field allowlists and canonicalize whitespace before comparison (`0eef31a`).
