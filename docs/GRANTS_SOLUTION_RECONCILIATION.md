# Grants solution and documentation reconciliation — 24 October 2026

## Export and portable source

A fresh PAC export of the canonical unmanaged CHHHS RIMS Platform solution is retained privately, with CRC and duplicate-entry checks. Its native solution version remains **1.0.0.0**. This version is distinct from the repository software version, source schema version and SharePoint document version; none was silently incremented to imply a new overall release.

The export contains **35 workflows and six connection references**. Every workflow in the prior 34-workflow export remains present; the additional member is the existing Crossref qualification flow. Other lanes' source changes are preserved in the export, not replaced with older local definitions. Standalone OpenCitations remains outside this solution. No import, component removal, reference rebinding or shared solution version change was performed.

The exported grants definition also matches a fresh direct native flow readback. Its portable authored definition matches `config/flows/grants-registry-reviewed-import.definition.json` after substituting only the exact SharePoint site/list bindings and removing the generated manual-trigger operation ID. Four older repository authentication expressions were aligned to the working native invoker expressions. Authentication, deadline guards, review-field exclusions and every other authored expression are compared, not normalized away. The flow remains Off.

The reproducible export comparison is `scripts/reconcile_grants_solution_export.py`. Raw ZIPs, native bindings and complete exports remain ignored private evidence. The sanitized [reconciliation manifest](https://github.com/edithatogo/research-publications/blob/main/contracts/grants-solution-reconciliation-20261024.json) records fingerprints and scoped outcomes without tenant identifiers.

## Accepted grants evidence

- [Source admission](https://github.com/edithatogo/research-publications/blob/main/docs/NIH_SOURCE_ADMISSION.md): one exact NIH opportunity, official attribution and retained source scope.
- [Import and same-input replay](https://github.com/edithatogo/research-publications/blob/main/docs/NIH_BOUNDED_IMPORT.md): 32 registry fields, seven nominal occurrences, four byte-verified original response attachments, no duplicate and exact review-note preservation; original note restored.
- [Changed deadlines and last-good preservation](https://github.com/edithatogo/research-publications/blob/main/docs/GRANTS_LAST_GOOD_ACCEPTANCE.md): seven native fixture cases and three source-admission rejection checks; last accepted data/version preserved and the synthetic fixture recycled.
- [Isolated-model reconciliation](https://github.com/edithatogo/research-publications/blob/main/docs/GRANTS_MODEL_REFRESH_ACCEPTANCE.md): transactional refresh of two grants partitions; one parent, seven distinct related occurrences, zero orphans; all 27 other table counts and 37 model definition parts preserved.

The effective application deadlines remain unresolved. Nominal dates and applicant-local 17:00 are retained without invented timezone, UTC instant or holiday adjustment. Announcement boundaries remain separate.

## Versioned documentation boundary

This maintained source is mirrored as `RIMS-Grants-Acceptance-20261024.md` in the existing versioned RIMS documentation library. Saved bytes, file identity, version and inherited access are read back; exact native destinations and receipts remain private. Existing field guide, catalogue, Loop content and documentation marker retain their identities, bytes and history.

The shared marker describes an older captured documentation generation; its grants diagram is explicitly labelled a historical R17b snapshot. This addendum records current grants evidence without relabelling every shared diagram as a fresh live readback. The field-guide source advanced from recorded version 15.0 to observed 16.0 with identical accepted bytes; that version-only drift is retained, not overwritten. Other lanes retain their documentation objects.

This reconciliation does not close unattended source acquisition/archival, recurring refresh or delivery, multirow source-write transaction recovery, concurrent-writer acceptance, main-report replacement or overall release/business acceptance. Existing release history and global acceptance flags are preserved.
