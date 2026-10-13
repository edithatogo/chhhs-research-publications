# Source routes for the current enrichment phase — 14 October 2026

This is a route decision for the existing T11/E01 source path, not admission of
all planned feeds. The first deliverable is the bounded OpenAlex addition to the
existing isolated model and publications flow. Existing PubMed/DoRA history,
canonical identities, reviews and dates remain the baseline. Native save,
processing, flow integration and routine activation are separate evidence.

Use the retained raw payloads first. Then collect only known identifiers missing
required context; keep complete authorised responses before selecting fields.
For slowly changing reference/award data, a versioned official file is usually
simpler than a per-publication API. This is an engineering recommendation based
on the present 1,341-publication consumer, not a measured coverage ranking.

| Planned source / role | Simplest route in this phase | Inclusion decision |
| --- | --- | --- |
| PubMed + DoRA publications | Reuse accepted archive and loaded canonical keys; no new harvest for enrichment bootstrap | Foundation, already accepted within its recorded scope |
| OpenAlex publication context | Bootstrap three existing frozen complete responses into the existing isolated Microsoft model, losslessly compressed; DOI joins to loaded Publication. For wider fresh coverage use bounded known-DOI calls, cache and free-budget guard | Implement now; bootstrap does not establish a recurring acquisition job |
| Crossref dates, funders, ORCID/ROR and update/retraction links | Reuse deposited fields in current metadata; then exact missing DOI requests through an existing qualified native Web/HTTP path | Next scholarly gap; extend existing adapter rather than duplicate it |
| Europe PMC PMCID/OA/trial/grant context | Reuse PubMed/raw article metadata first; exact PMID requests in documented core mode only for missing context | Existing local adapter; no new broad collector or full-text download |
| ROR organisation crosswalk | Exact v2 ROR IDs already deposited for a small crosswalk; official versioned dump if the whole reference directory is needed | First organisation gap; retain ambiguous candidates, no name-only institution merge |
| DataCite dataset/software relations | Exact known related DOI missing from Crossref; retain relationship direction and output type | Named related-output gap; no global dump for this register |
| Internal research/project/award registers | Existing approved SharePoint lists or Excel tables, through their standard Microsoft connectors; preserve original workbook as well as structured rows | First activity/funding slice after exact resource/field permission qualification |
| Office 365 Users | Approved selected ID lookups using the existing connector | Narrow identity context only; no bulk directory bootstrap or employment inference |
| Office 365 Groups | Selected approved group IDs, reuse existing organisation mapping | Supporting context only; membership is not affiliation/investigator proof |
| ABS geography/population | Official dated file release for fixed geography edition; API only for selected missing series/periods | First geography dependency, preserve vintage, units and suppression |
| NHMRC awards | Official funding-statistics file + dictionary, versioned and hashed, staged through approved Microsoft file intake | G02/G04-owned award slice; not an opportunity feed |
| MRFF awards | Official Excel grant-recipient file rather than PDF parsing; preserve grant ID and source as-of date | G02/G04-owned award slice. Current published file describes awards as at 10 July 2026 |
| GrantConnect, ARC, Queensland/QH, EMF/university opportunities | Reuse qualified maintained intake; official RSS/API only when exact item key/lifecycle is verified, otherwise permitted structured imports/link-out | Existing G02 admission decisions remain; no page scraping or treating calendars/awards as open rounds |
| NIH RePORTER awards/publication links | PMID or exact award/project-number queries, bounded pages | Only if accepted metadata lacks the needed award link; keep awards distinct from opportunities |
| Grants.gov opportunities | Existing qualified official API/feed adapter, bounded eligibility-relevant requests | Source-specific opportunity gap, not Australian award replacement |
| ClinicalTrials.gov | Extract existing NCT identifiers from retained publications, then exact-ID API v2 records | Trial link gap only; trial rows never multiply publication counts |
| ANZCTR | Existing ACTRN identifiers plus permitted export/reference links until an extraction route is qualified | Access-dependent; no assumed API/scraping |
| OpenAIRE | Reuse upstream Crossref/OpenAlex/Europe PMC fields; selected stable V3 exact-ID/project relations only for uncovered context | Successful token-bearing probe is not renewable native credential proof; routine refresh remains open |
| CORDIS | Permitted official project export where qualified; verify extraction API separately | Supplied widget credential does not qualify extraction |
| OpenCitations | Known DOI relationships/counts only after proving an uncovered field gap and native route | Optional; separate provider count and observation time, no summed citation total |
| DOAJ | Selected journal ISSN reference or authorised reference dump if needed | Optional journal/OA context, not proof of article compliance or quality |
| ORCID | Reuse deposited identifiers and source mentions before any direct authorised lookup | No name-derived identity assignment, person merge or writeback |
| Preprint repositories | Reuse Europe PMC/OpenAlex overlap and known version/DOI relations | Named version gap only, no duplicate publication counts |
| ARDC RLA / Research Data Australia | Confirm which service; permitted existing export/link-out, then qualified exact-ID API | Separate services; access/reuse gate remains, no new agreement/account |
| Dimensions / Scopus / Web of Science | Permitted institutional structured exports staged through existing file intake | Conditional entitlement/retention only; no paid key, scraping or claim of native feed acceptance |
| CORE / Semantic Scholar | Existing identifier metadata first; a bounded permitted API only for a demonstrated remaining field | Optional access/terms-dependent overlap; not current critical path |
| Zenodo | Reuse DataCite known-DOI relationships before exact record metadata | Conditional related outputs; record/file licence separate, no file harvest |
| NIH iCite | Exact retained PMID slice only if its distinct metric is required | Conditional metric; provider definitions/time kept separate |
| ABN Lookup / Azure Maps | Exact legal-entity ID / selected permitted address operation after existing credential and budget qualification | Conditional; ROR and known geography first, no subscription creation |
| GDELT | None for the current publication/archive/register capability | Future context, explicitly outside this phase |

