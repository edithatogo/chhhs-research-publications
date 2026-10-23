# Track Review: E01 Power Automate Ingestion Canonicalization and Recurrence Scheduling

## Current review summary — 23 October 2026

Plan compliance remains Partial; accepted work is reconciled and no failed guard is
waived. The selected writer/concurrency evidence, R45 reader dependency and digest
documentation handoff are accepted. PubMed's full restart after the recorded failed
generation is native-qualified (1,277 identical before/after IDs, 13 verified XML
batches, manifest/checkpoint guards true). Crossref's latest source-total drift was
rejected before commit; its pre-run checkpoint was read and guarded true. DoRA and
ARDC safe full-restart paths remain accepted. DataCite's empty-prefix receipt path
and archived-page ETag equality are qualified. A subsequent bounded readback of the
interrupted run exposed that completed query summaries omitted the scope hash required
by the recovery reader; this writer/reader mismatch is fixed in the local builder and
saved native action, and the original 63-action weekly graph is restored. The old
summaries remain ineligible, so nonempty-prefix iteration/count is still open.
Read-only action-level inspection of CU04 confirms the selected receipt had an empty
`complete_query_prefix`; the recovery loop correctly ran zero iterations. Its nonempty
page metadata, row reconciliation, completed-key seeding and remaining-query continuation
therefore remain unqualified. No eligible prefix currently exists; use a real naturally
failed run when one occurs rather than fabricating lineage or forcing partial acquisition.
ClinicalTrials continuation remains unqualified because its archived failed page
lacks same-run source-version lineage. Shared freshness/coverage and the digest's
actual Outlook action/binding remain open.

The historical 22 October findings below are superseded where these later receipts
provide updated evidence; they remain useful as dated review history. The bounded
DataCite attempt accidentally entered normal acquisition and was cancelled after two
page requests; no completion marker/checkpoint was written. Structural validation is
separate from live acceptance, and no mail send was performed.

### Current verification

- Plan compliance: Partial; accepted writer, reader and digest-documentation work is closed. Provider recovery/coverage and digest email wiring remain open.
- Style compliance: Pass against `conductor/code_styleguides/general.md`.
- New tests: No. Existing focused DataCite builder suite passed 9/9.
- Test coverage: Partial; no eligible nonempty DataCite prefix was available for native iteration/count proof.
- Test results: Publications-scoped harness passed `PASS_LOCAL_ONLY` in the pinned `uv` environment: 157 publication, 9 identity, 13 PubMed-decision and 11 monthly DOCX tests. Conductor validation reports 0 structural errors; scoped diff check passes. The active system Python run initially failed only because `python-docx` was absent; no dependency was installed into that interpreter.

- Current increment: focused DataCite preparation suite passes 9/9; Conductor
  validation reports 0 structural errors. Native diagnostic run
  `08584089122505886767065755263CU25` read the two interrupted query summaries and
  pages, then stopped before folder creation, DataCite paging or completion writes;
  its failure receipt was saved/read/verified. Final native readback confirms the
  original Started weekly trigger and SharePoint binding with the new query scope
  hash. This does not qualify nonempty-prefix runtime.

### Read-only DataCite recovery-loop reconciliation — 23 October 2026

The retained CU04 action details are now available through bounded action readback.
`Set_current_recovery_query` has zero repetitions and `For_each_recovery_query`
completed without iterations; the receipt selection and completed-key default actions
succeeded. This agrees with the selected receipt having an empty prefix. The page loop,
ETag guard, row-count reconciliation and query-summary continuation were not exercised.
The two earlier eligible v2 receipts also have empty prefixes, and the interrupted
CU04 summaries remain ineligible because their scope hash was absent. No eligible
nonempty prefix exists in current accepted evidence. Do not synthesize a receipt or
run a partial/full acquisition solely to manufacture this case. Evidence remains
under `private/ops/2026-10-23-e01-current-state/`; no native write or provider request
was made during this readback.

## Full-scope review follow-up — 22 October 2026

### Summary

The accepted writer qualification, raw-aware reader reconciliation and digest documentation handoff are correctly closed against their receipts and need no repeat. PubMed's new failed-generation receipt is now natively qualified on the same flow and its normal daily graph is restored. E01 remains in progress: source-specific recovery/freshness and coverage outcomes remain incomplete, and the digest's actual mail action/binding is still unimplemented.

### Verification checks

- [x] Plan compliance: Partial — the writer/read-reader evidence and versioned digest handoff are reconciled; the PubMed failure observer was saved, exercised before provider requests and restored with its normal trigger/binding.
- [x] Style compliance: Pass — the PubMed observer reuses existing SharePoint actions and archive location, preserves the completion path, and records uncertain completion-write state without advancing last-good.
- [x] New tests: Yes — PubMed receipt placement, byte verification, failure disposition and duplicate-install refusal have focused coverage.
- [x] Test coverage: Partial — 28 focused preparation tests across ARDC, ClinicalTrials.gov, DataCite, DoRA and PubMed pass; these do not prove all native continuation or source-health requirements.
- [x] Test results: Passed — 28 focused unit tests; `python3 scripts/validate_conductor.py` reports 0 structural errors; scoped `git diff --check` passes. The PubMed run `08584089286902726122143679218CU21` saved/read the failure receipt with verification true, skipped searches/fetches and completion writes, and preserved the prior 1,277-ID marker identity. The exact Started daily 01:30 Brisbane graph and SharePoint binding were restored.

### Findings

#### High — cross-source recovery and source-health projection remain incomplete

- **File**: `conductor/tracks/E01_flow_automation/plan.md`
- **Context**: DataCite has a qualified operator-run query-prefix recovery packet, but the normal weekly graph does not load it automatically. ClinicalTrials' retained failed page predates its source `dataTimestamp` guard and its token is stale; the configured full scope would require a 12,677-study acquisition, which should not be run only to create a recovery fixture. DoRA safely restarts at offset zero because no provider version token accompanies its failed page. ARDC's safe restart from a fresh `rif` initial URI after an injected failure is now natively qualified; cross-run OAI token/page reuse remains unsupported. PubMed has a verified failure receipt but deliberately restarts from a fresh ESearch. ROR release identity/hash proves raw release freshness, while its manifest still marks the Australian projection incomplete. QGIP is grants-owned and must not be changed by E01. The shared freshness/coverage view is not yet demonstrated from current accepted run outcomes.
- **Suggestion**: Keep cursors/pages non-reusable unless their provider version, exact query/cutoff and archived bytes are verified. Implement and qualify one source-specific continuation/restart path at a time; keep held sources fail-closed and proceed to the next independently implementable source. Build the shared freshness/coverage projection only from existing accepted run/source records and retain explicit incomplete/raw-only states.

#### High — digest mail action and binding remain absent

- **File**: `conductor/tracks/E01_flow_automation/plan.md`
- **Context**: The accepted documentation transaction represents the actual saved no-send graph. `Send_verified_digest_email` is still a Compose action and the fresh service readback has no used Outlook binding. The previous reference is disconnected, while the available same-owner connection has not been reconciled to the exact solution reference. The send-authority guard correctly remains false.
- **Suggestion**: Use the existing qualified VS Code PAC route after the shared-auth owner handoff, inspect the exact solution connection-reference component, and prepare the same-owner binding/action through the supported route. Keep the digest Stopped and the send gate closed; do not treat native wiring as delivery authority.

### Recommendation

Keep E01 in progress. The accepted work should remain closed; continue with one exact source gap and the digest technical binding when its qualified route is available. No schedule activation, report/model refresh, email send or publication is supported by this review.

### Code review follow-up — 23 October 2026

Two local defects were found and corrected during the E01 review. The DataCite
archive verifier rejected native server-relative archive paths (including the
maintained folder name containing spaces); it now maps the known Documents
library path beneath an explicit local archive root and keeps traversal and
cross-run hash guards. The ARDC base failure-receipt graph referenced
`Current_response` before initializing it; the variable is now initialized, and
the page-retention transformer accepts only that expected single-variable state.
Crossref's environment-configured contact now omits an empty `mailto` query/header
instead of sending `mailto=`. These changes are local only; native flow acceptance
is unchanged.

Focused review suite: 36 tests across the five E01 preparation modules, DataCite
archive verification, and Crossref request construction pass. This does not
qualify the still-open source continuation, source-health, ClinicalTrials native
restoration or digest binding requirements.

### DoRA live-run status — 22 October 2026 16:24 UTC

The preserved controlled full-restart run
`08584089251920110855873024124CU24` remains Running about 64 minutes after
start. Exact flow readback remains Started with the daily 04:30 Brisbane
recurrence and concurrency one. The native loop input contains 709 unique IDs.
The exact SharePoint run folder contains 619 unique record files (22,214,123
bytes); all match IDs in that input, with zero unexpected and 90 not yet written.
All36 collection-before pages remain present; 656 files total and no manifest or
completion marker. `For_each_record` remains Running; latest item timestamp is
16:23:55 UTC. Failure-only queries for all 16 loop actions at 16:24 UTC returned
zero. Preserve
the run and avoid overlap, resubmission or cancellation. On this same run,
reconcile all 709 keys and verify after-scan/completion artifacts. Receipt:
`private/ops/2026-10-22-e01-dora-checkpoint-lineage/full-restart-run-progress.json`.

#### DoRA same-handle follow-up — 22 October 2026 16:32 UTC

The exact run still reads `Running`; no after-scan or completion artifacts are
reported. A `Record_file` repetition query at top=100 exceeded the tool's
50,000-character limit with no partial output, while the failed-only query
returned zero. `Get_full_record` top=1 returned itemIndex0 only. The 16:24
inventory (619 of 709 matched records) remains the last reliable count; this
follow-up does not prove further progress. Keep the run handle and use a bounded
native folder/repetition readback before reconciling output.

### Exact digest target re-read — 22 October 2026 14:24 UTC

