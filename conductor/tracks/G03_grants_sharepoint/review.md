# G03 review

## Source row URL contract reconciliation — 2026-09-28

The read-only DEV list-field receipt and historical create-flow evidence
confirmed `SourceRowURL` is a custom optional URL field distinct from the
canonical opportunity `URL`. The local schema, reviewed importer, SharePoint
projection, flow create/update mappings, runtime reconciler, and isolated
GrantsRegistry model projection now preserve it as optional provenance,
including row fragments; it does not participate in `OpportunityKey`.
Focused grants tests and runtime parity tests pass. The frozen local drift
manifest now records only the two changed semantic-model files under this
outcome-linked review. These edits are local: no native field, flow, or model
write was performed, and the list's current empty view prevents nonvacuous
row acceptance. G03-H02/H03 remain open.


## Reviewed-batch replay preflight hardening — 2026-09-26

The local `preflight_grants_flow_activation.py` now requires a current (within
24 hours, not future-dated) flow/target/snapshot/batch readback, a reviewed
incoming decision with nonblank notes, and an OpportunityKey derived from the
text source/round identity. It treats source identity independently of
`EvidenceHash`, so a changed payload cannot hide a same-identity key collision;
round-only identities remain valid. Focused synthetic tests pass (9). The
current DEV list is empty and saved flow state is Off, but dated receipts are
not a fresh binding/snapshot for replay. This local gate does not approve a
reviewer, import a row, enable a flow, or prove native acceptance.

## GO8568 DEV replay boundary — 2026-09-26

A candidate-only private GO8568 review packet now specifies the exact
isolated-DEV replay and rollback order. The 2026-09-26 BrowserOS list receipt
observed zero rows, but a controlled write still requires a fresh complete
same-target row/version snapshot, saved Off flow export and all three
Get/Create/Update action bindings. The reviewed batch must pass
`scripts/preflight_grants_flow_activation.py` against those current inputs.
After a controlled run, compare the exact OpportunityKey, SourceID, all 22
projected fields, evidence hash and preserved review fields; then restore a
captured prior version or remove only the verified newly created test item.
Read back the flow Off and target state afterward. No flow or list mutation was
made in preparing this packet; G03-H02 remains open.

## Local activation preflight — 2026-09-26

`scripts/preflight_grants_flow_activation.py` now rejects a controlled grants
flow replay unless private readbacks prove the exact Off flow identity, all
three Get/Create/Update SharePoint site/list bindings, the serial exact-match
graph, a required/indexed/unique OpportunityKey, and a complete current-row
snapshot from that same list. It compares a complete proposed batch with the
snapshot for duplicate keys, changed key-to-source mappings, identical source
evidence under different keys, and older retrieval timestamps. Each input must
carry a timezone-aware `observed_at_utc`; the saved flow and target must be
observed no later than the snapshot, which must precede the batch. The CLI
accepts only ignored `private/ops/` inputs and outputs. Five focused preflight
tests and twelve existing flow contract/package tests pass.

The current native receipts are not a complete row-level snapshot plus saved
flow export in this input shape, so the preflight has **not** passed against
the tenant. The saved flow also lacks the proposed native source-identity
lookup. This local gate does not authorize activation or prove native replay;
G03-H02 and G04-H02 remain open.

## Funding runtime source-binding guard — 2026-09-25

The runtime reconciler now requires all 22 canonical projected fields in both
complete readbacks and compares every value for each shared OpportunityKey.
SharePoint's URL `{Url, Description}` shape is compared using its `Url` value
against the model text URL; null and empty text remain distinct. Its aggregate
receipt identifies mismatched field names/counts without exposing opportunity
rows. A matching key and `Reviewed` status can no longer mask stale title,
deadline, source identity or evidence hash in the imported model. This is a
local acceptance gate only; the DEV list is currently empty and no terminal
refresh plus nonempty DAX/list comparison has been captured.

