# Implementation plan

- [x] Record scope and acceptance requirements.
- [x] Inspect current inputs, dependencies and relevant platform objects. University research-office pages and access boundaries were checked; no institutional login or portal export was used.
- [x] Implement: Record JCU, UQ, QUT and Griffith authority pages, formats, access, eligibility scope and only source-backed internal lead-time facts.
- [~] Verify: Public-page evidence is recorded; permitted feed/export routes and internal portal access remain unverified, with unknown lead times retained as null.
- [x] Record local and live evidence separately before closure.

## Phase: Review fixes

- [x] Task: Validate known institutional lead-time objects while retaining null for unknown evidence (a179d73).
- [x] Task: Reject boolean lead times and invalid authority/verification metadata before source use (f0ee882).
- [x] Task: Reject fractional institutional lead times so catalogue values match integer-day planning inputs (ae2a630).
- [x] Task: Reject non-object rows, non-string institution identities and future verification dates using the Australia/Brisbane business date.
