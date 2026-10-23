# Historical desktop scope — cancelled 21 October 2026

Retained for provenance only. All unfinished assessments below are cancelled, not pending or completed technical work.

# T17_desktop_fallback_acceptance: Author and save a native PBIX in the Windows VM

## Outcome
Install the regular Power BI Desktop app, complete only the authoring operations that the web route could not perform, and validate a genuine native PBIX. Reuse the same data, report and export contracts.

## Dependencies
T09_execution_contracts; T16_utm_windows_fallback only if the existing VM is selected. An existing authorised Windows computer follows the same read-only preflight and acceptance boundaries.

## Acceptance criteria
- The regular Desktop app runs and the saved self-contained PBIX reopens successfully.
- Actual PubMed/DORA refresh and report rendering pass in the guest.
- The same source, publication, date, legacy-exclusion and export contracts pass.
- No unapproved publish/rebind/schedule action occurs.

## Evidence boundary
Conditional only. Existing native-acceptance work is consolidated here; a working web report does not need this track.

## Safety and scope
Read `conductor/workflow.md` and `contracts/web-first-execution.contract.json`. Preserve the existing report/model until an approved, isolated write path and rollback are proven. Do not require Fabric Git integration, capacity purchase, public publishing or a new repository. Do not enter or expose credentials in Git or this pack.

Timing: later/conditional Power BI presentation and genuine native PBIX acceptance. Current Mac data/cloud-flow/document work does not depend on this track; no device or fallback activation is inferred from planning. Use the current approved page contract, not a historical fixed page count.
