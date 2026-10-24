# Isolated grants model refresh — 24 October 2026

The existing unbound retention-recovery canary was refreshed through the native semantic-model API. Its identity, SharePoint bindings, complete 37-part definition, disabled schedule and absence of bound reports were checked before execution. No replacement model or report was created.

The service confirmed one completed Full refresh with Transactional commit mode, targeting only the Grants Registry and Grants Deadline Occurrences partitions. Both partition statuses were Completed. Native DAX readback and fresh SharePoint reads reconcile as follows:

| Check | Verified result |
| --- | --- |
| Grant records | One SharePoint item and one model parent, matching key and native item ID; zero synthetic records |
| Parent contract | All 32 registry fields match, including full schedule/date-facts JSON, attribution, review fields, source hash and acquisition timestamp; empty optional SharePoint nulls correspond to empty model strings |
| Deadline occurrences | Seven distinct occurrence keys, exact source key-set match; all 11 child fields reconcile for every occurrence |
| Original occurrence metadata | Each SourceOccurrenceJSON parses to the exact retained source occurrence object; serialization escaping does not change values |
| Relationship | Zero unmatched occurrences; RELATEDTABLE from the single parent returns seven children |
| Other model tables | All 27 unrelated table counts unchanged, including publication and retained-publication totals |
| Model definition | All 37 definition parts unchanged before/after refresh |
| SharePoint preservation | All stored fields, item/version/ETag, review notes/status and four attachment identities unchanged |
| Isolation and scheduling | No bound reports; refresh schedule remains disabled and unchanged |

The seven nominal due dates are 2026-11-05, 2027-02-05, 2027-03-05, 2027-06-05, 2027-07-05, 2027-10-05 and 2027-11-05. Source local time remains 17:00 at the applicant organisation. Effective due dates remain blank; no applicant timezone, UTC/Brisbane instant or holiday-adjusted deadline was invented. The announcement closing/archive facts remain separate in the parent metadata.

Exact native model/source identities, definition exports, refresh execution/partition details, DAX results, before/after source snapshots and field/key-set parity receipts are retained under ignored `private/ops/2026-10-24-grants-model-refresh/`. Comparisons exclude only the volatile response annotation odata.id; actual item IDs and version/ETag fields are compared.

This closes bounded isolated-model refresh/parity for the selected NIH opportunity. It does not activate unattended intake, automatic original-response archival, recurring refresh or distribution. Main report replacement, multirow transactional source-write recovery and concurrent-writer acceptance remain separate. Row-count preservation for unrelated tables is not a claim that all their contents were requalified.