The local `reconcile_funding_runtime.py` previously checked only that the list
and dataset IDs were nonblank. Identical reviewed keys from an unrelated list
could therefore return `PASS`. The runtime gate now requires a complete native
source-binding receipt with the exact dataset ID, canonical SharePoint list
GUID, site URL, `Grants Registry` table and `SharePoint.Tables` source kind.
Its binding observation must follow the completed refresh and precede the
complete list/model row observations. The fourth `--binding` input is required;
the earlier sanitized source-identity receipt alone lacks the private IDs and
cannot be passed off as a complete runtime binding. Six focused tests pass,
including unrelated-list/site and stale-binding rejection. This is local
verification tooling; the current empty DEV list still prevents nonvacuous
row admission and runtime parity acceptance.

Review status: in progress; isolated DEV list/schema, flow import, controlled
create/update replay and row-level readback are now evidenced. Organisation-wide
target acceptance, cleanup, unattended execution and production acceptance remain
open.

## Controlled native replay — 2026-09-21

Using the authenticated Power Automate web UI, the imported instant flow was
temporarily enabled, run with one synthetic `OpportunityKey`, and restored to
`Off`. Flow Checker reported zero editor errors. Run
`08584116923018304855211342755CU17` succeeded for the create path. The SharePoint
`Grants Registry` readback showed the expected synthetic row and all key fields.

Run `08584116920125684835586408484CU25` succeeded for a same-key replay. The
SharePoint readback showed the same unique key with updated title, funder, amount,
retrieval timestamp and evidence hash, proving the update path. The synthetic row
remains in the private DEV list pending explicit confirmation immediately before
cloud deletion. No production or organisation-wide target was touched.

Review status: in progress; the isolated DEV list/schema/create-update-duplicate-readback and reviewed-import flow import/readback gates are evidenced, while organisation-wide target acceptance, execution and unattended acceptance remain open.

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

## Remaining acceptance

The isolated DEV route is now implemented and read back. The remaining gates
are to decide and approve the organisation-wide target, bind the grants flow
to this canonical list or its approved successor, and obtain native execution
evidence. The imported flow has not been enabled or run, so native row-level
create/update execution, unattended operation and production acceptance remain
unproved. Do not use OneDrive actions for registry writes.

## Replay attempt — 2026-09-20

The requested controlled synthetic replay could not be started in this
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

The reviewed-import package was accepted by the Power Automate import wizard
after correcting the SharePoint URL, choice-object and required-key payload
contracts. The created flow is an Instant/manual flow, is Off, has no run
history, uses the selected SharePoint Online connection, and exposes the
expected trigger, JSON parse, serial Apply to each, SharePoint Get items,
duplicate guard and create/update branches. The native editor Flow Checker
reported no errors or warnings; the details-page warning is the expected
inactive-flow warning. Full private receipt:
`private/ops/2026-09-20-grants-flow-import-readback.json`.

The duplicate branch is intentionally diagnostic rather than a nested
`Terminate` action: Power Automate rejects `Terminate` inside this
`Apply to each` scope. The following create/update condition is independently
guarded by `length(Get items.value) == 0`, so duplicate matches cannot write.
The local definition uses a non-throwing diagnostic string; the current native
readback still shows the earlier integer diagnostic expression and therefore
requires a later controlled native edit before this track can close.

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
- [x] Test Results: Passed — 318 tests and Conductor validation passed; Flow Checker read back 0 errors and 0 warnings after saving the correction.

### Findings

No new implementation findings. The open target/operational gates are acceptance boundaries, not defects; G03 remains active.

## BrowserOS reviewed-import readback — 2026-09-22

BrowserOS readback confirms the isolated DEV reviewed-import flow remains an
Off Instant flow. Flow Checker has zero errors; its sole warning is the
inactive state. The latest successful controlled run parsed one input row,
completed the SharePoint lookup, skipped the duplicate diagnostic, and took
the Create branch while skipping Update. The created record is retained as a
`Needs Review` candidate with official-source evidence, rather than treated as
a disposable fixture. This confirms the native create path only; it does not
prove an unattended source feed, organisation-wide target, delivery, or report
binding. Private receipt:
`private/ops/2026-09-22-browseros-grants-reviewed-import-readback.json`.

## Native field-name reconciliation — 2026-09-24

