# Deferred source enrichment and reconciliation

Plan amendment requested 2026-09-14. Status: planned, not enabled. This extends the existing Power Platform-native dashboard after the PubMed/DORA foundation is properly set up; it does not delay or replace its acceptance criteria. Keep the existing Power BI workspace, retained storage and three report pages. No new source collection, account registration, access application, purchase or deployment is authorised by this planning amendment.

## Start gate and order

- [ ] Finish T11–T15 foundation: committed retained history, full metadata reconstruction, conservative canonical identities, three rendered report pages, complete CSV/HTML outputs and a validated monthly automation dry run.
- [ ] Prove successive refresh cycles, exact refresh/batch correlation, idempotent replay, DORA rollover, interrupted writes, incomplete exports and continued operation under ongoing licence rights. Retain review decisions and the last good report state.
- [ ] Resolve the existing publishing/schedule/delivery approval gates separately. A withheld delivery approval must not be interpreted as technical failure or permission to enable it.
- [ ] Once the foundation is accepted, implement OpenAlex and Crossref enrichment first, ARDC research-activity context second, and Dimensions only within documented free/reuse entitlements. Each source is independently optional and can be disabled without breaking the accepted two-source baseline.

## Source roles and current access evidence

Documentation checked 2026-09-14; verify again when implementation starts. Free provider access and Power Platform connector execution rights are separate questions.

| Source | Intended added value | Access and fallback |
| --- | --- | --- |
| OpenAlex | Broader publication discovery; work/author/institution identifiers; topics, open-access locations and reference/citation relationships where supplied. Use institutional candidates to identify possible coverage gaps, not as conclusive CHHHS affiliation evidence. | Public API has a small anonymous allowance; a free account/key currently supplies $1/day usage, with no payment method required. Configure a strict free-budget ceiling, caching and resumable bounded queries; do not buy credits automatically. Prefer exact DOI lookups before wider discovery. Recheck current request costs, limits and data/content rights. |
| Crossref | DOI resolution and publisher-deposited bibliographic enrichment; publication-date variants, funders/awards, ORCID/ROR, licences and update/retraction relationships where deposited. | Public REST API requires no sign-up. Follow documented rate-limit headers/backoff and polite-pool guidance. Metadata availability varies; abstracts may carry separate copyright. Do not assume a DOI guarantees complete affiliations, references or full text. |
| Scopus (Elsevier) | Comprehensive multidisciplinary citation index; author Scopus IDs, standardized affiliation profiles (AF-ID), and verified citation counts. | Requires institutional subscription or Elsevier Developer API key. For Queensland Health, verify whether existing institutional library entitlements permit API-based metadata harvesting or whether scheduled CSV exports via Scopus web interface should be used as the ingestion fallback. Never store proprietary full-text or raw XML beyond permitted metadata fields. |
| Web of Science (Clarivate) | Authoritative core collection indexing; Clarivate ResearcherID, journal citation indicators, and funding acknowledgment parsing. | WoS Starter API or Expanded API requires institutional access keys. Fallback route: structured manual/scheduled RIS/BibTeX/Excel exports ingested through the SharePoint staged file intake. Citation counts isolated in `CitationCount_WoS`. |
| ARDC research activities — provisional mapping to Research Link Australia (RLA) | Link publications to Australian researchers, organisations and funded activities; retain project/grant identifiers, relationships and provenance as contextual entities. | The supplied Google redirect could not be resolved. RLA is the likely intended service based on its research-activities scope; confirm the exact service before implementation. Official RLA documentation requires authentication, an access request and a signed service schedule. Verify no-cost eligibility and permitted organisational reuse; do not assume anonymous API access or execute an agreement. If the intended service is Research Data Australia, assess its collection/activity records and API separately. Where API rights are unavailable, use permitted reference links or explicitly assisted imports only. |
| Dimensions — freely accessible aspects only | Additional publication/dataset discovery and contextual citation information where the free service actually exposes it and permits reuse. | The free web application is for personal, non-commercial use. Analytics API access normally requires an institutional subscription; eligible scientometric projects can apply for free access, which is not established for this operational dashboard. First verify permitted organisational use, export fields/limits, retention and redistribution. Use only expressly permitted exports or link-outs; no scraping substitute for API rights. Leave automated ingestion disabled if no suitable free entitlement exists. |

Citation counts and grant information are optional source-attributed context, not new headline performance metrics. Do not add impact rankings or grant KPIs without a separate scope decision. Activities, grants, datasets, authors and organisations must never increase publication counts merely because a provider returns them. Each citation counter is recorded independently (`CitationCount_Scopus`, `CitationCount_Crossref`, `CitationCount_OpenAlex`) to preserve scientometric validity without false equivalence.

## SearchRight reuse review

