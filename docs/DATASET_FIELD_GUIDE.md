# Dataset field guide

Use this guide to interpret existing RIMS datasets and preserve their evidence
when making an authorised correction. It is a reading aid, not a new schema,
permission grant or instruction to run a collector. Field names below are exact
logical names unless an actual SharePoint internal name is shown explicitly.
Native target identities and row payloads remain in private operational records.

## Read the research dashboard

Monthly Publications is the starting page for reviewing recorded monthly output.
It uses native Power BI cards, a 24-complete-month trend, facility/service and
source comparisons, a month slicer and standard navigation buttons. Clear month
restores the previous complete Australia/Brisbane reporting month. In the native
month dropdown, use Search to find a `YYYY-MM` value; select one month at a time.

The publication total counts distinct accepted canonical publications. Facility
matches overlap, so their bars must not be added into an HHS total. The undated
card covers all periods and remains separate from the selected month. Publication
data refreshed shows the publication reporting-window processing timestamp in UTC;
it does not establish that every source or research dataset was acquired then.
Indexing delays can revise earlier months. Counts do not measure research quality,
patient benefit or locally approved funding.

Publication details opens full citation detail. Source reconciliation opens
overlap and diagnostic views. Open SharePoint register links to the existing
keyed source-row view; its row count is a different grain from the canonical
publication total. Use the normal Power BI page list to return to Monthly
Publications. Native chart help explains scope without adding long landing text.

Research datasets opens the maintained study and award registers. Their separate
counts, source statuses and original links describe register records, not complete
provider corpora or verified local projects. Study and award filters operate on
their own registers. Original source strings are retained in `SourceRecordJSON`,
including date/amount uncertainty; operator notes stay in the source lists.
The accepted 20 October capture reconciled six studies and 2,217 awards. Later
operator refreshes after accepted register updates can change these counts;
acquisition schedules and unattended report delivery have separate evidence.

Existing permissions apply to the report and each linked destination. The user
has deferred wider-reader access; these navigation improvements add no sharing.

Research relationships adds separate candidate, confirmed-reviewed and unresolved
funding counts, imported activity records, and author/facility-match distributions.
At the accepted capture these are two candidates, zero confirmed, zero unresolved
and 442 activity records. Its three SharePoint buttons open the keyed publication,
candidate relationship and confirmed-reviewed views. Clear a chart selection to
restore the page's counts. Multiple listed authors, matched facilities and source
project-ID strings do not establish verified collaborators or publication–project–
award links. Such links still need exact qualified identifiers and evidence.

`DORAObservedUTC` in the activity model is an explicitly parsed UTC observation
displayed through the existing dateTime field. Raw high-precision source text is
retained in SharePoint; the model does not promise every source subsecond digit.
Observation time, model processing time and provider modification dates describe
different events and must not be combined into a universal freshness badge.

## Source freshness and source-supported relationships — 21 October 2026

The Source freshness page distinguishes a provider's modification time, acquisition
or observation time, and model processing. A latest timestamp among imported rows
does not prove complete source coverage or a successful scheduled run. Unknown
means that the model has no qualified scalar for that timestamp; the source may
still have a complete retained acquisition. No common processing date substitutes
for all providers' freshness.

Source-supported collaboration uses source-stated author and institution IDs on
publications that map uniquely to the canonical register. Person keys preserve
provider identity or an unambiguous source-stated ORCID mapping. A valid ORCID
checksum establishes syntax, not authenticated identity. Conflicting identifiers
and unresolved author mentions remain visible and separate; names alone do not
merge people. Institution pairs represent source co-occurrence on a publication,
not confirmed institutional partnerships or current employment.

The accepted 21 October snapshot covers 1,318 publications, 1,105 identified source
authors, 7,790 distinct source researcher pairs and 2,489 distinct institution
pairs. Pair totals count distinct identifier pairs stored in a consistent order across admitted source
evidence, not publications, employee headcount or assessed collaboration quality.
Multiple authors, an exact name label, or a facility match cannot establish a
verified collaboration. No person identity has been authenticated by these views.

Publication, study and award links keeps these evidence types separate:

