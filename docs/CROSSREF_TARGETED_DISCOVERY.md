# Targeted Crossref discovery — 24 October 2026

The user selected targeted institutional discovery plus accepted-source DOI reuse.
This replaces the former requirement to retrieve a candidate superset using a
standalone word for every PubMed affiliation alias. It does not change PubMed's
searches or claim an exhaustive institutional publication census.

## Search policy and measured evidence

The versioned policy is `config/crossref-acquisition-hedge.json` schema2. Its
alias map assigns every maintained alias to discovery or DOI evidence with an
explicit independent-discovery gap. The acquisition list contains19 queries;
Tropical, Cow, Mission, Edmonton, Georgetown, Smithfield, Croydon and Liz are
excluded. Their aliases remain available for matching and provenance.

Independent reads of330 archived pages in the verified251-window prefix retained
all native byte hashes. Comparison against accepted PubMed/DoRA DOI inputs found:

| Query | Records | Explicit institutional alias matches | Useful DOIs unique to this query after other queries/accepted inputs |
| --- | ---: | ---: | ---: |
| Cairns | 4,014 | 844 | 194 |
| CHHHS | 3 | 3 | 0 |
| Liz | 171 | 22 | 0 |
| Tropical | 80,698 | 49 | 0 |

Tropical accounts for1,103,211,652 retained bytes in this prefix. Unmatched
records are unresolved, not proof of irrelevance; these are prefix findings,
not final whole-generation precision or clinical/institutional adjudication.
All explicit matches, including those from disabled queries, enter the prepared
DOI queue with original archive identity, ETag, byte hash and alias evidence.
The queue contains1,501DOIs: every1,283 previously reconciled DOI plus218more.
Successful immutable DOI responses are separately byte verified for bootstrap
cache reuse; non-200 archives remain evidence and are not treated as fresh work
metadata. One existing DoRA value is a title rather than a DOI; it is retained as an input
exception, not converted or silently dropped.

Seventeen bounded count-only provider requests, plus the two already archived
complete query counts, total5,000hits across the19enabled queries at the same
frozen cutoff. Counts overlap and are not5,000unique institutional publications.
They measure volume, not attribution or runtime. A separate20-record Plummer
sample had no maintained-alias matches out of204total hits; it remains disabled.
No provider recollection was used for the archived-prefix analysis.

## Collection and continuation

`scripts/prepare_crossref_targeted.py` prepares two local cloud-flow definitions:
existing daily incremental identity and separate Stopped baseline worker. Its
exact historical preimage fingerprint is mandatory. It retains daily timing,
seven-day overlap, ten-minute snapshot lag, existing connections and concurrency1.
The new full plan has19query windows and uses page-level yielding rather than
creating hundreds of mostly empty calendar partitions. It is generated from
the enabled query list. The new shared acquisition scope hash is distinct from the retained original
generation. The two lanes use the same targeted acquisition policy but separate
mode, storage and progress guards; execution pacing is not acquisition scope. A scope change never adopts an old accepted marker
as evidence that the new generation is complete.

Admission is checked after each verified page:50pages,32MB decoded-byte upper
bound,20minutes, or the existing50-window bound. The crossing response is retained
and read back before yielding. Progress schema2 stores an unaccepted partial
window, original folder, cursor, counters, page metadata and frozen request bounds.
Only a genuinely accepted complete window enters query completion. A resumed
partial window retains its original folder and verifies page IDs/ETags/lengths;
its existing scope bytes are checked before further acquisition.

Crossref's newer cursor implementation is documented as non-expiring with fixed
request parameters, while Swagger retains older five-minute wording. The new
compiler does not reset a cursor solely because time elapsed. Actual rejection,
total drift, duplicate/missing DOI totals or parameter mismatch fails closed and
requires evidenced unfinished-window recovery; completed windows are preserved.
See [current cursor guidance](https://community.crossref.org/t/changes-to-cursors-filtering-and-sorting-in-the-rest-api/16246)
and [API documentation](https://api.crossref.org/).

The DOI cache is indexed once using a Select projection and keyed object lookup;
there is no per-DOI Filter array copying the full cache into history. Successful
bootstrap cache coverage is1,279DOIs, leaving222planned fetches (including4prior
404responses). Freshness and incremental-change checks still decide actual reuse.
Native SharePoint read/action capacity remains a runtime measurement gate.

The full-payload Compose copy is removed; new raw envelopes still receive one
write and exact content readback. Native DOI cache reuse requires a fresh accepted
entry, preserved original file pointer, native ID/ETag/length before and after
read, and matching requested/canonical DOI. Responses older than28days or lacking
these fields are misses. DOIs seen in an incremental discovery page force refresh,
even when the cache entry is younger. Reused timestamps are never reset. This
uses native version guards, not a claim that Power Automate computes SHA256.
Independent byte hashes remain acceptance evidence.

Publication producer provenance remains in the manifest. Only verified relevant
discoveries enter the extra prepared DOI input; citing/cited works are never
recursively expanded. New unmatched discovery responses remain archived candidate
evidence. Updating that prepared discovery queue requires the same explicit alias
audit; it does not automatically adjudicate institutional membership.

## Migration and remaining native proof

The original generation and monitor remain active. Do not deploy the replacement,
rename scope, cancel/duplicate a run or discard completed partitions to accelerate
migration. Reconcile its actual terminal result under the original scope first.
The original recovery package is not rewritten by this policy.

The local create-only bootstrap bundle stages a new Scope and two summary
overlays for the compatible original Cairns/CHHHS windows. It keeps all original
raw files in place and pins their IDs, ETags, hashes and original scope. Its
unaccepted progress fixes the original cutoff; the17unresolved queries are
acquired against that same cutoff before daily catch-up. No support files or
progress have been uploaded. Native prefix reuse checks both the saved overlay
bytes and every original page version.

New-scope bootstrap must use independently verified archive coverage and a new
scope-specific manifest; old raw IDs/ETags/hashes and all accepted publication
relationships remain reachable. The baseline worker never writes the daily
watermark. The primary requires an accepted checkpoint for its exact new scope. Its new
bootstrap branch reads a complete baseline marker, verifies exact scope/mode/
cutoff, writes and reads back a separate primary-owned bootstrap marker, and
pins subsequent progress to that new marker. It accepts no partial baseline.
This branch still requires native runtime qualification. The older599-window
worker has a different scope and cannot seed it. An unaccepted input packet is not a
bootstrap checkpoint or a deployable receipt.

Before native execution: preserve fresh preimages, reconcile current connection
reference encoding, use the qualified PAC/Dataverse save route, and independently
read back both full definitions/settings. Prove two actual batches including
partial-window resume, zero completed-window recollection, immutable archive
reuse, final coverage/manifest/checkpoint/replay, and daily/baseline isolation.
Native diagrams must describe the saved graph; update them after adoption rather
than presenting this candidate as already deployed.

Measure provider time, storage/readback time, action/history volume and catch-up
lag. Daily completion within1hour and roughly20-minute reconciliation batches
are targets. Admission cannot interrupt an in-flight request or force platform
throttling to end. Shared daily capacity and sustained speed remain unmeasured.
If the reduced workload still exceeds capacity, record the actual deficit before
selecting a separate bulk-worker execution environment. No additional parallelism,
schedules, licences, connections or runtime migration are implied by this source
implementation.

Private evidence is under `private/ops/2026-10-24-crossref-targeted/` in the primary
checkout. Source checks establish local behavior only. E01 remains incomplete
until original terminal reconciliation and revised native acceptance pass.
