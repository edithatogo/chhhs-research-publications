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
- [x] Task: Reject non-string calendar opportunity identities, URLs and display fields without coercion (e03f17d).
- [x] Task: Reject non-string funder identities, including boolean false, before subscription matching (`cfc57b4`).
- [x] Task: Reject duplicate holiday dates during institutional-date projection (`d7019e0`).
- [x] Task: Require typed policy identity/version and effective-date fields before validation (`09adbe2`).

## Phase: Calendar omission-boundary review — 2026-09-21

- [x] Task: Validate optional calendar display fields before omitting uncertain
  dates, so malformed typed data cannot disappear silently (`29d97cf`).
- [ ] Native pages, personal access, calendar change ledger and delivery remain
  open; local omission semantics do not certify tenant acceptance.

## Phase: Exact-date validation review — 2026-09-21

- [x] Task: Reject impossible ISO dates when a grant deadline is explicitly
  marked day-precision (`01231b6`).
- [ ] Native pages, personal access, calendar change ledger and delivery remain
  open.

## Phase: Holiday collection boundary review — 2026-09-21

- [x] Task: Reject malformed holiday collections explicitly in institutional
  deadline projection (`6ca91b0`).
- [ ] Native policy persistence, calendar delivery and notification acceptance
  remain open.

## Phase: Subscription container boundary review — 2026-09-21

- [x] Task: Reject malformed subscription containers before rule iteration
  (`a0c8d06`).
- [ ] Native preference persistence, access isolation and delivery remain open.
