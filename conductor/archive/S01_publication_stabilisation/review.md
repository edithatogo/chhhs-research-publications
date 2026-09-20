# Execution evidence

Implementation started 2026-09-20. This review records local evidence only; it is
not a native Power BI, SharePoint or Power Automate acceptance certificate.

## S01.1 baseline and scope

| Surface | Observed locally | Generated locally | Contracted | Result |
|---|---|---|---|---|
| Canonical report artifact | `ReportSection3` CHHHS Publications; `ReportSection2` Monthly Publications; `ReportSection` Source Reconciliation; `ReportSection4` Clinical Analytics | `PublicationRegister`, `MonthlyPublications`, `SourceReconciliation`, `ClinicalAnalytics` | `dashboard.contract.json` contains the same four logical pages | Local definitions align after name/display-name translation | 
| Web-first contract | Four pages: CHHHS Publications, Monthly Publications, Source Reconciliation, Clinical Analytics | Four pages in current builders | `contracts/web-first-execution.contract.json` now requires four | Native inventory and contract migration align; Clinical Analytics is retained |
| Frozen runtime manifest | Four-page runtime hashes, including ClinicalAnalytics | Current generated report is a separate local artifact | Frozen manifest remains protected | No manifest regeneration performed |

Commands/results:

- `git status --short` and `git diff --stat`: existing user/runtime and documentation edits were present; no report or manifest paths were staged or overwritten.
- `python3 scripts/agent_harness.py check --task all`: initial baseline was `FAIL_LOCAL` because the dependency validator did not recognise the new non-T tracks; after the validator fix and subsequent repairs, final result is recorded below.
- Local JSON inspection of `downloads/canonical_live_artifacts/report/report.json`: four observed report sections. Native UI/plugin page inventory was not available in this tranche, so native scope remains open.

### Native read-only page inventory — 2026-09-20

Authenticated `playwright-cli` readback of the existing Power BI report confirmed
four rendered research pages: `ReportSection3` CHHHS Publications,
`ReportSection2` Monthly Publications, `ReportSection` Source Reconciliation and
`ReportSection4` Clinical Analytics. The private receipt is
`private/ops/2026-09-20-powerbi-report-page-inventory.json`.

This resolves the scope decision: retain Clinical Analytics and migrate the
web-first contract to four required pages. No report/model write was performed.

## S01.2 evidence-preserving attribution

Changed paths: `config/organisation-hierarchy.json`, `scripts/organisation_enrichment.py`, `scripts/clinical_attribution.py`, `tests/test_organisation_enrichment.py`, `tests/test_clinical_attribution.py`, `tests/fixtures/invalid-organisation-reference.json`.

- Generic aliases (`Community Health`, `Primary Health Centre`, `Emergency Service`) were removed or qualified; matching now uses token boundaries and validated parent links.
- Exact affiliation text is retained as `AffiliationTextObserved`; unmatched records retain empty organisation dates and unknown confidence.
- Reference version and effective dates come from the reference document/unit metadata; build time is not used as historical validity.
- Unordered structured affiliations and affiliation-string position no longer imply first/senior authorship. Explicit numbered/role evidence remains supported. Comma-separated surname/given-name strings are no longer mistaken for multiple authors.
- Focused organisation tests: 8 passed. Focused clinical attribution tests: 15 passed.

## S01.3 executable flow structure

Changed paths: `scripts/build_sharepoint_upsert_package.py`, `scripts/validate_publication_platform_contract.py`, `config/sharepoint-publication-target.template.json`, `tests/test_publication_platform_contract.py` and ignored private target/package artefacts.

- The generated package now places lookup, duplicate detection, create and update actions inside `Apply_to_each_Publication` with serial concurrency.
- The loop consumes query rows, SourceKey is escaped before the OData filter, and duplicate lookup results terminate the record path with `DUPLICATE_SOURCE_KEY`.
- The builder reads site/list/field mappings from a validated ignored private target file; the tracked template contains placeholders only. Internal `field_N` names are configuration data, not guessed renames.
- Validation now checks connector, target, loop, concurrency, duplicate fail-closed branch, update allowlist, escaped filter and sibling `runAfter` dependencies. Mutation tests cover missing loop, parallel writes, duplicate handling, top-level record actions, placeholder targets and unknown dependencies.
- Added `scripts/publication_batch_contract.py` and `tests/test_publication_batch_contract.py`. The local contract rejects partial/error pages, duplicate keys, non-advancing cursors, missing continuation cursors, count mismatches and independent-key-set mismatches. It also rejects updates to manual/provenance fields and permits only observation fields (including the configured `field_20` mapping).
- `python3 scripts/build_sharepoint_upsert_package.py ...`: exit 0; generated ignored private package.
- `python3 scripts/validate_publication_platform_contract.py`: exit 0; structural contract passed. This remains local structural evidence, not a live flow import or execution certificate.

## Review pass

Review outcome: no unresolved critical/high findings in the completed local tranche. Review fixes applied in the same tranche:

- updated `conductor/tech-stack.md` to the verified Conductor submodule pin;
- required valid SharePoint list GUIDs and ISO-formatted organisation reference dates;
- added regression coverage for invalid target/reference metadata.

Focused S01.3.5 result: 11 contract tests passed. This closes the local pagination/allowlist task; native paged-flow execution/readback remains outside this local track.

## Conductor review — 2026-09-20

Review scope covered the S01 plan, the four-page native inventory, the contract
migration diff and the focused/full local gates. The initial review finding was
stale three-page wording in the active web-first validator/test and scope table;
it was corrected before closure. No unresolved critical, high or medium findings
remain. The frozen runtime manifest was intentionally not regenerated because
the existing manifest already records four pages and its native_verified flag is
false.

Verification:

- `python3 -m unittest discover -s tests -p 'test_webfirst.py' -v`: 62 passed.
- `python3 -m unittest discover -s tests -v`: 281 passed.
- `python3 scripts/validate_project.py`: 319 checks passed.
- `python3 scripts/agent_harness.py check --task all`: PASS_LOCAL_ONLY.
- `python3 scripts/webfirst_contracts.py validate`: PASS_LOCAL_ONLY.

The private page-inventory receipt is the native read-only evidence; no report,
model, refresh, export, schedule or production mutation was performed.

## Remaining blockers

- S01.3 native paged-flow execution/readback remains an E01/T15 acceptance gate;
  the local structure and pagination contract are complete.
- Native refresh/export/release evidence remains outside S01 and is owned by
  T11, T14, E01, E07 and T15.
- Existing private runtime evidence remains ignored and was not copied into tracked artefacts.

For each task record: task ID, outcome, changed paths, command and exit status, fixture/live distinction, evidence path and capture time, remaining limitations, rollback reference. Do not include credentials or tenant IDs here.
