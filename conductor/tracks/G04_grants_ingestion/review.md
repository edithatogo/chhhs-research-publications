# G04 review

## Summary

Review status: in progress; local ingestion is implemented and tested, while live source and platform execution remain open.

Conductor review fix applied: calendar candidate identity now hashes the full
source row and duplicate identities fail closed before any candidate rows are
emitted. The focused adapter tests cover this failure path.

Additional review fix applied: duplicate non-empty RSS/Atom source identities
now fail closed in `parse_feed` rather than being silently deferred to a later
merge. The ingestion test suite covers this boundary.

Additional review fix applied: RSS/Atom entries without a title now fail closed
before normalization, matching the required SharePoint registry field.

Additional review fix applied: entries without either a source identifier or URL
now fail closed, preventing weak title/funder fallback identities from entering
the registry path.

Review fix applied: API-shaped records now use the same required title, URL,
stable-key and timezone-aware retrieval contract as RSS/Atom records before a
source batch can be accepted.

Additional review fix applied in `8817e21`: entries that lacked explicit
source IDs could still normalise to the same URL-based `OpportunityKey` within
one source batch. RSS/Atom and API-shaped batches now fail closed before
records are emitted; cross-source observation merging is unchanged.

Additional review fix applied on 2026-09-21: a non-object batch now fails
closed with an explicit `ValueError` before source-health processing, rather
than leaking an incidental attribute error.

## Changes

- Added `scripts/grants_ingestion.py` with namespace-tolerant RSS/Atom parsing and API-shaped batch normalization.
- Added per-source health results and failure isolation: a malformed source cannot erase successful records from another source, and a mixed batch is not accepted as complete.
- Retained raw deadline text and canonical deadline precision through the existing normalizer.
- Added `scripts/grants_arc_api.py` for the bounded ARC NCGP JSON API route. It
  preserves the public award identifier, evidence URL, status and amount but
  emits `RecordKind=Award` without an `OpportunityKey`, preventing award rows
  from entering the open-opportunity upsert path. `tests/test_grants_arc_api.py`
  covers page bounds, metadata preservation and fail-closed malformed input.
- Added `scripts/grants_html_calendar.py` for review-only extraction from
  official NHMRC and MRFF calendar tables. A live bounded probe produced 13 and
  179 candidate rows after suppressing a repeated MRFF header row, all with raw
  deadline text and `Needs Review`; no row was
  admitted to the accepted registry.

## Evidence

- `tests/test_grants_sources_ingestion.py` covers RSS, Atom, source failure isolation, catalogue validation and newest-observation/review preservation.
- No SharePoint write, flow import, recurrence or notification was performed.
  The HTML probe was read-only and its private receipt is
  `private/ops/2026-09-20-grants-html-calendar-readback.json`.

## Current bounded source exercise — 2026-09-21

The review-only adapter was run against fresh bounded HTTPS responses from the
official NHMRC and MRFF calendar pages. It returned `candidate_rows` with 13
NHMRC rows and 179 MRFF rows, preserving the source headers and raw deadline
text. The first NHMRC candidate was the published MRFF clinical-trial
collaboration row, demonstrating that the NHMRC calendar is a combined view;
source identity is therefore retained rather than inferred from page title.
No candidate was admitted to the accepted registry, and no SharePoint or flow
write was performed. This strengthens local/source evidence only; the live
source/list/flow acceptance gate remains open.

## Remaining gate

Run a controlled live cycle only after G02 endpoint/access verification and G03 isolated list readback. Then reconcile source keys, changed deadlines and archived rounds before operational acceptance.

## Verification Checks

- [x] **Plan Compliance**: Partial - RSS/Atom/API-shaped adapters, source isolation, calendar candidate handling and duplicate-identity fail-closed behaviour are implemented; live source/list/flow acceptance remains open.
- [x] **Style Compliance**: Pass - raw source values and uncertainty are retained; no source is promoted solely from page reachability.
- [x] **New Tests**: Yes - the ingestion suite now covers duplicate RSS/Atom source identity, titleless-entry, unbound-entry and incomplete API-record rejection.
- [x] **Test Coverage**: Partial - local parser and batch contracts are covered; live feed permissions, source changes and platform writes are not.
- [x] **Test Results**: Passed - focused ingestion tests (15) and canonical-clone full suite (363 tests, 8 skipped).

## Findings

### Medium - live ingestion acceptance remains open

- **File**: `conductor/tracks/G04_grants_ingestion/plan.md`
- **Context**: Local adapters do not prove a permitted source feed/API, SharePoint write, Power Automate execution, schedule or reconciliation against live rows.
- **Suggestion**: Keep G04 active until G02 source evidence and G03 target/binding gates are satisfied, then run a controlled source-to-list cycle and reconcile keys, deadline changes and archived rounds.

## Conductor review — malformed batch hardening — 2026-09-21

- **Verification:** focused G04 ingestion tests passed (15); full suite passed (363 tests, 8 skipped); project validation passed (438 checks); web-first contracts passed locally.
- **Finding/fix:** `ingest_batches` previously called `.get()` on a malformed non-object batch before it could fail through the contract. Commit `9d09f30ed154609515474d34ec0087d0a9b4649d` adds an explicit object check and regression coverage.
- **Residual gate:** permitted live source access, SharePoint/flow execution, reconciliation and unattended operation remain open.
