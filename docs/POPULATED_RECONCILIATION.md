# Populated saved-generation reconciliation — 24 October 2026

**Packet populated; overall result BLOCKED.** Existing saved native evidence
identifies one genuinely correlated historical model/export generation for
September2026. No new collection, registry write, refresh, export or delivery ran.
This is not a current24October whole-system snapshot.

| Available stage / comparison | Result |
| --- | --- |
| Completed isolated model refresh and paginated query | 1,341publication keys;32saved query receipts share the retained refresh request; before/after count probes agree. |
| Full export | 1,341keys match the model; no missing/unexpected keys; publication months agree. |
| September2026 monthly export | 14keys match the full-export month partition; no missing/unexpected keys. |
| Unknown publication months | 189remain in the full bibliography; none is silently assigned to September. |
| Candidate registry capture | 1,345keyed rows from its original successful native export run; retained as uncorrelated evidence, excluded from passing stage comparisons. Blank placeholders were excluded by that historical query. |

[Aggregate machine-readable result](../config/populated-reconciliation-summary.json).
The actual private packet, result, input hashes, exact key sets and generation/run
identities are under `private/ops/2026-10-24-whole-system-reconciliation/` in the
primary evidence checkout. `build_saved_packet.py` records the offline adaptation;
outputs use create-only writes. No raw data or actual tenant IDs are copied to Git.

## Why this generation is correlated

The saved `full-monthly-export-acceptance.json` identifies the generation, source
snapshot, completed model refresh and extraction-contract hash. The selected
T14 `native-extraction-receipt.json` points by exact SHA256 to the accepted
OpenAlex bridge receipt, which preserves all40,230canonical values. The terminal
model history has the same refresh request as all32native query receipts. The
full/monthly envelopes repeat that generation, source snapshot, refresh and query
contract. This establishes the model/export lineage; an enrichment bridge receipt
alone does not establish complete primary publication source membership.

The adaptation checks full paginated row queries against14independent full key
query pages and independent count probes, verifies each envelope's generation and
page chain, and compares exported CSV keys against the saved envelopes. Both CSV
file hashes match their manifests and the native downloaded-byte receipts. A
separate original key hash matches each export. CSV empty month cells are decoded
as null according to their retained export representation; no unknown date is
filled. Native saved-byte/runtime receipts are reused, not rerun.

The pinned identity digest in the packet describes **exact comparison of existing
CanonicalKey values** only. It does not assert historical source-merging policy
qualification. No PUB/PMID/DoRA key migration or title/DOI/person inference is used.
The model's derived source memberships are not presented as independent raw-source
captures or fabricated canonical admission evidence.

## Exact missing captures and disposition

| Missing outcome | Evidence needed to close it | Existing material / restriction |
| --- | --- | --- |
| Complete accepted source-membership capture | Complete paged accepted PubMed/DoRA publication source members for the selected frozen source lineage; original exact SourceKeys, accepted commit/completion marker, acquisition/cutoff times, query/schema versions, artifact bytes/hash and independent counts. | The accepted bridge concerns enrichment and preservation. Do not infer raw-source membership from model provenance, copy a later source generation into this one, or reharvest merely to complete this packet. First locate retained committed member exports/markers. |
| Evidenced source → canonical membership map | Every selected accepted SourceKey mapped exactly once to an existing canonical publication, including source overlaps and explicit correction/uncertainty provenance. Independent canonical count and durable accepted commit evidence must reconcile all1,341model keys. | The model has a usable canonical-key projection; it is not an independent accepted source-to-canonical map. Do not infer merges from equal titles or DOI alone. Keep distinct source aliases and uncertain author/date facts. |
| Selected-generation registry bridge and comparison crosswalk | Complete registry capture tied to this source/commit/refresh lineage, or an exact saved field/key preservation chain demonstrating that connection. Retain original durable keys, SourceKeys, item IDs, reviews, blank stubs, independent totals and complete paging. Supply the exact comparison identity crosswalk and explain any secondary representations. | Candidate1,345keyed rows lack that explicit correlation in the selected receipt. Its original run identity is retained rather than replaced with the selected model generation. Historical crosswalk attempts and count agreement cannot silently establish membership or authorize cleanup. |

All three gaps are evidence/correlation gaps, not automatic requests for new runs.
The recent1,651-row registry read used for147-field disposition belongs to a later
observation; it must not substitute for this historical capture without a verified
preservation chain. Likewise the grants model refresh and running Crossref
operation cannot be used to fill missing publication stages.

## Interpretation and next handover

The comparator now evaluates available model/full/monthly edges even when source
or canonical membership is missing. Missing stages still block the result, and
`native_acceptance` remainsfalse. This avoids both a false all-stage pass and an
empty result that conceals useful downstream parity.

First recover the two independent membership captures and the registry bridge
from saved owner evidence. If a historical capture cannot be established, record
that limitation and use a later owner-authorised coherent completed generation;
never relabel old artifacts to manufacture one. Full metadata/source-set/curated
correction parity, report rendering, runtime preservation, schedules and business
acceptance retain their separate gates. The144uncertain source/curated pairs
remain explicit differences under [their verified disposition](PUBLICATION_SOURCE_DISPOSITION.md).
