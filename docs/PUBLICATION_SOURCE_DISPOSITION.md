# Publication source differences — verified disposition, 24 October 2026

The retained147 field differences across140 registry records are accounted for
without overwriting any curated value. A fresh complete SharePoint read returned
1,651rows with no continuation; a separate list ItemCount read also returned1,651.
All147 compared fields still exactly match their retained curated audit values.
Exact item IDs, source identities, field pairs and native readbacks remain private.

| Disposition | Field differences | Meaning |
| --- | --- | --- |
| Title presentation equivalence | 2 | Bounded entity/formatting decoding gives exact literal equality; stored values remain unchanged. No substantive correction or author identity is inferred. |
| Bounded display with full source retained | 1 | Title is exactly the first255characters of the source title and SourceFullTitle exactly retains the full source. Fresh targeted readback retained the same Title/Modified values as the full capture. No missing-source-title defect remains for this pair. |
| Source/curation uncertainty retained | 144 | Different populated values, without qualifying correction provenance in the selected evidence. Keep both representations and label the distinction; do not automatically prefer the source or demand routine per-record approval. |

The144 comprise101affiliated-author strings,34raw dates,3publication months,
3date-precision values,2author lists and1facility value. These are field-pair
counts, not publication/person counts. No date, affiliation, employment or author
identity is invented. Unknown precision and original raw strings remain intact.

## Reconcile the historical counts

The original disposition retained147pairs/140records. The later v3case packet and
quality export contain145pairs/138records: their title field count is1 because the
two presentation-only title pairs were already omitted. That reduction was
classification, not registry correction. The remaining title is now verified as
bounded display with full source retention. The complete original147pair packet
was used here to ensure nothing disappeared from accounting. Historical147 and145
artifacts remain unchanged; neither should be presented as144unexplained defects.

## Correction and uncertainty contract

The existing private authoring checkout's `config/publication-policy.json`,
`config/publication-field-meanings.json` and `docs/PUBLICATION_AUTOMATION_POLICY.md`
require broad inclusion, retained observations/history, explicit uncertainty and
preservation of existing populated/curated values. A source mismatch is not an
approved correction. A correction claim needs exact old/new values, evidence,
rule/version and decision provenance. Free-text notes alone cannot establish it;
all140selected current records had blank ReviewNotes in this readback. No separate
structured correction ledger was supplied or inferred. This is a limit of selected
evidence, not a claim that no external correction evidence could exist.

The new `scripts/dispose_publication_source_differences.py` enforces complete current
capture/count, exact item/SourceKey pairing, retained source revision and exact
source values. Current curated drift, duplicate pairs, missing records or ambiguous
source pairing stop classification. It makes no network calls and never writes
registry values, source payloads, decisions or person identities. Only exact title
formatting or verified full-title retention can explain a title difference here;
fuzzy name equality is never used.

Its private result explicitly labels each remaining pair
`uncertain_source_difference_preserved`, includes both values and fingerprints,
and records `write_authorized=false` and `manual_record_approval_required=false`.
No title or semantic replacement is proposed. The sidecar labels are an evidence
disposition, not newly deployed SharePoint/model/export labels.

## Proof and remaining boundary

[Aggregate receipt](../config/publication-source-disposition-summary.json) contains
counts and observation time only. Full receipt:
`private/ops/2026-10-24-source-difference-disposition/disposition-result.json` in the
primary evidence checkout, beside full native readbacks and source fingerprints.
The source proposals belong to the named retained15October generation, not a new
24October source harvest. All147pairs were rebound to the original exact source
case packet and current registry SourceKeys; native rows remain untouched.

This closes current retained-pair accounting and policy disposition. It does not
adjudicate the truth of144semantic values, deploy new native uncertainty labels,
close all E07-H06 enrichment, or accept whole-system source/model/export parity.
Existing quality/readers must retain their dated-generation labels until an
owner-qualified refresh updates them. [Whole-system reconciliation](WHOLE_SYSTEM_RECONCILIATION.md)
should preserve these explicit differences rather than manufacture metadata equality.
Any future correction must bring its exact provenance and a fresh preimage before
an owner-controlled change; no automatic overwrite follows from this report.
