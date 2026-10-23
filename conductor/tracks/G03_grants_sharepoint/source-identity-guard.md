# G03 source-identity guard: native patch contract

Status: saved native Flow Service configuration verified on 5 October 2026.
The flow remains Off; direct native solution-export parity is proven.
Native replay remains open.

## Bounded executor continuation — 2026-09-28

Use `python3 scripts/agent_harness.py packet --item G03-H02`. The next slice is
deployment-route validation, followed by one stopped-flow update only when that
validation passes. Existing authorisation covers the isolated DEV repair; no
new approval is needed for its reversible definition update.

1. Load `private/ops/2026-09-28-grants-storage-guard-preparation-private.json`,
   its adjacent `grants-storage-guard-candidate-private.json` and
   `grants-storage-guard-rollback-private.json` files with the same date prefix,
   and `private/ops/2026-09-28-grants-live-flow-cli-prewrite-private.json`.
   Read target IDs only from these private files. The candidate is prepared,
   not deployed. Preserve native Invoker authentication, connection references,
   manual trigger, site/list and Stopped state.
2. Acquire a Flow Service token in process with
   `az account get-access-token --resource https://service.flow.microsoft.com/`;
   capture it without printing or storing it. GET the saved environment/flow
   using the existing `/providers/Microsoft.ProcessSimple/environments/…/flows/…`
   route with `api-version=2016-11-01`. Compare current definition, connection
   references, target and state with the saved baseline. Drift stops the write.
3. Inspect the current referenced connection's health and the exact supported
   update operation/schema. A successful GET is insufficient evidence for a
   guessed PATCH body. Use an exposed supported tool, documented API, or existing
   browser Update import route. Preserve the complete rollback before any write.
   The browser export/editor was stuck Loading; do not repeat that same read loop.
   One fresh check after a meaningful session/page change is sufficient.
4. Run the packet's focused tests, including blank-key, source-identity and
   activation-preflight cases. Verify nonzero test counts and zero failures.
   Fingerprint the exact candidate/rollback with harness `snapshot`; use `drift`
   immediately before writing. Keep snapshots under ignored `private/ops`.
5. Update only the existing stopped DEV flow. Reload via the proven GET route
   and compare the complete saved action graph, connector authentication,
   connections, source/list IDs and state. Use Flow Checker when operable;
   record an unavailable checker as an open gate rather than a pass.
6. Before controlled replay, obtain a fresh complete list snapshot and approved
   fixture inventory, then use the existing activation preflight. Exercise
   create/replay/update, blank identities, same-source/different-key conflict,
   failed lookup, reviewer-field preservation, concurrency and stale-source
   ordering. Bind each run/action result to exact rows and versions. The current
   unique OpportunityKey list cannot exercise multiple existing matches: keep
   that case open until an explicitly scoped duplicate-test route is accepted;
   do not remove uniqueness as implicit setup.
7. Restore the Off state, remove only identified test fixtures and prove the
   baseline key set is restored. A failing definition update uses the saved
   rollback through the same validated route, followed by exact readback.
   Keep failure evidence; do not retry an unchanged error.

Record each completed slice in the existing G03 review and private receipt.
G03-H02/H03 stay open until all applicable run/list/version/recovery evidence
exists. A saved guard alone does not prove stale-source ordering or full storage
acceptance. Then follow the completion-plan stage exits rather than selecting
an arbitrary unchecked track.

## Failure mode

The saved reviewed-import flow queries only OpportunityKey. Two input rows
may carry the same exact (Source, SourceID, EvidenceHash) and different
keys. Both key lookups can return zero, so both can be created. The local
operations preflight rejects this case, but the native flow does not yet.
Do not solve this with a hard-coded title, grant code or item ID.

## Preconditions

1. Re-read the exact DEV list field internal names and indexes before the
   patch. The 2026-09-28 native readback in
   `private/ops/2026-09-28-grants-registry-schema-readback-private.json`
   confirms that `SourceID` is already indexed in the existing isolated list;
   do not add a duplicate index. Keep `OpportunityKey` unique and verify
   that the current index state is unchanged at deployment time.
