# Implementation plan

**Access scope:** current-user local adapters and manual isolated source-to-list
validation only. Shared ingestion and unattended recurrence are future
extensions.

- [x] Record scope and acceptance requirements.
- [x] Inspect current inputs, dependencies and relevant platform objects. Reused the canonical normalizer and kept SharePoint/native objects out of the local adapter.
- [x] Implement: Implement independently testable adapters and one canonical ingestion workflow.
- [x] Verify: XML/API-shaped fixtures, malformed/incomplete batches, changed deadlines, archived rounds and failed-source isolation are covered locally; live source cycles remain open.
- [x] Record local and live evidence separately before closure; no unattended flow or schedule was activated.

## Native reviewed-import cycle — 2026-09-22

- [x] Execute one official Queensland HTML opportunity through the existing
  reviewed-import route, preserving the source and row URLs, raw deadline
  window, eligibility wording and evidence hash.
- [x] Read back the exact `OpportunityKey` from SharePoint after the successful
  run, then delete the exact row and confirm the empty list. Receipt:
  `private/ops/2026-09-22-powerautomate-g02-g04-metro-south-reviewed-row.json`.
- [~] RSS/Atom/API promotion, source change/archive reconciliation, recurrence,
  monitoring and unattended operation remain open.

## Review fixes — 2026-09-20

- [x] Task: Apply review suggestion: hash the complete source row and reject duplicate calendar identities before candidate emission (03733b8).
- [x] Task: Apply review suggestion: suppress repeated calendar headers before candidate emission (f16c297).
- [x] Task: Apply review suggestion: reject duplicate non-empty RSS/Atom source identities before emission (7cd7e47).
- [x] Task: Reject RSS/Atom entries without a required title before registry emission (697cdcd).
- [x] Task: Reject RSS/Atom entries without a source identifier or URL before registry emission (5cb8aab).
- [x] Task: Apply the same title, URL, key and timezone contract to API-shaped records before batch acceptance (c25b03e).
- [x] Task: Reject duplicate normalized `OpportunityKey` values within a single RSS/Atom or API source batch (8817e21).
- [x] Task: Reject malformed non-object source batches explicitly before source-health processing (`9d09f30`).
- [x] Task: Reject non-string source identities, URLs and opportunity keys without coercion before ingestion admission.
- [x] Task: Validate API-shaped source fields before normalization so booleans/numbers cannot be stringified into accepted records (`5fa0467`).
- [x] Task: Add a shared typed-input boundary to the canonical grants normalizer (`f6e33e4`).
- [x] Task: Reject structured and boolean `Amount` values while preserving scalar numeric amounts (`b10810d`).

## Conductor review fix — 2026-09-22

- [x] Task: Reject surrounding whitespace in feed and batch source identities instead of silently normalising distinct source IDs (`d728a32`).
- [x] Verification: focused ingestion tests (24), full local suite (448 tests, 8 skipped), project checks (460), web-first contracts, Conductor validation and diff validation pass locally.
- [~] Native feed permissions, source-change/archive reconciliation, recurrence, monitoring and unattended operation remain open; local success is not tenant acceptance.
