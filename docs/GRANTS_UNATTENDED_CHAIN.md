# Unattended grants chain qualification — 24 October 2026

The selected, already-admitted NIH opportunity now has a native scheduled
**acquisition → archive → cloud projection → conditional register commit →
grants-only model refresh** path. Six complete scheduled cycles succeeded,
including two after a controlled post-commit failure and two after solution conversion. This is bounded technical
qualification, not production activation or whole-source admission.

## Simplest supported implementation

The existing acquisition qualifier retains its identity. An owner-only Office
Script through the existing Excel connection performs the maintained semantic
replay, complete-input validation, normalization and SHA256 calculation. Its
native result matches the Python producer across all 32 fields, including the
EvidenceHash; it does not read or write workbook data. No copied bearer token,
new consent or unattended desktop is required.

The standard Power BI connector refreshes a separate grants-only model in the
existing workspace. Its two table definitions and explicit parent/occurrence
relationship come from the hash-pinned accepted isolated model. The original
mixed model and reports are preserved. This avoids refreshing unrelated
publication tables and avoids requiring enhanced-refresh HTTP authentication.
The new model uses the existing SharePoint datasource credentials.

The collector updates only the existing admitted parent. It requires one exact
stable key/native item, checks the current source projection against the last
verified commit receipt, captures the current ETag, and sends one conditional
MERGE containing the 29 source fields and ISO text together. ReviewNotes,
ReviewStatus and CHHHSRelevance are excluded. There is no create path and no
wildcard ETag or automatic mutation retry. Source-field drift fails closed;
review-only changes are preserved. A concurrent edit causes HTTP 412.

A commit receipt is saved, read back and byte-verified before refresh. The flow
then requests refresh, retains its request ID, and polls for the current parent
EvidenceHash plus exact one-parent/seven-occurrence counts. Native refresh
history independently confirmed each tested request Completed. The flow itself
**does not poll the REST refresh job to terminal status**; current-data visibility
and external terminal-job verification remain distinct claims.

## Native acceptance evidence

| Case | Result and preservation |
| --- | --- |
| Two complete scheduled cycles | New four-response/ZIP archive each time; independent saved-byte, semantic replay and ZIP checks pass; 32 parent fields and all seven occurrence records reconcile |
| Stale conditional write | Real HTTP 412; entire register item/version unchanged; no model refresh; retained failure receipt |
| Failure after verified commit, before refresh | Two bounded failed ticks retain valid source commits and immutable receipts; only observation/hash/version advance; accepted source facts and human fields preserved; model refresh history unchanged |
| Scheduled recovery | Two subsequent ticks succeed and expose the current EvidenceHash in the model; failed generations and receipts remain retained |
| Canonical solution conversion | Two subsequent scheduled cycles succeed with the same physical connections; final daily candidate Off |
| Native archive/worker shape mismatch | Initial integrated runs fail before register/model effects; explicit attachment-shape adapter fixes the boundary; regression check added |

There is one accepted parent, seven distinct related occurrences and no duplicate
parent. All 17 existing original attachments retain their identities, versions,
lengths and timestamps. Complete field reconciliation treats only the existing
model's documented null-to-empty-text representation as equivalent; it does not
invent dates or rewrite evidence JSON.

Raw acquisition manifests remain stage-specific and retain their original false
downstream flags. Separate verified commit/success/failure receipts carry the
later results. A successful archive alone is never promoted to full-chain proof.

## Failure signals, recovery and remaining boundaries

A failed processing scope writes and reads back a source/run/stage/action-status
receipt and terminates visibly Failed. If receipt storage itself fails, native
failed-run history is the fallback; no claim of guaranteed receipt persistence
or alert delivery is made. Before replay, reconcile whether the conditional
commit happened and whether a verified commit receipt exists. Preserve valid
commits, failed generations and the last-good model. Resolve an uncertain commit
against native item/version history; do not blindly reset the baseline or retry.

Push notifications are **not delivered or qualified**. Existing owner flow
failure-email subscriptions are off. The prepared minimal alert contains only
source, run link, stage/error, receipt link and commit/refresh state. Exact
recipient/content/scope authority and one delivered, deduplicated failure remain
needed for push delivery. Receipt persistence is the usable current failure signal.

