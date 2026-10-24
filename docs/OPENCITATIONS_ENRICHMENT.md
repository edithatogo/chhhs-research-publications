# OpenCitations DOI citation-count enrichment

Selected 24 October 2026 as the next independent enrichment task. Reuse verified
DOI identities from accepted OpenAlex originals; their observations identify the
input work, not the current OpenCitations count or a confirmed local affiliation.

The provider publishes its data under [CC0](https://opencitations.net/). Its
[official quickstart](https://github.com/opencitations/oc_docs/blob/main/docs/api/quickstart.md)
documents anonymous `index/v2/citation-count/doi:<DOI>` requests. This implementation
collects the complete count response and headers for each selected DOI. It does
not collect full citation edges, combine provider counts or infer research quality.

## Implementation

`scripts/prepare_opencitations_flow.py` prepares a manual Power Automate cloud
flow using the existing SharePoint site, archive folder and physical connection.
The source contains no tenant identifiers, credentials or publication snapshots.
Provide private seed JSON, existing site/folder and a new private output path.
Run through the explicitly selected qualified repository interpreter.

- One flow run and one DOI request at a time; finite HTTP timeout and no retries.
- A provider failure stops later provider requests within that batch.
- Retain complete decoded provider response JSON with request identity, headers,
  source observation time, licence and bootstrap provenance. This is not a claim
  of exact original HTTP wire bytes; independently hash the saved archive bytes.
- Safe GUID raw filenames; exact saved-byte readback before remembering an entry.
- Publish a source-specific complete marker only after every selected DOI passes.
- Replay uses the same seed fingerprint, validates all selected keys and exact
  raw bytes, and performs zero provider calls and zero archive writes.
- No canonical register/model fields, schedules or email actions are changed.

The seed defines a frozen observation batch. Repeating it verifies/reuses that
snapshot; it does not silently refresh counts. A later observation needs a new
explicit provenance-bearing seed revision. Never relabel a cached observation as
current or advance Crossref/DataCite checkpoints from this provider.

### Extend an accepted DOI selection without recollection

`--reuse-manifest` accepts an existing complete OpenCitations manifest whose DOI
entries are a subset of the new, at-most50-DOI seed. Preparation checks unique
DOIs, safe archive basenames, decoded source identity, successful HTTP status and
exact count agreement. The native flow reads each retained raw file and requires
exact base64 equality before reusing its unchanged entry/path. Only missing DOI
entries execute provider requests and create new raw files. Final acceptance is
a separate selection-specific marker; the previous marker remains last-good.

Mixed observations retain their original per-record timestamps and provider
scope hashes. The selection fingerprint describes membership and bootstrap
provenance; it does not imply every observation was fetched at one common time.

## Native authoring route

Inventory by exact purpose before creation. New standalone flow creation is
supported through FlowAgent. Standalone references use the existing physical
connection and API identity; a solution-only logical-reference property can cause
update resolution failure and must not be mistaken for a broken connection.
Solution-aware updates retain the qualified PAC/Dataverse route and native schema.
Always read back exact saved definition/state/binding before runtime.

## Interrupted archive recovery

If provider acquisition succeeded but persistence failed, retain the original run
and recover its successful envelope outputs from native run history. Independently
verify DOI identity, source scope and response status/count before passing the
complete bounded set via `--recovered`. Original provider observation times and
headers remain. Recovery skips provider HTTP requests. After the marker is
accepted, restore the normal candidate without embedded recovery envelopes and
prove its no-write replay. Do not retry an unchanged access denial.

## Current evidence boundary

Initial acquisition returned three valid provider counts, but archive creation
failed with HTTP403. No completion marker was written. The failed attempt remains
evidence. GUID filenames and the standalone binding representation were corrected;
the precise cause of the initial403 was not isolated between those changes.

Bounded native recovery succeeded in about13.5seconds, reusing all three original
envelopes with zero new provider requests. Independent M365 GETs verify three
raw files (2,712bytes) and the complete manifest (5,244bytes), exact saved base64,
provider observations and counts. The normal definition, with no embedded recovery
envelopes, then replayed successfully in about4seconds: zero provider requests,
zero archive writes, exact raw-byte and selected-key guards. Final complete native
definition readback passes with manual trigger and Stopped state.

Private receipt: `private/ops/2026-10-24-opencitations/acceptance.json`. This is three
DOI count observations, not a citation graph or regular refresh. The flow is
standalone; canonical solution admission and native versioned documentation are
pending. The provider failure-stop branch is saved but was not deliberately
fault-injected. At that bootstrap handover the post-repair live-request branch
had not been invoked with a fresh seed; the subsequent increment below proves it.

### Accepted retained-selection expansion — 24 October

The same manual flow now contains a48-DOI selection, derived from48 independently
hash-verified accepted OpenAlex originals. One native run succeeded in206.8seconds:
45provider requests succeeded and three retained observations were reused with
zero provider recollection. All48 raw entries reconcile to the selected DOI set.

Independent M365 GETs verify all45 new raw files; the three prior raw-file hashes
are reused with exact unchanged native IDs/ETags/lengths/modification times.
All48 raw envelopes total43,348bytes. The separate complete manifest is79,706bytes.
The original three raw files and original accepted marker remain unchanged.
Full native readback matches the selected candidate and physical connection;
the flow is restored Stopped with no recurrence.

Private receipt: `private/ops/2026-10-24-opencitations-48/acceptance.json`.
The accepted three-DOI replay evidence is reused for the unchanged cached
verification algorithm. A48-record replay was not separately invoked; that
cardinality is not represented as fresh replay proof. No new test suite or
diagnostic flow run was added. Canonical solution admission/versioned native
documentation and deliberate provider-failure injection remain unproved.
