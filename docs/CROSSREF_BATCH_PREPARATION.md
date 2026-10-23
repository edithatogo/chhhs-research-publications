# Crossref candidate preparation

These modules prepare cloud-flow definitions locally. They do not authenticate,
save, enable, cancel, resubmit or run a native flow. The deployed runtime remains
Power Automate. Keep native definitions, bindings and provider evidence private.

Run from the repository root with the explicitly selected repo-local Python
3.15.1 interpreter. Verify its actual version before preparation:

```sh
.venv/bin/python -c 'import sys; assert sys.version_info[:3] == (3, 15, 1); print(sys.version)'
.venv/bin/python -m scripts.prepare_crossref_lanes \
  --input /absolute/private/normal-native-readback.json \
  --expected-definition-sha256 REVIEWED_CANONICAL_DEFINITION_HASH \
  --output /absolute/private/paired-candidate.json
```

The fingerprint covers the complete definition using sorted-key compact JSON,
UTF-8 and unescaped Unicode. The input must be the normal collector with its
existing monthly created-date partition graph and sequential single-variable
initializers. It must not be a partial recovery graph or an already batched graph.
Preparation fails on drift or an unfamiliar archive contract.

## Selected changes

- Inline the full raw page envelope at save and equality verification, removing
  its extra Compose copy. Retain headers, request URL, status and provider body.
- Freeze a generation cutoff and resume only an accepted consecutive window
  prefix. Progress markers remain separate from accepted completion markers.
- Bound admission to 50 windows, 32 MB of archived bytes or 20 minutes. Finish an
  admitted window; these are soft budgets and do not guarantee a platform quota.
- Build the frozen window plan through per-query projections and ordinal checks.
- Keep the existing daily flow identity and trigger for incremental collection.
  Prepare a separate **Stopped** full reconciliation worker using the existing
  connection-reference map, with monthly partitions for the two large queries.
  Separate archive, progress and completion namespaces prevent the worker from
  advancing the daily watermark. Failure handling remains independent per lane.
- Pace worker pages using archived size. Historical volume informs this policy;
  actual platform metering and catch-up delay still require native measurement.

`scripts.measure_crossref_batches` consumes existing private receipts and saved
page proofs for historical tuning. It performs no provider or native requests.
Its timing and simulations do not establish the new candidate's throughput.

## Native acceptance remains required

Preserve an existing Running generation and its handle until it is terminal.
Reconcile the actual terminal result, complete partition content and coverage,
manifest, checkpoint and last-good before choosing continuation. Historical
prefix evidence needs extension for later completed partitions. Never reuse an
incomplete window's provider cursor or mix different frozen window plans.

At deployment, obtain a fresh exact preimage and rollback, refuse material drift,
use the supported same-identity update route and read back the complete saved
definition and preserved settings. The new worker needs canonical-purpose and
connection checks before creation. Local output and matching fingerprints prove
preparation only. Native expression/serialization parity, real batch continuation,
final coverage, manifest/checkpoint, replay and last-good preservation remain
separate runtime requirements. DOI batching remains conditional on measured
capacity in that phase.

## Existing monthly-generation recovery

`scripts.prepare_crossref_query_continuation` retains the original generation's
monthly policy, frozen cutoff, query order and all independently verified complete
window pointers. The unfinished window restarts at cursor `*`. It does not map
the old generation into a different worker partition policy. A later normal
generation can use the independently prepared worker policy after reconciliation.

The preparer requires a Stopped, unmanaged, manual-only preimage, an exact
definition fingerprint, matching scope and a receipt with
`status=VERIFIED_FAILED_HEDGE_RECOVERY_INPUTS`,
`source_terminal_status=Failed` or `TimedOut`, and
`native_terminal_gate_satisfied=true`. A staged Running-prefix receipt is evidence
for future reconciliation, not an accepted preparation input. Do not relabel a
receipt to pass these gates; populate it from a fresh native terminal readback.
The monthly route also requires a consecutive complete-window prefix, reconciled
page totals and terminal pages, accepted attempt identities, and the native
sequential single-variable initialization layout. The original scope and window
count remain intact; the added acquisition gate skips only the verified prefix.

After terminal reconciliation and supported preimage preparation:

```sh
.venv/bin/python -m scripts.prepare_crossref_query_continuation \
  --input /absolute/private/stopped-manual-native-preimage.json \
  --receipt /absolute/private/verified-terminal-recovery-inputs.json \
  --expected-definition-sha256 REVIEWED_PREIMAGE_DEFINITION_HASH \
  --output /absolute/private/new-recovery-candidate.json
```

The command refuses to overwrite an existing candidate. It performs no native
save, trigger or authentication. A successful local preparation still requires
fresh file/checkpoint drift checks, exact supported native save/readback, actual
continuation verification and restoration of the normal graph/settings. Do not
combine a frozen recovery generation with a changed monthly plan or infer that
local preparation satisfies any of those native gates.

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

Use `scripts.prepare_crossref_qualification` for the separate local-only
qualification packet. It fingerprint-checks the paired input, selects one query,
limits acquisition to two requests without retries, retains archive byte guards,
and removes accepted finalisation. Native creation/readback/runtime are separate
pending gates. The private E01 receipt records the exact authentication boundary.

The selected qualification packet now includes an explicit pre-request cap guard
and a storage-writer allowlist. The earlier local packets are superseded and
retained as history. Native authentication remains at the same account picker;
no native deployment or runtime claim follows from local preparation.

Native qualification refinement: removing finalisation must also replace failure
diagnostics that name those removed actions. The preparer now rejects unresolved
action-expression references. A Dataverse clientdata transport must preserve the
existing native `runtimeSource`/`connection`/`api` reference representation; the
Flow API reference presentation is not interchangeable with it. Compare the exact
logical reference and connection IDs and native definition on readback. Shell
exit zero from PAC Power Fx does not establish that a Patch succeeded.