The reusable native shape is one source envelope and raw retention contract,
source-specific typed tables, exact-ID context joins and conditional registry
updates. Reuse existing archive files, connections, stable IDs and rollback.
Retain source status and last-good values on missing/failed/older observations;
record each selected value's original source observation time. A partial page
set is not a successful empty result or deletion evidence. Complete authorised
raw capture does not authorise linked full text or sensitive workforce fields.

CLI/API authoring should read the exact current definition, compare the lease
baseline, apply only the assigned object diff, save native readback, and run only
the affected scope. Compression/file bootstrap removes repeated provider calls;
it does not substitute for native processing or flow acceptance. General HTTP
and custom connectors still require the appropriate Microsoft entitlement/DLP;
provider-free and connector-free are separate questions. No schedules, delivery,
sharing, report binding or production promotion are enabled by this assessment.

## Official references checked for this decision

- [OpenAlex authentication](https://help.openalex.org/api/authentication/) and
  [request costs](https://help.openalex.org/access/example-costs/): exact entity
  retrieval and bounded list queries have different costs; choose by actual gap,
  avoid a global snapshot for a small register, and retain full returned payloads.
- [Crossref REST metadata](https://www.crossref.org/documentation/retrieve-metadata/rest-api/),
  [Europe PMC core/search REST](https://europepmc.org/RestfulWebService),
  [DataCite REST](https://support.datacite.org/docs/rest-api),
  [ROR REST](https://ror.readme.io/docs/rest-api) and
  [ROR versioned data dumps](https://ror.readme.io/docs/zenodo).
- [NHMRC funding statistics/files](https://www.nhmrc.gov.au/funding/outcomes-and-data-research/research-funding-statistics-and-data),
  [MRFF official grant-recipient Excel/PDF](https://www.health.gov.au/resources/publications/medical-research-future-fund-mrff-grant-recipients),
  [NIH RePORTER](https://api.reporter.nih.gov/),
  [ClinicalTrials.gov API](https://clinicaltrials.gov/data-api/api).
- Remaining access/admission boundaries come from the current repository
  [source plan](FUTURE_SOURCE_ENRICHMENT.md),
  [platform delivery contract](PLATFORM_COMPLETION_PLAN.md) and G02/G04 decisions.
  Historical checked tracks do not prove current native integration.
