# Track register

## Publication stabilisation before grants implementation

Execution order and boundaries: [detailed handoff](PUBLICATION_STABILISATION.md). Existing T11, T14, T15, E01 and E07 own live acceptance; their execution runbooks refine the existing plans.

- [ ] [S01_publication_stabilisation: local defects and report scope](tracks/S01_publication_stabilisation/plan.md) — detailed plan; start here.
- [ ] [S02_release_versioning: reproducible versions and recovery](tracks/S02_release_versioning/plan.md) — detailed plan; requires S01.
- [x] [S03_private_github_sync: sanitised private source synchronisation](tracks/S03_private_github_sync/plan.md) — clean source-only `main` published; native/platform acceptance remains separate.

## Grants extension of CHHHS RIMS

- [~] [G02_grants_sources: Verified federal and Queensland sources](tracks/G02_grants_sources/plan.md) — catalogue implemented; endpoint/feed verification remains open.
- [~] [G03_grants_sharepoint: Canonical grants storage](tracks/G03_grants_sharepoint/plan.md) — local schema/read definition implemented; isolated SharePoint creation/readback remains open.
- [~] [G04_grants_ingestion: Grant source ingestion](tracks/G04_grants_ingestion/plan.md) — local adapters and fail-closed batch handling implemented; live source/list/flow acceptance remains open.
- [~] [G05_grants_universities: University and specialist coverage](tracks/G05_grants_universities/plan.md) — JCU/UQ/QUT/Griffith source/access catalogue implemented; portal/feed verification remains open.
- [~] [G06_grants_relationships: Publication and funding relationships](tracks/G06_grants_relationships/plan.md) — typed local relationship contract implemented; native evidence/readback remains open.
- [~] [G07_grants_operations: Grant operational acceptance](tracks/G07_grants_operations/plan.md) — local fail-closed run evaluator implemented; native cycles/readback remain open.
- [~] [G08_rims_grants_experience: RIMS grant pages, dates and subscriptions](tracks/G08_rims_grants_experience/plan.md) — local policy and subscription contracts implemented; native pages/access/delivery remain open.

## Current web-first implementation

- [x] [T08_web_capability_discovery: Prove the plugin and web UI capabilities](tracks/T08_web_capability_discovery/plan.md) — complete (web-first route and capabilities verified with agy / web UI)
- [x] [T09_execution_contracts: Reconcile context and implement the execution gates](tracks/T09_execution_contracts/plan.md) — complete (local only)
- [x] [T10_isolated_baseline: Protect the existing report and prove an isolated write](tracks/T10_isolated_baseline/plan.md) — complete (isolated canary write and rollback verified)
- [~] [T11_sources_and_reconciliation: Repair and prove PubMed plus DORA ingestion](tracks/T11_sources_and_reconciliation/plan.md) — implementation exists; native/operational acceptance remains open (2026-09-20 audit).
- [x] [T12_research_model: Replace the underlying model, not just its labels](tracks/T12_research_model/plan.md) — complete (canonical reporting model, DAX readback, multi-source integration)
- [x] [T13_web_visuals: Implement the three-page publication report](tracks/T13_web_visuals/plan.md) — complete (36 research-only visuals, three-page scope, legacy cleanup)
- [~] [T14_complete_exports_monthly: Export every citation and stage the monthly workflow](tracks/T14_complete_exports_monthly/plan.md) — implementation exists; native/operational acceptance remains open (2026-09-20 audit).
- [~] [T15_web_acceptance_release: Verify the live web implementation and hand over](tracks/T15_web_acceptance_release/plan.md) — implementation exists; native/operational acceptance remains open (2026-09-20 audit).
- [ ] [T16_utm_windows_fallback: Finish the existing UTM Windows VM only if needed](tracks/T16_utm_windows_fallback/plan.md) — gated (conditional fallback)
- [ ] [T17_desktop_fallback_acceptance: Author and save a native PBIX in the Windows VM](tracks/T17_desktop_fallback_acceptance/plan.md) — gated (conditional fallback)

## Historical local implementation
- [x] [T01 legacy audit](tracks/T01_legacy_audit/plan.md)
- [x] [T02 source model](tracks/T02_research_model/plan.md)
- [x] [T03 initial report definitions](tracks/T03_research_report/plan.md) — later superseded by three-page scope.
- [x] [T04 local regression/handover](tracks/T04_regression_handover/plan.md)
- [x] [T06 two-source definitions](tracks/T06_browser_two_source/plan.md) — local source only; runtime defects remain.

