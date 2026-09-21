# Implementation plan

**Access scope:** the existing user's isolated RIMS/Power Platform route and
personal watchlist only. Shared subscriptions, cross-user notifications and
unattended delivery are future extensions.

- [x] Record scope and acceptance requirements.
- [x] Inspect current inputs, dependencies and relevant platform objects. Existing RIMS page design, planning helper and subscription scopes were inspected; native page inventory remains open.
- [x] Review fix: escape carriage returns as well as line feeds in calendar display fields (`a573598`).
- [x] Apply review fix: reject non-string opportunity/category/funder identities and malformed subscription rule objects before watchlist matching (`53d2419`).
- [x] Implement: Add local versioned policy validation and stable delivery-event idempotency keys for the future list-backed pages.
- [~] Verify: Local policy/subscription tests pass. On 2026-09-21 the authenticated personal DEV SharePoint route created exactly one `My Funding Watchlist` list and exactly one `Funding Calendar` list after inventory confirmed neither existed. Read-only REST readback confirms the watchlist fields (`OpportunityKey` required/unique, `Scope`, `TargetKey`, `Active` default false) and calendar fields (`DeadlineKey` required/unique, `OpportunityKey`, `CalculatedDate`, `SourceURL`, `Cancelled` default false, `PolicyKey`, `ReviewStatus` default `Needs Review`); both lists read `ItemCount=0`. A synthetic calendar item was created/read back with date, source URL, policy and review fields, its policy key was edited/read back, and it was deleted; the calendar returned to zero rows. Reminder ledger, calendar change/cancellation execution, native report pages and delivery remain open.
- [x] Record local and live evidence separately before closure; no report page, subscription, notification or calendar was created.
- [x] Harden future delivery idempotency keys to reject coercible identities and out-of-range offsets without creating ambiguous keys.
- [x] Make institutional policy and holiday validation reject non-object and non-string inputs without incidental type errors.
- [x] Review fix: require an explicit current-user key and return only that user's matching subscription (`a6e1602`, `db96224`).
- [x] Review fix: bind delivery-event idempotency keys to the explicit current user (`0b5c920`).

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

## Phase: Native current-user list bootstrap — 2026-09-21

- [x] Task: Inventory the personal DEV site and create the sole `My Funding Watchlist` and `Funding Calendar` lists only when absent; persist the minimal user-scoped schemas with inactive/cancelled defaults and read back the fields through the authenticated SharePoint API.
- [ ] Task: Add the current-user flow/page binding, calendar revision ledger and controlled readback; do not enable cross-user delivery or unattended notifications.

### Native persistence evidence — 2026-09-21

- [x] Controlled current-user calendar round-trip: created one synthetic deadline with an exact calculated date, authoritative HTTPS source URL, policy key and `Needs Review` state; read back all visible fields; edited the policy key and read it back; deleted the synthetic item and confirmed the list returned to zero rows.
- [ ] Native page/report binding, revision ledger, reminder/change execution and delivery remain open.

The authenticated Power Automate designer was also checked for the next
current-user flow. It can expose the personal site as a custom SharePoint
address and resolve the `Funding Calendar` fields, but the manual-trigger
dynamic-content binding did not resolve reliably in the new designer. The
incomplete draft was discarded; no duplicate flow, invalid flow, schedule or
notification was saved.
