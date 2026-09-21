# G08 review

## Conductor review — calendar change identity boundary — 2026-09-22

- **Finding:** calendar-change projection stripped `DeadlineKey`, `OpportunityKey`, `ReviewStatus` and `SourceURL` values before emitting revision records, allowing malformed padded identities/URLs to appear canonical.
- **Fix:** required strings and source URLs now reject surrounding whitespace; regression coverage was added.
- **Verification:** focused calendar-change tests pass (4); the full suite passes 453 tests with 8 skips; project checks pass 460; web-first, Conductor and diff validation pass locally.
- **Residual gate:** native null-date branch/import/readback, model refresh/reconciliation, recurrence and delivery remain open.

## Conductor review — subscription identity isolation — 2026-09-22

- **Finding:** subscription and delivery matching stripped current-user,
  opportunity, target and event identity values before comparing or hashing
  them. A malformed identity with surrounding whitespace could therefore
  collapse into another user's or another target's canonical key.
- **Fix:** shared identity validation now requires non-empty strings with no
  surrounding whitespace across subscription matching and delivery-event key
  generation. Regression coverage covers padded current-user, opportunity and
  subscription identities and delivery keys.
- **Verification:** focused planning/operations tests pass (35); the full
  suite passes 452 tests with 8 skips; project validation passes 460 checks;
  web-first, Conductor and diff validation pass locally.
- **Residual gate:** native preference persistence, access isolation,
  calendar revision execution, refresh/reconciliation and delivery remain
  open.

## Summary

Review status: in progress; local planning and idempotency contracts are implemented.

## Synchronized verification — 2026-09-22

The canonical checkout passes 450 tests (8 skipped), 460 project checks,
Conductor validation and source-only CI run `35657921400`. This updates the
local evidence baseline only. The QLD Health null-date repair was not saved:
the authenticated browser session was lost before Flow Checker/readback or
replay, the canonical flow remains Off, and VUW PAC exposed no cloud-flow
export. Native refresh/reconciliation, calendar revision delivery and
notification acceptance remain open.

- `validate_policy` requires a version, organisation, anchor, lead time, holiday-calendar version and effective dates.
- `delivery_event_key` gives future notifications a stable deduplication key; it does not send messages or create calendar events.
- Existing subscription matching remains candidate generation only and does not authorize delivery.
- The current-user delivery ledger is now represented by a versioned personal SharePoint list and a SharePoint-only upsert flow. The first native run correctly exposed that empty optional `SentAt` was being submitted as an empty string; the tracked definition now uses null-safe expressions and the flow was updated in place rather than duplicated.
- Added `scripts/grants_calendar.py` as a local iCalendar projection contract.
  It derives institutional all-day dates from exact source deadlines and a
  versioned policy, preserves the external deadline, emits stable event IDs,
  marks unreviewed events `TENTATIVE`, and represents cancellations explicitly.
  Unknown or partial deadlines are omitted; no calendar or notification is
  created.

## Local report/model surface — 2026-09-20

- Added an empty-safe `GrantsRegistry` semantic-model table using the existing
  SharePoint read definition, with stable opportunity/deadline/review fields
  and explicit measures for total, open and needs-review opportunities.
- Added three additive pages to the existing PBIP: `FundingOpportunities`,
  `FundingCalendar` and `MyFundingWatchlist`. The calendar preserves raw
  deadline text and precision; the watchlist is explicitly a report preview,
  not a personal subscription or notification service.
- Expanded the local dashboard contract to seven pages and added model-binding,
  geometry and page-order tests. This is a source/report definition change,
  not native Power BI page authoring or readback.

Native funding pages, SharePoint list persistence, authenticated preference
isolation, calendar update/cancellation and notification delivery remain open.

## Native delivery-ledger review — 2026-09-21

### Summary

The personal DEV `Funding Delivery Ledger` list and its canonical upsert flow
are now natively bootstrapped and tested in the current-user scope. The list
contains the identity, user/opportunity, event, revision, offset, channel,
status, schedule/send and error fields; `Status` defaults to `Pending` and
list versioning is enabled. The flow uses serial SharePoint lookup/create/update
with a duplicate diagnostic and is restored Off after testing.

### Verification Checks

- [x] **Plan Compliance:** Partial — native ledger persistence and a controlled update are proven; delivery, subscriptions, report pages and unattended operation remain open.
- [x] **Flow Safety:** Pass — SharePoint-only definition, single-write concurrency, zero/exactly-one guards and no OneDrive dependency are locally validated.
- [x] **Native Flow Checker:** Pass — 0 errors and 0 warnings after the null-safe optional-date repair.
- [x] **Native Replay:** Partial — first run `08584116256446744665855863737CU13` failed at the expected empty optional `SentAt` conversion boundary; update package was imported in place and corrected run `08584116253756053128213151733CU27` succeeded. SharePoint readback showed the updated same-key row without a duplicate.
- [x] **Isolation:** Pass — personal DEV list/flow only; flow restored Off and no notification, sharing or schedule was enabled.

### Findings