2. Export the current disabled flow definition and connection references.
   Verify its site/list IDs against the existing G03 private target receipt,
   and retain the export as rollback input. Do not rebuild a second flow.
3. Obtain a complete current-row snapshot with exact key/source/source ID/
   evidence fields and a list freshness marker. Preflight the proposed batch
   against both itself and that snapshot with evaluate_run in
   scripts/grants_operations.py. A partial snapshot is not proof of absence.

## Candidate native graph

The serial reviewed-row loop must reject missing or whitespace-only
OpportunityKey, Source, SourceID or EvidenceHash before any lookup.
For each valid row, look up the existing OpportunityKey as now. Add a
second, source-identity lookup using the indexed SourceID and exact
Source/EvidenceHash, with OData string escaping. Query for a different
OpportunityKey and request at most one match. If a match exists, emit a
CONFLICTING_OPPORTUNITY_KEY_FOR_SOURCE_EVIDENCE diagnostic and take a
no-write branch. Only the no-conflict branch may reach the existing
exact-zero Create or exact-one Update path. A connector failure, truncated
query or ambiguous result is a failed run, not permission to write.

The source lookup also closes the within-batch case because the loop is
serial: a row created earlier in the same run becomes visible to the next
row. Verify that read-after-write behavior in a controlled synthetic DEV
run; do not assume it from the WDL graph. An independent batch preflight is
still required to avoid a partial batch before a later collision is found.

## Acceptance

Import the guarded definition into the same disabled DEV flow, read back
its saved action graph and connection bindings, and run Flow Checker. Then
perform controlled create/replay/update and same-source/different-key cases
with exact run-action outputs, list rows and versions. Confirm zero writes in
the conflict case, preserve reviewer fields, clean up synthetic rows with
readback, and restore the original Off state. Record hashes of before/after
definitions and a rollback export under ignored private/ops/. This is
isolated DEV evidence; organisation-wide acceptance remains separate.

## Consolidated-solution candidate — 5 October 2026

`scripts/patch_grants_solution_identity.py` now prepares the generic guard from
the verified post-deadline-update native solution export. It requires an exact
baseline hash, explicit workflow entry and separate private output. The
candidate retains all eight workflows, changes one workflow and preserves
connection references, triggers, component metadata, flow states and the saved
create/update actions, including the twelve deadline mappings.

The new serial row graph rejects blank OpportunityKey/Source/SourceID/EvidenceHash
before lookup, escapes the exact source-evidence filter, and encloses writes
in the no-conflict branch. Invalid, conflicting and duplicate identities
increment a failure counter; the run terminates Failed after the serial loop
if any row was rejected. This exposes partial-batch failure without claiming
transactional rollback, stale-source protection or concurrency acceptance.

Seventeen focused patch/package/comparison tests pass. Existing flow guard
and contract tests were checked separately. Candidate, hashes and comparison
receipt are in `private/ops/2026-10-05-grants-solution-identity-private/`.
Before stopped-flow deployment, re-read exact list fields/indexes and compare
a fresh solution export against this preserved baseline. Native runtime
acceptance stays separate; the parallel agent retains data/retention ownership.

## Native configuration readback — 5 October 2026

Fresh list settings confirm OpportunityKey remains required/unique and both
OpportunityKey and SourceID remain indexed. A fresh prewrite solution export
matched the preserved candidate baseline. The authorised solution import used
existing references, zero connection updates and disabled automatic activation.

Authenticated Flow Service GETs prove all eight saved definitions exactly match
the intended candidate; normalised connector logical references, API identities
and Invoker/Embedded sources match. Grants remains Stopped, Calendar Started,
and the remaining six Stopped. Flow Checker reports zero errors and one warning:
“This flow is off.” No flow was manually activated or executed.

**Export parity is unresolved:** two subsequent native solution exports still
contain the earlier grants graph despite the exact Flow Service readback. Do not
use either as the guarded release baseline or claim package portability. No
repeat import was attempted. Retain the fresh prewrite export as rollback and
the guarded candidate plus full native GETs as saved-configuration evidence.
The next bounded action is to reconcile the solution workflow representation
and active/draft linkage through a supported native route, without changing
flow state or the parallel agent's model. Runtime replay/concurrency remains
separate and open.