| Evidence shown | Accepted snapshot | Interpretation |
|---|---:|---|
| OpenAlex publication–award assertions | 23 | Explicit source assertions; source award IDs remain unchanged. |
| PubMed grant references | 169 | Original grant numbers and source-scoped agency labels, including unresolved mappings. |
| Publication–trial references | 26 | Explicit ClinicalTrials.gov RESULT/DERIVED references and PubMed trial identifiers; background citations are excluded. |
| Publication–award identifier mappings | 27 | Exact retained OpenAlex/Crossref identifiers qualified against ARDC grant records and funder authority. |
| Complete clinical-study award chains | 1 | Explicit publication → clinical trial → versioned protocol funding identifier. A clinical trial is not a DORA project. |
| Registry-related publication links | 1 from 25 source references | Typed ARDC publication references resolved through exact repository handles and explicit identity-equivalent DOIs where available. Related-publication evidence is not a fundedBy assertion. |
| Historical government-record publication links | 3 across 2 application IDs | Exact Crossref funding numbers joined to original NHMRC workbook APP IDs; preserve the historical application namespace and workbook coordinates. |

Unmapped references and identity-unknown records remain retained. A Figshare
IsPublishedIn relation does not establish DOI identity. APP/GNT/MRF prefix variants
remain unresolved without explicit supporting evidence; original strings are not
silently rewritten. A complete DORA publication–project–award chain still requires
explicit, qualified project relationships. Existing candidate/reviewed funding
links remain 2/0 and use their original review rules.

Each admitted reference retains its source work/publication ID, namespace-qualified
target, original identifier, source URL, observation or source version, raw payload
hash and relationship type. Government references also retain the complete source
workbook hash, source URL, sheet, row and original identifier column. These are
source facts, not human funding decisions, current award status or register
admissions. No monetary allocation or award-register total changes.

The report and model retain their original identities. At the accepted snapshot
they show 1,341 canonical publications, six study-register records and 2,217
award-register records; the evidence table has 23,552 rows across different grains.
Do not add those grains together. Clear a table or chart selection to restore
the unfiltered counts.

The crosswalk packets are immutable operator-qualified snapshots. Model refresh
replays the selected retained bytes. A new source revision needs a newly qualified
packet and normal model/report reconciliation; these views do not add automatic
enrichment or change existing collector schedules. Retain human notes, review
states, prior generations and recovery preimages. Local source, saved native
definitions, runtime processing and business acceptance remain separate evidence.

## Report-delivery observations

The independent delivery monitor reads the existing register CSV, printable index
and every HTML part, then adds an immutable observation receipt in the existing
reporting folder. It does not overwrite a report generation or the last good
output. The selected source export is due on day 1 at 09:00 Brisbane, with a noon
completion deadline. The monitor is enabled with the user-approved daily 12:05 Brisbane schedule,
starting on 1 November 2026. Native activation and exact definition readback
are verified; actual unattended operation remains unproved until that occurrence.

The controlled readable-output check and missing-delivery diagnostic are verified.
These tests do not prove a natural unattended occurrence. A successful monitor
run or Dataverse's `Scheduled` label does not by itself prove automatic export
origin. Retain the receipt's commissioning flag and distinguish missing, late,
failed, ambiguous and unqualified evidence. The observation's false hash-verification
flag must not be converted into a cryptographic integrity claim.

This delivery scope covers all keyed register rows in the extraction, without a
publication-month filter. It does not certify canonical monthly membership,
provider coverage, research quality or fresh acquisition. Existing report and
source-generation history remain authoritative. If observation or content readback
fails, reconcile the same source run and preserve its handles before replay.

## Choose the right unit before counting

| Dataset | Identity and unit | What it does not establish |
|---|---|---|
| Publication register | `SourceKey` is the intake/source lookup identity; `CanonicalKey` is the accepted publication identity. Retained aliases and blank-key placeholders are separate register rows. | Physical row count is not the canonical publication total. |
| Researcher projection | `MentionKey` identifies a publication-scoped author position; `NameGroupKey` groups an exact retained label. | A name group is not a resolved person, employee or contribution measure. |
| DoRA activities | Resource identity plus source `_id`; retain the source/provenance fields and raw dates. | A listed activity or contact label does not prove current project status or consent. |
| ARC award context | Source-scoped award identity; original source ID remains unchanged. Funding relationships use `AWARD:arc:<SourceID>`. | An award-context record is not necessarily funded, active or an open opportunity. |
| Grant Relationships | `RelationshipKey` identifies a typed relationship between exact `FromKey` and `ToKey`, with `AwardID` and `EvidenceURL`. | An identifier match alone is not confirmed funding or institutional attribution. |
| QGIP retained source and candidates | Preserve complete source identities and observations before selecting candidates. | A candidate is not an admitted canonical opportunity, eligible round or verified open call. |
| Source-expansion registers | Award context uses `SourceKey` = lower-case funder namespace + `:` + original `SourceID`; source assertions retain their own namespaces. | A prepared schema, imported seed or retained original does not prove a deployed collector or refresh. |

