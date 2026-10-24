# Whole-system publication reconciliation preparation

Status: **prepared and populated for a saved model/export generation; whole-system acceptance blocked**.
See the [populated packet result and exact missing captures](POPULATED_RECONCILIATION.md). This joins source,
canonical publication, registry, model and full/monthly export key sets. It does
not start collection, refresh a model, update a row, run an export or issue content.

## Freeze one lineage before comparing

Select one completed, durably committed source generation from the existing owner
receipts, not the latest timestamps across unrelated snapshots. Freeze its actual
generation ID, source snapshot ID and identity-contract SHA256. Select an explicit
reporting month. Preserve source acquisition/cutoff time, source/query/schema
versions and accepted completion marker in the retained receipt. Later observation
or refresh times cannot substitute for source acquisition lineage.

The retained Crossref operation is still behind its terminal gate in the selected
checkpoint. The accepted grants refresh is a different domain/generation; it must
not fill a missing publication-model stage. Current operation state can change;
resolve the retained handle before dependent effects. Missing evidence does not
commission a repeat of an already accepted run.

[Preparation template](../config/generation-reconciliation.template.json) is
intentionally incomplete: UNSELECTED IDs, a placeholder digest, an illustrative
month and no stage captures. Copy privately, replace the lineage from actual
receipts, and populate only stages supported by existing evidence. Running the
unfilled template reports all six missing captures and cannot pass.

## Capture contract

`scripts/reconcile_generation.py` accepts one JSON packet with `schema_version=1`,
`generation_id`, `source_snapshot_id`, `identity_contract_sha256`, `reporting_month`
and a `stages` object. Each populated stage repeats the exact three lineage fields
and supplies:

- `data_kind: native_readback`, `complete: true`, `next_links: []` from full paging.
- `terminal_status: Succeeded`, exact `operation_ref`, `evidence_ref`,
  `query_version` and retained `artifact_sha256`. Each stage has its own operation;
  correlation does not mean pretending source/import/refresh/export share a run ID.
- `independent_expected_count`, obtained independently from the selected native
  stage rather than calculated from the submitted projection. Boolean counts fail.
- `rows` as below. Do not paste raw tenant records into public Git. Preserve full
  original stage bytes and their SHA256 privately; the packet is a projection.

| Stage | Projection and dependency |
| --- | --- |
| source | Accepted committed publication source members, one exact SourceKey per `key`; `accepted_commit: true`. Exclude pending/error/enrichment observations from the publication membership set. |
| canonical | One canonical identity per `key`, exact `source_keys` array, `identity_evidence_ref`, and `publication_month` (YYYY-MM or null); `accepted_commit: true`. Every accepted source identity maps exactly once; multiple source identities may share a canonical publication only through evidenced membership. |
| registry | One comparison identity per `key`, backed by retained original SourceKey/CanonicalKey/PMID mapping evidence. Preserve legacy durable keys, blank stubs, all rows and review fields in the complete capture; never delete or rename them to obtain parity. Invalid/extra/duplicate identities block the comparison or are retained as explicit unresolved differences. |
| model | Complete publication comparison identities and `publication_month` from the exact selected model/terminal refresh. Query version and refresh operation must be retained, not inferred from count equality. |
| full_export | Complete unfiltered canonical bibliography, comparison identity and `publication_month`, exact exported bytes/manifest/hash, refresh/generation correlation and extraction contract. |
| monthly_export | Same generation/contract, explicit `reporting_month`, comparison identity and `publication_month`; include exactly the full canonical month partition. A genuinely empty month is allowed with independent count zero and complete paging. |

Do not infer an identity merge from a title or DOI alone. Use the existing typed
identity policy/crosswalk; this checker never rewrites source or durable IDs.
Unknown dates remain in the full bibliography and unknown-date accounting, not
silently assigned to the selected month. A known month and an unknown month must
not compare equal. Preserve precision/raw dates separately in the original receipts.

Full and monthly exports also require the same `extraction_contract_sha256`,
`query_version` and `model_refresh_correlation`; that correlation must equal the
selected model stage operation reference. Different export artifacts have distinct
byte hashes even when their extraction contract is shared.

## Existing evidence and outstanding captures

| Boundary | Reusable material | Missing correlated proof |
| --- | --- | --- |
| Source → canonical | Existing committed archive/member receipts and automatic identity policy; private-working-checkout `reconcile_publication_sources.py` | Selected complete generation plus evidenced complete membership map; no assertion that a running acquisition has committed. |
| Canonical → registry | Existing typed `reconcile_model_registry_identity.py` and `reconcile_pubmed_registry_keys.py`; full paged registry exports | Exact selected-generation registry keys, legacy/blank/extra disposition and preserved reviews. Old counts are not a current selection. |
| Registry/model provenance | `reconcile_registry_model_provenance.py` distinguishes primary registry source from derived model membership | Terminal selected-model refresh/query and source-set lineage parity; extra derived membership is not automatic source admission. |
| Full/monthly exports | `reconcile_full_month_exports.py` and extraction-contract/manifest receipts | Native complete exports tied to the same selected refresh and month, exact bytes and all metadata. |

Several of these tools remain in the private authoring checkout, absent from
canonical main. Reuse the owner's exact versions and receipts there; do not copy
untracked dependencies or assume a fresh main clone can import them. The new
six-stage checker is dependency-free and complements them; it does not replace
their richer source/provenance/metadata checks.

## Run preparation and interpret the result

Use the explicitly qualified repo-local Python with the code checkout and private
output directory. Output must be a new ignored `private/ops` path in that checkout:

```
<python> scripts/reconcile_generation.py <private-packet.json> --output private/ops/reconciliation/result.json
```

Exit0 is `PASS_SUPPLIED_KEY_PARITY_ONLY`; exit1 is BLOCKED with missing/unexpected
keys and stage-specific gaps; exit2 is malformed/unsafe input. The report contains
per-stage fingerprints, counts, missing/extra identities, unknown-month keys and
blockers. All reports retain `native_acceptance=false` and
`operational_acceptance=false`, including synthetic tests and supplied parity.
The checker validates declarations; it cannot authenticate a native receipt or
prove a producer actually exhausted paging. Owners verify retained artifacts and
independent counts against authoritative readbacks before accepting their stage.

## Final acceptance remains separate

E07-H05 closes only after the owner verifies actual terminal native source/commit,
registry, refresh/query and full/monthly export receipts for this lineage, resolves
all unexplained key differences, and checks metadata/source-set/date uncertainty,
first observations, human corrections and last-good preservation. Retain exact
model/flow/query/schema bindings and extraction-contract hashes. Existing richer
comparators remain required where they cover these fields. Do not promote local
key parity into full metadata, report-rendering, scheduling, delivery, licensing,
clinical or business acceptance. No refresh, cleanup or reharvesting is authorised
merely by an empty stage in this preparation packet.
