# Remaining Conductor track audit

Audit date: 2026-09-21. This is a source and acceptance ledger, not a claim
that the tenant is complete. A track is archivable only when its plan tasks
and its required native acceptance evidence are both complete.

| Track | Current evidence | Remaining gate | Archive decision |
|---|---|---|---|
| S02 | Clean canonical source package reproducibly verified; SharePoint item versioning observed | Isolated native report version/batch display and readback | Keep active |
| G02 | Official NHMRC/MRFF calendars, ARC awards API, Queensland metadata API, conservative source catalogue, and fail-closed row-level evidence/eligibility gate verified | Permitted opportunity feed/API or explicit human-reviewed rows with source links and eligibility | Keep active |
| G03 | Isolated Grants Registry schema and authenticated synthetic create/update/duplicate/concurrency evidence; existing flow updated in place; fresh native export contains `SourceRowURL`, choice mappings and current server timestamp; flow remains Off with Flow Checker 0 errors and 1 inactive-flow warning | Explicit cleanup/readback and user-scoped operational acceptance; shared organisation-wide target and unattended operation are future extensions | Keep active |
| G04 | RSS/Atom/API-shaped adapters and fresh 13/179 NHMRC/MRFF candidate extraction | Controlled source-to-list cycle and reconciliation | Keep active |
| G05 | University catalogue and access/lead-time evidence | Permitted institutional export/feed or reviewed intake | Keep active |
| G06 | Typed relationship contract and local safeguards; isolated personal DEV `Grant Relationships` list with all eight native fields; `RelationshipKey` required/unique/indexed; synthetic evidence-bearing create/read/update/read/delete round-trip; post-cleanup relationship `ItemCount=0`; publication registry `ItemCount=1468` read back with no publication mutation | Full before/after publication-key reconciliation and shared binding | Keep active |
| G07 | Fail-closed operational evaluator, exact-key reconciliation, selected-field readback reconciliation and isolated create/update replay | Native monitoring, operational reconciliation, delivery and scheduling | Keep active |
| G08 | Local calendar, institutional-date and current-user subscription contracts; exactly one native personal `My Funding Watchlist` and one `Funding Calendar` list with REST field readback and zero items | Native report pages, current-user flow/page binding, reminder/change ledger, manual calendar readback and delivery | Keep active |
| T11 | Local PubMed/DORA preservation and schema/key reconciliation | Native retained-history flow, refresh and list/readback | Keep active |
| T14 | Complete local exports, monthly generator and failure contracts | Manual native cycle, consecutive-cycle replay and delivery decision | Keep active |
| T15 | Local handover/package and current four-page report audit | Native release/readback; Clinical Analytics model bindings are broken | Keep active |
| E01 | Corrected publication query and successful DEV flow readback; standalone tracked-flow validator and CI gate pass | Manual replay/update, duplicate/failure safety and user-scoped reconciliation | Keep active |
| E04 | Local Fluent/grid/contrast and PBIR-to-TMDL field-binding tests pass; native Clinical Analytics has nine field errors; isolated model view bootstraps the original model and fails in the modeling iframe | Restore a correctly bound isolated authoring route, then repair/read back model/report bindings | Keep active |
| E07 | Local platform acceptance contract and isolated evidence | End-to-end tenant acceptance and release evidence | Keep active |

## Canonical-source invariant

The private GitHub repository has one remote branch, `main`. The synchronized
clean checkout used for this audit is the canonical local reference. The
original authoring checkout remains dirty by design and is not treated as a
second remote version. Conditional T16/T17 fallbacks remain gated and are not
created or activated.

## Review conclusion

Conductor review was applied to the active changes, stale completion claims
were corrected, and review SHAs were recorded in the relevant plans. No track
is archived in this audit because each active track has at least one explicit
native, source-access or operational gate still open.

## Native access recheck — 2026-09-21

Read-only PAC/Azure discovery was attempted after the browser debugger route
remained unavailable. PAC is authenticated to an unrelated Power Platform
environment and its environment query returns an Entra account-deleted
directory error; Azure is authenticated to a different tenant. No credentials
were changed and no tenant mutation was attempted. This confirms the remaining
native gates are externally blocked by tenant/account scope, while local source
and contract work remains synchronised and CI-green.

