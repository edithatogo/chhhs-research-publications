# Current RIMS checkpoint

Updated: 2026-09-21. This is the compact resumption checkpoint, not a live acceptance certificate. Refresh after meaningful work; keep historical narrative in existing evidence documents.

## Direction

Conductor audit: all track index/spec/plan/metadata files and dependencies validate. T11, T14, T15 and E01 are reopened for outstanding native/operational acceptance; do not treat their historical completion paragraphs as current status. The private GitHub origin contains the source-only canonical history; the dirty local working tree remains the authoring workspace and is not itself the remote release.

One person owns this repository and the existing CHHHS RIMS report. Add funding opportunities, funding calendar and personal watchlist pages to that report. Reuse publication identities and evidence conventions. Grant opportunities, awarded grants and applications have separate identities; institutional dates and subscriptions are explicit entities. No new Fabric project or mandatory preview/AI service.

## Verified locally

- Grants normalisation, round identity, invalid-date handling and observation snapshots exist in `scripts/grants_registry.py`.
- Institutional date offsets and subscription candidate matching exist in `scripts/grants_planning.py`. These are reference logic, not hosted services.
- G01–G08 specification/plan files exist. They are not completed deployments.
- G06 native progress advanced in isolated DEV: the `Grant Relationships` list exists at the personal DEV SharePoint site, and authenticated list readback confirmed all eight canonical fields (`RelationshipKey`, `RelationshipType`, `FromKey`, `ToKey`, `AwardID`, `EvidenceURL`, `Confidence`, `ReviewStatus`). `RelationshipKey` is required, unique and indexed. Remaining required-field readback, relationship round-trip and unchanged publication-total readback remain open; no production binding has been made.
- Latest canonical-clone harness: 393 tests (8 private-runtime tests skipped), 438 project checks, Conductor validation, web-first local validation and Power Platform tooling preflight passed. The live CKAN DoRA activity collector retrieved 442/442 rows with all 19 source fields plus the datastore `_id` key and 442 unique source `_id` values; scalar/non-boolean source-identity validation is covered locally. G02 now rejects non-string source IDs, future verification dates, non-string catalogue URLs, malformed optional descriptive fields, missing or non-distinct row-level evidence URLs, malformed ARC evidence URLs and missing eligibility statements; G04 validates API source field types before normalization, applies a shared typed-input boundary, and rejects malformed non-object source batches; G06 rejects malformed relationship identities and evidence fields and declares the tracked `RelationshipKey` unique; G07 rejects string-shaped reconciliation field allowlists and now canonicalizes selected fields while reconciling selected registry values as well as exact key sets; G08 rejects non-string policy identity/effective-date fields, opportunity/category/funder identities, duplicate holiday dates and malformed subscription rules. Source-only CI is now declared and structurally tested. This is source/readback evidence, not tenant acceptance.
- E07 local review fix: publication create/update actions are now required to use SharePoint Online and target the same site/list as lookup; native flow/list acceptance remains open.
- S02 local review fix: release manifests now reject empty schema and accepted-batch identities; native report version/batch display remains open.
- S02 version hardening: commit `42b3c91` rejects non-string release versions through the explicit validation boundary; focused package tests pass (5). Native report version/batch display and rollback remain open.
- Source-only CI correction: GitHub Actions run `35527515725` exposed a UTC-versus-Brisbane freshness-date failure in G02; commit `c00560f` switched the guard to `Australia/Brisbane`, added regression coverage, and run `35527622183` passed. This proves source-only CI only; it does not prove tenant acceptance.
- G07 identity hardening: commit `42833c6` rejects non-string source/opportunity identities without coercion and safely quarantines unhashable keys; focused operations tests pass (13), and the current full suite is 374 tests with 8 skips. Native monitoring, reconciliation, scheduling and delivery remain open.
- G08 delivery-key hardening: commit `b84cae8` rejects coercible delivery identities and out-of-range reminder offsets; focused planning/relationship tests pass (14), and the current full suite is 374 tests with 8 skips. Native pages, private preferences and notification delivery remain open.
- G08 policy hardening: commit `1a5fed0` rejects non-object policies and non-string/invalid holiday inputs without incidental type errors; combined planning/relationship tests pass (25), and the current full suite is 374 tests with 8 skips. Native policy persistence and delivery remain open.
- T14 local export-fidelity execution: commit `52c587d` records 64 web-first export-policy tests plus 5 publication-batch contract tests covering multi-page, Unicode, DORA-only, formula-safety, key reconciliation and uncertain-date cases. The next executable T14 step is a correlated native refresh/export readback; native cycle, replay and delivery remain open.
- E01 flow hardening: commit `22b5df1` adds an exact-one-match update guard so duplicate publication keys cannot write; focused publication-contract tests pass (17, with 8 private-package cases skipped) plus `validate_publication_platform_contract.py`. The corrected definition requires native re-import/readback; flow replay, reconciliation and schedule acceptance remain open.
- G05 catalogue hardening: commit `aa0c9ab` rejects non-object university rows, non-string institution identities and future `last_verified` dates using Australia/Brisbane date semantics; focused university tests pass (7), and the current full suite is 374 tests with 8 skips. Institutional feed/export and authenticated portal acceptance remain open.
- G02 reviewed-import hardening: commit `0a5fc92` rejects non-typed reviewer identities, URLs, review status/notes and source-or-round IDs without coercion; focused reviewed-import tests pass (5), and the current full suite is 374 tests with 8 skips. A real reviewed current row or permitted feed/API remains required.
- G02 ARC adapter hardening: commit `03568d7` rejects malformed award identities, evidence links and descriptive fields without coercion; focused ARC tests pass (4). ARC remains awards-only; a permitted opportunity feed/API or reviewed current row remains required.
- G02 row provenance: commit `e62b6f5` preserves actionable HTML calendar row links as explicit `SourceLinks`/`SourceRowURL` fields, with ambiguous links withheld from automatic evidence; focused calendar tests pass (6). Permitted intake and eligibility review remain open.
- G04 ingestion hardening: commit `213a704` rejects non-string source identities, URLs, titles and opportunity keys without coercion; focused ingestion tests pass (18), and the current full suite is 374 tests with 8 skips. Live feed permissions, SharePoint writes and unattended operation remain open.
- G03 flow hardening: commit `054aa2e` adds an exact-one-match update guard so duplicate SharePoint lookup rows cannot reach create/update actions; focused flow/package tests pass (8). The corrected definition still requires isolated native re-import/readback; organisation-wide binding and unattended acceptance remain open.
- G02 local review fix: source catalogues now require valid HTTP(S) authority/API URLs, scalar source IDs, non-future ISO verification dates and explicit source uncertainty; unverified intake status remains explicit.
- G05 local review fix: university catalogues now reject boolean lead times, malformed authority URLs and invalid verification dates; unknown institutional lead times remain null.
- G04 local review fix: RSS/Atom and API-shaped records now share required title, HTTP(S) URL, stable key and timezone-aware retrieval validation before batch acceptance; malformed non-object batches now fail closed explicitly.
- G08 calendar/watchlist hardening: commit `e03f17d` rejects non-string exact-date calendar identities, URLs and display fields without coercion; focused calendar tests pass (6), and watchlist matching rejects non-string identities and malformed subscription objects. Native pages, calendar persistence and delivery remain open.
- G07 operational hardening: commit `994dc05` adds exact emitted-to-registry key-set reconciliation and preserves prior accepted records on malformed, duplicate or mismatched readback; focused relationship/operations tests pass (18), and native monitoring, reconciliation, scheduling and delivery remain open.
- G06 relationship hardening: commit `8cf6b4f` rejects non-string relationship identities, evidence URLs, AwardID, confidence and review status without coercion; focused relationship tests pass (15), and the current full suite is 374 tests with 8 skips. Native relationship round-trip and approved target acceptance remain open.
- T11 retention hardening: commit `4c33b40` adds generator-level coverage for every paged source's readback/keyset checks and staging-only boundary; native application, processed-model readback and report integration remain open.
- The 2026-09-21 Conductor review refresh normalised Summary/Verification Checks/Findings evidence across the active grant reviews and updated stale test counts; G04 now fails closed for titleless or unbound RSS/Atom entries. Active tracks remain open where native, source-permission or operational evidence is absent.
- Canonical bootstrap verification: `.agents/plugins/conductor` is initialized at pinned commit `6e8f9a8` (`conductor-v0.4.1-18-g6e8f9a8`), matching upstream `gemini-cli-extensions/conductor` `HEAD`; no submodule pin change was needed.