The exact live digest flow `8ec29576-10b9-3e43-d1bc-3fbc7aa49002` remains
Stopped with a manual Request/Button trigger and 86 actions. Scoped FlowAgent
readback of `properties.definition.actions.Send_verified_digest_email` confirms
the action is still `Compose`, with `qualificationOnly=true` and `emailSent=false`.
The same-target `properties.connectionReferences` readback contains Power BI,
Dataverse and OneDrive references only; it contains no Outlook reference. This
independently reconfirms the H05a implementation gap. No edit or run was made.

The local source-freshness page builder continues to label unavailable provider
timestamps as Unknown and distinguishes latest imported observation from source
currency. Native model/report changes belong to the existing model/report owner;
the local builder is not evidence of an accepted native projection. Keep provider
freshness/coverage open for Crossref, DataCite, ClinicalTrials.gov, PubMed, DoRA,
ARDC, ROR and QGIP according to the plan's source-specific limits. In particular,
do not reuse stale or unversioned cursors to claim continuation. The user-approved
DataCite web diagnostic is already reconciled in its accepted receipt and was not
repeated.

#### Recovery preflight — 22 October 2026 14:54 UTC

The ARDC resubmission `08584089276494102008605090522cU14` completed Succeeded
from the normal `rif` `ListRecords` initial URI. It read prior marker
`ardc-registry-complete-08584092553880554107692675346CU07.json`, restarted at
page zero without reusing the injected failed run's token, passed `Guard_complete`,
and saved/read/byte-verified its 117,672-byte manifest and completion marker.
No page/protocol/save/read/verify failure repetitions were found. The exact
Started Monday 04:00 Brisbane trigger, concurrency one and SharePoint binding
remain. Evidence: `private/ops/2026-10-22-e01-ardc-restart/restart-runtime-acceptance.json`.
This qualifies safe restart for the incremental query; cross-run OAI token reuse
and shared source-health projection remain open. The separate DoRA native
preflight confirmed Started daily 04:30 Brisbane, concurrency one, offset reset
to zero and five-second page waits. The exact normal offset-zero restart is now
running as `08584089251920110855873024124CU24`; at 15:45 UTC its native loop
input contains 709 IDs, but a reliable latest completed-iteration count is not
exposed. Failure-only queries for all 16 loop actions return zero; no after-scan or completion marker is recorded. Preserve this handle
and do not overlap source writes.

## Local failure-contract hardening and current readback — 2026-09-30

The local paged-batch validator now fails closed for malformed batch inputs, nonpositive or non-integer expected counts, non-text/untrimmed identities, and the existing incomplete-page, cursor, count, duplicate, partial/error and independent-key-set cases. The focused `test_publication_batch_contract.py` suite passes all 11 tests.

BrowserOS neo read the canonical publication flow in a new owned tab. Power Automate showed it Disabled; its details page exposed ten recent history rows and one visible Power BI connection summary. Read-only action inspection found that the readiness query omits `PublicationRows`, the chain has no row-count guard before invalid-key filtering, and the publication query classifies every nonblank PMID as `pubmed:` while otherwise using `dora:` plus `CanonicalKey`. The local candidate includes the row-count guard and the generic strict positive-PMID/validated-DoRA identity rule. This is material saved-definition drift. No definition edit, export, save, run or enablement was performed. Browser receipts: `private/ops/2026-09-30-e01-publication-flow-browser-readback-private.json` and `private/ops/2026-09-30-e01-publication-flow-action-readback-r1-private.json`. PAC CLI list/actions did not resolve this UI-visible flow under the tested environment route, so the browser remains the current readback path.

This does not close E01-H04: action-level failure/recovery and row reconciliation remain unproven. T11-H02 data-layer acceptance is still prerequisite; therefore there was no online flow save or run. Keep the native task open until data-layer acceptance passes and a controlled isolated failure/replay test can be run with exact rollback and cleanup evidence.

## Implementation Summary
1. **Flow Definition Canonicalized:**
   - File: `config/flows/publication-registry-upsert.definition.json`
   - Name: `CHHHS Research Publications - Daily Ingestion & Enrichment`
   - Trigger: `Recurrence` daily at 20:00 UTC (06:00 AEST).
2. **Manifest Template Canonicalized:**
   - File: `config/flows/manifest.template.json`
   - Name: `CHHHS Research Publications - Daily Ingestion & Enrichment`
3. **Build Script & Deployable Package:**
   - Generator: `scripts/build_sharepoint_upsert_package.py` updated to inject the recurrence trigger.
   - Package: `private/ops/flow-packages/sharepoint-upsert.zip` generated and verified.
4. **Platform Handshake:**
   - The flow runs 1 hour prior to the dataset refresh at 07:00 AEST, ensuring the Power BI model consumes the latest daily SharePoint upserts.

## Native DEV flow test — 2026-09-20

The current Power Automate environment was inspected through authenticated
Playwright UI readback. The active history-commit DEV flow completed all six
actions successfully after changing both text failure markers from `int(...)` to
plain text. Flow Checker returned zero errors and zero warnings. The manual
ingestion DEV flow completed its Power BI query, SharePoint `Get items`,
new-publication condition and the True-branch `SharePoint Create item`
successfully; the False-branch update was skipped for the new row. Its list
action read back HTTP 200 from the configured `Publication Registry` list. That
flow was restored to Off after the manual test. The private run evidence is
`private/ops/2026-09-20-powerautomate-publication-flow-tests.json`.

This closes current DEV/manual execution evidence only. It does not close the
recurrence deployment, unattended schedule, full registry reconciliation or
production release gates.

The controlled replay also succeeded but again took the Create branch and skipped
Update. The observed blank SourceKey filter means this is not idempotency proof;
duplicate prevention and a nonblank-key update readback remain open.

## Review remediation — 2026-09-20

The first source-only review found that the tracked JSON definition and generated
package were not the same action graph. The readiness query returned a single
summary row, while the loop treated it as a publication; this explains the
blank `SourceKey` filter observed in the native replay. The tracked definition
and builder now share the corrected graph: readiness, a dedicated canonical
`Publication` rows query, a serial upsert loop, duplicate-key fail-closed
handling, and the protected update allowlist.

Local verification: `python3 scripts/validate_publication_platform_contract.py`,
JSON parsing, and the full unittest suite (283 tests) pass. This is still
source-only evidence. The isolated tenant deployment and create/replay/update,
duplicate, failed-batch, recurrence and reconciliation readback tasks remain
open, so the track remains in progress and must not be archived yet.

The corrected package was subsequently imported and read back on the retained
canonical DEV scheduled-flow identity. Both Power BI actions use the same
isolated model. Power Automate readback showed the canonical flow name, the
`Recurrence -> readiness -> publication rows -> Apply to each Publication`
chain, Flow Checker `Errors (0)` and `Warnings (0)`, and the flow Disabled. The
redundant disabled manual duplicate was removed, leaving one canonical flow
identity.
The actual recurrence run remains gated because activation requires explicit
approval.

## Current native status readback — 2026-09-20

The canonical flow details page was re-read through the authenticated Power
Automate UI. The flow is currently **Off**. Flow Checker reports **0 errors**
and **1 warning**; the warning is the expected inactive-flow warning, not a
proof of action correctness. The visible 28-day history contains 2 succeeded,
1 test-failed and 3 failed runs. This mixed history does not establish
consecutive-cycle, unattended, recurrence or release acceptance.

No edit, enable, run, list write or schedule activation was performed during
this readback. The evidence is recorded in the ignored private receipt
`private/ops/2026-09-20-powerautomate-publication-flow-tests.json`. Native
execution, replay/update and reconciliation gates therefore remain open.

## Current live retest correction — 2026-09-21

The authenticated Power Automate UI was used to run the retained canonical
scheduled DEV flow after isolating the prior failure. The original
`Run publication rows query` returned HTTP 400 `DatasetExecuteQueriesError`,
so the SharePoint loop was skipped. `EVALUATE TOPN(1, Publication)` succeeded,
proving the dataset and `Publication` table were reachable. The rows query was
then changed to a bounded `TOPN(100)` plus `SELECTCOLUMNS` projection, removing
the redundant nested readiness filter.

The corrected run read back `Succeeded` for the recurrence, readiness query,
publication rows query and 100-record `Apply to each Publication` loop. The
inspected `SharePoint Get items` action also succeeded against the
`Publication Registry` list. Flow Checker read back 0 errors and 0 warnings;
the flow was left On, matching its prior scheduled state. Run IDs and the
private list readback are recorded in
`private/ops/2026-09-20-powerautomate-publication-flow-tests.json`.

This closes the current DEV flow execution blocker. It does not prove
organisation-wide target ownership, unattended consecutive cycles, complete
registry reconciliation, or production acceptance; those gates remain open.

## Review Report: E01 Flow Automation — 2026-09-21

### Summary

The corrected publication rows query is consistent between the tracked flow definition and package builder, and the authenticated DEV retest proves the intended Power BI-to-SharePoint action path. The track remains in progress because the broader native operational acceptance contract is not complete.

### Verification Checks

- [x] Plan Compliance: Partial — the corrected-query retest is complete; replay/update, duplicate, failed-batch, reconciliation and unattended-cycle tasks remain open.
- [x] Style Compliance: Pass — the definition remains SharePoint-list-backed and preserves the existing serial, fail-closed graph.
- [x] New Tests: Yes — bounded-projection contract coverage was added.
- [x] Test Coverage: Partial — local contracts and live DEV execution are covered; full native operational acceptance is not.
- [x] Test Results: Passed — 318 tests, 438 project checks and Conductor validation passed; live corrected run succeeded.

### Findings

No new implementation findings. The documented open acceptance gates are substantive, not review defects, so E01 is not eligible for archive.

## Source-key guard repair and controlled run — 2026-09-22

An authenticated readback of the retained DEV scheduled flow found a successful
scheduled run whose SharePoint lookup used a blank `SourceKey` filter. The
lookup returned HTTP 200, but that result cannot establish idempotency.

