# Selected flow maturation — 16 October 2026

This refines existing E01-H05 and S02 work. It does not commission a new
framework, environment, recurring run, alert, approval queue or release.

## Demonstrated gaps and changes

| Area | Evidence and disposition | Result / remaining boundary |
| --- | --- | --- |
| Diagnostics | Must fix: the existing summary command discarded an actual combined `run` / paginated `actions` receipt and returned no observations. | `1741fc0` handles those control envelopes without recursing into business inputs/outputs. The actual retained receipt now reports one terminal run and all 79 action statuses. Tool errors cannot become successful run observations; IDs, payloads, signed links and error text stay withheld. Recorded observation remains separate from native acceptance. |
| Schema evolution | Existing contract already preserves unknown fields and requires the known classifier/identity types and source-commit format. Add only missing compatibility checks. | Stable additive schema/unknown nested values remain recoverable; breaking a required type or supplying a future major format rejects the generation without changing persisted last-good output. Eight committed-consumer cases pass; no schema migration or source-field rename was introduced. Native retained QGIP data already preserves all 400 rows/42 fields before the six-row candidate view. |
| Versioning | Must fix: the operator diagnostics helper and its tests were untracked and absent from r10 source companions. | Both are tracked by `1741fc0` and included byte-exact in independently reviewed R11 (source `961668d`); all 136 isolated packaged tests pass. R10 remains immutable. Existing stable IDs, source/native graph bindings, predecessor history and manifests remain authoritative. No second resource registry is needed. |
| Last-good recovery | Native output regeneration from the same QGIP commit and offline ARC derived-output recovery are accepted. They do not prove native flow-definition restoration. | Accepted: exact same-ID Stopped ARC consumer definition canary/restore and native saved readback, with complete original clientdata byte-identical, bindings preserved and probe absent. Main Active archive restoration and six-timestamp ZIP portability remain unproved; selected-consumer recovery does not establish whole-platform restoration. |

The diagnostics helper's 17 focused tests and the committed-consumer's eight
focused tests pass. The current task adds no native effects. Actual receipt
reconciliation is in
`private/ops/2026-10-16-flow-maturation/recorded-diagnostics-proof-private.json`.
The command stays `python3 scripts/powerplatform_tooling.py summarize-flowagent
--receipt <existing-private-receipt>`; it reads recorded evidence only.

## Preserved limits and ownership

The six archive timestamp strings changed by solution export remain a known
portable-import limitation. An exact in-place definition restore, if qualified,
is a separate supported recovery route; it does not repair ZIP serialization or
prove cross-environment portability. Never edit native ZIP entries, normalize
away source-string differences or delete last-good records to make a check pass.

Core owns the active ARC native operation, profile, source, package and checkpoint.
The existing flow chat owns calendar/watchlist/ledger work. This maturation slice
owns only the diagnostics helper/tests and committed-source compatibility tests;
no shared flow builder or tenant object is changed without explicit handoff.
Keep runtime adoption, saved readback, stored outputs and operational acceptance
as separate claims. Selected-consumer native restore and R11 package inclusion are accepted below; current-pointer advancement remains Core-owned.

The sealed r10 bundle already retains the complete historical native archive
clientdata in `solution/evidence/workflows-private.json`. Independent structured
comparison confirms all six exact original timestamp strings remain there while
the inner unmanaged ZIP normalises them. Proof:
`private/ops/2026-10-16-flow-maturation/archive-preimage-fidelity-proof-private.json`.
This establishes backup availability, not current-state equivalence or an actual
restore. Compare fresh native state and preserve a current preimage before using
that historical definition; the native owner's bounded restore remains open.

The bounded local recovery preparer is committed in `e909f4e` and `5618744`:
`scripts/prepare_archive_definition_recovery.py`. Five focused tests pass. It
binds the same workflow ID to its recorded Dataverse environment, requires a
successful Stopped single-entity read and row ETag, and prepares only a clientdata
patch. The first packet adds one inert Compose probe; the restore packet removes
only that exact probe and refuses unrelated definition, connection or timestamp
string drift. Inputs and packets stay in ignored private paths. The native owner
must apply the supported conditional update and verify saved readback; preparation
does not establish that a restore occurred. Include this source and its tests in
the next material S02 bundle alongside the diagnostics helper. Core received the
handoff; its active operation and native-object ownership remain authoritative.

