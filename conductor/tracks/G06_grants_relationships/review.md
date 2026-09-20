# G06 review

Review status: in progress; local typed relationship safeguards are implemented.

- `scripts/grants_relationships.py` requires evidence URLs, distinguishes `funded_by_award` from `relevant_to_opportunity`, and requires an exact AwardID for confirmed award links.
- Candidate topical relevance cannot be promoted to funding evidence.
- `tests/test_grants_relationships_operations.py` covers these boundaries.
- Added `config/grant-relationships.schema.json` and `config/GrantRelationships.m`
  for an additive SharePoint relationship bridge keyed by `RelationshipKey`.
  The projection keeps relationship type, evidence, confidence and review
  state explicit; it does not flatten relationships into publication rows.

The earlier `E_ACCESSDENIED`/404 observation is superseded by a later authenticated, isolated DEV action on 2026-09-21. The Microsoft Lists UI created `Grant Relationships` at the personal DEV site:

`https://healthqld-my.sharepoint.com/personal/dylan_mordaunt_health_qld_gov_au/Lists/Grant%20Relationships/AllItems.aspx`

Native list readback confirmed the list exists and is empty. The additive schema work created the text columns `RelationshipKey`, `FromKey`, `ToKey`, and `AwardID`; a `RelationshipType` choice column was also submitted through the native editor. No production relationship row, synthetic relationship row, publication backfill, or report/model binding change was made.

The native gate remains open: read back the complete eight-field schema including `EvidenceURL`, `Confidence`, and `ReviewStatus`; confirm required/indexed constraints for `RelationshipKey`; then prove an approved evidence-bearing relationship round-trip and reconcile publication totals unchanged. The list is an isolated DEV object, not an approved organisation-wide target or unattended flow binding.