## Native access recheck — resumed audit — 2026-09-21

The read-only `playwright-cli` check found that neither the `chrome` nor
`login` browser session is open. PAC still reports the unrelated NSW profile
(`Dylan.Mordaunt@health.nsw.gov.au`), and Azure still reports the unrelated
Flinders tenant/account (`mord0015@flinders.edu.au`). No login, tenant switch,
deployment, or write was attempted. The native gates listed above therefore
remain open; this is evidence of unchanged external state, not a completion
receipt.

## Native grants-flow continuation — 2026-09-21

The authenticated current-user route was restored through `playwright-cli`.
The existing flow `CHHHS Research Grants - Reviewed Import Upsert`
(`acf866e4-e4a2-4113-bce4-d2dd9e2f22d6`) was retained as the sole grants flow;
the legacy package importer was tested but offered only `Create as new`, so it
was cancelled and no duplicate was created. The personal DEV SharePoint list
`Grants Registry` received the missing `SourceRowURL` Hyperlink column. The
existing flow editor then persisted and reloaded SourceRowURL and choice
mappings for Create and Update; Create defaults ReviewStatus to `Needs Review`
and Update leaves ReviewStatus untouched. A fresh package export recorded
server modification time `2026-09-21T03:12:53.7725597Z` and contains the
SourceRowURL and choice mappings. Flow Checker reads 0 errors and 1 warning,
where the warning is only that the flow is Off. The flow remains Off and no
new run, schedule, sharing or notification was activated. G03 remains active
until the explicit synthetic-row cleanup/readback and current-user operational
acceptance gates are closed.

## Native G08 list bootstrap — 2026-09-21

Inventory of the authenticated personal DEV site found no funding watchlist or
calendar list. Exactly one `My Funding Watchlist` list and exactly one `Funding
Calendar` list were therefore created. Authenticated SharePoint REST readback
confirmed the watchlist identity and fields (`OpportunityKey` required and
unique, `Scope`, `TargetKey`, `Active` default false) and the calendar identity
and fields (`DeadlineKey` required and unique, `OpportunityKey`,
`CalculatedDate`, `SourceURL`, `Cancelled` default false, `PolicyKey`,
`ReviewStatus` default `Needs Review`). Both lists read `ItemCount=0`. No
subscription, calendar event, flow, notification, sharing change or report
page was activated; G08 remains active for binding and delivery acceptance.

## Native relationship continuation — 2026-09-21

The personal DEV `Grant Relationships` list was read back with all eight
canonical columns. The `RelationshipKey` column editor confirmed required
information and enforced unique values. A synthetic candidate relationship
with an HTTPS evidence URL was created and read back, updated (title and
evidence URL), read back again, and then deleted to the recycle bin. The list
now reads `ItemCount=0`. A read-only SharePoint API check of the personal
`Publication Registry` read `ItemCount=1468`; no publication item was changed
by the relationship test. G06 remains active until a true before/after
publication-key reconciliation is captured; no shared binding was made.

## Local hardening continuation — 2026-09-21

Since the resumed access recheck, three local review fixes were completed and
synced to the sole remote `main` branch:

- G02 `ec5322c`: source authority/API URLs with surrounding whitespace now
  fail closed before intake validation.
- G08 `a573598`: calendar CR/LF display-field escaping is explicit and tested.
- G07 `1ac3d52`: operational source and opportunity identities with surrounding
  whitespace now fail closed rather than being accepted after comparison-time
  trimming.

The canonical checkout is clean and remote-aligned at `0e67c89`. The full
local suite passes 426 tests with 8 skips; the harness, 438 project checks,
Conductor, web-first, Power Platform, visual and canonical flow validators pass
locally. GitHub Actions run `35552156045` is green. These changes do not close
the native tenant, permitted-feed or unattended-operation gates listed above.

## Platform route recheck — current user — 2026-09-21

The requested move to current-user platform implementation was attempted
read-only. `playwright-cli list` reported no browsers; the CUA Chrome provider
and in-app browser provider were unavailable; attaching to the running native
Chrome app failed with a ScreenCaptureKit stream error. No login, target
switch, platform write, flow activation, sharing change or schedule change was
attempted. The local user-scoped source remains the only synchronised
canonical version until an attachable current-user platform session is
available.
