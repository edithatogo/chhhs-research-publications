# Implementation plan

- [x] Record scope and acceptance requirements.
- [x] Inspect current inputs, dependencies and relevant platform objects. Existing publication `GrantIDs` are treated as award evidence candidates, not as opportunity identities.
- [x] Implement: Add typed, evidence-required relationships for awards, opportunity relevance and investigator affiliation, plus an additive SharePoint relationship-bridge schema and Power Query definition.
- [x] Verify: Local tests preserve the distinction between confirmed award links and candidate topic relevance; publication rows are not mutated.
- [~] Record local and live evidence separately before closure. The isolated DEV list now exists with all eight canonical fields read back, and `RelationshipKey` is required, unique and indexed. Remaining required-field readback, an approved relationship round-trip, and unchanged publication-total reconciliation remain open.
- [x] Task: Fail closed on non-HTTP evidence links and unsupported relationship review statuses (7375728).
