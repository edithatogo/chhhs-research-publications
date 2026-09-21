# G02 review

## Summary

Review status: in progress; the source catalogue is implemented and the ARC public awards API is now verified, while the opportunity-source and Queensland endpoint gates remain open.

## Conductor review finding and fix — 2026-09-22

The catalogue validated required source fields but accepted malformed optional
metadata such as boolean `record_kind`, numeric `sample_fixture` or a
non-string `api_url` on a non-API row. That could weaken provenance and source
classification without failing closed.

## Conductor review — optional API URL canonicalisation — 2026-09-22

- **Finding:** non-API catalogue rows accepted an optional `api_url` with
  surrounding whitespace. It was type-valid but not canonical, creating a
  future promotion ambiguity if that row later changed intake mode.
- **Fix:** all present optional `api_url` values now reject surrounding
  whitespace, while explicit `null` remains valid. A regression test covers a
  padded URL on a non-API row.
- **Verification:** focused source-ingestion tests pass (25); the full suite
  passes 451 tests with 8 skips; project validation passes 460 checks;
  web-first, Conductor and diff validation pass locally.
- **Residual gate:** permitted opportunity feeds, row-level review and
  eligibility evidence, unattended intake and production acceptance remain
  open.

The loader now requires optional metadata to be either a non-empty string or
explicit `null`, and validates any present `api_url` type before applying the
API-specific URL contract. Regression coverage was added in
`tests/test_grants_sources_ingestion.py`.

Commit `25ad9d8` passes the focused G02 suite (23 tests), the full suite (447
tests, 8 skipped), 460 project checks, web-first validation and Conductor
validation. This remains local source-catalogue evidence; permitted live
opportunity intake, eligibility review and unattended operation remain open.

## Synchronized verification — 2026-09-22

The canonical checkout passes 450 tests (8 skipped), 460 project checks,
Conductor validation and source-only CI run `35657921400`. This confirms local
source contracts only; permitted opportunity feeds, row-level review and
eligibility evidence remain open.

## Changes

- Added `config/grants-sources.json` covering NHMRC, MRFF, ARC, Queensland Health, EMF Queensland, Advance Queensland, FNQ Hospital Foundation, GrantConnect and CHHHS, with explicit format, access, coverage, eligibility and health fields.
- Added `scripts/grants_sources.py` to validate required source coverage, authority URLs, proposed intake modes, eligibility scope and explicit health states.
- Source-catalogue validation now also requires HTTP(S) authority/API URLs and ISO verification dates.
- Unverified feeds are represented as `research_only` or `unverified`; no source is silently treated as RSS/API-ready. The ARC route is the explicit exception: its public JSON API is marked `verified_sample` and `awards_only`, so it cannot be promoted to an open-opportunity feed.

## Evidence

- Catalogue validation is covered by `tests/test_grants_sources_ingestion.py`.
- The source map and authority references are documented in `docs/GRANTS_DELIVERY_REVIEW.md`.
- Official page checks on 2026-09-20 found NHMRC HTML/PDF/calendar and Tracker newsletter routes, MRFF open/forecast/closed HTML tables, Queensland Health HTML/PDF programme guidance, Health Practitioner Research Scheme, Metro South, Metro North and Torres and Cape discovery pages. The ARC Grants Dataset documentation exposes a paginated JSON API; a bounded read-only request returned HTTP 200 and one valid JSON award record. Receipt: ignored `private/ops/2026-09-20-grants-arc-api-readback.json`. No RSS/Atom endpoint or authenticated opportunity subscription was promoted.

- Additional Queensland sources are now explicit in the catalogue: QH Health
  Practitioner Research Scheme, Metro South Research Support Scheme, Metro North
  curated grants listing, Torres and Cape research support, and Cancer Council
  Queensland. They remain `manual_review`/`research_only` because the authority
  pages and application portals do not prove an unattended feed.

