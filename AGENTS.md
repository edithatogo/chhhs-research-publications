# Agent instructions

Solo-repository harness: after the required entry documents, read `handoff/CURRENT_STATE.md`. Run `python3 scripts/agent_harness.py context --task grants` (or publications/organisation/platform) for targeted context. See `docs/SOLO_AGENT_WORKFLOW.md`. Use existing Conductor plans; keep one short checkpoint and avoid extra approval or project-management layers. `python3 scripts/agent_harness.py check --task all` runs the three required checks with the active interpreter and preserves failures. Local success never proves tenant acceptance.

Read conductor/index.md and handoff/POWERBI_PLUGIN_START_HERE.md first. Use the existing Git history and the user's existing Power BI report, not a new Fabric project.

Primary route: actual Power BI plugin and/or ordinary Power BI web UI. Discover schemas and prove both report and semantic-model writes; data querying is not authoring. T16/T17 are conditional, not the default.

No shared/original model writes without an approved isolation/rollback path. No blind rename of old fields. Preserve source/date uncertainty. Full canonical bibliography and monthly exports must reconcile to model key sets. Synthetic fixtures are never live data.

Run `python -m unittest discover -s tests -v`, `python scripts/validate_project.py`, and `python scripts/webfirst_contracts.py validate`. Native M/DAX, report rendering, live refresh and scheduled delivery are separate gates.

Keep actual tenant IDs, screenshots, auth tokens, raw API snapshots and caches in ignored private paths. Do not copy old workforce row data to this repository or an unapproved third-party plugin. Do not change sharing, publish, enable schedules, purchase capacity or change an existing VM without the specific approval gate.
