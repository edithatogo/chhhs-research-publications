# G05 review

## Summary

Review status: in progress; university source and institutional-date discovery is recorded without promoting private portals to feeds.

- `config/grants-universities.json` covers JCU, UQ, QUT and Griffith with authority page, format, access boundary, eligibility scope, policy note and last verification.
- JCU public guidance states four weeks for major NHMRC/ARC schemes, one week for other Australian funders and two weeks for international bodies. UQ publishes internal/external close dates and states a standard ten-working-day Research Office close, with some strategic schemes up to four weeks.
- QUT and Griffith lead times remain null where a current public source was not sufficient. Griffith’s funding support page explicitly distinguishes internal-access support.
- `tests/test_grants_universities.py` prevents invented lead times and requires all four institutions.

- The shared bounded probe now supports `config/grants-universities.json`.
  A read-only 2026-09-20 probe observed one HTTP 200 page (UQ) and three HTTP
  403 responses (JCU, QUT and Griffith) through the same conservative path;
  this verifies page/access behaviour only and does not promote institutional
  portals, calendars or exports to feeds. Receipt:
  ignored `private/ops/2026-09-20-grants-university-probe.json`.

Portal exports, authenticated institutional feeds and specialist/foundation expansion remain open.

Fresh bounded probe evidence on 2026-09-20 observed UQ HTTP 200 and JCU,
QUT and Griffith HTTP 403. The receipt is ignored at
`private/ops/2026-09-20-grants-university-probe-current.json`. This confirms
the current public-page/access boundary only; it does not prove a permitted
institutional feed, portal export or calendar route.

Review fix applied: `load_universities` now validates known lead-time objects
for an allowed day unit and bounded non-negative numeric values, while keeping
unknown lead times as `null`. A focused regression test covers invalid data.

Review fix applied: boolean lead times, malformed authority URLs and invalid
`last_verified` dates now fail closed before a university source can be used.

Additional review fix applied in `ae2a630`: fractional lead-time values now
fail closed because institutional planning requires whole days. Unknown lead
times remain `null`.

## Verification Checks

- [x] **Plan Compliance**: Partial - JCU/UQ/QUT/Griffith source and access contracts are implemented; permitted institutional exports, feeds and authenticated portal routes remain open.
- [x] **Style Compliance**: Pass - unknown lead times remain unknown and are not inferred.
- [x] **New Tests**: Yes - malformed and boolean lead-time, authority URL and verification-date rejection are covered.
- [x] **Test Coverage**: Partial - catalogue and bounded probe contracts are covered; institutional access and feed acceptance are not.
- [x] **Test Results**: Passed - focused university tests (7), project validation (438 checks) and canonical-clone full suite (374 tests, 8 skipped).

## Findings

### Medium - university access and feed acceptance remains open

- **File**: `config/grants-universities.json`, `conductor/tracks/G05_grants_universities/plan.md`
- **Context**: Public-page probes and catalogue validation do not prove permitted portal exports, institutional feeds, authenticated access, or current specialist/foundation coverage.
- **Suggestion**: Keep G05 active until source-specific access evidence is captured; do not promote institutional pages to unattended intake or claim internal lead times where the catalogue retains `null`.

## Conductor review — catalogue identity and freshness hardening — 2026-09-21

- **Finding:** university catalogue loading string-coerced `institution_id` values, assumed object rows and did not reject future verification dates.
- **Fix:** rows must be objects with scalar non-empty string identities; `last_verified` is validated against the declared Australia/Brisbane date.
- **Verification:** focused university tests and the full local gates will be recorded against the implementation commit; institutional feed/export and authenticated portal acceptance remain open.
- **Verification:** commit `aa0c9ab` passes the focused university suite (7 tests), the full local suite (374 tests, 8 skips), project validation (438 checks), web-first contracts and Conductor validation; institutional feed/export and authenticated portal acceptance remain open.

## Conductor review — institution identity whitespace boundary — 2026-09-21

- **Finding:** university catalogue IDs were stripped for duplicate detection
  but the original whitespace-bearing row value could still be returned to
  downstream enrichment.
- **Fix:** commit `efc0dfeae03d8b5ab773e4c4d91a8e079465350e` rejects leading or
  trailing whitespace in `institution_id` values and adds regression coverage.
- **Verification:** focused university tests pass (8); the full suite passes
  420 tests with 8 skips, 438 project checks pass, and web-first, Conductor,
  Power Platform, visual and canonical flow validators pass locally.
- **Residual gate:** permitted institutional exports/feeds, authenticated
  portal access and current source acceptance remain open.

## University source freshness recheck — 2026-09-22

- **UQ:** the public current-funding table and research-office guidance were
  read back; internal and external closes are distinct and the standard
  research-office lead time is ten working days, with scheme exceptions.
- **QUT:** public research/ARC guidance was read back; internal deadlines are
  directed to the Research Office and no universal lead-time rule was
  promoted.
- **Fix applied:** UQ and QUT catalogue freshness dates now read `2026-09-22`.
- **Residual gate:** no permitted institutional export/feed or authenticated
  portal route was established. JCU/Griffith remain to be rechecked before
  G05 can close; unknown lead times remain null.

## Conductor review recheck — JCU and Griffith — 2026-09-22

### Summary

The official JCU and Griffith pages were rechecked. JCU's current application
procedures specify at least one week before Australian-funder internal deadlines
and two weeks before overseas-funder internal deadlines. Griffith's public
research-grants page confirms pre-award support and directs researchers to an
internal Research Funding service area.

### Verification checks

- [x] JCU authority and application-procedures pages are current official
  sources and are retained as manual-review evidence.
- [x] Griffith authority page is current official evidence; its internal-only
  support boundary is retained.
- [x] `last_verified` is refreshed to `2026-09-22` for JCU and Griffith.
- [x] No public feed, export, or authenticated portal route was inferred.
- [ ] Permitted institutional feed/export or authenticated portal acceptance.

### Findings

G05 remains active. JCU's qualified planning values and Griffith's unknown
lead-time value remain explicitly bounded; neither institution is promoted to
unattended ingestion.
