# G08 review

Review status: in progress; local planning and idempotency contracts are implemented.

- `validate_policy` requires a version, organisation, anchor, lead time, holiday-calendar version and effective dates.
- `delivery_event_key` gives future notifications a stable deduplication key; it does not send messages or create calendar events.
- Existing subscription matching remains candidate generation only and does not authorize delivery.
- Added `scripts/grants_calendar.py` as a local iCalendar projection contract.
  It derives institutional all-day dates from exact source deadlines and a
  versioned policy, preserves the external deadline, emits stable event IDs,
  marks unreviewed events `TENTATIVE`, and represents cancellations explicitly.
  Unknown or partial deadlines are omitted; no calendar or notification is
  created.

## Local report/model surface — 2026-09-20

- Added an empty-safe `GrantsRegistry` semantic-model table using the existing
  SharePoint read definition, with stable opportunity/deadline/review fields
  and explicit measures for total, open and needs-review opportunities.
- Added three additive pages to the existing PBIP: `FundingOpportunities`,
  `FundingCalendar` and `MyFundingWatchlist`. The calendar preserves raw
  deadline text and precision; the watchlist is explicitly a report preview,
  not a personal subscription or notification service.
- Expanded the local dashboard contract to seven pages and added model-binding,
  geometry and page-order tests. This is a source/report definition change,
  not native Power BI page authoring or readback.

Native funding pages, SharePoint list persistence, authenticated preference
isolation, calendar update/cancellation and notification delivery remain open.

## Native boundary readback — 2026-09-20

Authenticated Power BI read-only readback still shows four native pages:
CHHHS Publications, Monthly Publications, Source Reconciliation and Clinical
Analytics. No native funding page is present. Receipt:
ignored `private/ops/2026-09-20-powerbi-report-page-inventory.json`.
The local seven-page definition therefore remains a candidate for an isolated
authoring route, not a tenant deployment claim.

## Native funding-page readback correction — 2026-09-22

Authenticated BrowserOS readback now shows six native report pages, including
`Funding Opportunities` and `Funding Calendar & Watchlist`. The Funding
Opportunities page states that the SharePoint list and DEV upsert flow exist
but the semantic-model binding is pending. The calendar/watchlist page makes
the same pending-binding statement and shows one `synthetic-calendar-20260921`
calendar row plus one `synthetic-watchlist-20260921` watchlist row.

The personal DEV SharePoint site inventory was read back immediately after that
report view: Funding Calendar, Funding Calendar Changes, Funding Delivery
Ledger and My Funding Watchlist each have zero items. The visible synthetic
rows are consequently report-model content, not live list records. They must
be removed or clearly excluded during a future isolated model/report authoring
change; no shared report/model change was made in this readback.

## Flow-boundary readback — 2026-09-22

The authenticated DEV inventory contains separate instant flows for reviewed
Grants Registry upsert, Funding Calendar upsert, Funding Calendar Changes
upsert, Funding Delivery Ledger upsert and Funding Watchlist upsert. The
scheduled publication ingestion flow remains separate, as does the DoRA
registry import. Future grants work should extend those bounded responsibilities
or add a new flow for a genuinely separate trigger/failure domain; it should
not fold grants lifecycle or delivery work into publication ingestion.

## BrowserOS funding-page readback — 2026-09-22

A second authenticated BrowserOS readback confirmed the same boundary in the
rendered report: Funding Opportunities has no bound registry rows and labels
semantic-model binding as pending; Funding Calendar & Watchlist renders only
the explicit synthetic model rows and labels binding and delivery as open. The
report is in the current-user workspace, but model lineage and a recoverable
isolated write path remain unverified. No report or model write was made.
Receipt: `private/ops/2026-09-22-browseros-funding-pages-readback.json`.

## Semantic-model capability readback — 2026-09-22

BrowserOS opened the report's semantic model in the current-user workspace and
read back the existing Grants Registry, Funding Calendar, Funding Delivery
Ledger, My Funding Watchlist and Grant Relationships tables. The surface is
explicitly **Viewing mode** and says changes will not be saved. This proves
the tables exist in the current model but provides no isolated writable model
or rollback path for binding the funding visuals. No query, refresh, model or
report write was attempted. Receipt:
`private/ops/2026-09-22-browseros-semantic-model-readback.json`.

