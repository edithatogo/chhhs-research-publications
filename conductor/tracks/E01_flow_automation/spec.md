# Specification: E01 Power Automate Ingestion Canonicalization and Recurrence Scheduling

## Controlling execution scope — 21 October 2026

The selected publications operator-run slice and later collector/monitor
configuration increments have retained native acceptance. The original daily
production schedule/name and fixed one-hour refresh offset below are historical
proposal/implementation context, not a current activation instruction. E01's
[plan](plan.md#full-e01-goal-resumed--21-october-2026) controls technical
implementation and native controlled qualification. Later natural occurrence and
elapsed operating-window checks are transferred by user direction to
E08 operational follow-up. E01 does not wait for those dates;
its unresolved native access/adoption/recovery requirements remain real gates.
ClinicalTrials retry adoption, bounded affected-path runtime and exact weekly
restoration are accepted. Crossref pacing adoption and source-drift failure
preservation pass; complete query-prefix recovery and broader native gates
remain tracked in the plan. All delivery remains cross-platform web/API.


## 1. Overview & Business Value
Power Automate cloud flow `{{FLOW_ID}}` was initially configured with a manual button trigger and development nomenclature (`"CHHHS Publications - DEV manual ingestion validation"`). This caused operational uncertainty because the flow did not execute autonomously on schedule.

This track establishes the **single canonical production version** of the ingestion flow:
- Renamed cleanly to `CHHHS Research Publications - Daily Ingestion & Enrichment`.
- Replaces the manual trigger with a daily recurrence trigger scheduled at **06:00 AEST (20:00 UTC)**, precisely 1 hour prior to the Power BI dataset scheduled refresh at **07:00 AEST**.
- Retains idempotent upserts into the Queensland Health SharePoint publication registry (`{{SHAREPOINT_LIST_ID}}`).
- Continues token-free OpenAlex citation enrichment and field-level auditing.

## 2. Functional Requirements
1. **Recurrence Trigger:**
   - Type: `Recurrence`
   - Frequency: `Day`, Interval: `1`
   - Schedule: `hours: ["20"]`, `minutes: [0]`, `timeZone: "UTC"` (06:00 AEST daily).
2. **Canonical Nomenclature:**
   - Flow Display Name: `CHHHS Research Publications - Daily Ingestion & Enrichment`.
   - Manifest Resource Display Name: `CHHHS Research Publications - Daily Ingestion & Enrichment`.
3. **Upstream & Downstream Alignment:**
   - Executes at 06:00 AEST to harvest new citations and write to SharePoint.
   - Power BI dataset scheduled refresh triggers at 07:00 AEST daily with `notifyOption: MailOnFailure` to digest the freshly written SharePoint records into VertiPaq.
4. **Zero-Sprawl Deployment:**
   - Package generator (`scripts/build_sharepoint_upsert_package.py`) updates the existing flow definition in-place without generating orphan cloud logic flows.

## 3. Acceptance Criteria
- [x] Flow definition `config/flows/publication-registry-upsert.definition.json` contains recurrence trigger at 20:00 UTC and canonical display name.
- [x] `config/flows/manifest.template.json` reflects canonical display name.
- [x] `scripts/build_sharepoint_upsert_package.py` packages definition into `private/ops/flow-packages/sharepoint-upsert.zip`.
- [x] Zip package verified containing Recurrence trigger and canonical title.

## Current maturity and completion contract — 2026-09-24

Historical checked criteria describe the recorded local implementation or historical native observation; they do not certify current production or unattended acceptance. The numbered hardened tasks in [this track's plan](plan.md) are mandatory remaining acceptance work under the [shared hardened completion contract](../../../docs/PLATFORM_COMPLETION_PLAN.md#hardened-completion-contract). Each task records its input generation, target identity, expected-versus-actual result, terminal status, rollback and private evidence pointer; unexplained differences leave the task open.

Use existing source artefacts and discovered tenant objects. Synthetic-only personal/university development can qualify portable artefacts, but Queensland Health import, connection rebinding, native execution, permissions and data parity must be accepted in the destination. Keep live rows/contact fields, tenant identifiers and credentials outside Git and external development accounts. Local packaging or a successful test suite never closes a native gate.

The existing canonical flow is currently a DEV acceptance target, not proof of a production service. A fixed daily time or fixed offset from refresh is a proposal unless separately evidenced/approved; downstream work must depend on actual successful source/batch/refresh completion. Completion requires minimal export-patch-update promotion, observed internal-field mappings, generic string identifiers, create/replay/update and concurrency protection, bounded failure recovery and consecutive native cycles. E07 owns whole-list and integrated acceptance.

## CLI and shared data-space requirements — 13 October 2026

Implement shared authorised raw-payload/schema retention before typed publication
filtering under the existing plan, with immutable source identity, acquisition
time, batch provenance and replay. Preserve accepted historical evidence, source
uncertainty, corrections and existing target IDs. The plan's CLI delivery section
defines scoped authoring and native acceptance; solution import alone does not
prove flow runtime adoption. Source acquisition scope and effective permissions
remain explicit; no hosted Python runtime, new physical lake or broad source
expansion is implied. Publications is first; report presentation comes last.

## Requirements refined from source-capture lessons — 13 October 2026

Durable raw/rejected staging is distinct from the accepted commit marker. Only a
complete correlated generation with passing current source/typed audits and
qualified R1 freshness may advance consumers or trigger digest delivery. Preserve
last-good accepted history on source/schema/decode/partial-write failure. CLI
import/read access does not establish saved active runtime adoption, connector
execution or archive correctness; those require exact native readback and run proof.

See [the observed lessons and execution changes](../../../docs/SOLO_AGENT_WORKFLOW.md#source-capture-lessons--13-october-2026).