- Added `scripts/grants_source_probe.py`, a bounded read-only authority URL
  probe. It records status, redirect/content type, bounded-body hash and title
  without promoting an HTML page to RSS/Atom/API health. The 2026-09-20 local
  probe observed 9 HTTP 200 pages, 4 HTTP 403 responses and 1 HTTP 410 across
  the 14 catalogue rows. Receipt: ignored
  `private/ops/2026-09-20-grants-source-probe.json`.

- Added `scripts/grants_reviewed_import.py` as the explicit fallback route for
  sources without a permitted feed/API. It admits only rows with source and
  row identity, a valid HTTP(S) row URL, timezone-aware observation time,
  non-empty review notes and `ReviewStatus=Reviewed`; a single invalid row
  rejects the complete batch. `tests/test_grants_reviewed_import.py` covers
  admission, quarantine and fail-closed batch behaviour. This is a local
  import contract, not evidence that a current source row has been reviewed.

- The review-only HTML calendar adapter now preserves the complete observed
  source row in `SourceColumns`, keyed by normalised source headers. This
  closes a local evidence-loss gap for later human review while leaving
  `Deadline` unknown and `ReviewStatus=Needs Review` until row-level evidence
  is supplied.

- Review finding addressed: `SourceColumns` is convenient for lookup but cannot
  represent duplicate source headers without collision. The adapter now also
  emits ordered `SourceCells`, and the focused test asserts both forms.

- The probe confirms current authority-page reachability for NHMRC, MRFF, ARC,
  EMF Queensland, FNQ Hospital Foundation, CHHHS, the Health Practitioner
  Research Scheme, Metro North and Cancer Council Queensland. It also records
  access or stale-link evidence for Queensland Health, GrantConnect, Metro
  South, Torres and Cape and Advance Queensland. None of these observations
  proves a permitted unattended feed or API.

- A bounded table-discovery pass captured candidate rows from the NHMRC and
  MRFF authority pages, retaining source column names and raw date text. The
  private receipt contains six candidate rows and explicitly keeps them out of
  the accepted registry until identifier, date, URL and review fields are
  completed: ignored
  `private/ops/2026-09-20-grants-reviewed-table-discovery.json`.

- A fresh bounded probe on 2026-09-20 observed 10 HTTP 200 authority pages and
  4 HTTP 403 responses across the 14 configured federal and Queensland rows.
  The probe remains explicitly `not_proven_by_authority_probe`; it is not a
  feed/API test and does not change intake status. Receipt: ignored
  `private/ops/2026-09-20-grants-source-probe-current.json`.

The probe gives stronger current reachability evidence for NHMRC, MRFF, ARC,
EMF Queensland, FNQ Hospital Foundation, the Health Practitioner Research
Scheme, Metro South, Metro North, Torres and Cape and Cancer Council
Queensland. Queensland Health, Advance Queensland, GrantConnect and CHHHS
returned 403 in this bounded run. These outcomes are access observations, not
evidence that any source can be collected unattended.

- The new review-only HTML calendar adapter (`scripts/grants_html_calendar.py`)
  was exercised against bounded HTTP 200 responses from the official NHMRC and
  MRFF calendars. It produced 13 and 179 candidate rows respectively after
  suppressing a repeated MRFF header row, preserving raw deadline text and
  forcing `Needs Review`. It does not invent
  row links, exact dates, eligibility or current status. Receipt: ignored
  `private/ops/2026-09-20-grants-html-calendar-readback.json`.

- The Queensland Government Grants Finder CKAN `package_show` API returned
  HTTP 200 and valid JSON, but the package exposes only contribution-resource
  metadata rather than opportunity rows. It is therefore catalogued as
  `verified_sample`/`metadata_only`, not as an opportunity feed. Receipt:
  ignored `private/ops/2026-09-20-queensland-grants-finder-api-readback.json`.

