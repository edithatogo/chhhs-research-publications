# Saved whole-system reconciliation closeout — 24 October 2026

The selected historical publication generation is reconciled through source,
canonical publication, registry, model and full/monthly exports, including shared
metadata and the subsequent registry preservation checkpoint. This is saved-native
evidence accounting; no new native operation or semantic correction was performed.

[Recovered lineage](RECOVERED_GENERATION_LINKS.md) supplies all six stages:
1,983 source identities map to 1,341 canonical/model/full-export identities and
14 September export identities. All seven key/month comparisons pass. All
189 unknown-month publications remain in the full bibliography.

## Shared metadata is completely accounted for

| Registry ↔ canonical comparison | Field pairs |
| --- | ---: |
| Exact values | 12,791 |
| Equal numeric year representations | 1,334 |
| Retained exception dispositions | 4,638 |
| Null/empty representations | 11 |
| **Total: 14 shared fields × 1,341 publications** | **18,774** |

Every original exception binds its exact registry item, retained value and source
value to this generation. The exception dispositions reconcile to 144 uncertain
semantic pairs and three explained titles; the remainder retain their existing
field-role, literal representation, source-unknown, missing-fill and range-recovery
accounting. Literal name-segment equality is not person identity evidence.

The 709 missing source-link fills, 78 other missing-value fills and 14 bounded
range-field recoveries match the later native readback exactly. All other shared
fields remain unchanged. Durable keys, human review fields and first-observed
values are preserved across all original 1,648 registry rows. The four secondary
representations and 303 placeholders remain present. The later capture contains
three additional keyed rows: they remain outside this selected historical
generation and are preserved, rather than silently admitted or deleted.

Registry primary-source coverage passes for all 1,341 comparison identities:
699 classifications agree exactly; 642 model co-memberships have additional derived
source context. Derived membership is not an additional registry admission. Four
legacy secondary representations remain separately evidenced in the crosswalk.
The provenance comparator now accepts a null PMID for DoRA-only identities while
continuing to reject missing PubMed PMIDs and malformed non-text identities.

All 18 exported fields are verified in both CSV and HTML for the 1,341 full and
14 monthly records: 24,390 cells per format. Full/monthly metadata, source snapshot,
query/refresh correlation, extraction contract, saved hashes and month partition
agree. Accepted source/native runtime proofs are reused; no refresh/export was
repeated merely to reopen a completed gate.

## Evidence and reproducibility

The aggregate [machine receipt](../config/whole-system-metadata-summary.json) has
counts and boundaries only. Exact identities, original values and full receipts
remain in the primary evidence checkout under
`private/ops/2026-10-24-whole-system-metadata-qualified/`.

```
<qualified-repo-python> scripts/audit_whole_system_metadata.py \
  --evidence-root <primary-evidence-checkout>/private/ops \
  --output <primary-evidence-checkout>/private/ops/<new-output-directory>
```

The command refuses an existing or non-private output. It verifies full paging,
independent registry count, original/current identity and protected-field parity,
complete difference coverage, source provenance, and exact saved CSV/HTML contents.
Source dependencies are local/standard-library code. No native write path exists.

The 144 semantic pairs remain explicitly uncertain. This closes the selected
saved-generation reconciliation and preservation accounting, not semantic truth,
a fresh current-generation harvest, native uncertainty-column propagation,
report rendering, schedules, external delivery or operational/business acceptance.
Those gates must not be inferred from a green offline comparator.

## Worktree completion and cleanup

Nine helper/reconciliation worktrees from this chat have exact head matches to
merged PRs 40–45, 47–48 and 53, with the final active checkout superseded by this
closeout PR. Completed tracked work is integrated; no additional implementation
was found in the older checkouts. One untracked `.venv` is a symlink to the primary
qualified interpreter, not another environment to migrate or delete.

After this PR and merged-main Actions pass, cleanup checks each worktree again,
preserves ignored/untracked contents and source recovery references privately,
verifies the archive, checks live process use, and removes one checkout at a time.
No forced removal or branch deletion is needed. The primary checkout, active DoRA
checkout and shared CI checkout are retained. Exact cleanup receipts and archive
hashes belong under `private/ops/2026-10-24-reconciliation-worktree-cleanup/`.
