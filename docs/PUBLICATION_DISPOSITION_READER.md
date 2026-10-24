# Verified source-difference reader — 24 October 2026

The existing SharePoint **Source differences | Verified disposition** view now
shows **144 uncertain semantic pairs and 3 explained title differences**, covering
147 field pairs across 140 records. Two title pairs are presentation equivalents;
one is a bounded display whose full source title remains retained. The semantic
pairs remain explicitly uncertain, with both representations available.

The view links to new, immutable CSV and JSON disposition outputs, plus the
unchanged historical 15 October CSV/JSON. Source proposals still belong to the
retained 15 October generation; paired registry values were verified on 24 October.
This is not a new harvest, correction, or author-identity decision.

## Implementation and recovery

`scripts/prepare_disposition_reader.py` prepares four create-only files and a patch
for the existing view. It rejects current value/SourceKey drift, duplicate or
missing pairs, unknown categories, and unsupported full-title retention claims.
The CSV retains both values and a no-correction statement. The prior complete view
definition and file hashes are saved with the new outputs before the view changes.

Only the existing view's title, query and formatter changed. Identity, URL,
default status, fields, paging and row limit are retained. The query covers all
140 original records, restoring the two previously omitted presentation cases.
Row badges use the existing loaded SourceKey field; a native filtered-row check
caught and corrected an initial numeric-ID comparison that did not render them.
No publication, field schema, model, flow, schedule, sharing or permission changed.

Recovery uses the saved prior definition to restore those three view properties;
new dated files can remain as history. Do not overwrite or delete historical
outputs. Re-read current state before any future owner-controlled update.

## Accepted evidence

Private evidence is retained under
`private/ops/2026-10-24-reader-disposition/` in the primary evidence checkout:

- Complete pre/post captures: all 1,651 rows and 143 fields exactly unchanged;
  seven other views and the list count unchanged.
- Existing reporting-file identities, versions, modification times and lengths
  unchanged; the three historical quality-file byte hashes also match.
- Four new files created with overwrite disabled and exact native byte readback.
- Existing view identity/URL and saved formatter/query verified; query accounts
  for all 140 expected registry identities.
- Browser-rendered totals, preservation language, historical links, and filtered
  title classifications checked. Browser reads of both new and both historical
  linked outputs returned HTTP 200 and exact expected byte hashes.

The Lists client initially displayed a cached view. Opening the same native view
with explicit `viewid` and `env=WebViewList` rendered the current saved definition;
no cache/auth reset was needed. The browser download helper timed out, so linked
bytes were verified through same-origin browser reads and native file readback.
Do not report a completed filesystem browser download.

The original disposition receipt remains immutable: its statement that labels
were not yet deployed describes that earlier capture. This subsequent view-only
acceptance exposes the accounting without asserting native field/model/export
labels or semantic adjudication. See [the disposition contract](PUBLICATION_SOURCE_DISPOSITION.md)
and [whole-system reconciliation](WHOLE_SYSTEM_RECONCILIATION.md).
