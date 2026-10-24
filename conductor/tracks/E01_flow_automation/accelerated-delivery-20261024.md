# Accelerated source delivery — 24 October 2026

User direction: bootstrap from existing native flows and archives, minimise repeated
tests/runs, and use FlowAgent/PAC to deliver missing ingestion/enrichment work.

## Delivery rules

1. Inventory once through qualified PAC; match canonical purpose and native IDs
   before creation. Activated means configured state, not successful scheduled operation.
2. Reuse accepted source archives, schema mappings, connection references and
   source-specific runtime receipts. Do not recollect an accepted baseline solely
   to prove deployment or restart complete tests for documentation-only changes.
3. Existing solution-aware flow updates use the qualified PAC/Dataverse same-ID
   route and native reference representation. FlowAgent may be used where its
   operation/authentication is qualified; do not retry its unchanged expired
   authentication or the rejected Crossref save route.
4. Capture one fresh preimage; apply the smallest diff; read back exactly once
   after confirmed save. If uncertain, reconcile the operation before any retry.
5. Reuse unchanged verification. For changed behavior run only affected checks and
   one bounded real source-to-archive path with its necessary replay/recovery check.
   No automatic repeats, broad-suite runs per source, receipt-only diagnostics or
   provider reharvesting. Retain coherent integration/release security gates.
6. A test failure requires diagnosis, not another identical run. Keep first-failure
   evidence. Do not disable CI/security checks globally to accelerate delivery.
7. Preserve original Crossref Running handle; no cancellation, duplication or
   original-flow deployment while Running. The isolated qualifier stays Stopped.
8. Access/entitlement gaps remain conditional; scaffolding is not source ingestion.
   No new connections, consent, licences, contacts or email delivery.

## Native inventory and implementation queue

Full native collector trigger/state readback is now recorded in
[source flow setup](../../../docs/SOURCE_FLOW_NATIVE_SETUP_20261024.md).
ClinicalTrials is saved weekly but Stopped; source archive commit is manual.
OpenAlex is outside this selected native-name inventory and needs exact route
reconciliation before any replacement is considered.

Fresh PAC metadata inventory is retained privately as
`source-flow-inventory-20261024.pac.txt` with its FetchXML query in
`private/ops/2026-10-23-e01-current-state/`.

| Work | Disposition |
| --- | --- |
| ARC, ARDC, DataCite, DoRA, MRFF, NHMRC, PubMed, QGIP, ROR collectors | Existing Activated native objects: reuse; no replacement or bootstrap rerun |
| ClinicalTrials collector | Existing Draft object and accepted ingestion/recovery evidence: reuse; enabling recurrence remains distinct from setup |
| Archived assertions, ARC award export, NHMRC/MRFF typed consumers | Existing Draft objects: reuse accepted source-to-output evidence; do not confuse Stopped operator-run consumers with missing collectors |
| Crossref | Existing Activated collector; current original generation must reconcile before selected optimised pair deployment |
| Crossref independent lanes | Candidate already prepared; terminal checklist controls readback, recovery and real continuation |
| ANZCTR / WHO ICTRP / GrantConnect | No accepted supported machine route in current source disposition: defer, avoid repeated unchanged probes |
| Semantic Scholar | Optional enrichment: reuse DOI/PMID bootstrap and archive contracts; endpoint/terms/native implementation still needs qualification |
| Lens | Conditional existing institutional entitlement; no speculative deployment |

### Next independent increment delivered — 24 October

Semantic Scholar remains deferred after current provider licence review; no
request or contact was made. OpenCitations DOI count enrichment was selected and
implemented through FlowAgent using three byte-verified accepted DOI originals.
Native save/readback, interrupted archive recovery without repeated provider
requests, independent saved-byte verification and normal no-write replay pass.
The manual standalone flow is restored Stopped. See
[implementation and evidence limits](../../../docs/OPENCITATIONS_ENRICHMENT.md).
Crossref remains untouched and its existing monitor stays Active. No canonical
model/register field writes, recurring refresh or full citation-graph coverage
are claimed. Canonical solution admission/native documentation remain pending.

The retained-selection expansion now covers48 archived DOI identities: one native
run made45successful new provider calls and reused three existing raw observations.
The original four archive identities/ETags/lengths/times remain exact. Independent
new raw reads and complete manifest verification pass; same flow restoredStopped.
Reuse prior replay evidence rather than adding a48-record diagnostic invocation.
See the same implementation leaf and private48-DOI acceptance receipt for limits.

Execution order: reconcile existing objects and accepted receipts first; implement
only an evidenced missing diff, then one relevant runtime proof. Do not reopen
accepted sources merely because a historical checklist remains unchecked.

This inventory does not establish exact current recurrence, last-run success,
checkpoint freshness or consumer/model admission. Read these only when the next
selected effect depends on them, preserving disjoint object owners.
