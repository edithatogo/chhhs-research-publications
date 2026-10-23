# Flow diagrams

Every inventoried complete flow definition has one canonical JSON graph and
programmatically generated Mermaid, BPMN 2.0 XML, Petri-net PNML and editable
Visio VSDX outputs. See the [coverage inventory](inventory.json) and links below.
No tenant bindings, input expressions, credentials, row payloads or resource URLs
are copied into the graphs. Action keys and action types remain visible.

## Current collector documentation — 19 October 2026

The catalogue contains 38 documentary snapshots, with corresponding native
Mermaid code blocks in the existing Research page. PubMed, ClinicalTrials.gov,
NHMRC, MRFF, ARC, QGIP, DoRA activity/publications, Crossref, DataCite, ARDC and
the published OA archive graph have exact reopened source and preview evidence.
Each update preserved unrelated source hashes. The96 refreshed source/diagram
files have saved-byte and previous-version evidence. DoRA activity and
publications are distinct collections. First future natural schedule occurrences
and the OA storage-barrier runtime branch retain their separate pending status.

PubMed and DoRA publication include verified own-DOI completion checkpoints.
Crossref/DataCite retain the raw producer union and legacy inputs before filtering.
ARDC retains436,536 unique public registry metadata records in4,366 raw XML pages,
plus15,252 incremental records in153 pages; the normal Monday04:00 Brisbane
weekly flow is Started. Underlying research files are excluded. These are source
acquisitions, not publication-register admission or relationship adjudication.

Use the versioned native generation marker for current page/file/code versions
and complete/updating status. Previous generations remain in native history;
individual diagram evidence does not establish a successor release. The final
32-workflow canonical solution export is verified with exact membership and
qualified native definition/reference comparisons. See
[release readiness](../RELEASE_READINESS.md) for the selected internal release
and exact evidence boundaries.

## Maintain one definition

Power Automate definitions remain the executable authority. The canonical JSON
is the single documentary intermediate; edit the source flow under its existing
owner, then extract and regenerate all formats together. Do not hand-edit an
individual diagram. Source hashes identify the exact captured definition; a graph
is not proof that a candidate was deployed or that a live flow remains unchanged.

```sh
python3 scripts/build_flow_diagrams.py extract path/to/flow.json \
  --slug example-flow --status 'repository source; deployment not inferred' \
  --output docs/flow-diagrams/canonical/example-flow.json
python3 scripts/build_flow_diagrams.py render
python3 -m unittest tests.test_build_flow_diagrams
```

Extraction is local and read-only. Private native readbacks can be inputs, but
only the sanitised graph goes into this directory. Preserve one writer per native
flow. New flows need a new canonical graph; rendering regenerates the inventory and
catalogue automatically. Existing graphs
need refreshing after material definition changes. The inventory deliberately
includes maintained repository variants separately from solution snapshots;
documentary snapshot count is not the number of distinct active native flows.

## Meaning and limits

All formats preserve action identity, type, nested branch/scope membership and
explicit `runAfter` dependencies, including accepted Succeeded/Failed/Skipped/
TimedOut statuses. Mermaid dotted links identify nested scopes. Each nested scope
has a corresponding BPMN process, PNML net and Visio page; generated Markdown maps
page numbers to complete scope paths. Branch labels (body/else/case/default) are
retained. Conditions and inputs stay in the source, never inferred from names.

These are **documentary abstractions**, not a transpiler between execution engines.
BPMN processes are `isExecutable=false`; their tasks and labelled sequence flows
show dependencies, while trigger types, exact dependencies and nested scopes are
recorded in documentation. No executable BPMN gateway/condition equivalence is
claimed. PNML represents each action as a transition and each dependency as an
intermediate place, with no initial marking or executable status guards. It supports
structural inspection, not behavioural verification of retries, failure/skip
propagation, conditional branches, concurrency or loop iteration. A simulation
would require an additional explicitly modelled execution contract.

Visio exports contain native editable shapes and connectors, one page per scope,
with status labels. They are actual OPC `.vsdx` packages, not renamed Mermaid or
embedded screenshots. Layout is a deterministic grid; complex flows may benefit
from Visio's layout tools. Package/XML/relationship checks do not establish native
Visio rendering; opening and visual editing in the user's Windows Visio remain
unverified. No installed Visio runtime was used here.