- **Fixed:** empty optional `SentAt`/`ErrorMessage` values were sent as empty strings, which SharePoint date conversion rejected. The tracked flow now passes null for empty optional values and the corrected package was imported as an Update to the existing flow identity.
- **Residual acceptance:** the synthetic ledger row was subsequently deleted through the authenticated SharePoint UI and the list read back with zero data rows. Native report binding is evidenced for the saved visuals, while refresh/reconciliation, subscription isolation, calendar delivery and unattended operation remain unproven.

## Native boundary readback — 2026-09-20

Authenticated Power BI read-only readback still shows four native pages:
CHHHS Publications, Monthly Publications, Source Reconciliation and Clinical
Analytics. No native funding page is present. Receipt:
ignored `private/ops/2026-09-20-powerbi-report-page-inventory.json`.
The local seven-page definition therefore remains a candidate for an isolated
authoring route, not a tenant deployment claim.

Review fix applied: the iCalendar projection now rejects duplicate event UIDs
before emission, preventing duplicate opportunity inputs from generating an
ambiguous calendar artifact. A focused regression test covers this boundary.

Additional review fix applied: versioned institutional policies now reject
reversed effective ranges, malformed holiday dates and duplicate holiday dates
before date projection. Unknown source dates remain omitted.

Review fix applied: exact-date calendar events now fail closed unless the
opportunity has a stable `OpportunityKey` and authoritative HTTP(S) URL.

Additional review fix applied in `b45b4e1`: subscription matching now fails
closed for missing opportunity identity, unsupported scopes, blank user/target
keys and non-boolean `Active` values instead of silently dropping malformed
rules. This protects the future personal watchlist from unreported
subscription loss; it does not authorize or send delivery.

Additional review fix applied in `53d2419`: subscription and opportunity
identities must be strings, category/funder keys are not coerced from other
types, and non-object subscription rules fail closed explicitly. This prevents
malformed watchlist inputs from matching by string coercion.

Additional review fix applied in `e03f17d`: calendar opportunities, URLs,
titles, sources, statuses and deadline precision now require the expected
types; malformed values fail closed without string coercion. Partial or
unknown deadlines are still omitted before event identity is evaluated.

## Verification Checks

- [x] **Plan Compliance**: Partial - local date-policy, subscription and calendar contracts are implemented; native pages, access isolation, reminders and delivery remain open.
- [x] **Style Compliance**: Pass - uncertain dates remain omitted and event identity is deterministic.
- [x] **New Tests**: Yes - duplicate UID, malformed policy, missing-key, invalid-URL and calendar input-type rejection are covered.
- [x] **Test Coverage**: Partial - local calendar semantics are covered; native report persistence, personal access and delivery are not.
- [x] **Test Results**: Passed - focused calendar tests (6), planning/relationship tests (14), project validation (438 checks) and canonical-clone full suite (374 tests, 8 skipped).

## Findings

### Medium - native RIMS experience remains unproven

- **File**: `conductor/tracks/G08_rims_grants_experience/plan.md`
- **Context**: The local seven-page PBIP and iCalendar contract do not prove native funding pages, authenticated subscription persistence, reminder ledger, calendar update/cancellation or notification delivery.
- **Suggestion**: Keep G08 active until an approved isolated authoring route and native readback prove those behaviours; do not archive from local artefacts alone.

## Conductor review — subscription identity hardening — 2026-09-21

- **Verification:** focused planning tests passed (11); full suite passed (374 tests, 8 skipped); project validation passed (438 checks); web-first contracts passed locally.
- **Finding/fix:** `subscribers` previously string-coerced opportunity, category and funder keys and leaked an incidental exception for non-object rules. Commit `53d2419eccb664e9a61043096d8e208bea8ed7f1` requires string identities and explicit object validation.
- **Residual gate:** native funding pages, preference isolation, calendar update/cancellation and notification delivery remain open.

## Conductor review — delivery-key hardening — 2026-09-21

- **Finding:** the local delivery-event key helper string-coerced arbitrary values, allowing malformed or empty identity fields to enter a future delivery ledger.
- **Fix:** identity fields now require non-empty strings and reminder offsets require bounded integers; regression tests cover coercible values, booleans and out-of-range offsets.
- **Verification:** commit `b84cae8` and policy hardening commit `1a5fed0` pass the focused planning/relationship suite (25 tests combined), the full local suite (374 tests, 8 skips), project validation (438 checks), web-first contracts and Conductor validation; native delivery remains unproven.
- **Residual gate:** native page persistence, per-user access, calendar change/cancellation and notification delivery remain open.

## Conductor review — policy input hardening — 2026-09-21

- **Finding:** institutional policy validation assumed a mapping and coerced holiday values before parsing; malformed input could therefore escape the intended false/explicit-error boundary.
- **Fix:** policy validation now rejects non-object and non-string holiday inputs, while date projection raises an explicit validation error for malformed holiday collections.
- **Verification:** regression tests cover non-object policies and non-string/invalid holidays; native policy persistence and delivery remain unproven.

## Conductor review — calendar input hardening — 2026-09-21

- **Finding:** the local calendar projection previously string-coerced opportunity identities, URLs and display fields; malformed values could therefore enter a future calendar artifact.
- **Fix:** commit `e03f17d` requires typed calendar inputs and preserves omission of uncertain dates.
- **Verification:** focused calendar suite passes (6 tests); the full local suite remains 374 tests with 8 skips, with native page persistence, calendar update/cancellation and delivery still open.

