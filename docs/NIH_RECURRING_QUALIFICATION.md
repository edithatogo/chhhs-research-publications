# NIH recurring pipeline qualification — 24 October 2026

**End-to-end qualification is incomplete.** Recurring native acquisition and
archive retention are verified. Recurring register projection, scoped model
refresh integration and delivered failure alerts remain open. The standalone
qualification flow is Stopped; the existing reviewed-import flow is unchanged
and Off. No register/model writes or outgoing notification occurred.

## Native evidence

An exact-purpose inventory found no NIH collector. A disjoint
`CHHHS RIMS | Grants | NIH acquisition qualification` flow was created using the
existing owner SharePoint connection. Actual Recurrence runs and per-run response
processing both have concurrency one. The one-minute cadence was bounded test
configuration. Final saved settings contain a **disabled** daily 06:00 Brisbane
candidate with fault injection removed. This qualifier is outside the canonical
solution; it is not a promoted production component.

| Case | Native outcome | Independent evidence |
| --- | --- | --- |
| Initial JSON-only recurrence, two ticks | Both Succeeded | First generation's four files downloaded; byte equality to the manifest and maintained source-admission check passed |
| Initial post-archive injected failure | Failed | Failure receipt retained with four verified responses and no downstream/delivery claim |
| Attachment-capable recurrence, two ticks | Both Succeeded | Each generation's four JSON files and ZIP downloaded; exact manifest bytes, JSON values, semantic replay, ZIP CRC/member identity/sizes passed |
| Attachment-capable post-archive injected failure | Failed | Failure receipt retained; failing run did not promote a complete acquisition manifest; prior generations preserved |
| Scheduled recovery after fault removal | Succeeded | Native archive and manifest verification actions succeeded without replacing earlier generations |

Successful generations have unique `nih-acquisition-<run>` folders in the existing
source archive. Failures use `nih-acquisition-failed-<run>.json`. No other lane's
flow or files were changed. Complete before/after register reads and isolated-model
refresh history are unchanged. All 37 model definition parts match the prior
accepted definition exactly.

Acquisition makes the documented POST search/detail requests twice each for exact
FON PA-25-301 / opportunity 357812 and all four source statuses. Native guards check
response success, selected identity, one search page, posted/non-draft status and
matching attachment metadata. The stronger maintained semantic replay/admission
check is independently executed offline; it is not yet a recurring native
projection/admission boundary.

## Representation and attachments

Power Automate decodes the API JSON. Archives retain the **complete native-decoded
response serialized to UTF-8**, including unmapped properties, history and file
metadata. They do not prove preservation of provider wire whitespace, numeric
lexemes or transport headers. Independent download comparison proves the exact
bytes of the saved representation.

The attachment route was observed on the official opportunity's Related Documents
page. The flow downloads every current synopsis folder ZIP through that first-party
route and verifies binary SharePoint readback. Current/replay folder metadata must
match; unexpected counts or oversized folders fail closed. This observation has
one **445-byte ZIP** containing one **420-byte HTML attachment**. Independent ZIP
CRC, filename, declared sizes and hashes pass. The attachment is retained as supplied;
it does not substitute for independently reacquiring and qualifying the larger
NIH NOFO/schedule page.

- `scripts/prepare_nih_acquisition_flow.py` builds the native definition locally.
  Short cadence and injected faults are explicit options; default cadence is daily.
  The builder performs no network, register/model mutation or message delivery.
- `scripts/verify_nih_acquisition_archive.py` verifies downloaded manifest, all four
  response files, source consistency and every declared ZIP member offline. Missing,
  changed or contradictory evidence and false downstream claims are rejected.

Final native/source equality excludes only the service's known parameter-based
authentication annotation and redundant evaluatedRecurrence copy. Physical
SharePoint connection identity is preserved.

## Remaining dependencies and supported choices

| Dependency | Evidence / limitation | Recommendation | Contingency |
| --- | --- | --- | --- |
| Recurring projection and register commit | Maintained normalization, semantic replay, evidence-hash and pinned schedule checks remain local. Existing importer lacks atomic ETag protection | Port the admitted projection/provenance contract to a supported native processing step; commit after verified retention using conditional versions, preserving review fields | Retain generations and continue the explicitly operator-run admission/import route; do not label it unattended |
| Scoped isolated-model refresh | Existing Power BI connector exposes only workspace/dataset IDs for RefreshDataset, without objects/transactional options or refresh-history operation. Prior acceptance refreshed exactly two grants partitions via enhanced API | Qualify durable cloud authentication for enhanced refresh; retain the two-partition transactional request ID and poll that same operation to terminal state, then reconcile DAX | A separately approved grants-only isolated model could use the standard connector, after creation/binding qualification. Do not refresh unrelated publication partitions or paste short-lived CLI bearer tokens into flows |
| Failure alert delivery | Owner failure subscription is true; general failures need not produce per-run email, and per-run alerts have a 28-day cooldown. Receipt persistence is verified; notification delivery is not | Add a catch path with an explicit owner-only destination and minimal source/run/stage/error/receipt-link payload; verify one delivered failure and duplicate suppression | Native run history, retained receipts and weekly digests remain diagnostic routes; they are not immediate push-delivery proof |
| End-to-end acceptance and promotion | No automatically correlated register commit and completed model refresh exists for these generations | After dependencies: two actual scheduled full cycles; changed-source/partial-failure cases; exact register/model fields, keys and occurrences; review/last-good preservation; terminal refresh and delivered-alert proof; then canonical solution/export reconciliation | Keep the qualifier Off and preserve existing native objects |