Count distinct accepted canonical publication keys in the selected generation and
filter context. Do not add register rows, author mentions, label groups, awards
and relationships together. See the implemented [publication dictionary and
denominators](SHAREPOINT_LIST_REGISTRY.md#implemented-data-meanings--15-october-2026)
and [researcher summary](RESEARCHER_SUMMARY.md).

## Structured monthly publications report

The separate operator-run structured report uses the existing accepted monthly
extraction. It preserves every included canonical publication key, complete
citation, source evidence and date uncertainty. Its saved source snapshot,
HTML report and completion manifest share an explicit period and output revision;
the manifest also records accepted generation, query/template versions and count.
Metadata intake remains independent of report generation.

The native standard SharePoint path has verified HTML generation and rendered
output, unchanged replay, provenance metadata and preservation of an edited
output. Replaying the same accepted input/revision performs no Save actions.
An edited or changed source/template/output at that revision fails before overwrite;
use a new explicit revision after reconciling a partial folder. Preserve human
edits and issued history. Existing Title and Description properties aid navigation;
the adjacent manifest/source remain authoritative for full provenance.

The current canonical solution contains33 workflows, including this report under
its original identity; the selected historical R20b package retains its32-workflow
baseline. The report is Stopped and operator-run. SharePoint serves HTML as a
download; browser printing and manual editable Word remain working alternatives.
Automatic DOCX/PDF generation and Word-body refresh are not qualified. Generation
is not substantive review, approval, circulation or production activation.

## Publication fields operators encounter

The list retains historical internal names. Use the logical meaning and exact
internal name together when inspecting an API response or preparing a change.

| Logical name | Native internal name | Meaning |
|---|---|---|
| `Title` | `Title` | Bounded display label; populated existing text is protected. |
| `SourceFullTitle` | `SourceFullTitle` | Full plain-text source projection; fill-only when empty. The original payload remains in the archive. |
| `SourceKey` | `field_1` | Source lookup/alias key; never manufacture keys for legacy placeholders. |
| `CanonicalKey` | `field_2` | Accepted publication identity used for joins and deduplication. |
| `Authors` | `field_3` | Semicolon-separated source labels; commas inside names are not separators. |
| `PublicationYear` | `field_5` | Publication year supported by retained date evidence. |
| `PublicationMonth` | `field_6` | Supported `YYYY-MM` period or blank; never infer a missing month. |
| `PublicationDateRaw` | `field_7` | Retained date text from the projection, not necessarily parseable. |
| `PublicationDatePrecision` | `field_8` | `day`, `month`, `year`, `range`, `unknown` or `rss_unverified`; a range is not a point date. |
| `CHHHSAffiliatedAuthors` | `field_15` | Publication-level affiliation labels; blank is unknown, not proof of no affiliated authors. |
| `ReviewStatus` | `field_17` | `Included`, `Needs Review` or `Excluded`; exclusions remain stored. Needs Review is informational and does not block routine valid intake. |
| `ReviewNotes` | `field_18` | Preserved notes; presence alone is neither approval nor a structured correction ledger. |
| `FirstObservedUTC` | `field_19` | Registry first-create processing time, preserved on replay. |
| `LastObservedUTC` | `field_20` | Registry latest-upsert processing time, including replay; not proof of changed source content. |

`GrantIDs` retains source grant tokens. The funding matcher compares complete
accepted tokens to exact ARC identifiers; title, investigator and funder-label
similarity do not create award relationships. `PUB:` register keys and model
publication keys are different identity layers: use the explicit accepted
crosswalk, never rename one to resemble the other.

The maintained [field meanings](../config/publication-field-meanings.json),
[publication views](PUBLICATION_VIEWS.md) and
[source reconciliation](HISTORICAL_SOURCE_RECONCILIATION.md) contain the detailed
contracts. Historical intended schema tables are not evidence of current native
types, required settings or unique-value enforcement.

## Open-access paper storage and publication links

The existing publication register has four additive OA fields. Prepared archival
selection requires a nonblank, unpadded CanonicalKey; legacy blank-key placeholders
are skipped. They describe a
separate operator-run archival process; publication intake remains independent
of paper availability. External `OAUrl` and Europe PMC links remain source links.
They do not establish that a paper has been saved in SharePoint.

| Native internal name | Type | Meaning and operator use |
|---|---|---|
| `OALocationCandidates` | Note | JSON candidate projection bound to the exact CanonicalKey and DOI, with provider, file URL, licence, article version and retained-source provenance. A candidate alone is not archival acceptance. |
| `OAArchiveState` | Text | Durable archive outcome: retrieval pending, saved, linked, link-only, retryable failure or terminal failure. Native values use underscores, for example `retrieval_pending` and `link_only`. |
| `OAArchiveURL` | URL | Saved SharePoint paper reader link. Interpret with the matching canonical identity and verified receipt; a URL alone does not prove bytes, permissions or current association. |
| `OAArchiveManifest` | Note | JSON receipt retaining attempt, CanonicalKey, DOI, source location, licence/article version, folder/file identity, ETag and integrity evidence. Preserve this field during recovery. |

`linked` means the flow persisted the file receipt and register link. Independent
native byte/hash and authorised-reader checks are separate evidence. SHA-256 is
currently recorded by the existing operator-run verification adapter; a null
value or `independent_native_readback_required` must not be presented as a verified
hash. Provider-asserted MD5 and actual-byte SHA-256 have different provenance.
Neither a local downloader status nor a successful parent flow run proves a
SharePoint archive count. Count distinct CanonicalKeys only after reconciling the
selected native archive evidence; do not count files, versions or candidate URLs
as separate publications.

Ordinary replay skips linked records. Explicit `forceRefresh` handling
reacquires source locations and compares prior saved bytes. The unchanged-source
recheck and bounded backfill/replay have native evidence. Changed source content
preserves the old copy and retains a separate revision with receipt history.
A real changed-content refresh verified distinct saved bytes and file identity,
with the previous copy, link, hash and unrelated register fields preserved. A saved-but-unlinked
receipt resumes linking against the same file identity and ETag. A conflict or
human edit is preserved; do not clear the manifest or replace the file to force
success. Unknown or restricted archiving terms remain link-only with a reason.
No routine per-paper approval queue is introduced.

### Library properties for saved paper copies

The existing document library now uses `Title` and Description (internal
`_ExtendedDescription`, REST `OData__ExtendedDescription`) for readable labels
and a marked provenance summary. Only verified linked current copies are
eligible. Blank Title is filled from the canonical publication title/article
version; an existing human title is preserved. Human Description text remains
before the managed block. Canonical key, DOI, source/version/licence, original
retrieval time, content SHA256 and original source/register links are projections;
the complete archive manifest and receipt remain authoritative.

The operator-run metadata step changes no PDF bytes, file name/path/identity,
register manifest, reader link or access. It uses precise ETags, refuses human
or source drift, and replays without another property write. Native metadata
updates create a new version and file ETag; earlier content-verification ETags
remain historical evidence. Prior versions are retained and their identical
PDF bytes are retrievable. Saved-but-unlinked recovery and earlier paper copies
are left untouched. See the maintained [operator and recovery guide](PAPER_LIBRARY_METADATA.md).

The four fields, selected real-paper save/link, unchanged-source recheck and
bounded five-record backfill/replay have scoped native evidence. The storage
barrier's successful staging, saved-byte comparison, receipt and linking path
has now executed for a real paper; independent PDF identity/integrity and existing
reader access are verified. An uncertain-storage fault was not induced.

The OA flow is already a member of the accepted canonical solution. Retained
PubMed own-article PMCID integration is verified. Accepted OpenAlex responses
supply six discovery candidates under the existing licence projector; exact
parent identity and native producer integration require their own readback.
The narrowly qualified Frontiers public-health route binds provider, CC BY,
article version, DOI and canonical publisher path. One retained OpenAlex candidate
has now completed native save/link with exact DOI, saved-byte comparison to the
publisher file and hash recording verified. Its unchanged replay preserved the
complete publication row and both files; the native SharePoint reader displayed
the correct paper. General publisher-host admission is not implied.
The DOI-bound OpenAlex OUP route also binds CC BY, published article version
and the exact publisher DOI path; general host admission is not implied. A real
HTTP403 retrieval continued to a licensed PMC alternative and completed save/link.
Both accepted and published copies open through the existing SharePoint reader.
These are technical system checks, not scientific or business assessment.
Europe PMC/ORCID standalone payload admission remains conditional. Source links and null licences are
preserved even when no archival candidate is admitted. The
[canonical OA graph](flow-diagrams/canonical/source-publication-open-access-archive.json)
and [generated formats](flow-diagrams/generated/source-publication-open-access-archive.md)
describe the parameterised source variant. The selected PMC staged-save/link path
has native evidence; this does not prove every branch or later source integration.
[SVG](flow-diagrams/generated/source-publication-open-access-archive.svg) and
[PNG](flow-diagrams/generated/source-publication-open-access-archive.png) are full-graph
zoomable exports; the Visio file separates nested scopes into pages.
See [E01-OA](../conductor/tracks/E01_flow_automation/open-access-paper-archiving-20261018.md)
for the active checkpoint and acceptance boundaries.

## Funding relationships: state is evidence, not a label shortcut

The typed contract has exactly eight relationship fields:
`RelationshipKey`, `RelationshipType`, `FromKey`, `ToKey`, `AwardID`,
`EvidenceURL`, `Confidence` and `ReviewStatus`.

| Reader state | Required meaning | Operator interpretation |
|---|---|---|
| Candidate | Valid `candidate_award_match`, candidate confidence and explicit `Needs Review` or `Reviewed` status, with accepted typed identity/source gates. | Exact identifier evidence worth retaining; do not count as confirmed funding. |
| Confirmed reviewed | Valid `funded_by_award`, `confirmed` confidence and explicit `Reviewed` status, with exact award/funder/publication/evidence identity and source-status gates. | Requires an actual supported review decision; setup must not fabricate one. |
| Unclassified | A live row fails identity registration, typed validation or positive admission, including unknown/blank/padded status or new unregistered evidence. | Preserve the raw row and investigate its specific reason. It is not a confirmed link. |
| Withdrawn/retracted/rejected | Retained negative review state. | Preserve history; do not admit it as confirmed funding or delete it to improve counts. Such rows remain available in All Items. |

The native candidate and confirmed views use positive predicates. An unknown
status must not enter simply because it is not recognised as withdrawn. The
consumer retains every live row, while admission measures classify only accepted
states. A valid zero confirmed count is not a technical defect.

`RelationshipKey` is derived from type, exact from/to keys, award ID and evidence
URL. Changing evidence or type changes identity; never hand-edit a key or silently
rewrite an existing relationship. Identity-material rows register possible typed
identities only: they contain no live confidence/review decision and are not
relationship facts to count. New unregistered evidence remains unclassified until
the existing supported registration/model path is updated.

See [funding relationships and views](FUNDING_RELATIONSHIP_VIEWS.md), the
[consumer contract](FUNDING_RELATIONSHIP_CONSUMER.md) and the
[typed relationship implementation](../scripts/grants_relationships.py).

## Raw retention, projections and source expansion

Retain complete original payloads, pages, workbook sheets, unknown fields and
excluded rows before filtering. A compact list, candidate projection, model table
or CSV is a consumer of that evidence, not its replacement. A hash proves the
identified bytes, not completeness of the provider, correctness of interpretation
or business acceptance.

- **ARC:** retain source status and amount text. Blank amounts stay unknown;
  declined/not-yet-accepted records must not become funded-award totals. Do not
  substitute an earlier announced amount for a missing current value or sum
  amounts with incompatible meanings. See [ARC reader](ARC_AWARD_READER.md).
- **QGIP:** retain the unfiltered source alongside its candidate projection.
  Excluded source rows are not deleted evidence; canonical opportunity admission
  remains a separate decision. See [funding source retention](FUNDING_SOURCE_RETENTION.md).
- **NHMRC:** the retained workbook's `Application ID` is distinct from `Grant ID`.
  Preserve leading zeros and original workbook date-system/cell evidence. File
  label, application year, announcement date and dictionary version have separate
  meanings. A later collector/consumer receipt supersedes only its specific older
  pending milestone, not the original's historical evidence.
- **NHMRC/MRFF award register:** the maintained
  [award-context schema](../config/award-context-registry.schema.json) includes
  `SourceKey`, `SourceID`, `Funder`, `AmountMeaning`, `FullAwardTitle`,
  `Organisation`, `Scheme`, `ReportedAmountSource`, `SourceDatesJSON`,
  `RelatedIdentifiersJSON`, `SourceProvenanceJSON` and human `OperatorNotes`.
  Preserve exact decimal source text and meaning; do not infer currency or sum
  overlapping source assertions.
- **ClinicalTrials.gov, MRFF, ROR, ARDC, Crossref and DataCite:** collector,
  archive, refresh and replay acceptance are separate source-specific milestones.
  Source assertions are not automatic publication merges, resolved organisation
  identities, funding claims or opportunity admissions. The native pipeline owner
  maintains current deployment state; this guide does not freeze that moving queue.

## Current accepted raw acquisition — 19 October 2026

Raw archives are the shared horizontal source layer. Typed registers and subject
views consume selected records later; their row counts are different units.
Retain originals, unknown fields, source identities, acquisition scope, schema,
version and manifest before filtering. These observations describe accepted
captures, not permanent source sizes or automatic admission to a subject view.

| Source | Accepted retained scope | Configured updates and remaining boundary |
|---|---|---|
| PubMed | All 1,276 own PMIDs matching the maintained hedge; 13 original XML batches independently downloaded and reconciled. Original external-DTD bytes remain in the archive. The verified immutable completion checkpoint includes 1,231 article DOIs, excluding cited-reference DOIs. | Daily 01:30 Brisbane with full-hedge reconciliation, including older-record updates. Crossref and DataCite consume the verified raw checkpoint independently of register admission, preserving the legacy input union. Raw retention does not rewrite the existing publication register. |
| NHMRC | All 14 current official workbooks; original bytes and every worksheet independently verified. | Weekly Monday 05:00 Brisbane. Application IDs, grant IDs and workbook/sheet provenance remain distinct. |
| MRFF | All 3 current official workbooks; original bytes and every worksheet independently verified. | Weekly Monday 06:00 Brisbane. The previous 1,915 typed awards are a separate projection, not the complete workbook inventory. |
| ARC | Complete configured source: 34,977 records in each of two reads, 140 archived pages. | Weekly Monday 07:00 Brisbane. Preserve original source IDs and complete raw fields before context/relationship selection. |
| QGIP | All 24 distinct resources from 25 agency mappings; 4,645 raw rows per complete read; 96 saved page files independently verified. | Weekly Tuesday 05:00 Brisbane. Preserve agency aliases, resource IDs, offsets, schema and technical `_id`, including rows with blank business fields. |
| Queensland DoRA activity | Two identical complete reads of 442 raw records; all 4 archive files independently verified. | Daily 02:30 Brisbane. This activity collection and its source identities remain separate from the publication repository below. |
| DoRA publications | Complete maintained collection of 709 records, 72 before/after collection pages and full original HTML retained. All native full-content readback guards pass; independent first/last HTML samples and the complete marker/manifest are verified. Own DOI fields expose 695 raw values, including one invalid value retained for traceability, and 694 valid canonical DOIs. | Daily 04:30 Brisbane. Preserve raw metadata and invalid values before downstream normalisation. The immutable producer checkpoint feeds Crossref/DataCite without waiting for publication-register admission. Not all 709 HTML files were independently downloaded a second time. |
| ClinicalTrials.gov | Two complete 12,666-record query passes and 254 retained pages; all 127 first-pass pages and six institutional seeds independently reconciled. The seeds are already included in the query keyset. | Weekly Wednesday 04:00 Brisbane. Maintain the configured Australian-site/sponsor and institutional-alias scope, without date, status or study-type filtering. The six-record historical register projection below is separate. |
| Crossref | Complete maintained 27-query hedge with accepted full baseline and indexed catch-up retained. Final related input is 1,283 distinct DOIs from the verified PubMed/DoRA producer union plus legacy inputs; two additional full DOI responses are independently verified. Raw HTTP404 responses and checkpoint lineage remain retained. | Daily 03:30 Brisbane. The normal daily graph is restored; the bounded extension reused its verified capture window rather than replacing the last-good checkpoint or restarting the corpus. Provider assertions do not automatically change publication decisions. |
| DataCite | Final two-producer qualification retains 76 raw JSON pages from 76 queries (11 institutional and 65 related), 739 raw rows including query overlap, and 1,283 input DOIs. Both raw producer checkpoints and invalid raw inputs are retained. Earlier full JSON/XML baseline and catch-up evidence remain preserved. | Weekly Thursday 05:00 Brisbane. Retain overlapping raw responses. Native saved-content guards pass for every current page; independent manifest/root/input snapshots and unchanged full-metadata baseline evidence are reused. Exact counts and the pagination limit must pass; reaching the limit fails instead of truncating. |
| ARDC | Complete public RDA OAI-PMH RIF-CS registry metadata: 436,536 unique records across 4,366 original XML pages and 4,370 exact archive files. Incremental catch-up retains 15,252 unique update-window records across 153 XML pages and 157 files. Full token chains, key counts, native saved-content guards and root/manifest equality pass; the original baseline checkpoint is byte-unchanged. | Weekly Monday 04:00 Brisbane. Preserve all public registry metadata before secondary selection; underlying research files are excluded. First/last XML samples are independently verified, not every raw XML page downloaded twice. Current publication/funding relationship projections remain separate. |
| ROR | 144,717 organisations, including 2,043 Australian organisations; complete official release, checksum/ZIP checks and unchanged replay accepted. | Monthly recurrence and first natural scheduler run accepted. Raw foreign/inactive records remain retained before reference selection. |

Except the explicitly accepted ROR scheduler run, first natural weekly/daily
occurrences above remain unobserved. Started and saved schedule configuration
do not prove future execution. ARDC's final baseline/catch-up and weekly graph
are handed back and its canonical solution membership is accepted. Existing
bounded consumer samples remain separate from this expanded raw metadata scope.
Accepted raw retention does not
automatically expand the shared assertion consumer or rewrite publication,
funding or activity registers. The published documentation generation remains
separate until this repository update is saved and read back natively.

## Historical bounded source/consumer paths — 18 October 2026

The following table preserves the earlier typed-consumer qualification. Use the
raw acquisition section above for the later retained source scope. In particular,
the old DataCite relationship sample and ROR assertions are not raw corpus totals.

SharePoint lists are the maintained registers. Original workbooks and HTTP
responses remain archived evidence; Excel processing copies do not replace the
register or the original. The following counts describe bounded technical
verification captures, not provider-wide coverage or research findings.

| Source / register | Verified capture | Read and count safely |
|---|---|---|
| ClinicalTrials.gov / study register | Six study records; archive-to-register refresh and same-packet replay verified. | Use the retained study identity. Source status, dates and sponsor labels are provider statements, not local eligibility or participation decisions. |
| NHMRC / award context | 302 records; native refresh and zero-write replay verified. | Preserve `Application ID` separately from `Grant ID`, exact decimal amounts and workbook/sheet/row provenance. |
| MRFF / award context | All 1,915 source award rows verified through native refresh and same-packet replay. | Source IDs can be numeric or contain newlines. Never trim, rewrite or infer identity from a prefix. Footers and formatting rows remain in the original workbook but are not award rows. |
| ROR / source assertions | Full official ROR release retained: 144,717 unique organisations, including 2,043 Australian organisations; publisher checksum/ZIP integrity verified. Unchanged-release replay and first monthly scheduler run passed. The prior 32 typed assertions remain a separate bounded reference sample. | Full raw retention does not establish downstream Australian/reference projection or institutional relationships. Future monthly occurrences have not yet been observed. |
| ARDC / source assertions | Two exact-identifier lookup outcomes; native refresh/replay verified. | A lookup outcome is not proof of a funding relationship or complete catalogue coverage. |
| Crossref / source assertions | Ten DOI-bound notice records; native refresh/replay verified. | Preserve the provider's notice/update relation and raw projection; do not automatically merge or change publication review status. |
| DataCite / source assertions | Two raw-bound relationship records; native refresh/replay verified. | Preserve source types, version links and related identifiers as assertions; they do not establish reviewed local relationships. |

The seven settled paths above preserve stable register IDs and operator notes;
same-packet replay changed no item ETags in their recorded verification scopes.
MRFF replay preserved all 2,217 shared award-register items, including NHMRC's
302 records; all 1,915 MRFF field projections passed exact saved readback.
ROR, ARDC, Crossref and DataCite share a source-assertion consumer; their diagrams
therefore include one shared consumer rather than four invented native flows.
The bounded operator-run consumer captures above retain their recorded Stopped
states. The later raw acquisition section records the collectors' accepted
Started recurrence separately; it does not enlarge those consumer projections.
The final canonical export contains32 workflows with verified membership,
definitions and reference mappings. First future schedule observations and
production/business acceptance remain separate.

| Source-assertion field | Meaning and preservation rule |
|---|---|
| `SourceKey`, `Source`, `SourceID` | Source-scoped identity and original identifier. Preserve exact values and namespace; never rekey to make a display label cleaner. |
| `ContextKind`, `RelatedID` | Typed provider context and related identifier. Context is not a confirmed local relationship. |
| `SourceURL`, `FullSummary` | Retained provider evidence link and full source summary, subject to the maintained schema. |
| `SourceProjectionJSON` | Complete selected source projection; retain the raw archive as well, including unknown source fields. |
| `SourceProvenanceJSON` | Exact source generation, hashes and transformation context; a later processing time does not renew provider freshness. |
| `OperatorNotes` | Human-managed content excluded from source-owned refresh writes. |

For award-context fields, retain source date text when the workbook cell is not
a numeric Excel date. Preserve numeric-date system evidence separately; do not
infer a calendar date from an unqualified serial. When a source key contains a
newline or other significant character, use the existing exact-key adapter and
stable numeric item ID for saved readback, rather than a display-formatted CLI
string or an improvised OData identity repair. Unique-key enforcement prevents
duplicates; a rejected duplicate is a failed update to reconcile, not success.

See the maintained [source-assertion schema](../config/source-assertion-registry.schema.json)
and [current source delivery records](../conductor/post-mvp-sequence.md#current-source-queue--18-october-2026).

## Dates and provenance

| Value | Safe interpretation |
|---|---|
| Publication date/precision | Source-supported publication period; unknown components remain unknown. |
| Provider modification or announcement date | Meaning supplied by that provider; not necessarily retrieval or current status. |
| Archive retrieval/acquisition time | When that particular retained source generation was obtained. |
| Register `FirstObservedUTC` / `LastObservedUTC` | Registry processing history as described above. |
| Relationship connector `Modified` | Raw connector text; do not label timezone-free text UTC or source freshness. |
| Consumer `SourceReadUTC` | Runtime observation time; not evidence of a new provider acquisition. |
| Version / ETag | Concurrency/history evidence supplied by that route. A connector version does not substitute for an absent ETag. |

Keep source URL, snapshot identity/hash, source and transformation versions and
observation context with the selected generation. Fresh processing of an old
snapshot does not make its source current. Unknown is not zero, empty text is not
necessarily null, and a missing row in a new source snapshot is not proof of
withdrawal or permission to retire a stored record.

## Editing, correction and safe replay

Source keys, canonical crosswalks, source values, provenance and derived admission
are maintained through their existing source/consumer mechanisms. Do not edit
these directly to force a desired report result. `OperatorNotes` is explicitly
human-managed in award context and excluded from source-owned writes. Publication
`ReviewNotes` and existing review/correction records retain human input; their
presence does not authorise changing source identity or declaring approval.
Relationship confidence/status changes require the applicable supported review
process and evidence; this guide creates no business decision or new approval queue.

For an authorised correction or replay:

1. Identify the exact dataset, record/field, accepted generation and current
   native revision. Coordinate with the existing object owner.
2. Retain original and current values, evidence and proposed change separately.
   An approved-correction claim needs explicit old/new values, rule/version and
   decision provenance; unresolved source disagreements remain pending.
3. Use the existing guarded operation. Preserve populated metadata, human notes,
   review states, version history, unrelated rows and complete raw snapshots.
4. Reconcile an uncertain write by its exact stable key and existing operation
   journal before resubmitting. A timeout is not evidence that nothing happened.
5. Verify saved native values and the affected consumer separately. Replay must
   not create duplicate identities or overwrite human edits; processing timestamps
   may change only where their existing writer contract explicitly permits it.
6. Recover only the scoped increment after comparing current state with its
   saved postimage. Never delete a whole list, overwrite newer edits or rekey
   publications as a shortcut.

The [dataset operating contract](SHAREPOINT_RETENTION.md#dataset-operating-contract--15-october-2026)
and [governance/usability guide](DATASET_GOVERNANCE_USABILITY.md) retain ownership,
versioning and recovery details. Hidden model tables, omitted contact columns and
filtered views are presentation choices, not access controls. Access, retention,
publication, schedule activation and production promotion keep their existing
separate authority boundaries.

### ROR complete release and monthly acquisition — 18 October 2026

The organisation reference source now retains the complete versioned official ROR
release before country/reference selection. The verified release has 144,717 unique
records, including 2,043 Australian organisations, with publisher MD5, saved-byte
readback and ZIP CRC checks. Raw originals retain inactive/withdrawn and foreign
organisation records; local reference selection and relationship confirmation are
separate capabilities. No existing people or affiliation decisions were changed.

The same collector is Started with monthly recurrence, concurrency one, Brisbane
timezone. Its first scheduler-generated run and an earlier unchanged-release replay
succeeded without another download or archive write. This establishes saved cadence
and the observed run; future monthly occurrences have not yet been observed.
The previous 32 typed organisation assertions remain historical bounded consumer
coverage and are not the size of the newly retained raw release. Other providers'
maintained acquisition scopes and cadence are recorded individually in the raw
acquisition section above; optional broader sources and downstream relationship
work retain their existing deferred boundaries.