## Conductor review — calendar omission boundary — 2026-09-21

### Summary

The calendar projection now validates optional descriptive field types before
omitting an opportunity with an uncertain or partial deadline. Unknown dates
remain intentionally excluded from event output, but malformed typed metadata
cannot be hidden by that omission path. Code commit: `29d97cf82f956e1ff0ae35c1b74834c653996207`.

### Verification Checks

- **Plan Compliance:** Partial — local calendar safeguards are implemented;
  native pages, private access and delivery remain open.
- **Style Compliance:** Pass.
- **New Tests:** Yes — malformed display fields with uncertain dates are
  rejected explicitly.
- **Test Coverage:** Partial — local calendar semantics are covered; native
  persistence and delivery are not.
- **Test Results:** Passed — focused calendar suite (7 tests), full suite (396
  passed, 8 skipped), 438 project checks, Conductor validation, web-first and
  Power Platform checks.

### Findings

- **Fixed:** malformed `Title`, `Source` or `Status` values could be silently
  omitted when deadline precision was not an exact day.
- **Residual acceptance:** native funding pages, subscription persistence,
  calendar change/cancellation and notification delivery remain unproven.

## Conductor review — exact-date validation — 2026-09-21

### Summary

The calendar projection now rejects impossible dates when a source row declares
day precision, instead of allowing an invalid date to reach institutional-date
calculation or failing later during iCalendar rendering. Code commit:
`01231b6e9d3532f10cf5b4f1e182a6dd22ac1cf6`.

### Verification Checks

- **Plan Compliance:** Partial — local exact-date validation is implemented;
  native pages and delivery remain open.
- **Style Compliance:** Pass.
- **New Tests:** Yes — impossible ISO date regression covered.
- **Test Coverage:** Partial — local calendar semantics are covered; native
  persistence and delivery are not.
- **Test Results:** Passed — focused calendar suite (8 tests), full suite (397
  passed, 8 skipped), 438 project checks, Conductor validation, web-first and
  Power Platform checks.

### Findings

- **Fixed:** an impossible day-precision date was not rejected at the calendar
  boundary.
- **Residual acceptance:** native funding pages, subscriptions, calendar
  change/cancellation and notification delivery remain unproven.

## Conductor review — holiday collection boundary — 2026-09-21

### Summary

Institutional deadline projection now rejects malformed holiday collections as
an explicit policy error instead of leaking a raw type exception for values such
as `None` or a mapping. Code commit: `6ca91b0c1983d157b86821aefe995efbbfdf7762`.

### Verification Checks

- **Plan Compliance:** Partial — local policy validation is implemented; native
  policy persistence and delivery remain open.
- **Style Compliance:** Pass.
- **New Tests:** Yes — malformed collection shapes are covered.
- **Test Coverage:** Partial — local planning/calendar semantics are covered;
  native persistence and delivery are not.
- **Test Results:** Passed — focused planning suite (12 tests), full suite (397
  passed, 8 skipped), 438 project checks, Conductor validation, web-first and
  Power Platform checks.

### Findings

- **Fixed:** malformed holiday collection shapes could escape the explicit
  `ValueError` contract.
- **Residual acceptance:** native policy persistence, funding pages,
  calendar delivery and notifications remain unproven.

## Conductor review — subscription container boundary — 2026-09-21

### Summary

Subscription matching now rejects malformed top-level subscription containers
before iteration, producing the explicit contract error for `None`, scalar or
otherwise unsupported shapes. Code commit:
`a0c8d0636e99a7bc23d789671e75a73e04365ae2`.

### Verification Checks

- **Plan Compliance:** Partial — local watchlist validation is implemented;
  native preference persistence and delivery remain open.
- **Style Compliance:** Pass.
- **New Tests:** Yes — malformed container shapes are covered.
- **Test Coverage:** Partial — local planning semantics are covered; native
  access and delivery are not.
- **Test Results:** Passed — focused planning suite (12 tests), full suite (397
  passed, 8 skipped), 438 project checks, Conductor validation, web-first and
  Power Platform checks.

### Findings

- **Fixed:** malformed subscription containers could leak a raw iteration error.
- **Residual acceptance:** native preferences, per-user access, calendar
  delivery and notifications remain unproven.

## Conductor review — funder identity hardening — 2026-09-21

- **Finding:** a false-valued `FunderKey` could be treated as absent because the matcher tested truthiness before type validation.
- **Fix:** commit `cfc57b4` requires `FunderKey` to be a string whenever supplied, including boolean values; the planning regression suite covers the boundary.
- **Verification:** focused planning tests pass (11); the full suite passes 384 tests with 8 skips; project validation passes 438 checks; web-first, Conductor, Power Platform tooling and visual standards checks pass locally.
- **Residual gate:** native funding pages, preference isolation, calendar change/cancellation and notification delivery remain open.

## Conductor review — duplicate holiday projection — 2026-09-21

