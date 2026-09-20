# Implementation plan

- [x] Record scope and acceptance requirements.
- [x] Inspect current inputs, dependencies and relevant platform objects. Existing publication `GrantIDs` are treated as award evidence candidates, not as opportunity identities.
- [x] Implement: Add typed, evidence-required relationships for awards, opportunity relevance and investigator affiliation.
- [x] Verify: Local tests preserve the distinction between confirmed award links and candidate topic relevance; publication rows are not mutated.
- [x] Record local and live evidence separately before closure; native relationship storage and publication-total readback remain open.
