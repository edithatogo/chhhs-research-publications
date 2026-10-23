# E01 writer key concurrency — 22 October 2026

Native inspection found the existing SourceKey and CanonicalKey columns indexed
without uniqueness enforcement. The writer's serial per-publication loop does
not serialize separate flow runs. This was a concrete storage-level race gap.

The original full writer remained Stopped. Fresh readback matched the accepted
complete 1,648-row keyset. All 1,345 nonblank keys were distinct; the 303 legacy
blank-key placeholders remained pending and were not assigned invented keys.
Both fields are existing list-local, writable custom text fields with existing
indexes. Supported MERGE changed only `EnforceUniqueValues` to true. Each save
returned 204 and independent field readback returned 200 with the same field ID,
internal name, scope and index before the next change.

Two independent concurrent duplicate-insert attempts used a genuine existing
record's keys. Both were rejected with `SPDuplicateValuesFoundException`, naming
SourceKey and CanonicalKey. No duplicate row was created. Complete before/after
comparison of all 1,648 records and every returned field matches; all 303 blank
keys remain. This proves datastore rejection of those competing duplicate
attempts, not a successful new-publication create or general write serialization.
Existing native upsert/replay/restoration evidence remains separate.

An initial full-row fingerprint gate stopped before any negative attempt because
Python serialized integer-valued JSON numbers as `1.0` while JavaScript used `1`.
Independent canonicalization of the saved source data reproduced the native hash
exactly. The corrected case retained complete field/value comparisons; it did not
waive a substantive difference or repeat a submitted insert.

Rollback is a supported MERGE of `EnforceUniqueValues=false` on these same two
list-local custom fields, retaining `Indexed=true`, the original IDs and all row
values. Snapshot/read back the exact field state and reconcile active writers
before rollback. Do not disable constraints merely to admit a conflicting key.
No trigger concurrency setting, flow graph, permission, sharing or model changed.

Private receipts under `private/ops/2026-10-21-e01-runtime-qualification/`:
`writer-22-uniqueness-intent.json`, `writer-22-key-constraints-save.json`,
`writer-22-pre-constraint-full-register-sha256.json` and
`writer-22-key-constraints-qualification.json`.

Microsoft documents the indexed uniqueness property and supported field MERGE
route in [Field.EnforceUniqueValues](https://learn.microsoft.com/en-us/previous-versions/office/sharepoint-server/ee543809%28v%3Doffice.15%29)
and [SP.Field](https://learn.microsoft.com/en-us/previous-versions/office/sharepoint-visio/jj246815%28v%3Doffice.15%29).
Trigger concurrency was not enabled: Microsoft documents that setting as
[irreversible without a new flow](https://learn.microsoft.com/en-us/power-automate/guidance/coding-guidelines/optimize-power-automate-triggers).
