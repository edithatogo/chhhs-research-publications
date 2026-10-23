# Independent monitoring runtime — 18 October 2026

The user selected qualification of independent missed/failed execution detection.
The existing export's accepted failure receipt branch remains preserved; it
cannot observe failure to start. This increment changes no flow or connection.

Current native Management catalogue still has no run-history list operation.
Current environment connections include Dataverse and SharePoint, but no
HTTP-with-Entra connection. Discovery does not authorise a new connection,
credential transfer, scheduler or notification.

Dataverse FlowRun is a documented native reader candidate for positive failure
observations, but cannot alone establish a missed execution. Microsoft states
its ingestion is nontransactional and may lose records without FlowEvent entries.
Thus even complete pagination and no reported ingestion errors cannot establish
lossless absence. Retain UNKNOWN when complete qualified runtime history is
unavailable; do not turn an empty table or absent health file into MISSED.

The selected 09:00/day1 Brisbane occurrence and noon completion deadline remain
unchanged. Exact occurrence, manual-test discrimination, observation coverage,
correlated output and durable replay-safe receipt gates remain required. Existing
operator CLI history reads/local evaluator are not a deployed Microsoft runtime.

The dataset lane retains native-runtime prerequisite ownership from the prior
handoff; a bounded request for any current qualification evidence has been sent.
No duplicate native writer or acknowledgement polling was started. Next consume
that handoff or qualify an existing supported lossless native history route.
Receipt: private/ops/2026-10-18-independent-monitor/runtime-route-qualification.json.

Reference: https://learn.microsoft.com/en-us/power-automate/dataverse/cloud-flow-run-metadata

## Additional existing connector candidate

Current native shared_logicflows catalogue exposes WorkflowRuns_List,
WorkflowRuns_Get, WorkflowRunActions_List/Get and trigger-history operations.
Exact metadata requires api-version for run listing, with optional $top/$filter;
trigger-history listing additionally requires triggerName. This corrects any
inference that absence in Management means absence in every native connector.

No execution qualification follows from catalogue discovery. The exact monthly
export currently binds only SharePoint; its Dataverse and observed runtime IDs
have no matching Logic flows connection in the current environment inventory.
The working FlowAgent history reader uses Power Platform/Flow RP endpoints,
so it does not qualify these connector runtime actions. Native binding,
pagination, retention and scheduled-occurrence evidence remain missing. No
connection, monitor flow, source run, schedule or notification was created.

## User-assigned implementation and native preflight

The user assigned independent monitor implementation to the flow lane, alongside
public usability and CI. Dataset ownership alone is no longer a blocker. Preserve
its documentation work and the core-owned monthly export's read-only boundary.

A read-only manual-trigger reader candidate passed native structural validation
with zero errors/warnings. Native preflight returned overall block: the exact
monthly-export Logic flows connection is missing in this environment. No monitor
was created or run. The same check warns that unresolved references prevent
publishing solution-wrapped flows. Exact candidate and result are retained in
private/ops/2026-10-18-independent-monitor/reader-preflight-private.json.
The API-version value in this validation-only candidate is not runtime-qualified;
no service behaviour or deployable whole-monitor claim follows from validation.

## Exact binding readback

Read-only test_connection succeeds for a comparison existing Logic flows
connection. Exact monthly Dataverse ID returns404 ConnectionNotFound. Exact
recorded runtime ID returns403 ConnectionAuthorizationFailed. These direct
service results supersede inventory-only absence assumptions: the latter
operation is denied, and does not by itself prove the connection exists.
No new connection, profile switch, token transfer or unchanged authentication
retry was attempted. Resume requires the supported target binding to become
accessible under existing authority or the exact denial to be resolved by its
owner/admin; no wider grant is inferred from this task.
