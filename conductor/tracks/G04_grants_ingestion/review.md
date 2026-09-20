# G04 review

Review status: in progress; local ingestion is implemented and tested, while live source and platform execution remain open.

Conductor review fix applied: calendar candidate identity now hashes the full
source row and duplicate identities fail closed before any candidate rows are
emitted. The focused adapter tests cover this failure path.

Additional review fix applied: duplicate non-empty RSS/Atom source identities
now fail closed in `parse_feed` rather than being silently deferred to a later
merge. The ingestion test suite covers this boundary.

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
