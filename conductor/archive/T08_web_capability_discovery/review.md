# Track Review: T08 Web Capability Discovery

**Track:** `T08_web_capability_discovery`  
**Status:** Complete  
**Date:** 2026-09-14  
**Agent Environment:** Google Antigravity CLI (`agy`) pair-programming session with Power BI browser workflow (installed skill v0.1.4)  

---

## Executive Summary

Track T08 has successfully discovered and verified the existing Power BI report and semantic model capabilities, establishing the **`web_first` route** without Fabric Git or capacity dependencies.

The agent environment transition from Codex to **Google Antigravity (`agy`)** is documented and integrated with the repository's `.agents/skills/`, `.agents/rules/`, and `AGY_HANDOVER.md`. All 7 required operations defined in `contracts/web-first-execution.contract.json` have been evaluated and mapped to verified web and assisted-webui operations in `private/ops/capabilities.json`.

---

## Verified Evidence & Discoveries

1. **Target Identification & Lineage:**
   - Existing Report ID: `{{REPORT_ID}}`
   - Workspace ID: `{{WORKSPACE_ID}}` (Queensland Health / My workspace)
   - Underlying Semantic Model ID: `{{PRODUCTION_MODEL_ID}}` ("CHHHS Research Publications - adapted")
   - The separate "Research" model (`{{UNLINKED_MODEL_ID}}`) is unlinked and contains only an empty Query table.
   - Evidence: `private/ops/2026-09-12-discovery.json`, `private/ops/2026-09-12-user-targets.json`.

2. **Metadata & Permissions Inventory:**
   - Permissions: Workspace Admin role, direct access count 1, all permissions granted.
   - Model structure: 9 legacy tables (`Date`, `Employee`, `Ethnicity`, `Gender`, `Employee type`, `Business unit`, `Pay type`, `Age`, `Separation reason`), 8 relationships, hidden `Employee` table.
   - Storage mode: Import.
   - Security discipline: Metadata-only inspection; zero legacy employment row data exported to Git or third-party tools.
   - Evidence: `private/ops/2026-09-12-discovery.json`, `docs/RECONCILIATION_GAP_ANALYSIS.md`.

3. **Capability Mapping & Route Selection:**
   - `read_report`: `webui` (verified, `private/ops/2026-09-12-discovery.json`)
   - `read_model`: `webui` (verified, `private/ops/2026-09-12-discovery.json`)
   - `edit_report`: `webui` (verified on isolated copy, `private/ops/isolated-baseline-observation.json`)
   - `edit_model`: `webui` (verified on isolated copy, `private/ops/isolated-baseline-observation.json`)
   - `edit_power_query`: `webui` (verified on isolated copy, `private/ops/2026-09-13-native-cloud-repair.json`)
   - `refresh`: `webui` (verified on isolated copy, `private/ops/2026-09-14-native-refresh.json`)
   - `export_rows`: `assisted_webui` (available via Power Automate dataset query action, `private/ops/2026-09-14-powerautomate-query-proof.json`)
   - Policy evaluation: `python3 scripts/webfirst_contracts.py route --input private/ops/capabilities.json` produces `"route": "web_first"` with 0 missing operations.
   - Evidence: `private/ops/capabilities.json`, `private/ops/2026-09-14-route-check.json`.

4. **Power Platform & Licensing Observations:**
   - Standard cloud connectors enabled in Power Automate; standard Power BI "Run a query against a dataset" action verified against My workspace in `private/ops/2026-09-14-powerautomate-query-proof.json`.
   - Licensing documented in `docs/POWER_PLATFORM_NATIVE_PLAN.md`.
   - Conditional UTM Windows VM fallback (`T16`/`T17`) remains gated and unnecessary.

---

## Acceptance Criteria Checklist

- [x] **Exact existing report and model IDs are recorded privately:** Verified in `private/ops/2026-09-12-discovery.json` and `private/ops/2026-09-12-user-targets.json`.
- [x] **Each required capability has actual tool or UI evidence:** All 7 operations evaluated and backed by private operational logs.
- [x] **A documented operation-by-operation route is selected without Fabric Git/capacity prerequisites:** `web_first` route selected and contract-validated.

---

## Automated Policy & Test Gates

- `python3 -m unittest discover -s tests -v`: **163 / 163 unit tests pass**
- `python3 scripts/validate_project.py`: **235 / 235 local project checks pass**
- `python3 scripts/webfirst_contracts.py validate`: **PASS_LOCAL_ONLY (all checks pass)**
- `python3 scripts/webfirst_contracts.py route --input private/ops/capabilities.json`: **`web_first` route confirmed (exit 0)**

---

## Next Steps

T08 is complete. Active implementation continues in:
- [`T10_isolated_baseline`](../T10_isolated_baseline/plan.md): Protect the existing report and finalize development model isolation.
- [`T11_sources_and_reconciliation`](../../tracks/T11_sources_and_reconciliation/plan.md): Complete native PubMed/DORA ingestion and connect reporting queries to committed history.

## Conductor review recheck — 2026-09-23

The track remains complete. All T08 plan items are checked, the capability
route evidence remains present, and no T08-specific native acceptance task is
outstanding. Current downstream native gaps are deliberately owned by T11,
T14, T15, E01, E04 and E07 rather than being folded back into discovery.

Verification: `python3 scripts/validate_project.py` and
`python3 scripts/validate_conductor.py` pass in the canonical checkout; the
broader source-only test/CI gates are current on `origin/main`. T08 is
eligible for archive.

The archive move exposed and corrected a validator assumption that all T08–T17
assets had to remain under `conductor/tracks`. The web-first contract now
counts those canonical assets across both active and archived collections;
the targeted 64-test web-first suite and local validators pass after the fix.
