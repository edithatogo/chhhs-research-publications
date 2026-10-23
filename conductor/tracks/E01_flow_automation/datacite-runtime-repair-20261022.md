# DataCite pacing and rejected-response retention — 22 October 2026

The actual latest scheduled acquisition failed because Consumption rejected its
one-second Wait: this SKU requires at least five seconds. The precise failed
repetition remains retained. The source compiler and same native collector now
use five seconds, preserving all source scope, window/count/identity/cursor guards,
bindings, weekly recurrence and Started state.

A second concrete gap was corrected: validation formerly preceded raw storage,
so a failed HTTP response could disappear before archival. Raw capture now runs
after Succeeded, Failed or TimedOut HTTP outcomes. Save/readback/exact-byte
verification precedes the unchanged strict page guard. IDs, totals, cursor/page
advancement and successful manifests remain downstream of validation. Raw evidence
now explicitly retains request outcome and transport error without inventing an
HTTP response. A retained rejected page is never an accepted generation.

Three focused tests with expanded preservation/dependency/drift checks and the
full 2,248-test suite pass (eight skipped). The exact same-ID normal graph saved
and matched native readback before bounded qualification.

The isolated manual qualification made two actual provider requests from existing
source inputs: one institutional query with page size one, and one retained
publication DOI. DataCite returned HTTP 200 and HTTP 404 respectively. Both raw
files saved/read back exactly before the original guard accepted the first and
rejected the second. Both configured five-second Wait repetitions Succeeded
(actual durations about 5.08 seconds). The qualification-outcomes guard Succeeded;
the run ended Failed only at its explicit qualification hold. No successful
manifest, accepted marker, registry record or source-model processing was written.
Its archive uses a separate qualification prefix, outside accepted discovery.

Independent SharePoint HTTP 200 reads verify all 2,526 and 1,332 stored bytes,
SHA-256 and exact equality with both native runtime raw-page outputs. The latest
accepted 259,884-byte marker equals its earlier successful native manifest exactly.
The collector was restored to the repaired normal weekly definition, original
bindings and Started state, with exact readback and no active run.

Private evidence under `private/ops/2026-10-21-e01-runtime-qualification/`:

- `datacite-failed-delay-repetitions.json`
- `datacite-runtime-repair-preimage.json` (exact rollback)
- `datacite-runtime-repair-save-saved.json`
- `datacite-runtime-qualification-terminal.json`
- `datacite-runtime-qualification-actions.json`
- `datacite-runtime-independent-byte-bundle.json`
- `datacite-prior-accepted-native-manifest.json`
- `datacite-runtime-normal-restore-saved.json`
- `datacite-runtime-repair-acceptance.json`
- `datacite-runtime-repair-integration.log`

This closes the affected native repair, not a full-scope catch-up or a later
healthy natural occurrence. The observed natural failure and later occurrence
remain E08-F03; no calendar wait or extra activation is an E01 completion gate.
Provider-specific continuation and broader source-health work remain separately
open. Restore/export package coverage must use the actual current published graph;
a saved source candidate alone cannot establish that coverage.