## Remaining implementation

Current tranche: S01.2 evidence-preserving attribution, S01.3.1–S01.3.5 local flow/field contracts and the fail-closed paged-batch contract are implemented and tested. S01.1 native page inventory is refreshed; native paged-flow readback and explicit contract migration remain open. T11 preserves the linked Queensland Open Data DoRA activity resource as a separate local RIMS registry; its source `_id` identity, all 19 source fields and provenance are locally verified, while native list creation/readback remains open. Grant local foundations cover archived G01 contracts, G02 source/access catalogue plus bounded authority probing, G03 isolated SharePoint list and reviewed-import flow readback, G04 RSS/Atom/API-shaped ingestion, G05 university access/lead-time catalogue, G06 typed relationships, G07 fail-closed run evaluation and G08 policy/subscription idempotency plus a local seven-page grants report surface. The native report still has four pages; grants organisation-wide target, native pages, permissions, relationships, delivery, and unattended acceptance remain open. The next executable source step is a bounded reviewed-import or permitted-feed decision for G02/G04; the next native step is an approved target/model route for the outstanding list and report gates. Planning or local completion is not remote/platform completion.

S03 remote status: the existing GitHub repository is private and contains only
the reviewed source-only `main` history. The canonical remote is aligned with
the latest source-evidence, review and remaining-track-audit corrections. The dirty original
history remains private and was not pushed; a fresh local canonical clone is
the synchronized authoring/reference checkout for this tranche.