The flow finishes Off with a daily 06:00 Brisbane candidate; the qualification
worker flow and the model's independent refresh schedule are also disabled.
Later real daily freshness/operating-window observations belong to E08. Bounded
minute ticks do not count as operational days.

The NIH schedule remains the previously qualified structured transcription with
its original evidence vintage. It is not a fresh full NOFO capture. Changed API
date facts or attachment scope/bytes fail closed for readmission. First-time NIH
admission, other opportunities/sources, a backend failed-refresh/recovery test,
whole-service failure/concurrency matrix and production activation remain open.
There was no report rebind or global release/acceptance change.

## Reproducible source and private evidence

- `scripts/office/nih_grants_worker.ts`: saved owner-only native script body.
- `scripts/prepare_nih_unattended_flow.py`: pure builder from the original owned
  acquisition preimage, admitted context, exact accepted baseline and private
  resource bindings; default has no fault injection.
- `scripts/prepare_grants_only_model.py`: pure two-table extraction from the exact
  hash-pinned accepted model definition; excludes service-owned `.platform`.
- Focused worker, chain and model tests distinguish synthetic/local proof from
  native saved readback, scheduled runtime and operational acceptance.

Exact identities, raw archives, run/action payloads, model parts, connections,
preimages and successor solution export remain ignored under
`private/ops/grants-cloud-worker/`. The sanitized reconciliation manifest records
fingerprints and outcomes without tenant bindings.

---

# Earlier preparation checkpoint — retained history

**Not qualified end to end.** The existing acquisition qualifier and reviewed
import remain Off. Accepted records, attachments, review fields and the isolated
model have not been changed by this increment. No notification was sent or
enabled. Existing scheduled acquisition/archive, manual retention and isolated
refresh receipts remain valid within their recorded scopes.

## Current supported route and missing bindings

| Stage | Current position | Implementation and qualification needed |
| --- | --- | --- |
| Acquisition and archival | Actual scheduled ticks, freshness and partial-failure recovery already verified | Reuse the existing qualifier and archived generations; do not repeat settled archive tests merely to produce another receipt |
| Native projection/admission | Complete semantic replay, source normalization, SHA256 evidence and independently pinned NIH schedule are implemented in local Python | Qualify a supported cloud processing step using the same contracts. A recurrence must not mark a copied old row freshly observed or reuse an old EvidenceHash for a newly projected record. Office Scripts through the existing Excel connection is a possible bounded processing route, subject to its actual script/runtime/licence and byte/hash parity checks; it is not currently qualified |
| Existing-row commit | Current native importer uses PatchItem followed by an unconditional timestamp repair | Candidate below replaces only this existing-row update branch. First-time NIH admission remains fail closed; no trigger/caller credential conversion is proposed |
| Isolated-model refresh | Prior operator API refresh targeted only the two grants partitions | Existing Power BI connector's RefreshDataset schema exposes groupid and datasetid only. It cannot express the required objects, transactional mode or same-request terminal polling. There is no owner-connected Entra HTTP connector in the current inventory. A connected Power BI query action and a CLI bearer token are not renewable unattended scoped-refresh authentication |
| Failure signals | Native failed-run history and retained failure receipts already work | Keep an explicit run/source/stage/error/receipt-link failure record. Push delivery is separate: exact recipient, content and scope need direct authority. Native failure-email subscriptions stay off; do not use them to bypass the delivery boundary |

## Prepared conditional commit

`scripts/patch_grants_conditional_commit.py` is an offline candidate builder.
It preserves the full original connection-reference map and manual Button trigger,
keeps importer concurrency one, and changes only the existing-row commit branch:

1. Re-read the same stable key after original-file retention. Attachment additions
   can legitimately advance the item version, so the initial lookup version must
   not be blindly reused.
2. Require exactly one matching item, the same native ID, a nonempty concrete
   ETag and exact equality of all mapped source fields with the original lookup.
   An intervening source edit fails before the commit. Human review/classification
   edits are excluded from source comparison and from the write payload.
