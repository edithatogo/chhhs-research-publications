# OpenAlex retained-data integration — 14 October 2026

The human authorised implementation. The core publications chat transferred
separate bounded isolated-model and stopped-writer authoring leases. Shared
checkpoint, archive/export flows and activation remain with their owners.

## Delivered source slice

`scripts/prepare_openalex_retention.py` validates the frozen complete responses,
DOI/work identity, raw byte SHA256 and UTC observations. It retains unknown/null
fields and recursive observed schema in UTF8-HEX chunks. Failed/not-found attempts
produce explicit status evidence rather than replacement values.

`scripts/build_openalex_native_bootstrap.py` reuses the exact transferred 42-part
TMDL model and losslessly compresses the complete private preparation. It appends
four hidden tables and source-specific expressions. All 40 unrelated parts,
existing expression bodies and Publication fields remain unchanged. Private
payloads/target IDs/credentials never enter source Git. New objects retain the
existing Microsoft runtime; there are no provider calls or new connections.

Native update succeeded; one transactional refresh of only these four tables
completed in one attempt:

| Native table | Readback rows | Purpose |
| --- | ---: | --- |
| OpenAlexMetadataChunks | 22 | Complete three-response bytes/schema/provenance |
| OpenAlexWorks | 3 | Validated provider-specific fields |
| OpenAlexPublicationContext | 3 | Exact DOI match to already loaded canonical keys |
| OpenAlexFieldProvenance | 9 | Each provider field's value/observation/decision |

Native chunks exactly match preparation; all three transport responses reconstruct
with exact byte length, SHA256 and recursive schema. Publication remains 1,341
rows × 30 columns: all 40,230 scalar values unchanged. Native 46-part readback
preserves existing logic; the service moves new table references before the
existing culture reference and normalises new single-line M/trailing newlines.

Private acceptance pointer in the original workspace:
`private/ops/2026-10-14-openalex-native-acceptance-private.json`.
The refresh carries an unchanged `FreshPubMedIngestionAudit` DAX `DistinctCount`
syntax warning outside the four-table scope. This slice does not claim full-model
health or repair the unrelated source audit.

## Existing flow integration

`scripts/prepare_openalex_flow.py` adds a single accepted context query and an
exact canonical-key filter inside the existing serial upsert loop. It preserves
canonical/source queries, identity aliases, duplicate guard, reviews, corrections,
first-observed fields, connection references, recurrence and Stopped state.

The qualified list has `OpenAlexID`, `CitationCount_OpenAlex`, `OpenAccessStatus`
and `OAUrl`, but no qualified source/field-specific timestamp column.
Consequently the current slice fills missing values only. Existing zero counts
and nonblank values remain unchanged regardless of unknown age; missing provider
values never clear them. A conflicting existing WorkID skips provider fills and
records a `work_id_conflict` action diagnostic. Source observation times remain
in the accepted native provenance table and bound deployment receipt.
`CitationMetricsObservedUTC` remains unchanged: it is shared with other providers.

A future counter overwrite policy needs qualified source-specific persisted
field observation times and provenance. It is a separate gap rather than an
excuse to block the useful missing-only capability. No schedule/trigger conversion,
activation, run invocation, delivery, sharing or production change is included.
The same-ID authoring saved successfully and matches both the Flow API and stored Dataverse workflow definition after removing only service-injected authentication expressions for comparison. Native state remains Stopped and recurrence/connections are unchanged. No runtime invocation occurred. Private authoring acceptance: `private/ops/2026-10-14-openalex-flow-authoring-acceptance-private.json`. Runtime execution remains a separate gate.

## Reusable preparation and next sources

The file-backed `OpenAlexMetadataChunks.m`, `RetainedOpenAlexPublications.m` and
`config/native-openalex-retention.tmdl` remain preparation for the existing archive
commit-last path. They reuse `RetainedArchiveFiles` and the exact native reader
signature, avoiding a second site-wide file listing/connection. They are not the
active compressed bootstrap tables and do not prove archive-writer integration.
A prepared document is never an accepted commit manifest.