S02 local status: the release packager now produces only a source archive after a clean-tree gate, with independent software/schema/batch identities and fresh-extraction checks. A clean canonical clone produced and verified a source-only `0.3.0-rc1` preview with no Git history/private runtime and `NativeAcceptance=false`; the dirty authoring checkout has not produced an accepted release. The local PBIP now includes a model-backed `ReleaseMetadata` table and software/batch cards; native SharePoint/model/report version-history and report version/batch readback remain open.

Power Platform tooling decision: the local preflight detects PAC 2.12.2, Azure
CLI/Azure DevOps, PowerShell and GitHub CLI, but no Dataverse solution project.
Build Tools 2.0 and `microsoft/powerplatform-actions` are therefore retained as
conditional future routes for an isolated solution. The deprecated
PowerApps Test Engine is not adopted for this PBIP/SharePoint system; current
Power BI/SharePoint acceptance remains native browser/readback based.

Institutional lead times, holiday coverage and reminder delivery policies are not established by the example calculations. Source pages were researched; automated collectors and authenticated endpoints have not been accepted. GrantConnect returned HTTP 403 to the research fetch; that is not proof of tenant browser failure.

## Conflicts and known limits

- Historical publication tracks claim completion while acceptance documents retain open gates. Confirm current tenant receipts before repeating those claims.
- Three-page publication contracts coexist with a four-page dashboard definition. Funding pages are now requested, but native page inventory and explicit contract migration remain outstanding.
- Publication flow package checks use strings and do not prove executable action graphs, concurrency or live list writes.
- Organisation matching includes generic aliases and inferred validity dates; do not use it as confirmed institutional evidence until corrected.
- Organisation matching and leadership attribution corrections from S01.2 are local-only until a native schema/readback confirms the corresponding fields and any backfill is reviewed.
- Native grants pages, list/schema changes, subscriptions, calendar feeds and notification delivery have not been proved.
- An earlier 2026-09-20 Playwright snapshot recorded the pre-repair `int('COMMIT_VALIDATION_FAILED')` failure and an unapproved `eHealth-comm-test` site with no matching list. That snapshot is superseded for flow execution by the current evidence below; it remains relevant only as historical evidence that no write was attempted to that unapproved site.
- The second listed flow, `CHHHS Publications - DEV manual ingestion validation`, was initially observed Off and its details page exposed only the owner-facing Power BI connection summary; action-level run readback was required to determine its SharePoint target.
- Current Playwright platform tests corrected that earlier incomplete reading: the manual-ingestion flow was temporarily enabled, run, and restored Off. Its current run succeeded through Power BI query, SharePoint `Get items`, `Condition Is New Publication`, and the True-branch `SharePoint Create item`; the False-branch update was skipped for the new row. The SharePoint action read back HTTP 200 from the `Publication Registry` list with the expected publication columns. The active history-commit flow also passed every action after its text-typed failure branches were repaired; Flow Checker read back 0 errors and 0 warnings. Full private receipt: `private/ops/2026-09-20-powerautomate-publication-flow-tests.json`.
- Native read-only Power BI report inventory on 2026-09-20 confirmed four current research pages, including Clinical Analytics (`ReportSection4`). The web-first execution contract now matches that observed four-page scope; frozen runtime hashes were not regenerated. Receipt: `private/ops/2026-09-20-powerbi-report-page-inventory.json`.
- S02.3.2 versioning observation on 2026-09-20 confirmed SharePoint item history enabled for the DEV `Publication Registry` list with 500 versions. Power BI report readback exposed Save a copy/Download but no version-history control; the attempted model URL was unavailable. Receipt: `private/ops/2026-09-20-versioning-capability-observation.json`. S02.3.4 remains pending until the isolated report route is readable and a version/batch display can be saved and reloaded.
- G03 native list inventory and subsequent isolated readback now evidence the personal DEV `Grants Registry` with versioning, required/indexed/unique `OpportunityKey`, and controlled synthetic create/update/duplicate/concurrency behavior. The flow was restored Off; the organisation-wide target identity and unattended acceptance remain required.
- G07 local operational evaluation now also rejects missing source health and records from unreported sources while preserving the last accepted batch; native monitoring, reconciliation, scheduling and delivery remain open.
- G08 local iCalendar projection now rejects duplicate event UIDs before emission; native funding pages, personal subscriptions, reminder ledger and calendar delivery remain open.
- G05 university catalogue validation now rejects malformed known lead-time objects while preserving unknown lead times as null; institutional feed/export and authenticated portal acceptance remain open.
- G08 policy validation now rejects reversed effective ranges and malformed or duplicate holiday dates before institutional calendar projection; native pages and delivery remain open.
- Historical controlled replay `08584117040588468458780027430CU06` succeeded through `Create item` and skipped `Update item`; its blank-`SourceKey` observation predates the corrected rows query and is retained only as historical evidence. The corrected package now rejects blank canonical keys and derives a stable `SourceKey`; native replay/update and unattended acceptance remain open. The flow was restored Off.
- Local remediation now separates the Power BI readiness summary from the publication rows consumed by the SharePoint loop. The corrected package projects the canonical `Publication` table, derives `pubmed:<PMID>` or `dora:<CanonicalKey>`, rejects blank canonical keys, and is covered by the structural contract. The package has been imported and read back on the retained DEV flow; actual data execution and unattended acceptance remain unproved.
- The corrected package was imported and read back on the retained canonical DEV scheduled-flow identity. Both Power BI actions use the same isolated model, with chain `Recurrence -> readiness -> publication rows -> Apply to each Publication`; Flow Checker reads 0 errors/0 warnings and the flow is Disabled. The redundant disabled manual duplicate was removed so the platform now has one canonical flow. An actual recurrence run, replay/update readback and schedule acceptance remain gated on explicit activation approval.
- Latest native readback on 2026-09-20 supersedes the earlier zero-warning import snapshot for current operational status: the retained canonical flow is Off; Flow Checker reads 0 errors and 1 inactive-flow warning; visible 28-day history reads 2 succeeded, 1 test-failed and 3 failed runs. No edit, enable, run, list write or schedule activation was performed. This is not unattended or recurrence acceptance. The authenticated `eHealth-comm-test` SharePoint Site Contents page also did not expose `Publication Registry`, `Grants Registry` or `DORA Activity Registry`; no list was created there because it is not an approved grants target. Receipt: `private/ops/2026-09-20-powerautomate-publication-flow-tests.json`.
- G02/G05 source verification advanced on 2026-09-20 with fresh bounded read-only probes: 10/14 federal and Queensland authority pages returned HTTP 200 and 4/14 returned HTTP 403; university routes returned UQ HTTP 200 and JCU/QUT/Griffith HTTP 403. No result was promoted to a feed, API or unattended collector. Receipts: ignored `private/ops/2026-09-20-grants-source-probe-current.json` and `private/ops/2026-09-20-grants-university-probe-current.json`. G02/G05 remain open for permitted feed/export or reviewed-import evidence.
- G02 now has a local fail-closed reviewed-import route in `scripts/grants_reviewed_import.py`: reviewed rows require source/row identity, an HTTP(S) row URL, timezone-aware observation time, review notes and `ReviewStatus=Reviewed`; any invalid row rejects the batch. The 33 grants-focused tests and 438 project checks pass. This prepares manual/reviewed imports but does not invent or approve current opportunities; permitted source export or human-reviewed source rows remain required.
- The review-only NHMRC/MRFF HTML adapter now also preserves each complete observed source row in `SourceColumns` for later human review; candidates remain `Needs Review` and are not admitted automatically.
- A review-only HTML calendar adapter now parses bounded NHMRC and MRFF calendar tables into `Needs Review` candidates while preserving raw deadline text. A read-only probe observed HTTP 200 and extracted 13 NHMRC plus 179 MRFF candidates after repeated-header suppression; it did not admit rows, create tenant objects, or activate intake. Receipt: ignored `private/ops/2026-09-20-grants-html-calendar-readback.json`. Unattended feeds/APIs, row-level source links, eligibility review and native acceptance remain open.
- G04 ingestion now rejects duplicate non-empty RSS/Atom source identities before candidate emission and preserves the existing failed-source isolation contract. Focused ingestion tests pass; live source-to-list execution remains open.
- G04 RSS/Atom ingestion also rejects titleless entries before registry emission, matching the required SharePoint Title field; live source/list/flow acceptance remains open.
- G04 RSS/Atom ingestion now also rejects entries lacking both a source identifier and URL, preventing weak title/funder fallback identities; live source/list/flow acceptance remains open.
- The 2026-09-21 bounded adapter exercise repeated those official calendar reads and again produced 13 NHMRC and 179 MRFF candidates. The source catalogue dates for NHMRC, MRFF, ARC and Queensland Grants Finder now reflect that verification date; candidates remain review-gated.
- The Queensland Government Grants Finder CKAN `package_show` API also returned HTTP 200 and valid JSON, but its verified package contains contribution-resource metadata rather than opportunity rows. It is catalogued as `metadata_only`, not promoted to an opportunity feed. Receipt: ignored `private/ops/2026-09-20-queensland-grants-finder-api-readback.json`.
- A fresh authenticated SharePoint Site Contents readback on 2026-09-20 found no approved organisation-wide `Publication Registry`, `Grants Registry` or `DORA Activity Registry` on `eHealth-comm-test`; the isolated personal DEV lists are a separate target and are not production acceptance. The organisation-wide target identity remains gated.
- G03 isolated DEV progress: the canonical flow action readback identified the existing personal SharePoint DEV site as the SharePoint list target, distinct from OneDrive file actions. A `Grants Registry` list was created there with versioning enabled (50 major versions), 21 custom fields and unique/indexed/required `OpportunityKey`. Synthetic create/read/update/duplicate/delete readback succeeded with zero fixture rows remaining. Receipt: ignored `private/ops/2026-09-20-grants-native-g03-receipt.json`. Organisation-wide target approval, grants-flow binding and unattended acceptance remain open.
- The G03 list-level concurrency check returned one `201` and one `500` `SPDuplicateValuesFoundException` for simultaneous identical keys; one row was read back and removed, leaving zero fixture rows. This is isolated DEV evidence only.
- A local canonical grants flow definition now exists at `config/flows/grants-registry-reviewed-import.definition.json`: manual reviewed-row JSON input, SharePoint-only upsert, serial loop, duplicate-key diagnostic, exact-zero-match write guard and review-field preservation. The flow was imported and read back in the isolated DEV environment as Off with Flow Checker 0 errors/0 warnings in the editor. The native diagnostic expression was corrected, and authenticated synthetic create and same-key update runs succeeded before the flow was restored Off. A nested native `Terminate` remains intentionally excluded because Power Automate rejects it inside `Apply to each`; unattended and organisation-wide acceptance remain open. Receipt: ignored `private/ops/2026-09-20-grants-flow-import-readback.json`.
- The earlier 2026-09-20 automation/authentication bridge interruption is superseded for execution by the authenticated 2026-09-21 create/update replay. The synthetic row remains pending explicit deletion confirmation; no production, schedule, notification or organisation-wide target was touched.
- The canonical publication flow’s `SharePoint Get items` action was independently read back as SharePoint Online targeting the personal DEV `Publication Registry` list; OneDrive is confined to the separate source-archive action. Receipt: ignored `private/ops/2026-09-20-publication-flow-target-readback.json`.
- The isolated Power BI authoring route was rechecked for E04 using the recoverable development report/model evidence. The report route returned “Failed to get access request info for this artifact” and redirected home; the workspace model-view entry then bootstrapped the original model ID inside its iframe and failed with module MIME errors/`NG04002`. No model/report mutation was attempted. This is an isolated-route access/readback blocker, not permission to edit the original report/model.
- E04 local visual validation now also audits PBIR `Column`/`Measure` references against the local semantic-model TMDL and fails closed for unresolved bindings. All current local bindings resolve; this is a preventive package check only and does not overturn the native Clinical Analytics field-binding errors.
- Canonical flow validation now has standalone publication and grants validators (`scripts/validate_publication_platform_contract.py` and `scripts/validate_grants_flow_contract.py`) wired into source-only CI. Both tracked definitions pass locally; this proves structural contracts only, not connector permissions, native import, live runs or scheduling.
- The grants validator also inspects generated private grants packages when present, so a package cannot drift from its tracked SharePoint-only contract before import (`0bb59fb`).
- Reviewed grants imports now preserve and require distinct `SourceRowURL` evidence plus an explicit `Eligibility` statement; the field is carried through the schema, semantic model and SharePoint flow mapping. This remains a review gate, not an eligibility decision or native acceptance.

