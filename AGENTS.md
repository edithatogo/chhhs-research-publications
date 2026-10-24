# Agent instructions

## Runtime and dependency compatibility — 24 October 2026

Prefer the latest qualified runtime and dependency versions, including Python
3.15.1 for the current repository environment. Another version may be used when
needed for application, tooling, CI/helper or provider compatibility. Choose the
newest suitable version that works; record the concrete reason and scope of an
exception and verify the actual interpreter and dependency behavior. A necessary
alternate version does not require additional permission.

Select the repo-local interpreter explicitly for repository checks. Preserve
working latest-version environments and in-flight operations; do not downgrade
or rebuild unnecessarily. Follow setup instructions and exact hash locks for the
selected environment. Installation or a manifest alone is not qualification.
Keep security, functionality, ownership and private-evidence gates. No emails or
external messages are authorised by a runtime change. Historical evidence and
synthetic version-handling fixtures remain unchanged.

## Current route precedence — 13 October 2026

Follow the [shared-data delivery contract](docs/PLATFORM_COMPLETION_PLAN.md#shared-data-delivery-contract--13-october-2026): CLI/API-first on qualified exact targets, existing archive bootstrap, complete raw payload/schema retention before vertical filtering, and one writer per file/object. Historical browser-first/no-CLI statements and dated completion claims do not override this direction. Preserve current source scope, permissions, isolation, rollback and explicit activation/delivery gates. The publications chat retains its current objects and checkpoint; shared-data work requires disjoint scope or explicit handoff.


Solo-repository harness: after the required entry documents, read `handoff/CURRENT_STATE.md`. Run `.venv/bin/python scripts/agent_harness.py context --task grants` (or publications/organisation/platform) for targeted context. See `docs/SOLO_AGENT_WORKFLOW.md`. Use existing Conductor plans; keep one short checkpoint and avoid extra approval or project-management layers. `.venv/bin/python scripts/agent_harness.py check --task all` runs the three required checks with the active interpreter and preserves failures. Local success never proves tenant acceptance.

Read conductor/index.md and handoff/POWERBI_PLUGIN_START_HERE.md first. Use the existing Git history and the user's existing Power BI report, not a new Fabric project.

Primary route: supported CLI/API operations qualified on the exact target, with BrowserOS neo fallback under shared-UI ownership. Reuse established discovery/isolation evidence unless inputs changed. Data querying is not authoring; T16/T17 remain conditional.

No shared/original model writes without an approved isolation/rollback path. No blind rename of old fields. Preserve source/date uncertainty. Full canonical bibliography and monthly exports must reconcile to model key sets. Synthetic fixtures are never live data.

Validation cadence: use changed-behavior tests and affected structural checks. Documentation-only changes need structural/link checks, not new mirror tests. Run `.venv/bin/python scripts/agent_harness.py check --task all` at integration/release milestones or broad shared-contract changes. Native M/DAX, report rendering, live refresh and scheduled delivery remain separate gates.

Keep actual tenant IDs, screenshots, auth tokens, raw API snapshots and caches in ignored private paths. Do not copy old workforce row data to this repository or an unapproved third-party plugin. Do not change sharing, publish, enable schedules, purchase capacity or change an existing VM without the specific approval gate.

## Concurrent execution checkpoints

Use [bounded implementation and lane resume](docs/EXECUTION_EFFICIENCY.md) for
concurrent chats. Each owner keeps its own ignored compact checkpoint and explicit
finish line; `scripts/lane_resume.py --lane <lane>` reads it without executing
prose. Preserve in-flight operations. Reuse unchanged verification, distinguish
deployment/runtime/activation/scheduled proof, and record a changed hypothesis
before retrying a failed native operation. Consolidate qualified deployment helpers
at terminal handover rather than replacing an active owner's route.