Private evidence: `private/ops/2026-10-05-grants-solution-identity-private/`
contains `native-deployment-receipt.json`, `native-all-flow-comparison.json`,
raw native GETs, import log, both unmatched exports and field-level differences.

### Export parity resolved — 5 October 2026

A fresh authenticated Dataverse workflow GET confirms the intended full
definition and connection references, component state Published and statecode
0 (Off). Microsoft’s documented `ExportSolution` action then returned a fresh
unmanaged ZIP that exactly matches the candidate across all eight workflows
and component metadata. No workflow update, publication, activation or repeat
import was needed. The earlier browser-download mismatch is retained as dated
evidence; its cause is unverified and it no longer blocks package parity.

Accepted guarded export: `direct-native-solution-export.zip` under the private
identity-guard evidence folder, with its hash in `native-deployment-receipt.json`.
Use that verified export as the next package baseline; retain the prewrite
export for rollback. Next: scoped grants runtime acceptance after the parallel
data-layer gate, with fresh exact list-row inventory and fixture rollback.

Supported route reference: [Microsoft cloud-flow export API](https://learn.microsoft.com/en-us/power-automate/manage-flows-with-code#export-flows).

### Prepared runtime cases — 5 October 2026

Use `scripts/build_grants_runtime_cases.py --output private/ops/<private-path>.json`
to prepare the nine synthetic cases without invoking the flow. Output is
exclusive-create and restricted to ignored private storage. The prepared packet
is `runtime-cases.json` in the private identity directory; its separate receipt
records the SHA256 and six passing focused tests. Execute cases in packet order
only after its execution prerequisites are met; negative identity cases are
explicit acceptance fixtures, not normal batch admission. Confirm native field
types and permitted choices before execution. Capture complete before/after rows
and versions, correlated terminal run/action evidence and exact fixture cleanup.
A same-key replay may create a version; conflict/blank cases must write nothing.
This package is unexecuted and does not close runtime or data-layer acceptance.

Runtime evidence checker: `python3 scripts/validate_grants_runtime_evidence.py
--packet private/ops/<packet>.json --evidence private/ops/<evidence>.json`.
Evidence supplies the canonical JSON packet SHA256 (sorted keys, compact
separators), exact target, data-layer gate, authority/rollback references,
ordered case records, complete baseline and cleanup snapshots, and restored
Off state. Each record carries unique run ID, request/action references,
submitted rows, terminal status, write count, diagnostics, and full before/after
rows with ID and chronological `versions` arrays. Snapshots must form a
continuous chain; rejected cases preserve all rows/versions, successful cases
preserve unrelated rows, item identity, reviewer fields and prior history.
Nine focused tests pass. `PASS_RECORDED_EVIDENCE` checks supplied evidence only;
it always reports `native_acceptance=false`. Verify raw native provenance and
typed/deadline fields separately; duplicate, concurrency and restore gates stay
open. No native runs or tenant changes occurred while adding this checker.

The subsequent native list preflight supersedes `runtime-cases.json` with
`runtime-cases-v2.json` (same private directory). The original fixture used
invalid timestamp/deadline choices; do not execute it. Corrected payloads use
`valid`, lowercase `unknown`, explicit precision/status/relevance defaults and
expected native create review defaults. The checker enforces those defaults.
Readback receipt `runtime-native-list-preflight-private.json` records the
complete empty key set and observed field choices; 16 affected tests pass.
SharePoint versioning is capped at 50 and remains separate from full archive
retention acceptance. Readbacks are point-in-time; refresh the execution snapshot
when native runtime gates clear, without repeating fixture preparation.

Source-row provenance continuation (5 October): saved native create/update
actions omit `SourceRowURL` although the live list has that URL field.
`scripts/patch_grants_solution_provenance.py` prepares exactly two additive
mappings in the guarded grants workflow, preserving all other actions, guards,
references and metadata. Eleven focused patch/package comparison tests pass.
Private candidate and receipt: `private/ops/2026-10-05-grants-solution-provenance-private/`.
A fresh direct native solution export matches the accepted guarded baseline
with zero workflow drift and supplies current rollback. The browser file-chooser
route timed out; import panel still says No file chosen/Next disabled, and
Mac lock prevents native picker fallback. No import or state change occurred.
Next: recover supported upload access, select the existing candidate and import
with automatic activation unchecked/existing references; then compare all eight
saved definitions, bindings and states plus direct native export. Do not rebuild
the candidate or repeat unchanged upload attempts. Native runtime remains gated.

Provenance deployment closure (5 October): Microsoft's documented Dataverse
workflow PATCH route resolves the browser upload blocker for this scoped edit.
Native metadata confirms clientdata writable and workflow optimistic concurrency
enabled. Exact prewrite clientdata matches the accepted baseline; private full
clientdata rollback and fresh solution rollback are preserved. Conditional PATCH
with the exact ETag changes only clientdata and returns 204. Native readback
matches the intended definition/references; grants remains Off/Published.
Direct native export matches the candidate across all eight workflows and
component metadata; exact native state reads confirm Calendar On and seven Off.
Receipt: `private/ops/2026-10-05-grants-solution-provenance-private/native-provenance-deployment-receipt.json`.
Use that directory's `postwrite-native-solution.zip` as the next accepted package
baseline. No import, activation, run, publishing or connection change occurred.
Next: native runtime after the parallel data-layer gate, including separate
opportunity URL/source-row URL readback. Browser upload is no longer a blocker
for supported scoped definition edits. Runtime/concurrency/restore remain open.

Observation ordering (5 October): local flow contract and native stopped flow
now wrap the exact-one Update in known-UTC and not-older conditions. Incoming
status must be `valid`, both observation strings must explicitly denote UTC,
and incoming ticks must be >= persisted ticks. Equal-time replay remains
allowed. Older/uncertain observations take diagnostic/no-write branches and
increment RowFailureCount; malformed timestamps fail before Update. Create,
identity guards, connector mappings, review preservation and bindings remain
unchanged. Local contract/package compatibility: 27 tests + 16 subtests; key
guard/preflight: 12 + 18 subtests; runtime packet/checker: 18 tests.
Conditional native PATCH returned 204; exact saved clientdata matches candidate,
flow remains Off/Published, and direct native export matches all eight workflows
and metadata. Private evidence: `private/ops/2026-10-05-grants-solution-ordering-private/`.
Accepted package baseline: `postwrite-native-solution.zip`; full clientdata and
prior provenance export remain rollback inputs. Use `runtime-cases-v3.json`
(12 cases) instead of v1/v2: it adds older/missing-timezone/malformed cases and
distinct opportunity/source-row URLs; the checker also verifies URL provenance.
No activation, native run or model change occurred. Native ordering/runtime,
cross-run concurrency, archive retention and rollback rehearsal remain open.
Next: scoped runtime after the parallel data-layer gate; refresh the exact
list snapshot and correlate every no-write case to row/version readback.

Native definition recovery rehearsal (5 October): while grants stayed Off,
exact prewrite clientdata was verified against the current ordering candidate.
Two supported ETag-conditional clientdata-only PATCHes restored the verified
pre-ordering provenance definition, then reapplied the accepted guarded
definition. Both returned 204; separate native GETs matched each intended
definition/references and Off/Published state. Final clientdata equals the
original guarded candidate; elapsed 5.625 seconds. Receipt and exact native
stages: `private/ops/2026-10-05-grants-solution-ordering-private/definition-rollback-rehearsal-receipt.json`.
No run, activation, list/model change or schedule change occurred. This closes
only stopped-flow definition restore/reapply capability; G03-H01/H03 stay open
for list/archive recovery and their other required acceptance evidence. Native
runtime, concurrent requests and data-layer retention remain separate gates.
Next remains the scoped runtime cycle after the parallel data-layer gate.