## Report/model lineage correction — 2026-09-22

BrowserOS lineage readback shows the current-user report connected to the
current-user semantic model. This corrects the broader claim that model binding
is wholly absent. It does not prove the narrower missing link: Funding
Opportunities still has no rendered registry rows and Funding Calendar &
Watchlist still renders synthetic rows, so visual-level grants bindings remain
unverified. No model or report write was made. Receipt:
`private/ops/2026-09-22-browseros-report-model-lineage.json`.


## Isolated guidance readback — 2026-09-23

A current full RIMS PBIX export was checksum-verified and imported under a
distinct DEV recovery name. BrowserOS confirmed a separate report/model pair,
all six current report pages and report-edit access. Two verbose static text
boxes were replaced and saved only on the isolated report: Funding Opportunities
now directs readers to filter reviewed registry entries; Funding Calendar &
Watchlist now explains calendar/watchlist use and says reminder delivery is not
yet active. Both changes survived a reading-view reload. The original pair was
not changed. The semantic-model binding, live rows, refresh, calendar changes
and notification delivery remain unaccepted. Private receipt:
`private/ops/2026-09-22-isolated-pbix-recovery-preflight.json`.

## Grant review KPI correction — 2026-09-24

The local KPI previously counted every registry row whose review status was
not the obsolete value `accepted`. That included `Reviewed` rows and overstated
the review queue. The grants intake uses `Needs Review` for records awaiting
review, so the KPI now counts that exact status. The model builder, PBIP TMDL
and local model snapshot agree; a focused contract test checks the expression.
The runtime baseline hash is updated only for `GrantsRegistry.tmdl` after this
review. This correction has not been deployed or read back in the isolated
Power BI model; local validation is not native measure acceptance.

## Funding Opportunities filters and register — 2026-09-25

The local Funding Opportunities page now exposes seven registry slicers:
status, CHHHS relevance, review status, source, eligibility, deadline and funder.
Eligibility is also projected in the GrantsRegistry table visual. The report
definition edits are scoped to this page: its caption/footer, register and
four existing filter definitions. Two new filter visuals add eligibility and
deadline. `tests/test_grants_pages.py` verifies bindings to GrantsRegistry and
that publication pages have no grants binding; the visual-usability contract
checks titles, projections, labels and concise text panels.

Verification: `python3 -m unittest discover -s tests -p 'test_grants_pages.py'
-v` passed 6 tests; `python3 -m unittest discover -s tests -p
'test_report_usability_contract.py' -v` passed 4; `python3
scripts/validate_project.py` passed 446 checks. A report candidate was copied
outside the repository and regenerated with `--page FundingOpportunities`; its
97 files remained byte-identical, confirming this page's generated output
matches the candidate source. The freeze tracks only the seven changed and two
added Funding Opportunities visual files under
`contracts/runtime-baseline.manifest.json`, with this section as its review
reference. The manifest remains explicitly `native_verified: false` and
`known_defects_open: true`.

This is local definition and structural evidence only. It does not prove
rendered native filter behavior, a live GrantsRegistry binding, refresh or
accepted opportunity data. No Power BI write was made.

## Isolated Funding caption correction — 2026-09-25

