# G02 review

## Summary

Review status: in progress; the source catalogue is implemented and the ARC public awards API is now verified, while the opportunity-source and Queensland endpoint gates remain open.

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

## Remaining gate

Verify each remaining permitted opportunity feed/API or produce a reviewed import sample, beginning with NHMRC, MRFF and Queensland sources. The ARC public API sample is complete for awards-only context; it must remain separate from open-opportunity intake. Remaining work needs source readback and remains separate from local catalogue validation.

## Verification Checks

- [x] **Plan Compliance**: Partial - the local catalogue, fail-closed reviewed import, bounded calendar adapter and source-context preservation are implemented; permitted opportunity-feed/API evidence and row-level reviewed samples remain open.
- [x] **Style Compliance**: Pass - source uncertainty is retained explicitly and no HTML candidate is promoted to an accepted opportunity.
- [x] **New Tests**: Yes - the focused source tests cover URL/date metadata rejection as well as `SourceColumns` and ordered `SourceCells` preservation.
- [x] **Test Coverage**: Partial - local adapters and admission rules are covered; native source/feed, eligibility and unattended acceptance are outside local tests.
- [x] **Test Results**: Passed - focused tests (12), canonical-clone full suite (354 tests, 8 private-runtime skips), project validation (438 checks), and Conductor validation (0 errors).

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
