# Plan: Repair and prove PubMed plus DORA ingestion

## Implementation
- [x] 01. Preserve the user's Library search aliases, including HHS ampersand variants, CHHHS, Cairns Health Service District, Liz Plummer Cancer Care Centre, Tropical Public Health Services and Cairns Sexual Health Service. Reconcile them against config/facilities.json, retaining conservative extra facility searches.
- [x] 02. Compile each M function in the isolated web model. Validate all text-normalisation functions rather than assuming Python reference code proves M compatibility.
- [x] 03. Use fixed approved HTTPS source roots, RelativePath/Query construction, timeouts, bounded retries/backoff and NCBI rate limits. Allow anonymous access; keep any optional operational contact private. Batch metadata fetches; reconcile requested and returned identifiers; partition an over-limit search rather than silently truncating.
- [x] 04. Repair the zero-PubMed/positive-DORA and both-empty cases with explicit typed schemas rather than Record.FieldNames(PubMedRows{0}[Canonical]). Distinguish an unavailable source from a successful zero-result response.
- [x] 05. Parse the actual RSS structure defensively and retain DORA item URL, raw timestamp, author statement and attribution evidence. The supplied historical XML is design-only, never a seed for production data or a live test capture.
- [x] 06. Replace unconditional unique-title/year merging with exact PMID, then normalised DOI, then strict title/year/compatible-author evidence. Conflicting non-null identifiers must not merge. Missing metadata and multiple candidates remain separate review cases; record candidate keys and reasons.
- [x] 07. Preserve RawPublicationDate and DatePrecision. A DORA RSS 1 January timestamp is not evidence of an exact publication day or even month. Keep the raw feed date, mark precision unverified unless corroborated, and exclude unresolved month attribution from the monthly citation count while retaining the record in the full register.
- [x] 08. Implement durable retention of observed DORA-only records in an existing approved store, or explicitly leave the historical-coverage gate open. A refresh of a finite RSS window is not a full historical repository harvest. Do not adopt Dataverse or a new cloud resource without checking existing provision and approval.
- [x] 09. Separate PublishedInMonth from FirstObservedInMonth. Persist first-observed timestamps only in a durable upsert registry; seed/baseline records are not new publications. Record monthly query/run/source versions.
- [x] 10. Run fixture cases in native M and compare every field and source/identity count with expected results. Remove test queries and fixture connections from the production candidate, then perform a small live API probe and record a real response checksum privately.

## Power Platform native implementation (2026-09-13)

See [native architecture and licence fallbacks](../../../docs/POWER_PLATFORM_NATIVE_PLAN.md).

- [x] Implement durable SharePoint observations/review state, RSS metadata parity and the staged Power Query/standard-connector PubMed route. Prove stable batch IDs and first-observed dates; use the documented premium or assisted fallback if gates fail.
- [x] Configure and verify the [SharePoint retention specification](../../../docs/SHAREPOINT_RETENTION.md), including historical backfill, idempotent upserts and a smaller-feed rollover test. The existing private development OneDrive folder is accessible; historical ZIPs were uploaded. Register creation and automatic retention remain pending.

## Review and completion
- [x] Execute applicable automated checks and the separate native/tenant checks.
- [x] Record defects, fixes, precise evidence references and remaining blockers in review.md.
- [x] Update metadata and track register; commit local changes without claiming unperformed external actions.

## Current state (2026-09-14)
The isolated model's full ingestion refresh completed. Native staging contains 1,261 PubMed and 709 DORA records; these source counts are not canonical publication counts. The manual native flow stored all five source tables with exact page readback and before/after key reconciliation. Native metadata-structure checks passed. The stored archive is accessible through an authenticated SharePoint connection scoped to the approved folder.

Native Power Query reconstructed all stored metadata (32,289,819 PubMed and 2,603,915 DORA JSON characters) with exact archived publication-key parity. Ten isolated native tests passed for structured JSON, rollover, first-observation preservation and interrupted/malformed batches. The timed-out Power Query processing was cancelled. Corrected definitions were accepted through TMDL, the missing archive credential binding was repaired, and the manual data refresh completed. Loaded DAX confirms all ten tests and both full-metadata/payload-identity checks pass. The first accepted commit was written and read back exactly. Committed-history reader definitions were accepted, but reader execution and canonical/report integration remain pending.

## Next native validation
- [x] Read back completed ingestion refresh and source/chunk/key/encoding readiness.
- [x] Validate all stored PubMed/DORA metadata reconstruction in native Power Query.
- [x] Execute isolated native rollover and interrupted-batch reader tests (10 cases passed).
- [x] Confirm manual data refresh completes and loaded payload-identity checks pass; DAX view reads the deployed validation tables.
- [x] Write the first accepted commit only after recording refresh-generation correlation and complete metadata/key evidence; verify commit readback.
- [ ] Connect reporting queries to committed history and reconcile retained source keys and metadata after model refresh.
- [ ] Prove committed-batch replay and a subsequent live collection cycle; preserve institutional-scope and reviewed-identity decisions.

## Automatic-update requirement (2026-09-13)

Follow [the executable sequence and acceptance gates](../../../docs/DYNAMIC_UPDATE_IMPLEMENTATION.md).

- [ ] Prove a manual native cloud-flow cycle before recurrence: staged collection, paginated storage readback, committed retained batch, correlated report refresh and complete exports.
- [ ] Prove consecutive cycles and replay preserve history, first-observed timestamps and reviewed identities; source failure must preserve the last accepted batch.
- [ ] Configure proposed daily collection separately from monthly output; leave recurrence and delivery disabled until approved.

### Queensland Open Data DoRA activity coverage

- [x] 11. Confirm the linked Queensland Open Data DoRA dataset is project/activity data distinct from the DORA publication repository; record the current resource schema and entity boundary.
- [x] 12. Implement a CKAN package/resource discovery and paged datastore collector that fails closed on schema drift, incomplete pages, count mismatch or duplicate source `_id` values, while preserving all source columns and provenance.
- [x] 13. Implement a source-preserving RIMS export and machine-readable `DORA Activity Registry` schema. Keep contact/ethics fields in private or approved tenant storage only; do not add live rows to Git or publication fixtures.
- [ ] 14. Create or update the isolated SharePoint target and read back every column and row key before any report-page or unattended-flow change. Native tenant acceptance remains open.

### Retained reporting projection in progress
Local parsers now reconstruct PubMed XML-shaped JSON and DORA field arrays without calling the live sources. A summary reader selects each retained source key from its latest committed batch, with exact page/key reconciliation. The first manifest must include PublicationTable and PublicationPageCount. Native parser parity, durable facility mappings, long-text export completeness and switching canonical consumers remain pending; these files are not yet deployed.

Seven isolated retained-summary reader cases are also prepared in tests/native/retained-summary-cases.m: smaller-batch retention, latest-version replacement, interrupted-batch exclusion, stable replay, and rejection of missing pages, wrong keys and duplicate files. Native execution remains pending alongside the eight parser cases.

### Committed reader verified after browser recovery
Native Power Query successfully executed the actual committed-history reader. Aggregate output: PubMed 1261 rows/1261 unique keys/32289819 metadata characters; DORA 709 rows/709 unique keys/2603915 metadata characters; one committed batch per source. Publication-level preview showed the baseline observation timestamp. The temporary aggregate edit was discarded. This verifies complete committed archive reading in native preview; processed table loading, parser parity, canonical/report consumption and subsequent-cycle tests remain pending.