## Working rules

Track audit correction (2026-09-21): E02, E03, E05 and E06 passed local Conductor review and were archived with explicit native/platform boundaries. E04 was reopened because current evidence proves local visual geometry/contrast only, not the claimed production-report audit against the current four-page native scope.

Current replay correction (2026-09-21): authenticated `playwright-cli -s=login` proved controlled native grants execution. Run `08584116923018304855211342755CU17` succeeded for a synthetic create and run `08584116920125684835586408484CU25` succeeded for a same-key update. SharePoint readback showed the expected row and then changed title, funder, amount, timestamp and evidence hash. The flow was restored Off. The synthetic row remains pending explicit deletion confirmation; no production, schedule, notification or organisation-wide target was touched. Receipt: ignored `private/ops/2026-09-20-grants-flow-import-readback.json`.

Remaining-track audit (2026-09-21): `conductor/REMAINING_TRACK_AUDIT_2026-09-21.md` records each active track, evidence, remaining gate and non-archive decision. No active track is represented as complete while its native/source/operational acceptance gate remains open.

Latest local checkpoint (2026-09-21): DoRA activity export provenance was
hardened in code commit `93d2ac6`; malformed retrieved counts, observation
timestamps, resource IDs/URLs and structured activity-key inputs now fail closed.
Focused DoRA tests pass. The full canonical-clone harness passes with 392 tests
(8 skipped), 438 project checks, Conductor validation with 0 errors, web-first
`PASS_LOCAL_ONLY`, Power Platform tooling preflight, visual standards and
`git diff --check`. Documentation records the review separately. Native DoRA
SharePoint schema/row readback, report integration and unattended flow
acceptance remain open; this is not a tenant acceptance claim.

