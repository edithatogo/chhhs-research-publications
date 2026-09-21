# Implementation plan

**Access scope:** current-user source inspection and reviewed/manual intake
only. No shared feed credentials, organisation-wide collector or unattended
source schedule is part of this tranche.

- [x] Record scope and acceptance requirements.
- [x] Inspect current inputs, dependencies and relevant platform objects. The reviewed delivery source map and official authority pages were inspected; endpoint payloads remain unverified.
- [x] Implement: Convert the researched source map into configuration with authority, format, access, sample and coverage status.
- [x] Implement fallback: Add a fail-closed reviewed-import route for sources without a permitted feed/API; require source/row identity, evidence URL, timezone-aware observation, reviewer notes and explicit `Reviewed` status.
- [x] Preserve review context: the bounded HTML calendar adapter retains the complete observed source row under `SourceColumns`, alongside the normalised title and raw deadline, without promoting candidates.
- [~] Verify: Verify NHMRC, MRFF, ARC, QH, EMF, Advance Queensland and local foundation intake; use reviewed import where feeds are unavailable. Authority-page/configuration evidence is complete, including additional Queensland Health, Metro North, Metro South, Torres and Cape and Cancer Council sources. The ARC public JSON awards API has a bounded HTTP-200 sample and is explicitly `awards_only`; NHMRC and MRFF now have bounded HTTP-200 HTML calendar candidate extraction, while unattended feeds/APIs, row-level review, source links and eligibility verification remain open.
- [x] Record local and live evidence separately before closure; the catalogue marks unverified intake explicitly and does not promote it to a working feed.
- [x] Review fix: make catalogue freshness validation use the declared Australia/Brisbane business date so UTC-based CI cannot reject a same-day verification date (commit `c00560f`).

## First-party source recheck — 2026-09-22

- [x] Recheck the official NHMRC and MRFF calendars and the ARC Grants
  Search/API guidance. NHMRC and MRFF remain HTML calendar/search surfaces;
  the current MRFF page directs applicants to GrantConnect for current
  opportunities and notifications. ARC documents a public JSON API for the
  Grants Search dataset, but GrantConnect remains the authoritative source for
  Commonwealth grant opportunities and guidelines.
- [x] Preserve the source classification: ARC JSON remains `awards_only` for
  this registry and must not be promoted to open-opportunity intake; NHMRC and
  MRFF remain review-gated HTML candidates until a permitted export or API
  supplies stable row-level identity, evidence and eligibility.
- [~] Keep G02/G04 open for a permitted opportunity export/API or an explicit
  reviewed row package. Authority-page reachability is not feed acceptance.

## Queensland source freshness recheck — 2026-09-22

- [x] Recheck the official NHMRC calendar: it exposes current/upcoming scheme
  rows and explicitly cautions that dates are planning information requiring
  confirmation in the final guidelines. Keep the HTML adapter review-gated.
- [x] Recheck Queensland Health, Health Practitioner Research Scheme, Metro
  North and Metro South sources. The pages expose current programme or round
  information, including the HPRS 2027 round, Metro North curated openings
  and Metro South 2027 RSS/INNOVATE dates; each remains manual-review intake
  with scheme/employment eligibility preserved.
- [x] Refresh `last_verified` to `2026-09-22` for those five catalogue entries.
- [ ] Do not promote any of these pages to unattended RSS/API ingestion until
  a permitted row-level export/API, stable identity and eligibility evidence
  are obtained. G02/G04 remain active.

## Native reviewed-row acceptance — 2026-09-22

- [x] Use the official Metro South Health 2027 INNOVATE page as a reviewed
  HTML source, retaining its row URL, published dates, amount and employee
  eligibility statement. No feed/API promotion was made.
- [x] Admit the canonical reviewed row `metro-south-innovate-grants-2027`
  through the existing current-user Grants Registry flow; native run
  `08584115872127113780695944024CU04` succeeded and SharePoint readback
  returned one item (ID 8).
- [x] Delete the exact test row and read back the empty registry; receipt:
  `private/ops/2026-09-22-powerautomate-g02-g04-metro-south-reviewed-row.json`.
- [~] Keep unattended source/API promotion, broader row-level eligibility
  review and production acceptance open.

## Phase: Review Fixes

- [x] Task: Preserve positional source cells alongside the convenience header map in the review-only HTML adapter (review fix `24e880c`).
- [x] Task: Fail closed on malformed authority/API URLs and source verification dates (bb8ed64).
- [x] Task: Treat non-HTTP(S) opportunity links as non-actionable evidence and retain them as review-needed records (da0b657).
- [x] Task: Require scalar source IDs and reject future catalogue verification dates (`e4985b2`).
- [x] Task: Require typed reviewed-import identities, URLs, review status and notes without coercion.
- [x] Task: Reject malformed ARC award identities, links and descriptive fields without coercion (03568d7).
- [x] Task: Require structurally valid HTTP(S) ARC evidence URLs, not just a URL prefix (`96079a0`).
- [x] Task: Preserve row-level HTTP(S) provenance for review-only HTML calendar candidates (e62b6f5).
- [x] Task: Require distinct row-level evidence URL and explicit eligibility statement before reviewed import (working-tree review fix).
- [x] Task: Reject reviewed rows whose `SourceRowURL` is identical to the general opportunity URL (`ffdc5a8`).
- [x] Task: Reject malformed optional descriptive fields before reviewed-row normalization (`04642b1`).
- [x] Task: Reject non-string authority/API URLs in the source catalogue (`18dd567`).
- [x] Task: Reject authority/API URLs with surrounding whitespace before intake validation (`ec5322c`).
