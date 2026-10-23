# Source flow native setup — 24 October 2026

Read-only PAC definition/state inventory. No flow was invoked, activated, changed
or recreated. Private exact definitions, native workflow identities and source
fingerprints are under `private/ops/2026-10-23-e01-current-state/` in
`source-collector-native-setup-20261024.json` and its referenced PAC capture.

## Saved source schedules

Times below use Brisbane; all listed recurrence triggers have concurrency one.

| Collector | Native state | Saved cadence |
| --- | --- | --- |
| PubMed | Activated | Daily 01:30 |
| DoRA activity | Activated | Daily 02:30 |
| Crossref | Activated | Daily 03:30 |
| DoRA publications | Activated | Daily 04:30 |
| ARDC | Activated | Monday 04:00 |
| NHMRC | Activated | Monday 05:00 |
| MRFF | Activated | Monday 06:00 |
| ARC | Activated | Monday 07:00 |
| QGIP | Activated | Tuesday 05:00 |
| ClinicalTrials.gov | Draft/Stopped | Wednesday 04:00 saved; not enabled |
| DataCite | Activated | Thursday 05:00 |
| ROR | Activated | Monthly; explicit day/time absent from recurrence object |

Source archive commit is Activated with a manual Request trigger; it is not a
scheduled collector. Archived source assertions refresh and test archive staging
are Draft/manual and remain unchanged.

## What this proves

Existing native collection graphs, recurrence definitions and state are present.
Recreating these flows or rerunning bootstrap ingestion is unnecessary for setup.
This inventory does not prove recent scheduled success, current checkpoint
freshness, end-to-end consumer admission or operational licensing. ROR's exact
effective next trigger requires service scheduling evidence before claiming a
specific monthly execution time.

OpenAlex is not present in this selected Data spaces workflow-name inventory.
Do not infer absence across the tenant or conflate local/native bootstrap capture
with a saved recurring Power Automate collector. Resolve its existing owned route
before creating any replacement.

Crossref final results and independent-lane deployment remain pending under its
retained-run preservation rule. Conditional ANZCTR/WHO/GrantConnect access remains
separate. Use the E01 accelerated-delivery leaf to select only actual missing work.