Follow-up local checkpoint (2026-09-21): DoRA export provenance now also
requires a valid HTTP(S) resource URL and timezone-aware ISO-8601 observation
time. Code commit `2c58a93`; focused DoRA tests pass (9), full suite passes
with 394 tests and 8 skips, and the 438 project checks plus Conductor/web-first,
Power Platform and visual checks remain green. The canonical clone is ready for
remote synchronization after the review documentation commit. Native
SharePoint/report integration and unattended acceptance remain open.

Latest local DoRA hardening (2026-09-21): code commit `df9abeb` requires the
receipt's expected and retrieved counts to reconcile before export; focused DoRA
coverage is now 10 tests. The next full checkpoint must re-run the repository
harness before the review documentation is finalized. Native SharePoint,
report and unattended-flow gates remain open.

Latest local DoRA hardening (2026-09-21): code commit `bdb1303` verifies
present receipt hashes for the canonical activity records and source identity
set before export. Focused DoRA coverage is now 11 tests; the full suite is 395
tests with 8 skips, with 438 project checks and structural/native-boundary
checks passing locally. Native SharePoint, report and unattended-flow gates
remain open.

Latest grants-calendar hardening (2026-09-21): code commit `29d97cf` validates
descriptive field types before uncertain-date omission, preventing malformed
calendar inputs from disappearing silently. Focused calendar coverage is 7
tests; the full suite is 396 tests with 8 skips and the 438 project checks
remain green. Native grants pages, watchlist persistence, calendar delivery and
notification gates remain open.

