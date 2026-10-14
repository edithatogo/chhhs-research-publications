# OpenAlex field alignment into the existing RIMS pipeline

The target is complete authorised source capture for the existing RIMS scope,
then compatible field/entity alignment, then the existing canonicalisation,
registry upsert, exports and reports. The 48-work bootstrap is route proof, not
full OpenAlex coverage of the 1,281 distinct valid DOIs in the accepted snapshot.
Full coverage should reuse accepted cached responses and the existing archive;
it should not grow a separate enrichment pipeline or an inline-model data lake.

Complete raw payload/schema is already retained for the 48 successful works.
The native model now exposes all nine compatible fields. The existing registry
writer's additional five-field run/replay remains a separate core-owned gate. The remaining returned fields must have explicit mappings or retained
context dispositions; retaining raw bytes alone does not close field alignment.

| Existing registry field | Current source path | Native model mapping / source coverage |
| --- | --- | --- |
| OpenAlexID | id | Existing mapping; 48/48 |
| CitationCount_OpenAlex | cited_by_count | Existing mapping; zero distinct from missing; 48/48 |
| OpenAccessStatus | open_access.oa_status | Existing Text target: preserve exact provider lowercase status; 48/48 |
| OAUrl | open_access.oa_url | Existing mapping; 31/48 |
| FunderNames | funders[].display_name; awards[].funder_display_name | Verified native model projection; 14/48 |
| GrantIDs | awards[].funder_award_id | Verified native model projection; 5/48. Structured funder/award IDs and direction remain in raw relationships |
| MeSHHeadings | mesh[].descriptor_name | Verified native model projection; all headings, 16/48 |
| AuthorKeywords | keywords[].display_name | Verified native model projection; all keywords, 46/48 |
| AffiliationsRaw | authorships[].raw_affiliation_strings; affiliations[].raw_affiliation_string | Verified native model projection; all reported raw strings, 45/48 |

The older mapper used removed `grants` and keyword `keyword`, and presentation
caps silently restricted lists. `scripts/project_retained_openalex_fields.py`
reads the accepted complete transport bytes, verifies fingerprint/identity,
projects current fields without those caps, and labels every field with source,
original observation UTC, raw response hash and candidate/missing disposition.
Legacy field paths remain supported for historical responses. The five additional mappings are now saved and processed in the existing model.
Their registry writes remain coordinator-owned; no list schema, canonical rule,
report binding or schedule was changed by this alignment.

Other returned fields remain complete source context, not discarded data.
Existing PubMed/DoRA precedence preserves canonical titles/authors/journal/dates
and keys. Provider bibliography can support the existing reconciliation policy,
not overwrite accepted records automatically. Authors/ORCIDs, institutions/RORs,
funders/awards, references and versions use their source identifiers and existing
typed relationship contracts rather than multiplying publication rows. Topics
are not ANZSRC FieldOfResearch codes; provider study-design tags are not a native
StudyDesign classification without a qualified crosswalk. Affiliation evidence
is not proof of current employment or institutional hierarchy. No extra impact
KPIs, full-text harvest, directories or providers are activated by alignment.

No candidate clears last-good values, reviews, identity or source-date uncertainty.
Source-specific citation counts and observation dates remain separate; the shared
CitationMetricsObservedUTC must not be relabelled as an OpenAlex timestamp.
Single-line target field capacity still needs exact native qualification; values
must never be truncated to fit. The current 48-work candidate's maximum GrantIDs
and OAUrl lengths are 130 and 148 characters; FunderNames/keywords/affiliations use
existing multiline targets. Larger batches retain all values in raw/relationships
and fail the affected projection safely if a flat target cannot hold them.

