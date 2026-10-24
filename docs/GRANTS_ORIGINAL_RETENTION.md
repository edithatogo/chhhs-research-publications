# Reviewed-import original retention candidate

Status: locally implemented; native qualification pending. The existing importer
remains manual-only and Off. The scheduled acquisition/archive proof is recorded
separately in [NIH recurring qualification](NIH_RECURRING_QUALIFICATION.md).

The candidate extends the existing importer, preserving its identity, connection
reference, source mappings and exclusion of human review fields. It accepts an
additional `OriginalResponsesJson` envelope for the selected NIH opportunity.
`grants_import_originals.py` prepares this envelope from all four admitted raw
responses, every declared attachment-folder ZIP and the reviewed projection.
Preparation checks projection/hash provenance, semantic replay, date facts,
attachment metadata, ZIP coverage, CRC and members. `--source-observed-at` retains
the original producer timestamp spelling when it differs from normalized UTC;
the helper does not guess a different lexical value to force a hash match.

The flow candidate binds the envelope to the reviewed source identity and
observation, checks roles and decoded source content, and serializes its own runs.
It saves deterministic original attachments only when absent, reopens each file
and requires exact base64 byte equality. It never overwrites or deletes an
existing attachment. Native connector output shapes and actual byte comparisons
still require runtime verification; local graph checks are not that proof.

Existing-item originals are retained before source observation ordering checks.
A rejected older observation can therefore leave additional evidence attachments
while accepted typed fields remain unchanged. For a new item, SharePoint must
create the parent before attaching files; an attachment failure can leave a
partially created parent. Same-key replay is the recovery path, not transactional
rollback. Trigger concurrency controls this flow's writers; it does not provide
atomic protection against external edits or replace the existing non-atomic
source update behavior. Producer SHA declarations are checked locally; the native
flow independently compares saved bytes but does not recompute SHA256.

## Native checkpoint — 24 October 2026

The management API acknowledged a save, but fresh published-definition readback
retained the original graph. No candidate run was triggered. The manual flow was
returned Off and that state was read back. PAC confirmed the existing environment,
workflow and logical SharePoint reference. A clientdata-only Dataverse update,
guarded by exact name, Draft state and complete preimage, was then rejected:
`ActiveUnpublished` / a published update cannot proceed while an unpublished
active row exists. The pre-read guard is not an atomic ETag condition.

The existing unpublished version has not yet been retrieved or discarded.
The cached-only read adapter refused an expired Dataverse credential without
renewing or switching profiles. Browser entry points timed out twice. The existing
lane owner was contacted about the supported same-client renewal/draft route;
no authentication reset, new consent or grants-object handoff occurred.

Microsoft documents [separate draft and published flow versions](https://learn.microsoft.com/en-us/power-automate/drafts-versioning)
and a [bound RetrieveUnpublished function](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/webapi/reference/retrieveunpublished?view=dataverse-latest).
The recorded native metadata exposes that function for workflow records. These
contracts establish the next inspection route, not successful draft retrieval or
publication. Preserve the draft until its content and ownership are reconciled.

## Remaining qualification

1. Retrieve the exact unpublished version, compare it with the saved candidate
   and preimage, then reconcile through a supported same-object save/publish route.
2. Read back the complete published graph, original logical binding and manual
   trigger before running. Keep a verified restoration preimage.
3. Run one original-backed NIH replay: reopen all five saved originals, preserve
   the four existing attachments, all source fields and human review fields.
4. Repeat: prove zero duplicate items/files and stable existing attachment bytes.
5. Reject an incomplete envelope and conflicting existing-name bytes; prove
   last-good typed values and prior attachments survive, then recover by valid replay.
6. Return Off. Reconcile the final canonical solution export, source and versioned
   native documentation. No scheduled register/model chain or delivered alert is
   implied by this candidate.

Local validation on the qualified Python 3.15.1 interpreter: 848 tests passed
with 25 skips; 446 project checks and web-first contracts passed. Private fixtures
and native acceptance are separate from this public clone's test results.