The canonical definition and package builder were repaired with
`Compose SourceKey Required` immediately before `SharePoint Get items`. It
uses a foreach-compatible failing conversion when `SourceKey` is blank, so a
blank identity cannot reach the registry lookup or a write. The repaired action
was saved to the same isolated DEV flow and reloaded: the native checker showed
0 errors and 0 warnings, and the readback confirmed the action ordering. The
definition, builder and focused contract test were reconciled under the private
source snapshot `private/ops/publication-sourcekey-guard-native-parity-snapshot-20260922.json`.

One manual DEV run was submitted to exercise the saved repair. Power Automate
initially confirmed only that it successfully started. A later authenticated
history readback identified it as a 30-second **Test failed** run. Both Power BI
queries succeeded, then the first of 100 loop items failed at `Compose SourceKey
Required` because its `SourceKey` could not be converted from blank. The
SharePoint lookup and all write branches were downstream and did not run.

This proves the guard blocks the known bad identity before persistence. It also
reveals that the isolated model currently emits at least one identity-defective
publication row, so a create/replay/duplicate test would only repeat the same
safe failure. Repairing that source requires an approved isolated semantic-model
write and model readback; it must not be hidden by filtering or synthesising a
replacement key in the flow. The guarded native-save and run readbacks are
retained in ignored private receipts under `private/ops/`.

## Bracketed-key and PMID schema correction — 2026-09-22

BrowserOS action-output readback corrected the earlier diagnosis: Power BI
returned populated keys named `[SourceKey]`, `[CanonicalKey]` and so on. The
flow had referenced unbracketed names, which produced the apparent blanks. All
guard, lookup and create mappings now use the actual bracketed result keys in
the saved DEV flow, tracked definition and package builder.

The first corrected run reached SharePoint and exposed a separate schema defect:
the DEV `PMID` column was numeric, so publications without a PMID failed connector
validation. The isolated DEV column was changed to Single line of text, matching
PMID's identifier semantics and preserving missing values without a synthetic
number. Flow Checker read back 0 errors and 0 warnings.

The next controlled run succeeded across all 100 iterations. A replay also
succeeded: all 100 Create actions were skipped and all 100 Update actions
succeeded, proving the saved lookup/update path is idempotent for this bounded
set. Private receipts are
`private/ops/2026-09-22-browseros-publication-create-run.json` and
`private/ops/2026-09-22-browseros-publication-replay-run.json`.

Local reconciliation also passed: 325 tests, 438 project checks, web-first
contracts, Conductor validation and tooling preflight. These results establish
the isolated DEV create/replay path; duplicate-case injection, full registry
reconciliation and unattended consecutive-cycle acceptance remain open.

## Complete canonical-set reconciliation — 2026-09-22

The saved DEV rows query was then moved from the controlled 100-row validation
batch to the complete canonical `Publication` projection. BrowserOS readback
of the submitted test run reports `Succeeded` after 17 minutes 03 seconds,
with zero failed loop iterations. The isolated run receipt is
`private/ops/2026-09-22-browseros-publication-full-reconciliation-run.json`.

The Power Automate repetitions endpoint returned its first 100 entries for
each action; it therefore confirms the first page of replay/create statuses
but is not used as a claim of complete action-count pagination. The successful
full-run status and zero failed iterations establish the completed DEV flow
run; exact registry key-set reconciliation remains an explicit follow-up
readback rather than an inferred count.

## Key-set reconciliation readback — 2026-09-22

The full run's signed Power Automate action input was compared with a complete,
single-page BrowserOS SharePoint readback. All 1,329 unique model `SourceKey`
values are present in the DEV Publication Registry, and neither side contains
duplicate keys. The registry has four additional unique legacy keys. Their
values are retained only in the ignored private receipt
`private/ops/2026-09-22-browseros-publication-keyset-reconciliation.json` for
provenance adjudication; they were not deleted or silently hidden.

The four held keys were then read back individually. Each is a DORA-sourced,
PMID-absent record first observed on 2026-09-12 and retains a stable legacy
canonical key. They are not present in the current model key set. This is
historical-source evidence, not a safe basis for deletion: a provenance
adjudication rule or reviewed disposition is required before any cleanup.

## Duplicate-key guard run — 2026-09-22

An isolated temporary duplicate `SourceKey` fixture exercised the saved native
guard. BrowserOS run readback reports a **Test failed** result after 15m 26s:
the 1,329-row loop reached `Condition Duplicate SourceKey` after the SharePoint
lookup, and no dependent upsert action succeeded. This is the expected
fail-closed result. The ignored receipt is
`private/ops/2026-09-22-browseros-publication-duplicate-guard-run.json`.
The temporary fixture remains pending action-time deletion confirmation, so no
subsequent ingestion run may start until cleanup is read back.

The approved cleanup was completed immediately after the guard readback. Direct
item readback returned absent, and a filtered registry readback found exactly
one remaining canonical match for the tested SourceKey. The cleanup receipt is
`private/ops/2026-09-22-duplicate-guard-fixture-cleanup.json`. The next native
gate is therefore a readback of the existing enabled flow's next scheduled
cycle, with no schedule or delivery change.

A BrowserOS baseline readback confirms that the canonical DEV flow remains On
and Scheduled after cleanup. Its latest completed run is the deliberate
duplicate-guard failure; this does not substitute for the next unattended
recurrence. Receipt:
`private/ops/2026-09-22-browseros-publication-scheduled-baseline.json`.

## Recovery-model controlled replay — 2026-09-24

The retained DEV flow's controlled replay reached a terminal **Succeeded**
state: readiness query, publication rows query and all 1,335 serial loop
iterations succeeded; the loop duration was 15m 3s. Complete registry
exports contained 1,642 items both before and after the replay. All 1,277
expected PubMed keys had advanced `LastObserved` values. The comparison found
zero added or removed items or keys, blank-key item changes, duplicate keys,
PMID mismatches, or changes to reviewed fields and `FirstObserved`. The native
run and comparison receipts are
`private/ops/2026-09-24-publication-controlled-replay.json` and
`private/ops/2026-09-24-publication-replay-verification.json`.

This proves list-level replay stability for the accepted PubMed set. At this
checkpoint the six action-level create/update branches were still open; later
correlated readbacks below close E01-H02. Failure recovery, full canonical and
unattended operational acceptance remain separate gates.

## Root SourceKey preflight native replay — 2026-09-24

The scoped package was imported into the existing DEV flow. The designer
showed `Filter_invalid_SourceKeys` and `Condition_Invalid_SourceKeys` before
the publication loop; Flow checker reported zero errors. The import left the
flow Off. A controlled test completed successfully in 14m 11s. The preflight
filter returned an empty array for the current 1,335-row batch, the loop
succeeded, and the flow remained Off after the test.

A fresh complete 1,642-row registry export reconciled with the prior baseline:
all 1,277 expected PubMed `LastObserved` values advanced, with no item/key,
blank-key, duplicate, PMID, review or `FirstObserved` drift. Native and
registry receipts are `private/ops/2026-09-24-publication-sourcekey-preflight-native-acceptance.json`
and `private/ops/2026-09-24-publication-preflight-replay-verification.json`.
The invalid-key failure branch itself has not been exercised in a controlled
fixture. At this dated checkpoint the six initial additions still lacked
action-level proof; subsequent correlated readbacks below close E01-H02.
Unattended recurrence remains unaccepted while the flow is Off.

## Initial six iteration correlation — 2026-09-24

The raw `Run_publication_rows_query` output for run
`08584113582019259282186589014CU27` contains 1,335 ordered publication rows.
Each of the six previously missing PubMed keys was matched to its 1-based loop
iteration and current registry item ID. This narrows the remaining readback to
six saved loop repetitions. It does not establish that their `Create item`
branches succeeded or correlate returned IDs. Private correlation:
`private/ops/2026-09-24-publication-initial-six-loop-index-correlation.json`.


## Native action-level proof: first addition — 2026-09-24

The existing authenticated run `08584113582019259282186589014CU27` was read
back in the Power Automate run-history UI. For iteration 119, the SharePoint
lookup filter was `field_1 eq 'pubmed:42767656'`, returned HTTP 200 with zero
items, the duplicate-key failure action was skipped, and `Condition Is New
Publication` succeeded with the True-branch `SharePoint Create item` action
succeeded. Create returned HTTP 201, `ID=1638` / `ItemInternalId=1638`,
`field_1=pubmed:42767656`, and `field_2=PMID:42767656`. The ID matches the
current registry export. This closes action-level Create evidence for this one
addition only; the other five additions, independent GET-by-ID, and replay
Update evidence remain open. Private correlation receipt:
`private/ops/2026-09-24-publication-initial-six-loop-index-correlation.json`.

The returned ID was then independently read through the existing authenticated
SharePoint REST tab: GET item 1638 returned the same SourceKey, CanonicalKey,
PMID, title and Needs Review status. Its current ETag is 3 and Updated is later
than the flow run, so this confirms current identity by returned ID but is not an
immediate post-create snapshot and does not prove which intervening version came
from replay. The other five additions and a separately controlled replay/update
readback remain open.


## Run-history detail cache discrepancy — 2026-09-24

While inspecting iteration 253, the selected `SharePoint Get items` inputs
showed `pubmed:42772849`, but the `SharePoint Create item` detail panel returned
the earlier iteration 119 payload/ID 1638. This is contradictory UI detail and
was excluded from evidence. A reload of the same run URL then left the canvas
empty; after 30 seconds the expected loop text did not appear. Keep iterations
253 and onward open until a clean authenticated run-history readback correlates
each Create input/output with its selected loop iteration. No tenant object was
modified during this inspection.


## Native action-level proof: second addition — 2026-09-25

After reloading the existing run page, iteration 253 was reselected and the
run-history UI showed `SharePoint Get items` filtered to
`pubmed:42772849` (HTTP 200, 12-byte empty response), Duplicate SourceKey
condition succeeded with failure marker skipped, and Is New Publication
succeeded with the True Create branch. The Create action output showed HTTP 201,
ID/ItemInternalId 1639, matching SourceKey, PMID and title. Independent
SharePoint REST GET by 1639 returned the same key, PMID, title and Needs Review
status. Current ETag 3 and Updated timestamp post-date the run, so they confirm
current identity but do not identify intervening updates. The private correlation
receipt now contains two trustworthy action-level proofs; four remain open.

