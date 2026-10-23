# Crossref institutional discovery and DOI reconciliation

The same existing Crossref collector now has a complete-scope candidate saved
and read back. Native baseline qualification is in progress; this document does
not claim that the baseline or daily updates have passed.

`config/crossref-acquisition-hedge.json` is the maintained, editable search input.
Its 27 distinctive anchors collectively cover every quoted affiliation alias in
the existing PubMed hedge. The builder rejects dropped alias coverage, invalid
anchors and ambiguous duplicate query keys. Editing either hedge changes the
scope fingerprint and forces a new baseline on the next qualified deployment.
Keep the source JSON and exact native saved graph reconciled when changing it.

Crossref's `query.affiliation` is broad candidate retrieval. A native read-only
size probe found that quoted `Cairns Hospital` returned about 3.54 million results,
while `Cairns` returned about 4,000. The collector therefore queries a distinctive
token from each alias separately, rather than common Hospital/Health words.
Generic geographic anchors and Tropical deliberately retain false positives;
there is no pre-retention institutional selection. Complete query results are
not proof of complete institutional publication coverage because contributor
affiliations are optional in Crossref metadata.

The Microsoft flow retains every full response page, request URI, headers and
status in a unique run folder, with saved-content equality checks. Each query
uses cursor paging and 500 records per page. Full baselines use a stable
created-date cutoff; incremental updates use bounded index-date windows. Terminal
page, stable provider total, received count and unique DOI count must reconcile
before its completion summary. A page/timeout guard fails instead of claiming
truncated results are complete. Query overlaps are expected and retained.

DOI reconciliation complements discovery. The exact accepted Publication
Registry is read with pagination and its native item count is checked before
using the DOI fields. Original seed DOI lookups are preserved. Relevant raw DOI
fields and invalid non-empty values are retained; the collector does not repair
registry fields or make affiliation/business decisions. Every requested Crossref
DOI response, including a qualified 404, is archived and checked.

Completion is committed last in a new immutable marker. Failed runs cannot
advance the last successful cutoff or overwrite a previous archive. Subsequent
runs use a seven-day index overlap; a scope change or 28 days since the previous
baseline forces full reconciliation. A daily native trigger is still pending
until the complete baseline, catch-up and actual scheduler execution pass.

Private exact targets, preimage, restore packet, saved graph and active run
checkpoint are under `private/ops/2026-10-18-crossref-broad-acquisition/`.
Preserve the active handle; do not restart merely because observation times out.
Shared consumer/model/report and solution membership remain with their owners.

Primary references:

- [Crossref API queries and cursors](https://github.com/Crossref/rest-api-doc)
- [Crossref paging and bounded index windows](https://www.crossref.org/documentation/retrieve-metadata/rest-api/tips-for-using-the-crossref-rest-api/)

The first native baseline was explicitly cancelled after its first page returned
HTTP 400: Crossref accepts UTC date-times without a trailing Z in index filters.
A bounded corrected-date probe passed. The Until loop initially repeated failed
requests; it now sets a failure flag, exits paging and skips subsequent source
requests. Query and final completion gates require the flag to remain clear.
No completion marker advanced. DOI seeds are case-normalised/deduplicated and
raw DOI files use an indexed filename with an explicit manifest mapping.

The daily trigger preparation is now implemented in `with_daily_updates`: 03:30
Australia/Brisbane, concurrency one, preserving the complete acquisition graph
and connection bindings. A local preparation check passed against the accepted
Stopped preimage. This trigger is not applied while the baseline is running;
actual scheduler and checkpoint catch-up qualification remain pending.

The existing Microsoft 365 CLI can observe both the run and its nested page
repetitions through the qualified ProcessSimple route. FlowAgent's later Azure
sign-out does not invalidate these native receipts or justify restarting the run.
Shared authentication recovery remains with its assigned owner.

A later run stopped correctly when the provider total changed from 114,752 to
114,751 during the Tropical query. Its 35 saved pages remain preserved, and no
completion marker advanced. Crossref's August 2026 cursor upgrade explicitly
permits changing result sets when records are reindexed. The baseline now uses
the recommended stable creation-date boundary instead of a moving index-date
boundary. Strict count and unique-DOI reconciliation remain in place. The
baseline's initial cutoff remains the update checkpoint so subsequent overlap
retrieves new and changed records during the long baseline capture.

- [Crossref cursor changes and stable-date guidance](https://community.crossref.org/t/changes-to-cursors-filtering-and-sorting-in-the-rest-api/16246)

The stable baseline completed all 27 hedge queries and 499 saved pages, then
failed on DOI lookup 269 with an official 301 alias redirect. The failed run and
all raw files are preserved. The redirect-aware collector retains the initial
response, permits one HTTPS redirect within Crossref’s `/works/` API, and checks
the returned metadata DOI against that canonical target while retaining the
original identifier. Further redirects and unqualified targets fail closed.

A temporary same-ID native recovery now reuses all 27 completed query archives
and the consecutive 268 verified DOI responses through explicit archive-folder
references. It preserves the original cutoff, checks the current DOI input set
for exact drift, writes remaining responses into a new recovery folder and
commits completion only after reconciliation. Saved graph/bindings and the first
recovered alias’s original/redirect/final payloads passed native readback. This
is not terminal recovery or full-source acceptance. Restore the normal
redirect-aware graph before catch-up or daily activation; the temporary recovery
graph explicitly refuses scheduling. Private receipts are `recovery-save/acceptance.json`,
`verified-recovery-inputs.json` and `native-alias-acceptance.json` in the existing
Crossref acquisition directory.