- **Finding:** `institutional_deadline` silently collapsed duplicate holiday dates even though the versioned policy contract rejects them.
- **Fix:** commit `d7019e0` parses and validates holiday dates for uniqueness before date projection; regression coverage now rejects duplicate dates.
- **Verification:** focused planning tests pass (11); the full suite passes 384 tests with 8 skips; project validation passes 438 checks; web-first, Conductor, Power Platform tooling and visual standards checks pass locally.
- **Residual gate:** native policy persistence, funding pages, calendar change/cancellation and notification delivery remain open.

## Conductor review — calendar CR/LF escaping — 2026-09-21

- **Finding:** iCalendar display-field escaping handled LF but left CR
  characters intact, allowing malformed line content from source text.
- **Fix:** commit `a573598` escapes CR and LF consistently and adds regression
  coverage for title and category values.
- **Verification:** focused calendar tests pass (10); the full suite passes
  425 tests with 8 skips; 438 project checks, Conductor, web-first, Power
  Platform, visual and canonical flow validators pass locally.
- **Residual gate:** native grants pages, private preferences, calendar
  change/cancellation and notification delivery remain open.

## Conductor review — current-user subscription boundary — 2026-09-21

- **Finding:** the local subscription matcher returned every matching
  `UserKey`, which could be mistaken for a multi-user delivery decision even
  though the active implementation is user-scoped.
- **Fix:** commits `a6e1602` and `db96224` require an explicit signed-in
  `current_user_key`, validate it, and return only that user when a rule
  matches. Documentation now states that the matcher is not delivery
  authorisation.
- **Verification:** focused planning tests pass (12); the full suite passes
  426 tests with 8 skips; 438 project checks, Conductor, web-first, visual and
  canonical flow validators pass locally. Power Platform binary discovery is
  present, but the current preflight reported shell initialisation warnings for
  `az`/`pwsh`; this is not tenant acceptance.
- **Residual gate:** current-user native page persistence and manual
  readback remain open; shared subscriptions, cross-user delivery and
  unattended notification are future extensions.

## Conductor review — delivery-key user binding — 2026-09-21

- **Finding:** delivery-event key generation accepted an arbitrary `user_key`,
  so a caller could create a ledger identity for a different user even though
  the active implementation is user-scoped.
- **Fix:** commit `0b5c920` requires an explicit `current_user_key` and rejects
  mismatched delivery identities; regression coverage verifies the boundary.
- **Verification:** focused relationships/operations tests pass (22); the full
  suite passes 426 tests with 8 skips; 438 project checks, Conductor,
  web-first, Power Platform, visual and canonical flow validators pass locally.
- **Residual gate:** current-user native page persistence and manual readback
  remain open; shared delivery and unattended notification are future
  extensions.

## Conductor review — institutional policy field typing — 2026-09-21

- **Finding:** policy validation checked field presence and formatted dates but allowed non-string identity/version/date values through coercive parsing.
- **Fix:** commit `09adbe2` requires typed policy identity/version/effective-date fields and adds regression coverage for malformed values.
- **Verification:** focused planning tests pass (12); the full suite passes 390 tests with 8 skips; project validation passes 438 checks; web-first, Conductor, Power Platform tooling and visual standards checks pass locally.
- **Residual gate:** native policy persistence, funding pages, calendar change/cancellation and notification delivery remain open.

## Conductor review — explicit policy end-date boundary — 2026-09-21

- **Finding:** an explicitly present blank `EffectiveTo` value was treated as
  an omitted policy end date, allowing malformed institutional policy metadata
  to pass validation.
- **Fix:** commit `574193db93658351d9140008dc0b1b75c500d334` rejects blank
  `EffectiveTo` values while retaining `null` for an intentionally open-ended
  policy, with regression coverage.
- **Verification:** focused planning tests pass (12); the full suite passes
  415 tests with 8 skips, 438 project checks pass, and web-first, Conductor,
  Power Platform, visual and canonical flow validators pass locally.
- **Residual gate:** native policy persistence, funding pages, calendar
  change/cancellation and notification delivery remain open.

## Conductor review — calendar generation timestamp semantics — 2026-09-21

- **Finding:** iCalendar generation timestamps were checked for their textual
  shape but impossible dates or times could still pass the boundary.
- **Fix:** commit `f4b44ac34a1c6bd01c355e6efb24c541ce46957` parses
  `generated_utc` as a real second-precision UTC timestamp and rejects
  impossible values, with regression coverage.
- **Verification:** focused calendar tests pass (9); the full suite passes 417
  tests with 8 skips, 438 project checks pass, and Conductor plus the
  publication/grants flow validators pass locally.
- **Residual gate:** native policy persistence, funding pages, calendar
  change/cancellation, subscriptions and notification delivery remain open.

## Conductor review — dedicated watchlist contract — 2026-09-21

- **Finding:** the first local watchlist schema declared `Scope` as a choice
  without constraining its allowed values, leaving the category/funder/
  opportunity boundary implicit.
- **Fix:** commit `6e1b43a` records the three supported scope values and adds
  regression coverage. The schema remains explicitly current-user and
  personal-list scoped.
- **Verification:** focused watchlist tests pass (2); the preceding full suite
  passed 428 tests with 8 skips, project validation passed 438 checks, and
  Conductor/web-first/Power Platform preflight passed locally.
- **Residual gate:** the native cloned-flow experiment was discarded because
  its grants-specific trigger/parser did not carry `Scope` and `TargetKey`.
  A dedicated native watchlist flow, page binding and delivery remain open.