The subsequent explicit native-object handoff was checked against a fresh
single-entity native read (HTTP 200). It contradicted the expected Stopped state:
the exact archive workflow was Active (state 1/status 2). Recovery preparation
and all native mutations were therefore withheld. The exact preimage and ETag
are preserved in `private/ops/2026-10-16-flow-maturation/archive-active-drift-private.json`;
the object was returned to Core for intended-state/in-flight reconciliation.
Retry requires an explicit reconciled Stopped handoff and a new native preflight.
No definition restoration has occurred. Separately, the existing source-release
selector includes all six scoped tracked files with exact HEAD bytes; actual
successor-bundle inclusion is still pending.

## Accepted selected-consumer definition recovery

Core corrected the target assignment and handed over the completed ARC
award-context consumer, leaving the main archive Active and untouched. Fresh
same-client identity and exact native entity reads returned HTTP 200; the
consumer was Stopped and its complete clientdata matched the previously accepted
preimage. Two conditional same-ID updates each passed a fresh state/ETag/hash
check before submission: inert Compose canary (HTTP 204), then original
clientdata restoration (HTTP 204). Each had an independent saved native readback.
The final complete clientdata string is byte-identical to the original, including
the entire definition and connection bindings; name unchanged, probe absent,
final state Stopped (0/1). No activation, flow run, source or output write occurred.

Exact native preimage, packets, effects and readbacks are retained under
`private/ops/2026-10-16-flow-maturation/`; the acceptance receipt is
`arc-definition-recovery-acceptance-private.json`. Core received the terminal
handoff and owns the object again. This closes selected-consumer definition
recovery, separately from accepted output regeneration. It does not prove main
archive restoration, repair the six timestamp strings in portable solution ZIPs,
or establish production release. Successor-bundle inclusion remains open.


## Independent successor inclusion review

The sealed R11 candidate at frozen source `961668d` includes all selected
maturation sources/tests, diagnostics and eight native recovery receipts plus
acceptance. Its SHA-256 is
`5138402cbd95ad9b3a46232b5f1d328081710b1568bd9ce6f16a16ef33d944f8`.
Independent review verifies all 842 entries/841 manifest files, hashes and CRCs;
12 selected committed sources; 18 native flows/five references; restored-consumer
full graph/binding parity; prior 17 workflow bytes; unchanged R10 model/report
and all unselected bytes; exact replacement history; all 34,977 ARC records and
419,724 JSON fields/CSV cells (34,930 declared finite Decimal amount formatting
equivalents); source-manifest bytes; module 6.0 reconstruction at its actual
source binding; and every internal handover link. All 136 isolated packaged
tests pass. An initial reviewer scratch-directory error was corrected before the
successful rerun; no package/source change was needed.

External review evidence:
`private/ops/2026-10-16-flow-maturation/independent-r11-review-private.json` and
`r11-packaged-tests-private.log`. The immutable self-hashed ZIP is not rewritten
to include its later review. Core received the pass recommendation and retains
current-pointer/promotion ownership. The selected diagnostics, compatibility,
native last-good recovery and packaged source-versioning work is complete.
Existing main-archive/portable-import and production boundaries remain unproved.


## Expanded collector maintenance review — 19 October 2026

The selected review inspected the accepted canonical 32-workflow export and the
existing source handbacks, without changing live graphs, schedules or R20b. All
12 collector definitions serialize recurrence executions (`runs: 1`), retain
source-specific completion manifests/readback, and use explicit finite limits
where pagination requires Until loops. The accepted source scope freezer records
policy revision, full policy hash and editable hedge dependency hash; native
acceptance remains a separate receipt. Raw acquisition precedes projection, so
unknown provider fields remain retained. Existing committed-consumer compatibility
checks reject breaking known types/future major formats while preserving the
last good committed generation; this is not universal provider-schema validation.

No additional governance framework, general schema migrator or broad test suite
is warranted by this review. Maintain source-specific count/key/token guards
and immutable completed generations. A source's changed payload shape must be
qualified in its existing builder/consumer before deployment; do not silently
rename fields or treat an old scope snapshot's proof flags as current acceptance.

Existing S02 source/native versions and exact targeted preimages supply rollback
inputs. Accepted ARC consumer definition restoration is deliberately narrower
than main archive restoration or cross-environment solution import; those remain
unproved. Preserve that boundary rather than run disruptive recovery canaries
on working collectors. First natural cadence observations remain source-specific
and are not required to re-prove accepted collection runs.

Review extraction: `private/ops/2026-10-19-flow-maintenance-review/accepted-collector-controls.json`.
It binds the accepted export SHA, exact 12 workflow IDs, trigger controls, Until
limits and completion-action names. This is static accepted-definition evidence,
not a fresh live health or universal restoration certificate. No demonstrated
maintenance defect requiring a runtime change was found. The next selected
implementation is the existing T14 structured monthly report leaf.
