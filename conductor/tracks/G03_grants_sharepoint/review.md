# G03 review

Review status: in progress; the isolated DEV list/schema/create-update-duplicate-readback and reviewed-import flow import/readback gates are evidenced, while organisation-wide target acceptance, execution and unattended acceptance remain open.

The completed local G01 prerequisite is archived at `conductor/archive/G01_grants_contracts`; G03 has no unresolved active-track dependency.

## Changes

- Added `config/grants-registry.schema.json` for one canonical `Grants Registry` list with `OpportunityKey` as the indexed identity.
- Added `config/GrantsRegistry.m` using the SharePoint Online connector and preserving partial/unknown deadlines as text plus raw source values.
- Added schema/mapping parity tests; the local map and schema contain the same 22 persisted fields.
- Added `config/flows/grants-registry-reviewed-import.definition.json`, a
  SharePoint-only manual reviewed-row JSON upsert definition with serial
  processing, duplicate-key guard and review-field preservation. The private
  package builder injects the isolated DEV target without storing tenant IDs in
  tracked files.
- Added `scripts/build_grants_flow_package.py` and package-contract tests. The
  package was imported successfully as `CHHHS Research Grants - Reviewed Import
  Upsert` in the isolated DEV environment and read back with the SharePoint
  connection selected. Power Automate Flow Checker reported 0 errors and 0
  warnings in the editor; the details page reports one warning solely because
  the flow is intentionally Off.

## Remaining acceptance

The isolated DEV route is now implemented and read back. The remaining gates
are to decide and approve the organisation-wide target, bind the grants flow
to this canonical list or its approved successor, and obtain explicit approval
for a controlled run/replay test. The imported flow has not been enabled or
run, so native row-level create/update execution, unattended operation and
production acceptance remain unproved. Do not use OneDrive actions for registry
writes.

## Native list inventory — 2026-09-20

Authenticated Playwright readback of the personal DEV SharePoint site first
confirmed that only `Publication Registry` existed. A new isolated `Grants
Registry` was then created, with versioning enabled (50 major versions), 21
custom fields, and `OpportunityKey` required/indexed/unique. The schema
readback matched the local text, URL, multiline and choice contracts.

A clearly labelled synthetic DEV fixture was created, read back, updated and
then deleted. The duplicate attempt was rejected by the unique key constraint;
the final matching-row count was zero. Full private receipt:
`private/ops/2026-09-20-grants-native-g03-receipt.json`.

The concurrency case was subsequently exercised with two simultaneous creates
for one key. Native SharePoint returned one `201` and one `500`
`SPDuplicateValuesFoundException`; one matching row was read back and then
removed, leaving zero matching rows. This proves the list-level uniqueness
guard for this isolated DEV target, not production concurrency acceptance.

This closes the isolated DEV list/schema gate only. The list is not an
organisation-wide production registry, and no grants flow or report was bound
to it in this step.

## Native reviewed-import flow readback — 2026-09-20

The reviewed-import package was accepted by the Power Automate import wizard
after correcting the SharePoint URL, choice-object and required-key payload
contracts. The created flow is an Instant/manual flow, is Off, has no run
history, uses the selected SharePoint Online connection, and exposes the
expected trigger, JSON parse, serial Apply to each, SharePoint Get items,
duplicate guard and create/update branches. The native editor Flow Checker
reported no errors or warnings; the details-page warning is the expected
inactive-flow warning. Full private receipt:
`private/ops/2026-09-20-grants-flow-import-readback.json`.
