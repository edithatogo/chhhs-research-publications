# Architecture and Operations: Publication Registry Versioning Systems

This document clarifies the versioning capabilities across the CHHHS Research Publication Registry platform, covering SharePoint Online, Power Automate, Power BI semantic models, and local Git repositories.

---

## 1. Summary of Versioning Capabilities

| Layer | Native Versioning Mechanism | Repository / Git Integration | Disaster Recovery / Rollback |
| :--- | :--- | :--- | :--- |
| **SharePoint List** | Native item-level major version history (configured for 500 versions). | Seed datasets (`publication-registry-seed.csv`, `.json`) and deployment scripts in Git. | Revert individual fields or entire publication records via SharePoint UI or PnP PowerShell. |
| **Power Automate Flow** | Platform Version History (every save creates an immutable version snapshot). | Declarative workflow definitions (`config/flows/*.definition.json`) and Solution ZIP packages. | Revert to previous version via Flow portal "Version History" or re-import repo ZIP package into flow `{{FLOW_ID}}`. |
| **Power BI Semantic Model** | Fabric/Workspace version history & isolated development clones. | Declarative TMDL (`config/SharePointPublicationRegistry.m`, `tmdl/`) and DAX measure scripts. | Isolated canary model (`{{ISOLATED_MODEL_ID}}`) verified with clean rollback path. |
| **Publication Data & Lineage** | Persistent observation timestamps (`first_observed_utc`, `last_observed_utc`, `CitationMetricsObservedUTC`). | SQLite database (`Registry` table + `SourceRecord` table) with immutable raw ingestion batches. | Idempotent replay from raw feeds; deterministic deduplication ensures zero data loss or ghost deletions. |

---

## 2. SharePoint List Versioning

### Configuration
SharePoint Online supports automated versioning on custom lists. In this project, versioning is enforced via `scripts/Deploy-SharePointList.ps1`:
```powershell
Set-PnPList -Identity "Publication Registry" -EnableVersioning $true -MajorVersions 500
```

### Operational Behavior
1. **Automated Tracking:** Every modification—whether applied via the Power Automate upsert flow, human curation (changing `ReviewStatus` from `Needs Review` to `Included`), or batch PowerShell—creates a numbered version (1.0, 2.0, 3.0, etc.).
2. **Audit Trail:** Each version records:
   - Modified date/time (UTC).
   - Modified by (Service Principal or User Account).
   - Exact delta: previous value vs. new value for every modified column.
3. **Restoration:** Any previous version can be inspected and restored with one click from the SharePoint List context menu (`Item -> Version History -> Restore`).

---

## 3. Power Automate Flow Versioning & Platform Deduplication

### Platform Version History
Power Automate provides built-in version control on every cloud flow:
- Navigate to flow details: `Flow Details -> Version History`.
- Shows timestamp, author, save comments, and allows instant rollback to any previously saved revision.

### Git-Controlled Declarative Definitions
To ensure engineering rigor and compliance:
1. **Flow Definitions in Code:** The workflow is authored and maintained declaratively in `config/flows/publication-registry-upsert.definition.json`.
2. **Package Generator:** `scripts/build_sharepoint_upsert_package.py` packages the definition and metadata into `private/ops/flow-packages/sharepoint-upsert.zip`.
3. **Platform Deduplication:** To prevent multiple duplicate flows from accumulating on the Power Automate platform, new imports explicitly update the existing flow ID (`{{FLOW_ID}}`) using the "Update" action rather than "Create as new".

---

## 4. Multi-Source Ingestion & Enrichment Pipeline

### Architecture
The deduplication pipeline supports 8 distinct bibliographic and scientometric sources:
1. **PubMed:** National Library of Medicine API (mesh terms, affiliations, PMIDs).
2. **DORA:** Queensland Health Institutional Repository (staff publications, local facility tags).
3. **OpenAlex:** Live REST API (global citation counts, Open Access status, OA landing URLs, ROR affiliations).
4. **Crossref:** Live REST API (publisher citation counts, funder acknowledgments, grant award numbers).
5. **Dimensions:** Structured CSV/JSON ingestion (`ingest_dimensions.py` extracting citations, FCR, RCR).
6. **Scopus:** Structured CSV ingestion (`ingest_scopus_wos.py` extracting Scopus EID, Scopus citations, author affiliations).
7. **Web of Science:** Structured CSV/TSV ingestion (`ingest_scopus_wos.py` extracting WoS UT, Core Collection citations, grant numbers).
8. **ARDC Research Link Australia (RLA):** Structured activity ingestion (`ingest_scopus_wos.py` linking MRFF/NHMRC grants and Australian research activity IDs).

### Provenance Preservation
- Every raw ingestion maintains immutable timestamps and source identifiers.
- Independent citation counters (`CitationCount_OpenAlex`, `CitationCount_Crossref`, `CitationCount_Scopus`, `CitationCount_WoS`) prevent false equivalence.
- Merged records maintain a composite `SourceSet` (e.g. `PubMed; DORA; OpenAlex; Crossref`).

---

## 5. Automated Monthly Reporting & DOCX Export

### SharePoint View
The "Past Month Publications" view filters the list to:
- `ReviewStatus` = `Included`
- Sorted by `PublicationYear DESC`, `PublicationMonth DESC`.

### DOCX Generation Utility
`scripts/export_monthly_docx.py` generates an executive Word report for clinical governance:
```bash
python3 scripts/export_monthly_docx.py --month 2026-08 --output reports/CHHHS-Publications-Monthly-2026-08.docx
```
- Fully styled to Queensland Health Clinical Research branding (Deep Teal `#005C8A`, Navy Slate `#2B3E50`, Evergreen `#107C41`).
- Contains Executive Summary KPI cards, facility breakdowns, publication types, and hyperlinked citations with PubMed/DOI links.