### Initial-six additions: third action-level Create proof (iteration 1050)

Authenticated Power Automate run `08584113582019259282186589014CU27`, selected loop iteration 1050/1335. `SharePoint Get items` succeeded with filter `field_1 eq 'pubmed:42771227'` and HTTP 200/12-byte empty response; duplicate failure marker was skipped. `Condition Is New Publication` succeeded on its true branch. Create returned HTTP 201 with ID/ItemInternalId 1640, SourceKey `pubmed:42771227`, PMID `PMID:42771227`, title “Computational Approaches to Penicillin Allergy De-labelling: A Clinical Review.” Action start/end at 2026-09-24 11:29:20Z. The raw action output included the exact returned row. This is the third of six action-level Create proofs; independent GET-by-returned-ID and per-key replay Update/no-Create proof remain open.

Independent GET by Create-returned ID 1640 confirmed `field_1=pubmed:42771227`, `field_2=PMID:42771227`, `field_10=42771227`, matching title and `Needs Review` (ETag 3; Updated 2026-09-24T14:07:47Z). This is current identity/value confirmation, not immediate post-create history.

### Initial-six additions: fourth action-level Create proof (iteration 1211)

Authenticated run history showed the pager at 1211/1335. The `SharePoint Create item` input carried `pubmed:42764148` and `PMID:42764148`; output was HTTP 201, ID/ItemInternalId 1641, initial ETag 1, created at 2026-09-24T11:31:05Z, with the expected title and key fields. Current authenticated GET by returned ID confirms SourceKey, PMID, numeric PMID, review state and title (ETag 3; Updated 2026-09-24T14:10:40Z). This is the fourth of six Create proofs; per-key pre-create match and replay branch evidence remain separate acceptance gates.

### Initial-six additions: fifth action-level Create proof (iteration 1212)

The authenticated run-history pager showed 1212/1335. `SharePoint Create item` inputs carried `pubmed:42764356` and `PMID:42764356`; output was HTTP 201, ID/ItemInternalId 1642, initial ETag 1, action time 2026-09-24T11:31:06Z, with the expected title/key fields. Current authenticated GET by returned ID confirms the same key, PMID, numeric PMID, Needs Review status and title (ETag 3; Updated 2026-09-24T14:11:04Z). Fifth of six proofs; per-key preceding GetItems and replay Update/no-Create remain separate gates.

### Initial-six additions: sixth action-level Create proof (iteration 1335)

Authenticated run-history pager showed 1335/1335. Create inputs carried `pubmed:42761504` / `PMID:42761504`; output was HTTP 201, ID/ItemInternalId 1643, initial ETag 1, with matching key fields/title at 2026-09-24T11:32:24Z. Independent authenticated SharePoint GET by returned ID confirmed ID 1643, matching SourceKey, PMID, numeric PMID, title and Needs Review status. All six initial additions now have action-level Create output and current GET-by-ID evidence. Immediate version history, preceding GetItems branch attribution for remaining items, and replay per-key Update/no-Create evidence remain open.


### Controlled replay: six initial additions followed Update/no-Create

Authenticated Power Automate replay run `08584113554261775586350368486CU08` was read at iterations 119, 253, 1050, 1211, 1212 and 1335. For each mapped key (`pubmed:42767656`, `42772849`, `42771227`, `42764148`, `42764356`, `42761504`), Get items succeeded (HTTP 200) for the exact SourceKey; the Is New false branch's Update item succeeded (HTTP 200) against the previously created item IDs 1638–1643 with the corresponding numeric PMID; the true Create branch was Skipped. Run/action timestamps and the current/full response pointers are saved in the ignored private correlation receipt. Aggregate replay receipt independently confirms 1,277/1,277 expected PubMed keys advanced LastObserved with unchanged row/item/key/review/FirstObserved sets and no duplicates. The six action-level reads are correlated samples, not per-iteration action reads for all 1,277 rows. Publication capture is stronger; E07 retention policy, stub provenance, and operational acceptance remain open.

## Local fail-closed query-batch guard — 2026-09-25

E01 audit found that the old loop and package builder used `coalesce(...rows, createArray())`: a missing query envelope could therefore look like a successful empty batch, and readiness did not expose the canonical Publication row count. The tracked flow now requires a positive `PublicationRows` readiness count, compares it with the exact rows-query result before the invalid-key preflight, and passes the rows array directly so malformed or unavailable envelopes fail before writes. The package builder clones the tracked count and full-batch key guards rather than maintaining duplicate expressions. The previous ignored private package was retained as `sharepoint-upsert-pre-rowcount-guard-20260925.zip`; the regenerated local review package passes the structural contract. No package was imported and no tenant state changed.

The same audit confirmed that within-run serial processing does not prevent two overlapping runs from racing on a SourceKey because current SharePoint documentation/readback establishes indexing, not unique-value enforcement. E01-H03 now explicitly requires blank/duplicate disposition followed by SourceKey uniqueness-setting readback before concurrent or scheduled acceptance. This local fix does not close native failure/recovery tests or that list-column gate.

The row-count comparison proves cardinality agreement across the two local query actions; equal-count key/content drift between separate model reads remains possible. Native acceptance must therefore still reconcile the complete source and list key sets against one captured model generation, and the flow's two reads are not treated as a transaction.


## Generic source-key projection repair — 2026-09-28

The package builder and tracked definition now derive `pubmed:<PMID>` only from a positive canonical numeric PMID; otherwise they accept a strict official DoRA handle URL and emit its canonical key, or blank when identity is unusable. Create and Update both copy digits into the PMID field only for `pubmed:` keys and clear stale PMID values for non-PubMed keys. This replaces sentinel/malformed PMID classification with source-generic rules; no record-specific codes were added. The native DAX engine synthetic probe covered valid PMID, zero/malformed PMID fallback, invalid/ambiguous handles, dual-source preference, and leading-zero input.

The rebuilt private review package passes the expanded structural platform contract. Its prior package is preserved as `private/ops/flow-packages/sharepoint-upsert-pre-sourcekey-identity-20260928.zip`. Focused source-key tests and the full local harness pass (1,013 tests; project, web-first, Conductor and tooling checks pass). This is local package/test evidence only: the package has not been imported, run, or enabled online. The exact definition, manifest, builder, validator, candidate package and rollback package are fingerprinted in `private/ops/2026-09-28-e01-h03-sourcekey-import-snapshot-private.json`; the immediate drift check passed. Before import, reread the exact existing DEV flow, rerun this snapshot's drift check immediately before the write, and preserve the flow's Off state. Microsoft CLI auth is via VS Code.


## E01-H02 bounded create/replay cycle closed — 2026-09-28

The saved private receipts were checked per key before closing E01-H02. All six initial PubMed rows have Create HTTP 201 outputs with matching SourceKey, PMID and SharePoint item IDs plus current GET-by-ID evidence. The same six keys in replay run `08584113554261775586350368486CU08` each have successful GetItems, Update HTTP 200 against the same item ID and Create skipped. The replay completed 1,335 iterations. Full registry comparison passed: 1,642 rows before/after, all 1,277 expected keys advanced, and no row/key additions or removals, blank-key changes, duplicates, PMID mismatches or reviewed/FirstObserved drift. Receipt-hash-bound audit: `private/ops/2026-09-28-e01-h02-bounded-cycle-audit-private.json`.

This closes only the bounded initial create/replay subtask. It does not establish live parity for the newly rebuilt generic source-key package, invalid-key failure recovery, unique-key enforcement/concurrency, retention, complete source/model acceptance or unattended operation.


## Current native status readback — 2026-09-28

An authenticated, read-only BrowserOS neo detail-page readback of the existing
publication ingestion flow showed status **Off**, type Scheduled, last modified
24 September, and latest listed run “Test succeeded” (24 September, 14m11s).
The details page displayed a generic warning banner on repeated reads. The
existing editor's Flow Checker returned 0 errors and 0 warnings, so its cause
is unresolved. The current details-page connection summary visibly listed
Power BI only, while the 24 September import receipt records both existing
Power BI and SharePoint connections selected. This display discrepancy does
not prove a missing SharePoint binding; reconcile current action-level binding
before any update. The Power Platform MCP flow-list fallback returned a
shared-lock error. No run, import, enablement, connection change or other
tenant mutation was performed.
Private receipt: `private/ops/2026-09-28-publication-flow-browseros-details-private.json`.
This confirms current status only; it does not accept H03, explain the warning,
or prove current action bindings, key uniqueness, failure handling or cadence.

## Bounded row-count guard native deployment — 2026-10-03

User-authorised stopped-flow definition update completed through the ordinary
legacy-package importer after fresh native rollback/export, prewrite GET and
source drift checks. The candidate changes one ZIP member/six paths, preserving
the newer key guard, rows projection, trigger and existing connector bindings.
Readiness now emits positive PublicationRows; the count condition checks exact
rows length before key preflight; filter and loop no longer coalesce missing
results to an empty array. Native import success, exact full-definition/connection/
Stopped-state readback parity and reopened Flow Checker 0/0 are evidenced.
Final details Off, modified 14:01 AEST, no new run. Generic details warning remains;
designer validation and operational acceptance are recorded separately.

Receipt: `private/ops/2026-10-03-s02-publication-row-count-native-update-acceptance-private.json`.
Rollback: `private/ops/flow-packages/publications-native-rollback-before-row-count-20261003.zip`.
Source snapshot: `private/ops/2026-10-03-s02-row-count-native-import-source-snapshot-private.json`.
S02 review records route/preparation detail. Focused tests 25/25; integrated
harness passed 1,263 tests, 446 project checks and remaining required stages.
No run/activation/notification, list/model/report change or solution addition.
H03/H04/H05 remain open for strict identity projection, data-layer exit,
concurrency, runtime failure/replay and cadence acceptance.

## CLI-first planning update — 13 October 2026