`fnMergeOpenAlexPublicationContext.m` and `scripts/merge_openalex_context.py`
preserve null/newer observations and reject equal-time conflicts when complete
per-field provenance exists. The current native registry writer deliberately uses
missing-only behavior. No canonical Publication merge expression is changed.

See [phase source routes](../docs/OPENALEX_PHASE_SOURCE_ROUTES.md) for every planned
source. Reuse accepted fields first, exact missing identifiers next, and versioned
reference/award files where they reduce calls and parsing effort. Crossref and ROR
are the next practical scholarly gaps; funding source ownership stays G02/G04.

Focused checks:

```sh
python3 -m unittest discover -s tests -p 'test_openalex*.py'
```

Rollback uses the private exact model and flow preimages. Restore only the leased
object after drift/uncertain-write checks; preserve all accepted historical data.
Routine acquisition, broader DOI coverage and operational acceptance remain open.

Final local integration checks: 36 focused OpenAlex tests passed. The required
full source-checkout milestone ran once: 498 tests, two failures, eight skips;
460 project checks, Conductor structure and tooling checks passed. Both failures
also exist at the preceding source commit: module summaries contain seven Mermaid
blocks while their older test expects six; the shared frozen runtime manifest
already mismatches local runtime files. These remain with the coordinator, who
must review any shared manifest refresh after integrating source changes. No test
or frozen contract was rewritten here to turn those failures green.

## Wider increment — 14 October 2026

The next bounded preparation reuses the three accepted responses and queries 47
additional exact DOIs from the accepted canonical snapshot through the existing
CLI adapter: 45 successes, two explicit not-found outcomes, zero provider
failures. Complete raw bytes and recursive schema remain retained.

`scripts/extend_openalex_native_bootstrap.py` changes only the compressed source
expression in the accepted 46-part model. All 45 other parts and other expression
bodies stay unchanged; all prior chunks and original observation/input provenance
remain byte-for-byte intact. The candidate contains 48 works and 242 chunks.
It uses 642,198 compressed bytes for 5,310,222 prepared bytes, with no new schema,
connection or flow changes. Failed/partial passes and duplicate identifiers
cannot advance the candidate. Three focused increment tests pass.

Against the accepted registry export, 44 exact canonical-key/DOI matches have
real missing provider fields; 28 also have an available missing OA URL. One
ambiguous DOI is excluded from this admission claim. The private missing-fill
packet supplies expected values and preimages for a real bounded native test.
After the core chat's three-key manual/replay acceptance and exact stopped-flow
restoration, the source-only model lease transferred and the increment deployed
through CLI. Native 46-part readback exactly matches the candidate; only the
compressed source payload changed. The four-table refresh completed: 242 chunks,
48 works, 51 canonical context rows and 153 field-provenance rows. Every retained
response byte/SHA256/schema and projected provider value reconciles, all original
three raw chunks/input/observation provenance remain exact, and all 40,230
Publication values remain unchanged. No native provider harvest, flow edit,
connection/schedule/report change or broader Publication refresh occurred.

Typed observation DateTime readback differs by at most 2.311 ms within the
[documented Power BI 1/300-second precision](https://learn.microsoft.com/en-us/power-bi/connect-data/desktop-data-types).
Exact original UTC remains in the retained raw envelope; these values are not
relabelled as the native refresh or registry-write time. The unchanged unrelated
source-audit warning remains explicit in the private acceptance.

The model lease returned to the core RIMS chat at terminal acceptance. All 44
real missing-field target preimages were reverified against its latest replay
readback and bound to the accepted source receipt. Actual missing-field write
and replay remain its next native gate; source acceptance does not prove those
writes or routine provider acquisition.

Private input/candidate/staging prefixes: `2026-10-14-openalex-wider-`.
Private model candidate: `2026-10-14-openalex-increment-candidate-private.json`.
Private real-row packet: `2026-10-14-openalex-real-missing-fill-packet-private.json`.

Native increment acceptance: `2026-10-14-openalex-increment-native-acceptance-private.json`.
Lease handback: `2026-10-14-openalex-increment-to-core-model-handback-private.json`.
Fresh source-bound target packet: `2026-10-14-openalex-real-missing-fill-accepted-source-private.json`.
