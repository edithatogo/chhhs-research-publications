# OpenAlex field alignment into the existing RIMS pipeline

The target is complete authorised source capture for the existing RIMS scope,
then compatible field/entity alignment, then the existing canonicalisation,
registry upsert, exports and reports. The 48-work bootstrap is route proof, not
full OpenAlex coverage of the 1,281 distinct valid DOIs in the accepted snapshot.
Full coverage should reuse accepted cached responses and the existing archive;
it should not grow a separate enrichment pipeline or an inline-model data lake.

Complete raw payload/schema is already retained for the 48 successful works.
Only four provider fields are currently integrated into the native registry
writer. The remaining returned fields must have explicit mappings or retained
context dispositions; retaining raw bytes alone does not close field alignment.

| Existing registry field | Current source path | Native integration / candidate coverage |
| --- | --- | --- |
| OpenAlexID | id | Existing mapping; 48/48 |
| CitationCount_OpenAlex | cited_by_count | Existing mapping; zero distinct from missing; 48/48 |
| OpenAccessStatus | open_access.oa_status | Existing mapping; 48/48 |
| OAUrl | open_access.oa_url | Existing mapping; 31/48 |
| FunderNames | funders[].display_name; awards[].funder_display_name | Compatible local projection; 14/48 |
| GrantIDs | awards[].funder_award_id | Compatible local projection; 5/48. Structured funder/award IDs and direction remain in raw relationships |
| MeSHHeadings | mesh[].descriptor_name | Compatible local projection; all headings, 16/48 |
| AuthorKeywords | keywords[].display_name | Compatible local projection; all keywords, 46/48 |
| AffiliationsRaw | authorships[].raw_affiliation_strings; affiliations[].raw_affiliation_string | Compatible local projection; all reported raw strings, 45/48 |

The older mapper used removed `grants` and keyword `keyword`, and presentation
caps silently restricted lists. `scripts/project_retained_openalex_fields.py`
reads the accepted complete transport bytes, verifies fingerprint/identity,
projects current fields without those caps, and labels every field with source,
original observation UTC, raw response hash and candidate/missing disposition.
Legacy field paths remain supported for historical responses. Native deployment
of the five additional mappings remains coordinator-owned; no native model,
flow, list schema or canonical rule was changed by this local alignment work.

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
