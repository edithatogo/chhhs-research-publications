# G04 review

## Review fixes saved natively — 23 October 2026

Both H02 review findings below are fixed in the local and saved native
definition. The identity guard accepts SourceID or RoundID; the escaped
source-evidence lookup includes source, record and round identity and handles
SharePoint null text. Equal-time replay now compares all 22 source-fact fields
used by local reviewed-batch reconciliation, normalizing SharePoint choice
objects and date-only values. Newer observations remain eligible, older or
equal-time conflicting facts reach the failure diagnostic, and reviewer fields
remain excluded from Update.

The existing Azure CLI/Dataverse route patched only clientdata with the exact
preimage ETag. The PATCH response timed out; no write was resubmitted. Fresh
FlowAgent readback and direct Dataverse readback independently matched the exact
candidate. Workflow identity, display name, connection references and Stopped
state are preserved. Saved definition SHA256:
`a06397b1b7c76703f0b3378f4bb595f06f2ac459743fd78da21a0d88e012551b`.

The initial grants harness exposed two existing assertions tied to the old
required-SourceID/formatting contract. Those checks were updated while retaining
blank-key protection and escaped lookup fields, including RoundID. The final
grants harness passes 411 tests with 2 optional JSON Schema skips; the first
failed run remains retained. Focused regression cases cover round-only local
inputs, every equal-time source-fact conflict, unchanged replay, reviewer-only
changes, newer and older observations. No native runtime fixture or source batch
was submitted. H02 remains partial until runtime evidence covers the fixes;
H03/H04 and G02 source admission remain open.

Private receipts: `private/ops/2026-10-23-g04-fixes-native-parity.json`,
`2026-10-23-g04-fixes-dataverse-preimage.json` (exact rollback clientdata),
`2026-10-23-g04-fixes-dataverse-postimage.json`,
`2026-10-23-g04-fixes-timeout-flow-readback.json`, and
`2026-10-23-g04-fixes-grants-recheck.log`, all under `private/ops/`.
**Documentation pending:** this task owns reconciliation of the changed predicates
into the existing grants module's maintained native documentation after the
bounded runtime fixes are accepted. Existing source and generated-document
identities remain in place; no publication or schedule change occurred.

## G04-H02 native adapter review — 23 October 2026

**Original review result: changes required; H02 reopened.** At that baseline the read-only native definition
matches the retained H02 definition and connection references exactly; its
canonical definition hash was
`9568a122a1134e120aba76e3988db96bd0bebea61c8a5c33e67432187867e209`
and state is Stopped. Local action semantics match after the documented exact
target and authentication-expression normalization. Mapping resolution, the
excluded stale offline package and the retained same-ID rollback preimage remain
valid evidence. Matching intended and native graphs does not establish that the
shared graph implements every reviewed-import rule.

**High — equal-time conflicting facts can overwrite persisted facts.**
`config/flows/grants-registry-reviewed-import.definition.json:387-393` permits
`greaterOrEquals` observation times without comparing source facts on equality.
Two separately valid reviewed batches can carry the same key and timestamp but
different Title/EvidenceHash. The source-identity lookup excludes that same key,
and the native branch proceeds to Update. In contrast,
`reconcile_reviewed_batches` rejects `conflicting_same_time_observation` when
given the prior row; CLI prior comparison is optional. Add a native equality
guard that permits unchanged source facts/replay and rejects conflicting facts
before either update action. Verify unchanged replay and equal-time changed
facts against the exact stopped flow with retained row/version preimages.

**Medium — round-only reviewed identities are rejected by the native adapter.**
`config/flows/grants-registry-reviewed-import.definition.json:80-88` requires
nonblank SourceID. The established local contract accepts SourceID **or** RoundID
and generates a canonical key for a round-only row. An offline accepted row with
blank SourceID and an evidenced RoundID therefore reaches the native invalid
identity branch. Align the native guard and source-identity lookup with the
declared source/round identity contract, then verify create/replay and conflicting
identity behavior without weakening key uniqueness.

Focused review checks: `python3 -m unittest tests.test_grants_flow_contract
tests.test_grants_reviewed_import tests.test_grants_sources_ingestion -q` passed
84 tests. The existing tests do not exercise either native contract gap above;
passing checks do not close the findings. Offline reproductions used disposable
inputs only and submitted no fixture or native run. No definition, connection,
list row, schedule or model was changed. H03/H04 and overall G04 remain open.
This review corrects the completion record; native implementation and runtime
acceptance of both fixes remain required.

