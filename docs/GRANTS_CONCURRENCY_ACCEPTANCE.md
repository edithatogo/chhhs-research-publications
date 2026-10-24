# Grants concurrent imports and conflicting edits — 24 October 2026

Bounded tests ran against the existing owner-operated grants flow and list, using
separately keyed SYNTHETIC ACCEPTANCE ONLY fixtures. No live opportunity was used
as a mutation target. Native definition and connection references were unchanged.

| Native case | Observed outcome | Scope of proof |
| --- | --- | --- |
| Two overlapping identical two-record imports, initially absent keys | Both succeeded; one run created both records, the other updated the same IDs; exactly one item per key | Actual run intervals overlap. Their absent-key reads were not simultaneous; this alone does not reproduce the create race |
| Two direct concurrent creates with the same new key | One accepted, one failed HTTP 500; exactly one item retained | Native OpportunityKey is indexed and enforces unique values. A separate diagnostic duplicate request returned SPDuplicateValuesFoundException naming OpportunityKey; the CLI race error itself exposed only HTTP 500 |
| Conflicting deadlines with the same observation time, sequential | First accepted, second rejected with GRANTS_REVIEWED_IMPORT_ROW_FAILURE; accepted source facts unchanged | Existing equal-time conflict guard works when the later reader sees the accepted observation |
| Overlapping imports with conflicting deadlines and the same observation time | One succeeded, one rejected; one accepted deadline retained on the original item | Actual run intervals overlap; only the successful run executed the update. This does not force both runs to read the same old version |
| Two editor saves using one captured ETag | First accepted; stale second rejected HTTP 412; accepted note retained | Native conditional writes detect stale versions when callers supply the actual ETag |
| Simulated human review save while an import was active | HTTP 409; note remained unsaved. Same payload accepted after terminal completion and a fresh ETag read | The edit request began inside the native run interval. Its HTTP 409 is recorded; no automatic mutation retry was used and no more specific service error was exposed |
| Import after accepted review edits | ReviewNotes and ReviewStatus retained; existing-item update succeeded for the relevant fixture | The source row earlier in this batch was deliberately stale and rejected; the later fixture update still succeeded. Overall failure does not mean zero writes |

The persisted editor-A note contained CLI-escaped newline text. Comparisons used
the actual saved value exactly; this does not add multiline rendering acceptance.
Editor-B used a plain-text marker and retained it exactly after the later import.

## Remaining concurrency gap

The native definition serializes rows within each run, but has no explicit trigger
run-concurrency limit. It reads source facts, evaluates timestamp/conflict rules,
then uses PatchItem without a captured version precondition. Its following ISO
text MERGE uses IF-MATCH '*'. These operations are not an atomic read/check/write.

Consequently, these passing bounded cases do **not** establish protection when two
imports both read the same older version before either writes, or when an external
writer changes a mapped source field between the flow read and update. No lost
update was observed in these tests, but the definition does not prevent that race.
Unique keys prevent duplicate storage; they do not guarantee both import runs
succeed or that source updates are ordered correctly.

Recommended follow-on implementation:

1. Serialize runs of this importer, retaining its existing identity, trigger,
   connection references and manual operation. This controls its own writers only.
2. Replace the existing-item write sequence with a version-conditional update,
   preserving ISO text and all excluded human fields in the same guarded write
   where supported. On HTTP 409/412, fail visibly, read fresh state, re-evaluate
   source ordering and reconcile before an explicit replay; never blindly retry.
3. Verify simultaneous old-version reads and a conflicting external write with
   deterministic fixture orchestration, then reconcile source/solution export.
   Preserve ReviewNotes and ReviewStatus; decide any additional curated-field
   ownership explicitly rather than silently changing it during testing.

These changes were not deployed as part of this testing request. Unattended or
general concurrent-writer acceptance remains open.

## Preservation and recovery

Complete list snapshots after each material case retained the real NIH record's
fields, version and review state exactly, excluding only volatile response-level
odata.id. The three labelled fixtures' version histories were retained privately
before recycling. The final complete active-list snapshot matches the original
one-record baseline. The flow was returned to Stopped/Off; no model refresh,
schedule, sharing or email operation ran. No solution re-export was needed because
the native definition and bindings did not change.

Private input packets, native errors, complete snapshots, field-uniqueness
readback, run intervals and per-iteration update receipts are retained in ignored
`private/ops/2026-10-24-grants-concurrency/`.

See also [later-record batch recovery](GRANTS_LAST_GOOD_ACCEPTANCE.md).
