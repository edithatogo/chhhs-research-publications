# G07 review

Review status: in progress; local operational guardrails are implemented.

`scripts/grants_operations.py` rejects empty batches, missing or duplicate opportunity keys, and any failed source. When an explicit source policy is provided, it also requires exactly one health record per configured source, matching owner, successful status and timezone-aware `checked_at` within the configured maximum age. Missing/future timestamps, stale checks, duplicate/unexpected health rows and invalid policies fail closed; a rejection returns the prior accepted records. Focused local tests cover these controls. Source policy values and operational owners still need approved operational decisions before use, and native monitoring, concurrency and schedule/delivery evidence remains open.

A controlled authenticated Power Automate replay previously proved one synthetic create and one same-key update, with the flow restored Off; see `G03_grants_sharepoint/review.md` and the ignored receipt `private/ops/2026-09-20-grants-flow-import-readback.json`. This does not establish the freshness policy, monitoring, or acceptance matrix. No unattended schedule, notification or production path was touched.

### Local malformed-input fail-closed checks — 2026-09-25

`evaluate_run` now rejects non-object records, non-text/empty keys and unhashable-key cases without crashing; it preserves the supplied last-good record set on rejection. `evaluate_source_freshness` counts non-object health rows as malformed and reports the missing source identity. Focused operations/relationship suite passes 19 tests. Native connector failures, concurrency and restore remain open.
The full local harness passes 504 unit tests and 446 project checks; this does not close native failure/concurrency or operational restore proof.

### Explicit empty prior-snapshot receipt — 2026-09-25

`evaluate_run` now distinguishes an omitted prior snapshot from an explicitly
supplied empty snapshot. On failure, the latter reports that the prior state
was preserved without claiming any accepted rows; omission reports no
preservation evidence. The focused operations/relationship suite passes 21
tests. Native connector, concurrency, monitoring and restore acceptance remain
open.

### Freshness policy shape guard — 2026-09-25

`evaluate_source_freshness` now treats a non-mapping policy and non-mapping
policy entries as unhealthy diagnostics instead of raising during evaluation.
`evaluate_run` rejects the run and retains the supplied prior accepted records.
Regression coverage includes `None` policy entries and a list in place of the
policy map. The focused `test_grants_relationships_operations.py` suite passes
24 tests. This is local fail-closed evidence; operational policy approval,
native connector failure, concurrency, monitoring and restore acceptance
remain open.

### Strict source-health observation timestamps — 2026-09-28

The source-health evaluator now reuses the grants registry's strict offset-bearing RFC3339 parser. Space-separated timestamps, minute-only values, naive local timestamps and compact offsets are rejected as invalid rather than entering freshness calculations. Regression cases pass in the focused operations/relationship suite. This is local validation only; it does not establish approved source ownership, schedule health or native monitoring.