A fresh, complete readback of the existing isolated DEV `Grants Registry` fields
found exactly one writable native field for each of the 22 schema fields, with
each `InternalName` matching the local flow and schema reference. SharePoint
also exposes computed `Title` variants; those are excluded from the writable
mapping. The only observed schema-property drift is that native `Title` has
`Required=false`, while `config/grants-registry.schema.json` declares it
required. The ignored evidence is
`private/ops/2026-09-24-grants-registry-native-internal-fields.json`.

The required-setting change therefore needed an item-count and blank-`Title`
preflight before any write. This field-name readback alone did not close
G03-H01 or prove flow acceptance.

## Native Title requirement correction — 2026-09-24

The isolated DEV list preflight found zero items and zero blank `Title` rows.
The writable `Title` field was changed from `Required=false` to `true` through
a scoped SharePoint REST update. The update returned 204; a fresh field and
list readback confirmed `Required=true` persisted and the list still had zero
items. The private receipt is
`private/ops/2026-09-24-grants-title-required-native-acceptance.json`.

The 22 writable field names and the `Title` requirement now match the local
schema for this isolated list. This field correction does not prove the
reviewed-import flow's remaining native execution cases, approve an
organisation-wide target, or close G03-H01–H03.

## Duplicate-match flow finding — 2026-09-24

Read-only reconciliation of `config/flows/grants-registry-reviewed-import.definition.json`
found that the duplicate diagnostic runs when `Get items` returns more than one
row, but its `Compose` action succeeds. The later create/update condition tests
only whether the count is zero; its else branch updates the first returned row
for both one and multiple matches. The earlier review statement that the
duplicate branch cannot write is therefore incorrect. Native `OpportunityKey`
uniqueness in the isolated list limits exposure there, but does not establish
safe flow behavior for a migrated or drifted destination list.

G03-H02 now requires an exact-one update guard in the local definition and
saved native flow, followed by a controlled duplicate-match readback that
proves neither row changed. This is an open acceptance defect; no browser or
source edit was made during this reconciliation.

The local definition now nests `SharePoint_Update_item` under
`Condition_Exactly_One_Opportunity`, which checks lookup count `== 1`; the
zero branch alone creates, and counts above one reach an empty no-write branch.
The grants flow contract and package tests pass with the new action path.
This is local preparation only: the saved native flow may still have the
earlier unsafe branch until an isolated, controlled update and reload readback.
The next native gate is to compare the saved flow's zero/one/multiple-match
branches to this definition, then demonstrate that a duplicate-match replay
leaves both row values and versions unchanged. Restore the flow's prior state
and reconcile any fixture rows after the test.

## Exact-one native import — 2026-09-24

The scoped Update package was imported into the existing isolated DEV flow.
The native designer displayed the duplicate diagnostic and downstream
create/update condition, Flow checker reported zero errors and warnings, and
the details page showed the flow still Off. The ignored import/readback receipt
is `private/ops/2026-09-24-grants-exact-one-native-import.json`; the unchanged
rollback ZIP remains under `private/ops/flow-packages/`. This establishes saved
flow presence and structural validity, not duplicate-match runtime behavior.
The list's indexed unique `OpportunityKey` currently prevents two matching
rows, so the >1 no-write runtime gate remains open. No uniqueness setting was
changed for this import.

## Runtime-test preflight readback — 2026-09-24

Read-only SharePoint REST readback of the exact list targeted by the imported
flow reports `ItemCount=0` and returns no list items. `OpportunityKey` remains
required, indexed and unique; versioning is enabled with a 50-version limit.
The flow is still Off and its editor checker reports 0 errors/0 warnings.
Receipt: `private/ops/2026-09-24-grants-exact-one-runtime-preflight.json`.

This conflicts with the 2026-09-22 receipt describing a retained reviewed
candidate. The current full item enumeration is authoritative for present
list contents; historical creation/run provenance still needs reconciliation.
The zero-row and unique-key state do not permit a native >1-match test without
temporarily removing the list uniqueness guard. No list or flow write was made.

## H01 storage/readback reconciliation — 2026-09-25

