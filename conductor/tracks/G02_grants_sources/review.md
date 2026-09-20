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

## Remaining gate

Verify each permitted feed/API or produce a reviewed import sample, beginning with NHMRC, MRFF, ARC and Queensland sources. This needs source readback and remains separate from local catalogue validation.
