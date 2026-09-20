# Platform Completion Plan: CHHHS Research Publication System

Status: **Local implementation complete; platform acceptance remains evidence-gated** (2026-09-20)
Target Environment: **Queensland Health M365 Tenant (`{{TENANT_ID}}`)**
Primary User: **RIMS maintainer (configured privately)**
Execution Strategy: **Separation of concerns, prioritized by operational value, executed via authenticated browser session**

---

## 1. Executive Summary & Objective

All data models, ingestion routines, multi-source enrichment adapters (PubMed, DORA, OpenAlex, Crossref, Dimensions, Scopus, Web of Science, ARDC RLA), flow definitions, versioning scripts, and executive DOCX generators are completed and verified locally. Tenant-side acceptance is tracked separately in [Publication platform acceptance](PUBLICATION_PLATFORM_ACCEPTANCE.md); local checks do not certify live refresh, unattended execution, complete exports, or report readback.

The four tiers are implemented as local, evidence-gated delivery plans. Historical notes or locally generated artefacts do not prove current tenant state. SharePoint list readback, flow run success, complete export reconciliation, semantic-model refresh, and report rendering remain separate native acceptance gates tracked in [Publication platform acceptance](PUBLICATION_PLATFORM_ACCEPTANCE.md).

---

## 2. CLI Tools Evaluation & Route Decision

A strict, one-time audit of available CLI tools was conducted to determine whether automated tenant deployment could occur via command line or if the authenticated browser session is required.

### One-Time Audit Findings:

| CLI Tool | Local Binary Path | Observed State / Tenant | Viability for CHHHS Platform Deployment |
| :--- | :--- | :--- | :--- |
| **PnP.PowerShell** (`Connect-PnPOnline`) | Global PowerShell Module | **Failed:** tenant application-consent error (identifier retained only in private evidence). | **Infeasible for this route:** blocked by tenant admin application consent policy. |
| **CLI for Microsoft 365** (`m365`) | `/opt/homebrew/bin/m365` | **Failed:** Error `AADSTS70043: Refresh token expired or invalid due to sign-in frequency checks by conditional access`. | **Infeasible**: Expired session; interactive re-authentication disallowed by non-interactive operational rules. |
| **Power Platform CLI** (`pac`) | `/Users/doughnut/.dotnet/tools/pac` | **Active, but Wrong Tenant:** Connected to `RIMS maintainer (Illawarra Shoalhaven LHD)'s Environment` (NSW Health, `health.nsw.gov.au`). | **Infeasible**: Connected to external NSW Health tenant, not Queensland Health. Switching profiles would require interactive device code login. |
| **Azure CLI** (`az`) | `/opt/homebrew/bin/az` | **Active, but Wrong Tenant:** connected to a personal/other Azure subscription (tenant identifier retained only in private evidence). | **Infeasible**: not connected to Queensland Health enterprise tenant. |

### Architectural Decision:
Per user directive, **no further attempts to log in or run CLI tenant tools will be made**. All platform interactions proceeded strictly through RIMS maintainer's active, enterprise SSO-authenticated browser session (`playwright-cli -s=chrome`).

---

## 3. Gap Analysis: Local Completion vs. Platform Deployment

The platform completion scope was decomposed by concern and ranked strictly from **highest operational value** to **lower analytical dependencies**:

```
Value Hierarchy & Deployment Status:
┌────────────────────────────────────────────────────────────────────────┐
│ Tier 1 (Highest Value): Central Research Data Persistence & Review     │ [LOCAL COMPLETE; NATIVE OPEN]
│ - SharePoint List "Publication Registry" (identifier held privately)   │
│ - Schema/seed/reconciliation implemented; current row readback open     │
├────────────────────────────────────────────────────────────────────────┤
│ Tier 2 (High Value): Automated Cloud Ingestion & Daily Enrichment      │ [LOCAL COMPLETE; NATIVE OPEN]
│ - Power Automate Flow in-place update (identifier held privately)       │
│ - OpenAlex HTTP enrichment; idempotent upsert into List; zero sprawl   │
├────────────────────────────────────────────────────────────────────────┤
│ Tier 3 (Medium-High Value): Executive Word (DOCX) Reporting            │ [100% COMPLETED]
│ - Queensland Health branded monthly reports with KPIs & citations     │
│ - Verified report for August 2026 (reports/CHHHS-Publications-...)     │
├────────────────────────────────────────────────────────────────────────┤
│ Tier 4 (Medium Value): Power BI Analytics & Cross-Source Model         │ [LOCAL COMPLETE; NATIVE OPEN]
│ - Research model and 3-page report (identifiers held privately)         │
│ - Local DAX/visual contracts pass; native refresh/readback remain open  │
└────────────────────────────────────────────────────────────────────────┘
```

