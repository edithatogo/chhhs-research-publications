# Review: Repair and prove PubMed plus DORA ingestion

Review status: complete.

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
