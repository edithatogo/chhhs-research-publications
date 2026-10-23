# E01-OA — Open-access paper archiving and publication linking

Status: **complete — operator-run technical implementation and native documentation
accepted on 19 October 2026**. This E01 implementation leaf does not reopen the
accepted publications release. Conditional standalone provider admission and later
operational/business adoption remain separate, as recorded below.

## Outcome and architecture

For an existing canonical publication with an eligible accessible full-text copy,
retrieve the paper through a supported route, save it in an appropriate versioned
SharePoint document library and expose the saved-document link in the publication
collection. Preserve the original external links, article version and provenance.
Use Power Automate as the deployed runtime; local scripts prepare/check artifacts.

Existing source flows retain all acquired raw metadata and project candidate
locations into the existing publication/enrichment layer. A **separate operator-run
archival flow** reads committed eligible publications for a bounded backfill or
incremental batch. It owns file retrieval, persistence, reconciliation and linking.
Metadata intake must succeed independently of PDF availability. A callable child
flow may be adopted only if supported by the existing solution and connections;
it is not required for the first usable implementation. Do not add a new service,
queue framework, per-paper approval process or mandatory model/dashboard change.

## Provider roles and retrieval policy

- Crossref: retain relevant `link` entries with content type, content version and
  intended application plus licence evidence. A TDM/similarity-checking link does
  not automatically permit institutional archiving. DOI landing URLs are not PDF
  URLs; the `link` field does not guarantee publisher access.
- OpenAlex: retain supplied OA locations, direct PDF URLs, versions and licences
  where present. Reuse already-retained responses before another API call.
- Europe PMC / PubMed / PMC: retain explicit full-text links and PMCID mappings.
  Use currently documented supported retrieval services/datasets for the selected
  resource; do not turn ordinary article-page PDF routes into an assumed supported
  bulk interface. Preserve XML/HTML as distinct formats where explicitly supported;
  do not label a non-PDF response as a saved PDF.
- ORCID: use existing work identifiers/external links for discovery and provenance.
  It is not a full-text host or authority to merge people/publications by name.
- Unpaywall: add DOI-scoped enrichment/fallback to the existing enrichment path,
  not a new independent publication collector. Retain complete responses before
  projections, DOI, query time, OA locations, version and licence, including nulls.
  Reuse OpenAlex/retained locations first; call for missing/stale/failed candidates
  with bounded cache/retry policy. Configure an existing approved contact email
  privately as required by its DOI API; no invented identity or new API-key service.
- Google Scholar: excluded from automated collection/retrieval. Manual discovery
  may supply an identifier for verification through supported original sources;
  no scraping, CAPTCHA bypass or third-party scraping subscription.

Try already-supplied eligible direct file URLs first, then supported PMC resources
and DOI-based fallback locations. Preserve alternatives and select deterministically
by supported access, article version and licence suitability. A successful HTTP
response/free-to-read flag is not sufficient permission to archive. Ambiguous or
restricted copies remain link-only with a reason; no new human approval queue.
Respect provider rate limits, Retry-After and applicable terms; do not send tenant
credentials/cookies to external hosts. Restrict schemes/redirect destinations to
qualified public endpoints, reject private/internal destinations, bound response
size/time/redirects, and validate file format and publication identity before save.

## Storage, identity and recovery

Evaluate existing libraries/content types first; reuse a suitable publication-paper
library or document area. A new dedicated library is justified only if existing
storage cannot meet the file, metadata, access and versioning requirements. Keep
raw acquisition metadata in its existing source archive; papers have their own
file purpose. Use safe deterministic filenames, not raw DOI/CanonicalKey strings
containing filesystem/SharePoint-reserved characters.

Use the existing CanonicalKey as the parent identity; retain DOI/PMID/PMCID,
provider/location, original/final URL, retrieval UTC, article version, licence URL
and evidence, content type, bytes and SHA-256 in suitable existing/new fields.
Record stable SharePoint file/item identity, saved URL and output revision. Keep
multiple legitimate versions/locations associated with one publication; never
silently replace an edited/curated file or mislabel accepted versus published copy.

Deduplicate using publication + article version + content hash, with exact native
identity reconciliation and concurrency protection. An unchanged replay creates no
new file/revision/link. A changed source file is retained as an explicit revision
or distinct version under the qualified storage policy. Resolve uncertain creates
by stable identity/hash before retrying. A file saved but not linked must resume
at link reconciliation, not download/create again. Register status updates must
not retrigger archival loops or overwrite unrelated intake/enrichment fields.

Suggested logical states (adapt to existing contracts, do not create a parallel
registry): eligible/discovered, retrieval pending, retrieved, saved, linked,
link-only/not eligible, retryable failure and terminal failure. Reader-facing
success means saved bytes, correct association and working authorised reader link,
not a local path or a downloader's `Downloaded` value. Reconcile historical local
PDF statuses honestly before displaying an archived-paper metric.

## Implementation plan

- [x] E01-OA.1: Inspect exact current source/native definitions, accepted register
  fields, local downloader and library capabilities. Coordinate one writer per
  collector, register, library and solution with existing chats. Reuse current
  source scopes and in-flight handles; do not take over ongoing acquisitions.
- [x] E01-OA.2: Prepare the smallest retained-location/Unpaywall enrichment and
  storage-field contract changes. Preserve provider distinctions and raw originals;
  define safe filenames, eligibility, identity, retry and partial-success handling.
- [x] E01-OA.3: Build one separate operator-run Power Automate archival definition
  for both backfill and newly eligible records. Bootstrap CLI/API-first using the
  qualified existing route: PAC for supported solution lifecycle and FlowAgent
  for its actually exposed supported authoring operations. Check schemas, HTTP
  connector entitlement/DLP and exact target access before dependent effects.
  Tool availability/login or a local candidate is not native save acceptance.
- [x] E01-OA.4: Deploy through the existing native owner, save exact graph/bindings/
  state readback, and qualify one real eligible paper's retrieved and saved bytes,
  hash, correct register association and existing authorised reader access.
  Verify unchanged replay, partial-save/link recovery and preserved human edits
  with focused evidence; reuse prior valid checks instead of broad test expansion.
- [x] E01-OA.5: Wire minimal collector/enrichment integration through the owners;
  qualify a bounded backfill and incremental changed-record path independently
  of metadata intake. Leave schedules/notifications/sharing unchanged.
- [x] E01-OA.6: Add supported components to the exact existing Power Platform
  solution. Verify native membership by stable ID; libraries/external dependencies
  remain explicit companions, never fictional solution members. Preserve backups,
  flow state, rollback and known migration permission boundaries. Record an exact
  unresolved membership gap if the existing HTTP403 still applies; no repeated
  unchanged denial, package ZIP surgery or broader permission request.
- [x] E01-OA.7: Update dataset field guide and canonical flow graph; generate BPMN
  2.0, Petri net, Mermaid, Visio and existing image formats through maintained
  generators. Publish affected assets/pages through versioned SharePoint delivery
  and native Mermaid in Loop, preserving unrelated content/human edits. Record
  exact readback or an explicit documentation-pending handoff.
- [x] E01-OA.8: Reconcile scoped commits, technical handoff, solution/companion
  status and completion evidence with the release owner. No optional broad package
  rebuild or dashboard redesign solely to close this increment.

## Acceptance and boundaries

Complete implementation requires a natively saved flow and real saved-paper/link
proof, not just source code, a local PDF or a successful flow run. Retain evidence
for content integrity/identity, licence selection, exact file/version, correct
parent linkage, existing authorised reader opening, unchanged replay, retry and
preserved edits. Test only changed behaviour plus required integration gates.
Source with no eligible copy remains a usable linked publication with an honest
reason. A failed paper must not block ingestion of other publications.

