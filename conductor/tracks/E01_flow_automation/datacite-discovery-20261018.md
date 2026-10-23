# DataCite institutional and related-dataset acquisition

The user selected institutional hedge and related datasets, rather than every
Australian-provider record. Policy revision v2 records that decision. The new
same-ID definition is saved natively with exact graph and binding readback; it
was enabled after readback and its first baseline completed successfully.
Independent baseline and checkpoint catch-up qualification passed. The same
flow is now Started on a Thursday 05:00 Australia/Brisbane weekly recurrence;
its first weekly execution has not yet been observed.

`prepare_datacite_discovery_collection.py` derives every quoted institutional
affiliation alias from the maintained PubMed hedge. It searches both creators
and contributors, in bounded query shards. Unmapped unquoted affiliation terms
fail preparation instead of silently disappearing from the hedge.

Related-identifier queries cover the qualified publication DOI input, retained
previously acquired DOIs and historical seeds. They use batches of 20 DOI phrases
joined with OR, preserving coverage without one HTTP request per DOI. Source
fields, invalid non-empty values, population kind and the exact query list are
retained. No registry field is repaired and no downstream selection is applied.

The qualified DOI input is the existing Publication Registry. All direct DOI
identifiers in the accepted 1,274-record PubMed generation and the unchanged
historical 709-record DoRA collection reconcile to this input. Additional
unaccepted raw extensions remain unproved; registry coverage alone does not
establish a wider source population.

Every page requests `detail=true`, `affiliation=true` and `publisher=true`.
Complete responses retain XML, schema/source versions, identifiers, affiliations,
publisher details and other public metadata. Cursor tokens are extracted from
the provider's same-host next link and reused with the unchanged query/options.
The 10,000-record limit of numbered paging is therefore avoided.

Saved-content equality, terminal cursor, provider total, received count and
unique identifiers gate completion. Failed requests stop paging and subsequent
queries; completion is committed last in a new immutable marker. Earlier
archives remain available. Baselines use a creation-date cutoff. Institutional
updates use overlapping update-date windows with periodic full reconciliation;
related queries run in full each time so a newly acquired publication DOI can
discover an older dataset. Previously acquired DOI inputs are retained.

The weekly trigger constructor prepares Thursday 05:00 Australia/Brisbane with
concurrency one. Baseline and catch-up have passed; the exact weekly graph,
bindings and Started state are saved/read back. First weekly execution remains
unobserved, so scheduled output acceptance is not inferred.

Focused local checks and offline Power Automate definition validation pass.
A bounded public API qualification retrieved both pages of a two-record query,
with distinct identifiers and XML metadata. This proves request/cursor behaviour,
not acquisition of the entire selected source scope. After qualified access
recovered, fresh same-ID drift verification passed and the definition was saved
to the existing flow. Exact saved graph, binding identities and Stopped state
were read back. The later accepted 1,274-record PubMed generation was reconstructed from all
40 retained metadata pages with receipt hash/size and key/chunk checks. All 1,229
direct publication DOIs occur in the qualified register. The accepted manifest
preserves DoRA unchanged; its historical 709-record collection also reconciles.
Cited-reference DOIs are excluded. This accepts related-query inputs for the
currently accepted generations; `raw_extensions_accepted=false` remains explicit.
After enable/readback, exactly one guarded invocation was journalled and the new
Running handle reconciled. That invocation receipt alone does not establish
terminal acquisition, catch-up, schedule execution or additional raw-extension
completeness. Subsequent acceptance is recorded below. Exact candidate,
scope and API receipts remain in the ignored DataCite acquisition directory.

- [DataCite query syntax](https://support.datacite.org/docs/queries)
- [Full metadata options](https://support.datacite.org/docs/api-queries)
- [Cursor pagination](https://support.datacite.org/docs/pagination)

The first native baseline is verified against all 156 downloaded files: 76 queries,
817 raw rows including query overlap, and 709 distinct DataCite DOIs. Completion
marker, manifest, frozen scope, source input snapshot, every saved query receipt,
response page, cursor, total, unique identifier and XML payload presence reconcile.
This accepts the selected baseline against currently accepted publication inputs;
it does not accept replay/catch-up, weekly operation or unselected raw extensions.
Private receipt: `2026-10-18-datacite-broad-acquisition/native-full-archive-verification.json`.

The unchanged acquisition graph completed a checkpoint catch-up with 76 native
query guards and 739 raw rows including overlap. Saved marker/manifest, exact
seven-day institutional windows, full related queries, retained publication
DOIs and the unchanged baseline marker passed readback. This reuses the initial
full archive qualification and independently reads the changed window samples;
it does not repeat every unchanged baseline check. Receipt: `catchup-native-qualification.json`.

The first recurrence save was rejected because automated flows limit the
GetItems pagination threshold to 5,000. The scheduled constructors now use that
supported setting while retaining both strict boundary and exact native
ItemCount guards. The current input has 1,648 rows and is fully covered. An input
that reaches the boundary fails explicitly; no truncated scope is accepted.
Saved graph/bindings and Started weekly state passed after this correction.
Receipt: `weekly-activation-acceptance.json`. First natural weekly output remains
unobserved. Neither a new billing/access grant nor downstream model use is implied.