## Conductor review — native dedicated watchlist flow — 2026-09-21

- **Finding:** the first native bootstrap route could not carry the dedicated watchlist scope/target input.
- **Fix:** generated a dedicated SharePoint-only package from the reviewed local contract, with serial key lookup, duplicate diagnostics and exact-zero create/exact-one update guards.
- **Verification:** import created exactly one canonical current-user flow. Flow Checker read 0 errors; controlled create and same-key update runs succeeded and SharePoint readback showed the expected field changes. The flow was restored Off. A synthetic row remains pending explicit UI deletion confirmation.
- **Residual acceptance:** native funding pages/report binding, calendar revision ledger and notification delivery remain open; this does not prove unattended or organisation-wide operation.

## Conductor review — native dedicated calendar flow — 2026-09-21

### Summary

The calendar upsert path was bootstrapped from the existing reviewed SharePoint-flow package pattern and imported as one isolated current-user DEV flow. The implementation targets the personal `Funding Calendar` SharePoint list, not OneDrive, and remains disabled after testing.

### Verification Checks

- Local `validate_calendar_flow_contract.py` passed, including serial processing, duplicate-key diagnostics, exact-zero/exact-one guards, complete `funding-calendar-v1` field mapping, SharePoint connector use and no OneDrive actions.
- Native Flow Checker readback showed 0 errors and 0 warnings while enabled.
- Native create run `08584116266950718806813049204CU16` succeeded and read back all expected calendar fields.
- Native same-key update run `08584116266295302685959687164CU15` succeeded and read back the changed date, cancellation flag, policy key and review status without a duplicate.
- Native flow status was restored to Off; owner remains Dylan Mordaunt and no sharing, schedule or notification change was made.
- Local full suite after the calendar additions: 432 tests passed, 8 skipped; project validation passed 438 checks, web-first validation passed, and the agent harness passed with `PASS_LOCAL_ONLY` boundaries.

### Findings

- **Status:** Partial — the flow and controlled persistence path are proven in isolated DEV, but this is not organisation-wide or unattended acceptance.
- **Residual gate:** the synthetic calendar row was subsequently deleted through the authenticated SharePoint UI and the list read back with zero data rows; native report pages are now evidenced through saved visual readback. Refresh/reconciliation, institutional-date/reminder/change ledger, subscription isolation and calendar/notification delivery remain open.
- **Decision:** keep G08 active. The native flow evidence is sufficient to close the calendar-upsert subtask, not the whole track, so archiving would overstate completion.

## Local model/report parity — 2026-09-22

### Summary

The local PBIP now represents the three user-scoped grant-support surfaces as
separate SharePoint-backed tables instead of incorrectly projecting calendar
and watchlist pages from the opportunity registry. This aligns the source
artefacts with the native field contract while preserving the boundary between
local validation and tenant acceptance.

### Verification Checks

- [x] **Plan compliance**: Pass — `FundingCalendar`, `MyFundingWatchlist` and
  `FundingDeliveryLedger` have explicit local M projections and model tables.
- [x] **Report binding**: Pass locally — the calendar and watchlist visuals
  resolve against their dedicated tables; 83 visuals pass geometry and field
  binding validation.
- [x] **Tests**: Pass — 437 tests passed with 8 skipped; project validation
  passed 451 checks; web-first validation is `PASS_LOCAL_ONLY`.
- [x] **Baseline**: Pass — the frozen runtime manifest was replaced with an
  outcome-linked source-only parity baseline and remains explicitly non-native.

### Findings

- **Residual native gate:** Power BI `Schema and data` refresh still stalls at
  `Processing queries and validating semantic model`; no native refresh or row
  reconciliation is claimed.
- **Residual operational gate:** flows remain Off after testing; subscription
  isolation, calendar revision/change execution and actual delivery remain
  open.

## Native flow inventory — 2026-09-22

- **Verification:** the authenticated Power Automate Cloud flows view returned
  exactly six current-user flows: one publications recurrence and one each for
  grants, DoRA, watchlist, calendar and delivery-ledger upsert.
- **Status:** the publications recurrence is the sole enabled/scheduled flow;
  the five grant/DoRA flows are each present once and disabled.
- **Boundary:** this proves inventory uniqueness and intended disabled state,
  not execution correctness, refresh, delivery, sharing or production
  acceptance.

## Local calendar revision ledger projection — 2026-09-22

### Summary

The canonical local model now includes an additive `FundingCalendarChanges`
projection. It preserves `ChangeKey`, prior/current revision and date values,
cancellation transitions, source URL, observation time and review state.
`scripts/grants_calendar_changes.py` emits a record only when explicit
before/after values differ; it does not write SharePoint, create calendar
events or send notifications.

### Verification checks

- [x] **Plan compliance:** Pass locally — the projection is separate from both
  the opportunity registry and the current-user delivery ledger.
- [x] **Fail-closed identity/evidence:** Pass — required keys, revisions,
  booleans, ISO dates, timestamps and HTTP(S) evidence URLs are validated
  without coercion.
- [x] **Regression coverage:** Pass — focused change-ledger tests cover create,
  cancellation, unchanged revisions and malformed input.
