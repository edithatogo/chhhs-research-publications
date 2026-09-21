# G04 review

## Conductor review — ingestion identity boundary — 2026-09-22

- **Finding:** API-shaped `SourceID`, `ExternalID`, `RoundID` and URL fields were passed to the canonical normaliser, which strips surrounding whitespace before deriving keys and evidence URLs.
- **Fix:** those identity and URL fields now reject surrounding whitespace at the source-input boundary; human-readable title/description fields remain normalisable. Regression coverage covers each strict field class.
- **Verification:** focused ingestion tests pass (27); project checks pass 460; web-first, Conductor and diff validation pass locally.
- **Residual gate:** native feed permissions, source-change/archive reconciliation, recurrence, monitoring, unattended operation and production acceptance remain open.

## Summary

Review status: in progress; local ingestion is implemented and tested, while live source and platform execution remain open.

## Synchronized verification — 2026-09-22

The canonical checkout passes 456 tests (8 skipped), 460 project checks,
Conductor validation and source-only CI run `35660297803`. Live feed access,
SharePoint writes, native flow execution and unattended operation remain open.

Conductor review fix applied: calendar candidate identity now hashes the full
source row and duplicate identities fail closed before any candidate rows are
emitted. The focused adapter tests cover this failure path.

Additional review fix applied: duplicate non-empty RSS/Atom source identities
now fail closed in `parse_feed` rather than being silently deferred to a later
merge. The ingestion test suite covers this boundary.

Additional review fix applied: RSS/Atom entries without a title now fail closed
before normalization, matching the required SharePoint registry field.

Additional review fix applied: entries without either a source identifier or URL
now fail closed, preventing weak title/funder fallback identities from entering
the registry path.

Review fix applied: API-shaped records now use the same required title, URL,
stable-key and timezone-aware retrieval contract as RSS/Atom records before a
source batch can be accepted.

Additional review fix applied in `8817e21`: entries that lacked explicit
source IDs could still normalise to the same URL-based `OpportunityKey` within
one source batch. RSS/Atom and API-shaped batches now fail closed before
records are emitted; cross-source observation merging is unchanged.

Additional review fix applied on 2026-09-21: a non-object batch now fails
closed with an explicit `ValueError` before source-health processing, rather
than leaking an incidental attribute error.

## Changes

- Added `scripts/grants_ingestion.py` with namespace-tolerant RSS/Atom parsing and API-shaped batch normalization.
- Added per-source health results and failure isolation: a malformed source cannot erase successful records from another source, and a mixed batch is not accepted as complete.
- Retained raw deadline text and canonical deadline precision through the existing normalizer.
- Added `scripts/grants_arc_api.py` for the bounded ARC NCGP JSON API route. It
  preserves the public award identifier, evidence URL, status and amount but
  emits `RecordKind=Award` without an `OpportunityKey`, preventing award rows
  from entering the open-opportunity upsert path. `tests/test_grants_arc_api.py`
  covers page bounds, metadata preservation and fail-closed malformed input.
- Added `scripts/grants_html_calendar.py` for review-only extraction from
  official NHMRC and MRFF calendar tables. A live bounded probe produced 13 and
  179 candidate rows after suppressing a repeated MRFF header row, all with raw
  deadline text and `Needs Review`; no row was
  admitted to the accepted registry.

## Evidence

- `tests/test_grants_sources_ingestion.py` covers RSS, Atom, source failure isolation, catalogue validation and newest-observation/review preservation.
- No SharePoint write, flow import, recurrence or notification was performed.
  The HTML probe was read-only and its private receipt is
  `private/ops/2026-09-20-grants-html-calendar-readback.json`.

## Current bounded source exercise — 2026-09-21

The review-only adapter was run against fresh bounded HTTPS responses from the
official NHMRC and MRFF calendar pages. It returned `candidate_rows` with 13
NHMRC rows and 179 MRFF rows, preserving the source headers and raw deadline
text. The first NHMRC candidate was the published MRFF clinical-trial
collaboration row, demonstrating that the NHMRC calendar is a combined view;
source identity is therefore retained rather than inferred from page title.
No candidate was admitted to the accepted registry, and no SharePoint or flow
write was performed. This strengthens local/source evidence only; the live
source/list/flow acceptance gate remains open.

## Remaining gate

Run a controlled live cycle only after G02 endpoint/access verification and G03 isolated list readback. Then reconcile source keys, changed deadlines and archived rounds before operational acceptance.

## Verification Checks

- [x] **Plan Compliance**: Partial - RSS/Atom/API-shaped adapters, source isolation, calendar candidate handling and duplicate-identity fail-closed behaviour are implemented; live source/list/flow acceptance remains open.
- [x] **Style Compliance**: Pass - raw source values and uncertainty are retained; no source is promoted solely from page reachability.
- [x] **New Tests**: Yes - the ingestion suite now covers duplicate RSS/Atom source identity, titleless-entry, unbound-entry, incomplete API-record and non-coercible identity rejection.
- [x] **Test Coverage**: Partial - local parser and batch contracts are covered; live feed permissions, source changes and platform writes are not.
- [x] **Test Results**: Passed - focused ingestion tests (18) and canonical-clone full suite (374 tests, 8 skipped).

## Findings

### Medium - live ingestion acceptance remains open

- **File**: `conductor/tracks/G04_grants_ingestion/plan.md`
- **Context**: Local adapters do not prove a permitted source feed/API, SharePoint write, Power Automate execution, schedule or reconciliation against live rows.
- **Suggestion**: Keep G04 active until G02 source evidence and G03 target/binding gates are satisfied, then run a controlled source-to-list cycle and reconcile keys, deadline changes and archived rounds.

