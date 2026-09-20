# Execution evidence

## S02.1–S02.2 local implementation

- Replaced the unsafe packager that embedded `.git` and created an all-history bundle.
- Added explicit software, schema and batch identities, source commit, dirty-build and native-acceptance fields.
- Source archives exclude private runtime paths, canonical live downloads, ZIP/bundle files and the release manifest itself.
- Archive paths are sorted and the fresh extraction verifies the manifest, absence of Git/private runtime and local validation/tests.
- Added `tests/test_package_release.py`; focused result: 3 tests passed.
- Review fix: ZIP members now use a fixed timestamp and the focused result is 4 tests passed, including byte-stable member output.

The current checkout is intentionally dirty, so the package command refuses to create a reproducible release. This is a safety gate, not a packaging failure. S02.2.3–S02.3 remain open until a clean candidate and native recovery/versioning evidence exist.

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

Planning created 2026-09-20. Implementation has not run for this track.

For each task record: task ID, outcome, changed paths, command and exit status, fixture/live distinction, evidence path and capture time, remaining limitations, rollback reference. Do not include credentials or tenant IDs here.
