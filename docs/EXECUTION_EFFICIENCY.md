# Bounded implementation and lane resume

Use this alongside the existing Conductor plan and harness. Each chat owns one
compact ignored checkpoint at `private/ops/execution-lanes/<lane>.json`.
Read it with `.venv/bin/python scripts/lane_resume.py --lane <lane>` after
compaction. Do not fall back to another lane's shared Active resume. Missing or
stale checkpoints require reconciling the retained operation, not new discovery.
The helper only reads owner reports; it never certifies native acceptance or
executes checkpoint prose. Keep tenant IDs and raw receipts private. Checkpoints
are local to their worktree; use an explicit worktree path rather than copying or
sharing a mutable checkpoint across lanes. No new approval or reporting layer.

Checkpoint schema (version 1): nonempty text fields `owner`, `updated_at` (UTC
ISO timestamp), `owned_scope`, `outcome`, `finish_line`, `last_accepted`,
`current_operation` (retained handle or none), `next_action`, `blocker` (or none).
`failures` is a list of objects containing `operation`, `observed`,
`changed_hypothesis`, `retry_condition`. `completion` is a list containing `name`,
`deployed`, `runtime_proven`, `enabled`, `scheduled_proven`, `evidence`.
Use qualified/pending/unknown/not-applicable descriptions with receipt pointers;
activation is not scheduled success. Include only current relevant failures and
selected outcomes; preserve full history in existing receipts. Update on meaningful
outcomes or changed blockers, not every tool call. Never edit another owner's file.

## Finish the tranche

Agree one concrete outcome and finish line from the user's current scope. Complete
it, record evidence and limits, then advance only to the next agreed priority.
Additional enrichment is not progress toward unattended operation unless it is a
required dependency. While Crossref is running, preserve its handle and monitor;
its owner may do disjoint authorised work without restarting that operation.

## Reuse verification

Use existing harness snapshot/drift capabilities where present. A reusable receipt
records source/package/native-definition SHA256, interpreter/dependency identity,
exact test selectors, outcome and native receipt pointers. Reuse only if relevant
inputs, bindings and capabilities remain unchanged. A local hash cannot establish
current tenant parity. Run affected selectors during edits and required full
integration/security gates once at coherent milestones. Keep first failures;
never retry a native mutation through a test runner.

## Native deployment adapter and connector knowledge

Consolidate existing qualified helpers after in-flight operations reach a terminal
point; do not introduce a second live writer or speculative universal API wrapper.
The owning lane's adapter must: capture the preimage and draft/published state;
validate the target API's supported schema and explicit input transport; preserve
logical references and Invoker/Embedded credential mode; apply one smallest diff;
reconcile uncertain outcomes before retry; compare the complete saved graph,
bindings and state; exercise only the changed runtime behavior; restore the agreed
state. A successful save response alone does not pass.

Record reusable connector findings beside that helper: exact operation/version,
observed representation, qualified alternative, receipt and invalidation condition.
Current known findings to verify against owner receipts: management invocation may
omit manual inputs; CreateAttachment may reformat JSON; existing unpublished drafts
can block published updates; changing Invoker to Embedded changes credential
semantics. Do not repeat the unchanged failed route or adopt an alternative from
these descriptions without target qualification. Before a retry record the exact
failure, changed hypothesis, expected discriminating result and retry condition.

## Evaluate effectiveness

Compare accepted outcomes against the checkpoint finish line, not tool calls or
artifact counts. Watch unchanged retries, repeated broad orientation, full-suite
runs without relevant changes, ownership collisions, and expansion after closure.
A newly diagnosed defect with a discriminating check is progress, not a loop.
Recommend further changes only from concrete repeated friction. Observe existing
chats without triggering them; notify owners only for a completed improvement,
changed blocker or actionable conflict. Stay quiet on unchanged monitoring ticks.

## Separate code and evidence worktrees

When qualified helper code and owner evidence live in separate checkouts, use
`<qualified-python> <code-checkout>/scripts/lane_resume.py --lane e01
--checkpoint-root <owner-evidence-checkout>` (one command). This reads only the
explicit owner's checkpoint. It neither copies evidence nor changes the default
root. Do not silently search other worktrees for a missing checkpoint.

Keep recurring prompts short: identify the owner checkpoint and exact terminal
checklist, preserve retained operation and cadence, and read detailed history only
when the selected next action requires it. Do not append every successful receipt
to the recurring prompt. Preserve the previous prompt privately before shortening
it; retained safety/authority/terminal gates remain controlling. Notify a waiting
lane once on a genuine terminal result, not repeatedly while unchanged.

The consolidated [same-record deployment helper](FLOW_DEPLOYMENT_HELPER.md)
prepares guarded PAC updates and verifies saved clientdata. Use it at the next
required owner change; do not redeploy accepted graphs solely to test adoption.
