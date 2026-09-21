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
- [x] Review fix: constrain the watchlist `Scope` choice to `opportunity`,
  `category` or `funder`, preventing an untyped native subscription target
  (`6e1b43a`).

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

### Native watchlist-flow bootstrap boundary — 2026-09-21

The existing reviewed-grants flow was cloned temporarily as a bootstrap
candidate for `My Funding Watchlist`. The designer resolved the personal
SharePoint list and its `OpportunityKey`, `Scope`, `TargetKey` and `Active`
fields, but the cloned trigger/parser still accepted the grants-opportunity
payload and could not supply a dedicated subscription scope/target contract.
The incomplete copy was discarded. The live flow inventory was read back at
three flows: the canonical publications flow, the reviewed grants flow and the
reviewed DoRA flow. No temporary watchlist flow remains. A dedicated local
watchlist input contract is required before another native copy is created.

- [x] Add the dedicated `funding-watchlist-v1` local schema and regression
  coverage for the current-user personal list. Native flow binding remains
  open until the trigger/parser uses this contract directly.
### Native dedicated watchlist flow — 2026-09-21

- [x] Add and validate a dedicated SharePoint-only `funding-watchlist-v1` manual upsert contract and target-injected package locally.
- [x] Import exactly one `CHHHS RIMS - Funding Watchlist - Reviewed Upsert` flow into the authenticated current-user DEV context; Flow Checker read 0 errors.
- [x] Run controlled synthetic create and same-key update cases. SharePoint readback showed the expected opportunity-to-category scope/target and Active changes; the flow was restored Off.
- [ ] Delete the remaining synthetic watchlist row through the SharePoint UI and confirm zero rows; native report/page binding, calendar ledger and delivery remain open.

### Native dedicated calendar flow — 2026-09-21

- [x] Add and validate a dedicated `funding-calendar-v1` SharePoint-only manual upsert contract and target-injected package locally.
- [x] Import exactly one current-user DEV flow: `CHHHS RIMS - Funding Calendar - Reviewed Upsert`, flow ID `f18e3fad-7ee5-47d7-b166-d9bb41f93a3e`, using the existing SharePoint connection and the personal `Funding Calendar` list.
- [x] Native Flow Checker readback: 0 errors and 0 warnings while enabled; the only inactive-flow warning appeared after the flow was restored Off.
- [x] Controlled native create run `08584116266950718806813049204CU16` succeeded; SharePoint readback showed `synthetic-calendar-20260921`, `2026-10-15`, the authoritative source URL, `Cancelled=No`, the initial policy key and `Needs Review`.
- [x] Controlled same-key update run `08584116266295302685959687164CU15` succeeded; SharePoint readback showed `2026-10-20`, `Cancelled=Yes`, policy key `synthetic-policy-20260921-v2` and `Confirmed` without creating a duplicate.
- [x] Restore the isolated flow Off. Do not delete the synthetic calendar row without explicit UI deletion confirmation; it remains visible as native replay evidence.
- [ ] Native report/page binding, institutional-date and reminder/change ledger, subscription isolation and calendar/notification delivery remain open.

### Native delivery-ledger flow — 2026-09-21

- [x] Add and validate the SharePoint-only `funding-delivery-ledger-v1` schema, flow definition and package builder locally; optional date/error fields are null-safe.
- [x] Create exactly one personal DEV `Funding Delivery Ledger` list. Native field readback confirms the twelve visible ledger fields, `Status` default `Pending`, versioning enabled with a 50-major-version limit, and zero rows before testing.
- [x] Import exactly one `CHHHS RIMS - Funding Delivery Ledger - Reviewed Upsert` flow and update that same flow in place after the first controlled run exposed an empty optional `SentAt` conversion defect. Flow Checker read 0 errors and 0 warnings after the null-safe repair.
- [x] Controlled native create run `08584116256446744665855863737CU13` exposed the expected optional-date defect; no row was written by that failed run. The corrected same-key run `08584116253756053128213151733CU27` succeeded after the update package was imported. SharePoint readback showed one row with `Revision=v2`, `Channel=email`, `Status=Sent`, `ScheduledFor=2026-10-02` and `SentAt=2026-09-21`; the flow was restored Off.
- [ ] Ledger cleanup, native report/page binding, true subscription isolation and actual calendar/reminder delivery remain open. The synthetic ledger row remains as controlled evidence pending explicit UI deletion confirmation.

### Native report page shells and model binding — 2026-09-21

- [x] In the existing current-user My workspace report, add and save `Funding Opportunities` and `Funding Calendar & Watchlist` pages through the Power BI web editor; switch back to Reading view and read back both page names and their scope/status text.
- [x] In the existing current-user My workspace semantic model, use the Power Query SharePoint Online List connector and the existing organisational-account connection to add read-only native queries for `My Funding Watchlist`, `Funding Calendar`, `Funding Delivery Ledger` and `Grants Registry`. Model readback now shows tables 22–25 with 26, 29, 32 and 44 columns respectively; the Grants Registry preview evaluated with zero rows and the other three previews evaluated with one controlled synthetic row each.
- [x] Add and save a native table visual on `Funding Opportunities` bound to `Grants Registry.Funder`, `Deadline`, `Eligibility` and `OpportunityKey`; Reading-view readback shows those headers. The native Grants Registry preview currently has zero rows, so no opportunity row is claimed.
- [x] Add and save native table visuals on `Funding Calendar & Watchlist`: the calendar visual is bound to `Funding Calendar.CalculatedDate`, `DeadlineKey`, `ReviewStatus` and `SourceURL`, and the watchlist visual is bound to `My Funding Watchlist.Active`, `OpportunityKey`, `Scope` and `TargetKey`. Reading-view readback shows all eight headers, the synthetic calendar row and the synthetic watchlist row.
- [ ] Refresh/row reconciliation and current-user flow/page binding remain separate gates. The page status text still contains the older phrase that semantic-model binding is pending; this is a cosmetic documentation gap, not evidence that the native bindings are absent.
- [ ] Add current-user flow/page binding, subscription isolation, calendar revision ledger and actual reminder/change delivery after the semantic-model route is available.
