# OpenAlex retained-data integration — 13 October 2026

The user retained all native objects and shared UI with the core publications
chat. This source-only handoff closes the frozen OpenAlex retention/consumer
preparation dependency under T11 enrichment; it does not close native acceptance.

`scripts/prepare_openalex_retention.py` consumes the unchanged frozen input and
candidate from the preceding OpenAlex preparation. It makes no provider requests
and trusts complete response bytes, exact DOI/work identity and SHA256 rather
than derived candidate-record overwrites. Full response bytes and recursive
observed schema, including unknown/null fields, enter the existing UTF8-HEX chunk
format. Failed/not-found attempts yield status evidence and no replacement row.
Output is exclusive, owner-readable and explicitly uncommitted.

```sh
python3 scripts/prepare_openalex_retention.py \
  --private-root /path/to/repository/private/ops \
  --input /path/to/repository/private/ops/frozen-input.json \
  --candidate /path/to/repository/private/ops/enrichment-candidate.json \
  --output /path/to/repository/private/ops/new-retention-preparation.json
python3 -m unittest discover -s tests -p 'test_openalex*.py'
```

The existing private three-DOI evidence uses prefix
`2026-10-13-openalex-enrichment-`; prepared retention is
`private/ops/2026-10-13-openalex-retention-prepared-private.json` in the original
workspace. Raw transport bytes reconstruct exactly for all three works across
22 chunks. Local checks do not prove native stored bytes, M execution or refresh.

Exact next operation for the core owner after its archive/canonical dependency:
read the existing approved isolated source definition and archive writer, compare
their preimages and reserve the scoped change. Stage the prepared JSON through
the qualified existing Microsoft connector with absent-or-identical readback;
use a source-specific prepared filename, never a `commit-` filename. Configure
`pOpenAlexStagingFileName` and `pOpenAlexInputSHA256` privately alongside the
existing `pRetainedSiteUrl`/`pRetainedArchiveFolderUrl`. Do not alter common source
contracts merely by adding these source files.

The native source table `powerquery/OpenAlexMetadataChunks.m` exposes the exact
prepared chunk rows and reuses `fnReconstructMetadata` for complete key/chunk
reconstruction. It forces the typed identity/field projection before returning
staging chunks. Install `fnProjectRetainedOpenAlex.m` first. The additive table is
`config/native-openalex-retention.tmdl`; the compound-cursor extraction is
`config/source-OpenAlexMetadataChunks-page.dax`, two chunks per page to keep
expression payloads bounded. Their native compilation/execution remains open.
Core integrates that table into the existing bounded writer and
commit-last path with Source `OpenAlex`, ChunkTable `OpenAlexMetadataChunks`,
KeyColumn `OpenAlexWorkID`, ExpectedKeys from `expected_keys`, and source-specific
page/row/generation evidence. The existing native processing chain, archive byte
readback, duplicate/replay guards and consumer permissions remain prerequisites;
the preparation document itself must never be renamed into an accepted manifest.
No new flow, schedule or physical data store is required.

After accepted persistence, install `fnProjectRetainedOpenAlex.m` and
`RetainedOpenAlexPublications.m` beside the existing committed-history reader.
They derive a unique provider-work/DOI table from retained transport bytes,
preserve null counts and label OA/citation context by provider/time. Invalid or
conflicting typed observations fail refresh; retain the prior accepted consumer.
Full author/funder/topic/relationship fields remain in raw evidence for later
qualified projections. Core may left-join the unique DOI table to the canonical
publication view; preserve publication keys/counts, known values when incoming
fields are null, original dates/affiliations and field-specific observation times.
Do not add unmatched works to publication counts or infer CHHHS affiliation.

Rollback is removal of these additive isolated queries/source registration and
restoration of the exact saved writer/model preimage. Leave immutable raw evidence
and last-good committed consumers intact. One native happy path, saved definition
and byte/key readback plus unchanged replay are still required. The native M view
does not independently verify SHA256; that fingerprint is local provenance until
the owner's native byte readback reconciles it. This frozen bootstrap has no
provider credential: secure live acquisition and equivalent provider failure
branches remain separate integration work; do not embed the Keychain key in M,
flow definitions or staging files.
