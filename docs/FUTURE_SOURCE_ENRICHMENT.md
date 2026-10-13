# Deferred source enrichment and reconciliation

## Additional-source discovery — 13 October 2026

Official documentation was searched and compared with the existing source and
grants catalogues, author design and local enrichment adapters. This is a bounded
source-discovery assessment, not an exhaustive census or a native integration
claim. No source was enabled, credentials registered, agreement accepted, support
message sent or business-record harvest run. Priorities below are recommendations
for selection after the current shared-data path is accepted; already authorised
current-source field retention continues under T11/E01.

### Recommended additions and refinements

| Priority / source | Added value and vertical | Documented acquisition / rights boundary | Smallest useful integration and existing owner |
| --- | --- | --- | --- |
| First shortlist: **ROR** | Shared organisation/funder identifiers, names, status and relationships supporting all verticals | [Registry is CC0](https://ror.org/); [v2 REST API](https://ror.readme.io/docs/rest-api) and data dump. The [client-ID page](https://ror.readme.io/docs/client-id) currently says registration is paused and ID-based limits are not enforced during that pause; recheck at adoption. API defaults to active organisations and has a result ceiling. | Resolve a bounded set of existing organisation IDs/aliases, retain full records including nulls, include inactive/predecessor evidence when needed. Matching is candidate evidence, not employment proof. Existing author/organisation design and T11 retention; use a dump only if scale justifies it. |
| First shortlist: **Crossref Retraction Watch extension** | Publication correction/retraction provenance beyond ordinary bibliographic fields | [Crossref](https://www.crossref.org/documentation/retrieve-metadata/retraction-watch/) exposes Retraction Watch updates through REST and a downloadable CSV; retain source attribution and the chosen dataset's current reuse terms. Corrections/expressions of concern are less comprehensive than retractions. | Reuse the existing Crossref adapter and exact DOI matches; retain update relationships/status separately, preserving the original publication and notices. T11/E07; no automatic deletion or publication-count inflation. |
| First shortlist: **DataCite** | Dataset/software/other research-output metadata, DOI relationships, creators, ORCID/ROR and funding references | [Public REST retrieval](https://support.datacite.org/docs/api) needs no authentication; [public metadata files](https://support.datacite.org/docs/datacite-public-data-file) are CC0. Linked content has separate rights. [Full metadata options](https://support.datacite.org/docs/api-queries) require explicit affiliation/publisher parameters; detail adds further attributes. | Start with DOI relationships already present in accepted records. Preserve resource type and relation direction; datasets are not publications. Shared T11 retention and later projects/researcher consumers. No whole-corpus download by default. |
| Next projects slice: **ClinicalTrials.gov** | Registered study identity, status, sponsor/site context and publication links; strengthens projects/activity rather than inferring trials from text | NLM documents a [public REST/JSON v2 API](https://www.nlm.nih.gov/pubs/techbull/ma24/ma24_clinicaltrials_api.html). Current API/terms pages returned only application shells in this review, so current quota, full schema and reuse conditions remain to verify. | Start with exact NCT identifiers already present, qualify the current schema and preserve complete scoped records. Crosswalk registry aliases rather than counting each registration as a separate project. T11-H03/H04 and existing relationship design; registry listing is not local governance approval. |
| Next projects slice, assisted route: **ANZCTR** | Australian/New Zealand trials and local recruitment context; ACTRN identity and links to other registrations | Current [FAQ](https://www.anzctr.org.au/Faq.aspx) documents Excel downloads, superseding older XML-only guidance. [Terms](https://www.anzctr.org.au/Support/Terms.aspx) restrict unauthorised collection software and require attribution, currency, processed date and modification disclosure for permitted reuse. | Use permitted export intake after rights/refresh qualification; do not invent or reverse-engineer an API. Retain complete workbook and schema, then project trial records. T11-H03/H04. ANZCTR also displays regional ClinicalTrials.gov records, so those are overlapping evidence. |
| Next funding slice: **NHMRC award datasets** | Authoritative health-research award context, distinct from funding opportunities and publication acknowledgements | [Official statistics/data](https://www.nhmrc.gov.au/funding/outcomes-and-data-research/research-funding-statistics-and-data) provides annual snapshots and a dictionary; page reports update on 25 March 2026. Select the grant-level workbook, confirm its fields/licence and preserve its vintage. | Bootstrap a versioned official-file import through existing storage, with grant IDs and administering institution. G02/G04/G06. Aggregate disease-topic amounts can overlap and must not be summed as unique grant totals. |
| Next funding slice: **MRFF grant recipients** | Australian health-research awarded projects, grant identifiers, recipients, dates and values | [Official dataset](https://www.health.gov.au/resources/publications/medical-research-future-fund-mrff-grant-recipients) offers Excel and PDF. Published 27 August 2026, data as at 10 July 2026, excluding media-embargoed awards. Confirm workbook licence/reuse at selection; no API established here. | Prefer complete official Excel file over PDF extraction; retain workbook plus table/field provenance. G02/G04/G06; reconcile grant/agency IDs against GrantConnect and publication acknowledgements without treating them as independent awards. |
| Conditional local coverage: **ResearchOnline@JCU** | JCU research outputs potentially missing from existing publication sources; useful local overlap/gap evidence | [Repository information](https://researchonline.jcu.edu.au/information.html) describes its reviewed deposits. The [repository policy page](https://researchonline.jcu.edu.au/policies.html) currently has no defined policies; [JCU procedure](https://www.jcu.edu.au/policy/academic-governance/research-management/researchonline-procedure) distinguishes metadata from restricted full text. Bulk endpoint/reuse remains unqualified. | First assess a small set of known missing DOI/handle records through permitted access. Require actual CHHHS attribution rather than importing every JCU record. T11 source qualification; full-text download is separate. |
| Conditional OA gap: **Unpaywall** | DOI-based OA locations, versions and per-location licence evidence | [Data format](https://unpaywall.org/data-format) describes location/version/licence fields. The [API page](https://unpaywall.org/products/api) was JavaScript-only to this reader; current identification, quota and data-use terms were not verified. | Assess only if existing Europe PMC/OpenAlex coverage leaves a measured OA gap. Retain location evidence, not an assumed licence to download every linked article. Existing enrichment work; no new integration on this evidence alone. |
| Conditional researcher route: **ORCID direct data** | Public researcher identifiers, works and affiliation assertions with provenance | [Public API terms](https://info.orcid.org/public-client-terms-of-service/) distinguish individual credentials and allowed use; do not infer organisational entitlement. The [public data file](https://info.orcid.org/privacy-policy/) is CC0, with privacy/community-use considerations. | Prefer ORCIDs already deposited with source works. Qualify institutional member access or a justified public-file route separately. Never assign a person from name alone or infer current employment. Existing author/organisation design; no writeback or account registration. |
| Conditional Australian dataset/activity context: **Research Data Australia** | Collections, parties and activities complementary to Research Link Australia | [ARDC web services](https://documentation.ardc.edu.au/rda/web-services) and [getMetadata](https://documentation.ardc.edu.au/rda/getmetadata-api) document a key-bearing route. RDA and RLA are different services; this review does not establish API entitlement or record-level reuse. | Reuse DOI/organisation/activity identifiers from accepted data, select one demonstrated relationship gap and qualify access. T11 source qualification / existing ARDC extension. Under current keyless policy, retain as conditional or link-only. |

### Existing sources: reuse before adding another adapter

- **Europe PMC is already represented in local code**, including
  `scripts/enrich_europe_pmc.py`; it is not a newly discovered provider.
  Its [REST documentation](https://europepmc.org/RestfulWebService) distinguishes
  default lite results from core metadata. Audit full core response retention
  before writing a second collector. Publication/grant links are source evidence;
  API software licensing is not a blanket licence for article text.
- **Crossref and OpenAlex already have local adapters.** Current OpenAlex
  [authentication](https://help.openalex.org/api/authentication/) and
  [pricing](https://help.openalex.org/access/pricing/) describe limited anonymous
  usage and a larger free keyed budget. The old 100,000-request keyless/polite-pool
  assumption is retired. Keep keyless policy and actual source limits explicit;
  do not register an account or buy credits automatically.
- **ARC, Queensland Grants Finder/QGIP, university calendars and GrantConnect**
  already appear in local funding planning/catalogues. NHMRC/MRFF award files
  extend award evidence, not open-opportunity intake. Finance confirms
  [GrantConnect's official role](https://www.finance.gov.au/individuals/find-grant-grantconnect),
  but this search did not establish a supported public API. Existing permitted
  import/interface-verification decisions remain; HTML search results are not
  an API or reusable institutional entitlement.
- Dimensions, Scopus and Web of Science remain conditional under their existing
  entitlement/reuse gates. Do not duplicate their records through aggregators
  and claim independent corroboration or automatically enable paid sources.

### Selection and bootstrap rule

Recommended first shortlist is ROR, the existing Crossref update/retraction
path, and DataCite; projects then evaluates ClinicalTrials.gov/ANZCTR, while
funding evaluates NHMRC/MRFF award snapshots. This is a recommendation based on
entity/field value and documented routes, not a measured coverage ranking.
For each selected source, record incremental known-key coverage/field fill,
false links, upstream overlap, operation cost, rights and maintainability using
a small agreed benchmark before wider collection. Keep every raw field actually
returned, while explicitly requesting documented full-metadata modes; a default
API response is not necessarily all fields the source can provide.

Use the existing T11/E01 raw archive and source adapters, then typed vertical
projections. Bootstrap with exact-ID lookups or authorised official files;
retain file bytes, schema, version/as-of date, retrieval time and licence record.
Native Microsoft acquisition/retention and replay must work before a source is
marked enabled. No new runtime, resource catalogue or commissioning track.
Implementation remains subject to the current-source completion and existing
post-MVP/access gates; this discovery does not interrupt the publications owner.


Plan amendment requested 2026-09-14. Status: planned, not enabled. This extends the existing Power Platform-native dashboard after the PubMed/DORA foundation is properly set up; it does not delay or replace its acceptance criteria. Keep the existing Power BI workspace, retained storage and current approved report scope. No new source collection, account registration, access application, purchase or deployment is authorised by this planning amendment.

## Start gate and order

- [ ] Finish T11–T15 foundation: committed retained history, full metadata reconstruction, conservative canonical identities, the current approved rendered report pages, complete CSV/HTML outputs and a validated monthly automation dry run.
- [ ] Prove successive refresh cycles, exact refresh/batch correlation, idempotent replay, DORA rollover, interrupted writes, incomplete exports and continued operation under ongoing licence rights. Retain review decisions and the last good report state.
- [ ] Resolve the existing publishing/schedule/delivery approval gates separately. A withheld delivery approval must not be interpreted as technical failure or permission to enable it.
- [ ] Once the foundation is accepted, implement OpenAlex and Crossref enrichment first, ARDC research-activity context second, and Dimensions only within documented free/reuse entitlements. Each source is independently optional and can be disabled without breaking the accepted two-source baseline.

## Earlier source roles and dated access evidence

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

Its [provider contract baselines](https://github.com/edithatogo/searchright/blob/e1f78ecf3467a88fc95523c53babb503fb3921ef/integration/provider-contract-baselines.json) include PubMed, Europe PMC, Crossref and OpenAlex, with endpoint/parser/fixture mappings and `live_canary_status: not_executed`. Reuse ideas for provenance, pagination, response-shape checks and provider failure handling after code/licence review. Do not interpret fixtures or listed providers as production integrations. Keep Rust/CLI orchestration out of the hosted runtime: translate appropriate contracts into native Power Query/Power Automate implementations. Europe PMC has since acquired a local adapter; inspect that implementation and native evidence before further work. This historical review does not prove live acceptance.

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

- [ ] Extend Source Reconciliation within the current approved report design: source presence/overlap, incremental candidates, conflicting fields, coverage limits, last successful collection and unavailable/stale sources. Keep publication headlines canonical-key based.
- [ ] Extend full CSV/HTML export contracts deliberately for approved enrichment fields; provide separate relationship exports for one-to-many activities/identifiers when necessary. Preserve the full bibliography, field provenance, dates and attribution without row multiplication.
- [ ] Make optional-source refresh failures visible while retaining last accepted enrichment and the functional PubMed/DORA baseline. Quota exhaustion is a source-status event, never zero publications or permission to spend.
- [ ] Revalidate monthly output completeness, native rendering, runtime/licence rights and approved schedule/delivery scope. Obtain any new agreement, publishing or delivery approval only when the proposed change is concrete and reviewable.
- [ ] Checkpoint: end-to-end native dry run, exact output key/field parity, rollback and disable-one-source rehearsal before release.

## Official references

- [OpenAlex API](https://help.openalex.org/api/), [pricing](https://help.openalex.org/access/pricing/) and [operation costs](https://help.openalex.org/access/example-costs/).
- [Crossref REST API and reuse notes](https://www.crossref.org/documentation/retrieve-metadata/rest-api/).
- [Dimensions free version](https://www.dimensions.ai/products/all-products/dimensions-free-version/) and [Analytics API access](https://docs.dimensions.ai/dsl/api.html).
- [ARDC Research Link Australia](https://ardc.edu.au/services/ardc-research-link-australia/), [API access requirements](https://documentation.ardc.edu.au/rla/for-rla-api-users-how-to-access-and-reuse-rla-data) and [Research Data Australia scope](https://documentation.ardc.edu.au/rda/introduction).