- [x] **Canonical checks:** Pass — 443 tests passed with 8 skips, 460 project
  checks passed and web-first validation is `PASS_LOCAL_ONLY`.
- [x] **Baseline:** Pass — the reviewed source-only runtime baseline records
  the new generated TMDL and remains explicitly non-native.

### Residual gates

Native change-ledger list persistence, current-user flow/page binding,
successful model refresh/reconciliation and actual reminder/calendar delivery
remain open. This local projection does not close those gates.

## Conductor review — calendar change list/import boundary — 2026-09-22

### Summary

The authenticated QLD Health personal DEV workspace now contains one isolated
`Funding Calendar Changes` list created only after inventory and a 404 check
showed that the target was absent. Native schema readback confirms the 13
canonical fields, requiredness, the required/unique/indexed `ChangeKey`, the
`Needs Review` default and false cancellation defaults. No synthetic item was
written and no flow was created or enabled.

The matching local SharePoint-only upsert contract is structurally valid and
the package was rebuilt through three bounded diagnostic variants. All native
import attempts were rejected with `MalformedFlowAssetFlowDefinition`,
including a package carrying metadata, connection-reference and authentication
shape copied from a tenant-exported native flow.

### Verification Checks

- **Plan Compliance:** Partial — isolated native list schema is read back;
  flow import, execution, page binding and delivery remain open.
- **Style Compliance:** Pass — the local contract remains SharePoint-only,
  serialised and fail-closed for duplicate identities.
- **New Tests:** Yes — focused calendar-change and flow-contract tests pass.
- **Test Coverage:** Partial — local schema/change semantics and package
  structure are covered; native import/deserialisation is not accepted.
- **Native Evidence:** The import surface reported the exact malformed-flow
  error in all three retries and the final inventory showed no new flow copy.

### Findings

- **Fixed:** local package structure now matches the established flow asset
  shape, and optional mappings use the known-good direct expression form.
- **Open blocker:** the Power Automate legacy importer still cannot deserialize
  this asset, even after a tenant-exported native shape was used privately as a
  transformation baseline. The remaining safe route is a native
  designer-created baseline for this exact list or tenant-side importer
  diagnostics; no further blind package retry is warranted.
- **Residual acceptance:** native flow import/readback, controlled run,
  SharePoint row reconciliation, model refresh and calendar delivery remain
  unproven.

### Native designer fallback review — 2026-09-22

- **Fix applied:** after the three legacy importer failures, the existing
  `Funding Calendar - Reviewed Upsert` flow was copied through the native
  Power Automate Save As route. The copy
  `e95f2a40-0689-42ec-b35b-b0e5f0440ba2` was rebound to the isolated
  `Funding Calendar Changes` list.
- **Expression repair:** the first draft exposed invalid expressions because
  shell quoting removed the property-name quotes. The create/update mappings
  were corrected natively and rechecked; Flow Checker read `Errors (0)` and
  `Warnings (0)`.
- **Readback:** the details page showed the flow saved at Modified
  `Sep 22, 2026, 02:11 AM` with Status `Off`; a fresh editor open had no
  recovery banner. The successful create run was
  `08584115988253175752159968677CU24` and the same-key update run was
  `08584115987296857629538066289CU13`. REST readback showed one item with
  stable `Id=1`, all mapped fields, the expected v1-to-v2/date/cancellation/
  URL/review changes and no duplicate. The exact synthetic item was then
  deleted through the native SharePoint `Delete?` confirmation; the REST
  endpoint returned zero items and the flow remained Off.
- **Finding:** two diagnostic runs with `PreviousDate=null` failed because the
  SharePoint connector received an empty string for the date field, even after
  the null-safe `if(empty(...), null, ...)` mapping. This is a native
  connector edge case and remains open; it must not be represented as a
  successful null-date path.
- **Decision:** this closes the native configuration and non-null
  create/update/readback subtask but not G08. Native null-date handling,
  page binding, refresh/reconciliation and actual calendar/reminder delivery
  remain open, so the track stays active.

### Native expression recheck — 2026-09-22

- **Finding and repair:** a fresh QLD Health designer readback found the
  copied flow's `Create item` and `Update item` property expressions rendered
  without quoted property names in several fields. The expressions were
  corrected in the existing flow identity and saved.
- **Native check:** Flow Checker read `Errors (0)` and `Warnings (0)` after
  the repair. The canonical local definition already contained the quoted
  expressions, so no local flow-definition change was needed.
- **Boundary:** this repairs the tenant configuration syntax only. The
  `PreviousDate=null` connector edge, refresh/reconciliation and delivery
  gates remain open; no new test row was written.

### Native null-date recheck — 2026-09-22

- **Controlled run:** the existing current-user flow was temporarily enabled
  for a single synthetic row with `PreviousDate=null`. Run
  `08584115961596220678423119580CU22` reached `SharePoint Get items` and then
  failed at `Create item` because the connector received an empty string for
  the `PreviousDate` date field. The native error was
  `OpenApiOperationParameterTypeConversionFailed` (expected `String/date`).
- **Cleanup/boundary:** no synthetic row was written, and the flow was turned
  Off after the test. This is authoritative evidence of the optional-date
  connector edge, not a successful null-date execution. A null-preserving
  action design, model/page binding, refresh/reconciliation and delivery
  remain open; G08 stays active.

