# Crossref throughput implementation — 23 October 2026

Authorised by the user's instruction to incorporate and implement the design
recommendations. This supersedes the earlier optional-only status of local
throughput preparation. Existing accepted provider evidence remains accepted.

## Selected lifecycle separation — subsequent user direction, 23 October

### Further action/history reduction — subsequent implementation

`scripts/crossref_plan_projection.py` now replaces the per-month planning loop
with one native Select projection per query using the documented range/date
functions. The entire exact plan is reconstructed from the frozen scope/cutoff
on every batch; no saved plan can silently shorten accepted coverage. The
unbounded prefix, calendar boundaries, bounded final month and incremental
filter semantics are retained. Per-query and total plan guards reject plans
beyond the qualified5000-window bound before provider acquisition.

Reused summaries are checked by their exact prefix ordinal against that plan.
Every key, anchor, index, filter and created-date bound must match, followed by
the unchanged byte readback equality. This removes the Filter array that copied
the whole plan into history for each reused summary. The final consecutive-key
prefix guard remains. Four obsolete mutable date variables and their runtime
initializations are removed; provider pagination state and byte guards remain.

Current local cards/depth: daily227/6, worker233/7, with23 variables each.
For a599-window/27-query full plan, the old planner would schedule4901 action
executions versus138 for the projection, a structural projection of4763 fewer
executions per plan rebuild. This is not a measured native speedup or quota result.
Actual native projection/date serialization, independent runtime and final
coverage remain unqualified. Official semantics:
[Select data operations](https://learn.microsoft.com/en-us/power-automate/data-operations#use-the-select-action),
[expression functions](https://learn.microsoft.com/en-us/azure/logic-apps/expression-functions-reference).

### Measured tuning — subsequent user direction, 23 October

`scripts/measure_crossref_batches.py` measures the independently read historical
prefix. Its private output `crossref-batch-throughput-measurement.json` includes
hashed input receipts, per-window samples and admission simulations:

- 210 completed windows,247 retained pages,51,535 rows:617,354,647 raw bytes.
- Window sizes: median1,465,395 bytes;95th percentile8,217,409;
  largest53,829,252 (`cairns-window-0`). A single admitted window exceeds the
  32MB budget, so lowering the admission threshold cannot bound that unit.
- Provider HTTP calls in those windows total579.9seconds. Their window elapsed
  times total19,385.3seconds, including other actions and pauses. This is not a
  claim that every remaining second was throttling.
- Historical 20-minute admission simulation requires33/24/19 batches for the
  observed prefix at16/24/32MB respectively. Raising the window cap50→100 does
  not reduce those counts. These old-graph results do not predict the new graph.

Implemented tuning in the baseline worker only:

1. Partition both Cairns and Tropical into the existing full-only monthly bounds;
   retain the unbounded pre-2003 prefix and exact cutoff. For the recorded cutoff
   the worker plan has599windows. Raw source coverage/anchors are unchanged.
   Its physical acquisition scope hash changes independently; the daily scope
   hash and bounded index-date acquisition remain unchanged.
2. Keep32MB/50windows/20minutes soft admission budgets. Smaller tested limits
   extend the observed-prefix completion time; a higher window cap adds no
   measured benefit. An admitted window can still exceed a budget.
3. Replace the worker's fixed5second page wait with size-based pacing:
   at least5seconds, otherwise20seconds per retained archive MB, rounded up.
   With an explicitly assumed4× history multiplier this targets60MB per5minutes,
   leaving planning headroom below the documented Low120MB/5minute limit. It
   is not an internal quota reading, actual reserved capacity or a guarantee.

The unfinished generation's cutoff age was8.56hours at the saved11:44UTC
observation. That is not the daily delta catch-up delay. The paired candidates
are not deployed, so real daily lag, new monthly Cairns sizes, new-graph action
and content usage, shared24hour usage and sustained28day feasibility remain
unmeasured. Require those runtime measurements before calling tuning accepted;
do not increase frequency or claim that batching creates daily capacity.

The current paired artifact/receipt supersede their earlier local hashes; prior
native archives and accepted evidence are unchanged. No provider request,
native save, new run, schedule activation or email was used for measurement.

The user selected separation of daily increments from lengthy full
reconciliation. `scripts/prepare_crossref_lanes.py` now prepares two candidates:

- **Existing incremental flow:** retains its stable identity, Started state,
  daily trigger, concurrency one and original connection reference. It always
  uses the bounded index-date delta, requires an accepted checkpoint for the
  exact source scope, and never starts a full baseline merely because it is old.
- **Separate reconciliation worker:** prepared as a creation input in Stopped
  state, with no invented native ID, grant or new connection. It owns a distinct
  full-reconciliation clock, progress and raw archives. It reuses the existing
  connection-reference map and stages the original daily recurrence for later
  supported qualification; no new schedule is enabled now.

Storage ownership is explicit: the primary alone writes `crossref-complete-*`;
the worker writes `crossref-baseline-complete-*`. Progress is respectively
`crossref-progress-incremental-*` and `crossref-progress-baseline-*`, with raw
folders under `crossref-discovery-incremental-*` and
`crossref-discovery-baseline-*`. A worker completion cannot regress or advance
the daily source watermark. Its scheduling fallback reads the daily marker only
to seed the historical baseline clock; active worker progress stays pinned to
its own marker and original cutoff as daily commits advance independently.

Each component has its own pagination state and concurrency one. All variable
declarations stay at workflow root; former dynamic initializations become ordered
SetVariable actions. Partial batch yield affects its own lane only. Native
failure diagnostics and the final lane-result guard retain failures. A paused
baseline no longer owns the daily flow's run handle, although provider/account
capacity can still be shared and can still throttle both components.

- [x] Implement local independent lifecycle candidates and ownership boundaries.
- [x] Structural checks: incremental241cards/depth6 and worker247cards/depth7;
  no duplicate names, missing references, nested initializers, cross-lane variable
  references or malformed expression delimiters. Primary settings/identity and
  original connection references remain equal to the prepared native preimage.
- [ ] After retained-run terminal reconciliation, use supported same-ID update
  for the primary and qualified creation of one canonical Stopped worker. Check
  for an existing component of that exact purpose before creation; resolve an
  uncertain creation result before any retry. Record actual worker ID and exact
  native definitions, connection binding, state and recurrence readbacks.
- [ ] Qualify real independent lifecycle behavior: daily checkpoint advances
  while baseline progress remains pending/frozen; a baseline failure leaves the
  accepted daily checkpoint intact; a baseline completion leaves daily watermark
  unchanged; full/delta reader lineage, raw bytes, coverage and replay reconcile.
- [ ] Qualify shared capacity and scheduling before worker activation. Preserve
  the running original flow and all accepted archives; no new activation now.

Selected private artifact: `crossref-independent-lanes-local-candidate.json`
contains `incremental` and `baseline_worker` objects. The receipt is
`crossref-lifecycle-separation-receipt.json`. The earlier single-flow candidate
remains historical local evidence and must not be deployed as the current design.
Native deployment and real runtime behavior remain unproved.

## Delivery order

- [x] Preserve the existing run and archives; no live edit while it is Running.
- [x] Implement a fingerprint-gated low-copy transform preserving the full raw
  envelope and exact saved-byte equality checks.
- [x] Implement native bounded hedge batches with a frozen cutoff, original
  last-good identity, exact consecutive window-prefix guard and readback of
  every reused summary before provider acquisition.
- [x] Keep progress separate from acceptance: `crossref-progress-*` is always
  `complete=false`, `accepted=false`. Only original full query/DOI guards and
  manifest/completion write/read/verification can advance last-good.
- [x] Retain daily recurrence, concurrency one, flow identity, state, source
  scope and connection references. Keep seven-day overlap and 28-day full
  reconciliation interval. Do not increase polling frequency speculatively.
- [x] Add machine-readable progress: planned/verified/remaining windows, new
  windows, archived-byte upper bound, run identity and observation time.
- [ ] Qualify same-ID native save, expression/schema validation and exact stored
  readback after the retained run reaches a terminal state. Compare all bindings,
  trigger settings and state against a fresh preimage; use supported Dataverse
  route, not the failed FlowAgent save route.
- [ ] Qualify real two-batch continuation, unchanged frozen plan, reused original
  archives, no recollection of completed windows, failure preservation and final
  manifest/checkpoint/replay. Confirm affected readers honour per-query archive
  folders before deployment is accepted.
- [ ] Measure actual content/action consumption and daily catch-up lag. Tune
  admission budgets from observed throughput rather than treating them as quotas.
- [ ] If the DOI phase itself exceeds its budget, extend batching to that phase
  with frozen DOI input identity and exact prefix readback before promotion.
- [x] Implement local lifecycle separation under the subsequent selected design
  above. The older single-flow generation-first limitation is superseded locally;
  native creation/save/readback and runtime acceptance remain unchecked.

## Implemented candidate

`scripts/prepare_crossref_batches.py` composes the low-copy transform with native
progress discovery, strict progress schema, frozen plan generation, summary
readback, exact consecutive-prefix validation and bounded admission of new
windows. Acquisition is flattened to one window per loop item to keep nesting
within platform limits. New cursors start at `*`; no cursor survives a batch.
Every newly admitted window retains its bounded total-drift retries and original
provider/row/DOI/byte guards. The original final DOI phase remains unchanged.

Initial unqualified admission settings: 50 new windows, 32 MB archived-page
upper bound or 20 minutes, whichever is reached first. An admitted window
finishes before yielding. These are soft limits, not a guarantee of runtime,
daily capacity or freedom from throttling. At daily cadence a 313-window full
baseline needs at least 7 batches at the window cap, potentially more at the
byte/time limits. Batching prevents a single giant run; it does not increase
available daily throughput. Do not promise faster baseline completion from it.

The existing source watermark and `baseline_completed_at` semantics stay frozen.
A separate `baseline_accepted_at` is recorded when the final manifest is built;
future periodic full-reconciliation decisions prefer this acceptance clock,
falling back to the historical field for older markers. Otherwise a long baseline
could already be overdue when accepted and immediately start another baseline.
The following delta still starts from the original source watermark minus the
unchanged seven-day overlap, preserving catch-up coverage.

Progress files are created under unique run names and immediately read back with
byte equality. A partial successful batch terminates before DOI acquisition or
accepted checkpoint writes. A full prefix proceeds through the original final
coverage, DOI, manifest and completion checks. If those fail, the saved full
hedge prefix can be reused but acceptance remains unproved. Failed batches do
not replace progress; separately verified extra archives may be reconciled using
the existing terminal-failure recovery route, never automatically relabelled.

Older unbatched archives do not carry the new embedded per-query folder field;
they cannot simply be fed into this progress reader. Existing retained-run
recovery remains the supported route for the in-flight generation.

## Deferred parallelism

Keep both trigger and loop concurrency one. Future workers would need isolated
cursor/counter state, immutable partition ownership and a final coverage barrier.
Parallel workers must first demonstrate that provider and platform capacity can
support the aggregate rate. No worker flow, licence, connection or grant is added.

## Evidence and deployment boundary

Local preparation receipt and candidate are in the existing private E01 receipt
directory, `crossref-batching-implementation-receipt.json` and
`crossref-bounded-batches-local-candidate.json`. Native connector operation
discovery returned `not-logged-in`; no unchanged authentication retry or login
substitution was attempted. Cloned existing native cards remain unqualified for
the new control graph until supported native validation/readback succeeds.

Reference: [Microsoft content throughput limits](https://learn.microsoft.com/en-us/power-automate/limits-and-config#content-throughput-limits),
[workflow expression functions](https://learn.microsoft.com/en-us/azure/logic-apps/expression-functions-reference).

## Local preparation command

After selecting and verifying the repo-local interpreter, invoke the module from
the repository root. Supply the exact fingerprint of the reviewed normal native
definition; do not substitute a candidate fingerprint or overwrite private evidence.

```sh
.venv/bin/python --version
.venv/bin/python -m scripts.prepare_crossref_batches --help
```

Required arguments are `--input`, `--expected-definition-sha256` and `--output`.
The optional `--max-windows`, `--max-archive-bytes` and `--max-minutes` control
admission budgets. The command writes a local candidate only. It cannot deploy,
authenticate, trigger, cancel or change a native schedule.

## Authorised parallel qualification — 24 October 2026

The user explicitly authorised proceeding with a separate bounded qualification
alongside the retained original run. This supersedes the earlier blanket wait
for terminal state **only for this isolated qualification**. Editing the original
flow, deploying the production pair, and original-generation recovery still
require the retained run's genuine terminal reconciliation.

Qualification must use a separate manual-only flow, initially Stopped, the
existing SharePoint reference/connection, distinct qualification archive and
progress paths, concurrency one, and an explicit provider-request cap. Remove
accepted-checkpoint/DOI finalisation actions physically from its definition.
Require exact native definition/binding/state readback before execution. Preserve
original archives, run handle, normal settings and the current last-good selector
before and after. A small batch proves only its measured behaviour; it cannot
establish full coverage, sustained capacity, two-batch recovery or E01 completion.

Execution status: bounded local candidate prepared; native deployment pending. PAC target authentication failed
with AADSTS70043; one existing qualified interactive recovery is pending. No
native qualification flow creation/save/run is claimed. Keep the pending recovery
handle rather than launching another authentication challenge. Exact identifiers,
challenge details and runtime evidence belong in ignored private receipts.

- [x] Record the user's parallel qualification exception and safety boundaries.
- [x] Prepare and inspect a fingerprint-gated bounded qualification definition.
- [ ] Restore qualified native authentication and reconcile existing components.
- [ ] Save one canonical isolated component; read back its exact native definition.
- [ ] Run one bounded batch; verify raw bytes, request count and last-good preservation.
- [ ] Restore Stopped and record measured results and remaining acceptance gates.

Local preparation now exists in the canonical source worktree as
`scripts/prepare_crossref_qualification.py`. The candidate selects Yarrabah,
retains native raw-envelope/readback guards, caps paging at two iterations with
one attempt and no HTTP retries, uses manual triggering and qualification-only
storage prefixes, and removes the DOI/accepted finalisation chain. A cap hit must
fail closed rather than claim query coverage. Native expression validation,
creation and runtime remain pending. Private preparation receipt records the
candidate fingerprint and exact pending authentication handle. The Microsoft
account picker is the current authentication boundary; no additional challenge,
native flow or provider request has been started.

The selected qualification packet now includes an explicit pre-request cap guard
and a storage-writer allowlist. The earlier local packets are superseded and
retained as history. Native authentication remains at the same account picker;
no native deployment or runtime claim follows from local preparation.

### Authentication and source delivery update

The existing exact QH account selection completed the single pending PAC
interactive recovery successfully, without password, MFA, new consent or a new
challenge. Exact `org who` exited zero for the intended environment. This proves
the PAC target session; other service clients remain independently qualified.
The earlier pending-account-picker status is superseded. Read the current private
preparation receipt for handles and exact target evidence.

The qualification helper and maintained preparation documentation are merged in
PR16, with all three PR checks and both post-merge workflows successful. Native
purpose inventory is next; supported creation, exact readback and bounded runtime
remain unproved. No native qualification component or run has been created.

### Supported creation-route qualification

The recovered PAC Power Fx route returned the exact retained workflow, qualifying
that read through the existing client. It does not yet qualify creation: a bounded
schema query returned a compiler error that `primaryentity` is not exposed. The
CLI nevertheless exited zero, so process exit alone must not count as success.
Microsoft's cloud-flow creation contract requires that field with value `none`.
A documented Dataverse create payload is prepared privately; no create request
was sent. Continue with a qualified same-client Web API/SDK or supported maker
creation route, preserving reference bindings; do not omit required fields or
transfer tokens to make this route appear supported.

### Maker placeholder saved; candidate still pending

The authenticated maker route saved one separate manual-only qualification
placeholder with a harmless Compose action, then switched it off. The details
page disables Run and offers Turn on. No execution or provider acquisition was
started. Preserve the actual new handle in the private creation receipt; never
create another placeholder after a missing API result.

The post-save Dataverse exact-name inventory returned no row. Reconcile supported
solution membership and native identity before any PAC definition update. The
existing PAC client can read clientdata for the retained solution workflow;
the separate M365 client's silent renewal failed before target read and must not
be retried unchanged. The selected optimisation candidate has not been saved to
the placeholder, so exact native readback and runtime remain pending.

### Qualification solution membership and update capability

The single existing manual placeholder is now a verified Draft workflow in the
existing unmanaged platform solution. PAC FetchXML captured its complete rollback
clientdata: one harmless Compose action, no connections. Identity, Draft state
and exact preimage checks all passed before the candidate update.

The installed PAC Power Fx update implementation then raised
`System.IO.FileNotFoundException: UpdateAsync`. Its shell exit was zero, so it
must not be counted as a native save. A subsequent complete FetchXML readback
matches the original placeholder exactly and remains Draft. The optimisation
candidate is still local; no provider run occurred. Preserve the saved placeholder
handle and do not recreate it or retry this unsupported update path. See the
private qualification preparation and update-capability reconciliation receipts.

### Native save diagnosis correction

The earlier blanket `UpdateAsync` capability diagnosis is superseded. Fresh
original Dataverse clientdata proved the selected connection IDs are correct but
the prepared Flow API reference representation is unsuitable for a Dataverse
clientdata write. Reusing the original Dataverse reference map reached native
validation and returned a precise InvalidTemplate error: the qualification
failure receipt still referenced removed DOI/completion actions.

The local preparer now emits a qualification-specific failure receipt and rejects
all dangling action-expression references. Provider bounds, archive byte guards,
manual trigger, acceptance prohibition and original connection IDs are retained.
The corrected candidate is under one guarded native save attempt; reconcile its
actual readback before runtime. Earlier candidate files and failed saves remain
historical evidence. The private preparation receipt selects the current artifact.
The fresh full solution export is rollback/source evidence only; no solution
import has been performed and no original collector is included in an import.

### Corrected native definition accepted

The same isolated qualification workflow now has the corrected definition saved.
Fresh full Dataverse clientdata equals the desired definition and the original
native reference map exactly. Draft state, manual-only trigger and concurrency
one are verified. The selected definition fingerprint and complete readback are
recorded in `qualification-native-save-acceptance.json` under private evidence.
No qualification run has started. Before runtime, freshly verify the original
collector/retained handle and current last-good selector; then perform the bounded
qualification and restore Stopped. Native acquisition and throughput remain
unproved. The full solution export was never imported.

### Bounded parallel qualification completed

The isolated manual qualification succeeded. Its acquisition branch took25seconds
and retained one189,482-byte provider page with13rows/13unique DOIs, matching the
provider total. Scope, raw envelope, attempt/window summaries and progress were
independently read and hashed. Progress remains complete=false/accepted=false;
no accepted completion marker was created. The current last-good selector, ID,
ETag, length and SHA256 remain unchanged. The qualifier was switched off; fresh
Dataverse readback is Draft with its entire definition/reference map unchanged.

Keep this qualifier Stopped as evidence, and do not invoke it again automatically.
It is not the permanent baseline worker. The retained original collection remains
separate; later daily incremental/baseline-worker deployment, real two-batch
continuation, full coverage and sustained capacity remain unproved. The small
Yarrabah result is not a large-load speedup or quota claim. Private receipts:
`qualification-runtime-archive-proof.json`, `qualification-lastgood-postrun.json`
and `qualification-runtime-acceptance.json`. PR18 is merged and both post-merge
quality/security workflows passed. Versioned native documentation remains pending.