A fresh authenticated SharePoint REST readback confirmed the existing Grants
Registry list has zero current rows, versioning enabled (50 major versions),
and a required, indexed, unique OpportunityKey. Its unique role assignment is
Full Control for the current owner. A directory-filtered recycle-bin query
found one deleted entry titled `Synthetic G03 replay 20260920 UPDATED`. The
22 September Needs Review create receipt contains no item ID/key, so the
recycle-bin entry cannot be linked to that candidate; H01 provenance remains
unresolved. No restoration/deletion or other tenant mutation was performed.
The fresh readback is `private/ops/2026-09-25-grants-storage-reconciliation-readback.json`;
flow-to-list binding was not recaptured and the prior flow-state receipt remains
the latest saved evidence.

A follow-up read of the existing Power Automate editor confirmed the SharePoint
Get items action targets the existing DEV site and Grants Registry list, with
Top Count 2 and the current owner's connection. The action-details pane was
closed without saving or testing. Create and Update targets, and current flow
state, were not independently read in that editor capture. Receipt:
`private/ops/2026-09-25-grants-storage-flow-readback.json`.

## Reviewed-import blank-key guard — 2026-09-25

The local reviewed-import definition now gates every registry lookup and write
behind `Condition_OpportunityKey_Present`. Missing, null, empty and
whitespace-only keys take an `INVALID_OPPORTUNITY_KEY` diagnostic branch;
valid keys enter the existing duplicate/create/exactly-one update flow. Focused
flow contract, package and key-guard tests pass (11 tests). This is local
definition evidence; the imported native flow has not been updated or tested,
so runtime blank-key rejection and target parity remain open.

## Local private-package URL validation — 2026-09-25

Focused review of `scripts/build_grants_flow_package.py` found that a string
such as `https://` passed the former prefix check and could be embedded as the
SharePoint dataset target. The builder now requires a parsed HTTPS URL with a
host and rejects user-info, query/fragment components, unresolved template
markers and surrounding whitespace before writing the private package. The
focused package tests cover malformed and credential-bearing URLs and pass
(3 tests). This is local input validation only: it does not qualify the target,
prove the package's native import format, or change G03.X1–X6/H01–H03 status.

## Identity uniqueness contract — 2026-09-25

The local list schema declared `OpportunityKey` required and indexed but did
not state the unique constraint observed in the isolated DEV list. The schema
now explicitly declares `unique: true`, and `tests/test_grants_schema.py`
requires the sole identity field to be text, required, indexed and unique.
The focused schema suite passed 3 tests and `validate_project.py` passed 450
local checks. This is a contract correction, not a tenant schema write. The
existing DEV field readback and Title correction remain the native evidence;
G03-H01 still needs Create/Update action-target identity and historical
candidate provenance before its storage baseline can close.

## Historical candidate provenance audit — 2026-09-25

The saved 22 September reviewed-import receipt records one input, a successful
Create branch and `Needs Review`, but no flow run ID/time, SharePoint item ID,
`OpportunityKey`, title or version. The later storage receipt confirms zero
current rows and one list-directory recycle-bin entry titled `Synthetic G03
replay 20260920 UPDATED`, deleted on 21 September. That entry has a recycle ID
and leaf name, but the saved Create receipt has no common identifier. The
receipt's 22 September observation date is not the Create run time, so the
date order also cannot establish or exclude a match. No local reconciliation
can determine whether the reviewed candidate was deleted, moved, or created
against a different target.

The next native provenance read should capture the exact reviewed-import run's
trigger input, Create action output (`ID`, `OpportunityKey`, title and list
target), and run time, then compare those values with the list's item/version
history and recycle-bin item identity. If that run detail is no longer
available, record the history as irreconcilable and retain the current
zero-row readback as a separate present-state fact. Do not infer an item
identity from the synthetic-looking recycle-bin title or delete/restore any
row on that basis. Sources: ignored
`private/ops/2026-09-22-browseros-grants-reviewed-import-readback.json` and
`private/ops/2026-09-25-grants-storage-reconciliation-readback.json`.
## Historical Create run identity readback — 2026-09-25

