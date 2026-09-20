# G03 review

Review status: in progress; the isolated DEV list/schema/create-update-duplicate-readback and reviewed-import flow import/readback gates are evidenced, while organisation-wide target acceptance, execution and unattended acceptance remain open.

## Controlled native replay — 2026-09-21

Using the authenticated Power Automate web UI, the imported instant flow was
temporarily enabled, run with one synthetic `OpportunityKey`, and restored to
`Off`. Flow Checker reported zero editor errors. Run
`08584116923018304855211342755CU17` succeeded for the create path. The
SharePoint `Grants Registry` readback showed the expected synthetic row and
key fields.

Run `08584116920125684835586408484CU25` succeeded for a same-key replay. The
SharePoint readback showed the same unique key with updated title, funder,
amount, retrieval timestamp and evidence hash, proving the update path. The
synthetic row remains in the private DEV list pending explicit confirmation
immediately before cloud deletion. No production or organisation-wide target
was touched.

The completed local G01 prerequisite is archived at `conductor/archive/G01_grants_contracts`; G03 has no unresolved active-track dependency.

## Changes

- Added `config/grants-registry.schema.json` for one canonical `Grants Registry` list with `OpportunityKey` as the indexed identity.
- Added `config/GrantsRegistry.m` using the SharePoint Online connector and preserving partial/unknown deadlines as text plus raw source values.
- Added schema/mapping parity tests; the local map and schema contain the same 22 persisted fields.
- Added `config/flows/grants-registry-reviewed-import.definition.json`, a
  SharePoint-only manual reviewed-row JSON upsert definition with serial
  processing, duplicate-key diagnostic and an exact-zero-match write guard,
  plus review-field preservation. The private
  package builder injects the isolated DEV target without storing tenant IDs in
  tracked files.
- Added `scripts/build_grants_flow_package.py` and package-contract tests. The
  package was imported successfully as `CHHHS Research Grants - Reviewed Import
  Upsert` in the isolated DEV environment and read back with the SharePoint
  connection selected. Power Automate Flow Checker reported 0 errors and 0
  warnings in the editor; the details page reports one warning solely because
  the flow is intentionally Off.

Review fix applied: the private package builder now requires a parseable HTTPS
site with a host and rejects unresolved `{{...}}` placeholders after target
substitution.

## Remaining acceptance

The isolated DEV route is implemented and read back, and the controlled
authenticated create/update replay is proven by the 2026-09-21 evidence above.
The remaining gates are to decide and approve the organisation-wide target,
bind the grants flow to this canonical list or its approved successor, and
prove unattended operation and production acceptance. Do not use OneDrive
actions for registry writes.

## Replay attempt — 2026-09-20

The requested controlled synthetic replay could not be started in that
checkpoint. The authenticated Chrome automation surface dropped while loading
the Power Automate details page, and a fresh headless `playwright-cli` session
redirected to Microsoft sign-in rather than inheriting the existing login.
No flow toggle, run, list write, or deletion was attempted after that point;
the flow therefore remains safely Off. This is an automation/authentication
bridge blocker, not evidence that the flow works or fails. Re-open the
authenticated session and repeat the create/readback/update/readback/delete
sequence before native execution can be accepted.

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

This section records the initial import/readback state. Its statement that the
flow had not been executed is superseded by the controlled replay recorded
above; the flow was restored to `Off` after that replay.

The reviewed-import package was accepted by the Power Automate import wizard
after correcting the SharePoint URL, choice-object and required-key payload
contracts. The created flow is an Instant/manual flow, was Off before the
controlled replay, uses the selected SharePoint Online connection, and exposes the
expected trigger, JSON parse, serial Apply to each, SharePoint Get items,
duplicate guard and create/update branches. The native editor Flow Checker
reported no errors or warnings; the details-page warning is the expected
inactive-flow warning. Full private receipt:
`private/ops/2026-09-20-grants-flow-import-readback.json`.

The duplicate branch is intentionally diagnostic rather than a nested
`Terminate` action: Power Automate rejects `Terminate` inside this
`Apply to each` scope. The following create/update condition is independently
guarded by `length(Get items.value) == 0`, so duplicate matches cannot write.
The local definition uses a non-throwing diagnostic string; the native
expression was corrected in the 2026-09-21 edit recorded below.

## Native diagnostic-expression correction — 2026-09-21

The isolated DEV flow was opened in the authenticated Power Automate editor.
`Compose Duplicate OpportunityKey Failure` was read back with the legacy
`int('DUPLICATE_OPPORTUNITY_KEY')` expression. It was changed to the plain
diagnostic string `DUPLICATE_OPPORTUNITY_KEY`, saved, and rechecked. Flow
Checker read back 0 errors and 0 warnings. The correction is recorded in the
ignored private receipt
`private/ops/2026-09-20-grants-flow-import-readback.json`.

This closes the native diagnostic-expression gate only. The isolated DEV
create/update evidence remains valid; the organisation-wide target,
canonical binding, unattended operation, delivery and production gates remain
open, so G03 remains in progress.

## Review Report: G03 Grants SharePoint — 2026-09-21

### Summary

The canonical isolated grants list and reviewed-import flow remain structurally sound, and the legacy native diagnostic expression has been corrected and checked in Power Automate. The track is not archivable because the approved organisation-wide target and operational acceptance are still absent.

### Verification Checks

- [x] Plan Compliance: Partial — isolated schema, create/update replay and diagnostic correction are evidenced; target binding and unattended gates remain open.
- [x] Style Compliance: Pass — SharePoint Online remains the registry connector and OneDrive is not used for registry writes.
- [x] New Tests: Existing contract and schema tests remain green; the native correction is covered by private UI evidence.
- [x] Test Coverage: Partial — local structure and isolated DEV behavior are covered; production/organisation-wide behavior is not.
- [x] Test Results: Passed — canonical-clone full suite (357 tests, 8 skipped), project validation (438 checks) and Conductor validation passed; Flow Checker read back 0 errors and 0 warnings after saving the correction.

### Findings

The review added regression coverage in `3fc2c2f` for the reviewed-import
flow's `GetItems`, `PostItem` and `PatchItem` operations and connector
authentication metadata. The open target/operational gates are acceptance
boundaries, not defects; G03 remains active.
