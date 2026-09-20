# Review: Repair and prove PubMed plus DORA ingestion

Review status: in progress; local activity-resource tranche reviewed, native RIMS acceptance remains open.

## Evidence
- `private/ops/2026-09-15-dax-readback.json`: Live DAX query readback from isolated development model `{{ISOLATED_MODEL_ID}}`.
  - Publication counts: PubMed 1,261 rows; DORA 709 rows.
  - Native ingestion readiness: 0 failed audits (9 PubMed audit rows, 5 DORA audit rows). Status `READY_FOR_STORAGE_VALIDATION`.
  - Metadata structure readiness: 0 chunk/key/encoding failures. Status `METADATA_STRUCTURE_VERIFIED`.
  - Retention validation: 10/10 tests passed (`TRUE`).
  - Stored metadata validation: PubMed 1,261 records (32,289,819 characters), DORA 709 records (2,603,915 characters), KeysMatch=true, MetadataValid=true, PayloadIdentitiesMatch=true.
  - Retained history keys: 1,970 total rows (PubMed: 1,261, DORA: 709), batch ID `ae1a84a1-792c-471d-8c8b-b0d3f159cef7`.
- `private/ops/2026-09-14-native-refresh.json`: Refresh correlation and stored archive verification.
- `private/ops/2026-09-14-powerautomate-query-proof.json`: Power Automate commit readback verification.

## Open notes
Known local defects are listed in docs/WEB_FIRST_FINDINGS.md. Existing Python policy tests are not native M tests.

## Local preparation, 2026-09-12

The historical DoRA collection and PubMed registry were reconciled locally; see [source evidence](../../../docs/HISTORICAL_SOURCE_RECONCILIATION.md). Complete local candidate exports and review exceptions are recorded. No native task is closed: T10 isolation, live execution and model/export readback remain unverified.

Subsequent source identity review resolved all eight flagged cross-source groups using archived citation/identifier evidence. Ten scope/attribution exceptions remain. The identity ledger and aliases are preserved; 148 tests pass. This is local source progress, not native acceptance.

## F02 source repair — 2026-09-12

Outcome-linked contract revision: canonical output must retain its full schema when PubMed is empty, including a DORA-only or both-empty result. Replaced first-record schema inference with an explicit nullable `PublicationType`; both record lists are constructed against it and combined with the same type. Missing required fields still raise an error rather than being silently converted into null values. Source exceptions are not caught or converted to zero results. Rebuilt `audit/model.snapshot.json` and generated model TMDL from the source. The schema regression check failed before the repair and passes after it, comparing all output fields/types against the semantic model. This check does not execute M.

Reviewed runtime-manifest change is limited to the canonical M file and its generated model TMDL representation. Native verification remains false and other known defects remain open. Native PubMed-only, DORA-only, both-empty and source-failure execution is still required; gateway evaluation currently prevents those tests. No tenant research-model change is claimed.

## F03/F04 conservative matching and feed-date repair — 2026-09-12

The old model reference automatically merged a unique title/year even when DOI/PMID contradicted it or neither title nor year existed. Seven new behavioral regressions failed on that implementation. The repaired Python reference and canonical M use exact normalised DOI/PMID candidates; conflicting, malformed or multiple candidates are preserved for review. A title/year match only labels a review candidate. Empty titles/unknown years cannot establish a match. The title-only synthetic fixture now expects separate records, with independent tests proving identifier-backed merging. This intentionally changes candidate counts; it does not rewrite the separately reviewed durable registry or its identity ledger.

The DoRA RSS M retains raw `pubDate` as `PublicationDateRaw`, explicitly assigns unknown precision, and leaves publication date/year/month empty until corroborated. The canonical output preserves that uncertainty. A valid empty channel now produces a typed empty item table, while invalid channel/item schemas still raise errors. Removed the unverified `Text.RemoveDiacritics` dependency; title normalisation is a conservative ASCII comparison used only for review hints. A rolling RSS notice explicitly disclaims full historical coverage. F05 historical persistence remains an independent requirement; the existing complete private history/registry is not replaced by this RSS helper.