An authenticated Power Automate run from 22 September was read through the
existing DEV reviewed-import flow. Its one iteration shows a successful
SharePoint Create (HTTP 201) with a concrete item ID, `OpportunityKey`, title
and `Needs Review` value. The action's list identity matches the established
G03 DEV list. Exact run/item identities are in ignored
`private/ops/2026-09-25-grants-0541-create-run-readback.json`. The current list
has zero rows, and the one visible recycle entry has a different title. The
earlier candidate receipt did not record a run ID, time, item ID or key, so it
cannot yet be identified as this run. Its disposition and all other historical
runs remain open; a successful Create is not proof of current presence or an
accepted opportunity.
## Current DEV flow target parity — 2026-09-25

Authenticated BrowserOS readback of the existing disabled reviewed-import flow inspected the saved `SharePoint Get items`, `SharePoint Create item` and `SharePoint Update item` parameter panels separately. All three point to the same isolated personal DEV site and existing `Grants Registry` list; Create maps required Title/OpportunityKey and Update maps required ID/Title/OpportunityKey. Create/Update Code view contains the exact current DEV list ID, and Update selects the first ID returned by `SharePoint Get items`. The current flow list shows Disabled. The updated private receipt is `private/ops/2026-09-25-grants-storage-flow-readback.json`. No save, test, import, enablement or list write occurred. This closes saved-definition target/ID inventory only; controlled replay, historic candidate disposition, rollback and organisation-wide storage acceptance remain open.

A separate local identity audit found two historical official-source Create
outputs with identical source, source ID, title and evidence hash but distinct
supplied OpportunityKeys. The saved readback does not prove why those keys
diverged; the third historical Create was synthetic. The generic local
operations preflight now fails closed when candidate/prior snapshots reuse
the same (Source, SourceID, EvidenceHash) under different keys. Focused tests
pass. The currently saved key-only flow still cannot detect that cross-run
collision, and no tenant key migration or row change was made. Native replay
and rollback remain open.

The local funding runtime reconciler now requires a terminal Completed bound
model refresh plus complete, nonempty list and DAX key/status readbacks from
that refresh. It checks exact OpportunityKeys, uniqueness and Reviewed status
without writing keys into its aggregate output. Focused tests pass. The
complete list receipt must now carry the native `item_count` and the model
receipt the query `row_count`; each must equal the exported rows. This closes
a silent partial-export acceptance path where `complete: true` alone could
mask a short key inventory. These totals must be captured with the same
readback and are not a substitute for the separate 22-field schema check. The
existing 22/22 native field/type parity is a schema result only: the current
empty DEV list and missing terminal refresh cannot pass runtime parity. The
6-page/66-visual native versus 7-page/85-visual local scope gap is separate.

A fresh authenticated same-origin SharePoint REST read confirmed the exact DEV
list remains empty and returned all 107 field definitions without continuation.
The writable `Title` field is already Required=true; an older saved inventory
that showed false was stale, so no schema mutation was needed. The current
report-bound Fabric TMDL partition selects this exact site/list GUID. The
read-only `scripts/check_grants_field_parity.py` passed all 22 configured
fields against current model string types and native field type, required,
indexed and unique settings. Private receipts:
`private/ops/2026-09-25-funding-bound-partition-source-reconciliation.json`,
`private/ops/2026-09-25-grants-native-fields-current.json`, and
`private/ops/2026-09-25-grants-field-type-parity-current.json`. This closes
current source/schema identity, not refresh, admission, replay or report parity.

## Historic candidate correlation limit — 2026-09-25

Read-only run inventory for the existing DEV reviewed-import flow found seven retained runs, including three successful Create actions on 22 September Brisbane time (21 September 19:23, 19:36 and 19:41 UTC). The saved candidate receipt lacks run ID, time, item ID and key; it cannot be uniquely mapped to the 05:41 Create or either earlier Create. The ignored `private/ops/2026-09-25-grants-historic-run-inventory-readonly.json` records run/action identities. Next, inspect the three trigger inputs and Create outputs in authenticated Power Automate and compare exact IDs with item version/recycle evidence. If no contemporaneous receipt distinguishes one, record the historic candidate as irreconcilable; retain the current empty-list readback as a separate present-state fact. No tenant mutation was made.

