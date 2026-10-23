# Remaining source pacing compatibility — 22 October 2026

The captured canonical solution exposed five one-second Wait settings in three
existing collectors. Fresh native definitions confirmed the same settings:
PubMed's batch delay, DoRA publications' two collection-scan delays and record
delay, and ARDC's page delay. The latest PubMed and DoRA failed-run repetitions
explicitly reject one second for their Consumption execution context and require
at least five. ARDC's prior runs succeeded; no ARDC failure is claimed.

The three existing generators and same native flows now set these five values to
five seconds. A strict before/after comparison proves every other native field,
source scope, guard, binding, state and trigger is preserved. Ten focused existing
source-generator tests pass. No new collector or source scope was created.

## Performance-profile boundary

Microsoft documents a five-second minimum postpone interval for Low and one second
for other performance profiles: [Power Automate limits](https://learn.microsoft.com/en-us/power-automate/limits-and-config).
Manual flows are listed separately from owner-plan scheduled flows. Therefore the
controlled manual checks below do not establish the original scheduled performance
profile, owner entitlement or a healthy natural source occurrence. Five seconds
is compatible with the documented profiles; it is not a tenant-wide minimum.
ARDC's change is compatibility hardening, not a repair of an observed failure.
No licence, owner or authentication method changed.

## Controlled native check and exact restoration

Each existing flow temporarily ran only its copied Wait actions and identity/
completion Composes through the already-qualified web invoker route. The executed
action set matched that wait-only graph exactly. All five actual native input
artifacts specify five seconds; all runs Succeeded. Measured durations were:

- PubMed: 5.12 seconds.
- DoRA: 5.08, 5.05 and 5.15 seconds.
- ARDC: 5.07 seconds.

These runs performed no provider, storage, registry or model operations and wrote
no accepted generation marker. They are not successful acquisitions. The service
omitted the unused SharePoint reference while each wait-only graph was active.
The initial preservation check stopped on that projection; it was reconciled
explicitly before invocation. Restoration used the retained original normal
binding rather than the empty projected reference. Exact saved readback proves
all original reference fields, schedules, normal graphs and Started states are
restored. No temporary graph or active run remains from this work.

Private evidence in `private/ops/2026-10-21-e01-runtime-qualification/`:

- `remaining-pacing-preflight.json`: exact five-field native delta.
- `pubmed-pacing-failed-repetitions.json` and
  `dora-pacing-failed-repetitions.json`: observed original failures.
- `{pubmed,dora,ardc}-pacing-runtime-acceptance.json`: actual input/duration/action-set checks.
- `{pubmed,dora,ardc}-pacing-final-normal-restore-acceptance.json`: exact restoration.
- `remaining-pacing-runtime-acceptance.json`: aggregate scope and profile limits.

The earlier 34-flow export remains immutable historical evidence. The post-pacing
canonical refresh now covers these three newer normal definitions with exact
native graph/reference comparisons. The earlier ZIP remains historical evidence;
see [current export](current-native-export-20261022.md#post-pacing-refresh). Existing
publisher timestamp and digest annotation/reference recovery boundaries remain.
Later scheduled/profile/source occurrence observations stay in E08-F03. Broader
provider continuation and source-health implementation remain open in E01.
