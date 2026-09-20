# G01 review

Review status: complete for the local contract scope; no live platform write was required or performed.

## Changes

- `scripts/grants_registry.py` now validates observation timestamps, retains timestamp status, selects the newest observation as the current record, and preserves an existing reviewed status/notes when a newer source observation lacks review information.
- SharePoint mapping includes `RoundID`, `ReviewNotes`, and timestamp status without changing publication identities.
- Regression coverage includes partial/invalid deadlines, alias-shaped records, repeated observations, round identity, invalid timestamps, and review preservation.

## Evidence

- `python3 -m unittest discover -s tests -p 'test_grants*.py' -v`: passed (15 focused tests at the time of review).
- `python3 scripts/validate_project.py`: pass after the full tranche.
- No tenant object, list, flow, schedule, notification, or report was modified.

## Limitations

The local `OpportunityKey` migration impact still requires a reviewed mapping before any future backfill. Live storage and ingestion acceptance belong to G03/G04/G07 and remain open.