Historical note (superseded by the 2026-10-03 action-level readback below): the then-available candidate receipt had no run/key/ID fields, so matching among same-title creates was unresolved. The private payload evidence remains at `private/ops/2026-09-25-grants-three-create-correlation-readonly-private.json` and its payload siblings. Current list emptiness and item disposition are separate questions; no tenant write occurred during that readback.

## 2026-10-03 exact historical candidate correlation

Authenticated BrowserOS readback of run `08584115872127113780695944024CU04` proves that the 2026-09-22 reviewed-import run created item 8 with key `metro-south-innovate-grants-2027`, source `Metro South Health`, and `ReviewStatus=Needs Review`. The exact `Get items` filter used that key, the duplicate condition was false, and the create output returned ID 8. Synthetic item 7 had a different OpportunityKey, so the candidate identity is now uniquely established. The Sep 25 item read returned 404; the scoped recycle-bin read returned only unrelated item 5; the Oct 2 list count was 0. These establish current absence, not who/when/how removed the candidate or whether the deletion is recoverable. Purview audit search loaded on Oct 3, but all search controls were disabled and no query was submitted. Do not restore, delete, or recreate from inference. Keep the flow Off pending authorized audit evidence or explicit disposition, plus rollback rehearsal. Sanitized receipts: `private/ops/2026-10-03-g03-historical-candidate-run-action-readback-private.json`, `private/ops/2026-10-03-g03-purview-audit-search-access-private.json`, and `private/ops/2026-10-03-g03-candidate-correlation-reconciliation-private.json`.

A further authenticated BrowserOS neo SharePoint REST trace read the exact DEV list and three historical item IDs. The current item feed is empty; each exact item route returns 404 and its versions route cannot resolve the item. The site recycle bin has no matching entry for these three identities (its sole Grants Registry entry is an unrelated synthetic item), and the `ItemState=2` filter returns no entries. This proves the three are absent from the currently observable list/recycle surfaces, but not how or when they disappeared, nor which one the earlier candidate receipt described. Private receipt: `private/ops/2026-09-25-grants-three-create-disposition-browseros-private.json`. No tenant mutation occurred.

A 2026-09-26 Brisbane authenticated metadata reread still reports zero current
Grants Registry items, versioning enabled and a 50-major-version limit. The
ignored `private/ops/2026-09-26-grants-registry-empty-browseros-private.json`
records the read-only result. It does not resolve the historical Create-item
disposition or prove the bound model is refreshed.

The runtime reconciler now compares all 22 canonical values for each exact
list/model opportunity key, preserving null versus empty text; ten focused
tests pass. This strengthens the future row acceptance gate but cannot pass
against the empty DEV list. A bounded live read of the official Queensland
CKAN API produced six review-only rows marked Open, including one with a
2025 closing date; none has proven stable round identity and current lifecycle
evidence. No row was admitted. Private qualification:
`private/ops/2026-09-26-g03-official-candidate-qualification-private.json`.

A separate single-row discovery found official GrantConnect opportunity
GO8568 through NHMRC. BrowserOS neo read back its public `Current Grant
Opportunity View`, GO ID, agency and 11 November 2026 close time directly;
the linked Guidelines/Addenda document route redirected to a GrantConnect
login. This is a concrete reviewed-import candidate, not a machine feed or
accepted DEV row. The current Guidelines and addendum, authenticated human
review, and any required access/retention decision remain open. Private
receipts: `private/ops/2026-09-26-nhmrc-go8568-reviewed-import-discovery-private.json`
and `private/ops/2026-09-26-go8568-browseros-official-row-private.json`.

On 2026-09-27, after QH sign-in through VS Code, PAC identified the intended
environment but SharePoint REST via Azure CLI still returned HTTP 401 for the
existing DEV list. The single BrowserOS writer used the authenticated
SharePoint REST endpoint instead: the exact existing `Grants Registry` returned
HTTP 200, `ItemCount=0`, versioning enabled, 107 native fields (including the
required unique `OpportunityKey`), and an empty first items page. No list,
flow, or row was created or changed. Private readbacks:
`private/ops/2026-09-27-grants-cli-readonly-recheck-private.json` and
`private/ops/2026-09-27-grants-browseros-live-baseline-verified-private.json`.
The official QGIP API refresh remains byte/identity unchanged from 2026-09-25
with six review-only candidates, so no source-qualified row is ready for
admission into this list.