### Conductor review — null-preserving local fix and native retry — 2026-09-22

## Summary

The local branch design is structurally sound and tested, but G08 is not
ready to archive because the native Control operation cannot currently be
authored through the authenticated QLD Health designer.

## Verification Checks

- **Plan compliance:** Partial — the local null-preserving create/update
  design is implemented; native import/readback, refresh and delivery remain
  open as explicitly recorded in the plan.
- **Style/compliance:** Pass — the definition remains SharePoint-only and
  preserves the canonical schema fields in both date branches.
- **New tests:** Yes — the existing calendar-flow contract now checks both
  with-date and without-date actions for create and update.
- **Test coverage:** Partial — local structural coverage passes; native
  optional-date execution is not yet proven.
- **Test results:** Passed — 444 tests with 8 skips, 460 project checks,
  web-first contracts, Conductor validation, Power Platform tooling preflight
  and diff checks all passed.

## Findings

### High — native branch authoring remains blocked

- **Evidence:** the QLD Health flow editor exposed the correct
  `Funding Calendar Changes` list, but the Control operation metadata request
  returned HTTP 403. The new condition could be inserted only as an unsaved
  shell; its code-view textarea did not persist edits when returning to the
  designer. The unsaved change was discarded, leaving the existing flow
  unchanged and Off.
- **Impact:** there is no native proof that null `PreviousDate` create/update
  succeeds. Do not import a second flow or archive G08.
- **Next action:** use an approved legacy/solution import route or a tenant
  session with Control-operation authoring permission to update the existing
  flow identity, then run null and non-null create/update cases with exact
  SharePoint readback and cleanup.

### Low — VUW CLI is not a substitute target

- **Evidence:** the active `pac` profile is VUW (`mordaudy@staff.vuw.ac.nz`),
  but `pac power-automate list-cloud-flows` returned no flows in that
  environment. It therefore cannot export this QLD Health flow or provide a
  valid cross-tenant import source.
- **Decision:** retain QLD Health as the authoritative native target; the
  VUW profile remains a tooling check only.

### Medium — direct package-import route did not reach import confirmation

- **Evidence:** the QLD Health `/flows/import` page was reachable in the
  authenticated browser session. The local
  `funding-calendar-changes-null-preserving-20260922.zip` was selected and
  the page accepted it into the upload control, but it remained at
  `Uploading your package ... Don't navigate away` without exposing the
  package mappings or enabled `Import` action. The session was navigated back
  to the existing flow details page without submitting the package.
- **Impact:** there is still no evidence that the revised definition entered
  the tenant; the existing flow identity remains the only canonical native
  flow and no duplicate was created.
- **Next action:** retry only with a package/solution export shape known to
  complete in this tenant, or obtain a tenant session with a working import
  route. After a successful import, read back the same flow identity, Flow
  Checker state, null/non-null create/update runs and exact SharePoint rows.

- **Control test:** a previously known-good `New` package for
  `CHHHS RIMS - Funding Calendar - Reviewed Upsert` was selected through the
  same route. It also remained at the upload-progress state and never exposed
  mappings or an enabled `Import` button. The session was stopped before any
  mutation and returned to the existing flow details page.

- **Backend readback:** the browser network trace showed the package upload
  was accepted by `generateResourceStorage` and the subsequent
  `listImportParameters` operation returned HTTP 202; polling the returned
  operation returned HTTP 200 with `status: Succeeded`, the expected flow
  resource and SharePoint connection resources. The wizard still remained on
  `Uploading your package`, so the remaining failure is the UI handoff after
  successful server-side package parsing. No import submission occurred.

### Classic designer continuation — 2026-09-22

- The classic QLD Health designer was reached by disabling the new-designer
  switch and exposed the Control/Condition action. The dynamic-content picker
  nevertheless returned duplicate `PreviousDate` labels from earlier actions
  without an unambiguous current calendar-row token in the attempted branch.
- The temporary condition shell was discarded through the browser reload
  confirmation. No partial edit was saved; the existing flow remains the sole
  canonical identity and Off. This adds route evidence but does not close the
  null-date gate.

### Native canonical-flow inventory recheck — 2026-09-22

The authenticated QLD Health Power Automate flow list was filtered by
`Funding` and returned exactly four results: Funding Calendar Changes, Funding
Delivery Ledger, Funding Calendar and Funding Watchlist. Each result had one
canonical flow identity and was visibly Off. Receipt:
`private/ops/2026-09-22-powerautomate-g08-flow-inventory.json`.

This strengthens the single-version/readback gate but does not close the
null-date branch, refresh/reconciliation or delivery gates. G08 remains active.

### Null-preserving package retry — 2026-09-22

#### Summary

The revised local package was retried through the authenticated QLD Health
Power Automate import route. Server-side upload completed and the package was
recognised as an update to the existing canonical flow. The existing QLD
Health SharePoint connection was selected, but the wizard kept the final
`Import` action disabled. The wizard was abandoned without submission.

#### Verification Checks

- **Package contract:** Pass locally — the null-preserving definition and
  package validator remain green.
- **Native mutation:** Not performed — no import was submitted, no flow was
  enabled, and the details page still reads Off with Flow Checker 0 errors.
