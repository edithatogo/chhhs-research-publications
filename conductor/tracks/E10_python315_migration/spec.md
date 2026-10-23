# Specification: E10 Python3.15 migration and qualification

## Objective

Migrate every active Python use supporting this repository to Python3.15 at the
newest qualified patch (currently3.15.1): development, artifact preparation,
build/test, automation, CI, containers and helper/tool hosts. Verify the actual
explicit repo-local interpreter; align constraints, complete dependency locks,
CI and current setup instructions. Remove older active defaults/compatibility
runners. Preserve historical evidence and deliberate version-handling fixtures.

## Required outcomes

1. Inventory maintained manifests/locks, actual interpreter paths, CI matrices,
   jobs, containers and helper entrypoints; classify external ownership explicitly.
2. Resolve latest direct/transitive dependencies including development candidates,
   pip/uv/certifi; qualify isolated3.15.1 environments. Fix supported failures and
   record precise unresolved incompatibilities without an older fallback.
3. Select and verify explicit repo-local3.15.1 for next executions. Never replace
   an environment under a running operation; preserve current handles until
   terminal and prepare exact terminal handover for affected helper hosts.
4. Align current constraints, hash locks, CI/actions and instructions; retain
   significant artifact behavior and source/security checks.
5. Require meaningful checks, current-head integration, immutable PR/commit and
   post-merge main proof before claiming canonical promotion.
6. Account for every in-scope active use and unresolved handover. A source pin or
   installed interpreter alone is not full repository runtime completion.

## Existing accepted work

PR9 merged as `36bbb3f5df6a618c59c9b524f43a23580f08f215`.
See [qualification inventory](../../../audit/dependencies/python315-20261023.json)
and [setup/limits](../../../audit/dependencies/README.md). Working-checkout
execution and main/PR receipts are retained privately under
`private/ops/2026-10-23-runtime-upgrade/`. Do not repeat unchanged passing checks.

## Boundaries

No native flow/model/report/authentication/connection/schedule change is implied.
Preserve E01 Crossref run/checkpoints/archives, G02 source ownership, unrelated
dirty files and other repositories. No email, contact, approval-seeking or new
authentication method. External EndNote application hosting belongs to Submissions.
The existing attached Fabric MCP environment records3.14.6 and must not be
replaced mid-session; classify its RIMS use and exact supported3.15 handover
without editing another owner's global profile or claiming it already migrated.

## Goal-tool fidelity

The requested goal objective is this full specification. The existing unfinished
E01 goal prevents a separate goal in this chat. Preserve it; do not create a
second goal, overwrite/shrink the objective, falsely complete it or use a file
as a substitute for durable goal state. Registration still records actual work.