Latest grants-calendar hardening (2026-09-21): code commit `01231b6` rejects
impossible dates for day-precision deadlines before event projection. Focused
calendar coverage is now 8 tests; the full suite is 397 tests with 8 skips and
438 project checks remain green. Native grants pages, watchlist persistence,
calendar delivery and notification gates remain open.

Latest grants-planning hardening (2026-09-21): code commit `6ca91b0` rejects
malformed holiday collection shapes explicitly during institutional deadline
projection. Focused planning coverage is 12 tests; the full suite remains 397
tests with 8 skips and 438 project checks remain green. Native policy
persistence, grants pages, calendar delivery and notifications remain open.

Latest grants-planning hardening (2026-09-21): code commit `a0c8d06` rejects
malformed subscription containers before matching rules. Focused planning
coverage remains 12 tests; the full suite remains 397 tests with 8 skips and
438 project checks remain green. Native preference persistence, grants pages,
calendar delivery and notifications remain open.

Latest T11 local implementation (2026-09-21): code commit `6930271` adds the
canonical DoRA Activity Registry SharePoint-only upsert definition, a standalone
validator, four focused flow-contract tests and a CI gate. The full suite now
passes 401 tests with 8 skips; 438 project checks and all three canonical flow
validators pass. This is a local structural contract only: approved target
identity, native import, complete list readback, report integration and
unattended execution remain open.

Latest T11 bootstrap (2026-09-21): code commit `3c8edd1` adds the sole private
DoRA flow-package builder, with HTTPS/GUID/placeholder guards and package tests.
No tenant-specific package was generated or imported. The full suite now passes
403 tests with 8 skips; native target, import, list/readback and unattended
execution remain open.

Latest T11 package guard (2026-09-21): code commit `c9430cd` validates the
target-injected DoRA flow definition before writing a package and rejects
definition drift. The full suite now passes 404 tests with 8 skips; native
target, import, list/readback, report integration and unattended execution
remain open.

Latest T11 identity hardening (2026-09-21): code commit `538977e` declares
`DORAActivityKey` unique in the canonical DoRA Activity Registry schema and adds
a regression assertion. Focused DoRA tests pass (11); the full suite passes 404
tests with 8 skips, 438 project checks pass, and Conductor, web-first,
Power Platform and visual checks remain green locally. This is a schema-level
contract improvement only: native list uniqueness/readback, report integration
and unattended flow acceptance remain open. The next executable task is to use
an approved target identity for native list import/readback; no tenant mutation
was made in this checkpoint.

Latest T11 flow/schema coupling (2026-09-21): code commit `5af36f6` makes the
DoRA flow validator load the canonical registry schema and reject any definition
whose `DORAActivityKey` is not unique. Focused flow-contract coverage is now 5
tests; the full suite passes 405 tests with 8 skips, 438 project checks pass,
and Conductor, web-first, Power Platform and visual checks remain green locally.
This remains local structural evidence only; native list schema/readback,
report integration and unattended execution remain open. The browser bridge
still exposes Microsoft sign-in rather than an attachable authenticated
Power Automate session, so no tenant mutation was made.