- **Canonicality:** Pass — no duplicate flow was created; the existing flow
  ID remains the only target.
- **Receipt:** `private/ops/2026-09-22-powerautomate-g08-null-package-attempt.json`.

#### Findings

- **Residual blocker:** this tenant's browser import handoff accepts the
  package upload but does not expose an enabled final Import action, even
  after the target flow is set to Update and the SharePoint connection is
  selected.
- **Open gate:** native null-date create/update/readback remains unproven;
  refresh/reconciliation and calendar/reminder delivery are also open. G08
  remains active.

### Native code-view recheck — 2026-09-22

The existing canonical flow was reopened in the current QLD Health designer.
The `Apply to each Calendar Row` code view displayed the current loop and the
tenant SharePoint site/list identifiers, but the editor explicitly reported
`Cannot edit in read-only editor`. A locally validated null-preserving loop
definition was staged only in the browser control; it was rejected by the
read-only surface, no Save was enabled, and a reload restored the unchanged
flow. The flow remains Off and no second identity or partial draft exists.

- **Verification:** pass for blocker confirmation; no native mutation occurred.
- **Decision:** retain the existing flow as the sole canonical identity and
  keep G08 active until an approved editable designer, solution/import route or
  tenant permission enables the branch change and its null-date run/readback.
  Receipt: ignored `private/ops/2026-09-22-powerautomate-g08-code-view-readonly.json`.

### Native normal-designer insertion recheck — 2026-09-22

The normal Add an action route was tested against the same canonical flow. A
temporary nested `PreviousDate` condition could be staged, but the new
designer did not expose the existing downstream SharePoint action reliably
after the insertion, so its complete branch contract could not be verified.
The draft was reloaded and discarded. Receipt:
`private/ops/2026-09-22-powerautomate-g08-designer-insertion-reverted.json`.
No save, import, run, duplicate flow or tenant mutation occurred; the flow
remains unchanged and Off. The null-preserving local definition remains the
canonical implementation pending a safe native import/edit route.

### Native page-status text edit recheck — 2026-09-22

The current-user Power BI report was opened on `Funding Calendar & Watchlist`
to correct the stale cosmetic sentence that still says semantic-model binding
is open. The text box exposed a contenteditable rich-text surface, but the
browser replacement operation did not select the complete text and produced a
malformed unsaved draft. The report was reloaded before Save and native
readback restored the original text. No report/model mutation was saved.

Receipt: `private/ops/2026-09-22-powerbi-g08-status-text-edit-reverted.json`.
The cosmetic text correction remains open; the native table-binding evidence
and the separate refresh/reconciliation and notification-delivery gates are
unchanged.

### Native model refresh retry — 2026-09-22

The authenticated semantic-model editor started a fresh `Schema and data`
refresh after the prior synthetic grant rows had been cleaned up. It remained
at `Processing queries and validating semantic model` for a bounded 100-second
observation and was cancelled through the native confirmation. No model write,
refresh success or row reconciliation is claimed. Receipt:
`private/ops/2026-09-22-powerbi-native-refresh-retry.json`.

### Native branch insertion recheck — 2026-09-22

The authenticated new designer was rechecked against the same canonical flow.
It allowed a `Condition` to be inserted between `Condition Is New Calendar
Row` and `Create item`, but left the existing SharePoint action after the new
condition rather than placing it in a branch. The action menu exposed delete
and annotation controls only; no safe move/copy operation was available.
The unsaved draft was discarded by reload and the beforeunload confirmation.

- **Native mutation:** none; the flow remained Off and no Flow Checker or run
  was initiated.
- **Canonicality:** preserved; the existing flow ID remains the sole target.
- **Receipt:** `private/ops/2026-09-22-powerautomate-g08-condition-draft-discarded.json`.
- **Residual gate:** an approved editable branch/import/solution route is still
  required before null-date create/update/readback can be accepted.

### Native report/list reconciliation recheck — 2026-09-22

The current-user Power BI report page `Funding Calendar & Watchlist` still
rendered `synthetic-calendar-20260921` and `synthetic-watchlist-20260921`.
The corresponding authenticated SharePoint REST readbacks returned zero items
for both `Funding Calendar` and `My Funding Watchlist` after cleanup. This is
stale model/report data and must not be treated as current list persistence.

- **Mutation:** none; no model rows were manually changed and no refresh was
  claimed successful.
- **Receipt:** `private/ops/2026-09-22-powerbi-g08-stale-synthetic-readback.json`.
- **Residual gate:** a correlated successful refresh followed by row-set
  reconciliation is required before G08 can close.

### Native model refresh retry 2 — 2026-09-22

The authenticated QLD Health semantic-model editor was given one further
bounded refresh observation after the current-user `Funding Calendar` and `My
Funding Watchlist` SharePoint readbacks were empty. The refresh remained at
`Processing queries and validating semantic model` and was cancelled through
the native confirmation dialog.

- **Mutation:** none; no successful refresh, model write or row reconciliation
  is claimed.
- **Receipt:** `private/ops/2026-09-22-powerbi-native-refresh-retry-2.json`.
- **Residual gate:** native refresh remains blocked/stalled; G08 stays open.
