# G04 review

Review status: in progress; local ingestion is implemented and tested, while live source and platform execution remain open.

## Changes

- Added `scripts/grants_ingestion.py` with namespace-tolerant RSS/Atom parsing and API-shaped batch normalization.
- Added per-source health results and failure isolation: a malformed source cannot erase successful records from another source, and a mixed batch is not accepted as complete.
- Retained raw deadline text and canonical deadline precision through the existing normalizer.

## Evidence

- `tests/test_grants_sources_ingestion.py` covers RSS, Atom, source failure isolation, catalogue validation and newest-observation/review preservation.
- No network fetch, SharePoint write, flow import, recurrence or notification was performed.

## Remaining gate

Run a controlled live cycle only after G02 endpoint/access verification and G03 isolated list readback. Then reconcile source keys, changed deadlines and archived rounds before operational acceptance.
