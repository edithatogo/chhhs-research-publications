# Web-first work-package validation

Release scope: **Conductor implementation tracks and local execution helpers**, not a verified live Power BI report or a newly built PBIX.

## Source and route

- Baseline: `v0.3.0-rc1`, commit `92c1d0e0ddfe5ee3400b054d50ad3abeb11a8665`.
- Original archive SHA256: `4541c6429e9fa0c684082ccf0bb51b87d0e288b12111265b2c426e8bc2371f60`.
- Branch: `implementation/webui-first-v040`.
- Ordinary Power BI plugin/web UI is the preferred implementation route. Fabric Git/capacity is not a prerequisite.
- The exact Power BI editing plugin was not exposed in the originating chat after two directory searches. This does not establish a limitation in the user's other plugin-enabled session.
- Remote Desktop Commander returned zero connected devices. No user machine or VM was changed.
- Existing Git history and the upstream Conductor gitlink are preserved. The upstream checkout is not populated; the local Conductor context, tracks and handoff are present.

## Executed local checks

| Check | Result |
|---|---|
| Unit/regression tests | 110 passed: 54 existing plus 56 new |
| Original source-definition checks | 212 passed |
| New track/contract/baseline checks | 93 passed |
| Blank capability manifest | Correctly rejected as unverified, no automatic fallback |
| Blank native evidence template | Correctly rejected |
| Full synthetic register rendering | Six records in CSV and flowing HTML, with identity/count/hash receipt |
| Existing output destination | Protected by refusal-to-overwrite tests |
| Host diagnostic shell syntax | Passed `bash -n`; not run on the user's Mac |
| Python compilation | Passed for both new helper modules |
| Windows diagnostic | Prepared only; not executed or natively validated |

## Evidence boundaries

The policy helpers inspect declared capabilities, isolated-target IDs, source-definition hashes, artifact hashes, run correlation and full-export identities. They do not control a plugin or VM, authenticate a purported service receipt, or establish the completeness of a live source harvest. An authorised reviewer must compare native evidence with the actual service.

The bibliography exporter accepts canonical JSON. It does not retrieve Power BI data, call PubMed, or create a PDF. Its demonstration is visibly synthetic; it contains no publication text from the supplied historical DORA XML. For live use, expected counts and key sets must come independently from the same successful native refresh/filter context, not from the possibly truncated export being tested.

The authored M/DAX/PBIR baseline remains unchanged. Known runtime defects, including zero-PubMed handling, weak title/year matching and uncertain DORA dates, remain open in T11/T12. Passing source-policy tests does not repair those defects or certify native execution.

## Track disposition

T09 is the local work-package track. T08 remains blocked on actual plugin/item discovery. T10–T15 are planned live implementation tracks. T16/T17 remain conditional and require a demonstrated web-authoring incompatibility and owner approval; absence of a plugin here is not a fallback trigger.

## Release verification

A fresh extraction is tested independently and checked for a clean Git tree and Git integrity. The standalone release receipt records final commit/tag, archive/bundle hashes and the fresh-extraction results. No Power BI, tenant, scheduling, mail, production sharing or VM action is represented as performed.

## Evidence files

- `webfirst-unittest-output.txt`
- `webfirst-baseline-validation.txt`
- `webfirst-policy-validation.json`
- `../examples/webfirst-synthetic-export/manifest.json`
- `../config/web-first-session-observation.json`
- external release receipt supplied alongside the work package