## Coverage

The initial capture covers all 18 workflows in accepted R17b, all six complete
flow definitions in `config/flows`, seven current source collector definitions
and three source consumers. The newer source definitions are snapshots while
another lane continues implementation; check their hashes/status before reuse.
Historical operation/preimage duplicates are excluded.

The monthly blueprint, weekly-digest candidate and weekly-digest consumer fragment
are **design inputs, not complete Power Automate definitions**. Their maintained
sources remain `config/monthly-flow.blueprint.json`,
`config/flows/publication-weekly-digest.candidate.json` and
`config/flows/publication-weekly-digest-consumer.fragment.json`. The corresponding
packaged complete workflows are covered; this generator refuses to turn an
incomplete fragment into a falsely complete executable flow.

Format references: [OMG BPMN 2.0.2](https://www.omg.org/spec/BPMN/2.0.2/)
and [Microsoft Visio package format](https://learn.microsoft.com/en-us/office/client-developer/visio/introduction-to-the-visio-file-formatvsdx).

## Generated catalogue

| Flow snapshot | Status | Formats |
|---|---|---|
| [ardc-collector](canonical/ardc-collector.json) | Accepted full public registry metadata:436536 unique records/4366 raw XML pages; incremental catch-up15252 unique/153 pages; Monday04:00 Brisbane weekly Started. Original payloads/checkpoints retained; first natural weekly occurrence unobserved. Underlying research files excluded. | [Mermaid](generated/ardc-collector.md) · [BPMN](generated/ardc-collector.bpmn) · [Petri net](generated/ardc-collector.pnml) · [Visio](generated/ardc-collector.vsdx) |
| [crossref-collector](canonical/crossref-collector.json) | accepted maintained hedge and verified PubMed/DoRA raw-DOI union; normal daily Started snapshot; first natural daily occurrence unobserved | [Mermaid](generated/crossref-collector.md) · [BPMN](generated/crossref-collector.bpmn) · [Petri net](generated/crossref-collector.pnml) · [Visio](generated/crossref-collector.vsdx) |
| [ctgov-collector](canonical/ctgov-collector.json) | accepted full maintained Australian trial scope; two complete 12666-record passes and retained institutional seeds; weekly Wednesday Started runtime snapshot; first natural weekly occurrence unobserved | [Mermaid](generated/ctgov-collector.md) · [BPMN](generated/ctgov-collector.bpmn) · [Petri net](generated/ctgov-collector.pnml) · [Visio](generated/ctgov-collector.vsdx) |
| [ctgov-consumer](canonical/ctgov-consumer.json) | Accepted full public registry metadata:436536 unique records/4366 raw XML pages; incremental catch-up15252 unique/153 pages; Monday04:00 Brisbane weekly Started. Original payloads/checkpoints retained; first natural weekly occurrence unobserved. Underlying research files excluded. | [Mermaid](generated/ctgov-consumer.md) · [BPMN](generated/ctgov-consumer.bpmn) · [Petri net](generated/ctgov-consumer.pnml) · [Visio](generated/ctgov-consumer.vsdx) |
| [datacite-collector](canonical/datacite-collector.json) | accepted maintained institutional hedge and verified PubMed/DoRA raw-DOI union; weekly Started snapshot; first natural weekly occurrence unobserved | [Mermaid](generated/datacite-collector.md) · [BPMN](generated/datacite-collector.bpmn) · [Petri net](generated/datacite-collector.pnml) · [Visio](generated/datacite-collector.vsdx) |
| [mrff-collector](canonical/mrff-collector.json) | accepted complete maintained source and weekly Started snapshot; first natural weekly occurrence unobserved | [Mermaid](generated/mrff-collector.md) · [BPMN](generated/mrff-collector.bpmn) · [Petri net](generated/mrff-collector.pnml) · [Visio](generated/mrff-collector.vsdx) |
| [mrff-consumer](canonical/mrff-consumer.json) | verified native Stopped snapshot; all1915 fields and zero-write replay accepted | [Mermaid](generated/mrff-consumer.md) · [BPMN](generated/mrff-consumer.bpmn) · [Petri net](generated/mrff-consumer.pnml) · [Visio](generated/mrff-consumer.vsdx) |
| [nhmrc-collector](canonical/nhmrc-collector.json) | accepted complete maintained source and weekly Started snapshot; first natural weekly occurrence unobserved | [Mermaid](generated/nhmrc-collector.md) · [BPMN](generated/nhmrc-collector.bpmn) · [Petri net](generated/nhmrc-collector.pnml) · [Visio](generated/nhmrc-collector.vsdx) |
| [nhmrc-consumer](canonical/nhmrc-consumer.json) | Accepted full public registry metadata:436536 unique records/4366 raw XML pages; incremental catch-up15252 unique/153 pages; Monday04:00 Brisbane weekly Started. Original payloads/checkpoints retained; first natural weekly occurrence unobserved. Underlying research files excluded. | [Mermaid](generated/nhmrc-consumer.md) · [BPMN](generated/nhmrc-consumer.bpmn) · [Petri net](generated/nhmrc-consumer.pnml) · [Visio](generated/nhmrc-consumer.vsdx) |
| [pubmed-collector](canonical/pubmed-collector.json) | accepted full maintained PubMed hedge and own-DOI completion checkpoint; daily Started runtime snapshot; first natural daily occurrence unobserved | [Mermaid](generated/pubmed-collector.md) · [BPMN](generated/pubmed-collector.bpmn) · [Petri net](generated/pubmed-collector.pnml) · [Visio](generated/pubmed-collector.vsdx) |
| [ror-collector](canonical/ror-collector.json) | verified native Started monthly snapshot; full official release retention, unchanged no-write replay and first scheduler run accepted; future monthly occurrences unobserved | [Mermaid](generated/ror-collector.md) · [BPMN](generated/ror-collector.bpmn) · [Petri net](generated/ror-collector.pnml) · [Visio](generated/ror-collector.vsdx) |
| [solution-chhhsresearchpublications-weeklydigestcommissionin](canonical/solution-chhhsresearchpublications-weeklydigestcommissionin.json) | 22 October 2026 exact native manual-only Stopped definition; controlled no-send runtime and HTML rendering accepted; email delivery unauthorised | [Mermaid](generated/solution-chhhsresearchpublications-weeklydigestcommissionin.md) · [BPMN](generated/solution-chhhsresearchpublications-weeklydigestcommissionin.bpmn) · [Petri net](generated/solution-chhhsresearchpublications-weeklydigestcommissionin.pnml) · [Visio](generated/solution-chhhsresearchpublications-weeklydigestcommissionin.vsdx) |
| [solution-chhhsrimsdataspacesarcawardsourcecollection](canonical/solution-chhhsrimsdataspacesarcawardsourcecollection.json) | accepted complete maintained source and weekly Started snapshot; first natural weekly occurrence unobserved | [Mermaid](generated/solution-chhhsrimsdataspacesarcawardsourcecollection.md) · [BPMN](generated/solution-chhhsrimsdataspacesarcawardsourcecollection.bpmn) · [Petri net](generated/solution-chhhsrimsdataspacesarcawardsourcecollection.pnml) · [Visio](generated/solution-chhhsrimsdataspacesarcawardsourcecollection.vsdx) |
| [solution-chhhsrimsdataspacesdorasourcecollection](canonical/solution-chhhsrimsdataspacesdorasourcecollection.json) | accepted complete Queensland DoRA activity raw archive and daily Started snapshot; publication repository separate; first natural daily occurrence unobserved | [Mermaid](generated/solution-chhhsrimsdataspacesdorasourcecollection.md) · [BPMN](generated/solution-chhhsrimsdataspacesdorasourcecollection.bpmn) · [Petri net](generated/solution-chhhsrimsdataspacesdorasourcecollection.pnml) · [Visio](generated/solution-chhhsrimsdataspacesdorasourcecollection.vsdx) |
| [solution-chhhsrimsdataspacesqgipsourcecollection](canonical/solution-chhhsrimsdataspacesqgipsourcecollection.json) | accepted complete indexed QGIP agency resources and weekly Started snapshot; first natural weekly occurrence unobserved | [Mermaid](generated/solution-chhhsrimsdataspacesqgipsourcecollection.md) · [BPMN](generated/solution-chhhsrimsdataspacesqgipsourcecollection.bpmn) · [Petri net](generated/solution-chhhsrimsdataspacesqgipsourcecollection.pnml) · [Visio](generated/solution-chhhsrimsdataspacesqgipsourcecollection.vsdx) |
| [solution-chhhsrimsdataspacessourcearchivecommit](canonical/solution-chhhsrimsdataspacessourcearchivecommit.json) | accepted R17b solution snapshot; not a fresh live readback | [Mermaid](generated/solution-chhhsrimsdataspacessourcearchivecommit.md) · [BPMN](generated/solution-chhhsrimsdataspacessourcearchivecommit.bpmn) · [Petri net](generated/solution-chhhsrimsdataspacessourcearchivecommit.pnml) · [Visio](generated/solution-chhhsrimsdataspacessourcearchivecommit.vsdx) |
| [solution-chhhsrimsdataspacestestsourcearchivestaging](canonical/solution-chhhsrimsdataspacestestsourcearchivestaging.json) | accepted R17b solution snapshot; not a fresh live readback | [Mermaid](generated/solution-chhhsrimsdataspacestestsourcearchivestaging.md) · [BPMN](generated/solution-chhhsrimsdataspacestestsourcearchivestaging.bpmn) · [Petri net](generated/solution-chhhsrimsdataspacestestsourcearchivestaging.pnml) · [Visio](generated/solution-chhhsrimsdataspacestestsourcearchivestaging.vsdx) |
| [solution-chhhsrimsfundingarcawardcontextexport](canonical/solution-chhhsrimsfundingarcawardcontextexport.json) | accepted R17b solution snapshot; not a fresh live readback | [Mermaid](generated/solution-chhhsrimsfundingarcawardcontextexport.md) · [BPMN](generated/solution-chhhsrimsfundingarcawardcontextexport.bpmn) · [Petri net](generated/solution-chhhsrimsfundingarcawardcontextexport.pnml) · [Visio](generated/solution-chhhsrimsfundingarcawardcontextexport.vsdx) |
| [solution-chhhsrimsfundingcalendarchangeupsert](canonical/solution-chhhsrimsfundingcalendarchangeupsert.json) | accepted R17b solution snapshot; not a fresh live readback | [Mermaid](generated/solution-chhhsrimsfundingcalendarchangeupsert.md) · [BPMN](generated/solution-chhhsrimsfundingcalendarchangeupsert.bpmn) · [Petri net](generated/solution-chhhsrimsfundingcalendarchangeupsert.pnml) · [Visio](generated/solution-chhhsrimsfundingcalendarchangeupsert.vsdx) |
| [solution-chhhsrimsfundingcalendarupsert](canonical/solution-chhhsrimsfundingcalendarupsert.json) | accepted R17b solution snapshot; not a fresh live readback | [Mermaid](generated/solution-chhhsrimsfundingcalendarupsert.md) · [BPMN](generated/solution-chhhsrimsfundingcalendarupsert.bpmn) · [Petri net](generated/solution-chhhsrimsfundingcalendarupsert.pnml) · [Visio](generated/solution-chhhsrimsfundingcalendarupsert.vsdx) |
| [solution-chhhsrimsfundingdeliveryledgerupsert](canonical/solution-chhhsrimsfundingdeliveryledgerupsert.json) | accepted R17b solution snapshot; not a fresh live readback | [Mermaid](generated/solution-chhhsrimsfundingdeliveryledgerupsert.md) · [BPMN](generated/solution-chhhsrimsfundingdeliveryledgerupsert.bpmn) · [Petri net](generated/solution-chhhsrimsfundingdeliveryledgerupsert.pnml) · [Visio](generated/solution-chhhsrimsfundingdeliveryledgerupsert.vsdx) |
| [solution-chhhsrimsfundingqgipcandidateexport](canonical/solution-chhhsrimsfundingqgipcandidateexport.json) | accepted R17b solution snapshot; not a fresh live readback | [Mermaid](generated/solution-chhhsrimsfundingqgipcandidateexport.md) · [BPMN](generated/solution-chhhsrimsfundingqgipcandidateexport.bpmn) · [Petri net](generated/solution-chhhsrimsfundingqgipcandidateexport.pnml) · [Visio](generated/solution-chhhsrimsfundingqgipcandidateexport.vsdx) |
| [solution-chhhsrimsfundingtestmachineendpoints](canonical/solution-chhhsrimsfundingtestmachineendpoints.json) | accepted R17b solution snapshot; not a fresh live readback | [Mermaid](generated/solution-chhhsrimsfundingtestmachineendpoints.md) · [BPMN](generated/solution-chhhsrimsfundingtestmachineendpoints.bpmn) · [Petri net](generated/solution-chhhsrimsfundingtestmachineendpoints.pnml) · [Visio](generated/solution-chhhsrimsfundingtestmachineendpoints.vsdx) |
| [solution-chhhsrimsfundingwatchlistupsert](canonical/solution-chhhsrimsfundingwatchlistupsert.json) | accepted R17b solution snapshot; not a fresh live readback | [Mermaid](generated/solution-chhhsrimsfundingwatchlistupsert.md) · [BPMN](generated/solution-chhhsrimsfundingwatchlistupsert.bpmn) · [Petri net](generated/solution-chhhsrimsfundingwatchlistupsert.pnml) · [Visio](generated/solution-chhhsrimsfundingwatchlistupsert.vsdx) |
| [solution-chhhsrimsgrantsreviewedimportupsert](canonical/solution-chhhsrimsgrantsreviewedimportupsert.json) | accepted R17b solution snapshot; not a fresh live readback | [Mermaid](generated/solution-chhhsrimsgrantsreviewedimportupsert.md) · [BPMN](generated/solution-chhhsrimsgrantsreviewedimportupsert.bpmn) · [Petri net](generated/solution-chhhsrimsgrantsreviewedimportupsert.pnml) · [Visio](generated/solution-chhhsrimsgrantsreviewedimportupsert.vsdx) |
| [solution-chhhsrimsprojectsdoraactivityregisterupsert](canonical/solution-chhhsrimsprojectsdoraactivityregisterupsert.json) | accepted R17b solution snapshot; not a fresh live readback | [Mermaid](generated/solution-chhhsrimsprojectsdoraactivityregisterupsert.md) · [BPMN](generated/solution-chhhsrimsprojectsdoraactivityregisterupsert.bpmn) · [Petri net](generated/solution-chhhsrimsprojectsdoraactivityregisterupsert.pnml) · [Visio](generated/solution-chhhsrimsprojectsdoraactivityregisterupsert.vsdx) |
| [solution-chhhsrimspublicationsregisterexport](canonical/solution-chhhsrimspublicationsregisterexport.json) | accepted R17b solution snapshot; not a fresh live readback | [Mermaid](generated/solution-chhhsrimspublicationsregisterexport.md) · [BPMN](generated/solution-chhhsrimspublicationsregisterexport.bpmn) · [Petri net](generated/solution-chhhsrimspublicationsregisterexport.pnml) · [Visio](generated/solution-chhhsrimspublicationsregisterexport.vsdx) |
| [solution-chhhsrimspublicationsregisteringestionandenrichmen](canonical/solution-chhhsrimspublicationsregisteringestionandenrichmen.json) | accepted R17b solution snapshot; not a fresh live readback | [Mermaid](generated/solution-chhhsrimspublicationsregisteringestionandenrichmen.md) · [BPMN](generated/solution-chhhsrimspublicationsregisteringestionandenrichmen.bpmn) · [Petri net](generated/solution-chhhsrimspublicationsregisteringestionandenrichmen.pnml) · [Visio](generated/solution-chhhsrimspublicationsregisteringestionandenrichmen.vsdx) |
| [solution-chhhsrimsresearchersexport](canonical/solution-chhhsrimsresearchersexport.json) | accepted R17b solution snapshot; not a fresh live readback | [Mermaid](generated/solution-chhhsrimsresearchersexport.md) · [BPMN](generated/solution-chhhsrimsresearchersexport.bpmn) · [Petri net](generated/solution-chhhsrimsresearchersexport.pnml) · [Visio](generated/solution-chhhsrimsresearchersexport.vsdx) |
| [source-assertion-consumer](canonical/source-assertion-consumer.json) | Accepted full public registry metadata:436536 unique records/4366 raw XML pages; incremental catch-up15252 unique/153 pages; Monday04:00 Brisbane weekly Started. Original payloads/checkpoints retained; first natural weekly occurrence unobserved. Underlying research files excluded. | [Mermaid](generated/source-assertion-consumer.md) · [BPMN](generated/source-assertion-consumer.bpmn) · [Petri net](generated/source-assertion-consumer.pnml) · [Visio](generated/source-assertion-consumer.vsdx) |
| [source-dora-activity-registry-upsert](canonical/source-dora-activity-registry-upsert.json) | repository source variant; deployment not inferred | [Mermaid](generated/source-dora-activity-registry-upsert.md) · [BPMN](generated/source-dora-activity-registry-upsert.bpmn) · [Petri net](generated/source-dora-activity-registry-upsert.pnml) · [Visio](generated/source-dora-activity-registry-upsert.vsdx) |
| [source-dora-source-collection](canonical/source-dora-source-collection.json) | repository source variant; deployment not inferred | [Mermaid](generated/source-dora-source-collection.md) · [BPMN](generated/source-dora-source-collection.bpmn) · [Petri net](generated/source-dora-source-collection.pnml) · [Visio](generated/source-dora-source-collection.vsdx) |
| [source-funding-machine-endpoint-reconciliation](canonical/source-funding-machine-endpoint-reconciliation.json) | repository source variant; deployment not inferred | [Mermaid](generated/source-funding-machine-endpoint-reconciliation.md) · [BPMN](generated/source-funding-machine-endpoint-reconciliation.bpmn) · [Petri net](generated/source-funding-machine-endpoint-reconciliation.pnml) · [Visio](generated/source-funding-machine-endpoint-reconciliation.vsdx) |
| [source-grants-registry-reviewed-import](canonical/source-grants-registry-reviewed-import.json) | repository source variant; deployment not inferred | [Mermaid](generated/source-grants-registry-reviewed-import.md) · [BPMN](generated/source-grants-registry-reviewed-import.bpmn) · [Petri net](generated/source-grants-registry-reviewed-import.pnml) · [Visio](generated/source-grants-registry-reviewed-import.vsdx) |
| [source-publication-open-access-archive](canonical/source-publication-open-access-archive.json) | native published Stopped snapshot; numeric PMC ordering and optional manual-input schema qualified; storage recovery barrier published, runtime branch pending | [Mermaid](generated/source-publication-open-access-archive.md) · [BPMN](generated/source-publication-open-access-archive.bpmn) · [Petri net](generated/source-publication-open-access-archive.pnml) · [Visio](generated/source-publication-open-access-archive.vsdx) |
| [source-publication-register-monthly-export](canonical/source-publication-register-monthly-export.json) | repository source variant; deployment not inferred | [Mermaid](generated/source-publication-register-monthly-export.md) · [BPMN](generated/source-publication-register-monthly-export.bpmn) · [Petri net](generated/source-publication-register-monthly-export.pnml) · [Visio](generated/source-publication-register-monthly-export.vsdx) |
| [source-publication-registry-upsert](canonical/source-publication-registry-upsert.json) | repository source variant; deployment not inferred | [Mermaid](generated/source-publication-registry-upsert.md) · [BPMN](generated/source-publication-registry-upsert.bpmn) · [Petri net](generated/source-publication-registry-upsert.pnml) · [Visio](generated/source-publication-registry-upsert.vsdx) |
| [dora-publication-collector](canonical/dora-publication-collector.json) | accepted complete maintained publication collection and own-DOI completion checkpoint; daily Started runtime snapshot; first natural daily occurrence unobserved | [Mermaid](generated/dora-publication-collector.md) · [BPMN](generated/dora-publication-collector.bpmn) · [Petri net](generated/dora-publication-collector.pnml) · [Visio](generated/dora-publication-collector.vsdx) |
