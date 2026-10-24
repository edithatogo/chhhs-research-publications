# Guarded same-record flow deployment helper

`scripts/flow_deployment.py` consolidates the grants-qualified stopped-record PAC
clientdata guard and saved-definition comparison. It prepares the update formula;
the owner executes it through the existing qualified PAC Power Fx route. It never
connects, enables, invokes, publishes a draft, deletes a draft, changes credentials
or retries. This is not a replacement for the owning chat or a universal service
adapter. Existing OA-specific Flow RP deployment remains a separate qualified route.

## Owner readback contract

Capture supported native reads into one ignored JSON envelope:

```
{
  "published": {
    "workflowid": "<exact Dataverse workflow GUID>",
    "name": "<exact name>",
    "statecode": 0,
    "componentstate": 0,
    "clientdata": "<complete original JSON text, not reserialized>"
  },
  "draft_checked": true,
  "draft": null,
  "runs_complete": true,
  "active_runs": []
}
```

The owner must actually inspect published and unpublished state (including the
supported RetrieveUnpublished route where applicable), and complete active-run
history. A failed read, truncated listing or published GET alone cannot justify
these attestations. Preserve exact source receipts beside the envelope; this
helper validates supplied evidence, not its authenticity or freshness. Reconcile
ownership and native state immediately before any effect. An unknown or existing
draft stops preparation; inspect ownership/content through the supported route,
never automatically discard/publish it. No host/profile switching after a denial.

Candidate is complete Dataverse clientdata, not a Flow RP properties fragment.
Only the definition may differ: wrapper and all other properties, including the
complete logical references and Invoker/Embedded mode, must match exactly. Do not
silently transform credential modes or mix `host.connection` and
`host.connectionName` representations. Physical bindings and run-only-user rights
also need owner readback; clientdata equality alone cannot establish those rights.
The service validates native M/expressions/actions; local validation is not a
claim that every possible definition shape is supported.

## Prepare, execute once, verify

Use the explicitly qualified repo-local Python. All generated formula/plan/receipt
outputs must be new paths under that code checkout's ignored `private/ops`.
The snapshot and candidate may be read from the owner's separate evidence checkout.
Create the private output directory first.

```
<python> scripts/flow_deployment.py prepare --snapshot <preimage-envelope.json> --candidate <candidate-clientdata.json> --inputs <manual-body.json> --plan private/ops/change/plan.json --output private/ops/change/update.pfx
```

`--inputs` is optional for deployment. If supplied it validates the qualified
single manual Button trigger's required/declared string fields with no coercion.
It hashes the explicit body but never invokes it. Management Run and callback
fallback previously dropped inputs: do not silently substitute either route.
For actual invocation use the existing exact-target qualified input transport,
retain the input hash and verify what the run consumed. Non-string/other trigger
input shapes require separate qualification rather than guessing a conversion.

Inspect the plan/diff and use the existing qualified PAC Power Fx execution route
once. The generated formula guards exact workflow identity, name, stopped state
and full original clientdata; Patch changes clientdata only. This is a pre-read
comparison, **not atomic compare-and-swap**. Retain single-writer ownership and
recovery preimage; a second writer remains a stop condition. Reconcile uncertain
results and stored native state before any retry. A save response is not proof.

Capture a fresh complete postimage envelope through the same owner read routes:

```
<python> scripts/flow_deployment.py verify --snapshot <postimage-envelope.json> --candidate <candidate-clientdata.json> --plan private/ops/change/plan.json --output private/ops/change/comparison.json
```

Comparison requires the exact candidate graph, wrapper, references, stopped state,
name and identity. It performs no annotation stripping. If service annotations
cause differences, retain and diagnose them; do not broadly normalize them away.
The receipt is saved-definition comparison only, never runtime/scheduled acceptance.
Then run only changed behavior under existing authority, preserve/recheck physical
bindings and agreed Off/no-email state, and finish export/documentation handover.

## Qualification boundary

Focused synthetic tests cover refusal paths, explicit inputs, quote escaping and
source/native drift. No new live deployment is performed to qualify consolidation:
reuse grants' terminal `2026-10-24-import-original-retention/acceptance.json` and
same-record guarded PAC/readback receipts. The generated helper itself remains
unexercised on a new native update until the next genuinely required owner change.
Do not rerun accepted retention cases merely to create a helper receipt.
