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

This verifies the declared single-record cases. It does not establish a transaction across multiple SharePoint requests, rollback after a later row fails in a multirow batch, or concurrent-writer safety. The source-admission boundary must complete before submission; changed-source end-to-end unattended acquisition, archive delivery and model refresh remain separate gates. Fixtures are never live funding data.