User authorised routing remaining work through the proven CLI approach.
Existing plans/specs were extended for shared raw data retention and publications
first; Power BI presentation stays last. Scoped routes now exist in 14 plans;
four open implementation tasks record capture, persistence, consumers and the
existing digest. Current native owners, stable IDs, accepted historical scopes,
activation/permission gates and rollback remain intact. Access-probe receipt:
`private/ops/cli-access-probe-20261013/receipt.json`. Conductor structure passed
with 0 errors; targeted plan checks passed for all 14 sections, execution links
and four unique task entries. No native implementation or task closure occurred
in this planning update. Next implementation is T11-H01a under agreed source
ownership, followed by E01-H02a; current archive/digest operations retain their
existing next actions and must not be overwritten by this support checkpoint.

## Raw archive extension and comparison — 13 October 2026

E01-H02a is implemented locally in the existing preparer; native acceptance is open.
The prior source implementation exposed payload/schema chunks in one model part.
This extension persists those observations through the existing writer and gates
accepted work independently. Narrow packet/scope checking caught the archive-versus-
registry profile mismatch before edits. Reusing qualified native action templates
preserved trigger/connections and 50 of 51 original actions; only entry dependency
changes. Native timing/throughput cannot yet be compared: neither new slice has
completed its recorded native gate.

Initial per-page action expansion was replaced before deployment by constant-size
serial loops after checking Microsoft's 500-action limit. Source/header/length
comparison runs before file access, and complete reconstruction/byte matching
remains part of native readback. DAX zero-count BLANK semantics required COALESCE;
logical audit failures must be recorded separately from transport/decode failures.
Accepted raw and typed R1 identities must agree; rejected evidence must not force
rebasing the last-good typed manifest. Segmented indexes bound descriptor strings.

Checks: 14 changed-scope tests + 5 retained-package tests + 20 harness tests pass.
A four-megabyte synthetic capture with more than 100 data files uses the same graph
and two index parts; this is structural/local evidence, not native throughput proof.
Real saved-baseline rehearsal: 156 nested actions, about 200KB definition, no raw
payloads embedded, no connected synthetic candidate saved. No import, activation,
file write or accepted marker occurred. See the private final rehearsal receipt.

Next: obtain the source capture and writer handoff; verify runtime adoption,
permissions, paging, stored byte equality and replay once. T11-H02a must bind a
verified raw root/index chain to the same accepted typed commit, preserve legacy
readers and keep staged/rejected observations outside secondary views. Fixed-batch
qualification does not close routine automation. Lessons are incorporated in
SOLO_AGENT_WORKFLOW.md and the T11/E01 plans rather than a new tooling backlog.

## Archive commissioning repairs — 13 October 2026

Existing Azure CLI recovered through the supported exact tenant/Flow scope. FlowAgent scoped definition and history reads qualified; input invocation rejected by Logic Flows ACL, with empty subsequent history. Owning BrowserOS accepted the fixed manifest. First terminal native failure: Validation_row returned literal expression text; source generator and native action repaired with a leading @, exact state-preserving HTTP204 save and active Flow API readback. Second terminal failure: timestamp predicate used R2 instead of the actual R1 source window. Native counts/key sets/metadata characters/audits matched; existing local validation already bound R1. Source and runtime guard now align, with only two timestamp paths changed. All36 focused native-package/raw-archive tests pass on Python3.15. Third changed-cause native run is recorded under `private/ops/2026-10-13-archive-source-window-*`; acceptance remains open until terminal persistence and stored-byte readback. Original connectors, state, expected manifest and other guards/actions preserved.

## Review Report: E01 current implementation increment — 22 October 2026

### Summary

The accepted writer/read-reader receipts and digest documentation handoff remain valid. DataCite's completed-query-prefix/full-reconciliation failure-receipt fields now have bounded native runtime proof through the authorized web Run diagnostic, with no provider requests or accepted-checkpoint writes and exact normal-graph restoration. ARDC's controlled protocol-error run is preserved. E01 remains in progress because provider continuation/source-health work and actual digest mail wiring are incomplete.

### Verification Checks

- [x] Plan Compliance: Partial — accepted writer/read-reader evidence and the later canonical export are reconciled; DataCite's bounded failure-receipt run passed and its exact weekly graph/binding/Started state were restored. ARDC's same-ID raw-page/failure-scope patch is saved and read back, and a real HTTP200 OAI protocol-error run proved raw page and failure receipt byte readbacks before exact weekly restoration. Cross-run continuation and source-health outcomes remain open.
- [x] Style Compliance: Pass — reviewed changes preserve existing flow identities, bindings, archive paths, fail-closed completion and publication gates.
- [x] New Tests: Yes — DataCite failure-receipt graph coverage was added.
- [x] Test Coverage: Partial — focused local guards cover ARDC receipt placement, raw XML preservation, per-request diagnostic capture, pre-validation archive ordering, uncertain completion-write state and duplicate-preparation refusal. DataCite bounded failure receipt and ARDC real protocol-error raw-page/failure-receipt persistence are natively qualified; resumed OAI token and cross-provider continuations remain open.
- [x] Test Results: Passed — this review pass ran 26 focused unit tests across the ARDC, ClinicalTrials.gov, DataCite, DoRA and PubMed preparation modules; Conductor structure validation reports 0 errors and scoped diff check passes. Prior native evidence remains distinct: the DataCite completed-query-prefix/full-reconciliation diagnostic and ARDC provider-error run each passed their bounded save/readback checks with normal graphs restored. Cross-run continuation and source-health projection remain open.

### Findings

#### High — DataCite cross-run continuation needs archive and verifier support

- **File**: `scripts/prepare_datacite_discovery_collection.py`
- **Context**: The 22 Oct same-ID manual continuation consumed the exact failed-run query prefix and independently hashed saved page, pinned the old cutoff and delta mode, asserted the full last-good checkpoint identity, skipped the completed query, and processed the remaining queries. `Guard_complete`, `Save_completion`, `Read_completion` and `Verify_completion` succeeded; the SharePoint write returned HTTP 200 and exact readback verification returned true. The exact normal 50-action Thursday 05:00 graph and binding were restored. Evidence: `private/ops/2026-10-22-e01-datacite-continuation/continuation-runtime-acceptance.json`.
- **Remaining limitation**: This closes the operator-run manual recovery path. The normal weekly graph does not automatically discover and load a prior failed-generation receipt; the accepted manual recovery packet is the recovery entry point. An interrupted query's cursor must be restarted at page 1. Do not mark unattended failed-run recovery complete.
- **Suggestion**: Preserve the qualified manual recovery route and use it only with a complete, hash-verified prefix and exact checkpoint. If automated recovery is selected later, add a native receipt reader without weakening cutoff, scope or checkpoint guards.

#### High — Provider freshness/coverage and interrupted paging remain incomplete

- **File**: `conductor/tracks/E01_flow_automation/plan.md`
- **Context**: Current native reads still show gaps for ClinicalTrials cross-run page resume, DoRA interrupted collection-page resume, ARDC cross-run OAI token/page reuse, and QGIP's weekly full paging checkpoint. ARDC's safe from-page-zero restart after an injected failure now has native completion and exact marker readback. PubMed reads and validates the latest complete marker before provider requests, but still performs a full daily ESearch/EFetch and does not resume a partially completed XML-page run. ARDC also captures request outcomes/status/errors, retains raw XML with byte readback before validation, and persists response summaries; its controlled provider-error runtime and fresh restart both passed exact reads. ROR uses release ID/checksum for raw freshness, while its manifest leaves the Australian projection incomplete. Crossref's accepted continuation should not be repeated. Source freshness/coverage projections are not demonstrated across all selected sources. Exact ROR/QGIP readbacks and the terminal QGIP run remain in private evidence.
- **Current DoRA evidence**: The native reads show its cross-run collection-page resume remains open. PubMed now reads and validates the latest complete marker for run/scope lineage before provider requests, but still performs a full daily ESearch/Efetch and does not resume a partially completed XML-page run. ARDC captures request outcomes/status/errors, retains raw XML with byte readback before validation, and persists response summaries; its controlled provider-error runtime passed exact raw-page and failure-receipt readback with exact normal-state restoration. ROR uses release ID/checksum for raw freshness, while its manifest leaves the Australian projection incomplete. Crossref's accepted continuation should not be repeated. Source freshness/coverage projections are not demonstrated across all selected sources. Exact ROR/QGIP readbacks and the terminal QGIP run remain in private evidence. The observed DoRA one-second Consumption `Wait` failure occurred after a verified first page (total 709); the saved graph now has five-second waits and is Started daily. The old page remains unqualified for reuse because no provider version token was captured. Receipt: `private/ops/2026-10-22-e01-dora-checkpoint-lineage/offset-failure-reconciliation.json`.
- **Suggestion**: Address one source at a time against its exact native target and provider contract. Preserve immutable source lineage and last-good data, then verify saved native readback and a controlled runtime before checking off that source. Build source-health projection from accepted run outcomes and keep incomplete/raw-only states explicit.

#### High — Digest delivery action is still a Compose placeholder

- **File**: `conductor/tracks/E01_flow_automation/digest-runtime-completion-20261022.md`
- **Context**: Fresh service readback shows `Send_verified_digest_email` is Compose and there is no used Outlook send binding. The fail-closed gate correctly prevented delivery, but this does not implement email capability.
- **Suggestion**: Prepare the intended mail action against the existing verified connection while keeping the send-authority gate closed. Prove native action/binding readback and failure suppression before any separately authorized delivery.

### Recommendation

Keep E01 in progress. The existing writer/read-reader evidence and versioned digest documentation are accepted. The remaining findings are technical completion work; adoption, circulation, activation and later natural operation remain under their existing boundaries.

### Current evidence addendum — 22 October 2026

