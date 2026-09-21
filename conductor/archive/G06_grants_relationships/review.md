# Review Report: G06_grants_relationships

## Summary

Review status: complete for the current-user isolated DEV scope. Local typed relationship safeguards are implemented, the isolated DEV SharePoint list has the complete eight-field schema read back, the native key constraint is read back, the evidence-bearing round-trip preserved publication totals, the synthetic row was deleted, and the relationship table is now saved in the existing Power BI semantic model. Organisation-wide sharing and unattended delivery remain future extensions, not prerequisites for this user-scoped track.

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

The earlier native gate is now closed for the current-user scope: all eight fields and the required/unique/indexed `RelationshipKey` were read back; the evidence-bearing relationship round-trip and unchanged publication receipt were captured; the exact synthetic row was deleted through the native SharePoint dialog; and Power Query created/saved the `Grant Relationships` table in the existing semantic model. The list and model remain isolated DEV objects, not organisation-wide or unattended bindings.

Review fix applied: relationship normalization now requires a valid HTTP(S)
evidence URL and one of the native review-status choices (`Needs Review`,
`Included`, `Excluded`). Invalid values fail closed before projection.

Additional review fix applied in `e329641`: confirmed `funded_by_award`
relationships now require a nonblank, trimmed `AwardID`; whitespace-only
values no longer pass the prior truthiness check.

Additional review fix applied in `8cf6b4f`: relationship records, required
keys, evidence URLs, confidence, AwardID and review status now require the
expected string types; malformed values fail closed instead of being coerced
into registry identities. The focused relationship suite covers this boundary.

## Verification Checks

- [x] Plan compliance: local schema, validation rules, additive native object and current-user model binding are aligned.
- [x] Style compliance: relationship types, confidence and review state remain explicit; publication rows are not mutated.
- [x] New tests: `tests/test_grants_relationships_operations.py` covers evidence, confidence and input-type boundaries.
- [x] Test coverage: local relationship schema and Power Query contract are covered; native schema, row round-trip, cleanup and model-table readback are evidenced separately.
- [x] Test results: focused relationship suite passed (15 tests); canonical-clone full suite passed at the current checkpoint (374 tests, 8 skipped; project validation 438 checks).

## Findings

1. The complete native field set is present and read back in isolated DEV.
2. `RelationshipKey` is required, unique and indexed in isolated DEV.
3. Organisation-wide sharing, cross-user delivery and unattended operation remain out of scope for the current-user track and are recorded as future extensions.

## Conductor review — relationship identity schema parity — 2026-09-21

- **Finding:** the native DEV readback was recorded as required, indexed and unique for `RelationshipKey`, but the tracked schema declared only required and indexed.
- **Fix:** commit `2e39aee` adds the explicit `unique` identity invariant and regression coverage.
- **Verification:** focused relationship tests pass (20); the full suite passes 384 tests with 8 skips; project validation passes 438 checks; web-first, Conductor, Power Platform tooling and visual standards checks pass locally.
- **Residual gate:** remaining required-field readback, relationship round-trip, unchanged publication totals and approved target binding remain open.

## Local relationship model projection — 2026-09-22

### Summary

The canonical local semantic model now includes the eight-field
`GrantRelationships` SharePoint projection. It preserves relationship identity
and endpoint keys as a bridge rather than flattening or mutating publication
rows.

### Verification Checks

- [x] **Plan compliance**: Pass locally — all eight tracked fields and the
  existing SharePoint-only query are represented in TMDL.
- [x] **Identity safety**: Pass — `RelationshipKey`, `FromKey`, `ToKey` and
  optional `AwardID` remain distinct fields with no implicit join.
- [x] **Test results**: Pass — 439 tests passed with 8 skipped; 457 project
  checks pass; web-first and harness checks remain local-only.
- [x] **Baseline**: Pass — the source-only runtime baseline records this
  intentional model change and remains explicitly non-native.

### Findings

- **Residual native gate:** native relationship-table binding and the current
  synthetic-row cleanup are now accepted for the current-user isolated scope;
  no shared relationship binding or publication backfill is claimed.

## Native closure evidence — 2026-09-22

- **SharePoint cleanup:** the exact `REL-SYNTH-G06-20260922` row was deleted
  through the authenticated SharePoint `Delete?` confirmation. The list page
  showed no remaining data row and the REST items endpoint returned an empty
  result.
- **Power BI model binding:** the existing semantic model's Power Query editor
  created and saved one `Grant Relationships` query from the authenticated
  QLD Health personal SharePoint site. Model readback showed `Grant
  Relationships table 27 of 27`, 30 columns and zero rows.
- **Decision:** the current-user G06 implementation is complete and suitable
  for archiving. Organisation-wide sharing, cross-user delivery and unattended
  operation remain explicitly deferred extensions.