## Conductor review recheck — native reviewed-row cycle — 2026-09-22

### Summary

The official Metro South Health 2027 INNOVATE page was exercised through the
existing reviewed-import flow as a bounded current-user test. The canonical
row key was admitted, read back and removed; the flow was restored Off.

### Verification checks

- [x] Source and distinct row URLs are retained; eligibility, amount and date
  window were supplied as reviewed values.
- [x] Canonical flow run succeeded:
  `08584115872127113780695944024CU04`.
- [x] SharePoint readback returned one item with
  `OpportunityKey=metro-south-innovate-grants-2027` and ID 8.
- [x] Cleanup returned HTTP 200; final registry readback was an empty Atom
  feed and final flow status was Off.
- [ ] Unattended feed/API intake, source-change reconciliation, recurrence,
  monitoring, delivery and production acceptance.

### Findings

This closes the bounded reviewed-row-to-list execution gap for the isolated
manual route. It does not promote the official HTML page to an unattended
source and G04 remains active pending source change/reconciliation and
operational evidence.

Receipt:
`private/ops/2026-09-22-powerautomate-g02-g04-metro-south-reviewed-row.json`.

## Conductor review — malformed batch hardening — 2026-09-21

- **Verification:** focused G04 ingestion tests passed (15); full suite passed (374 tests, 8 skipped); project validation passed (438 checks); web-first contracts passed locally.
- **Finding/fix:** `ingest_batches` previously called `.get()` on a malformed non-object batch before it could fail through the contract. Commit `9d09f30ed154609515474d34ec0087d0a9b4649d` adds an explicit object check and regression coverage.
- **Residual gate:** permitted live source access, SharePoint/flow execution, reconciliation and unattended operation remain open.

## Conductor review — shared normalizer typing — 2026-09-21

- **Finding:** direct callers of `normalize_opportunity` could bypass adapter-level checks and have identity or display fields stringified implicitly.
- **Fix:** commit `f6e33e4` adds a shared typed-input boundary and regression coverage for malformed identity/display fields.
- **Verification:** focused registry tests pass (8); the full suite passes 388 tests with 8 skips; project validation passes 438 checks; web-first, Conductor, Power Platform tooling and visual standards checks pass locally.
- **Residual gate:** permitted live source access, SharePoint/flow execution, reconciliation and unattended operation remain open.

## Conductor review — pre-normalization source typing — 2026-09-21

- **Finding:** API-shaped records were normalized before raw field types were checked, allowing malformed title or identity values to be stringified when the URL was valid.
- **Fix:** commit `5fa0467` validates declared source fields before normalization and adds an adversarial regression case.
- **Verification:** focused ingestion tests pass (19); the full suite passes 385 tests with 8 skips; project validation passes 438 checks; web-first, Conductor, Power Platform tooling and visual standards checks pass locally.
- **Residual gate:** permitted live source access, SharePoint/flow execution, reconciliation and unattended operation remain open.

## Conductor review — ingestion identity type hardening — 2026-09-21

- **Verification:** commit `213a704` passes the focused ingestion suite (18 tests), the full local suite (374 tests, 8 skips), project validation (438 checks), web-first contracts and Conductor validation.
- **Boundary:** source, URL, title and opportunity-key admission is now type-safe and fail-closed; live feed permissions, source changes, SharePoint writes and unattended operation remain open.

## Conductor review — source identity whitespace boundary — 2026-09-21

- **Finding:** the source catalogue could pass an untrimmed source identity to
  ingestion after using its trimmed form only for duplicate detection.
- **Fix:** commit `232025adbfcb3a19ff7834a26ccfe7c59d91750c` rejects surrounding
  whitespace before a catalogue identity can reach source-health or registry
  processing.
- **Verification:** focused ingestion tests pass (21); the full suite passes
  415 tests with 8 skips, 438 project checks pass, and web-first, Conductor,
  Power Platform, visual and canonical flow validators pass locally.
- **Residual gate:** controlled live source-to-list execution, reconciliation
  and unattended operation remain open.

## Conductor review — amount scalar boundary — 2026-09-21

- **Finding:** the shared grants normalizer validated many display and identity
  fields but could stringify structured or boolean `Amount` values into the
  canonical registry, weakening source evidence and downstream list typing.
- **Fix:** commit `b10810d` accepts scalar text/numeric amounts, rejects
  objects, arrays and booleans, and adds regression coverage.
- **Verification:** focused registry tests pass (9); the full suite passes 423
  tests with 8 skips; 438 project checks, Conductor, web-first, Power
  Platform, visual and canonical flow validators pass locally.
- **Residual gate:** permitted live opportunity intake, controlled
  source-to-list reconciliation, native acceptance and unattended operation
remain open.

## Conductor review — source identity canonicalisation — 2026-09-22

- **Finding:** `parse_feed` and `ingest_batches` previously accepted source
  identities with surrounding whitespace and silently collapsed them to a
  trimmed value. This could conceal source-catalogue drift and make source
  health attribution ambiguous.
- **Fix:** the shared `_validate_source_identity` boundary now requires a
  non-empty string with no surrounding whitespace. `ingest_batches` records a
  malformed source identity as a failed source-health row without discarding
  successful batches; malformed batch objects retain the explicit fail-closed
  error contract. Commit is recorded with the implementation checkpoint.
- **Verification:** focused ingestion tests pass (24); the full suite passes
  448 tests with 8 skips; project validation passes 460 checks; web-first,
  Conductor and diff validation pass locally.
- **Residual gate:** live feed/API permissions, source-change reconciliation,
  SharePoint writes, recurrence, monitoring and unattended operation remain
  open. Local evidence does not certify native tenant acceptance.
