# G06 review

Review status: in progress; local typed relationship safeguards are implemented.

- `scripts/grants_relationships.py` requires evidence URLs, distinguishes `funded_by_award` from `relevant_to_opportunity`, and requires an exact AwardID for confirmed award links.
- Candidate topical relevance cannot be promoted to funding evidence.
- `tests/test_grants_relationships_operations.py` covers these boundaries.
- Added `config/grant-relationships.schema.json` and `config/GrantRelationships.m`
  for an additive SharePoint relationship bridge keyed by `RelationshipKey`.
  The projection keeps relationship type, evidence, confidence and review
  state explicit; it does not flatten relationships into publication rows.

Native relationship storage, exact award readback and unchanged publication totals remain open.
