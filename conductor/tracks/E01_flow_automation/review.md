# Track Review: E01 Power Automate Ingestion Canonicalization and Recurrence Scheduling

## Implementation Summary
1. **Flow Definition Canonicalized:**
   - File: `config/flows/publication-registry-upsert.definition.json`
   - Name: `CHHHS Research Publications - Daily Ingestion & Enrichment`
   - Trigger: `Recurrence` daily at 20:00 UTC (06:00 AEST).
2. **Manifest Template Canonicalized:**
   - File: `config/flows/manifest.template.json`
   - Name: `CHHHS Research Publications - Daily Ingestion & Enrichment`
3. **Build Script & Deployable Package:**
   - Generator: `scripts/build_sharepoint_upsert_package.py` updated to inject the recurrence trigger.
   - Package: `private/ops/flow-packages/sharepoint-upsert.zip` generated and verified.
4. **Platform Handshake:**
   - The flow runs 1 hour prior to the dataset refresh at 07:00 AEST, ensuring the Power BI model consumes the latest daily SharePoint upserts.

## Native DEV flow test — 2026-09-20

The current Power Automate environment was inspected through authenticated
Playwright UI readback. The active history-commit DEV flow completed all six
actions successfully after changing both text failure markers from `int(...)` to
plain text. Flow Checker returned zero errors and zero warnings. The manual
ingestion DEV flow completed its Power BI query, SharePoint `Get items`,
new-publication condition and the True-branch `SharePoint Create item`
successfully; the False-branch update was skipped for the new row. Its list
action read back HTTP 200 from the configured `Publication Registry` list. That
flow was restored to Off after the manual test. The private run evidence is
`private/ops/2026-09-20-powerautomate-publication-flow-tests.json`.

This closes current DEV/manual execution evidence only. It does not close the
recurrence deployment, unattended schedule, full registry reconciliation or
production release gates.

The controlled replay also succeeded but again took the Create branch and skipped
Update. The observed blank SourceKey filter means this is not idempotency proof;
duplicate prevention and a nonblank-key update readback remain open.

## Review remediation — 2026-09-20

The first source-only review found that the tracked JSON definition and generated
package were not the same action graph. The readiness query returned a single
summary row, while the loop treated it as a publication; this explains the
blank `SourceKey` filter observed in the native replay. The tracked definition
and builder now share the corrected graph: readiness, a dedicated canonical
`Publication` rows query, a serial upsert loop, duplicate-key fail-closed
handling, and the protected update allowlist.

Local verification: `python3 scripts/validate_publication_platform_contract.py`,
JSON parsing, and the full unittest suite (283 tests) pass. This is still
source-only evidence. The isolated tenant deployment and create/replay/update,
duplicate, failed-batch, recurrence and reconciliation readback tasks remain
open, so the track remains in progress and must not be archived yet.

The corrected package was subsequently imported into the existing DEV manual-flow
identity. Power Automate readback showed the canonical flow name, the
`Recurrence -> readiness -> publication rows -> Apply to each Publication`
chain, Flow Checker `Errors (0)` and `Warnings (0)`, and the flow Disabled.
The actual recurrence run remains gated because activation requires explicit
approval.
