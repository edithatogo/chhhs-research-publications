# Broad source acquisition and regular updates — 18 October 2026

## Current accepted state — 19 October 2026

All eleven policy-source families/twelve collections have accepted maintained-scope
acquisition/update handbacks, included in R20b and the final32-workflow solution.
See the [current source matrix](source-scopes-20261018.md)
and [release readiness](../../../docs/RELEASE_READINESS.md). Twelve collector graphs
are Started; most first natural occurrences remain unobserved, except accepted ROR
history. This does not enlarge unchanged consumers or assert global-corpus coverage.
The preparation/in-progress statements below are historical evidence, not current
execution instructions. Do not repeat accepted capture, conversion or release work.
OA handoff uses already committed OpenAlex payloads; EuropePMC/ORCID standalone
payload admission remains absent/conditional. Existing PubMed/PMC proof is retained.


The user's latest scope supersedes global-corpus wording: acquire the entire
maintained scope for each source, preserve complete raw originals before local
selection, and update regularly in Power Automate. No further downstream model,
register or dashboard expansion is selected by this increment.

`config/source-acquisition-scopes.json` records eleven existing sources. PubMed
retains its evolving editable institutional hedge. Crossref must implement the
same discovery intent in its own supported query semantics, plus DOI
reconciliation; sharing the hedge dependency is not a claim that PubMed query
syntax works in Crossref. Global trial coverage combines Australian and institutional scope. DataCite
uses the institutional hedge plus datasets related to acquired publication DOIs,
as explicitly selected by the user after qualification of the larger alternatives. Australian MRFF/NHMRC/ARC/QGIP/ARDC
sources retain complete official dataset/release coverage; DoRA completeness is
within its established authorised collections. ROR is organisation-reference
coverage: all Australian organisations, inactive/withdrawn included, and referenced
foreign organisations.

ROR's official filtering guidance recommends retaining its versioned data dump
and selecting country afterwards. API paging caps retrieval at10,000records;
queries for32IDs cannot establish this scope. Source-specific bulk/API limits,
metadata availability and retention permissions must be qualified, not guessed.

Daily publication/DoRA and weekly funding/trial/identifier checks, with monthly
ROR release checks, are implementation defaults in the maintained policy. They
are not claims that triggers are enabled. Native owners may stagger execution
within the existing environment while preserving this cadence and recording the
actual recurrence/readback. Full baselines, source-change overlap and periodic
scope reconciliation prevent updates from forgetting earlier records/corrections.

`source_acquisition_scope.py` freezes source policy, its revision/hash and the
current hedge-file hash. Hedge edits change the acquisition fingerprint even when
the policy revision is unchanged. Unknown/duplicate identities, sample initial
captures and escaping hedge paths are rejected. It makes no service calls and
never claims native completeness or recurring operation.

Three focused tests pass. Native acquisition remains archive-lane owned; this
lane owns only these policy/helper/test files and this leaf. Use the frozen scope
in capture/checkpoint/final manifests, after complete page or release inventory,
saved-byte readback and replay/catch-up checks. Keep bounded verification history
honest. Do not mark the whole system complete from policy preparation alone.

References:
- https://ror.readme.io/docs/api-filtering
- https://ror.readme.io/docs/api-paging
- https://ror.readme.io/docs/data-dump

## ROR native implementation underway

The exact ROR collector handoff is recorded in the existing source-expansion
handoff receipt. Fresh preimage matched the accepted32-ID graph and Stopped
state. The same flow now contains full official release retention with a frozen
scope fingerprint and manifest-last saved-byte checks. It reuses the exact
SharePoint connection/archive parent, leaving consumers and other sources alone.
The maintained builder is prepare_ror_dump_collection.py; two focused tests pass.

The full official v2.14 release was captured and independently downloaded from
SharePoint. Publisher MD5, ZIP CRC, unique identifiers and the official total all
reconcile: 38,536,565 bytes, 144,717 organisations, including 2,043 Australian
organisations. All Australian raw records are retained; no downstream projection
is claimed. The published Zenodo download URL resolved the API download timeout.

The same collector now reads an immutable release-completion marker before
capture. A native unchanged-release run succeeded: the retained file identity,
ETag and size matched, and download, folder creation and all archive-write actions
were skipped. Seven focused unittest checks pass. The same collector is now Started with a
monthly Recurrence trigger (Brisbane timezone, concurrency one). The scheduler
itself produced a successful unchanged-release run; download and archive-write
actions were skipped. Exact saved action graph, bindings and Started state match.
This proves activation and one scheduled execution, not future monthly outcomes.
Private receipts are under
private/ops/2026-10-18-ror-broad-acquisition/ (native-full-release-verification.json,
replay-acceptance.json, monthly-acceptance.json and monthly-started-readback.json).

A rejected FlowAgent update partially cleared connection references even though
its old graph remained. This was detected by saved readback, and exact original
graph/binding identities/Stopped state were restored through the existing direct
Microsoft365CLI FlowRP path before another candidate save. Use explicit complete
connection references and native reconciliation on this route; tool error alone
never proves zero effect. Do not reuse the failing rewrite path unchanged.

## DataCite scope selection — 18 October 2026

The user selected **institutional hedge and related datasets**. Policy revision
v2 records that choice, rather than all Australian providers or all Australian
affiliations. Read-only API qualification found 52 Australian providers with
about 8.85 million DOI records, versus about 209,000 Australian-affiliation
records. Those alternative counts are scale evidence, not acquisition acceptance.
The selected path must include every matching institutional query result and
related datasets for every acquired publication DOI, with full metadata options
(`detail`, `affiliation`, `publisher`), complete pagination and regular updates.

Existing ROR and in-flight Crossref definitions retain their accepted frozen v1
inputs and hashes. This DataCite decision does not alter those native graphs or
retroactively relabel their historical evidence. ARDC preparation uses policy v2.
