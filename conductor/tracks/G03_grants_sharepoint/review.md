# G03 review

Review status: in progress; local schema and read definition are implemented, while tenant object discovery and readback remain open.

The completed local G01 prerequisite is archived at `conductor/archive/G01_grants_contracts`; G03 has no unresolved active-track dependency.

## Changes

- Added `config/grants-registry.schema.json` for one canonical `Grants Registry` list with `OpportunityKey` as the indexed identity.
- Added `config/GrantsRegistry.m` using the SharePoint Online connector and preserving partial/unknown deadlines as text plus raw source values.
- Added schema/mapping parity tests; the local map and schema contain the same 22 persisted fields.

## Remaining acceptance

Resolve the authenticated SharePoint site, inspect whether `Grants Registry` exists, create it only if absent, then prove isolated create/replay/update/readback and serial unique-key handling. Do not use OneDrive actions for registry writes.
