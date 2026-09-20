# Remaining Conductor track audit

Audit date: 2026-09-21. This is a source and acceptance ledger, not a claim
that the tenant is complete. A track is archivable only when its plan tasks
and its required native acceptance evidence are both complete.

| Track | Current evidence | Remaining gate | Archive decision |
|---|---|---|---|
| S02 | Clean canonical source package reproducibly verified; SharePoint item versioning observed | Isolated native report version/batch display and readback | Keep active |
| G02 | Official NHMRC/MRFF calendars, ARC awards API, Queensland metadata API, and conservative source catalogue verified | Permitted opportunity feed/API or explicit reviewed rows with source links and eligibility | Keep active |
| G03 | Isolated Grants Registry schema and authenticated synthetic create/update/duplicate/concurrency evidence; flow checker 0/0 | Approved organisation-wide target, canonical binding and unattended acceptance | Keep active |
| G04 | RSS/Atom/API-shaped adapters and fresh 13/179 NHMRC/MRFF candidate extraction | Controlled source-to-list cycle and reconciliation | Keep active |
| G05 | University catalogue and access/lead-time evidence | Permitted institutional export/feed or reviewed intake | Keep active |
| G06 | Typed relationship contract and local safeguards | Native relationship target/readback and unchanged publication totals | Keep active |
| G07 | Fail-closed operational evaluator and isolated create/update replay | Monitoring, operational reconciliation, delivery and scheduling | Keep active |
| G08 | Local calendar, institutional-date and subscription contracts; additive report definitions | Native pages, private access, calendar change ledger and delivery | Keep active |
| T11 | Local PubMed/DORA preservation and schema/key reconciliation | Native retained-history flow, refresh and list/readback | Keep active |
| T14 | Complete local exports, monthly generator and failure contracts | Manual native cycle, consecutive-cycle replay and delivery decision | Keep active |
| T15 | Local handover/package and current four-page report audit | Native release/readback; Clinical Analytics model bindings are broken | Keep active |
| E01 | Corrected publication query and successful DEV flow readback | Replay/update, duplicate/failure safety, reconciliation and unattended cycle | Keep active |
| E04 | Local Fluent/grid/contrast tests pass; native Clinical Analytics has nine field errors | Authenticated isolated authoring route and model/report binding repair | Keep active |
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