No new consent, licence/capacity purchase, widened access, sharing, schedule,
notification or production cutover is implied. A denied operation remains unproved;
use an already-permitted supported route when available. Keep tenant IDs, response
payloads, credentials and paper binaries in approved private storage. The technical
handoff distinguishes implementation, native acceptance, packaging and later
operational adoption. Do not claim the whole goal complete while required native
or documentation/solution evidence remains missing.

## Official implementation references (recheck at execution)

- [Crossref full-text access](https://www.crossref.org/documentation/retrieve-metadata/text-and-data-mining/)
- [Unpaywall DOI API](https://data.unpaywall.org/products/api) and [location schema](https://unpaywall.org/data-format)
- [PMC supported retrieval](https://pmc.ncbi.nlm.nih.gov/tools/pmcaws/)
- [Google Scholar automation/bulk guidance](https://scholar.google.com/intl/en/scholar/help.html)

## Completed technical handover — 19 October 2026

The canonical operator-run flow is published and Stopped, with all runs terminal.
Real failed-source fallback and non-destructive changed-content refresh pass;
unchanged replay, saved-but-unlinked recovery, bounded backfill, integrity,
existing reader access and canonical solution membership remain accepted.
No further individual-record investigation or native run is required.

The complete five-group harness passes under the existing isolated Python3.15
environment:2,040 tests (8 optional skips),446 project checks, web-first contracts,
Conductor structure and tooling presence. All73 pytest-function tests pass.
Evidence: private/ops/2026-10-18-oa-paper-archiving/real-qualification-cases/
qualification-acceptance.json and technical-handover.json.

Conductor transferred only the affected documentation objects after their prior
owner became unreachable. Final publication passes:5 updated assets of307,
guide10/catalogue12/Loop54/marker23;38 exact reopened Mermaid sources, other37
preserved;171 OA preview elements. Prior versions, identities, layout and recorded
access shapes are preserved. Graph bodies/images and executable runtime are
unchanged by documentation. Receipt: private/ops/2026-10-19-oa-final-documentation/
acceptance.json, generationa61c73d7…50ca896.

Source106a6a8 adds three DOI-bound OUP eligibility predicates. Published definition
normalized SHA256 is c226d4e749e1efb9b27487f1a0debbec4e4d585ec3ece4e96222091ab3210407.
Canonical workflow membership is accepted; SharePoint storage/four fields are
external solution companions. Maintained source handoffs are operator-run;
standalone EuropePMC/ORCID input admission remains conditional on accepted inputs.
No schedules, sharing, permissions, production adoption or business decisions changed.
The release/report/source owners retain their disjoint objects. Handover and stop.

Historical execution evidence follows; earlier pending statements are superseded
by this completed handover and its accepted receipts.

### Native storage increment

Additive OAArchiveURL(URL), OAArchiveState(Text), OAArchiveManifest(Note) fields
and disjoint `05 Full-text papers` folder are natively created/read back. All
original field identities/types are preserved; existing library settings and
register rows are untouched. A second apply resolved existing fields/folder and
sent zero mutations. Receipt: private/ops/2026-10-18-oa-paper-archiving/storage-acceptance.json.
The reusable setup adapter is `scripts/setup_oa_paper_storage.mjs`; six location
tests now include exact best-location provenance. One real registered DOI's
Unpaywall API call returned200 with matching DOI and four CC-licensed locations;
raw original is retained privately. This is discovery, not paper-save acceptance.

Next: build/validate the separate operator-run native archival graph against the
qualified Default-prefixed environment and current SharePoint binding, qualify
create-only binary transport/content comparison, then verify a real eligible paper
and unchanged replay. No native flow has been created yet. Core supplied settled
ROR replay graph for a separate versioned documentation update before R19; preserve
that queued documentation request and do not mutate its collector.

### First native archival path accepted — 18 October

The separate OA flow is now natively saved (stable identity in private receipts),
with exact definition/binding readback. Operator-run management invocation works
without input when the bounded commissioning selection is saved/read back first.
Inputful FlowAgent callback discovery failed AzureCLI auth; no run started then.
The maker page initially remained blank; no competing recovery was attempted.
Two native template errors (filter parentheses and quoted GUID literal) and the
connector's site-relative folder requirement were corrected from exact failures.

A real registered PLOS paper was retrieved, natively saved, byte-compared and linked
to its existing CanonicalKey. Independent download/saved SHA-256 matches across
3,453,818 bytes; extracted PDF contains the exact registered DOI. Existing browser
access opened the17-page saved PDF and its first page was visually inspected.
Unrelated citation/review fields are preserved. Unchanged replay left the entire
register row and native file identities/ETags/timestamps/lengths unchanged.
Receipt: private/ops/2026-10-18-oa-paper-archiving/paper5-acceptance.json.
The failed first content-retention attempt is preserved; its recorded reservation
and folder were reused, not duplicated. Runtime HTTP success/run Succeeded alone
was not acceptance: the first run caught its per-record failure and did not save a
paper. Current generic batch filter has been restored and flow is Stopped; no
schedule/sharing/access changed.

Source `scripts/prepare_oa_archive_flow.py` and four focused write-gate tests now
exist (ten OA tests total). **Goal remains incomplete**: full provider/host and
version-refresh handling, early saved-but-unlinked recovery without re-download,
terminal/link-only persistence, native content-hash provenance, solution membership,
OA field-guide/diagrams and versioned SharePoint/Loop publication remain. These
are implementation tasks, not waived acceptance gates. Next bounded operation:
implement early saved-state recovery and persistent exception outcomes in this
same stable flow, then verify changed behaviour against the accepted paper.

ROR documentation ownership explicitly transferred to the release lane before any
ROR documentation write began here. It owns only settled ROR monthly assets/page
content/Loop block for R19. This lane retains OA files/flow and future OA block;
coordinate shared page preimages after their ROR increment settles.

### Durable recovery/provenance increment — source prepared; native update pending

Added `scripts/oa_archive_recovery.py`: verified saved receipts precede the link
effect; an early saved-state branch checks parent identity, exact owned path, file
identity and ETag, and can link without provider requests or file creation. Conflicts
preserve the file. Link-only, invalid-content/conflict terminal outcomes and
retryable failures are persistent, while saved recovery receipts remain intact.
The revised graph passes local FlowAgent validation and focused tests but has
**not been deployed or run**: exact own-flow get_flow now returns AzCliAuthError.
The release lane retains authentication recovery; no competing login was started.
The accepted previous graph remains last verified Stopped; no new native flow
update was submitted after that failed read. This is the first recurrence of this
blocking condition for the update, with independent implementation still available.

The independent M365 route remains usable: `record_oa_paper_verification.mjs` read
the real saved bytes and conditionally persisted SHA-256/MD5, stable file identity,
ETag and verification time in the existing OA manifest. Native readback and
unrelated-field preservation passed; receipt hash-provenance-v2/acceptance.json
in the OA private evidence directory. The first proof attempt stopped before
mutation because the nometadata body lacked row ETag; the correction reads the
actual response ETag header, retaining conditional writes rather than wildcard.

Current official PMC guidance retires the OA web service (August2026). Added
`pmc_paper_resources.py` for exact-PMCID complete cloud metadata listings and
explicit versions/DOI/CC licence/source MD5. A real retained PMC observation for
the accepted paper supplies a PDF whose asserted MD5 exactly matches the already
saved bytes; no second download was needed. No version1 or latest-version guess
is allowed. `prepare_oa_retained_locations.py` also binds retained provider records
by exact DOI and raw hash; ORCID requires a self DOI rather than a related work.
These are preparers, **not yet wired native provider acquisition/projection**.

Next: after the existing owner restores exact flow access, install the revised
recovery graph on the same stable flow and qualify saved-but-unlinked recovery
without download/upload, then wire retained-location/PMC fallback and verify its
changed native path. Keep all remaining solution/documentation/provider/version
requirements open. Existing ROR documentation remains with the release lane.

### Recovery natively accepted; independent M365 Flow route qualified

The prior FlowAgent Azure-auth blocker is superseded for this exact OA flow:
existing `m365 flow get` succeeded without sign-in/profile changes.
`deploy_oa_archive_flow.mjs` uses that same authenticated client for exact Flow RP
preimage/history checks, one guarded PATCH, and graph/binding/Stopped readback.
The service rejected literal-array operands in native If expressions that the
local validator missed; corrected createArray expressions were saved successfully.
Rejected updates left the native graph exact/Stopped. Initial request-error output
was too broad; transport failures now record only status/service body privately and
print a bounded message, never Axios request/header objects.

A controlled saved-but-unlinked case used the already verified real paper and
retained full preimage. Run08584092831579990768432202670CU10 restored its exact
reader link. Recovery_metadata/Recovery_link succeeded; Download_paper, Save_paper,
Retain_Unpaywall and Reserve_archive were Skipped. Exact native file identities,
ETags, sizes and times are unchanged; SHA-256 and unrelated register fields are
preserved. Row comparison excludes only enumerated OData transport annotations
and native modification/version fields. Receipt:
private/ops/2026-10-18-oa-paper-archiving/saved-gap-acceptance.json.
This was a commissioned link gap, not a fabricated operational failure.

Management invocation returned HTTP200, not202; its first wrapper classified that
as uncertain. Native history was reconciled before any retry, proving exactly one
run. The wrapper now accepts200/202. No duplicate submission was made.
The staging check and enable command were initially combined in one shell cell;
the staging check passed, but this ordering did not enforce the repo's separate
failed-effect gate. Subsequent effect steps were separated and checked explicitly;
retain this ordering lesson rather than treating reconciliation as retroactive
proof of correct gating. No failed staging preflight or unintended run occurred.

The general bounded batch definition is restored in Stopped state with exact
graph/binding readback. Receipt: recovery-restore-native-apply/acceptance.json
in the OA private evidence directory. Next implementation is retained provider/PMC
selection and alternative/version processing; membership and versioned OA
documentation remain open. ROR documentation remains separately owned by release.

### Provider pipeline deployed; PMC trial awaiting exact effect readback

Native OALocationCandidates plain Note field is added/read back without changing
existing fields or rows. The exact same OA flow now reads optional retained
locations, discovers explicit PMC cloud metadata versions, retains complete
responses before eligibility projection, and calls Unpaywall only when needed.
Initialisation is outside the serial publication loop; candidates reset per record.
The saved receipt retains provider/version/licence/source MD5/attribution.
Exact graph/ref/Stopped adoption passed (providers-native-apply/acceptance.json).

A second existing registered paper was scoped for one manual PMC trial. Run
08584092824302183992269029338CU06 was last observed terminal Succeeded. **Its
child actions, file bytes and register effects have not been accepted**: M365 then
failed AADSTS70043 after token sign-in-frequency expiry. A diagnostic wrapper
initially printed undefined instead of its structured error; identifying the
actual error required bounded read-only correction. No invocation was repeated.
The existing release lane retains authentication recovery.

Own maker UI remained usable. Turn off was clicked for the exact flow and a fresh
More actions menu offered Turn on. API state readback remains pending. The source
graph is still the explicit ID7 commissioning selection; general batch restoration
is pending qualified access. The new run viewer failed includes-of-undefined;
its classic fallback navigated into the editor, where no edits or Save occurred.
Read-only classic run navigation then timed out; preserve its URL/handle rather
than replaying the run. Exact active checkpoint: OA private directory
`paper7-pmc-checkpoint.json`. No schedule or sharing was changed.

Source owner confirms Crossref raw payloads include full link/licence evidence but
OALocationCandidates is not yet projected. This lane owns that enrichment consumer;
reuse the source owner's terminal archive/provenance handoff when available rather
than changing the ongoing collector. `prepare_oa_retained_locations.py` now emits
the native field projection with exact DOI/raw-hash guards; unknown licences stay
unadmitted, and Crossref licence version/start/purpose must qualify. This is a
prepared producer interface, not proof of native collector projection.

Next native action after existing-owner recovery: inspect this exact terminal run
and source/file/register effects, restore general batch filter and verify Stopped
without resubmission. Then finish alternative/version processing and retained
source consumption, solution membership, and versioned OA documentation. ROR
documentation remains with release; do not overwrite its shared pages/assets.

Documentation pending: the current OA native graph and four OA fields require versioned field-guide/diagram/SharePoint/Loop publication after the selected definition and runtime path settle. No OA documentation publication is claimed.


## Reusable Codex goal prompt

This resumes E01-OA; it does not create a duplicate track or restart an in-flight
operation. Use the following user-entered prompt:

```text
/goal Complete E01-OA — Open-access paper archiving and publication linking, following conductor/tracks/E01_flow_automation/open-access-paper-archiving-20261018.md. Resume the existing checkpoint, reconcile any submitted run before retrying, and preserve current collector, authentication, documentation and release ownership. Reuse retained Crossref, OpenAlex, Europe PMC/PubMed/PMC and ORCID metadata; add DOI-scoped Unpaywall enrichment/fallback, not a new publication collector. Implement a separate bounded operator-run Power Automate archive/save/link flow, using qualified CLI/API routes first and supported PAC/FlowAgent operations where available. Save eligible papers in the existing versioned SharePoint area, link them to the correct canonical publication, retain licence/article-version/source/hash provenance, and implement deduplication, alternative locations, safe version updates and saved-but-unlinked recovery while preserving human edits. Keep metadata intake independent of paper availability and Google Scholar manual-only. Finish retained-source integration through the existing owners; qualify real native bytes, identity, authorised reader links, unchanged replay and recovery. Reconcile supported components into the existing Power Platform solution, with SharePoint dependencies explicitly recorded as companions. Update the field guide and canonical graph, generate BPMN 2.0, Petri net, Mermaid, Visio and image outputs, and publish through versioned SharePoint documentation and native Mermaid in Loop. Make scoped reviewed commits and a technical handoff. Use existing permissions and resources; leave schedules, sharing and production adoption unchanged. Report exact unresolved gaps honestly and do not equate local tests or a successful parent run with native acceptance.
```


### Local version and alternative-location increment — 18 October 2026

The prepared graph now supports an explicit source-version recheck, compares
previous saved bytes before creating another paper, retains prior-copy provenance
and immutable receipt sidecars, and guards final register writes by canonical
identity, lease and expected state. A serial loop tries at most ten qualified
locations, stops after a saved receipt or storage conflict, and retains distinct
retryable/exhausted outcomes. Missing PMC manuscript classification is ineligible
rather than guessed to be the published version. Default linked replay still skips
retrieval. These changes are local source only and have not replaced the native
item7 commissioning graph.

Focused OA checks: 38 tests passed before the manuscript-classification assertions
were strengthened; rerun result is recorded in the private local-tests-resume log.
Native acceptance, actual alternate-source/version behavior and complete runtime
hash provenance remain pending. The existing recovery owner still records70043
and capture3811 in CURRENT_STATE. No competing sign-in, deployment or run was
started. Preserve the exact item7 run and perform its reconciliation/restoration
first after qualified recovery.


### No-overwrite source and documentary graph — 18 October 2026

The prepared paper write uses SharePoint REST Files/Add with overwrite=false and
an octet-stream binary body. After the conditional create (including failed or
uncertain response), it reads exact-path metadata and compares persisted bytes.
This removes reliance on the connector CreateFile overwrite default; actual native
binary upload and concurrent-conflict behavior remain unproved. The existing
[Microsoft REST file guidance](https://learn.microsoft.com/en-us/sharepoint/dev/sp-add-ins/working-with-folders-and-files-with-rest)
is the supported API basis. No existing paper was changed for this preparation.

The field guide documents all four OA fields and distinguishes provider-asserted
MD5, independently observed SHA-256, source links and saved reader links. One new
canonical OA source graph (57 scopes/116 actions) generates Mermaid, BPMN, PNML
and editable VSDX; it is labelled parameterised prepared source, distinct from the
native commissioning definition. SVG rendering succeeded using the existing local
Chrome executable after mmdc's default bundled-browser lookup failed. No browser
profile, authentication or tenant state was changed. Focused checks:38 OA tests
and5 maintained diagram tests pass. SharePoint/Loop publication is pending native
graph settlement and the existing versioned delivery route.

PNG rendering also succeeded and was visually inspected at overview scale. The
full graph is dense and needs zoom; VSDX separates57scopes into pages. Native
SharePoint/Loop delivery and reader verification are still pending.


### Exact-client recovery check and canonical parent guard — 18 October 2026

After the release owner verified PAC/Dataverse recovery, one existing-client
read of the exact OA flow exited1 with `Error: No access token found.` No login,
profile change or native mutation followed. This supersedes70043 as the currently
observed M365 failure; it does not invalidate PAC qualification. Evidence:
`recovery-owner-followup-flow-get.json` and `.stderr` in the existing OA private
directory. Recovery ownership remains with release. The pending item7 run was not
resubmitted and its effects remain unobserved.

Source owner confirms the preserved Crossref acquisition has no accepted terminal
archive yet, and no accepted OpenAlex/EuropePMC/ORCID raw-work mapping was handed
off in its scope. Do not ingest partial pages or prior failed-run archives as
accepted inputs. The downstream OA consumer remains this lane's responsibility;
its native integration awaits accepted source mappings and qualified access.

Prepared selection now rejects blank/padded CanonicalKeys, preserving legacy
register placeholders instead of archiving against an absent accepted parent.
Focused OA checks:39 pass. The canonical documentary source hash is refreshed;
action/dependency structure is unchanged, so rendered images remain applicable.


### Native paper7 reconciliation and service corrections — 18 October 2026

After the owner restored the existing M365/FlowRP client, the original paper7 run
was observed directly without resubmission. Its parent succeeded but Archive_one
failed; PDF_base64 had InvalidTemplate because `$content` was selected on a String.
SharePoint has retryable_failure, no reader URL and no paper.pdf, with three raw
PMC/Unpaywall artifacts retained. Every unrelated row field matches the original
preimage. Evidence: paper7-browser-effect-reconciliation.json and the exact run
action/repetition captures in the OA private directory.

The PMC HTTP output is a binary/octet-stream envelope with `$content-type` and
`$content`; its raw-retention string is valid JSON. Explicit parsing now uses
that decoded string. PDF decoding selects the binary envelope only for PDF or
octet-stream content types and handles textual responses separately, then applies
the existing PDF format/size gate. This repairs the observed response-shape
failure; native changed-path acceptance is still pending.

The generic provider-v11 graph was restored Stopped with exact saved definition
and binding readback (after-paper7-generic-restore-apply/acceptance.json). The first
new candidate was rejected400 for nesting above eight levels, with no acceptance
claimed. The source now flattens redundant Try/scope/branch containers, keeps
saved recovery separate from retrieval, and treats an empty candidate loop as
link_only. Maximum action level is8;39 focused OA tests pass. The revised candidate
is being qualified on the same stopped flow. No schedule, sharing or new run was
enabled by reconciliation.


The flattened v16 graph saved with exact readback. One corrected scoped item7
run reached supported PMC discovery, skipped Unpaywall, downloaded and created a
file, then failed byte equality. Exact retrieved MD5 matches PMC's assertion.
Retrieved1,235,298bytes became2,030,319savedbytes with UTF-8 replacement characters:
the SharePoint HttpRequest string-body transport is not binary-safe. The flow
preserved its content-conflict outcome and skipped receipt/link writes. No saved
paper acceptance is claimed. Evidence:v16-paper7-byte-conflict.json; the run's
110-action readback required a second native page, retained before reconciliation.
The flow was disabled exit0 after its terminal run. Generic Stopped restoration
uses v16-after-trial-restore-apply. Next implement a supported binary-safe
server-side no-overwrite route; preserve this bad artifact and use a fresh attempt
after correcting the transport. Do not fall back to overwriting CreateFile merely
to make the content check pass.


### Binary-safe staged upload natively accepted for paper7 — 18 October 2026

The separate flow now uploads to a fresh GUID staging name through the binary
CreateFile operation, reads those staging bytes, and finalizes only after exact
equality. Finalization uses short SP.MoveCopyUtil.MoveFileByPath with source and
destination in JSON, overwrite=false, KeepBoth=false and no lock bypass. A first
MoveTo variant failed only because its527character URL exceeded the service
limit; the staged1,235,298bytes were independently exact. That401 was not an
authentication denial, and no recovery/login was attempted for it.

One corrected native run selected the supported PMC version, skipped Unpaywall,
saved the final paper, persisted its receipt and linked the exact publication.
Independent native file readback SHA256/MD5 match the retrieved/staged bytes and
PMC's asserted MD5. Exact DOI is present in PDF text. The authorised existing
browser opened the saved ten-page PDF; first-page title and DOI were visually
inspected. All unrelated publication fields match the original preimage. Actual
hashes are conditionally recorded in the native manifest. Evidence:
paper7-acceptance.json and v18-paper7-hash-verification/acceptance.json in the OA
private directory. The generic v18 graph is restored Stopped with exact full
definition/connection-reference readback; no schedule or sharing changed.

The prior failed artifacts remain retained. Explicit forceRefresh may recheck a
terminal technical outcome in a fresh attempt while ordinary replay still skips
terminal/linked records; previous-attempt provenance is carried into reservation
and saved receipts. Native atomic-conflict, default replay and version/alternative
changed-path evidence remain separate pending checks, as do source consumption,
solution membership and SharePoint/Loop documentation publication. Do not infer
full increment completion from this successful selected paper.

Supported finalization contract:
[Microsoft MoveFileByPath protocol](https://learn.microsoft.com/en-us/openspecs/sharepoint_protocols/ms-csomspt/eabb7cc0-dcb3-45b0-99f4-555bbe13e14f);
[maintained PnP REST serialization](https://github.com/pnp/pnpjs/blob/version-4/packages/sp/files/types.ts).


### Native conflict, unchanged replay and saved-link recovery accepted — 18 October 2026

The same server-side MoveFileByPath operation, overwrite=false and KeepBoth=false,
refused a controlled destination-exists collision between two disjoint new text
fixtures. Both files' bytes, identities, ETags and timestamps remained exact.
No accepted paper or register row was targeted; fixtures are retained. Receipt:
no-overwrite-qualification/acceptance.json in the existing OA private directory.

One default replay of linked paper7 skipped download, provider acquisition, save
and link actions. Its entire native row and13selected current/prior-attempt files
were byte-for-byte/metadata exact, with no new file or revision. Receipt:
v18-default-replay-acceptance.json. A separately labelled commissioned link gap
then exercised the corrected graph's saved-receipt branch: Recovery_metadata and
Recovery_link succeeded; Download_paper, Stage_paper, Save_paper, Unpaywall and
Reserve_archive skipped. The exact reader URL and verified SHA256 were restored,
all13file identities/ETags/times/lengths stayed exact, and every unrelated row
field reconciled. Receipt:v18-saved-recovery-acceptance.json. This was a controlled
technical case, not a fabricated claim of real operational failure.

E01-OA.2/.3/.4 now record their selected contract/build/real-paper acceptance
requirements as complete. E01-OA.5 source-producer integration and bounded generic
batch/incremental acceptance, .6 solution membership, .7 native documentation and
.8 handoff remain incomplete. Version/alternative changed-path qualification is
not inferred from the selected source success or these replay/recovery checks.


### OA documentation generation accepted — 19 October 2026

Versioned SharePoint assets (291 across36source snapshots), guide6.0 and catalogue8.0 are reconciled. Loop26.0 retains36native Mermaid blocks, with35previous blocks exact; the OA preview has127nodes and42clusters with exact logical IDs. The same release-marker identity now records a complete generation; saved bytes and previous-version history pass. Evidence: documentation/acceptance.json and documentation/marker-complete-plan/acceptance.json under the existing private OA directory. This closes the selected documentation transaction, not full E01-OA completion. Source integration, native version/alternative qualification and final handoff remain pending.

Solution membership is independently accepted by stable flow/workflow identity, exact graph, effective binding and Stopped state: private release-followup/oa-migration-acceptance.json. SharePoint storage and four fields remain external companions. Plan items .6 and .7 are now complete for the selected implementation.


### Accepted retained PubMed identity integration — 19 October 2026

The retained-source adapter reconstructs all1,274 accepted PubMed own-article payloads with exact contiguous chunk/count/encoding/length checks; reference-list identifiers are excluded.465 own-article PMCIDs reconcile to fresh native register PMID/DOI/CanonicalKey without conflicts.452 already match;13 are blank. The exact13-cell additive fill plan is privately prepared and source-owner handoff requested; no write is claimed. Three focused reconstruction/identity checks pass. Private evidence: retained-pubmed-identifiers.json, retained-source-parent-readback.json, retained-pubmed-register-candidates.json and retained-pubmed-missing-pmcid-plan.json in the existing OA directory. This advances .5 but does not establish full provider consumption or native incremental acceptance.


### Retained PubMed PMCID native fill accepted — 19 October 2026

The registry owner handed over exactly13blank PMCID cells. All13 own-article identifiers from the accepted raw archive are now conditionally saved and read back; fresh parent ID/CanonicalKey/PMID/DOI, stillblank and exactETag guarded each write. Unrelated fields and the full1,648-record keyset remain preserved. Evidence: pmcid-field-handoff.json, pmcid-fill-header-etag/progress.json (first savedcell) and pmcid-fill-resume/acceptance.json. A missing-bodyETag preflight and nullableDOI comparison stopped safely; headerETag and nullableidentity handling were corrected, first effect reconciled, no duplicate write. Ownership returned to registry owner. All465 accepted own-article PMCIDs are now represented. Native source-version/operator-input qualification remains pending; browser calls timed out and subsequent CLI run-ID/status reconciliation showed no new run.


### Native operator-input unchanged-version path accepted — 19 October 2026

Native operator run08584092704473072255935294464CU05 with publicationId7, afterId0 and forceRefreshtrue succeeded. PMC discovery/download, prior-version read/comparison and unchanged-receipt restoration succeeded; staging/save/link skipped. All13existing files and unrelated row fields remain exact; saved identity/URL/SHA256 are preserved. Evidence: version-refresh-acceptance.json and version-refresh-actions-complete.json in the OA private directory. Native UI requires numeric afterId0 rather than blank. Lifecycle after solution conversion must reconcile canonical workflow identity rather than infer activation from the predecessor runtime alias; exact canonical graph equals accepted source. This proves unchanged-source recheck only, not changed-content version or alternative-failure acceptance.


### Bounded five-publication native backfill accepted — 19 October 2026

Canonical operator run08584092686376159576156222794CU17, publicationId0/afterId595/forceRefreshfalse, completed records596–600. Two eligible PMC papers were saved and linked; three records retain explicit link-only reasons. Both native PDFs match providerMD5, exact ownDOI in extracted text and stable file metadata; actualSHA256 values are recorded/read back in their native manifests. Existing authorised browser links open13-page and2-page PDFs; first-page title/DOI visually verified. Citation, source, review and other unrelated fields are unchanged. Canonical flow is restoredStopped with exact graph. Evidence: backfill-acceptance.json and backfill-file-verification/ under the existing OA private directory. This proves real bounded backfill and consumption of retained PubMed PMCID enrichment; remaining provider admission/integration and alternative/changed-content qualification remain open.


### Five-record replay and qualified browser readback accepted — 19 October 2026

Run08584092677699170901765602522CU01 repeats the accepted records596–600 batch. All five complete native rows and11file identities/ETags/lengths/timestamps remain exact. PMC/Unpaywall acquisition, reservation, download, staging, save and linking all skipped. Canonical flow is restoredStopped with exact graph. Evidence: backfill-replay-acceptance.json and before/after snapshots in the existing OA private directory. The SharePoint CLI read encountered its existing browser-client AADSTS70007 boundary; that request was reconciled and not repeated. The already authenticated same-origin SharePoint browser route supplied exact readback; FlowRP CLI remained independently usable. No new permission, client substitution, schedule or sharing change occurred.


### Numeric PMC version ordering repair pending native save — 19 October 2026

The prior lexical S3 listing could select an unchanged older source before a newer version. Local source now retains original metadata keys and sorts numeric versions descending using a Select and reverse(sort(...)).18focused checks pass, and the pre-change generator exactly matches the accepted native graph. One canonical FlowRP PATCH was submitted; initial and later fresh readback retain the exact OLD graph, Stopped and bindings preserved. This is a failed native delivery gate, not deployment acceptance; no second PATCH or runtime test was submitted. Evidence: newest-pmc-version/reconciliation.json under the OA private directory. A supported solution-aware save route is being qualified with the release owner; documentation stays on the working native generation until that save succeeds. Crossref source owner independently accepted its complete1281lookup raw archive and lineage; consumer enrichment qualification is now available, not automatically admitted.

Function contract: [Microsoft workflow expression functions](https://learn.microsoft.com/en-us/azure/logic-apps/expression-functions-reference#sort).


### Crossref envelope consumption and unpublished-state diagnosis — 19 October 2026

The recovered stock SharePoint CLI downloaded an exact20,256-byte committed Crossref envelope for an existing canonical publication. The projector now handles the actual retained requested_doi/status_code/body envelope, verifies request status and both request/work DOI, and preserves the original envelope SHA256. Sixfocused checks pass. The real selected record supplies only an unspecified similarity-checking HTTP link, so zero PDF candidates are correctly admitted; no guessed PDF or field clearing was applied. Evidence: crossref-integration/projection.json in the OA private directory.

Native version repair: metadata explicitly maps stableworkflow to FlowRP resourceId. Resource-target readbacks still show the old published graph. A minimal definition-only save then returned HTTP500 XrmApiServerError0x80040203, identifying an existing ActiveUnpublished workflow row. Earlier unchanged published reads therefore do not establish that no draft effect occurred. No further PATCH is allowed until that exact unpublished row is inspected. Fresh readback retains old published graph, Stopped and bindings unchanged. Browser RetrieveUnpublished returned AccessDenied; authenticated PAC FetchXML for componentstate1 returned no rows and is not equivalent to RetrieveUnpublished. Preserve all receipts/draft; do not guess PublishXml workflow XML or publish all customizations. Supported native single-flow Publish is the selected route only after exact candidate/bindings inspection.


### Exact unpublished candidate and bindings verified — 19 October 2026

The native editor successfully read draftFlow=true through its first-party Power Platform service. A temporary observer of only that selected response captured HTTP200; it did not change requests, headers or authentication and was removed after capture. The native Draft definition exactly matches the intended numeric-order candidate (only normal service authentication annotation excluded); stable workflow/resource identity and every stable connection-reference field match the published baseline. The distinct workflowUniqueId identifies this draft version. Evidence: newest-pmc-version/native-unpublished-response.json and native-draft-acceptance.json in the OA private directory. This proves a saved draft, not a published/runtime update.

The new designer fails with Cannot read properties of undefined (reading includes). Its offered classic fallback loads, but explicitly says it displays the published version and requires the new designer for this draft. No Remove draft changes, Save or Publish was selected. Preserve both versions; qualify supported single-flow publish only after resolving that editor capability gap. Native editor inspection and cleanup are recorded in native-editor-inspection.json.


### Published numeric PMC ordering reconciled — 19 October 2026

The optional manual-trigger schema now explicitly includes required:[], resolving the native designer failure. The exact draft was inspected, the native checker reported zero errors/warnings, and single-flow Publish succeeded. Fresh published readback exactly matches the intended numeric-order graph (excluding service authentication annotations), preserves the logical SharePoint binding and confirms Stopped state. The selected paper baseline contains all13 existing files. Evidence: newest-pmc-version/manual-schema/published-stopped-acceptance.json and its source readbacks under the OA private directory. This supersedes the earlier pending-save/editor-gap checkpoint; it does not prove changed-path runtime acceptance. Next: one publicationId7/afterId0/forceRefreshtrue operator run, terminal action/file reconciliation, then restore Stopped and hand the accepted graph to the documentation owner.


### Numeric PMC selection native runtime accepted — 19 October 2026

Run08584092640425697502499761158CU07 succeeded for publicationId7/afterId0/forceRefreshtrue. PMC_version_keys and descending-version iteration executed successfully; unchanged-source detection and receipt restoration succeeded. Stage/save/link skipped. All13existing files are exact; only last_source_recheck and normal Modified/UIVersion fields changed. Fresh published graph matches source and canonical state is Stopped. Evidence: newest-pmc-version/manual-schema/qualification-acceptance.json, complete actions and before/after snapshots. This qualifies the numeric-order repair against a real unchanged source; genuine changed-content and alternative-failure cases remain unproved. Documentation owner receives the settled graph; full E01-OA remains in progress.


### Additive retained-candidate integration — 19 October 2026

The retained-source consumer now prepares additive candidate merges with exact parent identity/provenance, replay no-op and explicit overflow refusal. Empty projections cannot clear another provider’s candidates. Seven focused tests pass. Reprojecting the real retained Crossref envelope against a fresh native publication readback correctly yields no eligible PDF and no field mutation; evidence: crossref-integration/merge-acceptance.json. This is a real negative/no-op consumer case, not positive native producer deployment. Source owner has been asked for accepted EuropePMC/ORCID/OpenAlex retained manifests without new acquisition or collector takeover.


### Storage-effect alternative barrier prepared — 19 October 2026

A storage failure after staging could previously advance to another candidate even though an uncertain staging write required reconciliation. The generator now sets OA_stop_candidates before Stage_paper, preserving retrieval-only fallback while preventing additional sources after storage effects begin. Ten focused alternative/build checks pass. Candidate prepared privately under storage-recovery-barrier/candidate.json; native save/publication and changed-path qualification remain pending. The accepted published numeric-order baseline remains unchanged.


### Storage barrier natively published — 19 October 2026

Independent first-party native Draft GET exactly matches the candidate and stable binding. Temporary response observation was removed before publication. Native checker reports0errors/0warnings; single-flow Publish succeeded. Fresh canonical graph exactly matches source and state is restoredStopped. Evidence: storage-recovery-barrier/draft-acceptance.json and publication-acceptance.json. Runtime execution of Stop_before_storage remains pending; no existing-paper unchanged recheck can establish that branch. Next qualification must exercise an eligible new-file path and reconcile actual saved bytes/link, with uncertain effects preserved.


### Additional real link-only outcome reconciled — 19 October 2026

Run08584092633330802182773939941CU00 for publication10 succeeded. PMC and Unpaywall discovery yielded no qualified licensed PDF; link_only reason persisted and citation/review/source fields remain exact. Stage/save/link skipped, so this does not qualify the new storage barrier. Flow is freshly confirmedStopped. Evidence: storage-recovery-barrier/paper10-acceptance.json. Publication12 has a fresh unarchived baseline, but no run was submitted: the native editor returned a validation-service error. Preserve that baseline and use the existing details/operator route after bounded service recovery; do not duplicate paper10.


### Input-bearing invocation route inspected — 19 October 2026

Installed FlowAgent implementation provides a Logic Flows connector transport that delivers triggerBody inputs, with runtime discovery rather than hardcoded regional hosts. A bounded M365 read first failed with inferred-audience AADSTS500011; the installed documented Power Platform audience then returnedHTTP401. No invocation, callback extraction, new login/consent or cache transfer occurred. Native form remains blank; preserve stopped flow and paper12 baseline. Evidence: storage-recovery-barrier/input-transport-boundary.json. Retry requires exact metadata access through an existing qualified client or a functional native manual form; no unchanged authentication retries.


### Execution blocked with preserved native baseline — 19 October 2026

The input-form/service failure persists across bounded attempts: editor validation failed, details later renders but Run does not open its form, and the supported connector-metadata route returnsHTTP401. Fresh native history proves no publication12 run was submitted; canonical state is Stopped and all recent runs terminal. The real retained Crossref envelope for publication12 was consumed locally and correctly admits no candidate (HTTP/TDM links and TDM licence only). Remaining provider integration also awaits accepted OpenAlex/EuropePMC/ORCID retained manifests from their existing owner. No new acquisition, login/consent, permission change or duplicate run was made. Exact remaining scope and retry conditions: storage-recovery-barrier/blocked-handoff.json. E01-OA is incomplete; resume the same work when a qualified input route or accepted provider handoff becomes available.


### Accepted OpenAlex handoff consumed against fresh parent — 19 October 2026

Archive owner supplied a previously committed OpenAlex work, distinct from the earlier staged10pages. Manifest/acceptance hashes, native_commit_exact/consumer_commit and all6file byte/SHA checks pass. Fresh exactDOI register query resolves one existing parent831, although the historical baseline had none. The actual original work projects directly:4discovery locations,0eligible native candidates (null or other-oa licences/landing-only locations). Additive merge is a no-op; no field write or new acquisition occurred. Evidence: private/ops/2026-10-19-oa-source-handoff/oa-consumer-handoff-readback.json, oa-work-projection.json and oa-candidate-merge.json. This closes the selected real OpenAlex negative/no-op consumer case, not positive producer wiring, standalone EuropePMC/ORCID admission or native runtime/documentation gaps.


### Existing authentication and operator route recovered — 19 October 2026

The exact FlowRP CLI session expired. Reusing the existing Toolkit client, saved connection and MSAL form_post correction for the installed resource mapping succeeded; independent native flow/history preflight passed. Existing browser sign-in remains valid. Native More actions/Turn on aligned displayedOn state and enabled the previously disabledRun command; the real input form now works. One publication12/afterId0/forceRefreshfalse run08584092189206117718772497028CU12 is submitted and tracked without duplication. Evidence: auth-recovery-20261019/acceptance.json and paper12-handle.json. RestoreStopped after terminal reconciliation. Accepted48 OpenAlex handoff now supplies six exact native parent matches and a single candidate-cell handoff for1635; host qualification and write remain pending. These facts supersede earlier blocked-route/provider-absence summaries without reopening completed evidence.


### Storage barrier real save/link path accepted — 19 October 2026

Run08584092189206117718772497028CU12 succeeded for publication12. Stop_before_storage, staging/readback, finalsave, saved-byte comparison, receipt and linking succeeded. Independent native PDF bytes match providerMD5, exact ownDOI and stable file metadata; actualSHA256 is conditionally recorded/read back in the manifest. Existing authenticated SharePoint reader opens5pages, with firstpage title/DOI visually verified. Unrelated fields are preserved and fresh flow state is Stopped. Evidence: auth-recovery-20261019/paper12-acceptance.json, file-verification/12-evidence.json and native-hash/acceptance.json. This closes the selected successful storage-barrier execution; genuine changed-content and alternate-failure acceptance remain open.


### Qualified retained Frontiers route natively published — 19 October 2026

The accepted retained OpenAlex paper for exact native parent1635 has a qualified samehostHTTPS PDF redirect, exactDOI and explicitCCBY evidence. Source b0d18a6 adds only the narrow OpenAlex/cc-by/publishedVersion/fpubhDOI/canonicalPDF-path eligibility condition at three shared predicates. Exact independent native Draft and stablebindings pass; native checker0errors/0warnings; single-flow Publish succeeds. Fresh canonical graph matches candidate and state is Stopped. Evidence: openalex1635/retrieval-qualification.json, flow-diff.json, draft-acceptance.json and publication-acceptance.json. Candidatecell handoff is received but no fieldwrite or retained-provider consumer run is claimed. Next: conditional additive1635candidate merge and one actual native save/link qualification.


### Retained OpenAlex candidate cell natively accepted — 19 October 2026

The exact parent1635 OALocationCandidates handoff is implemented by a bounded additive writer. Fresh native ID/CanonicalKey/DOI, priorcandidate value and nonwildcardETag guard the onecell write; savedreadback matches and unrelatedfields remain exact. One earlier attempt stopped before anymutationreceipt; an independentnative read verified the session before the successful attempt. Evidence: openalex1635/candidate-save-verified-session/acceptance.json. No1635 archival run was submitted before browsertransport interruption. Subsequent FlowRP expiry70043 requires the established Toolkit/form_post recovery; the single current challenge awaits userpassword/MFA. Preserve candidate/readback and challenge, then verify exacttarget/history and resume one consumer run. No newconsent/profile, sourcefield or schedulechanges.


### Retained OpenAlex native save and integrity accepted — 19 October 2026

The existing Toolkit/form_post authentication recovery succeeded, followed by exact-target preflight. One native input run for parent1635/afterId0/forceRefreshfalse succeeded, consuming its retained OpenAlex candidate without PMC or Unpaywall acquisition. The flow staged, saved, compared bytes, persisted its receipt and linked the publication. Independent SharePoint retrieval matches the qualified publisher PDF (1,100,143 bytes), exact DOI and SHA256; the actual hash is recorded/read back in the manifest with unrelated fields preserved. Evidence under ignored private/ops/2026-10-18-oa-paper-archiving/openalex1635/: run-details.json, run-actions-complete.json, file-verification/acceptance.json, native-hash/acceptance.json.

Fresh history confirms all recent runs terminal and no duplicate or replay submission. The canonical flow is restored Stopped; final-stop-acceptance.json and final-stopped-readback.json prove the exact normalized published graph and stable logical references. Known FlowRP response omissions of authentication/physical connection expansion were reconciled explicitly. BrowserOS tool exposure disappeared in both owning chats while opening the replay form; the new paper's unchanged replay and browser reader check remain pending. No new sign-in, profile mutation or download is needed. Existing paper12 and earlier replay/reader evidence remain closed.

The documentation owner received the settled graph/evidence and retains the five changed versioned assets, native SharePoint pages and Loop updates. Generation19 remains the preserved native baseline until that update qualifies. Genuine changed-content, alternate-failure and absent accepted EuropePMC/ORCID inputs remain explicit gaps. Next: when the existing BrowserOS tools return, reconcile the preserved form, verify history, perform one1635/0/false replay plus reader check, then restore Stopped and hand back final evidence.


### Candidate producer replay corrected and natively qualified — 19 October 2026

An already-applied candidate plan previously failed its stale-preimage check before reaching the intended no-op branch. The writer now validates the exact parent first, accepts an exact current target value without mutation, and retains prior-value plus fresh ETag guards for any actual write. Replaying the original accepted1635 plan through the qualified CLI returned PASS_NO_CHANGE with zero submissions; the complete native row and both folder files match their prior snapshots exactly. Syntax and scoped diff checks pass. Evidence: openalex1635/candidate-replay/acceptance.json and candidate-replay-comparison.json. This proves candidate-handoff retry safety, not the still-pending archival-flow replay or browser reader check. Source owner has been asked to identify the maintained producer handoff for future retained metadata; no collector or native definition was changed.

### Maintained operator Crossref handoff implemented — 19 October 2026

The source owner supplied the exact accepted extension manifest/complete-marker pair and its explicit predecessor pair. `scripts/prepare_oa_crossref_handoff.py` now consumes pinned local copies, verifies identical commit-marker bytes, accepted scope, completion and counts, follows explicit extension lineage and preserves its DOI prefix/window. The selected raw envelope must match the manifest's exact folder/file, requested DOI, status and saved-readback evidence. No query-hit identity or licence inference is admitted. Negative responses preserve existing candidates; eligible additions require the exact candidate-cell handoff and remain subject to the existing native writer's fresh identity/preimage/ETag guards. This is an operator CLI handoff, not a scheduled local runtime or unattended native collector.

Usage: `python3 scripts/prepare_oa_crossref_handoff.py HANDOFF.json NEW_PRIVATE_OUTPUT.json`. The handoff supplies `scope_sha256`, `commit` and `lineage` entries containing pinned `manifest`/`complete_marker` path+SHA256 references, pinned `parent_readback`, pinned `envelope` with explicit `archive_folder`/`file`, and `observed_utc`. A changed result additionally requires a pinned `cell_handoff`. Its output retains projection/provenance and an additive `plan` only when changed; apply that plan through `scripts/apply_oa_retained_candidates.mjs` using the existing exact target. The preparer performs no network call or native mutation and refuses output overwrite.

Real qualified CLI retrieval of the selected immutable Crossref envelope plus fresh native parent read passed. Preparation against the accepted extension and predecessor manifests passed with no eligible PDF/no change, preserving raw metadata and all native objects. Evidence: ignored `private/ops/2026-10-18-oa-paper-archiving/crossref-handoff/handoff.json` and `prepared.json`. Four focused tests cover negative no-clearing, raw/marker drift, explicit lineage/prefix preservation and positive exact-cell authority. Python compilation and scoped diff checks pass. Collector definitions, schedules, source checkpoints and report files remain with their owner. OpenAlex maintained handoff and remaining native/archive documentation gates remain open; this does not close the full increment.

### OpenAlex paper native replay and reader accepted — 19 October 2026

BrowserOS tool exposure returned. After exact current Stopped/history reconciliation, one publication1635/afterId0/forceRefreshfalse replay succeeded. Provider lookup, download, save and link actions were skipped; the complete publication row and both folder files remain exact, including their native versions and metadata. The canonical flow is restored Stopped with the same normalized published graph. Existing SharePoint web preview opens the saved paper; its first-page title and exact DOI were visually verified. Direct binary preview was blank, so the existing supported `?web=1` reader route was used. No editing, sharing or access change occurred. Own-page focus emulation resolved restored-browser background throttling and was reverted after use.

Evidence: ignored openalex1635/replay-acceptance.json, replay-run-details.json, replay-run-actions-complete.json, replay-before.json, replay-after.json, reader-acceptance.json, replay-stopped-readback.json and replay-stop-acceptance.json under the existing OA private directory. This closes the selected1635 replay/reader checks. Documentation owner retains final versioned SharePoint/Loop publication; genuine changed-content/alternate-failure and remaining maintained-provider handoff gaps are not claimed complete.

### Maintained operator OpenAlex handoff implemented — 19 October 2026

`scripts/prepare_oa_openalex_handoff.py` consumes a pinned existing source-owner handoff, verifies the committed manifest and native acceptance against all exact page hashes/counts, and reconstructs a selected original work from contiguous UTF8-HEX chunks. It checks envelope identity, original byte count/SHA and exact requested DOI before binding the fresh parent identity and preparing additive candidates. New additions require pinned exact-cell authority; the native writer retains fresh preimage/ETag checks. URL discovery is not retrieval qualification and this preparer does not acquire, schedule or mutate native objects.

Usage: `python3 scripts/prepare_oa_openalex_handoff.py HANDOFF.json NEW_PRIVATE_OUTPUT.json`. Inputs are pinned `source_handoff` and `parent_readback` path/SHA references plus exact `work_id`, with pinned `cell_handoff` required only for a changed plan. The source-owner handoff supplies its immutable manifest, native acceptance and complete exact retained page set. Output records provenance, projection, merge and an optional native writer plan. Fresh parent read plus real committed six-page source preparation passed with no eligible candidate/no field change. Evidence: ignored openalex-handoff/handoff.json and prepared-final.json under the existing OA private directory. Three focused reconstruction tests cover original-byte restoration, missing/duplicate/conflicting chunks and hash/work substitution. Both provider handoff suites total seven passing tests. This closes maintained operator preparation for the accepted Crossref/OpenAlex routes; it does not claim unattended producer wiring, new acquisitions, absent EuropePMC/ORCID admission or remaining changed-content/alternate-failure native qualification.

### Genuine version/fallback qualification remains input-bound — 19 October 2026

Supported public PMC listing reads for the four accepted PMC copies expose only version1. A bounded sample of ten other already-retained register PMCIDs exposes zero or one version each. No PDF was downloaded and no native field/file/flow changed during this inspection. Evidence: ignored remaining-native-cases/version-opportunities.json, bounded-version-opportunities.json, retained listing XML and qualification-gap.json under the existing OA directory. These reads cannot prove changed-content retention or retrieval-failure-to-next-source execution. The source owner has been asked for an already accepted real multi-version work or genuinely unavailable first licensed location, without new broad collection. Preserve these requirements as unproved; do not fabricate URLs, provider hashes or source versions, or repeatedly rerun accepted happy paths. Retry when a genuine selected source case is available. Documentation publication is progressing independently with its existing owner.


### Documentation dependency closed; remaining runtime input gap — 19 October 2026

The documentation owner completed the coherent native transaction: five updated assets of307, guide9, catalogue11, Loop53 and complete marker21. All38 native Mermaid sources survive reopen exactly, the other37 remain preserved, and171 OA diagram elements render. Saved content, stable identities, prior-version retrieval and inherited access pass. Authoritative owner receipt: ignored private/ops/2026-10-19-oa-documentation/acceptance.json (PASS_OA_DOCUMENTATION_NATIVE_COMPLETE), with page, Loop and history receipts alongside it. This closes the affected documentation dependency without rebuilding R20b or repeating archive runs.

The source owner confirms no additional accepted real multi-version or retrieval-failure-to-next-source case is available. Both operator handoffs and accepted archive/save/hash/reader/replay/recovery/membership evidence remain closed. Full E01-OA acceptance remains unproved for genuine changed-content and alternate-failure runtime behavior; absent standalone EuropePMC/ORCID admission remains conditional. No further native run is queued. Resume qualification on an already accepted genuine source version/failure case, preserving the current Stopped flow and all saved papers; do not broaden acquisition, fabricate metadata or substitute another happy-path rerun.

### Both genuine system cases qualified — 19 October 2026

The user explicitly requested finding real cases, then clarified that individual-record work must serve an overarching system benefit. Discovery stopped once one accepted retained work supplied both cases; no scientific or business review was performed. The source owner handed off only its OA candidate cell and a separately verified blank PMCID fill. Real retained publisher metadata asserts CC BY; its actual PDF URL returned403. Supported PMC metadata supplies accepted and published versions with different provider MD5 and independently verified SHA256/bytes and exact DOI.

Source106a6a8 adds only the DOI-bound licensed OpenAlex OUP publisher path to the three existing eligibility predicates. Ten focused tests, exact native Draft/binding readback and checker0errors/0warnings pass. The same canonical flow is published and independently read back. One native fallback run records publisher Forbidden403 then successful PMC accepted-version download/save/link. One explicit refresh discovers the real published version and saves a different file identity. Both original files retain exact identities, ETags, lengths and version metadata; the new manifest preserves the prior-copy identity/hash and unrelated register cells remain unchanged. Both versions' saved bytes match their real provider MD5/SHA and exact DOI, native hashes are recorded/read back, and existing SharePoint readers open both copies. All runs are terminal and the exact qualified graph is restored Stopped.

Authoritative private receipt: private/ops/2026-10-18-oa-paper-archiving/real-qualification-cases/qualification-acceptance.json, with fallback-acceptance.json, version-acceptance.json, independent-version-qualification.json, both native hash receipts, reader-acceptance.json and final-stop-acceptance.json. This supersedes the earlier absence-of-case blocker. No further record search or native run is needed. Final matching versioned documentation handoff and repository-wide check diagnosis remain before lane closure; required full harness returned FAIL_LOCAL while web-first/Conductor/tooling checks passed, so no all-checks-pass claim is made.

### Final local validation and technical handover — 19 October 2026

The complete five-group harness passes under the existing isolated Python3.15
environment:2,040 unittest tests (8 optional skips),446 project checks, web-first
contracts, Conductor structure and tooling presence. All73 pytest-function tests
pass separately. The prior12 import errors were missing declared dependencies in
the default interpreter; no package installation or native rerun was needed.
Logs and exact technical handover are in the existing real-qualification-cases
folder: repository-validation-final.log, repository-pytest-final.log and
technical-handover.json. Native acceptance remains independently evidenced.

The bounded backfill, maintained operator source handoffs and incremental refresh
close .5. No unattended collector integration is claimed. Standalone EuropePMC/
ORCID input admission remains conditional on accepted retained inputs. Canonical
workflow membership remains accepted; SharePoint storage/four fields are external
companions. All saved paper history is retained. No release rebuild, activation,
permission change, broader audit or further individual-record work is required.
The documentation owner has the affected source/hash/receipts, with coordination
relayed to the active source/report chat because direct steering is unavailable.
Final native documentation receipt is the sole remaining closeout dependency.

### Lane closed — 19 October 2026

Final affected native documentation is complete: guide10, catalogue12, Loop54 and
marker23. All38 reopened native code sources match, other37 are unchanged, and
171 OA preview identities render. Five affected assets have exact saved bytes;
existing page identities/layout,74 unrelated catalogue controls, prior versions
and access shapes are preserved. The prior307-asset generation remains history.
Conductor received the terminal documentation and technical handover. All eight
plan items are complete for the selected operator-run scope. No further record
work, run, package rebuild or optional expansion is a closure prerequisite.

### Paper-library metadata increment — 19 October 2026

Seven existing linked PDF copies now have native Title and provenance Description,
with a nondefault folder-scoped catalogue. File bytes/identity, register links,
manifests, access and prior versions are preserved; unchanged replay writes zero.
The operator CLI refuses source drift and human-field conflicts. These external
library companions add no solution member or runtime flow change. Documentation
is accepted at guide12/catalogue13/Loop59/marker27,316assets;39 native Mermaid
sources remain exact. Receipt: private/ops/2026-10-19-paper-library-metadata/acceptance.json.
The eight original OA plan items remain closed; no further record work is needed.