Intentional generated/runtime changes: canonical M, DoRA M, generated model TMDL and audit snapshot. Local validator vocabulary is updated to require the conservative policy instead of title-only merging. The runtime manifest is revised only for these reviewed files; native verification remains false. Native empty-source, identifier, date and source-failure matrices remain unexecuted because of the documented Power Query gateway failure. No production or development research-model deployment is claimed.

Review also removed unconditional CHHHS facility attribution from unmatched RSS rows: an explicit nonempty affiliated-author statement is required for the HHS bridge. Rows without that evidence remain in the canonical register with attribution-review status. A linked DoRA record no longer overwrites PubMed attribution with a stronger unsupported claim. This does not adjudicate the outstanding human scope decisions in the durable registry.

## Native source milestone — 2026-09-13

After persisted legacy SQL table removal in T10, source-free M and the actual ReportingWindow query evaluated successfully. A real DORA Web.Contents/XML staging query returned four feed items and four raw metadata columns using an anonymous public cloud connection with no gateway. This is finite live RSS coverage, not canonical reconciliation, full historical coverage or durable first-observed retention. Implementation: `../../../powerquery/DoraSourceObservations.m`. Private receipts: `private/ops/2026-09-13-native-cloud-repair.json`.

Runtime-baseline review: the only added runtime file is DoraSourceObservations.m. It stages the approved public RSS URL using fixed-root Web.Contents with a two-minute timeout, checks channel/item structure, preserves raw description/pubDate and allows a typed empty feed. It does not merge identities, infer publication dates, assert historical coverage or load fixtures. Native preview returned four live items. Its hash was added to the drift manifest; existing runtime hashes and native_verified=false were preserved. The local generated release model is unchanged and does not yet consume this incremental staging table.

## Native parser validation

fnParsePubDate compiled in the actual Power Query editor; all ten synthetic date cases passed, including null/empty, year/month/day, leap-day, ISO date, range and invalid-month inputs. The entire temporary test query was replaced with the real DoraHarvest query before saving. DoraHarvest then evaluated four live rows and eleven metadata columns. It now references DoraSourceObservations rather than declaring a second source expression. This does not promise a persistent engine cache or historical store.

Regenerated the local model snapshot and TMDL to include the staging expression before its consumer. Reviewed runtime changes are limited to DoraHarvest.m and model.tmdl; updated their drift hashes while preserving native_verified=false. Full canonical/source acceptance remains open. Private evidence: `private/ops/2026-09-13-native-parser-validation.json`.

Save status: Power BI requested identity verification while applying the parser changes. Continue returned to the editor briefly, then the same identity-verification prompt reappeared. The editor is preserved for user sign-in; parser persistence remains unverified. Native preview evidence is valid but is not a saved-model claim. PubMed execution also awaits the requested operational NCBI contact email. Local validation: 158 tests, 214 project checks, PASS_LOCAL_ONLY.

Anonymous PubMed correction: NLM permits calls without an API key below three requests per second per IP; email is suggested identification, not authentication. Blank/null contact now omits email; supplied malformed contact still fails. The parameter is optional; 1.1-second pacing and retry handling remain. Reconciled the reviewed attribution-evidence changes plus fnNCBIJson in the drift manifest, preserving native_verified=false. Native execution is not verified. Source: https://www.nlm.nih.gov/dataguide/eutilities/utilities.html

## Continued ingestion deployment (2026-09-13)