On the isolated `CHHHS Research Publications - RIMS DEV recovery` report, the
Funding Opportunities caption's unsupported sentence `Only reviewed registry
entries appear here.` was replaced with `Registry data and review status are
pending native acceptance.` Power BI displayed `Report saved`; after reloading
the same report, the rendered accessibility readback retained the new wording.
The report still shows an empty register and the `ReviewStatus` filter is
`(All)`. Receipt: ignored
`private/ops/2026-09-25-funding-caption-save-reload-readback.json`.

This is report-only evidence. The native title/filter wording still lists the
older funder/deadline/eligibility/opportunity subset and is less complete than
the local seven-filter definition. The semantic-model identity and registry
binding, source credentials, refresh, data population, and release acceptance
remain unverified. No data, model, sharing, or schedule was changed. The local
runtime baseline records the intentional PBIP caption change but remains
`native_verified: false` and `known_defects_open: true`.

## GrantsRegistry partition binding — 2026-09-25

The local model snapshot held the full canonical query from
`config/GrantsRegistry.m`, but `model.tmdl` had no matching shared expression
and `GrantsRegistry.tmdl` bypassed the query's column-selection and typing
steps with a shorter SharePoint read. The model definition now contains the
canonical M expression and the table partition references that expression.
Existing table, column and measure lineage tags were retained while the query
binding was corrected. The table's canonical opportunity-projection
description is also present in the local TMDL definition.

`python3 -m unittest discover -s tests -p 'test_grants_pages.py' -v` passed
7 tests; the new case compares the config query with the snapshot and checks
the TMDL expression and partition binding. `python3
scripts/validate_project.py` passed 446 checks. This local change has not been
deployed or refreshed. Native query evaluation, source credentials, field
availability and lineage parity remain open; no Power BI write was made.

## Funder filter and page baseline — 2026-09-25

The local `FundingOpportunities` report now adds a `Funder` dropdown bound to
`GrantsRegistry[Funder]`. The six existing filters retain their first-row
positions; Funder occupies a second row and the register keeps its prior lower
edge. The page generator and a candidate build were checked before copying
only this page's generated visuals into the local PBIP. Five baselined visual
files changed or were added: footer, deadline filter, eligibility filter,
Funder filter and register. Existing publication pages, model definitions and
native tenant objects were not part of this change.

The frozen manifest was refreshed for the current local visual definitions
after this review. It remains a drift baseline, with `native_verified: false`
and `known_defects_open: true`. `python3 -m unittest discover -s tests -p
'test_grants_pages.py' -v` passed 8 tests before the manifest refresh; the
full harness must pass after reconciliation. Rendered native filter behavior,
live binding, refresh and accepted opportunity rows remain unverified.

## Recovery report structure readback — 2026-09-25

Authenticated BrowserOS rendered the isolated recovery report
`CHHHS Research Publications - RIMS DEV recovery` in My workspace. The report
has six pages: CHHHS Publications, Monthly Publications, Source Reconciliation,
Clinical Analytics, Funding Opportunities, and Funding Calendar & Watchlist.
The Monthly Publications page showed Aug 2026, 9 publications, 189 records
without a usable month, with visible provenance counts of 8 PubMed and 1 DORA.
Its release metadata reads `source-only-canonical`, `NativeAcceptance=false`,
schema `rims-grants-publications-v1`, version `0.3.0-rc1`.

The local PBIP has seven pages and 85 visuals, including a separate
`My Funding Watchlist`; the native report combines calendar and watchlist.
This report readback exposes a layout/page-scope delta that must be reconciled
against current local artifacts before preparing an upload. It does not
establish local/native visual parity, live funding rows, model refresh
acceptance, or tenant release. No tenant object was changed. Private receipt:
`private/ops/2026-09-25-browseros-powerbi-report-readback.json`.

The current rendered funding pages were also read directly in that
authenticated report. Funding Opportunities shows concise reviewed-only
guidance and one empty table with Funder, Deadline, Eligibility and
OpportunityKey headers; no slicer controls are visible and the filter pane
reports no filters. Funding Calendar & Watchlist shows two empty tables, one
with deadline/calendar fields and one with watchlist fields; its filter pane
also reports no filters. This confirms useful page copy but not functioning
filters, live registry rows or personal preference isolation. The seven-slicer
local Funding Opportunities definition has not been reconciled to this native
render. The readback was read-only; no tenant object was changed.

After that readback, the authenticated Power BI `Download this file` route
produced a fresh report-and-data PBIX from the isolated recovery item. The
download callback timed out, but Power BI displayed its completed-download
notice and the file was recovered from Downloads, copied to ignored private
storage, and passed ZIP integrity plus SHA-256 verification. Its
`Report/Layout` is six pages/62 visuals and matches the live page inventory.
Compared with the Sep22 import source, the current export's Calendar and
Watchlist visuals both query `Grants Registry` fields rather than the old
separate `Funding Calendar` and `My Funding Watchlist` tables. Funding
Opportunities still has only a text panel and one table, with no slicers;
Calendar & Watchlist has one text panel and two tables. These exact current
export queries are recorded in
`private/ops/2026-09-25-current-report-artifact-reconciliation.json`; private
PBIX and checksum are recorded with that evidence. It is a new rollback
checkpoint for the current report state. Source-level equivalence between the
native `Grants Registry` table and local `GrantsRegistry` model remains to be
proved before import or rebinding.

The exact isolated recovery PBIX import source in private storage independently
parses to six pages and 62 visual containers. Compared with local counts, this
baseline has CHHHS Publications 15/16, Monthly Publications 12/11, Source
Reconciliation 14/14, Clinical Analytics 16/15, Funding Opportunities 2/14,
and three containers on the combined Funding Calendar & Watchlist page versus
15 visuals across two local pages. Its checksum matches the private preflight.
This PBIX is the Sep22 import source; the report was subsequently edited and
saved in the browser on Sep24. Its visual queries and counts are recoverable
baseline evidence, not the exact current saved tenant visuals. Some baseline
visual ids are hashes, although their visual types and queries are readable.
The separate downloaded canonical report is older and must not be substituted
for the recovery PBIX. Current report queries are now available in the fresh
authenticated service export, but local/native table and source identity,
visual-level field equivalence, slicer behavior, and save/reload of any new
filters remain open.

## 2026-09-25 institutional policy date validation

`scripts/grants_planning.py` now rejects impossible date-only values, timestamp-
shaped policy dates and reversed effective windows. `institutional_policy_status`
classifies current, future, expired and invalid policies for a supplied date;
the effective end is inclusive. The focused planning suite passes 8 tests.
Approval of institutional date policies and integration into native operations
remain open.

## 2026-09-25 post-caption service export reconciliation

After the caption save/reload, `Download this file` produced a fresh isolated
service PBIX. ZIP integrity and the expected SHA-256 were verified, then
`scripts/reconcile_report_artifacts.py` compared its `Report/Layout` with local
PBIP. The native export has six pages/66 visuals versus local seven pages/85;
local `Funding Calendar` and `My Funding Watchlist` remain merged into the
native three-visual `Funding Calendar & Watchlist` page. Funding Opportunities
has six native visuals versus 14 local visuals. The binding matrix reports 28
entity mismatches and 13 unknown/incomparable bindings; source equivalence is
not inferred. Receipt and PBIX are in ignored `private/ops`:
`2026-09-25-post-caption-report-artifact-reconciliation.json` and
`2026-09-25-post-caption-isolated-rims-report.pbix` (SHA-256
`82d4143f915e8eef46aff8b57860441e48c90acf076feef81e4f6c622a3ac16f`). The
parser did not connect to the tenant and no tenant object was mutated during
reconciliation. This export confirms report artifact state only; model source
identity, refresh, data population, field equivalence and release acceptance
remain open.

## Minimal isolated binding preflight — 2026-09-25

The later post-edit and post-reviewed-column service-export receipts still show
six native pages/66 visuals versus seven local pages/85 visuals and retain
`source_equivalence_inferred=false`. They are report-layout evidence, not a
model-source readback. Before changing a funding binding, the single browser
owner should read the isolated report's linked semantic-model identity from
that report, compare its workspace/model ID with the already-open model tab and
the original report/model pair, and read the model's actual `Grants Registry`
field names and SharePoint source target. Match that target to the existing
isolated DEV list's site/list identity and the local
`config/GrantsRegistry.m`/schema mapping. Record the current report export
checksum and a scoped restoration route in the same private packet. A title
match, field-name resemblance, or downloaded PBIX alone does not establish
this identity chain or a tested rollback.

The next report edit can then be limited to one verified field or filter in
the isolated report, followed by save, reload and fresh export comparison.
The empty list prevents a live filter-value or row-key acceptance claim; G03-H01
also still needs Create/Update flow-target readback and historical candidate
provenance. Existing evidence: ignored `private/ops/2026-09-25-post-edit-report-artifact-reconciliation.json`,
`private/ops/2026-09-25-post-reviewed-column-report-artifact-reconciliation.json`,
`private/ops/2026-09-25-grants-storage-flow-readback.json`, and
`private/ops/2026-09-25-grants-storage-reconciliation-readback.json`.

## Recovery report/model identity readback — 2026-09-25

The authenticated post-caption PBIX `Connections` entry names the same report
as the open recovery report tab and the same semantic model as the already-open
model-view tab. In Viewing mode, the native `Grants Registry` field list showed
`CHHHSRelevance`, `Deadline`, `DeadlinePrecision`, `DeadlineRaw`, `Description`,
`Eligibility`, `EvidenceHash`, `Funder`, `Geography`, and `OpportunityKey` among
other fields. The field list was collapsed again after readback. Exact IDs and
the export hash are in ignored
`private/ops/2026-09-25-recovery-report-model-binding-readback.json`.

This closes the report-to-model ID question for the current recovery pair, but
not source or field equivalence. The older `private/ops/isolation.json` names
different development/original report and model IDs. Its rollback and baseline
claims cannot be applied to this pair. Read the current model's SharePoint
source/list identity and establish a current-pair restoration route before a
binding edit or import. The downloaded PBIX has not been tested as a rollback.
The model's read-only Gateway and cloud connections settings show a
`SharePointList` source and an existing DEV retained-archive connection; they
do not expose which list the `Grants Registry` partition selects or its stable
list ID. That data-layer reconciliation precedes further report work under the
current stage order.


## Current funding flow status — 2026-09-28

An authenticated, read-only BrowserOS readback found the existing `CHHHS RIMS -
Funding Calendar - Reviewed Upsert` flow **On** with an Instant/manual trigger.
Its two visible run-history entries (21 September) both succeeded in one to
two seconds. The latest run canvas showed successful `Manually trigger a flow`,
`Parse Calendar Rows`, and `Apply to each Calendar Row` (three nested actions).
No run was started or resubmitted. This historical controlled evidence does
not establish accepted funding rows, full key/field reconciliation, current
source authority, or replay safety. Keep this flow's enabled state unchanged
while its source and G08 acceptance gates remain open. Private receipt:
`private/ops/2026-09-28-funding-calendar-flow-browseros-readback-private.json`.
## 2026-09-28 iCalendar component timestamp correction

RFC 5545 requires `DTSTAMP` and `UID` on each `VEVENT` when the calendar has
no `METHOD`; it also recommends folding content lines longer than 75 octets.
The exporter now places `DTSTAMP` on every event and folds long lines at
Unicode code-point boundaries. Regression tests verify per-event timestamps,
75-octet limits and exact unfolding of long Unicode titles. This corrects the
local ICS artifact only; no feed/event/preference/subscription was created, and
client revision/cancellation behavior remains unverified. Source: [RFC 5545,
iCalendar](https://www.rfc-editor.org/info/rfc5545/).


## Delivery-event key collision guard — 2026-09-28

The local delivery idempotency helper now hashes a typed JSON tuple and rejects malformed identity fields. Regression tests prove that offset zero differs from a missing offset and delimiter-bearing identifiers cannot alias another tuple. Ten planning tests and 32 grants relationship/operations tests pass. This is preparatory local logic only: no ledger rows, preferences, notifications or calendar events were written; G08-H04 still requires its native prerequisites and dry-run evidence.


## Institutional policy input validation — 2026-09-28

Versioned date-policy validation now rejects non-text or whitespace-padded policy identity fields and an explicit empty `EffectiveTo`, which previously could pass or be treated as no end date. Eleven planning tests and 12 calendar tests pass. This is local input validation; it does not accept a native policy, establish timezone/DST behavior, or close G08-H01.

## Subscription candidate input guard — 2026-09-28

The local candidate matcher now validates canonical OpportunityKey, optional funder key, category-key collection shape, and active preference rows. It rejects strings-as-category-lists and malformed active/scope values, while preserving deduplication of overlapping matches. Thirteen planning and 12 calendar tests pass. The canonical opportunity contract does not yet provide `CategoryKeys` or `FunderKey`; no key inference was added. Preference persistence, per-user access isolation, delivery and native acceptance remain open.


The local candidate matcher now rejects active subscription targets that are absent from the opportunity's exact key set. This distinguishes a stale/mistyped preference from a valid no-subscriber result and covers opportunity, category, and funder scopes. The 12 focused planning tests pass. This is local validation only; no tenant preferences were read or written, and it does not establish per-user isolation or authorize delivery.

## Business holiday-calendar input guard — 2026-09-29

Business-day policies now require an explicit `HolidayDates` list of unique,
real ISO dates; missing, malformed, duplicate and non-list values fail closed.
Direct business-day calculation also rejects an omitted calendar. Calendar-day
policies may omit the unused field. Every locally generated ICS date is marked
provisional in its structured output and description until policy and holiday
coverage have separate authoritative acceptance. Seventeen planning and 15
calendar tests pass, including a supplied weekday holiday shifting the
proposed date. This is structural local validation only: an explicit empty
list is not evidence that an authoritative institution has no holidays.
Approved calendar coverage, native persistence/rollback, overrides and
timezone/DST acceptance remain open.
### Holiday coverage provenance guard — 2026-09-30

Business-day policy validation now requires a `HolidayCoverage` record whose
calendar version matches the policy, whose source URL is HTTPS, whose capture
time and SHA-256 are well formed, whose coverage interval is valid, and whose
coverage was explicitly verified. Holiday entries outside that interval
invalidate the policy; a projection whose deadline calculation crosses the
interval is omitted. Calendar-day policies remain independent of unused
holiday metadata. ICS events remain provisional pending authoritative policy
and source-capture acceptance. `python3 scripts/agent_harness.py check --task
grants` passes 275 grants tests with `PASS_LOCAL_ONLY`; no tenant, policy or
calendar was written.

### Strict policy and coverage metadata keys — 2026-10-03

Policy validation now rejects unknown top-level keys and unknown
`HolidayCoverage` keys, preventing misspellings from being silently ignored.
HTTPS source URLs with malformed, out-of-range or zero ports also fail closed.
Date subtraction at the representable year boundary now yields an unknown
projection instead of aborting a batch. The focused policy/calendar suites
pass 37 tests and the full grants harness passes 298 tests. This validates
supplied metadata shape only; it does not establish the source's authority or
approve a holiday calendar.

## Holiday source qualification — 2026-09-30

A targeted read-only request to the [Queensland Open Data API](https://www.data.qld.gov.au/api/3/action/package_search?q=public%20holidays&rows=20) returned four unrelated datasets and no public-holiday calendar. Queensland's [state public-holiday table](https://www.qld.gov.au/recreation/travel/holidays/public) and separate [regional show-holiday page](https://www.qld.gov.au/recreation/travel/holidays/show) are official references, but are web tables and do not establish CHHHS or university deadline policy. The portal's [public-holiday API request](https://www.data.qld.gov.au/datarequest/9bec66f5-ead7-45b3-a798-2d5c3d800247) remains open in the observed record and describes the missing state/local-boundary API. No table scraping or holiday import was performed. Business-day outputs remain provisional until an authoritative, version-bound institutional calendar and coverage contract are available from existing sources; no approval request or external contact is to be made. Private source qualification: `private/ops/2026-09-30-g08-holiday-source-qualification-private.json`.

### Machine-readable holiday feed recheck — 2026-09-30

The official [Australian Public Holidays Dates Machine Readable Dataset](https://www.data.gov.au/data/dataset/australian-holidays-machine-readable-dataset) is marked inactive; its custodian states that no further updates will be released and directs consumers to state and territory government sources. It therefore cannot establish current Queensland calendar coverage. Together with the Queensland Open Data API request above and the absence of a matching Queensland Open Data API package, this leaves no qualified machine-readable source for the required institutional coverage. Do not ingest the inactive feed or scrape the official display table. Keep business-day projections provisional until Queensland Health or the relevant institution supplies an authoritative, versioned calendar/API and confirms its coverage and applicability.

## Preference-store bootstrap correction — 2026-10-03

The isolated model's unchanged `My Funding Watchlist` projection contains opportunity/scope/target/active fields but no `UserKey`, event types, reminder offsets, cadence, channel or timezone. This is projection evidence only, not a complete SharePoint schema or per-user access proof. A fresh BrowserOS read of the exact existing watchlist list returned HTTP 403 `System.UnauthorizedAccessException` with no sign-in challenge, so the existing object cannot currently be inspected for additive reuse. Receipt: `private/ops/2026-10-03-g08-watchlist-sharepoint-readback-failure-private.json`. G08-H02 now requires current schema and permissions readback before choosing additive fields versus a separate preference store; do not infer that a preferences list exists or claim personal isolation.
