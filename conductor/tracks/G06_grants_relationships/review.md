# G06 review

Review status: in progress; local typed relationship safeguards are implemented.

- `scripts/grants_relationships.py` requires evidence URLs, distinguishes `funded_by_award` from `relevant_to_opportunity`, and requires an exact AwardID for confirmed award links.
- Candidate topical relevance cannot be promoted to funding evidence.
- `tests/test_grants_relationships_operations.py` covers these boundaries.
- Added `config/grant-relationships.schema.json` and `config/GrantRelationships.m`
  for an additive SharePoint relationship bridge keyed by `RelationshipKey`.
  The projection keeps relationship type, evidence, confidence and review
  state explicit; it does not flatten relationships into publication rows.

Native relationship storage, exact award readback and unchanged publication totals remain open. An isolated DEV creation attempt for `Grant Relationships` returned SharePoint `E_ACCESSDENIED`; a direct list URL then returned 404, so no relationship list was created and no synthetic relationship row was written. The local schema/M definition remains ready for a permitted target.

Current authenticated UI evidence on 2026-09-28 supersedes the old 404 inference: an existing empty `Grant Relationships` list is visible in the isolated personal DEV site. It has versioning, a unique/indexed key and one owner role. Native schema drift remains in relationship/review choices and required flags; see `private/ops/2026-09-28-g06-native-list-settings-readback-private.json` and the active G06 plan. This is a reuse and rollback baseline, not H02 acceptance. No list or row was changed.

The isolated DEV physical schema was subsequently aligned with the eight-field local contract and read back after every field save. `ReviewStatus` is required Text, `RelationshipType` includes `candidate_award_match`, and the other required flags are enabled. The final parity receipt and exact prewrite rollback pointers are `private/ops/2026-09-28-g06-native-schema-alignment-postwrite-private.json`. No rows were written; authoritative key/reviewer reconciliation, controlled replay and model/report acceptance remain open.

## 2026-09-25 award identity separation

Local normalization now requires `AWARD:* -> PUB:*` plus a nonblank exact
AwardID for award relationships, and `PUB:* -> GRANT:*` for opportunity
relevance. Unconfirmed award candidates use `candidate_award_match` and cannot
be serialized as `funded_by_award`; withdrawn/retracted/rejected awards cannot
be confirmed as funded. Focused relationship tests pass 8/8. This is local
contract evidence; native storage and exact award evidence remain open.

## 2026-09-25 batch-source validation slice

`validate_relationship_batch` now accepts explicit publication, opportunity,
award and affiliation source snapshots and returns validated typed rows plus
input ordinals with rejection reason codes. It rejects all duplicate derived
relationship keys; duplicate or absent source keys; orphan publication or
opportunity targets; mismatched or ambiguous `(AwardID, FunderKey)` identities;
withdrawn awards; and missing/unresolved/ambiguous confirmed affiliations.
Award IDs reused by different funders remain separate only when each supplied
funder-scoped AwardKey resolves exactly; there is no AwardID-only join. A valid
candidate award relationship remains a candidate. No publication row mutation
is performed.

Focused tests pass 19/19 at this checkpoint. The H01 checklist remains open because repository
fixtures and local contracts do not reconcile authoritative tenant key formats,
reviewed identity reuse, or current publication/organisation acceptance
evidence. Native bridge, joins, and publication-total parity remain unverified.

The integrated repository harness passes 504 unit tests and 446 project checks after this slice. Conductor and web-first checks remain local structure/contract evidence; native bridge and publication-total parity remain open.

## 2026-09-25 normalized affiliation identity collision

Fixed a reproducible last-write-wins gap: two source-map keys that differed
only by surrounding whitespace normalized to the same investigator identity,
but the later key replaced the earlier affiliation target. The batch validator
now aggregates targets for normalized identities and rejects a confirmed
relationship as ambiguous when the combined target set has multiple members.
Regression: `test_batch_rejects_affiliation_identity_collision_after_whitespace_normalization`.
Focused local validation only; native identity/source reconciliation remains
open.

## 2026-09-25 relationship evidence URL validation

`EvidenceURL` validation now requires an absolute HTTP(S) URL with a hostname
and rejects embedded credentials while preserving the supplied URL. Focused
relationship tests pass 25 tests. This validates local evidence references;
native relationship storage and evidence-row readback remain open.

## 2026-09-28 typed input guard

`normalize_relationship` rejects non-object inputs and non-text relationship
type, endpoint keys, evidence URL, confidence, AwardID and ReviewStatus.
`validate_relationship_batch` also rejects malformed caller-supplied
publication/opportunity keys, award identity fields, and affiliation key/target
types before matching. This prevents malformed upstream JSON values from being
coerced into identities or review decisions. Focused local tests pass 31/31;
authoritative key reconciliation and native bridge acceptance remain open.

### Confirmed funding review-state guard — 2026-09-28

The normalizer previously allowed a `funded_by_award` relationship with
`Confidence=confirmed` while leaving `ReviewStatus` at the default `Needs
Review`. It now requires explicit `ReviewStatus=Reviewed`; missing, blank and
pending review states fail. Candidate award matches are unchanged. The focused
relationship/operations suite passes 32 tests. This is local contract evidence,
not trusted reviewer identity or native acceptance; G06-H01 remains open for
authoritative key-format and reviewed-identity reconciliation.

A final source-snapshot boundary check found whitespace-only publication or
opportunity keys were silently filtered. The validator now rejects those
malformed snapshots while continuing to accept a genuinely empty key set; the
same 32-test suite passes, including blank-key subcases. H01 remains open for
authoritative source identity and review evidence.

## Author-key interoperability — 2026-09-28

Relationship test fixtures now use the generated author registry prefix (`AUTH:`). A cross-module regression builds a real deterministic author key from a DORA source record and resolves it through the relationship batch validator as a candidate affiliation. The 33 focused relationship/operations tests pass. This verifies local key-shape interoperability only; human-reviewed affiliation evidence, authoritative organization keys and native bridge acceptance remain open.

### Relationship key encoding hardening — 2026-09-28

`RelationshipKey` now hashes a compact JSON tuple of the typed identity fields instead of joining them with `|`. This prevents delimiter-bearing source keys, target keys, award IDs or evidence URLs from aliasing a different relationship and improves idempotency before the native bridge is accepted. A focused regression demonstrates that two formerly colliding affiliation tuples now produce different keys. The bridge remains undeployed/unaccepted, so no native migration was performed; if any pre-existing relationship rows are discovered during H02 inventory, correlate their old keys before replacement. Local tests do not prove native key migration or acceptance.
