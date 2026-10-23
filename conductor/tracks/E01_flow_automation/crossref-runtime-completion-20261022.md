# Crossref controlled recovery qualification — 22 October 2026

The retained controlled recovery is terminal Succeeded. It reused three complete,
independently verified query archives and completed the remaining 24 queries in
the frozen source window. All 27 query expected/received/unique counts and page
counts reconcile. No incomplete cursor was reused.

The downstream lookup input contains exactly the retained 1,283 ordered DOI keys.
The archive retains 1,279 HTTP 200 responses, four explicit HTTP 404 outcomes and
the supported redirect results. Missing provider records remain explicit source
outcomes; they were not silently converted into successful metadata.

Independent native reads of the stored generation manifest and completion marker
are byte-identical: 453,919 bytes each, with the same SHA-256. The normal daily
definition, connections and Started state had already been restored exactly.
This accepted generation remains a delta with its existing baseline and frozen
change window; it is not a full reconciliation.

A later naturally queued occurrence failed its total-stability guard when the
provider's HTTP 200 result changed from 8,065 to 8,064 within query 3, page 6.
The guard retained that failed occurrence and blocked a new accepted generation.
The earlier controlled completion marker was independently rechecked afterward.
This observed natural occurrence is recorded in E08-F03; no failed guard was
waived and no further recovery run was submitted merely to obtain a green result.

Private evidence under `private/ops/2026-10-21-e01-runtime-qualification/`:

- `crossref-23-terminal-generation-acceptance.json`
- `crossref-23-post-all1283-terminal.json`
- `crossref-23-terminal-native-byte-bundle.json`
- `crossref-23-fresh-complete-inventory-summary.json`
- `crossref-23-successor-source-drift-diagnosis.json`

This closes the retained controlled Crossref reconciliation. Later natural
operation remains E08; broader provider-specific implementation tasks remain in
E01 unless separately completed.