Native anonymous ESearch and full EFetch succeeded. The initial 1,254-PMID source pass passed nine native M audits but failed 34 post-import metadata length checks. Revised UTF8-HEX chunks, historical scope-search coverage, full-author parsing, PubMed publications/evidence tables and historical DORA queries were applied via the web TMDL editor. Refresh started, then browser policy verification denied further access. Final native ingestion acceptance is open. See docs/PROTECTED_DEVELOPMENT_BASELINE.md and the ignored continuation receipt. Resume with refresh readback and config/native-ingestion-storage-check.dax; do not infer completion from the successful TMDL Apply response.

### Automatic updates implementation, 2026-09-13

User clarified that dynamic updates are required. Added the end-to-end daily collection/retention/refresh plan, generated bounded source extraction queries and linked daily/monthly blueprints. Historical ZIP uploads are backfill only. Local checks: 161 tests, 235 checks, PASS_LOCAL_ONLY. Native query acceptance and cloud-flow creation remain open: Power Automate control access was denied by browser policy verification. The last successful Power BI observation showed refresh processing, not completion. See docs/DYNAMIC_UPDATE_IMPLEMENTATION.md.

### Retention merge source review

Added only fnRetainSourceObservations.m to the frozen source manifest. Outcome: source-scoped upsert retains absent feed records, preserves first observation and isolates review state. Reviewed explicit schema/JSON/uniqueness/time validation, anti-join retention and the outer guard needed for empty batches under lazy M evaluation. Nine native fixture cases are prepared but unexecuted; native_verified remains false. No generated model or cloud deployment changes are included in this addition.

### Committed-history reader preparation, 2026-09-14

User explicitly requested committed-history model wiring and native rollover/interruption tests. Added fnReconstructMetadata, fnReadCommittedHistory and RetainedSourceObservations to the source baseline only after verifying every existing baseline hash unchanged. The reader ignores uncommitted pages, rejects missing committed files and absent commits, reconstructs ordered UTF8-HEX with exact length/index checks and UTF-8/JSON validation, reconciles manifest keys and folds committed observations through the existing non-deleting retention merge. The SharePoint query requires private site/folder parameters and scopes reads to the exact approved archive folder. Eight isolated native fixtures cover reconstruction, rollover, interruption and malformed commits. These new M definitions are not yet deployed or natively verified; no live report rebind or committed marker has been written. Native validation remains required before promotion.

### Native retained-metadata validation, 2026-09-14

Applied the three retention functions and isolated RetentionValidation table in the protected development model. Native Power Query exposed and corrected a format mismatch during source review: both ingestion sources serialize full metadata as arrays of records; the decoder must accept structured arrays as well as objects. Scalar JSON remains rejected. All ten isolated native tests passed, including Unicode/object/array roundtrip, missing-key/page rejection, rollover and interruption. This is native preview execution, not yet processed-model acceptance.

Created and authenticated the SharePoint archive connection with Organizational privacy. The connection-only file query is scoped to the exact approved source-archive folder. Native full stored-metadata reconstruction passed for 1,261 PubMed records (32,289,819 JSON characters) and 709 DORA records (2,603,915 characters), with exact archived publication-key parity and source-specific record structures. Added fnValidateStoredMetadata as a read-only validator; it never writes commits. Reviewed only its addition and the decoder correction into the frozen baseline, preserving native_verified=false. No commit manifest or production report rebind is claimed. Private evidence: private/ops/retention-native-tests.json.

### First-commit writer preparation

Prepared scripts/build_native_commit_package.py and successfully imported the private manual bootstrap package as a new development flow. It is explicitly operator-assisted for the verified first batch, not unattended generation acceptance. A native Power BI query must prove all ten tests and both complete stored-metadata totals before a manifest can be written, followed by exact file readback. No flow run or commit promotion has occurred.

The Power Query Save UI reported a busy-pane timeout on onFlowCommitted. A separate native model session explicitly reported an ongoing refresh; this is not evidence the server save failed. The running refresh was preserved, with the second session switched to view-only. Await the terminal native result rather than restarting the operation.

### Payload identity binding prepared

