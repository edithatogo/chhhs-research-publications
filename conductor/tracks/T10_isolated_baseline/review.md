# Review: Protect the existing report and prove an isolated write
 
Review status: complete.
 
## Evidence
- `private/ops/original-pbix-backup.json`: Original report/model PBIX downloaded and backed up outside repository.
- `private/ops/isolated-baseline-observation.json`: Development report/model ID separation confirmed (`{{ISOLATED_MODEL_ID}}` vs production `{{PRODUCTION_MODEL_ID}}`).
- Canary measure creation, save, reload persistence, and subsequent rollback reload verified cleanly.
 
## Open notes
Power BI web changes can autosave. Report-only copying is not sufficient protection. Isolation to separate development semantic model enforces protection.
 
## Incremental native execution review — 2026-09-13
 
Verified baseline checkpoint immediately before isolated table removal. Reload confirmed zero inherited tables; Power Query Queries [0] confirmed persisted query removal. Source-free TRUE evaluation succeeded. Replaced probe with actual ReportingWindow; native dates, save/load and post-reload three-column table verified. Isolated target verified. See `../../../docs/PROTECTED_DEVELOPMENT_BASELINE.md`.