## 2026-09-28 current schema contract readback

The existing Grants Registry was re-read from its already-open authenticated
SharePoint page using GET-only list and field metadata requests. Its exact list
identity matches the saved G03 baseline; the list remains empty, versioning is
enabled, and its 23 configured contract fields are present. The live physical
types, required flags, indexes and uniqueness now pass the current local schema
and GrantsRegistry model comparison (23/23). In particular, the current
readback shows `SourceID` indexed; the 2026-09-25 native snapshot used by the
older parity result showed it unindexed and is now stale for that property.
Private evidence:
`private/ops/2026-09-28-grants-registry-schema-readback-private.json` and
`private/ops/2026-09-28-grants-field-type-parity-current-private.json`.
No tenant state was changed. G03-H01 remains open for historic-candidate
correlation and a verified controlled replay/rollback; schema parity alone
does not close storage acceptance.

## G03 alternate CLI route decision — 2026-09-28

Completed the bounded read-only G03.X1 inventory. The PAC profile list contains
saved NSW, VUW and Queensland Health entries, with VUW active; it shows no
personal profile. The one `pac org who` request for VUW timed out at 30 seconds.
M365 CLI reported expired conditional-access authentication and the Fabric CLI
reported signed out. No login, token acquisition, source/target write, package
export/import, fixture or cleanup was attempted. Sanitised capability matrix
and evidence hashes: `private/ops/grants-dev-route-20260928T0415Z-private.json`.

G03.X1 is closed with `needs_identity_or_permission`; G03.X6 retains the
existing Queensland Health web route for current delivery. No cross-route
cycle time or efficiency is claimed because an alternate route was not
eligible to run. The web route has current storage baseline evidence and prior
isolated synthetic upsert/restore evidence; G03-H01/H02/H03 remain open for
their own historic-candidate, native source-identity/duplicate, replay and
rollback gates. G03.X2-X5 are unexecuted and unaccepted. Reconsider only after
supported service-specific sign-in and metadata prove alternate capability.


## Rebased guard package preparation — 2026-09-28

PAC 2.12.2 was interactively reauthenticated. Its connection inventory reports the SharePoint connector Connected; PAC's preview flow inspection returns null for this flow and offers no definition update. Azure CLI can read it using Flow Service, but Microsoft identifies that API as unsupported for writes. A documented Dataverse read using the Azure CLI token returned 401.

The guarded candidate was rebased on the latest private Flow Service snapshot. It preserves the native trigger, parameters, connector references, SharePoint binding and nine existing action metadata IDs. The guarded Update and rollback ZIPs pass local structure checks, both remain Off, and the candidate retains the source-identity filter and two optional `SourceRowURL` mappings. Private validation receipt: `private/ops/2026-09-28-grants-storage-guard-package-validation-private.json`. Six focused suites pass (26 tests).

No import or native change has occurred. The existing BrowserOS import page currently shows Sign in required; one automated sign-in click did not clear it. The Flow Service snapshot is useful for preparation but is not supported-portal rollback/readback evidence. Resume by signing in on the existing tab, exporting and comparing the current flow, then importing the candidate as an Update and reading back definition/Flow Checker while keeping the flow Off.

## Grants Registry current list properties — 2026-10-05

A fresh BrowserOS neo read of the exact existing isolated DEV `Grants Registry`
returned list ID `371e0410-ee4e-48db-8136-c63255745712`, zero current items,
versioning enabled with a 50-major-version cap, and unique list-level role
assignments. The REST representation reports ETag 78 and resource update time
2026-10-05 07:56:45 UTC. No rows, fields, permission principals, or flow state
were read or changed. This reconfirms the bounded storage baseline only; it
does not resolve historic-candidate disposition, permission membership,
rollback rehearsal, duplicate-runtime proof, or organisation-wide approval.
Receipt: `private/ops/2026-10-05-g03-registry-current-readback-private.json`.