Private evidence: `private/ops/2026-10-23-g04-h02-review-native.json` (fresh
native readback), `private/ops/2026-10-23-g04-h02-review-findings-private.json`
(reproductions/check results), and the unchanged H02 pre/post and rollback
receipts in `private/ops/2026-10-23-g04-h02-native-adapter-private/`.

## 2026-09-28 shared source-time parsing

Canonical grants observation timestamps and G04 RSS/Atom/API snapshot
timestamps now share one strict RFC3339 parser requiring seconds and an
explicit UTC offset. The parser retains the distinct `missing_timezone`
classification for naive local instants and rejects permissive forms such as
space separators, omitted seconds, compact offsets and malformed offsets.
Snapshot ordering applies the same parser to both the current and prior
observation before comparing UTC instants. Focused registry, ingestion and
institution suites pass 12, 30 and 30 tests. This is local validation only;
no opportunity feed has been admitted and G04-H02/H03 native intake remains
open.

The G01 canonical normalizer now rejects non-object rows and non-text source
facts instead of coercing them. This extends the source intake guard to direct
normalizer and merge callers, including falsey malformed values otherwise
masked by alias fallback. Registry, planning, machine-ingestion and
reviewed-import suites all pass; no source is newly admitted and native
ingestion remains open.

## Source fact type integrity before G03 import — 2026-09-26

Both the reviewed-import and machine-API boundaries now reject recognized
source facts supplied as numbers, lists or objects where the canonical Grants
Registry schema stores text. Previously optional values such as `Status`,
`Amount` and `Eligibility` could be stringified by the shared normalizer and
appear as authority facts in a G03 row. A real API adapter must explicitly
map its documented structured values to text before intake; this guard does
not admit a feed or authenticate a reviewer. The grants-focused suite passes
208 tests, including the new malformed-optional-field cases. No tenant row or
flow was changed.

## Reviewed identity type and reconciliation guard — 2026-09-26

The reviewed-import boundary now rejects a non-text `SourceID` or `RoundID`
even when the other identifier is valid. This prevents a JSON number or object
from being silently stringified into a canonical opportunity key. The batch
comparator also verifies that pre-normalized reviewed rows carry a key matching
their text source identity, so a caller cannot reconcile a changed ID under an
old key. The focused reviewed-import suite passes 20 tests. This is local
contract evidence only; it does not authenticate a reviewer, admit GrantConnect
as a machine feed, or prove native list execution.

## GO8568 bounded reviewed-import packet — 2026-09-26

The official GrantConnect row read through the authenticated BrowserOS session
confirms public GO ID `GO8568`, its direct opportunity URL, and a displayed
close of 11 November 2026 at 5:00 pm ACT local time. The existing canonical
key is `GRANT:0d13beb2f4175dc25720be58`, derived from
`grantconnect:go8568`; no separate RoundID is evidenced. The generic
date parser now projects the source-stated offset timestamp to 2026-11-11
with day precision while retaining `2026-11-11T17:00:00+11:00` as
`DeadlineRaw`. The NHMRC calendar dates remain planning information until
checked against the latest Guidelines and Addenda.

The GrantConnect documents route redirected to login, so the latest
Guidelines/Addenda, current eligibility and final deadline were not verified.
The candidate remains `Pending`, with empty reviewer notes; it would be
rejected by `scripts/grants_reviewed_import.py`. No HTML collector, tenant
import, list write or review decision occurred. The complete private review
packet and guarded DEV replay/rollback sequence are in
`private/ops/2026-09-26-go8568-reviewed-import-packet-private.json`; the
official row receipt and normalized preview remain separate evidence. Next,
an authenticated human reviewer must verify the latest documents and current
row, determine eligibility/relevance, and bind the decision to trusted review
evidence before preparing a Reviewed batch. G04-H03 remains open.

Review status: in progress; local ingestion is implemented and tested, while live source and platform execution remain open.

## 2026-09-26 reviewed-batch observation ordering

The same-key comparison also rejects conflicting authority facts at the same
observation instant; reviewer-note changes at that instant remain possible.
This avoids order-dependent factual replacement when neither observation is
newer. The focused reviewed-import suite passes 18 tests. No new source or
native opportunity was admitted by this local guard.

