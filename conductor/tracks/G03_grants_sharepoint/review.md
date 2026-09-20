# G03 review

Review status: in progress; the isolated DEV list/schema/create-update-duplicate-readback gate is evidenced, while organisation-wide target acceptance and grants-flow binding remain open.

The completed local G01 prerequisite is archived at `conductor/archive/G01_grants_contracts`; G03 has no unresolved active-track dependency.

## Changes

- Added `config/grants-registry.schema.json` for one canonical `Grants Registry` list with `OpportunityKey` as the indexed identity.
- Added `config/GrantsRegistry.m` using the SharePoint Online connector and preserving partial/unknown deadlines as text plus raw source values.
- Added schema/mapping parity tests; the local map and schema contain the same 22 persisted fields.
- Added `config/flows/grants-registry-reviewed-import.definition.json`, a
  SharePoint-only manual reviewed-row JSON upsert definition with serial
  processing, duplicate-key guard and review-field preservation. Its target
  site/list remain placeholders until the native flow is intentionally
  imported.

## Remaining acceptance

The isolated DEV route is now implemented and read back. The remaining gate is
to decide and approve the organisation-wide target, then bind the grants flow
to this canonical list or its approved successor. Do not use OneDrive actions
for registry writes.

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
