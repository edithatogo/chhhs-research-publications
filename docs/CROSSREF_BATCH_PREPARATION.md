# Crossref candidate preparation

These modules prepare cloud-flow definitions locally. They do not authenticate,
save, enable, cancel, resubmit or run a native flow. The deployed runtime remains
Power Automate. Keep native definitions, bindings and provider evidence private.

Run from the repository root with the explicitly selected repo-local Python
3.15.1 interpreter. Verify its actual version before preparation:

```sh
.venv/bin/python -c 'import sys; assert sys.version_info[:3] == (3, 15, 1); print(sys.version)'
.venv/bin/python -m scripts.prepare_crossref_lanes \
  --input /absolute/private/normal-native-readback.json \
  --expected-definition-sha256 REVIEWED_CANONICAL_DEFINITION_HASH \
  --output /absolute/private/paired-candidate.json
```

The fingerprint covers the complete definition using sorted-key compact JSON,
UTF-8 and unescaped Unicode. The input must be the normal collector with its
existing monthly created-date partition graph and sequential single-variable
initializers. It must not be a partial recovery graph or an already batched graph.
Preparation fails on drift or an unfamiliar archive contract.

## Selected changes

- Inline the full raw page envelope at save and equality verification, removing
  its extra Compose copy. Retain headers, request URL, status and provider body.
- Freeze a generation cutoff and resume only an accepted consecutive window
  prefix. Progress markers remain separate from accepted completion markers.
- Bound admission to 50 windows, 32 MB of archived bytes or 20 minutes. Finish an
  admitted window; these are soft budgets and do not guarantee a platform quota.
- Build the frozen window plan through per-query projections and ordinal checks.
- Keep the existing daily flow identity and trigger for incremental collection.
  Prepare a separate **Stopped** full reconciliation worker using the existing
  connection-reference map, with monthly partitions for the two large queries.
  Separate archive, progress and completion namespaces prevent the worker from
  advancing the daily watermark. Failure handling remains independent per lane.
- Pace worker pages using archived size. Historical volume informs this policy;
  actual platform metering and catch-up delay still require native measurement.

`scripts.measure_crossref_batches` consumes existing private receipts and saved
page proofs for historical tuning. It performs no provider or native requests.
Its timing and simulations do not establish the new candidate's throughput.

## Native acceptance remains required

Preserve an existing Running generation and its handle until it is terminal.
Reconcile the actual terminal result, complete partition content and coverage,
manifest, checkpoint and last-good before choosing continuation. Historical
prefix evidence needs extension for later completed partitions. Never reuse an
incomplete window's provider cursor or mix different frozen window plans.

At deployment, obtain a fresh exact preimage and rollback, refuse material drift,
use the supported same-identity update route and read back the complete saved
definition and preserved settings. The new worker needs canonical-purpose and
connection checks before creation. Local output and matching fingerprints prove
preparation only. Native expression/serialization parity, real batch continuation,
final coverage, manifest/checkpoint, replay and last-good preservation remain
separate runtime requirements. DOI batching remains conditional on measured
capacity in that phase.