[Official current work attributes](https://help.openalex.org/data/works/attributes/)
confirm that `funders` and `awards` replace `grants`. Actual retained-schema
readback supplied the mapping and coverage above; these counts describe this
slice, not completeness of the provider or institutional research activity.

Private local alignment receipt:
`private/ops/2026-10-14-openalex-compatible-field-alignment-private.json`.
Four focused alignment tests pass. Full coverage, additional native mappings and
routine acquisition remain explicit delivery gaps; the downstream pipeline is
reused rather than replaced.

## Native status casing and existing representations

The qualified OpenAccessStatus destination is Text. Preserve exact provider
values such as `closed` and `gold`; do not apply the legacy local mapper's
Titlecase conversion. Expected writes must bind the accepted native context,
not older candidate-record presentation values. Existing nonblank registry
values remain preserved under the missing-only policy. A later destination
Choice/enum mapping would require its own explicit qualified translation.

The core owner also reconciled the four legacy PMID-zero DoRA registry items:
their source records are already present in retained DoRA and merged into the
accepted canonical publications. Preserve those secondary registry
representations; do not treat them as missing raw coverage or reharvest/delete
them to make counts agree. Source-map evidence remains private and core-owned.

## Prepared same-model native envelope

The source-owned `fnProjectRetainedOpenAlexAligned.m` wraps the unchanged native
validator. `build_openalex_alignment_model.py` refuses a deployable candidate
until the physical destination schema is verified, fingerprinted and supplies
positive limits for all five additional fields. The agreed input is the accepted
46-part, 48-work model; no new table, connection, provider request or pipeline is
created. Exactly four parts change:

| Part | Additive change |
| --- | --- |
| expressions.tmdl | Append qualified limits and the wrapper; every existing expression body remains a byte-for-byte prefix |
| tables/OpenAlexWorks.tmdl | Add five provider-specific fields plus exact raw UTC, response hash and projection diagnostics; preserve the six existing columns/values |
| tables/OpenAlexPublicationContext.tmdl | Add their lookups and observation columns; preserve canonical membership and the existing four-field mappings |
| tables/OpenAlexFieldProvenance.tmdl | Preserve the existing three branches; add WorkID and five field branches, plus raw UTC/hash/diagnostics |

The remaining 42 parts, including model.tmdl and all Publication/source definitions,
remain unchanged. Expected slice readback is 48 works, 51 existing canonical keys,
and 459 field-provenance rows. Four existing OpenAlex tables are the affected
processing scope; Publication and broader source harvesting remain excluded.
These are prepared expectations, not native execution proof.

If a candidate exceeds either the qualified physical field limit or the model's
32,766-character cell bound, only that field candidate is suppressed and a
`projection_rejected_size` diagnostic records its name, length and bound. Complete
original text remains in raw evidence; the local reference also preserves it in
raw-linked candidate provenance. No prefix truncation, empty-success substitution
or clearing of existing registry values is allowed. Any diagnostic must remain
visible to the coordinator and downstream exception path; a successful table
refresh alone cannot claim complete field alignment when diagnostics are present.

Microsoft's M parser accepts the wrapper. Three native-envelope preservation,
qualification and drift tests pass; five Python field/size checks pass. Parser
and local checks do not establish native save, processing or physical field
qualification. The other RIMS chat owns that qualification and lease allocation;
no native object was changed by this preparation.

## Native nine-field acceptance — 14 October 2026

The physical fields were qualified through the existing SharePoint connection:
four Note fields (63999-character physical policy) and GrantIDs Text (255). The
model cell bound remains separate. After an explicit model-only lease and fresh
exact baseline check, the four prepared parts saved successfully on the same
isolated model. Native readback differs only by serializer blank lines in the
new expression/provenance portions; every prior expression body and the other
42 parts are unchanged. No new table/connection/provider request was introduced.

The affected four-table transactional refresh completed. Native readback: 242
raw chunks, 48 complete responses, 51 canonical context rows and 459 provenance
rows. All nine candidate fields match the lossless projector and qualified size
policy, and the actual parsed native diagnostic count is zero. Original Works,
Context and provenance columns/values, all complete transport bytes/schema, exact
raw observation UTC/hash and all 40,230 Publication values remain unchanged.
The unrelated existing source-audit warning remains recorded.

Transient status/result reads timed out; the same retained operation handles
resolved without write resubmission or authentication changes. The model lease
returned at terminal acceptance with native context/works/provenance exports.
The other RIMS chat owns the existing writer's nine-field run/replay. Full
1,281-DOI coverage and routine shared-archive acquisition are still open.

Private acceptance: `2026-10-14-openalex-nine-field-native-acceptance-private.json`.
Private model handback: `2026-10-14-openalex-nine-field-to-core-model-handback-private.json`.