Latest G03 flow/schema coupling (2026-09-21): code commit `192c53e` makes the
grants flow validator load the canonical registry schema and reject any
definition whose `OpportunityKey` is not unique. Focused grants flow coverage is
now 9 tests; the full suite passes 406 tests with 8 skips, 438 project checks
pass, and Conductor, web-first, Power Platform, visual and both canonical flow
validators remain green locally. The approved organisation-wide target, native
readback and unattended operation remain open; no tenant mutation was made.

Latest E01 publication target coupling (2026-09-21): code commit `71912c7`
declares `source_key` as the sole unique field in the publication target
template and makes the private package builder reject targets without that
invariant. Focused publication-platform coverage is 18 tests (8 private-package
tests skipped when ignored live artefacts are absent); the full suite passes 407
tests with 8 skips and 438 project checks remain green. Native uniqueness/schema
readback, replay/update, reconciliation and unattended scheduling remain open;
no tenant mutation was made.

The publication SharePoint architecture documentation was aligned with that
contract: `SourceKey` is now described as both indexed and unique, with
duplicate rejection required at the list boundary. This is documentation
alignment, not native schema evidence; the S02 report version/batch display and
all remaining native publication acceptance gates remain open.

Latest T11 DoRA model hardening (2026-09-21): code commit `e77be2f` makes
`config/DoraActivityRegistry.m` reject duplicate nonblank `DORAActivityKey`
values instead of silently returning them. Focused DoRA coverage is now 12
tests; the full suite passes 408 tests with 8 skips, 438 project checks pass,
and Conductor, web-first, Power Platform, visual and canonical flow checks are
green locally. Native DoRA list schema/readback, report integration and
unattended flow acceptance remain open; no tenant mutation was made.

Latest T11 DoRA projection parity (2026-09-21): code commit `1bacdea` adds an
exact schema-to-`DoraActivityRegistry.m` projection test, so every canonical
registry field must remain selected by the model query. Focused DoRA coverage
is now 13 tests; the full suite passes 409 tests with 8 skips and 438 project
checks remain green. Native list/readback, report integration and unattended
flow acceptance remain open; no tenant mutation was made.

Latest T11 DoRA flow mapping lock (2026-09-21): code commit `d82a19d` makes the
flow validator require an exact match between canonical schema fields and the
SharePoint create/update mapping set. Focused flow-contract coverage is now 6
tests; the full suite passes 410 tests with 8 skips, 438 project checks pass,
and Conductor, web-first, Power Platform, visual and canonical flow checks are
green locally. Native list/readback, report integration and unattended flow
acceptance remain open; no tenant mutation was made.

Latest G03 grants mapping lock (2026-09-21): code commit `bdf17b2` makes the
grants flow validator require the SharePoint create mapping to match every
canonical `Grants Registry` schema field. Focused grants flow coverage is now 10
tests; the full suite passes 411 tests with 8 skips, 438 project checks pass,
and Conductor, web-first, Power Platform, visual and canonical flow checks are
green locally. Native target/readback, canonical binding and unattended
execution remain open; no tenant mutation was made.

Latest T11 DoRA fail-closed projection (2026-09-21): code commit `205e561`
changes `DoraActivityRegistry.m` to reject missing SharePoint columns rather
than replacing them with nulls. Focused DoRA coverage is now 14 tests; the full
suite passes 412 tests with 8 skips, 438 project checks pass, and Conductor,
web-first, Power Platform, visual and canonical flow checks remain green
locally. Native list/readback, report integration and unattended flow
acceptance remain open; no tenant mutation was made.

Latest E01 publication fail-closed projection (2026-09-21): code commit
`a1d3305` changes `SharePointPublicationRegistry.m` to reject missing registry
columns rather than replacing them with nulls. The full suite passes 413 tests
with 8 skips, 438 project checks pass, and Conductor, web-first, Power Platform,
visual and canonical flow checks remain green locally. Native publication list
schema/readback, complete reconciliation and unattended execution remain open;
no tenant mutation was made.

Native access recheck (2026-09-21): read-only PAC/Azure discovery does not reach
the CHHHS Power Platform tenant. The active PAC profile is an unrelated
environment and its environment listing fails with an Entra account-deleted
directory error; the active Azure profile is also a different tenant. No
tenant-switch, sign-in, deployment or write was attempted. This is the current
blocker for S02.3.4 and the remaining native SharePoint, Power BI and
Power Automate acceptance gates.

Latest E01 package-binding hardening (2026-09-21): code commit `996d1f3`
corrects the publication SharePoint package builder so the lookup `$filter`
uses the configured `source_key` internal field mapping rather than hardcoded
`field_1`. A synthetic package test covers a custom mapping; the full suite
passes 414 tests with 8 skips, 438 project checks pass, and Conductor,
web-first, Power Platform, visual and canonical flow checks remain green
locally. Native import/readback, replay/update, reconciliation and unattended
execution remain open; no tenant mutation was made. Next executable task is
native E01 replay/readback once an authorised CHHHS tenant session is
available.

