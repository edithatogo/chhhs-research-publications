# Start here in the chat with the Power BI plugin

The user supplied the exact existing report and development-folder links on 2026-09-12. They are recorded in ignored `private/ops/2026-09-12-user-targets.json`; do not copy these identifiers into tracked files. The Microsoft Power BI plugin is a browser workflow (installed skill version 0.1.4), and local Chrome access to both targets was observed. Semantic-model lineage and persistent write capabilities remain unverified. The report already exists in your Power BI account; do not create a Fabric Git project or purchase capacity.

Read [the initial reconciliation status](../docs/RECONCILIATION_STATUS.md) before continuing T08. The private pointer is local-only and will not accompany a Git checkout.

## Opening prompt

> Continue the CHHHS research-publications project in this package. Read `conductor/index.md`, `conductor/workflow.md`, `contracts/web-first-execution.contract.json` and the T08 specification and plan. Use my existing Power BI report and its actual semantic model. Try my Power BI plugin and the ordinary Power BI Service web UI first. UTM with my existing Windows 11 copy is a conditional fallback only. Start read-only: list your actual tool schemas, identify the exact existing report/model IDs, inspect their lineage, permissions, pages, filters, tables, hidden metadata, queries and measures, and tell me which report-editing and semantic-model/Power Query editing operations are actually available. Do not claim that querying data or producing code proves editing. Do not modify or duplicate data yet. Record a capability manifest and proceed to a recoverable isolated development model in T10 before any persistent write. A report copy can still point to the original model. Implement dependency-satisfied tracks incrementally; test/read back every change. Do not mark native, refresh, export, PBIX or automation acceptance complete without actual evidence. No sharing, production rebind, mail send, capacity purchase, flow activation or VM changes without the relevant approval. Preserve exactly the three publication-report pages and the full PubMed+DORA canonical bibliography. Address the known defects in `docs/WEB_FIRST_FINDINGS.md` rather than trusting prior completion claims.

## Practical execution order

T08 discovery → T10 protected baseline/canary → T11 source repair/reconciliation → T12 research model → T13 three report pages → T14 full exports and monthly dry run → T15 native web acceptance.

T09 is local work-package implementation and does not require a Power BI account. T16/T17 remain gated unless a real web-authoring blocker is evidenced and fallback is activated.

## First response expected from the plugin-enabled session

Report the exact plugin/provider, supported actions, selected report and semantic model, current three-page/legacy audit state, effective permissions, and any blocker. Put real IDs/evidence in `private/ops/`, not a public repository. Do not expose old workforce row data to a third-party provider; metadata is enough for the audit. Ask for the exact report only if the tool inspection cannot uniquely resolve it.

## When the plugin lacks a write operation

Use a documented web UI step for the missing operation when the UI supports it. Provide the exact M/DAX snippet and its intended location, then obtain a read-back or user screenshot of the result. Do not substitute made-up tool calls. A missing plugin capability alone is not a failed web route.

## Stop conditions

Unknown target; shared original model; no recoverable baseline; missing permission; tenant policy; unreviewed concurrent edits; unexpected source schema; incomplete exports; failed native query. Record the specific condition and leave the task unchecked. No security or tenant-control workarounds.

Latest update: [protected development baseline](../docs/PROTECTED_DEVELOPMENT_BASELINE.md) records restored browser access, PBIX recovery and successful isolated model/report canary rollbacks. Earlier browser-denial notes are historical.
