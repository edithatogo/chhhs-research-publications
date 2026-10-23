# Crossref failed-generation visibility — 22 October 2026

The accepted controlled recovery and later rejected natural generation exposed a
remaining E01 implementation gap: raw pages and native action failures are retained,
but no durable failed-generation summary is written beside the successful marker.
The source collector now prepares a separate immutable run-named failure receipt.

A single failure-observation scope follows unsuccessful or skipped completion
verification. Its receipt records source/scope/window/run/archive identity and
query, DOI, completion-write and readback statuses. It does not contain raw
provider content or credentials. It uses the existing archive binding and does
not change any original action, trigger, accepted marker or connection.

The completion-write status remains explicit. If a marker write succeeded and
readback failed, recovery must reconcile that uncertain marker; the receipt never
claims the write did not happen. Receipt save/readback uses the existing connector
pattern and exact bytes. A final Terminate keeps the generation Failed whether
receipt storage succeeds, fails, times out or is skipped. The entire diagnostic
scope is skipped after successful acquisition, preventing its failure termination
from changing a healthy run into a failed run.

Thirteen focused collector/continuation/failure tests pass. The exact current
native preimage was read with no active run; the prepared candidate adds one
scope while preserving all 55 original actions, recurrence, bindings and Started
state. Native save and runtime qualification remain pending; this is not yet a
native delivery claim. Private preflight and candidate use the
`crossref-failure-projection-` prefix in the existing E01 runtime directory.
Later natural occurrences remain E08. No extra acquisition or recovery was run.


Full local integration passes 2,248 tests with eight skips and zero Conductor
errors. The supported same-ID save was attempted after no-active/no-queued and
exact drift checks. It returned network ETIMEDOUT/EHOSTUNREACH without a native
response. The exact reconciliation GET failed with the same transport error.
The save is unverified; no write was retried and no authentication was changed.
On restored Flow-origin connectivity, read the same target once and compare with
both preserved preimage and candidate before deciding whether any retry is needed.
Native runtime qualification remains open. Existing accepted Crossref recovery,
raw archive, digest and writer evidence is unaffected by this diagnostic increment.


## Native adoption and remaining runtime gate

Connectivity recovered and the exact native read proved the first timed-out save
left the collector unchanged. After fresh no-active/no-queued and drift checks,
one guarded retry saved the normal 56-action graph. Exact native readback preserves
all 55 original actions, bindings, daily recurrence and Started state. Receipt:
`crossref-failure-projection-save-acceptance.json` and
`crossref-failure-projection-recovered-save-saved.json`.

The bounded runtime candidate contains no provider requests, source-record writes
or successful-marker writes. Its separately named qualification receipt cannot be
mistaken for a normal failed generation. A first temporary save timed out; exact
readback confirmed the normal scheduled graph remained intact. A subsequent save
was rejected HTTP 400. Local inspection found that placeholder stages referenced
by the diagnostic scope were parallel rather than ancestors of final verification;
the corrected candidate serializes them. This is a concrete local correction,
not a proven explanation of the server rejection, whose body was unavailable.
Local FlowAgent validation passes. The corrected candidate's fresh preflight GET
then failed with ETIMEDOUT/EHOSTUNREACH before a mutation was attempted.

No qualification run was submitted. Resume with a fresh same-target read after
connectivity recovers, then qualify the corrected bounded graph and restore the
normal 56-action schedule/bindings/state. Actual stored receipt bytes and terminal
Failed disposition remain unproved; native saved adoption alone does not close
the failed-generation visibility task.


## Corrected native save, execution boundary and exact restoration

A fresh native read confirmed the normal 56-action graph. With no active or queued
run, the corrected bounded manual graph saved successfully and matched exact
native readback. This establishes native acceptance of its corrected dependency
ancestry; it does not prove runtime.

The one resubmit attempt timed out. Complete run history, queued-run and manual
trigger-history reads independently showed no new run. One reconciled resubmit
then returned HTTP 403; that denied operation was not repeated. The installed
FlowAgent manual-run operation returned `not-logged-in` / `AzCliAuthError` for its
separate Azure session. No Azure login, new client, consent or grant was attempted.
Subsequent history still contains no qualification run.

The temporary manual graph was restored to the exact normal 56-action daily
collector, with original bindings and Started state independently read back.
Intermittent socket timeouts delayed restoration. The installed Node transport's
family-attempt timeout is 500ms; a per-command change to 2000ms allowed the same
qualified CLI route to complete reads, save and restoration. Authentication,
resource and destination were unchanged; this is not proof of the timeout's
underlying cause and no global configuration was changed.

`crossref-failure-projection-runtime-disposition.json` binds the saved graph,
403 receipt, history and exact restoration evidence. Runtime remains open until
an existing permitted manual execution route or eligible self-created run history
is qualified. Do not retry the unchanged denial or treat another client's missing
session as permission to introduce an unqualified authentication route. The normal
working collector is preserved; later natural observations remain E08.


## Accepted failure-receipt runtime and normal restoration

The existing recovery guide already qualifies the web Run route when invoker
context is required. That route was reused only for this diagnostic graph, which
has no provider requests, source expansion or successful-marker writes. No refused
CLI resubmit was replayed. The existing service account/session required no login
or connection change. Ordinary CLI expiry was separately recovered through the
same previously qualified client and one silent refresh; its exact target read
passed before any dependent save.

The saved corrected graph was invoked once through the real web Run control.
The intended read-only rejection failed its guard, while query/DOI/marker stages
were Skipped. Receipt save, read, exact-byte verification and the final Terminate
all Succeeded. The run is terminal Failed as required. The enclosing diagnostic
scope reports Cancelled because Terminate ended the run; this is not a receipt
storage failure. This runtime exercises the same diagnostic scope as the normal
collector, differing only in its qualification format/name/label.

Independent SharePoint HTTP 200 readback proves all 732 stored bytes equal the
runtime receipt and the connector readback. Source/scope/window/run/archive
identity and the actual Skipped stages are retained. The existing accepted
453,919-byte completion marker retains its exact SHA-256 after qualification.
The same collector was restored to its normal 56-action daily graph, unchanged
bindings and Started state, with exact native readback and no active run.

Authoritative private receipt: `crossref-failure-web-runtime-acceptance.json`.
Supporting files: `crossref-failure-web-run-terminal.json`,
`crossref-failure-web-run-actions-raw.json`,
`crossref-failure-web-independent-stored-bytes.json`, and
`crossref-failure-web-normal-restore-saved.json`. This closes the selected Crossref
failed-generation projection's native runtime/restoration gate. The earlier
permission/transport checkpoint is superseded; the refused routes remain refused.
Later natural occurrences belong to E08. Other providers' continuation and broader
source freshness/coverage work are not declared complete by this result.