3. Send a single SharePoint REST MERGE with that captured ETag, source fields and
   exact ISO text together. No PatchItem/second wildcard MERGE remains on this
   existing-row branch. Connector retries are disabled. A 409/412 must remain a
   visible failure; recovery requires fresh read, admission/order evaluation and
   explicit replay, never a wildcard or blind retry.

The payload excludes ReviewNotes, ReviewStatus and CHHHSRelevance. It retains
source attribution, uncertainty, full schedule/date-facts JSON, source identity
and EvidenceHash. The existing non-NIH create path is preserved, including its
historical timestamp repair; no new create-path concurrency guarantee is claimed.

Focused tests prove candidate structure, source-drift guards, mapping refusal,
human-field exclusion and preservation outside the changed branch. The builder
also prepares successfully from fresh native clientdata with exact reference-map
preservation. These are **local preparation checks**, not runtime or native save
acceptance. The tracked live template and canonical solution are unchanged.

Before deployment, use fresh draft/run inspection and the existing guarded
`flow_deployment.py` route. Qualify normal source/ISO values and hyperlink fields,
stale ETag rejection, intervening source edits, concurrent review/classification
edits, replay and recovery on labelled fixtures. Reconcile native graph, canonical
solution and versioned documentation before promoting the candidate.

## Refresh options and recommendation

| Option | Recommendation / contingency |
| --- | --- |
| Renewable authenticated enhanced REST refresh on the existing isolated canary | Preferred when an existing approved cloud authentication route can be qualified. Target only Grants Registry and Grants Deadline Occurrences; retain the returned request ID, poll it to terminal status and reconcile all parent/child fields and keys. Do not embed a copied CLI token or add credentials/consent silently |
| Separate grants-only isolated model with the standard Power BI connection | Simpler refresh surface if a separate model is selected and its isolation, credentials, refresh correlation and rollback are qualified. It adds a maintained native object; none has been created or rebound here. Preserve the existing model and accepted totals |
| Whole-model refresh of the existing mixed canary | Do not use as a shortcut: it would refresh unrelated publication partitions and cannot satisfy the narrow existing acceptance scope |
| Continue the current operator bridge | Safe interim route: automated acquisition/archive, reviewed producer/import and scoped operator refresh. Label it operator-assisted, never unattended |

## Concrete failure-alert proposal

Prepare one owner-only alert per failed run, keyed by source + native run ID.
Subject: `RIMS grants pipeline failed — <stage>`.
Content: source identifier, run link, failed stage, stable error code, retained
receipt link, whether register commit occurred, and refresh request/status when
known. Exclude source descriptions, attachment content, review notes and tokens.
If a send outcome is uncertain, retain that state and reconcile delivery before
another attempt; a receipt alone does not prove delivery. A recovered run links to
the earlier failure without deleting it. This proposal authorizes no send and
names no new recipients.

## Remaining acceptance sequence

Once processing and refresh authentication are qualified, use two correlated
actual scheduled full cycles, unchanged replay, changed-source/deadline admission,
source/schema/partial-batch failure and model-refresh failure/recovery. Each cycle
must retain the same archive generation, conditional register commit and refresh
request, reconcile the one admitted parent and seven supported occurrences, and
preserve human fields, prior archives and all unrelated model counts/definitions.
Delivered alerts and duplicate suppression require their own native receipts.
Permanent activation, daily reliability and E08 operating-window observations
remain distinct from bounded technical qualification.

Sources: [Power BI connector](https://learn.microsoft.com/en-us/connectors/powerbi/),
[enhanced refresh and authentication](https://learn.microsoft.com/en-us/power-bi/connect-data/asynchronous-refresh),
[SharePoint conditional list updates](https://learn.microsoft.com/en-us/sharepoint/dev/sp-add-ins/working-with-lists-and-list-items-with-rest).
Related accepted evidence: [recurring acquisition](NIH_RECURRING_QUALIFICATION.md),
[original retention](GRANTS_ORIGINAL_RETENTION.md),
[concurrency limits](GRANTS_CONCURRENCY_ACCEPTANCE.md),
[isolated-model parity](GRANTS_MODEL_REFRESH_ACCEPTANCE.md).

Native documentation publication is pending because this is an undeployed
candidate and unresolved integration decision; the existing versioned grants
acceptance document remains unchanged.
