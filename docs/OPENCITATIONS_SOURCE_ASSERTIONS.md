# OpenCitations archived source assertions

This increment joins the accepted48-DOI citation-count and bibliographic metadata
snapshots into the existing Archived source assertions consumer. It makes no
provider requests and retains the original observation times, complete responses,
raw hashes and archive identities. These are unadjudicated source observations;
they do not establish canonical publication metadata or person/organisation links.

## Preparation and native changes

`scripts/prepare_opencitations_assertions.py` requires the accepted manifests and
their independent raw-byte receipts. The selected DOI sets must match exactly.
It produces48 assertions, one combined manifest and a uniquely named ready packet.
The packet references98 existing files:96 raw observations and the two source
completion manifests. Only three support files are uploaded, create-only. The
existing shared ready pointer and all original archives remain unchanged.

`scripts/extend_opencitations_assertion_consumer.py` extends the existing manual
consumer from an exact native preimage. It preserves the entire protected upsert
writer, connection reference and concurrency one. Five actions change or are
added; optional packet-name input preserves the existing default route. The
action guard accepts only the exact OpenCitations prefix,64 lowercase hexadecimal
characters and `.json`. Power Automate rejects JSON Schema `pattern` on this
trigger, so validation is performed by the action guard.

OpenCitations rows use `publication_enrichment_assertion` and keep both complete
observations in SourceProjectionJSON. Metadata no-hits and multiple matches stay
explicit; no arbitrary record is selected. SourceProvenanceJSON records the
metadata observation and combined source scope; count observation time remains
separate in the complete projection. No common observation-time claim is made.

## Invocation and recovery

PAC updates must compare the exact Stopped native clientdata preimage before
saving, followed by full native readback. In this environment, management Run
discarded the optional body; the callback tool silently fell back to that route.
The Logic Flows connector route returned connection-not-found and created no run.
Do not retry these unchanged routes or create a new connection.

The bounded import instead pins the one prepared packet path in Guard_packet_path
while Stopped, saves/readbacks the exact definition, then invokes the manual
management route with no body. After terminal reconciliation, restore the general
candidate and verify the complete definition, references and Stopped state. Keep
each operation handle and reconcile uncertain outcomes before another invocation.
The two initial inputless invocations replayed the existing DataCite packet and
did not constitute OpenCitations import proof.

Private evidence: `private/ops/2026-10-24-opencitations-consumer/`. Native identifiers
and raw snapshots stay there. Native versioned documentation publication remains
pending. This increment does not enable recurrence, refresh a shared model, change
canonical publications, send messages or alter the retained Crossref operation.

## Accepted native result — 24 October 2026

The bounded import succeeded in77.43seconds. All48 create and48 saved-field
verification repetitions succeeded with complete, untruncated readback. Independent
list reconciliation found94 unique assertions:48 new exact OpenCitations
projections/provenance records and46 prior records with unchanged stored fields,
versions and ETags. The volatile transport `odata.id` URI is excluded from that
stored-field comparison. All99 earlier OpenCitations archive files retained exact
IDs, ETags, lengths and modification times; only the three prepared support files
were added. Their uploaded bytes were independently downloaded and hashed.

Full PAC native clientdata readback after restoration exactly matches the general
candidate. Flow API confirms Stopped, manual concurrency one and the original
logical reference. The existing physical connection resolved when Started and was
preserved. Provider requests: zero. No new OpenCitations replay or failure fixture
was run; unchanged protected-writer evidence is reused. The98-item raw guard
container passed, but the tool rejected its full repetition listing as too large;
that listing is not claimed as independently retrieved.
