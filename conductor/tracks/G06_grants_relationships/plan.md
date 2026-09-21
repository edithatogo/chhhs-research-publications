# Implementation plan

**Access scope:** current-user isolated DEV list and manual readback only;
relationship data is not shared or delivered to other users in this tranche.

- [x] Record scope and acceptance requirements.
- [x] Inspect current inputs, dependencies and relevant platform objects. Existing publication `GrantIDs` are treated as award evidence candidates, not as opportunity identities.
- [x] Implement: Add typed, evidence-required relationships for awards, opportunity relevance and investigator affiliation, plus an additive SharePoint relationship-bridge schema and Power Query definition.
- [x] Verify: Local tests preserve the distinction between confirmed award links and candidate topic relevance; publication rows are not mutated.
- [~] Record local and live evidence separately before closure. The isolated DEV list exists with all eight canonical fields read back, and `RelationshipKey` is required, unique and indexed. On 2026-09-21 a synthetic evidence-bearing relationship was created, read back, updated, read back again, and deleted to the recycle bin. The list then read back `ItemCount=0`; the unchanged personal `Publication Registry` read back `ItemCount=1468`, with no publication mutation performed. Full before/after publication-key reconciliation remains open; shared binding is a future extension.
- [x] Task: Fail closed on non-HTTP evidence links and unsupported relationship review statuses (7375728).
- [x] Task: Reject whitespace-only AwardID values for confirmed award relationships (e329641).
- [x] Task: Reject non-string relationship identities, evidence URLs and review fields without coercion (8cf6b4f).
- [x] Task: Declare `RelationshipKey` required, indexed and unique in the tracked schema (`2e39aee`).
- [x] Task: Complete a current-user synthetic relationship create/read/update/read/delete round-trip and read back the publication-list boundary (2026-09-21).

### Native invariant readback continuation — 2026-09-22

- [x] Read the authenticated personal `Grant Relationships` list through SharePoint REST: `ItemCount=0`; `RelationshipKey` is required, indexed and unique; all eight relationship fields are present.
- [x] Read the personal `Publication Registry` through SharePoint REST: `ItemCount=1468`; the current page returned all 1,468 rows with no continuation link, 1,265 nonblank `CanonicalKey` values, and no duplicate nonblank keys.
- [ ] Capture a correlated before/after key-set receipt around a relationship round-trip. The current count/key-set readback strengthens the invariant evidence but does not by itself prove the historical before/after key-set comparison.