The user-selected writer and reader receipts were reconciled against the current
plan. The writer receipts prove the selected empty/partial/error response guards,
three genuine creates, same-ID replay, protected-field preservation, full
configured exports, SourceKey/CanonicalKey uniqueness enforcement and competing
duplicate rejection. The R45 receipts prove the selected raw-reader integration,
31-field canonical and retained parity, all 1,986 history identities, and
successful completion of the four required tables. The separate native receipt
records `runtime_and_memory_qualified=false`; therefore no engine performance or
memory qualification is claimed. The refresh and data-parity evidence still close
the selected E01 raw-reader integration dependency. These accepted cases are not
repeated. Physical Fresh projections, broader H03/H04/H05 criteria and final
report-reader acceptance remain distinct.

The digest documentation handoff is complete under the existing versioned
publisher. Its receipt records 324 assets (10 changed), all 40 native source
reopens, the 86-action/one-trigger/17-scope preview, preserved asset identities
and history, and no pending native handles. This closes the requested diagram
regeneration and documentation handoff. Email delivery remains technically
unwired (the current action is Compose) and unauthorized; it is separate from
documentation acceptance.

ClinicalTrials.gov's retained token probe used the exact saved scope query and
returned provider HTTP 400 directing the caller to start from page one because
the data changed during pagination. This confirms stale-token rejection and
supports restart-from-first-page behavior. A fresh two-page read-only probe then
continued the exact maintained query successfully while the provider
`dataTimestamp` stayed unchanged; both pages contained 100 unique, disjoint IDs.
This is same-session continuation evidence, not cross-run token durability. The
existing weekly collector already starts from page one, checks two matching
discovery passes and verifies its source timestamp before committing. Durable
checkpoint/resume remains open. Evidence:
`private/ops/2026-10-22-e01-clinicaltrials-continuation/token-stability-probe.json`.
The local continuation helper now prepares a stopped manual-only candidate from
strictly verified failed-run page evidence. It binds the source definition,
query, scope, archive run/folder and provider timestamp; validates ordered page
indices, cursor lineage, saved-byte SHA-256/readback and unique IDs; resumes only
the first discovery pass; then preserves the complete independent second pass
and source-version commit guards. Five focused tests pass. The normal weekly
graph remains unchanged. Native run `08584092670823209314684645672CU00` is a genuine
failed collector run whose first discovery page was saved and read back before
the provider-page guard failed; native repetition errors show the guard's
`greaterOrEquals` received null `totalCount` on page two in each pass. That
historical graph predates the current
source-version guard and did not capture a same-run `dataTimestamp`; its archived
cursor cannot be trusted for continuation. A direct stale-token probe returned
HTTP 400 directing restart from page one. Native runtime qualification remains
open until a bounded native failure captures source timestamp with its own saved
page, or a valid accepted same-version token is available. The 12,677-study full
scope was not replayed merely to exercise recovery. The precise reconciliation
is retained in `private/ops/2026-10-22-e01-clinicaltrials-continuation/historical-native-failed-prefix-audit.json`.

The current Started weekly definition was read back and contains the repaired
`coalesce(totalCount,-1)` guard; this is native definition evidence only. The
focused ClinicalTrials builder suite passes 5/5 and Python compilation passes.
The publications-scoped harness reached an unrelated DOCX test and failed import
because `python-docx` is not installed; no dependency was installed. Conductor
structure validation reports zero errors. No ClinicalTrials definition was
changed or run in this increment.
Focused local checks for the DataCite builder/verifier and ClinicalTrials builder
passed: 13 tests. They do not qualify a native continuation run.

The refreshed unmanaged solution ZIP was reconciled against the actual preceding
archive. It differs in exactly the ARDC and DataCite workflow definitions; the
other32 workflow JSON files are byte-identical. The prior record's 390,544-byte
and `5156b78d…` claim did not match the ZIP at that path; the actual preceding
archive is 389,936 bytes and still has the 49-action DataCite graph. The new
391,372-byte package SHA and comparison receipt are now recorded in the plan and
current-export note. ZIP integrity, safe unique paths and duplicate-key JSON
checks pass.

The ARDC negative-path qualification used the existing weekly flow identity and
a temporary one-action URI override. The provider returned HTTP200 with
`cannotDisseminateFormat`; the exact 469-byte XML response was archived and
read back before the protocol guard rejected it. The failure receipt records the
response status/outcome and `Save_completion`/`Verify_completion` were skipped.
The original definition, binding, recurrence and Started state were restored
byte-for-byte against the preimage. Evidence:
`private/ops/2026-10-22-e01-ardc-native-repair/ardc-failure-runtime-acceptance.json`.

A read-only live RDA probe repeated one opaque OAI token twice. Both responses
returned the same 100 ordered record XML elements, while full response bytes
differed; the token had no `expirationDate`. This supports immediate same-token
page idempotency only and does not establish post-interruption token lifetime,
saved-prefix lineage or cross-run resume. Receipt:
`private/ops/2026-10-22-e01-ardc-native-repair/ardc-oai-token-replay-acceptance.json`.
The ARDC continuation finding therefore remains open.

The DataCite bounded failure candidate was then saved to the existing flow,
invoked once through FlowAgent's authenticated manual trigger, and restored. Its
injected guard failed; provider/query actions and completion writes were skipped.
The run-specific receipt was saved, read back with HTTP200, and byte-verified
before the run terminated with `DataCiteGenerationRejected`. The 50-action weekly
definition, recurrence, binding and Started state match the exact pre-test
snapshot; two native backups are retained. This closes only the selected
failure-receipt runtime gate. Evidence:
`private/ops/2026-10-22-e01-closeout/datacite-failure-runtime-acceptance.json`.

The subsequent same-ID configuration repair added `complete_query_prefix` and
`full_reconciliation`. After the user's approval, the prepared qualification graph
was run once using the existing Power Automate web Run control. The 12-action
manual graph contained no provider HTTP action and no accepted completion write;
its deliberate guard failed, query/completion placeholders were skipped, and the
new fields evaluated as `[]` and `false`. The v2 qualification failure receipt
saved, read back with HTTP200 and passed exact-byte verification. The normal
50-action Thursday recurrence, SharePoint binding and Started state were restored
exactly, with no active run. Evidence:
`private/ops/2026-10-22-e01-datacite-continuation/failure-receipt-web-runtime-acceptance.json`.
This qualifies the receipt fields only; page SHA-256 and cross-run continuation
remain open.

### DoRA post-repair execution reconciliation — 22 October 2026 15:01 UTC

The restored DoRA definition was re-read: exact daily 04:30 Brisbane recurrence,
Started state, concurrency one, same SharePoint reference, and offset reset to
zero. Run history still contains no successful collection after the five-second
wait repair. One resubmit attempt specifying the restored `Recurrence` trigger
created no new run; no execution handle exists to poll. Preserve the terminal
failure-receipt diagnostic and wait for the next normal recurrence before
claiming a post-repair acquisition. The plan and active checkpoint identify the
required readback: offset-zero full scan, source key/metadata reconciliation,
completion marker and exact saved-byte verification. Last-good 709 remains.
FlowAgent's save-oriented preflight returns `block` on nine native
`extra-authentication` paths even though the SharePoint connection is Connected;
no manual run was issued and native auth fields were preserved. Private receipt:
`private/ops/2026-10-22-e01-dora-checkpoint-lineage/manual-run-preflight.json`.

#### Controlled DoRA full restart — 22 October 2026 15:08 UTC

The connection test passed and the authenticated FlowAgent run route started
`08584089251920110855873024124CU24` using the exact existing Recurrence trigger.
The save-oriented preflight errors did not require a definition save and no auth
properties were removed. Native run readback confirms the prior 709-record,
same-scope marker guard and offset-zero reset; all36 before-scan pages, their
readbacks and `Guard_complete_Before` passed. The per-record stage remains
Running. Failure-only repetition queries currently return zero failed full-record
requests and zero failed byte-verifications; the successful-repetition endpoint
is capped. No after-scan or completion write is observed yet. Preserve this run
handle and do not resubmit. Progress receipt:
`private/ops/2026-10-22-e01-dora-checkpoint-lineage/full-restart-run-progress.json`.

### PubMed prior-checkpoint lineage runtime — 22 October 2026

The live PubMed flow now reads and validates the latest complete marker before
querying the provider, then records its run, count, scope hash and modified time
in the next manifest. It never reuses previous XML; daily full-scope acquisition
and the existing before/after ESearch equality guard remain intact. Controlled
run `08584089319354348011783448763CU24` succeeded with 1,277 IDs in both search
snapshots, 13/13 XML batches saved/read/verified, all batch guards passing,
`Guard_complete=true`, and exact completion-marker readback (`true`). One prior
attempt received transient provider HTTP 502 before any acquisition pages or
completion marker; after the provider's 30-second retry interval, one authenticated
run succeeded. The resubmit API denied the first run with 403 and created no
additional run. The original daily recurrence, Started state, action graph and
SharePoint connection reference were restored and read back exactly. Receipt:
`private/ops/2026-10-22-e01-pubmed-checkpoint-lineage/acceptance.json`.
This closes prior-checkpoint lineage/freshness metadata for PubMed; interrupted
XML-page resume remains unqualified.

### DoRA failure-receipt runtime — 22 October 2026

The unmanaged daily DoRA flow now includes a failure scope that retains the
last-good marker, captures the failed generation's progress, saves and reads
back a `rims-dora-failure-v1` receipt, verifies its exact bytes, then fails the
run. Controlled web Run `08584089297655049230846717283CU15` stopped at the
injected pre-provider guard: collection/full-record requests and completion
marker write were skipped. Receipt save and readback succeeded and the verifier
returned `true`; the receipt records the prior complete count (709), offset zero,
and restart-from-zero policy. The temporary manual trigger and stop action were
removed. Native readback confirms the original Started daily 04:30 Brisbane
trigger, concurrency one, prior-marker lineage wiring and failure observer.
Evidence: `private/ops/2026-10-22-e01-dora-checkpoint-lineage/failure-receipt-qualification.json`.
This qualifies failure evidence only; provider paging has no source-version token,
so interrupted-page reuse remains unproved.


#### DoRA restart terminal acceptance — 22 October 2026 16:39 UTC

