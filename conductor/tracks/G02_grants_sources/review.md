# G02 review

Review status: in progress; the source catalogue is implemented, but official-page discovery is not endpoint/feed acceptance.

## Changes

- Added `config/grants-sources.json` covering NHMRC, MRFF, ARC, Queensland Health, EMF Queensland, Advance Queensland, FNQ Hospital Foundation, GrantConnect and CHHHS.
- Added `scripts/grants_sources.py` to validate required source coverage, authority URLs, proposed intake modes, eligibility scope and explicit health states.
- Unverified feeds are represented as `research_only` or `unverified`; no source is silently treated as RSS/API-ready.

## Evidence

- Catalogue validation is covered by `tests/test_grants_sources_ingestion.py`.
- The source map and authority references are documented in `docs/GRANTS_DELIVERY_REVIEW.md`.
- No external endpoint payload or authenticated subscription was imported.

## Remaining gate

Verify each permitted feed/API or produce a reviewed import sample, beginning with NHMRC, MRFF, ARC and Queensland sources. This needs source readback and remains separate from local catalogue validation.
