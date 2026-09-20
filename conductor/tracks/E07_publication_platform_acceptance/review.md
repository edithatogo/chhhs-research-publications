# Track Review: E07 Publication Platform Acceptance

## Current status — 2026-09-20

This track remains **in progress**. Local contracts, package construction,
source reconciliation and the seven-page grants design are implemented, but
the platform acceptance gates require current tenant evidence.

The authenticated Power Automate details page for the single retained
canonical publication flow currently reads **Off**. Flow Checker reads **0
errors** and **1 warning**, where the warning context is that the flow is off.
The visible 28-day history reads 2 succeeded, 1 test-failed and 3 failed runs.
That is useful operational evidence but not consecutive-cycle, unattended,
recurrence or release acceptance. No write, enable, run or schedule activation
was performed for this readback.

The authenticated SharePoint Site Contents readback for `eHealth-comm-test`
did not expose `Publication Registry`, `Grants Registry` or `DORA Activity
Registry`. This site is therefore not an approved target for creating or
migrating a registry, and no list was created there. The earlier private DEV
flow receipt records a personal DEV `Publication Registry`; it does not prove
an organisation-wide target or grants-list availability.

Review fix applied: the local validator now requires create and update actions
to use SharePoint Online and target the same site/list as the lookup action.

## Review Report: E07 hardening — 2026-09-21

### Summary

The local acceptance contract is stronger after review: registry lookup and
write operations must use the expected SharePoint operation IDs, and writes
must declare connector authentication. Native tenant acceptance remains open.

### Verification Checks

- [x] Plan Compliance: Partial — the local contract hardening is complete; the native platform gates remain open.
- [x] Style Compliance: Pass — the validator remains fail-closed and preserves the SharePoint-list-only boundary.
- [x] New Tests: Yes — regression coverage rejects an incorrect lookup operation and missing write authentication.
- [x] Test Coverage: Partial — local definition coverage is present; private package and tenant execution are not available in the canonical clone.
- [x] Test Results: Passed — full canonical-clone suite 362 tests, 8 skipped; publication contract validation passed.

### Findings

One local contract gap was found and fixed in `6230e1e`: connector identity
and target parity alone did not prove the expected SharePoint operation or
authentication metadata. The fix is committed and tracked above. Remaining
tenant gates are substantive acceptance boundaries, so E07 is not eligible
for archive.

## Remaining gates

- [ ] Approved isolated SharePoint target and list schema/readback.
- [ ] Controlled create/replay/update and duplicate/concurrency evidence.
- [ ] Failure-safe batch, source failure and canonical key-set reconciliation.
- [ ] Refresh/report readback and monitoring evidence.
- [ ] Additive organisation fields readback and controlled backfill.
- [ ] Unattended recurrence evidence and release decision.

Evidence receipt: `private/ops/2026-09-20-powerautomate-publication-flow-tests.json`.
Local checks do not close these native gates.
