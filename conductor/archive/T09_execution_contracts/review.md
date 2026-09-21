# Review: T09 local execution contracts and handoff

## Decision
Complete for local work-package scope only. No Power BI runtime or tenant acceptance is asserted.

## Scope and checks
Reviewed the changes from the v0.3.0-rc1 baseline through `affafc9`, including ten track plans/dependencies, helper modules, adversarial tests, source notes, synthetic examples and protected fallback instructions.

- 110 unit/reference tests passed, including 56 new tests.
- 212 original source-definition checks passed.
- 93 new structure/policy/manifest checks passed.
- Blank capability and live evidence templates correctly fail closed.
- The complete CSV/HTML demonstration contains six synthetic records; independent expected counts and key identities are checked.
- Fresh extraction passed the same checks, clean Git status and `git fsck --full`.
- The synthetic output hashes match after extraction.

## Review corrections
- Replaced stale four-page and PMID-only guidance with the three-page canonical-key target.
- Explicitly superseded Fabric Git acceptance without marking it deployed.
- Separated report copying from semantic-model isolation.
- Required evidence artifact hashes, exact target IDs, refresh correlation and observation timestamps; receipt structure is not proof of authenticity.
- Corrected generated CSV line endings and Git attributes so hashed example files survive source checkouts without platform-dependent changes.
- Kept known source defects unresolved in T11/T12 rather than laundering them through passing local tests.

## Remaining boundaries
The exact user Power BI plugin and live report/model IDs have not been discovered. No live query, report mutation, source refresh, full native export, scheduled flow or VM operation was executed. The Conductor upstream dependency is still a pinned unpopulated gitlink. T08 is blocked, T10–T15 are pending, T16/T17 are gated.

## Evidence
`../../../audit/WEB_FIRST_VALIDATION_REPORT.md`, `../../../audit/webfirst-extraction-verification.json`, `../../../audit/webfirst-unittest-output.txt`, `../../../audit/webfirst-policy-validation.json`.

## Conductor review recheck — 2026-09-23

T09 remains complete for its local execution-contract scope. Every plan item
is checked, its local evidence is preserved, and its downstream native gates
are explicitly owned by later tracks. The current canonical checkout passes
the full local suite, project validation, web-first validation and Conductor
structure validation. T09 is eligible for archive.
