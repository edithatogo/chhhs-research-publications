# Ingestion efficiency review — 24 October 2026

This review covers fresh native definitions for 14 collectors and the register
ingestion actions. Static findings are not runtime capacity measurements. The
Crossref original run and archives retain their separate scope and terminal gate.
The selected strategy is targeted discovery, immutable archive reuse, compact
progress and measured batch admission. It does not claim exhaustive institutional
coverage or that every connector is optimally tuned.

## Findings and priority

| Collector | Observed design | Action |
| --- | --- | --- |
| Crossref | Broad original queries and repeated payload history; retained execution still Running | Deploy the revised 19-query daily/baseline pair only after actual terminal reconciliation; measure real continuation and capacity. |
| PubMed | Two ESearch inventories, batched XML fetch, full response alias before archive | Removed only the redundant XML string copy through guarded same-ID PAC update; exact native clientdata readback passed. Keep both inventory checks and exact archive readback. |
| DoRA publications | Before/after collection inventories and fresh full HTML per publication | Removed only the redundant HTML string copy through guarded same-ID PAC update; exact native clientdata readback passed. Prior successful schedules took 89.77 and 177.91 minutes. Per-record retrieval is the next workload to measure. |
| DataCite | DOI batches of 20 plus discovery paging and verified-prefix recovery | Inspect repeated raw-envelope copies and query yields against real page/history sizes. Do not weaken accepted recovery or change broad scope solely to reduce counts. |
| ClinicalTrials.gov | Two discovery inventories with version checks and separate requested-ID detail acquisition | Keep Stopped; qualifying discovery does not make six configured detail IDs exhaustive trial-detail coverage. Measure the discovery and detail phases separately before activation. |
| ARDC | OAI-PMH change windows, seven-day overlap, 28-day full reconciliation; XML parsing and growing identifier sets | Profile full versus incremental history. Prefix recovery is constrained by resumption-token lineage. Do not silently reuse expired/changed tokens or remove tombstone handling. |
| ROR | Official release identity/checksum and native archive-version check skip unchanged releases | Retain this design; no extra acquisition needed to repeat already accepted replay evidence. |
| OpenCitations count | Accepted cached manifest and retained-entry reuse, serial bounded DOI scope | Keep Stopped. Raw content is embedded in manifest entries and retained-entry filters repeat per DOI. A pointer/index migration must update existing assertion consumers together. |
| OpenCitations metadata | Same cached architecture; multiple/no-hit observations retained | Same compact-manifest migration candidate, preserving unresolved matches and provenance. No automatic provider rerun. |
| OpenCitations incoming citations | Cached DOI responses; bounded observations | Same migration candidate. Do not recursively enqueue citing/cited works. |
| DoRA activity | Two full CKAN reads and before/after package checks | Only replace the second data pass after a qualified provider version contract supplies equivalent drift detection. Preserve this other lane's ownership. |
| QGIP | Two complete data reads plus package/resource/schema checks | Repeated acquisition merits measurement; metadata timestamps alone are not proof that datastore rows did not change. Preserve owner. |
| ARC awards | Two complete page traversals | Consider a qualified immutable release or snapshot route before changing consistency checks. Preserve owner. |
| NHMRC and MRFF | Source-page discovery and workbook acquisition with after-page check | Assess conditional retrieval and release identity. An unchanged URL is not unchanged workbook content. Preserve owner. |

The register flow consumes OpenAlex context through an existing model query;
there is no separately named OpenAlex cloud collector in the fresh name inventory.
Its model refresh/acquisition path has not been performance-audited here. No model,
report, grants-owned flow or schedule was changed by this review.

## Implemented response-copy reduction

`scripts/prepare_ingestion_low_copy.py` accepts an exact definition hash and explicit
action paths. It replaces a plain `string(body('HTTP_action'))` Compose reference
with the identical expression at its consumers and reconnects successful action
dependencies. It rejects altered preimages, structured envelopes, status consumers,
non-success dependencies and tracking metadata. Archive serialization, provider
requests, scopes, verification, checkpoint logic and triggers remain unchanged.

The native PubMed graph now has 57 cards and DoRA publications 108 cards. Each
executed batch/record avoids one response-copy action and its input/output history;
this is structural evidence, not a measured speedup. PAC stored clientdata matched
the complete supplied candidate exactly for both. Independent Flow API readback
preserved Started, original references, concurrency one and daily Brisbane schedules
(PubMed 01:30; DoRA 04:30). Physical connections were compared unchanged.

DoRA's previous scheduled durations and PubMed's approximately two-minute durations
are historical baselines. Do not compare unlike source sizes as performance gains.
No provider acquisition or new full collection run was started for this change.
Use the next existing natural schedules for affected-path evidence, then compare
records, bytes, runtime and action/history usage before any tuning claim. Keep
preimages and exact guarded rollback inputs in private evidence. Native versioned
field-guide/diagram publication for these two small graph changes remains pending.

## Next measured decisions

1. Finish original Crossref terminal reconciliation and the revised scope's two
   actual bounded batches, unfinished-window resume, archive reuse and checkpoint
   isolation. Preserve old raw partitions; do not relabel old coverage.
2. Compare one natural PubMed and DoRA occurrence after adoption with accepted
   baselines. Investigate provider wait, storage/readback and per-record iteration
   separately. No repeated unchanged test generations.
3. For DoRA, qualify HTTP validators or a reliable change inventory against retained
   pages before skipping detail requests. Bootstrap unchanged versions only when
   current source evidence supports reuse; retain periodic full reconciliation.
4. For OpenCitations, design versioned pointer manifests with native file identity,
   length, ETag and independent hash evidence. Preserve legacy manifests and prove
   consumer/replay compatibility before migration. These small accepted batches do
   not currently show Crossref-scale capacity failure.
5. Budget requests and history across active flows. Do not enable additional full
   reconciliation schedules or parallel acquisition solely because a connector is
   configured. Activation requires a complete maintained input scope and measured
   capacity, within the user's existing authority.
6. If reduced Crossref or DoRA workloads still exceed measured capacity, prepare a
   separate worker migration decision: Power Automate orchestrates compact work
   references; a worker acquires, hashes and processes bulk payloads. No new service,
   licence, connection or runtime deployment is implied by this review.

Current provider/platform guidance supports caching, smaller retrieval segments,
source filtering and reduced history payloads:
[Crossref API guidance](https://www.crossref.org/documentation/retrieve-metadata/rest-api/tips-for-using-the-crossref-rest-api/),
[Power Automate relevant data](https://learn.microsoft.com/en-us/power-automate/guidance/coding-guidelines/work-with-relevant-data),
[platform limits](https://learn.microsoft.com/en-us/power-automate/guidance/coding-guidelines/understand-limits).

Private native definitions, preimages, saved candidates, rollback and verification
receipts are under `private/ops/2026-10-24-ingestion-efficiency/` in the primary
checkout. The review does not close E01 or claim new operational acceptance.
