# Implementation plan

- [x] Record scope and acceptance requirements.
- [x] Inspect current inputs, dependencies and relevant platform objects. Existing publication `GrantIDs` are treated as award evidence candidates, not as opportunity identities.
- [x] Implement: Add typed, evidence-required relationships for awards, opportunity relevance and investigator affiliation, plus an additive SharePoint relationship-bridge schema and Power Query definition.
- [x] Verify: Local tests preserve the distinction between confirmed award links and candidate topic relevance; publication rows are not mutated.
- [~] Record local and live evidence separately before closure. An isolated DEV list now exists and the first native columns were created, but full schema readback, an approved relationship round-trip, and unchanged publication-total reconciliation remain open.
