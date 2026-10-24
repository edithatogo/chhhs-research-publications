# OpenCitations bibliographic metadata enrichment

Selected 24 October 2026 as the next independent enrichment capability. This
reuses the48 accepted OpenAlex DOI identities and the established native archive
pattern; it does not fetch the completed OpenCitations citation counts again.

The provider's [official quickstart](https://github.com/opencitations/oc_docs/blob/main/docs/api/quickstart.md)
documents anonymous Meta API `meta/v1/metadata/doi:<DOI>` requests, complete returned
metadata fields and identifier tokens. OpenCitations publishes its datasets under
[CC0](https://opencitations.net/). No new token, consent, connection or licence is
required by the selected anonymous route. No full text is requested.

## Native behavior

`scripts/prepare_opencitations_metadata.py` reuses the count collector's bounded
manual trigger, existing SharePoint connection, exact saved-byte guards,
manifest-last acceptance and cached replay algorithm. It adds Meta-specific
schema/identity checks and a distinct capability fingerprint, raw-file prefix
and completion marker. The citation-count collector and snapshots remain unchanged.

- Retain the complete decoded metadata response, request URL, response headers,
  observed time, source scope and frozen input provenance.
- Nonempty returned records require an `id` field whose space-delimited identifier
  tokens include the exact requested DOI, compared case-insensitively.
- Keep zero results as explicit `no_hit`; multiple results remain
  `multiple_matches_unadjudicated`. Never silently choose the first match.
- The envelope/entry `count` is the number of metadata records, not a citation count.
- Preserve provider author/identifier/date/venue strings without adjudication,
  inferred affiliation, date precision upgrades or overwriting canonical fields.
- One sequential request at a time, two-second pacing, finite timeout and zero
  retries. Request, validation or archive failure stops later provider requests.
- Complete only after every selected DOI's response is saved/read back exactly.
- The source-specific cached branch verifies saved raw bytes and selected DOI
  keys without provider requests or archive writes. Existing count replay evidence
  covers the reused algorithm; Meta-specific replay is a separate evidence scope.

No schedule, canonical register/model write, email, source-count mutation or
Crossref effect is part of this increment. The intended handover state is
manual/Stopped. This is a selected DOI metadata snapshot, not a full corpus or
an accepted author/project/organisation relationship.

## Evidence

Private operation directory: `private/ops/2026-10-24-opencitations-metadata/`.
Preparation rechecks the accepted48-DOI selection and prior complete manifest
hash rather than recollecting its input source. Native creation and exact saved
readback preceded one successful acquisition run of269.4seconds. All48 provider
actions succeeded. Independent M365 GETs verify48 raw envelopes (87,569bytes) and
the complete manifest (138,995bytes), including exact saved base64 and DOI tokens.

The48 responses contain46 metadata records:44 single matches, three no-hits and
one two-record multiple match retained without adjudication. All50 prior
citation-count archive identities/ETags/lengths/modification times remain exact.
Final full definition readback passes with manual trigger and Stopped state.
Private acceptance: `acceptance.json` in the operation directory.

No extra test suite, reharvest or Meta-specific replay was invoked. Existing count
replay evidence covers the reused cached algorithm, not a fresh Meta replay result.
Provider-failure stop and negative identity/schema cases were not fault-injected.
Standalone canonical solution admission and versioned native documentation remain
pending; existing shared documentation is not rewritten by this source change.
