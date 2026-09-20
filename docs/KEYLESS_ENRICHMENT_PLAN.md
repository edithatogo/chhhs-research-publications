# Keyless & Token-Free Enrichment Plan: CHHHS Research Publications

Status: **Approved Architecture & Implementation Plan** (2026-09-18)  
Target Environment: **Queensland Health M365 Tenant (`{{TENANT_ID}}`)**
Primary User: **RIMS maintainer (configured privately)**
Governing Constraint: **Zero API Key / Token / Subscription Dependency**

---

## 1. Executive Mandate & Strict Keyless Constraint

Per user directive, the CHHHS Research Publication system must **operate entirely without API keys, developer tokens, paid subscriptions, or vendor account registrations**. 

This constraint guarantees:
1. **Zero Operational Friction:** No credential rotation, expired tokens, credit card ceilings, or vendor access requests.
2. **Enterprise Cloud Compliance:** Power Automate flows, Power Query transformations, and Python routines run purely over open public protocols with zero secrets stored in the tenant or codebase.
3. **Institutional Longevity:** Ingestion and enrichment remain durable, reproducible, and self-sustaining across staff transitions without institutional account maintenance.

---

## 2. Provider Audit: Keyless vs. Key-Required Matrix

All potential data sources and enrichment providers are audited against the keyless constraint:

| Provider / Source | Access Model | Key / Token Required? | Status in CHHHS Pipeline | Notes / Enforcement |
| :--- | :--- | :---: | :---: | :--- |
| **PubMed (NCBI E-Utilities)** | Public REST API | **NO** | **ACTIVE (Core)** | Standard anonymous access (up to 3 req/sec). Comprehensive biomedical metadata, MeSH, grant lists, clinical trial links. |
| **OpenAlex** | Public REST API (Polite Pool) | **NO** | **ACTIVE (Enrichment)** | Requires only a polite email header (`mailto:{{POLITE_EMAIL}}`). Free tier provides 100,000 req/day. Open citations, OA status, topics, grants. |
| **Crossref** | Public REST API (Polite Pool) | **NO** | **ACTIVE (Enrichment)** | Public polite pool header. DOI resolution, publisher-deposited funder registries, award numbers, clinical trial numbers. |
| **Internal Rule Engine** | Deterministic Algorithmic Classifier | **NO** | **ACTIVE (Governance)** | Pure Python / Power Query rule sets running locally and in cloud flows over harvested metadata. |
| **Europe PMC (EBI)** | Open REST API (Keyless) | **NO** | **ACTIVE (Enrichment)** | Keyless open API from EMBL-EBI. Provides PMCID, open-access full-text URLs, author ORCID identifiers, and grant funder linkages. |
| **Dimensions.ai API** | Proprietary REST / DSL API | **YES** | **EXCLUDED** | Automated API access requires an institutional Dimensions Analytics subscription and API token. Excluded from automated cloud ingestion. |
| **Scopus (Elsevier) API** | Proprietary REST API | **YES** | **EXCLUDED** | Requires Elsevier Developer API key (`X-ELS-APIKey`). Excluded from automated cloud ingestion. Staged manual CSV intake only if available. |
| **Web of Science API** | Proprietary REST API | **YES** | **EXCLUDED** | Requires Clarivate API key (`X-ApiKey`). Excluded from automated cloud ingestion. Staged manual CSV intake only if available. |
| **ARDC RLA API** | Authenticated Registry API | **YES** | **EXCLUDED** | Requires institutional access request, registered authentication, and signed service schedule. Excluded from automated ingestion. |

---

## 3. Keyless Funding Architecture & Columns

All funding metadata is extracted exclusively from **OpenAlex, Crossref, Europe PMC, and PubMed**, supplemented by internal deterministic categorization:

```
Harvest Pipeline (Zero Keys):
┌─────────────────────────┐
│ PubMed (GrantList)      │──┐
├─────────────────────────┤  │
│ Europe PMC (EBI Grants) │──┤
├─────────────────────────┤  ├─► [Harmonization & Deduplication] ─► [Rule Classifier] ─► SharePoint / PBI
│ OpenAlex (Grants Array) │──┤
├─────────────────────────┤  │
│ Crossref (Funder Array) │──┘
└─────────────────────────┘
```

### Approved Funding & Governance Columns (Keyless):

