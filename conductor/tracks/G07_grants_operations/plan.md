# Implementation plan

- [x] Record scope and acceptance requirements.
- [x] Inspect current inputs, dependencies and relevant platform objects. Reused G04 source health and G01 stable keys; no operational tenant object was changed.
- [x] Implement: Add a local fail-closed run evaluator for empty/duplicate/key-missing/failed-source batches and last-accepted preservation.
- [~] Verify: Local controlled-failure checks pass; two native cycles, concurrency and exact-key readback remain open. Delivery/scheduling remain separately gated.
- [x] Record local and live evidence separately before closure.
