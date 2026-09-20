# G05 review

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
