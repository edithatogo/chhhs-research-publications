# Execution evidence

## S02.1–S02.2 local implementation

- Replaced the unsafe packager that embedded `.git` and created an all-history bundle.
- Added explicit software, schema and batch identities, source commit, dirty-build and native-acceptance fields.
- Source archives exclude private runtime paths, canonical live downloads, ZIP/bundle files and the release manifest itself.
- Archive paths are sorted and the fresh extraction verifies the manifest, absence of Git/private runtime and local validation/tests.
- Added `tests/test_package_release.py`; focused result: 3 tests passed.
- Review fix: ZIP members now use a fixed timestamp and the focused result is 4 tests passed, including byte-stable member output.

The current checkout is intentionally dirty, so the package command refuses to create a reproducible release. This is a safety gate, not a packaging failure. S02.2.3 and S02.2.4 were verified against a separate clean candidate; native recovery/versioning evidence remains open.

## S02.2.3–S02.3.3 local evidence

- Clean candidate `/tmp/chhhs-source-candidate-release.g0VSzp` was bootstrapped
  with Conductor `6e8f9a860bcdd6a2c423473c12e745200688c633`.
- Earlier candidate checks were `validate_project.py` 319/319 and unit tests 258/258; the current canonical clone now passes 319/319 and 280 tests.
- `scripts/package_release.py --version 0.3.0-rc1` passed fresh extraction,
  manifest equality, no Git/private runtime content and source tests. The
  receipt records `NativeAcceptance=false`; it is not a live export.
- `docs/VERSIONING_ARCHITECTURE.md` now distinguishes local source receipts
  from conditional native SharePoint/Power Automate/Power BI versioning and
  documents the one-owner release routine.

## S02.3.0 tooling decision

- Local read-only preflight: `pac 2.12.2`, Azure CLI with Azure DevOps extension,
  PowerShell 7.6.6 and GitHub CLI 2.101.0 detected; no solution project was
  found. Result: `PASS_LOCAL_ONLY`.
- Build Tools 2.0 and `microsoft/powerplatform-actions` are retained as the
  future solution-aware route, with pinned action references and environment
  secrets outside source history.
- `microsoft/PowerApps-TestEngine` is explicitly not adopted: it is deprecated,
  scheduled for repository removal on 1 November 2026, and targets canvas Power
  Apps rather than this PBIP/SharePoint system. A future canvas app would need
  a separate Playwright-based regression track.
- Changed paths: `docs/POWER_PLATFORM_CI_CD.md`,
  `scripts/powerplatform_tooling.py`, `scripts/agent_harness.py`, and this
  track plan/review. Fixture/local-tool evidence only; no tenant acceptance.

## Current canonical verification — 2026-09-20

- A clean clone of the canonical remote at `bb2ec04` was bootstrapped with the
  grants context and ran `scripts/package_release.py --version 0.3.0-rc1
  --schema-version rims-grants-publications-v1 --accepted-batch-id
  source-only-canonical`.
- Fresh extraction passed source validation and the full unit suite. The
  receipt reported `FreshExtractionVerified=true`, `ContainsGitHistory=false`,
  `ContainsPrivateRuntime=false`, and `NativeAcceptance=false`.
- Current archive SHA-256 was recorded only in the temporary verification
  output; no archive or live data was added to the repository.

## Remaining S02 gates

S02.3.4 still needs isolated native report readback for a version/batch display.
The 2026-09-20 private observation confirms SharePoint item history is enabled
for the DEV list (500 versions), while the Power BI report exposes Save a copy
and Download but no version-history control and the attempted semantic-model
route is unavailable. These cannot be closed by a source archive or by editing
the original report.

## Current canonical release verification — 2026-09-21

A fresh clean clone at source commit `cfd0383445bb273d603cbf66670bc2b83c3c3d7d`
produced `CHHHS-Research-Publications-v0.3.0-rc1-Source.zip` with
`FreshExtractionVerified=true`, no Git history, no private runtime content and
`NativeAcceptance=false`. The archive SHA-256 was
`4bc587c04136abcfde1a80df03e80f0b8351b5df923ca8f931d5d1295d0c990e`.
This confirms the source-only release remains reproducible and is not evidence
of native report/model version readback.

## S02.3.2 capability observation — 2026-09-20

Receipt: `private/ops/2026-09-20-versioning-capability-observation.json`.
SharePoint item versioning is enabled in the configured DEV list. Power BI
report/model rollback was not evidenced, so definition backups, source manifests
and Git remain the recovery contract. The report/model observation was read-only;
no platform mutation was attempted.

Planning created 2026-09-20. Implementation has not run for this track.

For each task record: task ID, outcome, changed paths, command and exit status, fixture/live distinction, evidence path and capture time, remaining limitations, rollback reference. Do not include credentials or tenant IDs here.
