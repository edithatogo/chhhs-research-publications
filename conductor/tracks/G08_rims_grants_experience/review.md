# G08 review

## Summary

Review status: in progress; local planning and idempotency contracts are implemented.

- `validate_policy` requires a version, organisation, anchor, lead time, holiday-calendar version and effective dates.
- `delivery_event_key` gives future notifications a stable deduplication key; it does not send messages or create calendar events.
- Existing subscription matching remains candidate generation only and does not authorize delivery.
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
- **Residual gate:** the synthetic calendar row remains in the list pending explicit UI deletion confirmation; native report pages, institutional-date/reminder/change ledger, subscription isolation and calendar/notification delivery remain open.
- **Decision:** keep G08 active. The native flow evidence is sufficient to close the calendar-upsert subtask, not the whole track, so archiving would overstate completion.