The preserved run `08584089251920110855873024124CU24` reached Succeeded. Its
709 unique record inputs completed, before/after and stable-collection guards
passed, and manifest/completion checkpoint save, readback and native verification
passed (`Verify_complete_checkpoint=true`). The flow compared exact serialized
manifest content with SharePoint `$content`; no separate out-of-band byte hash was
obtained. This accepts the offset-zero restart path for this generation. Cross-run
page/offset reuse remains unsupported without qualified source-version evidence.
The earlier 16:24 and 16:32 Running notes are superseded by this terminal readback.
Receipt: `private/ops/2026-10-22-e01-dora-checkpoint-lineage/full-restart-run-progress.json`.


### Current exact-target review — 23 October 2026

Fresh FlowAgent readback of ClinicalTrials.gov flow
`44bb0b78-8529-46f9-9377-ac7424cde8f0` still shows Stopped with the manual
Request/Button trigger and the recorded SharePoint binding. The component is
unmanaged and customizable, but the earlier FlowAgent restore response was not
accepted because readback stayed unchanged; that payload must not be retried. No
run is active. The alternate PAC exact-target probe returned AADSTS70043 from the
currently selected profile. Shared authentication ownership remains released to
another task, so this turn made no profile/authentication change. Private receipt:
`private/ops/2026-10-23-e01-current-state/ctgov-restoration-route-status.json`.

The DoRA offset-zero run acceptance appended above remains current. DataCite's
operator-run same-ID recovery and digest documentation transaction are accepted;
the normal DataCite recurrence still lacks an automatic failed-prefix reader, and
the actual digest email action remains unwired. The R45 raw-reader dependency is
closed; physical freshness projections and final report-reader acceptance remain
separate. E01 remains in progress.


### DataCite current graph review — 22 October 2026 16:47 UTC

Fresh exact-target readback confirms the normal DataCite flow remains Thursday
05:00 weekly with concurrency one and its existing SharePoint reference. The latest
listed run succeeded. The saved graph reads only the latest complete checkpoint;
its query loop resets paging state and starts the current query list. It contains no
failed-generation receipt reader or verified completed-prefix skip. The manual
same-ID recovery receipt remains valid for its bounded scope, but cannot be credited
as automatic weekly recovery. A native change needs explicit cutoff/scope/query
lineage, page byte verification, stale-receipt disposition, and commit-order guards
before controlled qualification. No mutation/run was performed. Evidence:
`private/ops/2026-10-23-e01-current-state/datacite-weekly-recovery-gap-readback.json`.

### DataCite recovery provenance local review — 22 October 2026 17:04 UTC

The local patch is pinned to the exact saved DataCite definition fingerprint and
requires a stopped, unmanaged exact-flow preimage. It adds page ETag capture only
after the existing byte readback and successful HTTP guard, and retains the
pre-run checkpoint identity/ETag in a v2 failure receipt. The focused preparation
suite passes (6 tests), Conductor structure validation reports 0 errors, and the
scoped diff check passes. No native mutation or provider run occurred. The local
patch does not yet load or validate failure receipts, so it does not close the
automatic recovery finding; native save/readback and controlled runtime remain
required.


### DataCite automatic recovery recheck — 22 October 2026 17:08 UTC

A fresh full native definition readback is saved privately at
`private/ops/2026-10-23-e01-current-state/datacite-live-flow-readback.json`.
Its canonical definition SHA-256 is
`9da071350f566e0cf72fdae787971cbba529a80195667569669efc191ec7cfc7`; the flow
is Started on the weekly Thursday 05:00 Brisbane recurrence with 50 top-level
actions. The checkpoint listing selects only `Name`; the failure observer emits
`rims-datacite-failure-v1`; no failure-receipt reader or page ETag capture exists.
The live graph includes the accepted raw PubMed and DoRA DOI producer actions,
which are absent from the older reconstruction builder. Earlier local v2/ETag
preparation therefore is not deployment evidence and cannot be applied as a
whole-definition replacement. No native mutation or provider run occurred. The
next change must be prepared from this exact live preimage and preserve producer
inputs, bindings, recurrence and state. Detailed structured readback:
`private/ops/2026-10-23-e01-current-state/datacite-weekly-recovery-gap-readback.json`.


### DataCite v2 provenance native review — 22 October 2026 17:16 UTC

The bounded diagnostic now proves the saved v2 failure receipt contains the exact
planned query array and pre-run checkpoint file/identity/ETag. Receipt save,
readback and byte verification succeeded; the injected early guard prevented any
DataCite request and any completion-marker effect. The original guard and exact
weekly Started state were restored. The saved graph captures page ETags only after
page write/readback and gates ID processing on a nonempty metadata ETag, but that
new metadata action has not yet executed on a provider page. The normal graph
still has no automatic receipt reader. Conductor `validate_flow` on current native
readback reports 16 pre-existing `extra-authentication` errors in unchanged
connector actions, identical to the captured preimage; no authentication field
was changed. Evidence: `private/ops/2026-10-23-e01-current-state/datacite-v2-provenance-diagnostic-acceptance.json`.


### DataCite checkpoint freshness readback — 22 October 2026 17:22 UTC

The saved native latest-checkpoint query now returns `Name`, `ETag`, and
`TimeCreated`. This is a prerequisite for deciding whether a v2 failure receipt
is still current before reusing its query prefix. Readback confirms the normal
Started weekly recurrence, 50 top-level actions, v2 failure receipt, and page
ETag guard remain. Seven focused preparation tests and Conductor structural
validation pass. The automatic receipt reader and page-metadata runtime remain
open; no claim of continuation acceptance is made. Evidence:
`private/ops/2026-10-23-e01-current-state/datacite-checkpoint-freshness-readback.json`.


### DataCite marker freshness runtime review — 22 October 2026 17:25 UTC

The current connector runtime returned the latest completion marker name, ETag,
and `TimeCreated` through `Find_checkpoint`. The bounded diagnostic terminated
at the injected guard before the DataCite request; failure receipt save/read/byte
verification succeeded and completion actions were skipped. The original guard
and Started weekly flow were restored. The reader still needs to compare marker
and receipt times, validate exact checkpoint/query lineage, verify each archived
page ETag, and resume only a contiguous complete query prefix. Evidence:
`private/ops/2026-10-23-e01-current-state/datacite-checkpoint-freshness-diagnostic.json`.

### DataCite automatic reader native review — 23 October 2026

The automatic failure-prefix reader is now saved and read back on the same unmanaged flow. Current definition has 63 top-level actions; exact weekly recurrence, existing SharePoint binding and Started state are present. The graph validates the newest failure receipt against time, scope, query plan and pre-run checkpoint identity; verifies reused complete query pages by contiguous name, row totals and SharePoint ETag; skips only validated complete query keys; and restarts all remaining queries from page one. Completion marker remains after the complete guard. This supersedes the 22 October reader-absent findings above. Private exact readback: `private/ops/2026-10-23-e01-current-state/datacite-automatic-reader-saved-readback.json`.

Local focused preparation tests pass (8); Conductor structure validation reports 0 errors. FlowAgent validation reports the same 16 legacy authentication-field errors plus a new error for `Find_failure_receipt`, whose connector action received an injected authentication field on save. No existing authentication field was removed or edited. Native diagnostic acceptance is still open: the authorized Power Automate web Run tab is currently owned by another agent, so no run was initiated through another route. After that owner releases the tab, run the deliberately guarded diagnostic, verify no DataCite requests or completion writes occurred, and confirm the receipt and restored Started weekly graph. E01 remains in progress.

### DataCite automatic reader runtime recheck — 23 October 2026

This supersedes the preceding note that runtime acceptance was still open. The authorized web Run `08584089159414948845797408784CU08` passed receipt/checkpoint identity, completion disposition, query-plan matching, empty-prefix qualification and completed-key seeding. The intentional post-`Run_folder` guard failed; archive creation, provider `Get_page`, and completion writes were skipped. SharePoint receipt save/read/byte verification succeeded. The existing publication DOI source list was read, but there was no DataCite provider request. The missing Boolean expression marker found in the first attempt was repaired before this run. Evidence: `private/ops/2026-10-23-e01-current-state/datacite-automatic-reader-runtime-acceptance.json`. The temporary guard was removed and final native readback confirms the 63-action weekly Started graph. Nonempty-prefix page ETag execution remains open.

### Review correction: full-size terminal page — 23 October 2026

Found and fixed an edge case: a valid final DataCite page can contain exactly 250 records when total count is divisible by page size. The automatic and manual continuation guards now allow up to 250 on the final page, while enforcing exactly 250 on nonterminal pages and the full query total. A focused test covers a 250-row terminal page. The same native guard expression was saved on the existing flow, and current readback confirms it with the normal Started weekly graph. The nonempty-prefix page-reader path still lacks native runtime evidence.
### DataCite archived-page metadata review — 23 October 2026

The approved web Run route qualified SharePoint `GetFileMetadataByPath` on the
actual archived `related-0-page-0.json`: HTTP 200, 203,344 bytes, with the
metadata ETag equal to the folder-list ETag. The equality guard passed. Two
initial bounded attempts used a nonexistent filename and returned 404; no provider
request, archive creation, or completion write occurred. The final diagnostic
intentionally stopped after the metadata guard, and receipt save/read/byte
verification passed. Temporary actions were removed; exact readback confirms the
normal 63-action Started Thursday graph and existing SharePoint binding.

Review result: plan compliance Partial; style Pass; new tests Yes (the previously
recorded nine focused DataCite tests, unchanged); test coverage Partial; test
results Pass for local focused checks, Conductor structure validation, and the
bounded metadata diagnostic. The actual nonempty-prefix loop, ETag iteration,
and row-total reconciliation remain unproved because the three recent failed-run
receipts all have an empty completed-query prefix. Do not treat metadata equality
alone as page-loop acceptance.
### PubMed fresh-restart recovery — 23 October 2026