- A fresh official-source verification snapshot on 2026-09-21 confirms that
  NHMRC and MRFF continue to publish HTML calendar tables with planning-date
  caveats, ARC continues to document a public JSON grants API for funded
  projects, and the Queensland Grants Finder remains a CKAN metadata catalogue
  rather than an opportunity-row feed. The snapshot is recorded in
  `docs/GRANTS_SOURCE_VERIFICATION_2026-09-21.md`; it refreshes source-page
  evidence only and does not promote any route to unattended intake.

- The first-party route decision was refreshed against the current NHMRC,
  MRFF, ARC and Queensland Grants Finder pages. NHMRC/MRFF remain HTML
  calendar surfaces with GrantConnect notification dependence; ARC’s public
  route remains awards/project context; and Queensland Grants Finder remains
  contribution metadata. The decision and source links are recorded in the
  verification snapshot; no unattended route was promoted.

## Remaining gate

Verify each remaining permitted opportunity feed/API or produce a reviewed import sample, beginning with NHMRC, MRFF and Queensland sources. The ARC public API sample is complete for awards-only context; it must remain separate from open-opportunity intake. Remaining work needs source readback and remains separate from local catalogue validation.

## Verification Checks

- [x] **Plan Compliance**: Partial - the local catalogue, fail-closed reviewed import, bounded calendar adapter and source-context preservation are implemented; permitted opportunity-feed/API evidence and row-level reviewed samples remain open.
- [x] **Style Compliance**: Pass - source uncertainty is retained explicitly and no HTML candidate is promoted to an accepted opportunity.
- [x] **New Tests**: Yes - the focused source tests cover URL/date metadata rejection as well as `SourceColumns` and ordered `SourceCells` preservation.
- [x] **Test Coverage**: Partial - local adapters and admission rules are covered; native source/feed, eligibility and unattended acceptance are outside local tests.
- [x] **Test Results**: Passed - focused tests (14), canonical-clone full suite (374 tests, 8 private-runtime skips), project validation (438 checks), and Conductor validation (0 errors).

## Findings

### Low - malformed evidence URLs could be treated as actionable

- **File**: `scripts/grants_registry.py`
- **Context**: URL normalization previously retained non-HTTP(S) values such as `javascript:` links, allowing malformed evidence to look usable downstream.
- **Suggestion**: Reject non-HTTP(S) URLs during normalization, return an empty actionable URL and force `Needs Review`.

Implemented in `da0b657`, with regression coverage in `tests/test_grants_registry.py`.

### Medium - permitted opportunity intake remains unproven

- **File**: `config/grants-sources.json`, `conductor/tracks/G02_grants_sources/plan.md`
- **Context**: Authority-page reachability, an ARC awards-only API sample, and HTML candidate extraction do not prove a permitted opportunity feed/API, reviewed eligibility, row-level source links or unattended collection.
- **Suggestion**: Keep the track active and complete the source-specific evidence gate through an approved export/feed or an actual human-reviewed import sample. Do not archive or mark the track complete based on local adapter tests.

### Low - native delivery remains outside this review

- **File**: `conductor/tracks/G02_grants_sources/plan.md`
- **Context**: No SharePoint write, Power Automate run, schedule, notification or organisation-wide target has been accepted for this source track.
- **Suggestion**: Close the local review phase, then hand the accepted source rows to G03/G04/G07 for native storage, ingestion and operational acceptance.

## Conductor review — catalogue evidence hardening — 2026-09-21

- **Verification:** focused G02 source tests passed (14); full suite passed (374 tests, 8 skipped); project validation passed (438 checks); web-first contracts passed locally.
- **Finding/fix:** catalogue validation previously string-coerced `source_id` values and accepted future `last_verified` dates. Commit `e4985b2bda7c2cf78b2b1fdf0a411f21f8c7c40a` requires a non-empty string identity and rejects dates later than the current date.
- **Residual gate:** source-page/API reachability is still not equivalent to permitted opportunity intake; reviewed rows or approved feeds remain required before G02 can close.

## Conductor review — remote CI timezone correction — 2026-09-21

