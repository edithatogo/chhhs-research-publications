# Remaining Conductor track audit

Audit date: 2026-09-21. This is a source and acceptance ledger, not a claim
that the tenant is complete. A track is archivable only when its plan tasks
and its required native acceptance evidence are both complete.

| Track | Current evidence | Remaining gate | Archive decision |
|---|---|---|---|
| S02 | Clean canonical source package reproducibly verified; SharePoint item versioning observed | Isolated native report version/batch display and readback | Keep active |
| G02 | Official NHMRC/MRFF calendars, ARC awards API, Queensland metadata API, conservative source catalogue, and fail-closed row-level evidence/eligibility gate verified | Permitted opportunity feed/API or explicit human-reviewed rows with source links and eligibility | Keep active |
| G03 | Isolated Grants Registry schema and authenticated synthetic create/update/duplicate/concurrency evidence; existing flow updated in place; fresh native export contains `SourceRowURL`, choice mappings and current server timestamp; flow remains Off with Flow Checker 0 errors and 1 inactive-flow warning; synthetic replay cleanup completed and API readback is `ItemCount=0` | User-scoped operational acceptance; shared organisation-wide target and unattended operation are future extensions | Keep active |
| G04 | RSS/Atom/API-shaped adapters and fresh 13/179 NHMRC/MRFF candidate extraction | Controlled source-to-list cycle and reconciliation | Keep active |
| G05 | University catalogue and access/lead-time evidence | Permitted institutional export/feed or reviewed intake | Keep active |
| G06 | Typed relationship contract and local safeguards; isolated personal DEV `Grant Relationships` list with all eight native fields; `RelationshipKey` required/unique/indexed; synthetic evidence-bearing create/read/update/read/delete round-trip; post-cleanup relationship `ItemCount=0`; publication registry `ItemCount=1468` read back with no publication mutation | Full before/after publication-key reconciliation and shared binding | Keep active |
| G07 | Fail-closed operational evaluator, exact-key reconciliation, selected-field readback reconciliation and isolated create/update replay | Native monitoring, operational reconciliation, delivery and scheduling | Keep active |
| G08 | Local calendar, institutional-date, current-user subscription and delivery-ledger contracts; exactly one native personal `My Funding Watchlist`, `Funding Calendar` and `Funding Delivery Ledger` list; dedicated watchlist, calendar and delivery-ledger SharePoint upsert flows each have controlled native evidence and are Off after testing; delivery-ledger first failure was repaired by an in-place Update import and a same-key success replay; native delivery identity (`Title` mapped from `DeliveryEventKey`) is now required, unique and indexed by SharePoint readback; two report pages and the existing semantic model have native SharePoint tables; the existing My workspace report now has saved native visuals with Reading-view field/row readback for Grants Registry, Funding Calendar and My Funding Watchlist; all three synthetic test rows were removed through exact-item SharePoint delete confirmations and list readback | Current-user flow/page binding, subscription isolation, report refresh/reconciliation, revision/change ledger and actual calendar/reminder delivery; stale status copy on the calendar page is cosmetic documentation debt | Keep active |
| T11 | Local PubMed/DORA preservation and schema/key reconciliation; isolated personal `DORA Activity Registry` with all 26 fields, required/unique/indexed identity, indexed record/resource IDs, synthetic full-field create/read/delete round-trip, and one imported current-user upsert flow with successful controlled create/update/readback and cleanup to `ItemCount=0` | Native retained-history flow/report integration, refresh, recurrence, delivery and operational acceptance | Keep active |
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
for current-user operational acceptance; shared organisation-wide target and
unattended operation remain future extensions.

Native G03 cleanup continuation — 2026-09-21: the remaining synthetic replay
row (`Synthetic G03 replay 20260920 UPDATED`) was deleted from the isolated
personal `Grants Registry` through the authenticated SharePoint UI. The
SharePoint API immediately read back `ItemCount=0`. No production row was
changed and the flow remains Off.

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

Controlled calendar persistence evidence: one synthetic deadline item was
created in the personal `Funding Calendar` with an exact calculated date,
source URL, policy key and default `Needs Review` state. All visible values
were read back, the policy key was edited and read back, and the item was
deleted. The list returned to zero rows. This proves current-user list
persistence only; it does not prove report binding, revision-ledger logic,
calendar delivery, notifications or unattended operation.

## Native T11 DORA Activity Registry bootstrap — 2026-09-21

The authenticated personal DEV site had no existing `DORA Activity Registry`,
so exactly one isolated list was created. The canonical 26-field schema was
then bootstrapped and read back through SharePoint REST. `DORAActivityKey` is
required, unique and indexed; `DORARecordID` and `DORAResourceID` are required
and indexed; the remaining fields have the canonical text, note, date/time and
URL types and requiredness. Versioning is enabled and the list initially read
zero items. A synthetic row populated every mapped field, read back all 26
fields and identity values, was deleted, and the API read back `ItemCount=0`.
This proves isolated schema/row persistence only; DoRA flow import, retained
model/report integration and live or unattended operation remain open.

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

## Native G08 watchlist-flow bootstrap boundary — 2026-09-21

An existing reviewed-grants flow was cloned temporarily to test reuse for the
personal `My Funding Watchlist`. The personal list and its four fields were
resolvable, but the cloned grants trigger/parser lacked the dedicated
`Scope`/`TargetKey` subscription contract. The incomplete copy was discarded.
Power Automate then read back exactly three remaining flows: publications,
reviewed grants and reviewed DoRA. No temporary watchlist flow remains.

## Native DoRA flow continuation — 2026-09-21

The first target-injected DoRA package was rejected by the SharePoint connector
because action parameter keys used display names rather than connector
internal names. The canonical definition and validator now apply the explicit
internal-name map. The rebuilt package imported as exactly one current-user
`CHHHS DoRA Activity Registry - Reviewed Upsert` flow in the isolated personal
DEV target. Controlled create and same-key update runs both succeeded;
SharePoint readback confirmed the mapped identity and updated values, then the
synthetic row was deleted and `ItemCount=0` was confirmed. Flow Checker showed
0 errors and one warning for the flow being Off; it was restored to Off after
testing. Retained-history/report integration, recurrence, notifications,
delivery and production acceptance remain open.

## Native G08 delivery-ledger continuation — 2026-09-21

The personal DEV site then received exactly one `Funding Delivery Ledger` list.
Native field readback confirmed the visible identity, user/opportunity, event,
revision, offset, channel, status, schedule/send and error fields; `Status`
has default `Pending`, versioning is enabled with a 50-major-version limit,
and the list was empty before testing. A SharePoint-only ledger flow was
bootstrapped from the calendar/grants package pattern and imported as the sole
new flow identity. The initial controlled run
`08584116256446744665855863737CU13` failed because an empty optional `SentAt`
value was submitted as `""` to a SharePoint date field. The definition was
repaired to pass null for empty optional date/error values, the same flow was
updated in place, Flow Checker read 0 errors and 0 warnings, and the corrected
same-key run `08584116253756053128213151733CU27` succeeded. SharePoint readback
showed the single row updated to revision `v2`, channel `email`, status `Sent`,
the revised scheduled date and a populated send timestamp. The flow was
restored Off. The synthetic row remains pending explicit UI deletion
confirmation; this is current-user persistence/replay evidence only and does
not prove notification delivery, subscriptions, report binding or unattended
operation.
