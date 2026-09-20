# Validation report: corrected research project

Date: 11 September 2026. Scope: local source correction and regression checks.

| Check | Result |
|---|---|
| Python unit/reference-policy tests | 49 passed |
| Local project contract checks | 222 passed; 0 failed |
| Rebuilt pages / visuals | 4 / 41 |
| Visual field projections checked | 58 |
| Runtime project files scanned | 53 |
| Old employment fields and hidden filter regression | No matches in replacement runtime files |
| Old employment binary model/cache in new project | Not included |
| Deliberate legacy-field / hidden-filter / old-cache mutations | Rejected by regression tests |
| Old adapted PBIX passed to saved-file checker | Rejected, as expected |
| Native Power BI Desktop, M/DAX and render checks | NOT RUN |
| Live PubMed harvest | NOT RUN |
| Tenant refresh/export and monthly distribution | NOT DEPLOYED |

The local validator parses JSON, checks structural contracts, resolves model references, scans for legacy artefacts and checks M lexical balance. It is **not** full transitive Microsoft JSON Schema validation or native engine execution. The Python date/API tests exercise explicit reference policies, not executed M expressions.

Review fixes included valid M quote escaping, all original active-model/cache exclusions, visible and hidden field replacement, duplicate-count prevention, valid 30/31-day dates, year-only and uncertain dates, supported model date range, guarded query/summary reconciliation, nonfatal phrase warnings and required NCBI contact configuration.

For individual checks and runtime SHA-256 values, see `validation-results.json`. Test names and results are in `unittest-output.txt`. Source evidence is in `source-audit.json`. The release receipt alongside the ZIP records clean working-copy extraction, Git integrity, bundle verification and deterministic regeneration. Native acceptance remains in T05.
