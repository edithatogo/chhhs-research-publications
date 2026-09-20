# Implementation plan

- [x] Record scope and acceptance requirements.
- [x] Inspect current inputs, dependencies and relevant platform objects. Existing RIMS page design, planning helper and subscription scopes were inspected; native page inventory remains open.
- [x] Apply review fix: reject non-string opportunity/category/funder identities and malformed subscription rule objects before watchlist matching (`53d2419`).
- [x] Implement: Add local versioned policy validation and stable delivery-event idempotency keys for the future list-backed pages.
- [~] Verify: Local policy/subscription tests pass; native page persistence, per-user access, reminder ledger and calendar change/cancellation remain open.
- [x] Record local and live evidence separately before closure; no report page, subscription, notification or calendar was created.
- [x] Harden future delivery idempotency keys to reject coercible identities and out-of-range offsets without creating ambiguous keys.
- [x] Make institutional policy and holiday validation reject non-object and non-string inputs without incidental type errors.

## Local review extension — 2026-09-20

- [x] Add deterministic iCalendar projection with versioned institutional dates, stable event IDs, tentative review state and explicit cancellation semantics; cover unknown/partial dates and duplicate-safe revisions with tests (f8d0262).

## Phase: Review fixes

- [x] Task: Reject duplicate projected calendar event UIDs before iCalendar emission (ecf3d43).
- [x] Task: Reject reversed policy ranges, malformed holiday dates and duplicate holidays (efd3abd).
- [x] Task: Require an authoritative HTTP(S) URL and stable opportunity key for exact-date calendar events (ba4f5b4).
- [x] Task: Reject malformed subscription rules and missing opportunity identity before candidate matching (b45b4e1).