Extended the stored-metadata validator to bind each archive key to the identifier inside its reconstructed payload: PubMed MedlineCitation/PMID and DORA dc.identifier.uri (normalizing the previously accepted HTTP URI to HTTPS). Missing or ambiguous embedded identities fail acceptance. The commit package builder now requires PayloadIdentitiesMatch. This extension is local-only while the model's existing save remains in progress; it must be deployed and natively tested, and the imported commit flow updated before execution. Reviewed only the changed validator hash into the drift baseline. Native acceptance remains false.

### Retained reporting projection draft review (2026-09-14)
Added six M definitions for offline retained PubMed/DORA parsing, latest committed summary selection and PubMed bibliography restoration. The parsers preserve the existing full-metadata extraction semantics, adapt serialized XML node lists, reject mismatched identities, and retain uncertain dates and affiliation evidence. The summary reader validates the manifest inventory and exact source key sets before selecting each latest observation. An explicit empty PubMed schema preserves the zero-source path. These additions are recorded in the drift baseline with native_verified=false; they are not deployed or certified. Eight isolated native parser cases are prepared, not yet executed. Complete live parity, retained facility mapping and long-text model/export limits remain open. The existing canonical consumers are unchanged until those gates pass.

### First accepted retained baseline (2026-09-14)
Native on-demand refresh completed at 19:46:57 Brisbane. Loaded DAX returned ten Passed=true retention cases and two stored-metadata rows with exact counts, character totals and KeysMatch/MetadataValid/PayloadIdentitiesMatch=true. The manual first-commit flow succeeded at 19:51:59 and returned COMMIT_READBACK_VERIFIED. Committed-history expression and key/date projection were accepted through TMDL. The next Power Query action was denied because the browser security policy check was unavailable; no bypass attempted. Reader execution, eight new parser cases, canonical history integration, live replay and subsequent-cycle retention remain open. This is one accepted baseline, not full retention completion.
## Current DoRA activity coverage review (2026-09-20)

The linked Queensland Open Data resource was checked through the public CKAN API. The latest active CSV datastore resource exposed 19 source columns plus the datastore `_id` key and 442 rows at observation time. A live collection attempt also established that `Project ID` is not unique; the source `_id` is therefore the activity-row identity. This is research-activity/project data, not publication metadata, so it must not be merged into the publication identity table.

Local implementation now includes `scripts/dora_activity.py`, `scripts/export_dora_activity.py`, `config/dora-activity-registry.schema.json` and `tests/test_dora_activity.py`. The collector discovers the current resource, pages all records, checks exact fields/count/unique source `_id`, and retains every source column plus provenance. The exporter produces a source-preserving CSV/JSON RIMS payload. Focused tests cover pagination, schema drift, source-field preservation, repeated Project IDs and provenance keys.

Native SharePoint list creation/import/readback and any RIMS report page remain open; no tenant write was attempted. Live source rows were not added to the repository.

## Conductor review — local activity tranche

Summary: the local DoRA activity implementation is source-preserving and fail-closed; the track is not complete because native RIMS persistence/readback is still outstanding.

- Plan compliance: **Partial** — tasks 11–13 are implemented; task 14 remains open by design.
- Style compliance: **Pass** — standard-library implementation, explicit errors, no credentials or live rows in source.
- New tests: **Yes** — five focused tests cover pagination, exact schema, schema drift, repeated Project IDs, source-key uniqueness, provenance and schema declaration.
- Test coverage: **Pass for local tranche** — live CKAN retrieval also returned 442/442 records and the complete 19-source-field-plus-`_id` contract.
- Test results: **Passed** — current canonical-clone full suite (363 tests, 8 skipped), 438 project checks, Conductor validation, and `PASS_LOCAL_ONLY` web-first contracts.

## Conductor review — identity hardening — 2026-09-21

Summary: the DoRA activity collector now fails closed when a datastore `_id` is boolean or structured, instead of coercing arbitrary values to strings and treating them as row identities. Invalid expected record counts are also rejected before count reconciliation. The original scalar source value remains preserved in the accepted record.