Resumed native-access recheck (2026-09-21): `playwright-cli` reports that the
`chrome` and `login` sessions are not open. PAC remains on the unrelated NSW
environment and Azure remains on the unrelated Flinders tenant. No sign-in,
tenant switch, deployment or write was attempted. Native Power Automate,
SharePoint and Power BI gates remain open pending an authorised CHHHS session;
the canonical local source and remote `main` remain synchronised.

Latest G02/G04 source-catalogue hardening (2026-09-21): code commit
`232025a` rejects leading or trailing whitespace in grant `source_id` values,
preventing a trimmed duplicate-check identity from diverging from the value
sent to ingestion and source-health reconciliation. Focused source-ingestion
coverage is 21 tests; the full suite passes 415 tests with 8 skips, 438
project checks pass, and Conductor, web-first, Power Platform, visual and
canonical flow validators pass locally. Permitted live opportunity intake,
controlled source-to-list reconciliation, native acceptance and unattended
operation remain open; no tenant mutation was made.

Latest G07 operational hardening (2026-09-21): code commit `206588c` makes
batch duplicate detection compare normalized trimmed `OpportunityKey` values,
closing a whitespace-variant identity gap before registry reconciliation.
Focused relationship/operations coverage is 21 tests; the full suite passes
416 tests with 8 skips, 438 project checks pass, and Conductor, web-first,
Power Platform, visual and canonical flow validators pass locally. Native
monitoring, list readback, operational reconciliation, scheduling and delivery
remain open; no tenant mutation was made.

Latest T11 DoRA package-boundary hardening (2026-09-21): code commit `44b6242`
rejects non-string DoRA SharePoint package target parameters before URL/GUID
handling. The full suite passes 421 tests with 8 skips, 438 project checks
pass, and Conductor, web-first, Power Platform, visual and canonical flow
validators pass locally. Native DoRA list schema/readback, report integration,
execution and unattended delivery remain open; no tenant mutation was made.

Latest G03 package-boundary hardening (2026-09-21): code commit `96c5bc7`
rejects non-string grants package target parameters before URL/GUID handling,
so malformed tenant-specific inputs fail through the explicit validation
contract. The full suite passes 418 tests with 8 skips, 438 project checks
pass, and Conductor, web-first, Power Platform, visual and canonical flow
validators pass locally. Native target approval, import/readback, canonical
binding, unattended execution and delivery remain open; no tenant mutation was
made.

Latest G05 university-catalogue hardening (2026-09-21): code commit `efc0dfe`
rejects leading or trailing whitespace in `institution_id` values, preventing
identity drift between duplicate detection and downstream organisation
enrichment. Focused university coverage is 8 tests; the full suite passes 420
tests with 8 skips, 438 project checks pass, and Conductor, web-first, Power
Platform, visual and canonical flow validators pass locally. Permitted
institutional exports/feeds, authenticated portal access and native acceptance
remain open; no tenant mutation was made.

Latest G08 calendar hardening (2026-09-21): code commit `f4b44ac` validates
the semantic value of the iCalendar `generated_utc` timestamp, not only its
textual shape, and rejects impossible UTC dates/times. Focused calendar
coverage is 9 tests; the full suite passes 417 tests with 8 skips, 438
project checks pass, and Conductor plus the publication/grants flow
validators pass locally. Native policy/page persistence, subscriptions,
calendar change/delivery and notification acceptance remain open; no tenant
mutation was made.

Latest G08 policy hardening (2026-09-21): code commit `574193d` rejects an
explicitly blank institutional grant-policy `EffectiveTo` while preserving
`null` as the valid open-ended representation. Focused planning coverage is
12 tests; the full suite passes 415 tests with 8 skips, 438 project checks
pass, and Conductor, web-first, Power Platform, visual and canonical flow
validators pass locally. Native policy persistence, grant pages, personal
subscriptions, calendar change/delivery and notification acceptance remain
open; no tenant mutation was made.

Latest E01 target-boundary hardening (2026-09-21): code commit `7a32165`
requires publication SharePoint target identifiers and field mappings to be
strings before trimming, GUID parsing or package generation. The full suite
passes 419 tests with 8 skips, 438 project checks pass, and Conductor,
web-first, Power Platform, visual and canonical flow validators pass locally.
Native publication list schema/readback, replay/update, reconciliation and
unattended execution remain open; no tenant mutation was made.

Inspect `git status --short` at entry. Preserve unrelated report/manifest and other existing edits; do not mass-stage. Use the active track's spec and plan for tasks. Follow AGENTS.md approval boundaries for deployment/sharing/schedules. Current user direction defines scope; historical observations supply evidence only for their dates. Live contradictions require readback, not a convenient choice of document.

Update this checkpoint with outcome, next executable task, test command/result and exact blocker after work. Keep credentials, actual tenant identifiers and screenshots under ignored private storage. Do not paste raw private output into a context bundle.
