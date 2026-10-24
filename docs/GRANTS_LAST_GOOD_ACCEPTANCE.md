# Changed deadlines and last accepted records — 24 October 2026

Seven bounded cases ran through the existing manual grants flow, using a separately keyed record explicitly labelled SYNTHETIC ACCEPTANCE ONLY. This fixture was not an admitted source opportunity. The real NIH record was read before and after every case and remained unchanged, including its version, review fields, seven nominal occurrences and four original attachments. No downstream refresh or schedule was enabled.

| Native case | Expected and observed result | Last accepted state |
| --- | --- | --- |
| Create labelled fixture | Succeeded; one create, no update | One distinct test item; real NIH unchanged |
| Newer changed deadline | Succeeded; create skipped, same-ID update succeeded | Date changed from 2026-12-01 to 2027-01-15; submitted deadline fields reconciled, allowing SharePoint null for empty optional text; test review note preserved |
| Older deadline observation | Failed; create/update skipped | Accepted changed deadline and all stored fields/version unchanged |
| Changed deadline with same observation timestamp | Failed; create/update skipped | Accepted changed deadline and all stored fields/version unchanged |
| Missing source identity | Failed; create/update skipped | Accepted records and versions unchanged |
| Malformed JSON | Failed before row writes | Accepted records and versions unchanged |
| Empty array | Succeeded as a zero-write no-op | Accepted records and versions unchanged; empty input did not delete missing records |

Three additional source-admission cases used the retained admitted NIH batch and maintained catalogue: incomplete pagination, a record with missing title, and an iterator interrupted after yielding a complete batch. All returned accepted=false and no records eligible for submission. They were rejected locally before calling the native flow; this is not a claim that the cloud flow independently validates provider pagination.

Full list snapshots had no continuation. Comparisons include actual item IDs, all stored field values, review notes/status, attachment identities, Modified, ETag and current SharePoint version. Only the volatile response-level odata.id annotation was excluded: it changed between otherwise identical reads, including for the untouched NIH item. No stored field or version was excluded. Five fixture versions were retained privately before cleanup.

The exact synthetic item was recycled with identity checks and its current ETag; it was not permanently deleted. The final complete active-list snapshot matches the original one-record baseline, including the NIH version and attachments. The manual flow is Off again. No definition change was needed for these cases.

Private input packets, correlated terminal runs/actions, complete before/after reads, source-admission rejection results, fixture history, recycle receipt and acceptance summary are retained under ignored `private/ops/2026-10-24-grants-last-good/`.

This verifies the declared single-record cases. It does not establish a transaction across multiple SharePoint requests, automatic rollback after a later row fails, or concurrent-writer safety. Corrected multirow replay is verified below. The source-admission boundary must complete before submission; changed-source end-to-end unattended acquisition, archive delivery and model refresh remain separate gates. Fixtures are never live funding data.


## Later-record failure and corrected batch recovery

A two-record, serial native batch was tested on 24 October 2026 using distinct
SYNTHETIC ACCEPTANCE ONLY fixtures. Record A was created successfully. Record B
had a missing required Source and was rejected without a create or update. The
overall run failed with GRANTS_REVIEWED_IMPORT_ROW_FAILURE. Iteration-level
action receipts prove that A succeeded before B was rejected; the complete list
read contained A and no B. Earlier writes are retained, not rolled back.

A review-note marker was saved on A before recovery. The complete corrected batch
was then submitted: A used the existing-item update path with its original ID and
B used the create path. The terminal run succeeded. A further unchanged resubmission
also succeeded, retaining exactly one item per key, both item IDs and the persisted
review-note marker. The CLI encoded the marker's newline as escaped text; this is
proof of preserving the saved marker, not an additional rich-text rendering test.
No manual repair or deletion of A was required to recover.

The real NIH item matched its baseline across failure, correction and replay,
including all returned fields, version and review state, excluding only volatile
response-level odata.id. The fixture records were recycled, the complete active
list returned to its baseline, and the flow was stopped again. No model refresh
or scheduled operation ran. Native flow definition and bindings were unchanged.

An initial probe omitted SourceID but retained RoundID; it correctly succeeded
because the contract accepts either identifier. Its results were retained and
its separately labelled fixtures recycled before the actual failure case.

Recovery procedure: reconcile the failed batch by stable key against SharePoint,
retain successful rows, correct the rejected source input, then replay the complete
batch. Reconcile IDs, source fields and human fields after terminal success.
Do not treat a failed batch as zero-write or expect automatic rollback. This
bounded identity-validation case does not prove recovery from every connector
outage, a write followed by a lost response, or concurrent external writers.

Private packets, complete list snapshots, terminal run identities and per-iteration
create/update/diagnostic receipts are retained in ignored
`private/ops/2026-10-24-grants-multirow-recovery/`.