- **Plan compliance:** Partial — local source discovery, preservation and validation remain implemented; isolated SharePoint list creation/readback and report integration remain open.
- **Verification checks:** Focused DoRA tests passed; full canonical-clone suite passed (355 tests, 8 skipped); project validation passed (438 checks); web-first contracts returned `PASS_LOCAL_ONLY`; `git diff --check` passed.
- **Finding and fix:** `validate_records` previously accepted values such as `True`, `{"row": 7}` and `[7]` after `str()` coercion. Commit `12798092b64de6d420904c7cd77d589829076f1c` restricts source identities to non-boolean scalar string/integer values and adds regression coverage.
- **Residual acceptance:** native SharePoint target/schema/row-key readback and RIMS report integration remain unproven. No tenant mutation was made.

Review fix applied: `tests/test_webfirst.py` now asserts that
`config/native-canonical-retained-partitions.tmdl` is reference-only and
explicitly scoped to the isolated development model; it cannot silently drift
into shared-model table creation. Native application and readback remain open.

Review finding applied: the first draft treated `Project ID` as unique. Live readback disproved that assumption (375 distinct values across 442 rows), so identity now uses the resource-scoped source `_id` and preserves `Project ID` unchanged. No unresolved local findings remain. Native list creation/import, complete row/column readback and report integration remain the next acceptance gate.

## Native continuation check — 2026-09-20

The authenticated Chrome inventory showed the public DoRA dataset and an existing OneDrive tab, but the SharePoint tab could not be rebound because it is already owned by a prior CUA browser session. A later authenticated-looking SharePoint/Loop tab also timed out during binding, after which the browser inventory exposed no surfaces. No list creation, upload or tenant write was attempted.

## Playwright CLI continuation — 2026-09-20

An earlier Playwright snapshot found only two CHHHS publication DEV flows and
captured the pre-repair failure in the active history-commit flow. It also checked
the unapproved `eHealth-comm-test` site, which contained neither `DORA Activity
Registry` nor `Publication Registry`. That snapshot is superseded for current
execution by the tested runs below and is retained only as historical evidence.

This is stronger native evidence for the connector/list mismatch, but it does not
identify the approved RIMS SharePoint site or authorize creating a list on this
test site. No tenant mutation or DoRA row upload was performed. Native acceptance
therefore remains open; the next executable action is to use the approved RIMS site
identity, then create or locate the isolated list and read back its schema and
source-key coverage.

The second flow listed in the same environment, `CHHHS Publications - DEV manual
ingestion validation`, was initially observed Off and its details page exposed only
the owner-facing Power BI connection summary. Its action-level run readback was
required to determine the actual SharePoint target.

## Current platform flow test — 2026-09-20

The two listed publication DEV flows were tested through the authenticated
Power Automate UI. The active history-commit flow now completed Power BI read,
manifest parse, validation, OneDrive archive write, archive readback and final
verification successfully. The prior failure was corrected in both text-valued
failure branches; the live readback showed no Flow Checker errors or warnings.

The manual-ingestion flow was temporarily enabled only for its instant/manual
test, then restored to Off. Its current run completed the Power BI query,
SharePoint `Get items`, `Condition Is New Publication` and the True-branch
`SharePoint Create item` successfully; the False-branch update was skipped for
the new row. The SharePoint action read back HTTP 200 from the configured
`Publication Registry` list and the visible list UI exposed the publication
schema and populated rows.
The private receipt is `private/ops/2026-09-20-powerautomate-publication-flow-tests.json`.

This proves current DEV/manual flow execution and list readback, not unattended
production scheduling, organisation-wide site migration, or full canonical
registry reconciliation. A controlled replay again took Create rather than
Update; the blank SourceKey filter observed in action readback leaves duplicate
prevention/idempotency open.
