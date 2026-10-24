# OpenCitations incoming citation-link enrichment

This collector extends the existing48-DOI archival selection with incoming
citation relationships. It reuses the accepted DOI identity originals and common
archive/replay guards. Count and bibliographic metadata observations are not
requested again; the earlier count total344 is planning evidence at its own
observation times, not a forced equality for this later response.

The provider's [Index v2 API documentation](https://api.opencitations.net/index/v2)
defines `/citations/{id}` as incoming citations for the selected identifier.
The anonymous route uses the same existing access and CC0 data basis as the count
collector. Sequential two-second pacing stays below the documented180requests
per minute per IP. No token, grant, connection or licence change is introduced.

## Native behavior

`scripts/prepare_opencitations_citations.py` reuses the qualified metadata builder.
It changes the capability fingerprint, endpoint, response validation, raw prefix
and complete marker. Each response retains all unknown fields, complete citing
and cited PID strings, OCI, creation/date, timespan and source self-citation flags.
The stored creation field is provider publication-date evidence, not a locally
asserted event timestamp. No quality, impact or confirmed collaboration follows.

- Validate array shape, nonempty identifiers, exact selected cited DOI and unique
  OCI within each response. Native schema has a5000-row fail-closed ceiling;
  it never truncates an oversized response into a complete result.
- Empty HTTP200 arrays explicitly mean no incoming citations in that response.
  Transport, schema, identity or archive failure stops further provider requests.
- Save/read back the full envelope before recording the DOI as complete.
- Complete only after all48 DOI responses and the final manifest read back exactly.
- The cached branch reuses the established no-provider/no-write archive check.
  No additional cached replay or deliberate fault-injection run is required to
  restate unchanged common-algorithm evidence.
- Keep per-query memberships separate from distinct OCI counts: aliases or overlap
  across selected DOIs must not be silently dropped from raw responses.

This is incoming citation acquisition for a selected archived identity set, not
outgoing references, whole-corpus coverage, current universal counts or accepted
canonical relationships. It has no publication/model/list writes, recurrence,
email, count/metadata mutation or Crossref effect. Final intended state is manual/
Stopped with the existing SharePoint connection. Standalone solution admission
remains separate.

## Evidence

Native receipts and raw data stay in ignored
`private/ops/2026-10-24-opencitations-citations/`. Native save/readback and the
single actual acquisition are accepted:48 successful provider responses,
344 citation observations and344 distinct OCI identifiers in266.56seconds.
All48 raw envelopes were independently downloaded and byte/hash checked;
their141,790 bytes preserve complete responses and original observation times.
The final complete manifest retains the exact48-DOI provenance selection.
All102 prior OpenCitations archive files retain their IDs, ETags, lengths and
modification times. No count/metadata reharvest, replay or failure fixture was run.
The final native definition and existing reference read back exactly; manual
concurrency one and Stopped state are restored. Service-added authentication
annotations are explicitly compared, with no other expression normalization.
