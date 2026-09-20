# Implementation plan

- [x] Record scope and acceptance requirements.
- [x] Inspect current inputs, dependencies and relevant platform objects. The canonical G01 mapping and existing publication SharePoint conventions were inspected; no live grants object was found/read back in this tranche.
- [x] Implement: Generate the explicit additive `Grants Registry` schema and Power Query read definition with `OpportunityKey` as the only local identity.
- [~] Verify: Local schema/mapping parity is tested and the isolated DEV list has been created and read back with synthetic create/update/duplicate/concurrent-create/delete evidence. The reviewed-import flow has also been imported and read back Off with native Flow Checker 0/0; a controlled authenticated DEV replay proved synthetic create and same-key update, with the flow restored Off. The native diagnostic expression is now corrected and read back with Flow Checker 0/0; organisation-wide target approval, flow binding to the approved target and unattended acceptance remain open.
- [x] Record local and live evidence separately before closure; isolated DEV writes were synthetic fixtures only and were deleted.

## Phase: Review fixes
- [x] Task: Apply review corrections for the controlled native replay and preserve the remaining acceptance boundary (0536b98).