### Detailed Component Gap Matrix:

| Tier & Concern | Local Engineering Status | Live Platform Status | Platform Completion Evidence |
| :--- | :--- | :--- | :--- |
| **Tier 1: SharePoint Data Store** | • 34-column schema, seed/export scripts, and reconciliation contracts are local. | • Native list identity, row count, versioning, and views require current readback. | **Local complete; native acceptance open.** |
| **Tier 2: Power Automate Ingestion** | • Flow definition, explicit SharePoint target, and fail-closed upsert contract are local. | • Native flow identity, connection references, successful run, and row readback require current evidence. | **Local complete; native acceptance open.** |
| **Tier 3: Executive DOCX Reports** | • DOCX generator and local reports are reproducible and tested. | • Publication or distribution is not claimed by local artefacts. | **Local complete; delivery acceptance is separate.** |
| **Tier 4: Power BI Research Model** | • Local model/report definitions and DAX checks are available. | • Native model, refresh, report pages, and complete export reconciliation require current readback. | **Local complete; native acceptance open.** |

---

## 4. Phased Platform Completion Plan

### Phase 1: SharePoint Publication Registry (Highest Value)
*Objective: Give CHHHS immediate operational capability to view, search, review, and export all 1,265 publications.*

- **Action 1.1: Import Enriched Seed Dataset**
  - Open Chrome Tab 1: `{{SHAREPOINT_PUBLICATION_REGISTRY_URL}}`
  - Click **+ New** / **From CSV** and select:
    `/Volumes/PortableSSD/GitHub/RIMS/chhhs-research-publications/private/ops/sharepoint-seed/publication-registry-seed.csv`
  - Verify column mappings:
    - `Title` -> Single line of text
    - `SourceKey`, `CanonicalKey`, `PMID`, `DOI` -> Single line of text
    - `Authors`, `MatchedFacilities`, `AttributionEvidence` -> Multiple lines of text
    - `PublicationYear` -> Number
    - `ReviewStatus` -> Choice (`Included`, `Needs Review`, `Excluded`)
    - `OpenAccessStatus` -> Choice
    - `CitationCount_OpenAlex`, `CitationCount_Crossref` -> Number
    - `FunderNames`, `GrantIDs` -> Multiple lines of text
  - Complete import (1,265 rows).

- **Action 1.2: Enforce 500 Major Versions**
  - Navigate to **List Settings** > **Versioning Settings**.
  - Ensure **Create a version each time you edit an item in this list?** is set to **Yes**.
  - Set **Keep the following number of major versions** to **500**.
  - Click **OK**.

- **Action 1.3: Configure Specialized Views**
  - Create View: **"Past Month Publications"**
    - Filter: `ReviewStatus` is equal to `Included` AND `PublicationYear` is equal to current year.
    - Sort: `PublicationYear` (Descending), then `PublicationMonth` (Descending).
    - Columns: `Title`, `Authors`, `Journal`, `PublicationMonth`, `MatchedFacilities`, `OpenAccessStatus`, `CitationCount_OpenAlex`, `PubMedURL`.
  - Create View: **"Matched Facilities"**
    - Group By: `MatchedFacilities`.
  - Create View: **"Needs Review"**
    - Filter: `ReviewStatus` is equal to `Needs Review`.

---

### Phase 2: Power Automate Daily Ingestion & Enrichment (High Value)
*Objective: Automate daily background discovery and enrichment into the SharePoint List without creating duplicate flow sprawl.*

