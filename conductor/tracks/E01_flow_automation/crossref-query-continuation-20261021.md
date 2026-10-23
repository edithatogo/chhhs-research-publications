# E01 Crossref query continuation — 21 October 2026

## Current native qualification — 21 October

The helper now also supports a failed incremental hedge with a verified prior
complete checkpoint. It pins source/scope, old watermark, baseline and overlap;
changed runtime checkpoint identity fails before query reuse. Native recovery
from a genuine three-query prefix passed that guard and completed the other
24 queries, with all-query completeness accepted; its unchanged 1,283-DOI
stage remains active. Exact normal daily definition/state are restored;
source-total guards remain intact. See [runtime evidence](runtime-qualification-20261021.md).
The original baseline-only preparation below is retained as implementation history.

## Existing accepted capability

Crossref already has saved complete-query/DOI-prefix recovery and incremental
index-date catch-up. Retained receipts independently inspected:
`private/ops/2026-10-18-crossref-broad-acquisition/native-recovery-lineage-acceptance.json`,
`native-catchup-acceptance.json` and `native-catchup-checkpoint.json` in that folder.
The cutoff, index-date window and complete manifest agree; the recovery lineage
retains explicit old archive pointers. This evidence is historical and bounded,
not a fresh current trigger/run observation or acceptance for every provider.

## New implementation

`scripts/prepare_crossref_query_continuation.py` prepares recovery when an initial
full-baseline hedge fails after a consecutive prefix of completed queries. The
existing recovery helper requires the entire hedge to have completed. The new
helper reuses only verified complete queries and restarts the unfinished queries
at cursor `*` in the original immutable created-date window.

Crossref's [official API documentation](https://api.crossref.org/swagger-ui/index.html)
states that cursors expire after five minutes without use. Persisting an old
cursor across an arbitrarily delayed run would not provide durable continuation.
The supported unit of retained progress here is a complete verified query; pages
of an interrupted query remain diagnostic evidence and are reacquired. This
limitation is explicit rather than an unsupported promise of arbitrary page resume.

Preparation requires the complete graph fingerprint, a stopped manual-only
unmanaged normal collector, terminal failed-run evidence, exact scope/run/archive
identity, preserved UTC cutoff/window and a contiguous prefix of complete query
and page readbacks. Query anchors/order, counts and terminal-page conditions must
agree. False booleans used as row counts, changed scope, missing readback,
non-terminal pages, changed gates and already-started DOI collection are refused.

The native query gate skips the retained prefix while the existing query reset,
page save/readback, failure, all-query, DOI, manifest and completion-marker gates
remain intact. Reused summaries point to their old immutable archive folder;
new acquisition uses the existing fresh run folder. The existing scheduling
builder rejects the resulting recovery manifest. Normal recurring acquisition
must be restored under its exact owning operation after recovery, before any
schedule is enabled; this helper cannot make that switch or activate a flow.

## Verification and native boundary

Six new continuation tests pass. Three existing Crossref discovery/recovery tests
and three DataCite discovery tests pass unchanged. The tests verify actual graph
preservation and refusal cases; they do not execute Power Automate or prove new
native continuation. The accepted older receipts are reused without provider
queries, uploads or schedule changes.

Native adoption and a representative interrupted-hedge recovery remain open.
First obtain a fresh exact graph/history through a working qualified route and
resolve pending runs; do not manufacture a failed-run receipt from a complete
archive or reuse an old receipt as current authorization. The user retained
shared authentication recovery with its existing owner. No login, token/profile
change, native save, provider acquisition, send or report/model mutation occurred.

## Remaining full E01 scope

The previous accepted watermark/recovery evidence does not close partial-hedge
native qualification, bounded-retry deployment, other provider continuation gaps,
current publication concurrency/failure acceptance, digest runtime adoption or
natural unattended histories. By the later user-directed scope split, natural
occurrences and elapsed operating windows belong to E08 operational follow-up;
E01 remains open for technical implementation/native qualification only.