Fresh current run history shows the normal daily run
`08584089238575771756163954669CU08` completed after the accepted failed-run
receipt `08584089286902726122143679218CU21`. The run restarted at ESearch rather
than reusing earlier XML pages. Native outputs show matching ordered before/after
sets of 1,277 IDs; all 13 XML batch save/read/byte-verification repetitions and
record-file reconciliations succeeded. The manifest and completion checkpoint
were written, read and accepted by their exact-byte guards; `Guard_complete` and
completion verification returned true. There were no failed actions. Current
readback retains Started, daily 01:30 Brisbane, concurrency one and the original
SharePoint reference. Receipt: `private/ops/2026-10-23-e01-current-state/pubmed-fresh-restart-runtime-acceptance.json`.

Review result: plan compliance Partial; style Pass; new tests No (native runtime
reconciliation only); coverage Partial; results Pass for the selected fresh-restart
path and structural validation. This does not prove cross-run XML page resume,
source freshness/coverage projection, or broader provider completeness.
### Crossref source-drift failure reconciliation — 23 October 2026

Current native history identifies run `08584089166653249081865509587CU16` as
Failed with `CrossrefGenerationRejected`. The bounded repetition read identified
`Guard_total_stable` failing at query index 3/page index 13; the query-complete
guard then failed. The failure receipt was saved/read and its byte-verification
action returned true. It records the failed query guard and skipped DOI stage,
completion write and completion readback. The exact numeric totals were not
available from the bounded repetition output. The current flow is restored Started
with its daily 03:30 Brisbane recurrence and original SharePoint reference.

Review result: plan compliance Partial; style Pass; new tests No; coverage Partial;
results Pass for fail-closed behavior only. Do not retry or weaken the total-stability
guard. The pre-run completion marker `crossref-complete-08584090222463479784369292586CU18.json` was read in the same run and passed `Guard_checkpoint`; source-health projection remains open. Receipt:
`private/ops/2026-10-23-e01-current-state/crossref-natural-drift-failure-reconciliation.json`.


### DataCite web Run boundary incident — 23 October 2026

The user authorized a bounded diagnostic. Native verification showed the candidate selectors were empty, but Run invoked the saved normal Recurrence graph because its diagnostic-stop action was absent. Exact run `08584089133689854943448526668CU04` was cancelled after two successful DataCite page requests and two query summaries were saved/read/verified. The incomplete run folder contains source/scope and partial query artifacts; no completion marker/checkpoint action ran. Flow readback confirms the 63-action weekly Thursday 05:00 Started graph and SharePoint reference remain. See `private/ops/2026-10-23-e01-current-state/datacite-web-run-boundary-incident.json`. Review result remains Partial: before another diagnostic, implement and read back a saved branch that cannot enter provider paging, then invoke only that route.

### Objective reconciliation and continuation review — 23 October 2026

The user's four requested work items were reconciled against current accepted
receipts. The writer-runtime and concurrency qualifications remain accepted and
are not reopened. The three R45 receipts prove the selected raw-reader dependency:
refresh Completed, 1,344 canonical rows/31 fields with every prior key retained,
1,277 retained rows/25 fields with zero substantive differences, and all 1,986
history identities and metadata preserved. `runtime_and_memory_qualified=false`
remains an explicit limit, not a failed reader refresh. Physical Fresh
projections and broader report-reader acceptance remain separate. Evidence:
`private/ops/2026-10-22-publications-slice1/raw-reader45-consumer-canonical-field-acceptance.json`,
`raw-reader45-consumer-retained-field-acceptance.json`, and
`raw-reader45-history-acceptance.json`.

The digest diagram/documentation handoff is also accepted and must not be
regenerated again absent changed inputs: existing publisher receipt
`private/ops/2026-10-22-e01-closeout/digest-documentation/acceptance.json`
records PASS, 324 assets/40 native sources, 10 changed assets, all prior
identities/history preserved, generation digest recomputed, and no pending
native handles. This does not implement or authorize email delivery; the saved
digest remains no-send/Stopped.

Current provider gap disposition: Crossref CU16 and its one CU31 continuation
both failed the exact `Expected == total-results` guard (CU16 page 13, CU31 page
7). The signed action outputs were fetched in memory: page 0 returned HTTP 200,
total 9,230 and 500 rows; page 7 returned HTTP 200, total 9,229 and 500 rows.
This confirms provider index drift during pagination, not a missing/malformed
field. No completion write ran; CU31's exact Started daily 56-action definition,
binding and authentication expressions were restored. Keep the guard, do not
retry the same frozen continuation, and reconcile the next already-scheduled
daily run from a new query snapshot. If it also drifts, design a finite restart
with separate attempt storage before editing the graph. DataCite's
approved web Run attempt was denied maker access to the exact environment; its
automatic reader still has empty-prefix runtime proof only. ClinicalTrials'
failed page has no same-run `dataTimestamp` and its token is stale; do not run a
12,677-study acquisition just to make a fixture. PubMed and DoRA safe full
restarts pass; ARDC fresh-initial-URI restart passes. None proves cross-run
cursor/page resume without provider-version lineage. QGIP remains grants-owned;
ROR release freshness is accepted but its Australian projection remains
incomplete and shared source-health projection retains its existing owner.

Review result: plan compliance Partial; style Pass; no tests added or run in
this documentation reconciliation; coverage Partial; Conductor structure and
scoped diff checks pass. The E01 track remains in progress. Resume provider work
after the next scheduled Crossref run terminates; do not issue another manual
continuation. The local PAC route remains expired on another environment and
the Mac is locked, limiting any later PAC work. No source guard, schedule,
email, or accepted checkpoint was changed by this review.

### Bounded DataCite web-route recheck — 23 October 2026

The user explicitly authorized one bounded diagnostic through the existing web
Run control. Fresh FlowAgent readback confirms the exact DataCite target remains
63 actions, Started, weekly Thursday 05:00 Brisbane, with its original SharePoint
reference. Current run history still ends at CU25 Failed after CU04 Cancelled.
The browser inventory reports the Mac is locked; the prior exact web page also
denied maker access to this environment. No run or native change was made. Before
web Run is attempted, save and read back a temporary stop before `Run_folder` and
provider paging, then verify no provider/checkpoint effect and restore the exact
weekly graph. The earlier CU04 run fetched two pages because the stop was absent;
its partial folder remains unaccepted. Review remains Partial; structure and
scoped diff checks pass, with no test rerun because no executable source changed.


### Crossref bounded restart terminal reconciliation — 23 October 2026

The deployed one-restart policy was exercised on the existing daily flow. Run
`08584089086945869450001321955CU00` terminated Failed with
`CrossrefGenerationRejected`. Its `tropical` attempt summaries report expected
totals 114,999 then 115,000 in attempt 1, and 115,000 then 115,001 in attempt 2;
both attempts are incomplete and marked total drift. The 22 fetched pages in the
five query summaries (`cairns`, `chhhs`, `liz`, and two `tropical` attempts) all
record successful archive save/readback equality. The only failed actions are
`Guard_query_complete` and `Guard_all_queries`; the DOI, manifest and completion
stages were not accepted. Exact flow readback after termination remains Started,
daily 03:30 Brisbane, concurrency one, with its original SharePoint connection
reference. Receipt: `private/ops/2026-10-23-e01-current-state/crossref-bounded-restart-runtime-progress.json`.

Review result: plan compliance Partial; style Pass; focused implementation tests
from the prior turn pass (6/6); current native runtime fails the full-acquisition
acceptance but passes the fail-closed/no-commit outcome. The one-restart policy is
finite and correctly refused a drifting query; it does not solve provider index
churn. Crossref's current guidance documents that reindexing can change cursor
result membership, recommends verifying total count and reducing result-set size
with narrower windows, and describes created-date filters as stable against other
metadata updates ([paging guidance](https://www.crossref.org/documentation/retrieve-metadata/rest-api/tips-for-using-the-crossref-rest-api/),
[2026 cursor behavior](https://community.crossref.org/t/changes-to-cursors-filtering-and-sorting-in-the-rest-api/16246)).
The current full-reconciliation filter is only `until-created-date`, while
`query.affiliation` membership is still mutable during a long traversal. Next
change should partition the same created-date scope into bounded windows and keep
exact total/page/readback checks per window; broadening retry count or weakening
total equality would not meet completeness. This run is not a successful source
generation. No code change or test rerun occurred in this reconciliation.

### Crossref created-date partition implementation review — 23 October 2026

The local candidate partitions only the `tropical` full-reconciliation query
into inclusive monthly created-date windows, with an unbounded lower edge through
2002-12-31 so later backfills remain in scope. Incremental runs and other anchors
retain the existing filter. Window identity is included in page, attempt, and
accepted query summaries; exact total equality and page/summary save-readback
guards remain. The final manifest scope hash is synchronized to the changed scope,
and a guard requires one accepted query summary per expected window. The first
native parse rejection exposed an extra parenthesis; this was corrected, and the
same candidate then passed template parsing far enough to reach connection
resolution. Focused Crossref tests pass 7/7, `py_compile` and scoped
`git diff --check` pass.

The native preview changed five existing actions, with no additions/removals,
trigger changes, or reference changes. FlowAgent preflight reports the existing
SharePoint reference Connected; its 18 `extra-authentication` findings are
identical on preimage and candidate. Both `edit_flow` and `update_flow` rejected
the save with `WorkflowRunActionInputsInvalidProperty`: the embedded reference
could not be found for `Find_last_complete`. Final native readback confirms the
original 56-action Started daily 03:30 flow, trigger, binding, query loop, guard,
scope hash, and manifest remain unchanged; no run was created.

Review result: plan compliance Partial; local style/guard review Pass; local
focused tests Pass; native implementation and runtime acceptance remain open.
The saved candidate is ready for a qualified maker save route that resolves the
existing reference. Do not edit the reference or remove existing authentication
fields to work around the FlowAgent error. The user-authorized DataCite web Run
route was rechecked; the Mac remains locked and no Power Automate tab is present,
so no run occurred. See
`private/ops/2026-10-23-e01-current-state/crossref-created-date-partition-save-blocker.json`.
