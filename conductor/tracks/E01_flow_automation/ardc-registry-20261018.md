# Complete public ARDC registry acquisition

The existing ARDC collector has a same-ID full-registry candidate saved and read
back. Its initial native baseline was last observed Running. Full acquisition and weekly
updates are not yet accepted; preserve the exact private active run checkpoint.

The selected source is the public Research Data Australia metadata registry.
Its official OAI-PMH provider supports canonical RIF-CS (`metadataPrefix=rif`),
continuation tokens, second-granularity change datestamps and transient deletion
headers. Bounded public qualification returned 436,536 records, 100 per page.
That count is scale evidence, not proof that the baseline has acquired them all.
Underlying research data files and other repositories' original records are
outside this metadata-source acquisition boundary.

`prepare_ardc_registry_harvest.py` reuses the accepted archive parent and existing
SharePoint binding. It saves complete native HTTP XML values, Identify and
ListMetadataFormats responses before record interpretation. Each raw page is
read back and checked for content equality. This does not certify original
compressed HTTP transport bytes. Native XML retains all namespaces, metadata,
origin/source identifiers, datestamps and exposed deletion headers.

The baseline enumerates the full published RIF-CS registry without a mutable
datestamp filter. This avoids ordinary metadata edits moving records out of a
long baseline. The initial cutoff remains the high-water mark for subsequent
overlapping change acquisition. Source pagination tokens are retained and used
according to OAI-PMH's exclusive resumption-token request form.

Terminal token, provider total, received records and unique OAI identifiers must
reconcile before a complete manifest is saved and read back. A completion marker
is written last. Page/time guards fail instead of accepting a truncated corpus;
the failure path exits paging rather than repeatedly sending a failed request.
Previous successful archives and markers are never overwritten.

Updates use a seven-day overlap and a full reconciliation after 28 days. Since
deletion headers are transient, retain observed tombstones and earlier raw
archives; periodic full inventories are still needed. No downstream deletion,
affiliation decision, register or model write is performed by this collector.

The weekly trigger constructor prepares Monday 04:00 Australia/Brisbane with
concurrency one. It will be applied only after terminal baseline and catch-up
qualification. A Started manual baseline is not an enabled weekly service.

Exact handoff, preimage, rollback packet, saved graph, public qualification and
active run are under `private/ops/2026-10-18-ardc-broad-acquisition/`; the handoff
receipt is in the existing release-followup directory. Shared source consumers,
authentication recovery, solution membership and release files retain their
existing owners.

- [Official ARDC OAI-PMH provider](https://documentation.ardc.edu.au/rda/oai-pmh-provider)
- [ARDC metadata harvesting and incremental dates](https://documentation.ardc.edu.au/rda/oai-pmh-metadata-harvesting)

Subsequent Flow management CLI observation reached Conditional Access
sign-in-frequency expiry (AADSTS70043). This does not establish a terminal
cloud-run state. Preserve the submitted handle and observe it after the existing
authentication owner restores the qualified route; do not resubmit on expiry.
