# Recovered historical generation links — 24 October 2026

All three previously missing links are recovered from saved evidence for the
selected September 2026 model/export generation. The six-stage packet reports
`PASS_SUPPLIED_KEY_PARITY_ONLY` with no key or month mismatch. No native run,
refresh, registry change, export or delivery was started.

| Required link | Accepted evidence and result |
| --- | --- |
| Complete accepted source membership | 1,274 PubMed identities match the exact native-read committed inventory; all 172 saved archive files match their native byte hashes and prepared semantic contents. All 709 DoRA identities match the complete hash-validated retained archive and correlated native retained-source query. Earlier PubMed inventories are retained subsets. Total: 1,983 distinct source identities. |
| Existing source → canonical map | Every PubMed source identity has its existing canonical PMID identity; every DoRA identity is linked by the exact existing canonical DORAURL. All 1,983 sources map once to 1,341 canonical publications. The 11-expression dependency closure and three relevant native table definitions are identical, and all 40,230 canonical values are exactly unchanged between the source reconciliation and selected export generation. No new title/DOI-based merge is inferred. |
| Registry capture / preservation chain | The successful native keyed export has 1,345 rows. Its original item IDs, stored keys, source keys and all 20 curated/core fields exactly match the later complete 1,648-row native capture. The crosswalk covers all 1,341 canonical identities, retains four individually evidenced secondary representations and retains all 303 blank placeholders. Original run IDs and observation times remain distinct. |

The selected terminal refresh detail lists only the four enrichment tables;
Publication and retained source tables were not refreshed by that operation.
The source-query target, committed-source model and selected model IDs match.
The original canonical source-query window is separately proven Completed before
and after capture. Its persisted Publication values match the selected physical
Publication capture exactly, bridging the two operations without relabelling their
run IDs or claiming a new collection.

The registry projection groups comparison identities only. It retains every
original row in the crosswalk and complete capture. Nine PubMed-shaped registry
SourceKeys are attached to exact stored DoRA canonical identities; they do not
establish nine additional primary PubMed source members. Legacy SourceKey shapes
are preserved rather than silently renamed. The independent comparison count is
the native 1,345 keyed rows minus four separately evidenced secondary
representations, rather than a count copied from the submitted projection.

## Populated packet result

| Stage | Comparison identities |
| --- | ---: |
| Accepted source membership | 1,983 |
| Canonical publication | 1,341 |
| Registry, with original representations retained | 1,341 |
| Model | 1,341 |
| Full export | 1,341 |
| September 2026 monthly export | 14 |

All seven available key comparisons pass. All 189 unknown-month publications stay
in the full bibliography. Existing model/export receipts are reused unchanged.
The historical initial blocked packet remains intact; the recovered packet is a
new version under `private/ops/2026-10-24-reconciliation-links/accepted-v2/` in the
primary evidence checkout. It includes source membership, the complete map,
registry crosswalk/preservation proof, input fingerprints, packet and oracle result.
The new identity-comparison contract records the recovered native-link basis and
retains the original exact-key contract digest as its parent; the old missing-map
basis is not carried forward as a current claim.
Only [aggregate counts and boundaries](../config/recovered-generation-links-summary.json)
are committed to Git.

## Reproduce without native effects

`scripts/recover_selected_generation.py` reads the retained named receipts and
verifies their file hashes, exact definitions, source membership, canonical values,
registry preservation and six-stage comparison. It uses the source-integrated
`scripts/verify_retained_canary_metadata_values.py` and `scripts/reconcile_generation.py`;
all imports are standard-library/local source. Exact targets and raw data are
supplied only from the private evidence checkout.

```
<qualified-repo-python> scripts/recover_selected_generation.py \
  --evidence-root <primary-evidence-checkout>/private/ops \
  --output <primary-evidence-checkout>/private/ops/<new-output-directory>
```

Output must be a new ignored private directory. The tool refuses an existing
output and has no network or native mutation path. A clean clone can reproduce
the checks when supplied the same private evidence; private data is not bundled.

## Remaining boundary

The three missing lineage links are closed. Whole-system **metadata and operational
acceptance remain separate**: the oracle deliberately retains
`native_acceptance=false` and `operational_acceptance=false`. This is the selected
historical generation, not a new current snapshot or an accepted schedule.

The 144 semantic source/curated pairs remain explicitly uncertain; the three title
differences remain explained. No correction or routine per-record approval follows.
The 69 permitted source-to-native text-display normalizations in the DoRA metadata
comparison are a different boundary; original source text remains hash-preserved.
They neither resolve nor increase the 144 semantic pairs. Field/model/export
uncertainty propagation, richer metadata/source-set preservation, and any genuinely
missing E07-H05 runtime/operational proof retain their own evidence gates. Do not
repeat already accepted model/export tests to close stale wording.
