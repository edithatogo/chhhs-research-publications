# Current RIMS checkpoint

Updated: 2026-09-20. This is the compact resumption checkpoint, not a live acceptance certificate. Refresh after meaningful work; keep historical narrative in existing evidence documents.

## Direction

Conductor audit: all track index/spec/plan/metadata files and dependencies validate. T11, T14, T15 and E01 are reopened for outstanding native/operational acceptance; do not treat their historical completion paragraphs as current status. The private GitHub origin contains the source-only canonical history; the dirty local working tree remains the authoring workspace and is not itself the remote release.

One person owns this repository and the existing CHHHS RIMS report. Add funding opportunities, funding calendar and personal watchlist pages to that report. Reuse publication identities and evidence conventions. Grant opportunities, awarded grants and applications have separate identities; institutional dates and subscriptions are explicit entities. No new Fabric project or mandatory preview/AI service.

## Verified locally

- Grants normalisation, round identity, invalid-date handling and observation snapshots exist in `scripts/grants_registry.py`.
- Institutional date offsets and subscription candidate matching exist in `scripts/grants_planning.py`. These are reference logic, not hosted services.
- G01–G08 specification/plan files exist. They are not completed deployments.
- Latest local harness: 291 tests, 438 project checks, Conductor validation, web-first local validation and Power Platform tooling preflight passed. The live CKAN DoRA activity collector retrieved 442/442 rows with all 19 source fields plus the datastore `_id` key and 442 unique source `_id` values; this is source/readback evidence, not tenant acceptance.

## Remaining implementation

Current tranche: S01.2 evidence-preserving attribution, S01.3.1–S01.3.5 local flow/field contracts and the fail-closed paged-batch contract are implemented and tested. S01.1 local baseline/scope comparison is recorded, but native page inventory and native paged-flow readback remain open. T11 now also preserves the linked Queensland Open Data DoRA activity resource as a separate local RIMS registry; its source `_id` identity, all 19 source fields and provenance are locally verified, while native list creation/readback remains open. Grant local foundations now cover archived G01 contracts, G02 source/access catalogue plus bounded authority probing, G03 list schema/read definition, G04 RSS/Atom/API-shaped ingestion, G05 university access/lead-time catalogue, G06 typed relationships, G07 fail-closed run evaluation and G08 policy/subscription idempotency plus a local seven-page grants report surface; all native list, flow, page, permission, relationship and delivery gates remain open. Next executable task: S01.4 contract migration and native acceptance where an authenticated bindable session exists; source-side next step is to verify permitted feed/API routes or produce reviewed imports for G02. Planning or local completion is not remote/platform completion.

S03 remote status: the existing GitHub repository is private and now contains
only the reviewed source-only `main` history. A fresh clone with the pinned
Conductor submodule passed 325 checks and 287 tests (8 private-runtime tests
skipped). The dirty original local
history remains private and was not pushed.

S02 local status: the release packager now produces only a source archive after a clean-tree gate, with independent software/schema/batch identities and fresh-extraction checks. A clean canonical clone at `bb2ec04` produced and verified a source-only `0.3.0-rc1` preview with no Git history/private runtime and `NativeAcceptance=false`; the dirty authoring checkout has not produced an accepted release. The local PBIP now includes a model-backed `ReleaseMetadata` table and software/batch cards; native SharePoint/model/report version-history and report version/batch readback remain open.

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
- G03 native list inventory on 2026-09-20 found only the personal DEV `Publication Registry`; no Grants Registry or DORA Activity Registry was present. No list was created. Receipt: `private/ops/2026-09-20-grants-list-inventory.json`; approved organisation-wide target identity remains required.
- A controlled replay of the manual publication flow (run `08584117040588468458780027430CU06`) again succeeded through `Create item` and skipped `Update item`; the blank SourceKey filter remains an idempotency/duplicate-risk blocker. The flow was restored Off. This is not a production or unattended acceptance certificate.
- Local remediation now separates the Power BI readiness summary from the publication rows consumed by the SharePoint loop. The corrected package projects the canonical `Publication` table, derives `pubmed:<PMID>` or `dora:<CanonicalKey>`, rejects blank canonical keys, and is covered by the structural contract. The package has been imported and read back on the retained DEV flow; actual data execution and unattended acceptance remain unproved.
- The corrected package was imported and read back on the retained canonical DEV scheduled-flow identity. Both Power BI actions use the same isolated model, with chain `Recurrence -> readiness -> publication rows -> Apply to each Publication`; Flow Checker reads 0 errors/0 warnings and the flow is Disabled. The redundant disabled manual duplicate was removed so the platform now has one canonical flow. An actual recurrence run, replay/update readback and schedule acceptance remain gated on explicit activation approval.

## Working rules

Inspect `git status --short` at entry. Preserve unrelated report/manifest and other existing edits; do not mass-stage. Use the active track's spec and plan for tasks. Follow AGENTS.md approval boundaries for deployment/sharing/schedules. Current user direction defines scope; historical observations supply evidence only for their dates. Live contradictions require readback, not a convenient choice of document.

Update this checkpoint with outcome, next executable task, test command/result and exact blocker after work. Keep credentials, actual tenant identifiers and screenshots under ignored private storage. Do not paste raw private output into a context bundle.
