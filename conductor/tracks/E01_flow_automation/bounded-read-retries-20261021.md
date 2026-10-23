# E01 bounded native read retries — 21 October 2026

## Native update — 21 October

The prepared historical packet below is superseded by a fresh same-ID native
save/readback. Both policies are saved; bindings, schedule, Started state and the
existing running acquisition are preserved. A later bounded native run passed both GET paths, complete saved outputs and
exact weekly restoration; no actual transient retry is claimed. See
[runtime qualification](runtime-qualification-20261021.md). Historical
access failures below no longer describe the qualified cached-only CLI route.

## Implemented change

`scripts/patch_clinicaltrials_read_retries.py` prepares an exact-definition-hash
bound patch for the maintained ClinicalTrials collector. Only
`Two_discovery_reads.Discovery_pages.Get_discovery_page` and
`For_each_trial.Get_trial` receive a retry policy: exponential, count 3,
interval/minimum PT10S, maximum PT1M. The original request gets at most three
additional attempts. Native runtime handles retryable HTTP failures; this is
not an instruction to retry permission denials or unsuccessful business guards.

[Microsoft retry-policy documentation](https://learn.microsoft.com/en-us/azure/logic-apps/error-exception-handling)
documents transient timeout/408/429/5xx handling. Verify behaviour in the selected
Power Automate host before declaring native retry execution accepted.

The helper rejects definition drift, a changed provider, non-GET actions,
unexpected custom retry policies, missing graph structure, unrecognised state or
a different collector/manifest. Repeated preparation is a no-op. Tests restore
only the two changed policies and require the entire candidate to equal its
preimage, covering all cursor, write, complete-generation, scope, trigger,
reference and state preservation. Tests do not execute the native retry engine.

## Concrete candidate and deployment boundary

Ignored packet: `private/ops/2026-10-21-e01-retry-continuation/candidate.json` and
`preparation.json`. Source is the retained 19 October weekly started readback,
not current tenant state. The fingerprint is canonical JSON of the complete
`properties.definition`; bindings/state/identity require their separate current
preflight before any native update. Do not submit this historical packet without
fresh readback and material-drift reconciliation. Preserve stable identity,
current trigger/state, exact connection references and an exact-definition
rollback. Read back both saved definition and adopted runtime before one affected
native verification. No run or native mutation has been submitted.

Native history read through FlowAgent returned `not-logged-in`/`AzCliAuthError`.
The user explicitly chose to retain the existing shared recovery owner. No login,
profile selection, token transfer, browser recovery or retry through an unchanged
failed route occurred. Authentication availability and the future monthly
occurrence are distinct gates; neither closes the broader E01 requirements.

## Verification and limits

Six new patch tests and two existing discovery tests pass. The initial patch-test
fixture lacked the existing connector's required identity fields; it was corrected
to use the same qualified fictional reference shape as the original collector
tests. All guards then passed without changing connector rules.

Same-page HTTP retry leaves the cursor unchanged until an actual successful
response passes the existing save/readback guards. Durable continuation across
separate failed runs, delta/watermark handling, current native adoption,
concurrency/failure acceptance and unattended histories remain open in the plan.
No generic retry framework, new collector or provider scope was introduced.
