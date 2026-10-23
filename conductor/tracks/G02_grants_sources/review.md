# Review

## Public-source continuation — 23 October 2026, 11:36 UTC

Resumed G02-H02/H03 under the no-contact direction. The official QGIP
[expenditure dictionary resource](https://www.data.qld.gov.au/dataset/queensland-government-investment-portal-expenditure-data-consolidated-view/resource/80e06969-7193-4b94-a425-f52e27ece371)
was acquired as an original PDF (811,721 bytes; SHA256
`71c3660e423006ff017bd0f4f133af552cafb2e697968b89e8a46f9ad1cb112a`).
The resource states CC BY 4.0. PDF page 3 (printed page 2) explicitly delegates Grants Finder programme
funding requirements to a separate dictionary; expenditure definitions cannot
qualify opportunity identity. PDF annotations identify that reference as
`https://treasury.govnet.qld.gov.au/wp-content/uploads/qggf-program-funding-data-dictionary-data-file-standards.pdf`.
The hostname did not resolve from this environment; the public web tool also
could not access it. No authentication or alternate private access was attempted.
A bounded current QH datastore metadata read (`limit=0`) reports 400 records and
Service ID as text, with no explanatory field metadata. The web index also returned
an older resource view; its older dates/type were not substituted for current API
metadata. Existing complete snapshots remain the pagination/replay evidence.

Finance's [publishing requirements](https://www.finance.gov.au/government/managing-commonwealth-resources/commonwealth-grants-rmg-410/publishing-reporting-requirements)
reconfirm GO ID as opportunity identity and require publication of alterations,
addenda and closing-time changes. This is useful identity/change evidence, but
supplies no new retrieval, complete replay, reuse or withdrawal/deletion contract.
The QH 2026 call and linked guideline were rechecked without changing their
partial qualification or retrying the unchanged original-download denial.

**Unresolved:** QGIP Service ID stability, programme/round and lifecycle semantics;
GrantConnect complete permitted retrieval/replay and reuse/lifecycle proof; QH
source identity/lifecycle and retained original; source-to-registry/model acceptance.
No source or reviewed batch was admitted. G02-H02 remains partial and G02-H03
remains dependent on accepted G04-H03. The concrete QGIP recheck trigger is an
accessible official publication of the referenced programme dictionary or equivalent
publisher definitions; inspect those definitions before changing qualification.
No native mutation, source promotion, contact, approval request or archive occurred.
Private acquisition, metadata, access result and assessment receipts:
`private/ops/2026-10-23-g02-public-continuation/receipt.json`.
Actual `.venv/bin/python` was 3.15.1. No tests were rerun for these evidence-only
documentation changes; unchanged prior scoped checks remain local evidence only.

## Current closure audit and model evidence — 23 October 2026

G02 remains incomplete: current catalogue qualification has zero opportunity
admissions, the reviewed-batch route has no accepted batch, and G04-H03 did not
pass. These are technical source/intake gaps, not operational adoption or a
request for anyone's approval. The archive action remains ineligible.

The same source/intake gate persists across three consecutive goal turns. Current
execution is blocked pending new public authoritative source identity, round and
lifecycle evidence with authorized original retention, or an already-evidenced
reviewed source batch, followed by accepted G04-H03 intake/recovery. The existing
checkpoint reserves model/report writes for another lane; its current source
changes are preserved. No native mutation, rerun, contact, approval request or
archive is justified by this blocked audit. Exact current catalogue/task checks
are retained in `private/ops/2026-10-23-g02-blocked-audit.json`.

An authenticated in-app-browser read identified the existing recovery canary's
Grants Registry partition and exact registry binding in Viewing mode. Its table
contains 44 columns, lacks all six deadline-time columns, and is marked as
containing no data. The 20 displayed refresh-history entries are terminal, with
the latest completed on 9 October. This supplies a concrete candidate target and
schema gap; it does not establish full current rollback, external-consumer
isolation or a nonempty accepted baseline. No model edit or refresh occurred.
Private native receipt:
`private/ops/2026-10-23-g02-canary-target-readback/native-web-receipt.json`.

The Fabric MCP failed with a broken pipe; Azure CLI Power BI acquisition
returned AADSTS70043. The separately authenticated Fabric CLI is 1.8.0 with
declared Python support below 3.15. A disjoint Python 3.15.1 resolution selected
1.3.1; this automatic downgrade was rejected and the temporary environment was
removed without authentication or native calls. Shared clients, profiles and
dependency files were preserved. The supported authenticated in-app browser
provided the bounded native readback instead. Compatibility evidence is retained
in the same private directory's `fabric-cli-python315-qualification.json`.

Actual repo-local `.venv/bin/python` reports 3.15.1. Its grants harness passes
411 tests with 2 optional JSON Schema skips:
`private/ops/2026-10-23-g02-python3151-grants-check.log`. This verifies the changed
runtime for this scoped check; broader migration belongs to its existing owner.
The current source and intake gate audit is retained in
`private/ops/2026-10-23-g02-completion-audit.json`.

## G02 continuation and dependent fixes — 23 October 2026

The official Queensland Health Clinical Research Capacity Building Grant 2026
funding guideline has its own CC BY 3.0 Australia notice on page 2, allowing
adaptation with State of Queensland (Queensland Health) attribution. This is
document-specific evidence and does not change the general website's CC BY-ND
terms or establish FAQ reuse. Pages 1/3 identify the scheme and 2026 round;
page 6 states the closing instant. Source identity/reopening and opportunity
withdrawal/deletion meaning remain unqualified; the application's withdrawal
provision on page 7 must not be misclassified as an opportunity lifecycle rule.
The official PDF was read via the web tool, but one CLI original acquisition
returned HTTP403. The receipt explicitly records no retained PDF/hash:
`private/ops/2026-10-23-g02-qh-2026-guideline-evidence/receipt.json`.
No reviewed batch or source admission was manufactured from this partial proof.

The dependent G04 adapter's reviewed-input defects were fixed locally and saved
to the same stopped native workflow using the qualified ETag-guarded Dataverse
route. Exact post-save definition/binding/state readback and 411 passing grants
tests (2 optional skips) are recorded in G04's existing review and private
receipts. Native runtime for those predicates and G04-H03 intake remain unproved.
G02-H02/H03 and G02 archival remain open until opportunity qualification and
selected intake acceptance actually pass. No contact, new access or source
collector was initiated.

## Implemented

- The grants catalogue now permits only official HTTPS RSS, Atom or API endpoints
  with a verified machine readback and a configured stable reconciliation key.
- ARC's official grants API returns JSON:API award identifiers at `data[].id`;
  it is retained only as awarded-grant context, never as an open-opportunity feed.
- Queensland's official CKAN API returns its Grants Finder package identifier at
  `result.id`; it is retained only as source-catalogue metadata, never as an
  opportunity or award feed.
- The endpoint probe reads machine endpoints only and rejects missing configured
  identities. HTML calendars, portal pages, newsletters, directories and
  browser page content cannot create candidate records.
- RSS and Atom endpoints now receive the same bounded readback: an explicit
  structural identity path such as `channel.item[].guid` or `entry[].id` must
  yield a record identifier before a feed can be reconciled.

## Remaining gate

No reconciled official machine-readable open-opportunity source is currently
verified. Add one only after its endpoint, stable record identity, schema and
model-key reconciliation are read back.

An official GrantConnect RSS URL was assessed as a candidate only. Its
non-interactive bounded GET returned HTTP 403 on 2026-09-22, so it is not in
the catalogue and cannot create records. A successful official machine-endpoint
readback is required before reconsidering it.

## G02-H01 disposition review — 2026-09-24

The source-by-source matrix in `docs/GRANTS_DELIVERY_REVIEW.md` reconciles the two maintained machine endpoints with the priority official authorities and existing private receipts. It records entity class, key status, access observation, dated evidence and an explicit admission or fallback decision. The historical NHMRC/MRFF HTML counts remain research history, not accepted records. G02-H01's coverage-decision task is complete; no official open-opportunity machine route has been admitted. G02-H02's replay/schema checks and G02-H03/G04 opportunity acceptance remain open. This review contains no tenant operation or new source fetch.

## G02-H02 local probe hardening — 2026-09-25

The machine endpoint probe now fails closed when a configured API/RSS/Atom
identity path returns duplicate IDs, reports malformed XML as a bounded
readback failure, and closes HTTP error responses. Sanitised regression tests
cover duplicate API identities, malformed RSS, and HTTP 403/429. The focused
probe suite passes (6 tests) and ARC API tests pass (3 tests). This advances
local failure semantics only; per-source pagination, replay/change/deletion
semantics and native endpoint-action acceptance remain open.

## G02-H02 API representation check — 2026-09-28

The shared bounded probe now requires an API response media type containing
`json` before parsing configured reconciliation IDs. This prevents a 200 HTML
login/error page from appearing reconciled merely because it embeds a
JSON-shaped identifier. JSON structured-suffix media types remain supported.
Two focused tests cover HTML rejection and `application/problem+json`
acceptance. RSS/Atom structural parsing is unchanged. This is local response
integrity only; pagination/replay semantics, native endpoint-flow execution,
QGIP/ARC lifecycle authority and opportunity admission remain open.

2026-10-03 historical identity route check: the QH CKAN package contains a
2017–18 program-funding resource with the same `Service ID` field and a
reported total of 200 rows. A complete two-page official API read found all
200 values blank/non-text. This historical resource cannot provide a
cross-year identity comparison; do not treat the field's presence in the
schema as evidence of populated identity or lifecycle semantics. Receipt:
`private/ops/2026-10-03-qgip-historical-service-id-probe-private.json`.

The same live probe exposed that its old 128 KiB generic limit rejected the
configured QGIP 100-row CKAN page, while the existing QGIP adapter already uses
a 2 MB bounded limit. The generic probe now uses that same hard ceiling. A
focused oversized-response regression confirms responses above 2 MB still
fail closed; the 2 MB ceiling is not an unbounded read. A second exact source
probe is recorded separately to preserve the first failed observation.

The RSS/Atom probe also now rejects a non-feed envelope or any entry without
a nonblank reconciliation ID. It no longer silently drops such entries while
reporting a feed as reconciled. Focused source-probe tests pass; this does not
admit an opportunity feed or establish deletion/lifecycle semantics.

## G02-H02a QGIP review-only adapter — 2026-09-25

Local hardening re-reads the official CKAN package and Grants Finder index after
the paged snapshot. It fails closed if the package slug, licence, resource
membership, or QH-to-resource pointer changed during collection. Synthetic
tests cover both mapping-drift cases. This remains local consistency evidence;
it does not establish Service ID lifecycle semantics or canonical admission.

The official Queensland CKAN API resolves the Grants Finder index's `QH` row
through its `Resource` field to QGIP's `Current program funding` resource. Live
readback showed 400 rows with an explicit exact-count flag, four pages of 100,
CC-BY-3.0 package metadata, and populated unique Service IDs in this snapshot.
The resource was last modified 2026-02-11. `_id` is ordinal; Service ID
immutability and change/deletion behavior remain undocumented.

Added a read-only QGIP adapter that validates package/resource/licence,
rechecks resource metadata around paging, requires exact contiguous pages,
rejects missing or duplicate source IDs, and emits only rows with source status
Open and an exact normalized Grant assistance category. Both derived availability
and freshness remain `Needs Review`; the observed source status is retained
separately and does not assert current availability. It preserves per-row evidence
hashes plus a deterministic complete-snapshot digest and does not create a canonical key. Catalogue admission is `candidate_only`, which
is not accepted by the canonical opportunity ingestion boundary. Thirteen
synthetic adapter tests and grants source-intake tests pass. No raw source rows
or tenant artifacts were saved.

The local adapter now emits complete-snapshot metadata plus per-Service-ID row
hashes, and `compare_snapshots()` classifies same-day digest equality as
repeatability only. A later-date comparison reports added, removed, and changed
Service IDs from row hashes; equal later digests mean only that no content
change was detected between the dated observations. Neither comparison proves
Service ID immutability or authoritative lifecycle semantics, and both retain
`canonical_admission=false`. Four regression tests cover same-day equality,
later-date equality, row-level changes, and invalid/non-forward comparisons.
This is comparison tooling; G02-H02b also requires dated official snapshots and
public documentation of identity/lifecycle semantics. No external confirmation
will be sought.

Federal route disposition was rechecked against official pages on 2026-09-25;
details and direct source links are in `docs/GRANTS_DELIVERY_REVIEW.md`. NHMRC's
calendar and Find Funding are human-facing pages, while Tracker is an email
subscription. MRFF publishes dated current/forecast tables and directs users to
GrantConnect for current records and notifications. The Department documents
its RSS as general news. No opportunity-specific machine contract (endpoint,
key, terms, schema, paging and replay) is evidenced for these routes, so no
adapter was added. GrantConnect's prior public 403 plus the missing public API
documentation leave its authenticated/export interface unresolved, not absent.
The next executable research gate is a read-only check for new public authoritative
interface documentation; do not contact the platform owner or administrator.
Keep reviewed imports with provenance in the interim. G02-H02c's
route-disposition research is complete; G02-H02d and G02-H02b identity/lifecycle
evidence remain open, so H02 is not complete. No HTML scrape or news-to-
opportunity inference is allowed. Mocked retrieval tests cover multi-page
offsets, metadata drift, HTTP errors, content type and byte bounds.

## 2026-09-25 redirect host boundary

`scripts/grants_source_probe.py` now marks a probe reconciled only when the
final response remains HTTPS on the exact catalogued official hostname. A
successful HTTP response redirected to another host is not accepted as source
evidence; no additional redirect host is inferred. The focused source-probe
suite passes 7 tests. Official feed/API contract and source identity gates stay
open.

## 2026-10-03 probe evidence boundary

Normal CLI output now exposes the source classification, response status,
record count and body fingerprint without printing response record IDs,
endpoint URLs, catalogue paths or exception details. The public
`probe_catalogue()` API has the same redacted contract; raw results are
available through an explicitly named private evidence collector. Full
evidence is written only when `--out` resolves inside the repository's ignored
`private/ops/` directory; the path is checked before any endpoint request.
The source-probe suite passes 20 tests, including API/stdout redaction and
rejection of an external evidence path. No source was fetched or admitted for
this change; the saved 2026-10-03
receipt predates the redacted CLI and has not been rewritten. G02-H02 full
pagination/replay/lifecycle and native acceptance remain open.
## Opportunity admission contract — 2026-09-25

The source catalogue now rejects a proposed opportunity admission unless the entity is `opportunity` and `official_row_hosts` is a nonempty list of valid official hosts. This prevents award or catalogue-metadata rows from becoming an admitted opportunity feed through a catalogue edit alone. The current three machine rows remain ARC award context, Queensland catalogue metadata and QGIP review-only candidates; no open-opportunity feed was admitted. Focused validation passed 22 tests; G02 native identity/interface and source-row acceptance gates remain open.

A further bounded official QGIP CKAN API read returned the same complete 400-row digest as the earlier 2026-09-25 snapshots. All current Service IDs are populated and unique, and six rows remain review-only; the private receipt `private/ops/2026-09-25-qgip-identity-lifecycle-followup.json` stores current per-ID hashes and lifecycle fields for future comparison. The source's published update timestamp remains 2026-02-11. Same-day equality does not establish immutable IDs or authoritative change/deletion semantics, so QGIP is still not an admitted opportunity feed.

Official `datastore_info` describes `Service ID` as nullable text, neither indexed nor a declared unique/primary key, and provides no change-event or tombstone contract. The QGIP collector now checks that schema before and after pagination, failing if the key field shape drifts; a fresh 400-row API read still yields six review candidates and `accepted=false`. This prevents a stable same-day digest from being mistaken for lifecycle proof.

The review-only snapshot comparator now compares the complete per-Service-ID row-hash map and source update timestamp for content equivalence. CKAN may reorder identical rows between page reads, so the order-sensitive snapshot digest remains a diagnostic rather than a false added/changed/deleted signal. A metadata-only update is identified separately. This does not prove that a Service ID is immutable or that a missing row is an authoritative tombstone; G02-H02b and canonical admission remain open. Focused QGIP tests cover reordering and metadata-only change.

The collector now performs two complete bounded datastore reads and requires their per-Service-ID row hashes to agree, so a same-count row replacement during offset pagination cannot silently become a review snapshot. A fresh official CKAN API read passed this check: 400 source rows, six review candidates, source update `2026-02-11T04:31:12.900845Z`, `accepted=false`. This is intra-read consistency only; it does not establish immutable IDs, authoritative deletion semantics, or an admitted opportunity feed. Focused QGIP tests: 24 passing, including a same-count row-replacement failure case.

The local QGIP review comparator now also rejects source timestamps after retrieval and source-update regression across snapshots. These fail-closed checks prevent inconsistent metadata from becoming lifecycle evidence; they do not establish a source ID contract or admit candidates. Focused QGIP tests: 26 passing. No tenant write occurred.

The comparator now retains both raw row hashes and business-content hashes
that exclude CKAN's `_id` ordinal. It distinguishes ordinal-only churn from
program-content change, while treating observed absence as unproven deletion.
Because older receipts lack the new business hashes, comparison with them
fails closed. A fresh complete official API baseline using the revised
adapter has 400 rows and six review-only candidates, with 400 business hashes
and `accepted=false`: `private/ops/2026-09-25-qgip-business-hash-baseline-private.json`.
The next later-date snapshot may test observed changes but still cannot prove
an immutable Service ID or authoritative tombstones. Focused QGIP tests pass.

## ARC award adapter correction — 2026-09-25

A bounded official ARC API read (`page[size]=1`) exposed an `http://` self-link on the exact documented API host even though the request used HTTPS. The local adapter now validates that host, path and record identity before returning an HTTPS URL. It uses JSON:API `data[].id` as `SourceID`, as the catalogue contract specifies, and retains `attributes.code` separately as `AwardCode`; a code difference cannot silently change the reconciliation key. Missing or duplicate API IDs and oversized responses fail closed. Eight focused tests and the bounded live one-record fetch passed. This repaired the initial award-context readback; the subsequent full capture is recorded below.

The full official award-context snapshot completed on 2026-09-25 with 500-record pages: 70 pages, 34,960 unique source IDs and two passes with the same content digest. A genuine slash-containing award ID initially stopped the capture; the general self-link validator now compares the complete official path suffix to the source ID and rejects unsafe or mismatched paths. The raw snapshot and its compact verification receipt remain in ignored `private/ops/2026-09-25-arc-awards-full-snapshot*.json`. This closes complete bounded ARC award observation and same-run replay parity, but not authoritative deletion/change semantics or open-opportunity admission. ARC awards stay outside the opportunity upsert path.

The saved field profile found nonblank source ID, award code, title, official HTTPS URL, description and status on all 34,960 rows; 688 rows have no amount. Source status values describe awards, including closed and declined records, and cannot be used as opportunity lifecycle states. The private aggregate is `private/ops/2026-09-25-arc-awards-field-profile.json`.

## ARC bounded full-source capture contract — 2026-09-25

The local ARC award adapter now requests every page twice and returns a
`snapshot_complete` receipt only after exact pagination metadata, contiguous
page sizes, the declared source total, unique `data[].id` values across pages,
and a digest of every raw source row agree between passes. It defaults to 500
records per page; the observed 34,960-row metadata corresponds to 70 pages at
that size. The adapter caps each response at 2 MB, the source total at 50,000
awards, and each pass at 1,000 pages. A page exceeding the byte bound or a
changed count or row fails the capture without emitting a complete receipt.
The receipt remains `awards_only`, with no canonical opportunity admission or
claim of authoritative award deletion semantics. Thirteen focused tests pass,
including live-scale pagination metadata, incomplete/changed-page fixtures
and a slash-containing official ID. The
full official two-pass capture is recorded above; native registry/model
reconciliation remains pending.

The reviewed-import adapter now emits an order-independent digest and compares
validated batches by stable key as added, changed, unchanged or unobserved.
`--compare-to` exposes the receipt through the CLI. A missing key is never
interpreted as an authoritative deletion, and this comparison cannot promote
ARC awards or QGIP review candidates into opportunities. The current G03
target still has zero rows; a reviewed opportunity source and native
source-to-list reconciliation remain open.

The shared grants normalizer now case-folds `RoundID` in the compound
`SourceID`/round identity, matching its round-only behavior. A source changing
only the case of a round label no longer creates a second OpportunityKey;
distinct rounds remain distinct. This is a local identity fix, not a tenant
rekey. Any already persisted mixed-case keys need an explicit old-to-new
mapping and a fresh target readback before import. Focused registry and
reviewed-import tests passed, followed by the full local harness (645 tests,
450 project checks); native acceptance remains open.

The local official-source probe now rejects the entire API identity array if any record lacks a valid nonblank, unpadded scalar ID. It no longer silently drops malformed records and reports a partial batch as reconciled. The focused grants-source suite passed 33 tests; no source was admitted or tenant row changed. A fresh official-source review of Queensland Grants Finder, MRFF newsletter/news RSS and Health Translation Queensland found catalogue/checklist or news/link material, without a verified opportunity-row API/RSS with stable key and lifecycle. Existing metadata-only and candidate-only classifications therefore remain unchanged. This is an evidence boundary, not a substitute for an accepted source.

## QGIP candidate lifecycle readback contract — 2026-09-26

The complete QGIP snapshot comparator now separates source-row presence from
review-queue entry and exit. An Open/Grant status change can move a Service ID
into or out of the review queue without being misreported as a new or deleted
source row. It reports business changes among retained candidates and ignores
CKAN `_id`-only changes for that purpose. Candidate IDs, boundary status, and
evidence hashes are checked against the complete source-row maps before the
comparison is emitted. Earlier complete receipts without the newly added
candidate business hash remain comparable via their raw evidence hash. The
focused QGIP suite passes 34 tests. These are review signals only: observed
exit is not a tombstone, Service ID immutability is unproven, and canonical
opportunity admission remains false. No tenant write or new source admission
occurred.

The source update clock is now a fail-closed lifecycle input: QGIP snapshots
reject `last_modified` without an explicit timezone instead of silently
assuming UTC. Later comparisons flag business-row changes observed while the
resource update timestamp remains unchanged. That flag is a discrepancy for
source-owner review, not a change event or proof of Service ID immutability.
The saved same-day 400-row baseline remains review-only; it contains no
authoritative Service ID or tombstone contract. The focused QGIP suite passes
36 tests. No feed was admitted or tenant data changed.

## GrantConnect official-route recheck — 2026-09-26

Finance's current GrantConnect requirements establish publication obligations,
not a machine interface. The Community Grants Hub registration guide describes
optional filtered future-opportunity CSV email attachments, without a complete
schema, GO ID mapping, replay coverage or change/withdrawal contract. A bounded
GET of the candidate official RSS URL returned HTTP 403 to this client and no
payload; the URL's third-party mention is not an official specification. The
precise route/evidence gap is recorded in `docs/GRANTS_DELIVERY_REVIEW.md` and
ignored `private/ops/2026-09-26-grantconnect-machine-route-recheck-private.json`.
GrantConnect remains reviewed-import-only; no collector, catalogue admission,
portal login or tenant write occurred.

## 2026-09-27 official QGIP API recheck

The official Queensland CKAN resource emits a timezone-free `last_modified`.
The read-only adapter now interprets that value as UTC under CKAN's documented
UTC storage convention and records `source_timestamp_basis=ckan_utc_naive`;
the original source value and source-age uncertainty remain in private evidence.
The current exact API snapshot contains 400 rows and six review-only Open/Grant
candidates. Comparison with the 2026-09-25 complete snapshot finds identical
source row hashes, zero added/removed/changed Service IDs and six unchanged
review candidates. Receipts:
`private/ops/2026-09-27-qgip-official-review-queue-private.json` and
`private/ops/2026-09-27-qgip-official-two-date-comparison-private.json`.
This supplies two dated observations, but does not establish that Service ID is
an immutable opportunity or round key, that source absence is a tombstone, or
that the annual catalogue reports current opportunity status. The six rows
remain `Needs Review`; G02-H02b and canonical admission stay open.
# 2026-09-28 — strict catalogue identity and authority metadata types

The shared grants-source catalogue loader no longer coerces a non-text
`source_id` into a reconciliation identity, and requires a nonblank text title
and text HTTPS URLs. This closes a local schema-boundary gap where malformed
JSON types could be normalized into apparently valid catalogue metadata.
Regression tests cover numeric source identity, non-text title/authority URL,
and non-text API URL. Focused validation and probe tests pass (16 tests).
Catalogue rows, source dispositions, and opportunity admission are unchanged;
G02-H02 pagination/replay/lifecycle and native acceptance remain open.

## ARC adapter identity and fact-type guard — 2026-09-28

The bounded award adapter now rejects padded IDs/self-links and malformed
title, scheme, status or amount shapes rather than converting objects to text.
Finite numeric funding amounts remain valid and zero is preserved. Page-size
protocol values must be exact integers, not booleans or floats. Focused tests
pass (15 ARC adapter, 11 source-probe). ARC remains classified as award context;
this local schema guard does not prove authoritative lifecycle semantics or
admit awards as open opportunities.

## ARC two-date source comparison — 2026-09-28

A fresh official API capture completed two bounded 34,960-row passes with an
identical digest within the capture. Its key set matches the complete
2026-09-25 capture (zero observed added or missing IDs), while the overall
content digest differs. The later bounded capture initially retained row
hashes only. A further full API capture and local comparison of normalized
records now attributes all observed differences: 641 rows changed only in
`Amount`, from blank in the 2026-09-25 typed snapshot to explicit `0.0`; all
other compared fields match, with zero added or removed IDs. The comparison
ignores only capture-time and evidence-hash fields. Private row-level receipt:
`private/ops/2026-09-28-arc-awards-row-reconciliation-private.json`; fresh
two-pass snapshot: `private/ops/2026-09-28-arc-awards-full-snapshot-current-private.json`.
This supports preserving explicit zero amounts in the adapter but does not
establish authoritative change/deletion semantics; ARC remains award context
and is not admitted to opportunity intake.

The reusable `scripts/reconcile_arc_awards_snapshots.py` now validates complete
unique-ID snapshots and reports added/removed IDs and normalized field changes
without inferring opportunity lifecycle. Its focused tests cover field/key
changes, duplicate IDs and incomplete snapshots.

The 2026-09-28 local catalogue check, `python3 scripts/grants_sources.py
config/grants-sources.json`, validates three official source rows. This is
structural validation only: no opportunity feed was admitted, and G02-H03
remains open pending source acceptance and the G04 reviewed-import gate.

## 2026-09-28 official QGIP package metadata follow-up

A read-only `package_show` call to the official Queensland CKAN API reconfirmed
the QH package licence as CC-BY-3.0 and identified the selected resource as CSV
with the description “Program funding data for the current financial year. All
enquiries should be directed to the funding agency.” Package and resource
metadata contain no update-frequency value; the resource was last modified on
2026-02-11. This supports the stale-prone annual-catalogue assessment but does
not establish a service-level refresh commitment. The `Service ID` field and
two dated snapshots remain evidence of a populated, repeated key only, not an
immutable identity or scheme/round key. Source: [official QH QGIP package
metadata](https://www.data.qld.gov.au/api/3/action/package_show?id=55e12628-5b50-448c-ad27-fa79930e0991).
G02-H02b remains open for authoritative key, identity, closure/deletion, and
timestamp semantics; no candidate was promoted or written to the registry.

A further official read on 2026-09-28 completed two exact, four-page reads of
the 400-row QGIP resource after rechecking the Grants Finder pointer,
package/resource membership and datastore schema. The same-run row hashes
matched. Comparing this capture with the 2026-09-27 complete snapshot returned
the same full digest, zero observed additions/removals or candidate changes,
and six review-only candidates. Receipts:
`private/ops/2026-09-28-qgip-full-snapshot-private.json` and
`private/ops/2026-09-28-qgip-third-date-comparison-private.json`. This is a
third dated observation, not a guarantee of immutable Service ID, lifecycle
semantics, availability, or canonical opportunity identity. No registry write
or promotion occurred; G02-H02b remains open for public authoritative
documentation of identity/lifecycle semantics.


## G02 external-contact direction — 2026-10-23

No person is to be asked for approval, permission, confirmation, review, a
decision or information for G02. Do not contact a QGIP steward, GrantConnect
platform owner, administrator or anyone else, and do not revive prepared outreach
drafts as next actions. Use public authoritative documentation and read-only
source evidence. G02-H02b's public-evidence disposition is complete: QGIP remains
candidate-only because public material does not establish identity/lifecycle
semantics. G02-H02d's public-evidence disposition is complete: GrantConnect
remains unresolved, not absent, and its reviewed-import fallback is preserved.
G02-H03 remains open until G04-H03 accepts a selected opportunity route. Older
G02 notes that mention seeking a response are historical only and do not
authorize or direct contact.

## GrantConnect official documentation route recheck — 2026-09-28

The current Department of Finance applicant page describes GrantConnect as a centralised web-based facility and offers applicant notification sign-up; the publication-requirements page describes publishing obligations, not a machine interface. The official FAQ also identifies manual reporting steps. These consulted official pages document no API, RSS/Atom, export schema or lifecycle contract. This is not proof that no supported interface exists; retain reviewed-import fallback, do not build a collector, and keep G02-H02d open unless public authoritative technical documentation establishes the route. No outreach or response request is part of this project. Sources: [Find a grant (GrantConnect)](https://www.finance.gov.au/individuals/find-grant-grantconnect), [GrantConnect requirements](https://www.finance.gov.au/government/commonwealth-grants/changes-commonwealth-grants-framework-2024/grantconnect-requirements), [Commonwealth Grants FAQ](https://www.finance.gov.au/government/commonwealth-grants/frequently-asked-questions).
# 2026-09-28 QGIP candidate projection guard

While the isolated publication model refresh is still active, advanced this
independent data-layer validation without starting or cancelling a refresh.
The QGIP adapter previously replaced malformed non-text `Purpose` and
`Eligibility` values with empty strings, hiding source-schema drift in the
review candidate. It now rejects non-null values of the wrong type and keeps
null/missing optional values empty. Regression coverage checks numeric,
boolean, array and object values. `python3 -m unittest discover -s tests -p
'test_grants_qld_qgip_api.py' -v` passes 40 tests. No live source request or
registry write was performed. QGIP Service ID stability, authoritative
lifecycle semantics, canonical admission and native endpoint execution remain
open.

## Machine-source 429 response evidence — 2026-09-28

The bounded official endpoint probe now retains `Retry-After` and response
`Date` headers when an HTTP 429 is raised, while keeping the result
unreconciled and performing no automatic retry. The 14 focused source-probe
tests pass, including exact header preservation. This is local diagnostic
hardening only; it does not accept any source, infer a reset window, or prove
native adapter execution. The Power BI refresh allowance is a separate service
boundary.

## JSON API media-type validation — 2026-09-29

The bounded API probe now accepts only `application/json` and registered
`application/*+json` media types (ignoring parameters). Incidental `json` text
in a non-JSON media type no longer permits a response to reconcile. Regression
tests cover misleading parameters, `application/not-json` and JSONP; all 15
focused source-probe tests pass. This is local response validation only; G02-H02
source admission and native endpoint execution remain open.

## 2026-10-03 cross-receipt QGIP lifecycle audit

A read-only local comparison of all six already-saved complete QGIP snapshots
from 2026-09-25 through 2026-10-02 found 400 populated Service IDs, identical
per-ID row hashes and the same complete ordered digest in each capture. No
observed additions, removals or content changes occurred; this is repeated
continuity evidence, not proof of immutable identifiers, program-versus-round
identity, closure/deletion semantics, or freshness. The official [QH QGIP
resource metadata](https://www.data.qld.gov.au/dataset/qh-queensland-government-investment-portal-qgip/resource/03db77e8-d6af-46db-8c39-724d4c8c140c)
still describes a 2026-02-11 data update and a text `Service ID`; published
metadata does not define its lifecycle. Keep all six rows in the review-only
candidate queue; no source admission, registry write, or steward contact was
made. Existing receipts: `private/ops/2026-09-25-qgip-business-hash-baseline-private.json`,
`private/ops/2026-09-26-qgip-candidate-gate-private.json`,
`private/ops/2026-09-27-qgip-official-review-queue-private.json`,
`private/ops/2026-09-28-qgip-candidate-snapshot-private.json`,
`private/ops/2026-09-28-qgip-full-snapshot-private.json`, and
`private/ops/2026-10-03-qgip-fourth-complete-snapshot-private.json`.

## QGIP exact Service ID preservation — 2026-10-03

The review-queue adapter now rejects padded `Service ID` values across all
source rows, including rows filtered out of the candidate queue. It preserves
the exact source key in candidate output and row-hash maps, and rejects padded
keys in saved comparison receipts. Previously trimming could silently change
an identity or merge padded variants. The focused QGIP adapter suite passes 41
tests. Existing six complete source snapshots contain exact unpadded numeric
keys and are unchanged; the stricter comparator revalidated all five
consecutive snapshot pairs at 400 rows each with no observed key or business
content changes. This prevents local key mutation; it does not prove that the
source defines `Service ID` as an immutable program or round identity. No live
request, admission, registry write, or steward contact was performed.

## G02 source adapters revalidated during T11 wait — 2026-10-05

While the separately authorized isolated `RetainedHistoryKeys` refresh remained
in flight, `python3 scripts/agent_harness.py check --task grants` completed
successfully: 350 focused grants tests passed and the existing report builder
returned `PASS_LOCAL_ONLY`. This confirms local source-catalogue, adapter,
identity and validation behavior only. It does not resolve GrantConnect's
undocumented machine interface, QGIP identity/lifecycle authority, source
admission, native flow execution, or canonical registry persistence. No live
source fetch or tenant write occurred in this check.

## ARC HTTP failure and snapshot integrity hardening — 2026-10-05

The ARC adapter now converts `urllib` HTTP errors into a sanitized failure
containing only status and bounded `Retry-After`/`Date` metadata. It closes the
error response, does not retry, and does not expose response bodies or request
URLs. A later-page HTTP failure aborts the whole snapshot rather than returning
earlier pages as complete. The 21-test ARC suite passes, including 403, 429 and
partial-snapshot regressions; grants-focused validation passes 353 tests and
the report builder returns `PASS_LOCAL_ONLY`. This improves local failure
handling only: no source was fetched or admitted, and G02 source
authority/admission and G04 native intake acceptance remain open.

## QGIP classification schema guard — 2026-10-05

The QGIP read-only adapter now validates that `Service ID`, `Status` and each
of `Assistance type1–3` exist as text fields before it reads opportunity pages.
A removed, renamed or type-changed classifier field can no longer silently
produce an empty or incomplete candidate queue. Synthetic tests prove early
rejection and cover the missing/renamed/type-changed cases. The QGIP suite
passes 46 tests and the grants harness passes 355. No source fetch or
admission occurred; Service ID identity, lifecycle and canonical admission
remain open.

## QGIP sixth dated full snapshot — 2026-10-07

The existing explicit-fetch adapter completed the official CKAN read-only
snapshot at `2026-10-06T14:06:48Z`: 400 source rows, exact total, complete
pagination, internally repeated row-hash equality, and unchanged package,
resource, schema and Grants Finder pointer. The six projected rows remain
review-only. Against the complete 2026-10-04 UTC snapshot, the ordered digest
and every Service-ID row hash are equal; there are zero additions, removals,
content changes or candidate transitions. The source-reported update timestamp
is still 2026-02-11 (237 days old). This is another observation of continuity,
not proof of immutable identity, program/round semantics, deletion/tombstones,
or current opportunity availability. No source disposition, canonical
admission, registry row or tenant object changed. Private evidence:
`private/ops/2026-10-07-qgip-sixth-complete-snapshot-private.json` and
`private/ops/2026-10-07-qgip-sixth-dated-snapshot-comparison-private.json`.

## ARC full snapshot timeout — 2026-10-07

The existing `--snapshot` command was run once against the configured official
ARC API. A page request timed out; the adapter returned a network timeout and
did not emit partial records. The zero-byte redirected output was removed and
the sanitized failed-attempt receipt is
`private/ops/2026-10-07-g02-arc-snapshot-timeout-observation-private.json`.
No retry, catalogue status change, opportunity admission or tenant write
followed. This does not show the source is unavailable; complete ARC paging,
replay and lifecycle reconciliation remain open.

## ARC snapshot timeout diagnostics — 2026-10-07

The full-snapshot adapter now locates a failed request by pass/page and reports
completed pages and declared total pages without retaining the endpoint URL,
response body, or partial award records. HTTP failures retain only the already
allow-listed status and Retry-After/Date metadata. A timeout regression proves
the request is not retried and partial records are not returned; the CLI emits
safe failure metadata with a nonzero status. All 23 ARC
adapter tests pass. No live request was repeated; complete source paging, replay,
lifecycle reconciliation and opportunity admission remain open.

The full grants-focused harness also passes 360 tests and builds its local
research-only report output (`PASS_LOCAL_ONLY`). No tenant acceptance is implied.

## ARC official API contract recheck — 2026-10-07

ARC's [Grants Search Help](https://dataportal.arc.gov.au/NCGP/Web/Grant/Help)
(version 8.0, checked 2026-10-07) documents the JSON:API endpoint, pagination
metadata, a maximum of 1,000 records per page, and `attributes.code` as static;
it identifies administering organisation, lead investigator, current funding,
grant status, anticipated end date and investigators as current/post-award
fields. Its example distinguishes an API `data[].id` (`50699`) from the grant
`code` (`LP180100122`). A metadata-only check of the saved 34,960-award
2026-09-28 capture found every `SourceID` and `AwardCode` nonblank and unique;
that observation is not a cross-release stability guarantee. The adapter now
fails closed if a row lacks a nonblank, unpadded `code`, preserving it as
`AwardCode` while leaving the existing `SourceID` mapping unchanged until
cross-snapshot key reconciliation. Official documentation does not specify
source deletion/replay semantics or a cadence/retention contract. No ARC API
call, opportunity admission or tenant write occurred; local ARC tests cover the
required static code shape, and G02-H02 remains open.

## ARC two-date ID/code mapping reconciliation — 2026-10-07

The maintained `scripts/reconcile_arc_awards_snapshots.py` now validates
nonblank, unique, unpadded `AwardCode` values and reports source-ID set,
award-code set and one-to-one mapping parity using counts and a pairing hash.
Running it against the complete 34,960-award captures retrieved on
2026-09-25 and 2026-09-27 found identical ID/code sets and pairing, no added or
removed IDs, and 641 `Amount` differences (all blank-to-zero). The detailed
reconciliation is retained only in ignored
`private/ops/2026-10-07-g02-arc-two-date-row-reconciliation-private.json`.
This supports continuity of the observed mapping across those dates only; it
does not establish future API-ID stability, grant-round semantics,
deletion/lifecycle behavior, cadence or reuse terms. ARC remains awards-only
context and is not an opportunity source. No network request or tenant write
was made for this comparison.

## Public opportunity-source disposition update — 2026-10-23

The official Finance pages rechecked for G02-H02d still document GrantConnect's
authority and GO ID identity but no permitted retrieval API/export contract,
authentication, reuse, schema, paging or lifecycle. H02d is therefore complete
as a public-evidence disposition: the interface remains unresolved, not absent;
no contact, support request, authentication or collector is part of this work.

The official EMF calendar lists Queensland Research Program Rounds 47 and 48,
schemes, deadlines and maximum amounts. EMF's website terms allow one copy for
research/personal use unless otherwise stated and prohibit changing its material;
they do not establish bulk or transformed-system reuse. Keep EMF human-reviewed
discovery only. One anonymous request to GrantLedger's documented API returned
HTTP 200 with one of 636 open results and exposed source ID `GO8618`, GrantLedger
ID `2930`, a GrantConnect source URL, per-row `CC BY 3.0 AU`, and
`last_verified=2026-10-22T20:30:28.855836+00:00`. This sample does not prove full
coverage, identity continuity, lifecycle or source accuracy. GrantLedger remains
non-selected; no full capture, data retention, collector or automated intake was
performed.

G02-H02b's public-evidence disposition is complete: QH QGIP remains
candidate-only because public documentation still does not define Service ID
identity, program/round semantics, or closure/deletion behavior. This does not
qualify or admit the source.
G02-H03 remains open: no selected opportunity route has been accepted by
G04-H03. These observations change source classification only; they do not
establish registry or native acceptance.

## G02 source evidence reconciliation and focused checks — 2026-10-23

Reconciled the existing ARC evidence without another source fetch or native run.
The 27 September complete two-pass snapshot records 34,960 award rows, 70 pages
of 500, the full source-ID hash map, and no opportunity admission. The dated
25/27 September comparison records identical source-ID and AwardCode sets with
one-to-one pairing; 641 changes were blank-to-zero `Amount` normalisations.
The 22 September native test receipt records a successful read-only run of the
ARC sample and Queensland catalogue actions; the flow is Off, Flow Checker has
zero errors and the Off-state warning, and the run made no writes or schedule
changes. This establishes access and dated award-key continuity only. It does
not establish API-record reuse rights, future key stability, round identity,
lifecycle/deletion semantics or opportunity acceptance. The ARC catalogue
`last_verified` date now matches the latest complete snapshot observation
(2026-09-27).

The required local H03 checks were run: catalogue validation accepted four
official rows; `test_grants_source_probe.py` passed 20 tests and
`test_grants_arc_api.py` passed 33 tests. The delivery-review operations matrix
already records role-only ownership, recheck interval, last-good pointer and
disable/recovery for maintained sources. G02-H02 and H03 remain open: rights and
lifecycle gaps remain for context-only sources, and G04-H03 has not accepted a
release-selected opportunity route. No live fetch, native flow run, registry
write, or contact occurred.

## Official opportunity-page route recheck — 2026-10-23

Rechecked the existing NHMRC and MRFF official discovery pages. NHMRC's Find
Funding page lists open, upcoming and recently closed calls; its funding
calendar lists schemes and dates and says dates are planning estimates subject
to change. The checked pages document no API/RSS/CSV/export contract. The MRFF
calendar states its current-opportunity table is as of 2026-09-30, the page was
last updated 2026-10-02, and current details/notifications go through
GrantConnect. These remain human-reviewed discovery pages; their check date is
not their data vintage and this review does not prove no separate machine
interface exists. No HTML rows were copied or admitted. The public source matrix
now preserves these dates and limitations. Sources: [NHMRC Find Funding](https://www.nhmrc.gov.au/funding/find-funding), [NHMRC Funding Calendar](https://www.nhmrc.gov.au/funding/calendar), [MRFF grant opportunities calendar](https://www.health.gov.au/our-work/mrff/grant-opportunities-calendar).

## Fail-closed opportunity qualification gate — 2026-10-23

The source catalogue previously allowed an opportunity admission after checking
entity kind and official row hosts, without requiring the full proof listed in
the G02 specification. Added one shared qualification contract to catalogue
validation and enforced it again at the ingestion boundary. Opportunity rows
now require a timezone-aware observation timestamp and, for response schema,
complete pagination, replayed keyset, stable identity, lifecycle semantics,
reuse terms and entity reconciliation, an explicit `verified` status with its
own nonempty evidence-reference list. All other source classifications keep
their prior behavior. No current source was promoted; the maintained four-row
catalogue still validates with zero opportunity admissions. Focused
`test_grants_sources_validation.py` (13 tests) and
`test_grants_sources_ingestion.py` (41 tests) pass. No source fetch, native run,
registry write or contact occurred.

## Structured qualification status for maintained sources — 2026-10-23

Added a dated evidence record to each of the four machine-source catalogue rows.
ARC has verified schema, full pagination and two-pass replay, but only partial
cross-date identity/entity mapping and unresolved lifecycle/reuse. RGS has a
documented schema and status vocabulary, but only sample pagination, no full
replay, partial identity/lifecycle/entity mapping and unresolved reuse. Grants
Finder is qualified only as package/resource metadata. QGIP has verified schema,
complete paging, cross-date replay and CC-BY terms, while stable identity,
program/round meaning, lifecycle and canonical mapping remain partial or
unverified. These states do not promote any route. The catalogue validator now
requires timezone-aware observation, an allowed status per field and safe
HTTPS/repository-relative references for every route. Opportunity admission
requires all nine fields verified, an `access.decision` of `public` or
`existing_authorized`, and a `reuse_terms.decision` of `permitted`.
Catalogue validation accepted all
four rows; all current repository-local evidence references resolve. The
focused catalogue suite passes 13 tests and the ingestion suite passes 41.
There are zero opportunity admissions; the source rows remain context-only,
metadata-only or candidate-only.

## Repository evidence-reference existence gate — 2026-10-23

The qualification validator now resolves repository-relative evidence paths
against the checkout and requires an existing file whose resolved target stays
inside the repository. Missing paths, directories and symlinks that escape the
checkout are rejected; safe HTTPS references remain accepted. Focused tests cover
both missing and existing local evidence files. The maintained catalogue still
validates with zero opportunity admissions; no source status was promoted.
`python3 scripts/grants_sources.py config/grants-sources.json` validated all four
rows; focused validation passed 14 tests and source ingestion passed 41 tests.

## Explicit reuse decision for opportunity admission — 2026-10-23

The `reuse_terms` evidence field now carries an explicit decision enum in
addition to its evidence status and references. Opportunity admission requires
`status: verified` and `decision: permitted`; restricted, not-permitted,
unresolved and not-applicable decisions fail closed. Current decisions are
unresolved for ARC, RGS and Grants Finder, and permitted for QGIP under its
CC BY-3.0 source licence. QGIP remains candidate-only because identity,
lifecycle and entity reconciliation are not fully verified. This separates
proof that terms were observed from a decision that the intended reuse is
allowed; no source classification or admission changed.
The updated catalogue passed validation with four rows; the focused source
validation suite passed 16 tests and the ingestion suite passed 42 tests.

## Explicit access decision for opportunity admission — 2026-10-23

The source qualification now also records an `access` status, evidence and
decision: public, existing-authorized, restricted, unavailable, unresolved or
not applicable. A public or existing-authorized decision requires verified
access evidence; opportunity admission rejects the other decisions. The
independent ingestion boundary uses the same qualification check, so direct
batches cannot bypass it. Current catalogue sources have verified public read
access, but remain classified as awards context, metadata or candidates. The
catalogue validated four rows; focused validation passed 18 tests and ingestion
passed 44, including acceptance of `existing_authorized` when its evidence is
verified. No source was promoted.

## Separate program/round qualification — 2026-10-23

Added `round_semantics` as a required evidence field separate from
`stable_identity`. This records whether source identifiers distinguish program,
scheme and round boundaries, including repeated or changed rounds. Opportunity
admission now requires verified round semantics at both catalogue validation
and direct ingestion. Current dispositions are partial for RGS, not applicable
for the Grants Finder metadata index, and unverified for ARC/QGIP. Catalogue
validation accepted all four rows; focused validation passed 18 tests and
ingestion passed 44. No source class changed and no opportunity source passed
admission.

## NHMRC and MRFF award-data route distinction — 2026-10-23

Current official documentation confirms these source classes remain separate.
NHMRC describes its research-funding datasets as annual award snapshots and
reports a 2026-03-25 data vintage; its accountability page says awarded grants
are published on GrantConnect within 21 days, may be revised there, and are also
published on NHMRC's site. The MRFF statistics dashboard refreshes alongside
recipient outcomes, excludes embargoed outcomes, and licenses webpage material
under CC BY 4.0 subject to exclusions. This does not qualify an opportunity feed
or generalize the dashboard licence to recipient workbooks. The delivery review
and G02 plan now record these distinctions; no source classification or
admission changed. Sources: [NHMRC research funding statistics and data](https://www.nhmrc.gov.au/funding/outcomes-and-data-research/research-funding-statistics-and-data), [NHMRC accountability and reporting](https://www.nhmrc.gov.au/about-us/accountability-and-reporting), [MRFF funding statistics dashboard](https://www.health.gov.au/our-work/mrff/about/medical-research-future-fund-funding-statistics-dashboard).

## Explicit bounded-sample qualification — 2026-10-23

Added `bounded_sample` as a required, separately evidenced source qualification
field. It records sample capture and response-shape checking; complete pagination,
replay/keyset, identity/lifecycle and entity reconciliation remain independent
gates. ARC, RGS, Grants Finder metadata and QGIP each reference existing bounded
readback evidence. Catalogue validation and direct opportunity ingestion both
fail closed when the field is missing. The validator accepted four rows; focused
validation passed 19 tests and ingestion passed 45 tests. No source class or
opportunity admission changed; G02-H02 remains open for unresolved source proof.

## Grants-focused harness recheck — 2026-10-23

After adding the bounded-sample gate, `python3 scripts/agent_harness.py check
--task grants` completed successfully: 404 grants-focused tests passed, 2 optional
JSON Schema tests skipped because `jsonschema` is not installed, and the report
builder returned `PASS_LOCAL_ONLY`. This is repository-local evidence only; it
neither qualifies a new source nor closes G02-H02/H03 or G04-H03.

## Canonical source entity-class guard — 2026-10-23

The catalogue validator and independent direct-ingestion boundary now fix the
required ARC row to awarded-grant context and the Queensland Grants Finder row
to source-catalogue metadata. Neither can be relabelled as an opportunity by
changing `record_kind` and `reconciliation` fields or by bypassing the loader.
Regression cases cover both protected rows and retain a separate synthetic
opportunity row for generic admission-contract tests.
`python3 -m unittest tests.test_grants_sources_validation
tests.test_grants_sources_ingestion` passes 67 tests. The maintained source
catalogue still validates with zero opportunity admissions; this local
integrity guard does not qualify a route or close G02-H02/H03.