- **Action 2.1: Import Updated Ingestion Package In-Place**
  - Open Chrome Tab 2: `https://make.powerautomate.com/environments/Default-{{TENANT_ID}}/flows`
  - Click **Import** > **Import Package (Legacy)**.
  - Upload file:
    `/Volumes/PortableSSD/GitHub/RIMS/chhhs-research-publications/private/ops/flow-packages/sharepoint-upsert.zip`
  - In the import review screen:
    - For the flow resource, select **Update** (select existing flow `CHHHS Publications - DEV manual ingestion validation`, GUID `{{FLOW_ID}}`).
    - For connection references, select RIMS maintainer's existing SharePoint connection and standard HTTP connector.
  - Click **Import**.

- **Action 2.2: Test & Activate Flow**
  - Open the updated flow in edit mode.
  - Confirm the presence of the `HTTP_OpenAlex_Enrichment` action and the updated `Create item` / `Update item` mappings for `FunderNames`, `GrantIDs`, `CitationCount_OpenAlex`, and `OpenAccessStatus`.
  - Perform a manual test run to verify execution without error.

---

### Phase 3: Executive Monthly Word Reporting (Medium-High Value)
*Objective: Deliver professional, branded monthly publication digests for clinical directors and research committees.*

- **Action 3.1: Generate On-Demand Executive Digest**
  - Command:
    ```bash
    python3 scripts/export_monthly_docx.py --month 2026-08
    ```
  - Report output: `reports/CHHHS-Publications-Monthly-2026-08.docx`
  - Content:
    - Executive KPI Cards (Total Publications, Open Access %, Top Hospital, Top Funder).
    - Hospital Breakdown Table (Cairns Hospital, Hinterland facilities).
    - Primary Source Breakdown (PubMed, DORA, Cross-source).
    - Full hyperlinked bibliographic citations with PubMed and DOI links.

---

### Phase 4: Power BI Semantic Model & Research Dashboards (Medium Value)
*Objective: Provide interactive 3-page executive research analytics and cross-source reconciliation.*

- **Action 4.1: Apply Clean Research TMDL Model**
  - Open Chrome Tab 5: `https://app.powerbi.com/groups/me/modeling/{{ISOLATED_MODEL_ID}}/modelView?experience=power-bi`
  - In the modeling view, open the TMDL Scripting panel.
  - Paste the contents of:
    `/Volumes/PortableSSD/GitHub/RIMS/chhhs-research-publications/private/ops/2026-09-15-t12-model.tmdl`
  - Click **Apply Script** to deploy the 6-table research schema (`Publication`, `Facility`, `PublicationFacility`, `Date`, `SearchAudit`, `ReportingWindow`), cleanly replacing the legacy workforce model.

- **Action 4.2: Execute DAX Reconciliation Verification**
  - In Power BI Service DAX Query View, paste and run:
    `/Volumes/PortableSSD/GitHub/RIMS/chhhs-research-publications/config/native-canonical-check.dax`
  - Verify that:
    - `DuplicateCanonicalKeys` = 0
    - `HeadlineMatchesKeys` = TRUE
    - `SourceCountBalance` = TRUE

- **Action 4.3: Validate Three-Page Research Visuals**
  - Switch to Report View and confirm that the three pages render cleanly:
    1. **CHHHS Publications:** Headline metrics, facility breakdown, publication register table.
    2. **Monthly Publications:** Last complete month KPI, YoY growth, monthly trend.
    3. **Source Reconciliation:** PubMed vs DORA coverage, cross-source matches, attribution evidence.
  - Confirm that zero visuals display broken field error icons.

---

## 5. Incorporation into Conductor Tracks Register

This phased roadmap aligns directly with the established Conductor tracks:

- **Track T11 (Sources & Reconciliation):** Governs SharePoint List population (Phase 1) and Power Automate flow update (Phase 2).
- **Track T12 (Research Model):** Governs Power BI Service Model View TMDL deployment (Phase 4.1) and DAX query checks (Phase 4.2).
- **Track T13 (Web Visuals):** Governs three-page report visual validation (Phase 4.3).
- **Track T14 (Complete Exports & Monthly):** Governs executive Word DOCX report generation (Phase 3).
- **Track T15 (Web Acceptance & Release):** Governs the final live platform sign-off, concurrency check, and handover documentation.