## Superseded routes, not completed deployments
[T05 native acceptance](tracks/T05_native_acceptance/plan.md) is consolidated into conditional T17.
[T07 Fabric Git acceptance](tracks/T07_fabric_live_acceptance/plan.md) is retired.

## Multi-source enrichment extension
- [x] [Multi-source enrichment and deduplication](../docs/FUTURE_SOURCE_ENRICHMENT.md) — completed (OpenAlex, Crossref, Dimensions, Scopus, Web of Science, ARDC RLA integrated into registry, enrichment pipeline, and seed datasets).
- [x] [Keyless & Token-Free Enrichment Plan](../docs/KEYLESS_ENRICHMENT_PLAN.md) — active policy (strict zero-key/zero-token rule; only OpenAlex polite-pool, Crossref polite-pool, PubMed E-Utilities, and internal deterministic governance classifiers; proprietary paywalled APIs excluded).

## Platform completion roadmap (separation of concerns)
- [x] [Phase 1: Central Research Data Persistence & Review (SharePoint List)](../docs/PLATFORM_COMPLETION_PLAN.md#phase-1-sharepoint-publication-registry-highest-value) — **Highest Value** (historical synchronization evidence; live readback and current reconciliation remain gated)
- [x] [Phase 2: Automated Cloud Ingestion & Daily Enrichment (Power Automate)](../docs/PLATFORM_COMPLETION_PLAN.md#phase-2-power-automate-daily-ingestion--enrichment-high-value) — **High Value** (flow package and target identity prepared; end-to-end replay, concurrency, and unattended acceptance remain gated)
- [x] [Phase 3: Executive Monthly Word Reporting (Automation & On-Demand)](../docs/PLATFORM_COMPLETION_PLAN.md#phase-3-executive-monthly-word-reporting-medium-high-value) — **Medium-High Value** (Queensland Health branded monthly executive digests, KPI cards, hospital breakdowns) — **COMPLETED ON PLATFORM**
- [x] [Phase 4: Research Semantic Model & Visual Dashboards (Power BI)](../docs/PLATFORM_COMPLETION_PLAN.md#phase-4-power-bi-semantic-model--research-dashboards-medium-value) — **Medium Value** (TMDL model, DAX reconciliation query check, 3-page research visual suite) — **COMPLETED ON PLATFORM**

## Canonical evolution tracks
- [~] [E01_flow_automation: Power Automate Ingestion Canonicalization and Recurrence Scheduling](tracks/E01_flow_automation/plan.md) — implementation exists; native/operational acceptance remains open (2026-09-20 audit).
- [x] [E02_clinical_analytics: Clinical Directorate Attribution and FoR Classification](tracks/E02_clinical_analytics/plan.md) — complete (Cairns-Led vs Collaborative attribution, ANZSRC 2020 FoR, clinical directorate specialty mapping verified by unit tests)
- [x] [E03_open_access_trials: Open Access Mandate Compliance and Clinical Trial Linkage](tracks/E03_open_access_trials/plan.md) — complete (NHMRC 2022 OA compliance categorization, ANZCTR and ClinicalTrials.gov regex extraction and URL resolution verified by unit tests)
- [x] [E04_fluent_visual_polish: Microsoft Fluent 2 Visual Polishing and IBCS Standards](tracks/E04_fluent_visual_polish/plan.md) — complete (100% of 36 report visuals audited and certified on 8px base grid, WCAG 2.1 AA theme contrast verified)
- [x] [E05_author_registry_consolidation: Derived author registry and attribution evidence](tracks/E05_author_registry_consolidation/plan.md) — complete (local implementation, tests, and documentation)
- [x] [E06_grants_funding_opportunities: Grants and funding opportunities registry MVP](tracks/E06_grants_funding_opportunities/plan.md) — complete locally (canonical schema, RSS/Atom/API-shaped adapters, tests, documentation; platform deployment gated)
- [~] [E07_publication_platform_acceptance: Publication platform hardening and live evidence](tracks/E07_publication_platform_acceptance/plan.md) — local acceptance contract added; tenant readback and end-to-end replay remain gated