- **Finding:** the first source-only GitHub Actions run at `5fa9a48` failed because `date.today()` evaluated the runner's UTC date (`2026-09-20`) while the catalogue's valid Brisbane verification date was already `2026-09-21`. This affected G02 freshness validation before targeted source assertions could run.
- **Fix:** commit `c00560f` evaluates the freshness guard with `Australia/Brisbane` and adds `test_catalogue_freshness_uses_brisbane_date`.
- **Verification:** focused G02 tests passed (17); canonical-clone full suite passed (374 tests, 8 skips); project validation passed (438 checks); web-first contracts passed locally; source-only GitHub Actions run [35527622183](https://github.com/edithatogo/chhhs-research-publications/actions/runs/35527622183) passed.
- **Residual gate:** this resolves source-only CI determinism, not the open permitted-feed/reviewed-row or native intake gate. G02 remains active.

## Conductor review — reviewed-import type hardening — 2026-09-21

- **Finding:** the manual reviewed-import fallback string-coerced reviewer fields and URLs, so malformed values could appear actionable.
- **Fix:** source/title/timestamp, URL, review status/notes and source-or-round identity now require their declared types and explicit values; malformed batches remain fail-closed.
- **Verification:** commit `0a5fc92` passes the focused reviewed-import suite (5 tests), the full local suite (374 tests, 8 skips), project validation (438 checks), web-first contracts and Conductor validation.
- **Residual gate:** a real human-reviewed current row or permitted opportunity feed/API is still required before G02 can close.

## Conductor review recheck — native reviewed-row evidence — 2026-09-22

The official Metro South Health 2027 INNOVATE page supplied a bounded,
explicitly reviewed row with distinct source and row URLs, a published amount,
eligibility statement and date window. The canonical current-user flow run
`08584115872127113780695944024CU04` succeeded, SharePoint readback returned
one item with key `metro-south-innovate-grants-2027` (ID 8), and the exact row
was deleted with HTTP 200. The final registry readback was an empty Atom feed
and the flow was Off.

This closes the specific reviewed-row/native-write evidence gap for the
isolated manual route. It does not promote the HTML page to an unattended
feed/API, establish organisation-wide eligibility, or prove recurrence,
monitoring, delivery or production acceptance. G02 remains active.

Receipt:
`private/ops/2026-09-22-powerautomate-g02-g04-metro-south-reviewed-row.json`.

## Conductor review — ARC adapter type hardening — 2026-09-21

- **Finding:** the ARC awards adapter string-coerced API identities, evidence links and descriptive fields, allowing malformed payload values to enter award context.
- **Fix:** commit `03568d7` requires typed source identities, links and text fields; numeric funding amounts remain supported as scalar API values, while objects/lists fail closed.
- **Verification:** the focused ARC adapter suite passes (4 tests). The ARC route remains awards-only and is not promoted to open-opportunity intake; permitted source access, reviewed eligibility and native intake remain open.

## Conductor review — HTML calendar row provenance — 2026-09-21

- **Finding:** the review-only NHMRC/MRFF table adapter retained only the page URL, so reviewers could not distinguish a row-specific source link from the calendar landing page.
- **Fix:** commit `e62b6f5` preserves actionable HTTP(S) row links as `SourceLinks` and exposes `SourceRowURL` only when exactly one unambiguous link is present; ambiguous or non-HTTP links remain explicit and do not become evidence automatically.
- **Verification:** focused HTML-calendar tests pass (6); full local suite passes (374 tests, 8 skips). This improves review provenance but does not create a permitted unattended feed or approve eligibility.

## Conductor review — reviewed-row evidence gate — 2026-09-21

- **Finding:** reviewed imports accepted the source-page `URL` without requiring a distinct row-level evidence link or an explicit eligibility statement.
- **Fix:** `SourceRowURL` is now required as an actionable HTTP(S) value and is preserved through normalization, the schema, semantic model, SharePoint create/update mapping and field-map export. `Eligibility` is required as a typed, non-empty reviewer input; no eligibility decision is inferred.
- **Verification:** focused reviewed-import, registry and flow-contract suites pass; the full suite passes 381 tests with 8 skips, project validation passes 438 checks, and the frozen runtime hash was intentionally refreshed for the model field change.
- **Residual gate:** these are local fail-closed controls; a human-reviewed current row or permitted opportunity feed/API and native list/flow acceptance remain required.

## Conductor review — distinct row evidence — 2026-09-21

- **Finding:** the reviewed-import gate required a row URL but did not reject a value identical to the general opportunity URL, weakening the documented row-level evidence boundary.
- **Fix:** commit `ffdc5a8` rejects identical `SourceRowURL` and `URL` values and adds regression coverage.
- **Verification:** focused reviewed-import tests pass (7); the full suite passes 384 tests with 8 skips; project validation passes 438 checks; web-first, Conductor, Power Platform tooling and visual standards checks pass locally.
- **Residual gate:** this strengthens local evidence validation only; a real human-reviewed current row or permitted opportunity feed/API and native intake remain required.

## Conductor review — ARC evidence URL structure — 2026-09-21

- **Finding:** the ARC adapter accepted any string with an HTTP(S) prefix, including malformed evidence URLs without a host.
- **Fix:** commit `96079a0` applies structural URL parsing and adds regression coverage while retaining the awards-only boundary.
- **Verification:** focused ARC tests pass (4); the full suite passes 385 tests with 8 skips; project validation passes 438 checks; web-first, Conductor, Power Platform tooling and visual standards checks pass locally.
- **Residual gate:** ARC remains awards-only; permitted opportunity intake, human-reviewed eligibility and native intake remain open.

## Conductor review — reviewed descriptive-field typing — 2026-09-21

- **Finding:** optional reviewed-row fields such as amount or status could be stringified by normalization, weakening the fail-closed import boundary.
- **Fix:** commit `04642b1` validates optional descriptive fields before normalization and adds an adversarial regression test.
- **Verification:** focused reviewed-import tests pass (8); the full suite passes 386 tests with 8 skips; project validation passes 438 checks; web-first, Conductor, Power Platform tooling and visual standards checks pass locally.
- **Residual gate:** a real human-reviewed current row or permitted opportunity feed/API and native intake remain required.

## Conductor review — catalogue URL typing — 2026-09-21

- **Finding:** source-catalogue URL validation stringified non-string authority or API values before parsing, weakening the explicit input-type boundary.
- **Fix:** commit `18dd567` requires URL values to be strings before structural HTTP(S) validation and adds regression coverage.
- **Verification:** focused source-ingestion tests pass (20); the full suite passes 389 tests with 8 skips; project validation passes 438 checks; web-first, Conductor, Power Platform tooling and visual standards checks pass locally.
- **Residual gate:** permitted opportunity intake, human-reviewed eligibility and native intake remain open.

## Conductor review — source identity whitespace boundary — 2026-09-21

- **Finding:** catalogue IDs were stripped for duplicate detection but the
  original whitespace-bearing value could still be returned to downstream
  ingestion and source-health reconciliation.
- **Fix:** commit `232025adbfcb3a19ff7834a26ccfe7c59d91750c` rejects leading or
  trailing whitespace in `source_id` values and adds regression coverage.
- **Verification:** focused source-ingestion tests pass (21); the full suite
  passes 415 tests with 8 skips, 438 project checks pass, and web-first,
  Conductor, Power Platform, visual and canonical flow validators pass
  locally.
- **Residual gate:** permitted opportunity intake, human-reviewed eligibility
  and native intake remain open.

## Conductor review — source URL whitespace boundary — 2026-09-21

- **Finding:** source catalogue URL validation stripped whitespace while
  retaining the original value, allowing an identity-divergent authority or
  API URL to pass configuration validation.
- **Fix:** commit `ec5322c` rejects surrounding whitespace on authority and API
  URLs and adds regression coverage for both paths.
- **Verification:** focused source/ingestion tests pass (22); the full suite
  passes 424 tests with 8 skips; 438 project checks, Conductor, web-first,
  Power Platform, visual and canonical flow validators pass locally.
- **Residual gate:** permitted opportunity intake, reviewed eligibility,
  controlled source-to-list reconciliation, native acceptance and unattended
  operation remain open.

## Bounded authority probe — 2026-09-22

- **Evidence:** the read-only source probe captured private receipts at
  `private/ops/grants-source-probes/grants-sources-20260922.json` and
  `grants-universities-20260922.json`. NHMRC, MRFF, ARC, EMF, Metro North,
  Cancer Council Queensland, Queensland Grants Finder and UQ returned HTTP
  200 authority pages; Queensland Health, Advance Queensland, GrantConnect,
  CHHHS, QH practitioner research, Metro South, Torres and Cape, JCU, QUT
  and Griffith returned HTTP 403 to the unauthenticated bounded probe.
- **Interpretation:** this updates reachability evidence only. It does not
  promote any source to RSS/Atom/API intake, infer eligibility, or overcome
  the tenant's authenticated-access boundary; `promoted_to_feed` remains
  false for every result.
- **Residual gate:** retain the reviewed-import fallback and obtain approved
  source/API or browser evidence before closing G02.

## Official Queensland/federal freshness recheck — 2026-09-22

- **NHMRC:** the official calendar was read back with current/upcoming rows
  and its planning-date caveat; it remains HTML/reviewed-import intake.
- **Queensland Health:** the research grants hub and Health Practitioner
  Research Scheme page were read back; the latter exposes a 2027 round and
  application guidance, not a permitted machine feed.
- **Metro North / Metro South:** official pages expose curated opportunities
  and current local rounds, including Metro South RSS/INNOVATE information;
  employment and scheme restrictions remain explicit.
- **Fix applied:** catalogue freshness dates for NHMRC, Queensland Health,
  QH HPRS, Metro North and Metro South now read `2026-09-22`.
- **Residual gate:** no source was promoted to unattended intake; stable
  row-level identity, permitted export/API and eligibility evidence remain
  required. G02 remains active.

## Official source/API cross-check — 2026-09-22

- **ARC:** the official Grants Search documentation exposes a paginated JSON
  API for funded projects and identifies the returned fields as award/project
  context. This is useful for historical/funded-award enrichment, but it is
  not an open-opportunity or deadline feed and remains awards-only.
- **Queensland Health / Metro South:** official programme pages expose current
  rounds, guidance and applicant restrictions. Metro South's 2027 Research
  Support Scheme is a concrete reviewed HTML source, but no permitted RSS,
  Atom, API or export route was established from the public pages.
- **UQ:** the research-office pages expose current-funding guidance and a
  public news RSS link. The RSS is news, not a funding-opportunity feed; the
  funding pages remain manual-review or institutionally controlled intake.
- **NHMRC:** the official search did not establish a machine-readable
  opportunity endpoint; the existing HTML calendar and Grant Tracker/manual
  route remain review-gated.
- **Decision:** VUW is not a viable bootstrap tenant because its authenticated
  PAC context has no cloud flows to export. QLD Health remains the authoritative
  target; no cross-tenant import or duplicate flow was created.

**References:** [ARC Grants Search help](https://dataportal.arc.gov.au/RGS/Web/Grants/Help),
[Queensland Health research grants](https://www.health.qld.gov.au/research-reports/research/researchers/grants-support),
[Metro South Research Support Scheme](https://www.metrosouth.health.qld.gov.au/research/research-grants/research-support-scheme),
[UQ research grants](https://research-support.uq.edu.au/research-office/research-grants).

- **Residual gate:** approved source access, row-level review/eligibility,
  native list/flow readback and unattended operational acceptance remain open.
