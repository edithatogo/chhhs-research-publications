# DoRA retrieval and native documentation — 24 October 2026

## Documentation completed

The saved PubMed57-action and DoRA108-action response-copy changes were published
as17stable-ID SharePoint updates. Saved bytes and prior versions passed. Guide18,
catalogue19 and43reopened native Loop sources retained existing identities and
unselected content; both updated sources and58/109preview elements reconciled.
Later DoRA hardening has its own versioned successor described below. Historical
snapshots remain history, not proof of the current graph or runtime performance.

## Measured retrieval constraints

The accepted DoRA baseline has709records. Its record loop took80.03minutes inside
an89.77-minute generation; the preceding generation took177.91minutes. The old
five-second per-record delay alone represents59.08minutes at that record count.

Three accepted records expose Last-Modified but no ETag. Normal and matching/older
If-Modified-Since requests all returned200 and complete HTML: nine record requests
provided no conditional-download saving. The two standard public OAI/REST routes
checked returned404; other possible interfaces remain unqualified.

The provider's published robots policy specifies Crawl-delay:10. A temporary
two-second candidate was corrected before any native collection ran. The current
saved graph uses10seconds and serial concurrency one. Faster crawling is not the
selected optimisation.709records require118.17minutes of programmed spacing alone,
so a one-hour daily full-HTML sweep cannot meet this provider policy.

## Saved hardening and the next optimisation

The110-action graph has a fresh Boolean provider-failure latch. The existing handle
guard checks it before delay/request; a failed or timed-out HTTP action sets it,
preventing further provider requests in that generation. This includes429 reported
as a failed HTTP action. Existing failure receipts/last-good preservation remain;
there are no new retries or concurrent requests. Failure-latch runtime proof is
pending; structural tests and exact native save/readback are separate evidence.

Flow identity, physical connection, Started, daily04:30Brisbane, concurrency one,
source scope, provider URL, raw HTML serialization/readback, own-DOI extraction
and manifest/checkpoint guards are preserved. No additional full collection was
invoked. The next natural occurrence supplies performance/integrity evidence.

The published sitemap is available:35,073URLs/4,453,597bytes, containing all709
accepted publication handles. This provides a candidate bulk version inventory.
Three sampled sitemap timestamps differ from HTTP Last-Modified by10or11hours;
they remain opaque tokens, not certified UTC dates or acquisition cutoffs.

`scripts/dora_change_inventory.py` maps the complete required handle set, exposes
gaps, rejects duplicate selected handles/entities and preserves exact version
tokens. Its local selector defaults to fetching rather than reusing. Reuse needs
independent qualification of source version-change semantics plus the original raw
file ID, ETag, length, hash and provenance. It is not deployed in the native flow.
No unchanged URL, elapsed cache age or stable timestamp alone establishes freshness.

Remaining implementation is to qualify version changes/index freshness, bootstrap
verified raw references and migrate the producer/consumers together, retaining
complete membership checks and periodic full reconciliation. Do not carry all
35,073sitemap rows through per-record flow history. If that reduced workload still
exceeds capacity, retain the measured deficit for a separate bulk-worker decision.

Private receipts: `private/ops/2026-10-24-ingestion-documentation/` and
`private/ops/2026-10-24-dora-retrieval/` in the primary checkout. Crossref's retained
run, archives, monitor and terminal-gated19-query deployment remain separate.
