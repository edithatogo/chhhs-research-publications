# Implementation plan

- [x] Record scope and acceptance requirements.
- [x] Inspect current inputs, dependencies and relevant platform objects. Reused the canonical normalizer and kept SharePoint/native objects out of the local adapter.
- [x] Implement: Implement independently testable adapters and one canonical ingestion workflow.
- [x] Verify: XML/API-shaped fixtures, malformed/incomplete batches, changed deadlines, archived rounds and failed-source isolation are covered locally; live source cycles remain open.
- [x] Record local and live evidence separately before closure; no unattended flow or schedule was activated.

## Review fixes — 2026-09-20

- [x] Task: Apply review suggestion: hash the complete source row and reject duplicate calendar identities before candidate emission (03733b8).