| Column Name | SharePoint EntityPropertyName | SharePoint Type | Source / Derivation Method | Value & Operational Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **`PMCID`** | `PMCID` | Single line of text | Europe PMC / PubMed | PubMed Central identifier for direct open-access full-text retrieval. |
| **`AuthorORCIDs`** | `Author_x0020_ORCIDs` | Multiple lines of text (Note) | Europe PMC (`authorList.author[].authorId[type=ORCID]`) | Author persistent digital identifiers for researcher attribution. |
| **`FunderNames`** | `FunderNames` | Multiple lines of text (Note) | OpenAlex, Crossref, Europe PMC, PubMed | Preserves acknowledged funding bodies (NHMRC, MRFF, Emergency Medicine Foundation, etc.). |
| **`GrantIDs`** | `GrantIDs` | Multiple lines of text (Note) | OpenAlex, Crossref, Europe PMC, PubMed | Exact award reference numbers. |
| **`FundingType`** | `Funding_x0020_Type` | Choice | Deterministic Regex Classifier on `FunderNames` | Categorization: Commonwealth (NHMRC/MRFF), State / Qld Health, Philanthropic / Foundation, Commercial / Industry Trial, University Partner, Unfunded / Departmental. |
| **`IsInternalFunding`** | `Internal_x0020_Funding` | Choice (`Yes`, `No`) | Rule Match on Cairns Foundation / SERTA | Quantifies ROI from internal CHHHS research trust funds. |
| **`ClinicalTrialID`** | `Clinical_x0020_Trial_x0020_ID` | Single line of text | Regex (`ACTRN\d{14}`, `NCT\d{8}`) | ANZCTR and ClinicalTrials.gov registry tracking. |
| **`IndigenousHealthFocus`** | `Indigenous_x0020_Health_x0020_Fo` | Choice (`Yes`, `No`) | Rule Classifier on MeSH / Keywords / Title | Tracks First Nations health equity research in Far North Queensland. |
| **`FieldOfResearch`** | `Field_x0020_of_x0020_Research` | Single line of text | OpenAlex (`primary_topic.field.display_name`) | ANZSRC FoR clinical specialty mapping. |
| **`StudyDesign`** | `Study_x0020_Design` | Choice | MeSH / PublicationType classifier | Evidence hierarchy: RCT, Systematic Review, Observational/Cohort, Guideline, Case Report. |
| **`EuropePMC_OpenAccess`** | `Europe_x0020_PMC_x0020_Open_x002` | Single line of text | Europe PMC | Open access status indicator. |
| **`EuropePMC_FullTextURL`** | `Europe_x0020_PMC_x0020_Full_x002` | Hyperlink (URL) | Europe PMC | Direct full-text PDF or HTML link. |
| **`EuropePMC_CitedByCount`** | `Europe_x0020_PMC_x0020_Citations` | Number | Europe PMC | Open Europe PMC citation count. |

---

## 4. Implementation Status

- [x] **Phase 1: Local Rule Engine & Keyless Adapters (COMPLETED)**
  - Created [`scripts/enrich_europe_pmc.py`](file:///Volumes/PortableSSD/GitHub/RIMS/chhhs-research-publications/scripts/enrich_europe_pmc.py) with batch query support.
  - Created [`scripts/keyless_classifiers.py`](file:///Volumes/PortableSSD/GitHub/RIMS/chhhs-research-publications/scripts/keyless_classifiers.py) for FundingType, InternalFunding, IndigenousHealthFocus, StudyDesign, ClinicalTrialID.
  - Extended [`scripts/enrich_openalex.py`](file:///Volumes/PortableSSD/GitHub/RIMS/chhhs-research-publications/scripts/enrich_openalex.py) with batch query and FieldOfResearch extraction.
  - Extended [`scripts/batch_enrich_sources.py`](file:///Volumes/PortableSSD/GitHub/RIMS/chhhs-research-publications/scripts/batch_enrich_sources.py). All 1,265 records enriched and cached in under 40 seconds.
  - All 184 unit tests passing.
- [x] **Phase 2: SharePoint List Schema Update & Live In-Place Sync (COMPLETED)**
  - Created 11 new columns directly on `Publication Registry` (`{{SHAREPOINT_LIST_ID}}`) via REST API.
  - Mapped exact `EntityPropertyName` values.
  - Synchronized all 1,265 items in-place using [`scripts/sync_sharepoint_seed.py`](file:///Volumes/PortableSSD/GitHub/RIMS/chhhs-research-publications/scripts/sync_sharepoint_seed.py).
- [x] **Phase 3: Executive Reporting & Governance Visuals (COMPLETED)**
  - Updated [`scripts/export_monthly_docx.py`](file:///Volumes/PortableSSD/GitHub/RIMS/chhhs-research-publications/scripts/export_monthly_docx.py) to incorporate executive funding governance breakdowns, study design distribution, First Nations health focus counts, and direct PMCID / OA links.
  - Updated [`config/SharePointPublicationRegistry.m`](file:///Volumes/PortableSSD/GitHub/RIMS/chhhs-research-publications/config/SharePointPublicationRegistry.m) with complete typed schema.
