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

## Verification Checks

- [x] **Plan Compliance**: Partial - local date-policy, subscription and calendar contracts are implemented; native pages, access isolation, reminders and delivery remain open.
- [x] **Style Compliance**: Pass - uncertain dates remain omitted and event identity is deterministic.
- [x] **New Tests**: Yes - duplicate UID, malformed policy, missing-key and invalid-URL rejection are covered.
- [x] **Test Coverage**: Partial - local calendar semantics are covered; native report persistence, personal access and delivery are not.
- [x] **Test Results**: Passed - focused calendar tests (5), planning/subscription tests (11), project validation (438 checks) and canonical-clone full suite (358 tests, 8 skipped).

## Findings

### Medium - native RIMS experience remains unproven

- **File**: `conductor/tracks/G08_rims_grants_experience/plan.md`
- **Context**: The local seven-page PBIP and iCalendar contract do not prove native funding pages, authenticated subscription persistence, reminder ledger, calendar update/cancellation or notification delivery.
- **Suggestion**: Keep G08 active until an approved isolated authoring route and native readback prove those behaviours; do not archive from local artefacts alone.

## Conductor review — subscription identity hardening — 2026-09-21

- **Verification:** focused planning tests passed (11); full suite passed (358 tests, 8 skipped); project validation passed (438 checks); web-first contracts passed locally.
- **Finding/fix:** `subscribers` previously string-coerced opportunity, category and funder keys and leaked an incidental exception for non-object rules. Commit `53d2419eccb664e9a61043096d8e208bea8ed7f1` requires string identities and explicit object validation.
- **Residual gate:** native funding pages, preference isolation, calendar update/cancellation and notification delivery remain open.