No new consent, connection, licence, capacity, recipient or stored credential was
introduced to bypass these boundaries. Manifests explicitly retain accepted=false,
register_updated=false, model_refreshed=false and end_to_end_qualified=false.

## Sources and private receipts

- [Grants.gov search](https://www.grants.gov/api/common/search2),
  [detail contract](https://www.grants.gov/api/common/fetchopportunity) and
  [official opportunity/documents](https://www.grants.gov/search-results-detail/357812).
- [Power BI connector refresh parameters](https://learn.microsoft.com/en-us/connectors/powerbi/#refresh-a-dataset)
  and [enhanced refresh](https://learn.microsoft.com/en-us/power-bi/connect-data/asynchronous-refresh).
- [Microsoft failure-notification exclusions and cooldown](https://learn.microsoft.com/en-us/power-automate/understand-flow-failure-notifications).
- [Prior isolated-model acceptance](GRANTS_MODEL_REFRESH_ACCEPTANCE.md) and
  [concurrent import/edit tests](GRANTS_CONCURRENCY_ACCEPTANCE.md).

Exact native identity, definitions, runs/actions, fault receipts, archived files,
hashes, settings and preservation evidence remain ignored under
`private/ops/2026-10-24-nih-recurring/`.

## Further scheduled freshness and partial-archive recovery observation

Three additional **actual one-minute Recurrence ticks** were observed on 24 October
2026. Native trigger receipts include scheduledTime and originHistoryName matching
each current run. No manual invocation or resubmission counted as a scheduled tick.

| Brisbane start | Outcome | Verified behavior |
| --- | --- | --- |
| 12:31:33 | Succeeded in 13.6 seconds | Four new HTTP actions, complete response/ZIP archive, manifest and independent source/ZIP parity |
| 12:32:33 | Controlled failure in 8.8 seconds | Deliberate guard failure before attachment acquisition; scope and four responses retained, no ZIP or complete manifest; failure receipt retained |
| 12:33:33 | Succeeded in 12.6 seconds | Next scheduled tick after fault removal reacquired all responses and ZIP into a different complete generation; independent parity passed |

For both successes, all four provider HTTP Date headers fell inside the native run
window with a 30-second clock tolerance, and each actual HTTP body matched its
archived response object. Observed UTC lay inside its correlated run. At independent
verification the observation ages were **103.84 seconds** and **54.22 seconds**,
within the selected five-minute test bound. This is point-in-time source-observation
freshness, not an agreed production SLA or a claim that the source record changed.
The provider's separate last-updated text remains **Jun 02, 2026 10:48:02 AM EDT**;
it was not replaced with acquisition time or silently converted to another zone.

The new read-only helper `scripts/verify_nih_observation_freshness.py` checks the
native scheduled trigger, correlated manifest, four non-truncated action receipts,
provider clocks and exact HTTP-body/archive parity. Tests reject stale/future
observations, resubmissions, incomplete receipts, stale/missing provider dates and
changed archived bodies. It makes no register/model freshness claim.

Earlier complete and failed-partial generations retain their exact file IDs,
ETags, lengths and modification times after recovery. Complete register reads and
isolated-model refresh history match their pre-test baselines. The flow's exact
pre-test definition, connection references, disabled daily candidate and Off state
were restored and read back; the deliberate fault is absent. No new source scope,
accepted register record, model refresh or outgoing alert was introduced.

This bounded short-cadence test does not establish daily or multi-day operational
reliability, missed-trigger detection, sustained freshness, alert delivery or full
source-to-model acceptance. Those existing gates remain open. Private native HTTP
receipts, full downloaded generations, freshness proofs and preservation evidence
are under `private/ops/2026-10-24-nih-scheduled-observation/`.


## Reviewed-import original retention — 24 October 2026

The separate [original-retention increment](GRANTS_ORIGINAL_RETENTION.md) now
retains four complete JSON bodies and the declared ZIP without direct operator
attachment uploads, and verifies exact saved bytes. It preserves the existing
Invoker reference map, accepted parent/review fields and prior attachments;
incomplete/conflicting inputs and a missing parent fail closed. Both grants
flows remain Off with native owner failure-email subscriptions false. Producer
admission/envelope inputs remain separate from unattended orchestration; this
increment does not close the remaining recurring register/model or delivery gates.