The existing reviewed-import batch comparison now rejects a same-key current
observation older than the prior reviewed observation, comparing timezone-aware
instants rather than timestamp strings. It also rejects malformed timestamps
in pre-normalized comparison inputs. Missing keys in a partial current batch
still do not imply withdrawal. The focused reviewed-import suite passes 16/16;
this local guard does not admit a GrantConnect export or prove native upsert.

## 2026-09-25 bounded official API readback

The bounded machine endpoint probe was rerun against the two existing official
catalogue entries; both returned HTTP 200 and one configured reconciliation ID
each. The ARC response reconciled `FT260100001` as award context; the Queensland
CKAN response reconciled package ID
`1d72cbb9-5f99-4ad7-ae92-ddd87884527b` as source metadata. Private receipt:
`private/ops/2026-09-25-grants-source-api-readback.json`. Catalogue verification
dates were refreshed. These samples confirm endpoint reachability and metadata
identity only; they do not establish an open-opportunity feed or admit either
source into the opportunity registry. G04-H01 native upsert/history and
source/list/model reconciliation remain open.

## 2026-09-24 official machine-source admission check

No additional opportunity feed was admitted. The [Queensland Grants Finder dataset](https://www.data.qld.gov.au/dataset/grants-finder) describes its API/CSV resource as a Grants Finder *checklist contribution* resource, with non-regular updates; it is machine-readable catalogue data, not a verified list of current opportunity rounds or stable round identifiers. Its existing `metadata_only` classification remains appropriate. The [official MRFF calendar](https://www.health.gov.au/our-work/mrff/grant-opportunities-calendar) is an HTML table and points applicants to GrantConnect. The [MRFF researcher guidance](https://www.health.gov.au/our-work/mrff/research-themes/researchers) describes registered GrantConnect keyword notifications, which supply neither a verified API/RSS/Atom response nor a replayable row key in this review. Read-only GETs to the GrantConnect home page and two exploratory `/Rss/` paths returned HTTP 403; those responses establish only that this client could not inspect those routes, not that an official feed does not exist.

[Health Translation Queensland's funding page](https://healthtranslationqld.org.au/resources/funding-opportunities) links to administering authorities. Its [CCI Microgrants programme page](https://healthtranslationqld.org.au/our-work/our-consumer-and-community-involvement-program/microgrants-program-3) provides round information in HTML, with 2026 quarterly rounds, but no official machine endpoint or stable round identity was verified. Read-only GETs to exploratory `/feed` and `/rss` paths returned HTTP 404. The page may support a human-reviewed opportunity with provenance; it cannot yet support unattended reconciliation. Next admission evidence must include an official endpoint or export, response schema and terms, stable round key, update/pagination behavior, and a repeated readback that distinguishes changed and closed rounds. No source configuration or tenant object was changed for this research pass.

## 2026-09-24 bounded G04-H01 local hardening

The automated batch boundary now requires an explicit catalogue row admitted as an
opportunity, a machine intake type, an official row-host allowlist and complete
ordered page accounting. Each source batch fails without emitted records for
blank/duplicate identities, invalid authority URLs, timezone-less observations,
invalid supplied deadlines and observations older than a prior watermark. Other
source batches remain isolated. The reviewed importer requires a caller-provided
official host allowlist and rejects invalid deadlines and duplicate keys while
retaining its explicit review evidence requirements. Focused local suites pass
(8 ingestion, 6 reviewed import, 5 registry). These are synthetic contract
fixtures; the current catalogue still admits no open-opportunity machine feed.
G04-H01 remains open pending a real admitted source contract and native history/
write reconciliation; no tenant object or schedule was changed by this patch.

Conductor review fix applied: calendar candidate identity now hashes the full
source row and duplicate identities fail closed before any candidate rows are
emitted. The focused adapter tests cover this failure path.

## 2026-09-25 catalogue identity guard

The local ingestion boundary now fails closed when its supplied source
catalogue contains duplicate `source_id` values. Previously, direct callers
could bypass `load_catalogue` validation and Python's last-wins mapping could
let a later conflicting row shadow a metadata-only identity as an approved
opportunity source. The matching batch now emits no records and reports
`duplicate_catalogue_source_id`. The focused ingestion suite passed all 10
tests with `python3 -m unittest discover -s tests -p
'test_grants_sources_ingestion.py' -v`; `git diff --check` was clean. This is
local synthetic regression evidence only. Native upsert acceptance and
source/list/model key and row reconciliation remain open; no tenant data was
written.

## Changes

- Added `scripts/grants_ingestion.py` with namespace-tolerant RSS/Atom parsing and API-shaped batch normalization.
- Added per-source health results and failure isolation: a malformed source cannot erase successful records from another source, and a mixed batch is not accepted as complete.
- Retained raw deadline text and canonical deadline precision through the existing normalizer.
- Added `scripts/grants_arc_api.py` for the bounded ARC NCGP JSON API route. It
  preserves the public award identifier, evidence URL, status and amount but
  emits `RecordKind=Award` without an `OpportunityKey`, preventing award rows
  from entering the open-opportunity upsert path. `tests/test_grants_arc_api.py`
  covers page bounds, metadata preservation and fail-closed malformed input.
- Native BrowserOS implementation now has an isolated instant flow that makes only the official ARC and Queensland CKAN HTTPS API GET requests. Its controlled run succeeded, after which it was returned Off. It creates no candidate row and has no list, model, report, delivery or schedule write. Receipt: ignored `private/ops/2026-09-22-browseros-funding-machine-endpoint-reconciliation-readback.json`.

## Evidence

- `tests/test_grants_sources_ingestion.py` covers RSS, Atom, source failure isolation, catalogue validation and newest-observation/review preservation.
- No SharePoint write, flow import, recurrence or notification was performed.
  The HTML probe was read-only and its private receipt is
  `private/ops/2026-09-20-grants-html-calendar-readback.json`.

## Remaining gate

Run a controlled live cycle only after G02 endpoint/access verification and G03 isolated list readback. Then reconcile source keys, changed deadlines and archived rounds before operational acceptance.

BrowserOS readback on 2026-09-22 separately confirms that the existing
isolated reviewed-import flow can retain a single official-source candidate as
`Needs Review` through the native Create branch. It is not evidence of a
permitted unattended source or an accepted batch. Receipt:
`private/ops/2026-09-22-browseros-grants-reviewed-import-readback.json`.

### Automated review-field trust boundary — 2026-09-25

API-shaped machine records now pass through a source-owned-field allowlist before canonical normalization. Forged or source-supplied `ReviewStatus`, `ReviewNotes` and `CHHHSRelevance` values cannot enter the registry as internal judgements; defaults remain `Needs Review`, empty notes and `Unknown` relevance. The explicit reviewed-import path remains unchanged and its existing positive admission test passes. No native flow or registry was changed.

The API review-field regression and reviewed-import suite pass (12 ingestion tests and 8 reviewed-import tests). The complete local harness passes 486 unit tests and 446 project checks; Conductor/web-first/tooling pass remain local-only evidence. Native flow and accepted-opportunity intake are still open.
The integrated harness now passes 504 tests and 446 project checks after the separate hardening slices; this remains local-only evidence.

### Reviewed-import envelope hardening — 2026-09-25

The local reviewed importer rejects rows that self-assert reviewer identity or
platform provenance and rejects non-text review evidence. A non-iterable batch
returns a contract error; duplicate canonical keys and any single bad row
reject the whole batch. The focused suite passes 12/12. The importer does not
authenticate the reviewer; reviewer identity must come from a trusted review
surface, and no native flow or accepted batch is claimed.

### Pagination counter type hardening — 2026-09-25

The automated ingestion boundary now requires each `pages_received` value to
be an exact integer. This rejects booleans and floats that Python otherwise
compares equal to page number `1`, as well as string counters. The focused G04
suite passed 19 tests with `python3 -m unittest discover -s tests -p
'test_grants_sources_ingestion.py' -v`; scoped `git diff --check` was clean.
This is local validation only; native intake and acceptance gates remain open.

### RSS/Atom payload bound — 2026-09-25

The official-feed intake now rejects XML payloads above 2,000,000 UTF-8 bytes
before parsing, using the same bounded-response policy as the ARC and QGIP API
collectors. An oversized source yields `feed_xml_payload_too_large`, leaves
other source records inspectable, and rejects the combined batch. Focused
tests cover ASCII and multibyte excess; 20 G04 ingestion tests passed. The
full local harness passed 702 tests and 450 project checks. This is a local
resource-safety contract, not a native accepted feed or DEV registry replay.

### Intake identity type guard — 2026-09-28

The public batch/adapter boundary now rejects non-text batch source IDs,
observation timestamps and prior watermarks instead of coercing them. Direct
catalogue input is validated for text source identity/intake, official host
strings, and reconciliation shape before admission, so it cannot bypass the
stricter catalogue loader or shadow identity through string conversion. Direct
RSS/Atom parsing enforces the same source/timestamp type contract. The focused
G04 ingestion suite passes 26 tests; reviewed-import suite passes 23 tests.
No tenant flow or row was changed. This closes only a local malformed-input
subcheck; an admitted current opportunity source and native history/key
reconciliation remain open.

### RSS/Atom envelope validation — 2026-09-25

The parser now accepts items only from an RSS channel, an Atom feed or an RSS 1.0 RDF document. Incidental nested `<item>` nodes in unrelated XML fail before opportunity intake. A malformed-envelope/RDF regression passed with the 21 focused G04 ingestion tests. This remains local validation; no feed was newly admitted or run in the DEV flow.


### 2026-09-28 source-row URL reconciliation

Historical native receipts confirm the optional custom `SourceRowURL` is distinct from canonical `URL` and can retain a row/anchor fragment. The canonical grants normalizer, observation snapshots, reviewed import, machine API allowlist, SharePoint field projection, schema, and source M query now preserve it separately. A supplied source-row URL is required to use an admitted official HTTPS host; the field does not affect `OpportunityKey`. Focused tests cover fragment preservation, missing optional values, host rejection, and history conflicts. The native flow binding and semantic-model table remain later flow/Power BI gates.

### Iterator-exhaustion failure boundary — 2026-09-28

The adapter now catches exceptions raised while enumerating the catalogue or
batch source. Catalogue failure returns a bounded failed diagnostic. If the
batch iterator fails after yielding rows, the partial snapshot is cleared and
the intake is rejected with `batch_iteration_failed`; it cannot be mistaken
for a complete observation. The focused suites pass 28 ingestion, 23 reviewed-
import and 11 registry tests. No native write or source admission occurred.

The reviewed importer also converts an interrupted row iterator into a stable
contract error and discards any partially materialized rows; underlying
exception text is not exposed. Its focused suite now passes 24 tests. This
remains local validation only.

### G04-H01 local contract acceptance — 2026-09-28

Closed the local adapter-hardening task after matching its planned cases to the
implementation and running all four scoped suites: ingestion 28, reviewed
import 24, native flow definition contract 7, and registry/history 11 (70
tests total). Coverage includes catalogue/entity admission, unsafe and
unapproved URLs, invalid/duplicate identities, timezone and deadline handling,
pagination completeness/order, stale observations, review-field isolation,
retained source observations, exact zero/one/multiple-match flow branches, and
partial iterator failure. This does not admit an opportunity source, prove
official API lifecycle semantics, or accept a native flow/list/model cycle;
those gates remain G02-H02, G04-H02–H04 and G03-H02 onward.

### Reviewed-import CLI output boundary — 2026-10-03

The reviewed-import CLI now emits a summary with counts only;
contact values, reviewer notes, titles, exact identities and source paths are
not printed, and no content fingerprints are exposed. A full validated receipt is optional, restricted to ignored
`private/ops/`, and cannot overwrite an existing file. Focused regressions
confirm the summary is sanitized and a full receipt remains private. This is
not native intake or tenant admission; G04-H02–H04 remain open.


## Funding-source integration review — 16 October 2026

Scope: source commits `3da46ed`, `7e074ef`, `4330dbe`; QGIP reference
adapter, manual native collector builder and downloaded-commit consumer, with
their six source/test files. This is a selected G02/G04 implementation review,
not closure of the whole grants track. All foundational Conductor files and the
existing code style guide were checked. Shared native objects were not changed.

Focused verification: `python3 -m unittest discover -s tests -p
"test_*qgip*.py" -q` passed 60 tests. Source preserves full native envelopes,
closed rows and unknown fields before candidate projection, checks complete
coverage and repeated-read metadata/content, and retains candidate-only/no-
canonical-admission boundaries. The archive consumer performs no network or
service writes. No embedded credential was identified in the reviewed changes.

**Medium / P2 — raw source CLI output bypasses private receipt storage.**
`scripts/grants_qld_qgip_api.py:551-553` prints the complete fetched payload.
The newly retained `raw_source.http_responses` now includes complete API bodies
(base64), and the snapshot also includes unfiltered source rows. A synthetic
fetcher containing a raw-response marker reproduced its appearance in stdout.
This conflicts with the repository rule to keep raw API snapshots in ignored
private paths and can copy them into terminal/CI logs. These are public-source
responses, not a demonstrated credential leak. Suggested fix: emit counts and
status only; add an explicit exclusive-create private receipt output, enforcing
`private/ops` before source acquisition and testing rejection/no-overwrite and
absence of raw rows/body content from stdout. No fix was applied by this review.

Native evidence: saved graph/binding readback is recorded as PASS, Stopped,
with only 21 standard service authentication injections. The latest scoped
receipt says no run submitted and native solution membership not yet qualified
(`private/ops/2026-10-16-funding-intake/collector-saved-parity-private.json`).
Therefore complete native source retention/readback, downstream candidate
reconciliation and exact canonical solution membership/export remain open with
core. Local tests or a saved definition do not close G04-H03/H04 or G02 source
identity/lifecycle gates. Do not archive or mark G04 complete.

Recommendation: fix the CLI output boundary; retain the existing core-owned
native operation and finish its bounded run/archive readback and solution
integration. Product/technology/branding documents need no strategic change.


### Review-fix reconciliation — 16 October 2026

- [x] Close the raw-source stdout finding using existing core commit `06943b8`
  (`scripts/grants_qld_qgip_api.py` and its tests). No duplicate code change was
  needed: stdout contains only counts/status, `--output` is restricted to
  `private/ops`, existing/invalid destinations are rejected before fetching,
  and the receipt is exclusively reserved with mode 0600 before source calls.
  Regression tests check no raw stdout, outside-private rejection before fetch,
  full private receipt preservation and no overwrite. The focused QGIP suite
  now passes **67 tests**. The P2 finding above is resolved.

The native-status paragraph above was accurate at the initial review and is now
superseded by later core receipts: `native-collector-acceptance-private.json`
records 17 stored files, 400 complete rows/42 fields, two reads and 394 excluded
rows retained, with the collector restored Stopped.
`candidate-export-acceptance-private.json` records six candidates/17 fields,
exact JSON/CSV values and unchanged 17 raw source files, with state restoration.
Both receipts remain under `private/ops/2026-10-16-funding-intake/`. This review
checked their consistency locally; it did not submit a run or independently
repeat native reads. Exact source acquisition and candidate export acceptance
do not establish canonical opportunity admission, authoritative lifecycle or
whole-platform/production acceptance. Existing broader G02/G04 tasks stay open.

Core retains ARC's current native run/readback, package, model and checkpoint.
No native effect, source acquisition, schedule, connection or public push was
performed by this fix reconciliation. No further code defect remains from the
selected QGIP review.


### Retained-data replay follow-through — 16 October 2026

The downloaded committed source consumers were each executed twice offline:
QGIP reproduced all 400 source-row hashes and the same six candidate records;
ARC reproduced identical 34,977 award records and source-row hashes. All 17 QGIP
and 141 ARC downloaded file hashes matched before/after. This uses actual
retained source data, not synthetic coverage, and submits no acquisition or
native effect. Private receipt:
`private/ops/2026-10-16-funding-intake/independent-replay-reconciliation-private.json`.
Native output replay/recovery and the next canonical bundle/operator handover
remain integration-owned; within-run repeated acquisition is not substituted
for replay of the existing committed generation.

Public-repository Renovate PR #2 was reviewed at exact head
`0ffe66d8628ed991fe15a643ca97b40bff059365`: a single workflow line upgrades
checkout to an upstream-verified v7 commit. Read-only token permissions, complete
history and disabled credential persistence remain unchanged; no privileged
PR event or unsafe override was introduced. Both exact-head CI checks passed.
Recommendation: merge; no issue identified. This was review only, without
posting an approval or merging. Its private receipt is
`private/ops/public-github-careops-rims/renovate-pr2-review-private.json`.
