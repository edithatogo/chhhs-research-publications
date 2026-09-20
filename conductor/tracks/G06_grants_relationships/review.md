# Review Report: G06_grants_relationships

## Summary

Review status: in progress. Local typed relationship safeguards are implemented, and the isolated DEV SharePoint list now has the complete eight-field schema read back. The native key constraint is also read back. The track remains open because the remaining required-field constraints, an approved evidence-bearing relationship round-trip, unchanged publication totals, and an approved organisation-wide target/binding are not proven.

- `scripts/grants_relationships.py` requires evidence URLs, distinguishes `funded_by_award` from `relevant_to_opportunity`, and requires an exact AwardID for confirmed award links.
- Candidate topical relevance cannot be promoted to funding evidence.
- `tests/test_grants_relationships_operations.py` covers these boundaries.
- Added `config/grant-relationships.schema.json` and `config/GrantRelationships.m`
  for an additive SharePoint relationship bridge keyed by `RelationshipKey`.
  The projection keeps relationship type, evidence, confidence and review
  state explicit; it does not flatten relationships into publication rows.

The earlier `E_ACCESSDENIED`/404 observation is superseded by a later authenticated, isolated DEV action on 2026-09-21. The Microsoft Lists UI created `Grant Relationships` at the personal DEV site:

`https://healthqld-my.sharepoint.com/personal/dylan_mordaunt_health_qld_gov_au/Lists/Grant%20Relationships/AllItems.aspx`

Native list readback confirmed the list exists and is empty. The additive schema work created and read back all eight canonical fields: text `RelationshipKey`, `FromKey`, `ToKey`, and `AwardID`; choice `RelationshipType`; hyperlink `EvidenceURL`; and choices `Confidence` and `ReviewStatus`. The choice values were configured as `confirmed`, `review`, `candidate` for `Confidence`, and `Needs Review`, `Included`, `Excluded` for `ReviewStatus`. `RelationshipKey` was read back as required, unique, and indexed. No production relationship row, synthetic relationship row, publication backfill, or report/model binding change was made.

The native gate remains open: configure/read back the remaining required fields, prove an approved evidence-bearing relationship round-trip, and reconcile publication totals unchanged. A subsequent browser navigation replaced the authenticated session with a sign-in page before the remaining column settings could be read back; those constraints are therefore not inferred. The list is an isolated DEV object, not an approved organisation-wide target or unattended flow binding.

Review fix applied: relationship normalization now requires a valid HTTP(S)
evidence URL and one of the native review-status choices (`Needs Review`,
`Included`, `Excluded`). Invalid values fail closed before projection.

## Verification Checks

- [x] Plan compliance: local schema, validation rules and additive native object are aligned.
- [x] Style compliance: relationship types, confidence and review state remain explicit; publication rows are not mutated.
- [x] New tests: `tests/test_grants_relationships_operations.py` covers evidence and confidence boundaries.
- [x] Test coverage: local relationship schema and Power Query contract are covered.
- [x] Test results: canonical-clone full suite passed at the current checkpoint (344 tests, 8 skipped; project validation 438 checks).

## Findings

1. The complete native field set is present and read back in isolated DEV.
2. `RelationshipKey` is required, unique and indexed in isolated DEV.
3. Remaining required-field settings, relationship round-trip, unchanged publication reconciliation and approved production/unattended binding remain open.
