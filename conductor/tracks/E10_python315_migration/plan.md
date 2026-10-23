# E10 numbered implementation plan

Status: in progress. Source/CI qualification is accepted; host handover and final
full-scope audit remain. Reuse accepted evidence, no status-only commits or
routine second review. Each step has an explicit implementation/evidence boundary.

- [x] E10.1 Inventory canonical Python/Node manifests, hash locks and active CI/tool
  targets; verify root `.venv/bin/python` actually3.15.1. No maintained root
  container, pyproject/Pipfile or Node package graph found. Native runtime stays
  Microsoft. Source inventory: PR9 and audit/dependencies.
- [x] E10.2 Resolve newest compatible stable/development direct/transitive local
  dependencies in isolation;40 packages. pip26.2.2/certifi2026.10.19/uv0.13.5,
  lxml7.0.0b1/zizmor1.32.0rc1 retained. Supported PyYAML6.0.3 source build fixed
  missing cp315 Linux wheel without a3.14 fallback. Exact hashes recorded.
- [x] E10.3 Promote source constraints/locks, `.python-version`, active source/tool/
  security CI and current instructions to3.15.1; candidate execution restricted
  to3.15.x. Old compatibility runner removed. RIMS-owned security job retains
  gitleaks/actionlint/pin/security checks. PR9, canonical commit36bbb3f5.
- [x] E10.4 Qualify significant behavior and security:619 tests/12 skips,460
  contracts, full harness, consistency/audit/lint, DOCX/XLSX roundtrips;5 exact-head
  hosted checks pass and post-merge main quality/security/dependency graph pass.
  Qualified/main tree615a10ae679fc7e590548881debb8f619f02f184.
- [x] E10.5 Safely establish working-checkout3.15.1/40 packages after selected
  runtime process inventory; local agent launcher verifies exact interpreter and
  E01 next-run prompt selects it. Existing operations/host environments untouched.
- [ ] E10.6 Finish attached helper-host accounting and terminal handover. Existing
  external Fabric MCP host environment records3.14.6. Inspect actual configured
  launcher/ownership and supported latest package qualification; prepare isolated
  repo-local3.15.1 replacement for a terminal host boundary, preserving native
  bindings/authentication and other consumers. Do not restart the active host.
  External EndNote3.13.13 host is separately owned outside RIMS; exclude with
  evidence, do not alter it. Any genuine unsupported dependency stays explicit.
- [ ] E10.7 Audit all numbered specification requirements against current state,
  complete any remaining in-scope uses/handover and verify current-head/main
  integration of necessary source changes. Do not promote optional host claims
  or infer full qualification from PR9 alone.
- [x] E10.8 Inspect durable goal state: unfinished E01 goal remains blocked,
  preserved unchanged. Separate E10 CreateGoal not attempted because no goal
  slot is available; no retry or false rejection/success claim. Registration
  receipt records requested objective and actual goal status. This completed
  inspection is not a claim that E10 has an armed goal.

## Next exact action

Read the configured attached Fabric MCP launch path and package metadata, then
prepare only an isolated3.15.1 host candidate within existing ownership. Retain
active process and route; no native/auth changes or contacts. Run only newly
relevant qualification, then hand over at terminal.

## Completion receipts

- Canonical qualification: `audit/dependencies/python315-20261023.json`.
- Current working runtime/main proof: `private/ops/2026-10-23-runtime-upgrade/completion.json`.
- Registration/goal state: `private/ops/2026-10-23-runtime-upgrade/track-registration.json`.
- No separate goal is armed; E01 remains unfinished and must not be overwritten.
