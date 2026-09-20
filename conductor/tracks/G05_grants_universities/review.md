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
- [x] **Test Results**: Passed - focused university tests (7), project validation (438 checks) and canonical-clone full suite (369 tests, 8 skipped).

## Findings

### Medium - university access and feed acceptance remains open

- **File**: `config/grants-universities.json`, `conductor/tracks/G05_grants_universities/plan.md`
- **Context**: Public-page probes and catalogue validation do not prove permitted portal exports, institutional feeds, authenticated access, or current specialist/foundation coverage.
- **Suggestion**: Keep G05 active until source-specific access evidence is captured; do not promote institutional pages to unattended intake or claim internal lead times where the catalogue retains `null`.

## Conductor review — catalogue identity and freshness hardening — 2026-09-21

- **Finding:** university catalogue loading string-coerced `institution_id` values, assumed object rows and did not reject future verification dates.
- **Fix:** rows must be objects with scalar non-empty string identities; `last_verified` is validated against the declared Australia/Brisbane date.
- **Verification:** focused university tests and the full local gates will be recorded against the implementation commit; institutional feed/export and authenticated portal acceptance remain open.
- **Verification:** commit `aa0c9ab` passes the focused university suite (7 tests), the full local suite (369 tests, 8 skips), project validation (438 checks), web-first contracts and Conductor validation; institutional feed/export and authenticated portal acceptance remain open.
