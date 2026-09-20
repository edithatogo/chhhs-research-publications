# Implementation plan

- [x] Record scope and acceptance requirements.
- [x] Inspect current inputs, dependencies and relevant platform objects. The reviewed delivery source map and official authority pages were inspected; endpoint payloads remain unverified.
- [x] Implement: Convert the researched source map into configuration with authority, format, access, sample and coverage status.
- [x] Implement fallback: Add a fail-closed reviewed-import route for sources without a permitted feed/API; require source/row identity, evidence URL, timezone-aware observation, reviewer notes and explicit `Reviewed` status.
- [x] Preserve review context: the bounded HTML calendar adapter retains the complete observed source row under `SourceColumns`, alongside the normalised title and raw deadline, without promoting candidates.
- [~] Verify: Verify NHMRC, MRFF, ARC, QH, EMF, Advance Queensland and local foundation intake; use reviewed import where feeds are unavailable. Authority-page/configuration evidence is complete, including additional Queensland Health, Metro North, Metro South, Torres and Cape and Cancer Council sources. The ARC public JSON awards API has a bounded HTTP-200 sample and is explicitly `awards_only`; NHMRC and MRFF now have bounded HTTP-200 HTML calendar candidate extraction, while unattended feeds/APIs, row-level review, source links and eligibility verification remain open.
- [x] Record local and live evidence separately before closure; the catalogue marks unverified intake explicitly and does not promote it to a working feed.
- [x] Review fix: make catalogue freshness validation use the declared Australia/Brisbane business date so UTC-based CI cannot reject a same-day verification date (commit `c00560f`).

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
