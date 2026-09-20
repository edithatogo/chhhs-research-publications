# G02 review

Review status: in progress; the source catalogue is implemented, but official-page discovery is not endpoint/feed acceptance.

## Changes

- Added `config/grants-sources.json` covering NHMRC, MRFF, ARC, Queensland Health, EMF Queensland, Advance Queensland, FNQ Hospital Foundation, GrantConnect and CHHHS, with explicit format, access, coverage, eligibility and health fields.
- Added `scripts/grants_sources.py` to validate required source coverage, authority URLs, proposed intake modes, eligibility scope and explicit health states.
- Unverified feeds are represented as `research_only` or `unverified`; no source is silently treated as RSS/API-ready.

## Evidence

- Catalogue validation is covered by `tests/test_grants_sources_ingestion.py`.
- The source map and authority references are documented in `docs/GRANTS_DELIVERY_REVIEW.md`.
- Official page checks on 2026-09-20 found NHMRC HTML/PDF/calendar and Tracker newsletter routes, MRFF open/forecast/closed HTML tables, Queensland Health HTML/PDF programme guidance, Health Practitioner Research Scheme, Metro South, Metro North and Torres and Cape discovery pages, and an ARC research-fetch 403. No RSS/Atom/API endpoint or authenticated subscription was promoted.

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

## Remaining gate

Verify each permitted feed/API or produce a reviewed import sample, beginning with NHMRC, MRFF, ARC and Queensland sources. This needs source readback and remains separate from local catalogue validation.
