# Implementation plan

- [x] Record scope and acceptance requirements.
- [x] Inspect current inputs, dependencies and relevant platform objects. The canonical G01 mapping and existing publication SharePoint conventions were inspected; no live grants object was found/read back in this tranche.
- [x] Implement: Generate the explicit additive `Grants Registry` schema and Power Query read definition with `OpportunityKey` as the only local identity.
- [~] Verify: Local schema/mapping parity is tested and the isolated DEV list has been created and read back with synthetic create/update/duplicate/concurrent-create/delete evidence; organisation-wide target approval, flow binding and unattended acceptance remain open.
- [x] Record local and live evidence separately before closure; no tenant write was performed.