Reference: [SearchRight](https://github.com/edithatogo/searchright), reviewed main revision `e1f78ecf3467a88fc95523c53babb503fb3921ef`.

Its [provider contract baselines](https://github.com/edithatogo/searchright/blob/e1f78ecf3467a88fc95523c53babb503fb3921ef/integration/provider-contract-baselines.json) include PubMed, Europe PMC, Crossref and OpenAlex, with endpoint/parser/fixture mappings and `live_canary_status: not_executed`. Reuse ideas for provenance, pagination, response-shape checks and provider failure handling after code/licence review. Do not interpret fixtures or listed providers as production integrations. Keep Rust/CLI orchestration out of the hosted runtime: translate appropriate contracts into native Power Query/Power Automate implementations. Europe PMC is an additional candidate to assess from the repo after the named sources, not an integration enabled by this amendment.

## Implementation work packages

### 1. Capability and feature comparison

- [ ] Inventory SearchRight provider contracts and parsers at a pinned revision; record which added fields genuinely improve PubMed/DORA coverage or quality and which merely repeat their upstream data.
- [ ] Confirm the intended ARDC service, current schemas, source licences, quotas, keys, export/redistribution rights and organisational eligibility. Record API availability separately from website availability and from local connector availability.
- [ ] Build a representative benchmark from accepted canonical records, DORA-only records, missing-DOI records and reviewed ambiguous cases. Measure incremental records, metadata fill rates, conflict rates, affiliation evidence and cost/request budgets before choosing bulk queries.
- [ ] Checkpoint: review the source-by-source benefit and access matrix; unavailable optional sources do not block the base dashboard.

### 2. Native adapters and retained provenance

- [ ] Define per-source schemas, persistent IDs, parser versions, query scope, retrieval time, licence/attribution, completeness flags and immutable raw observations before implementation.
- [ ] Implement OpenAlex and Crossref in isolation using cloud-compatible Power Query Web.Contents with stable origins, bounded pagination and caching; retain through the proven standard Power BI and OneDrive/SharePoint path where supported. Verify secure key handling and cloud refresh without embedding secrets in source or exports.
- [ ] Use direct Power Automate HTTP/custom connectors only if current assigned licences and tenant rules permit. If neither native route executes, classify the source as assisted/unavailable; do not introduce a Fabric trial or external hosted runtime as an implicit dependency.
- [ ] Add ARDC and Dimensions adapters only after their access/reuse gates pass. Preserve a documented link-only or approved-file-import fallback and expose its refresh limitations.
- [ ] Checkpoint: native canaries, quota/429 handling, schema drift, pagination termination, exact retained-file readback and independent key-set checks for each source.

### 3. Canonical reconciliation and enrichment

- [ ] Preserve existing canonical IDs and reviewed aliases. Match exact normalized DOI/PMID first; retain provider IDs as source aliases, not new canonical IDs. Conflicting identifiers and fuzzy title/author/year matches require review. A source addition cannot undo an existing exclusion or merge decision.
- [ ] Separate discovery candidates from accepted publications. Require the same CHHHS scope/affiliation evidence as the baseline; author identity or broad institution matching alone is insufficient.
- [ ] Keep field-level source, observed time, original value, selected value and conflict reason. Define explicit per-field precedence, preserve raw publication dates and precision, and never replace a known value with an absent enrichment field.
- [ ] Keep citation counts by provider and observation date; do not sum incomparable counts. Record upstream lineage so multiple aggregators are not mistaken for independent corroboration.
- [ ] Model Activity, Dataset, Organisation and Author relationships separately, with typed IDs and evidence-bearing links to publications. Preserve missing/uncertain links and per-record reuse conditions.
- [ ] Checkpoint: replay, conflict, false-affiliation and multi-source-duplicate tests; exact canonical key sets reconcile before/after, with every addition/removal explained.

### 4. Reports, exports and operations

- [ ] Extend Source Reconciliation within the existing three-page design: source presence/overlap, incremental candidates, conflicting fields, coverage limits, last successful collection and unavailable/stale sources. Keep publication headlines canonical-key based.
- [ ] Extend full CSV/HTML export contracts deliberately for approved enrichment fields; provide separate relationship exports for one-to-many activities/identifiers when necessary. Preserve the full bibliography, field provenance, dates and attribution without row multiplication.
- [ ] Make optional-source refresh failures visible while retaining last accepted enrichment and the functional PubMed/DORA baseline. Quota exhaustion is a source-status event, never zero publications or permission to spend.
- [ ] Revalidate monthly output completeness, native rendering, runtime/licence rights and approved schedule/delivery scope. Obtain any new agreement, publishing or delivery approval only when the proposed change is concrete and reviewable.
- [ ] Checkpoint: end-to-end native dry run, exact output key/field parity, rollback and disable-one-source rehearsal before release.

## Official references

- [OpenAlex API](https://help.openalex.org/api/), [pricing](https://help.openalex.org/access/pricing/) and [operation costs](https://help.openalex.org/access/example-costs/).
- [Crossref REST API and reuse notes](https://www.crossref.org/documentation/retrieve-metadata/rest-api/).
- [Dimensions free version](https://www.dimensions.ai/products/all-products/dimensions-free-version/) and [Analytics API access](https://docs.dimensions.ai/dsl/api.html).
- [ARDC Research Link Australia](https://ardc.edu.au/services/ardc-research-link-australia/), [API access requirements](https://documentation.ardc.edu.au/rla/for-rla-api-users-how-to-access-and-reuse-rla-data) and [Research Data Australia scope](https://documentation.ardc.edu.au/rda/introduction).
