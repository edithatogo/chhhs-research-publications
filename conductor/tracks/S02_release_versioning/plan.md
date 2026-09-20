# Reproducible source and deployment versioning: executable plan

Status: in_progress. Source packaging is locally verified; native recovery/versioning remains unaccepted.

## S02.1 Version contract and tests

- [x] S02.1.1: Inspect package_release.py without running it: it currently hardcodes v0.2.0-rc1, bundles all history and includes .git. These behaviours are unsuitable for a source-only GitHub release.
- [x] S02.1.2: Define a version argument, Git commit identity, dirty-build flag, schema versions, content hashes and local/native status fields. A dirty preview is never labelled an accepted release.
- [x] S02.1.3: Write tests for missing/invalid version, dirty accepted release, changed file hash, missing required artefact, private file exclusion and repeatable manifests.
- [x] S02.1.4: Use independent fields for SoftwareVersion, SchemaVersion and AcceptedBatchID. A daily harvest changes batch identity, not software version.
- [x] Checkpoint: write commands/results, changed paths and remaining blockers in review.md; update CURRENT_STATE. Stop dependent work on failure.

## S02.2 Packaging and reproducibility

- [x] S02.2.1: Refactor packaging to produce a reviewed source allowlist archive without .git, tenant exports, private configuration or history bundles. Keep an explicit separate private backup route.
- [x] S02.2.2: Use sorted paths and stable archive metadata. Exclude the receipt itself from its own hash calculation; report capture time separately from reproducibility hashes.
- [x] S02.2.3: Run the harness on a fresh temporary extraction. Missing private data must not be replaced with fabricated receipts; verify submodule pin and explicit bootstrap instructions.
- [x] S02.2.4: Add manifest verification that detects changed files. Do not call a local file copy a new live export.
- [ ] Checkpoint: write commands/results, changed paths and remaining blockers in review.md; update CURRENT_STATE. Stop dependent work on failure.

## S02.3 Native versioning and solo operation

- [x] S02.3.0: Assess Microsoft Power Platform Build Tools 2.0, `powerplatform-actions` and PowerApps Test Engine. Keep Build Tools/actions conditional on a Dataverse solution; reject the deprecated Test Engine for the current PBIP/SharePoint acceptance surface.
- [x] S02.3.1: Correct VERSIONING_ARCHITECTURE.md: Power Automate drafts/versioning is conditional on solution-aware flow support. Verify actual flow/environment capability before claiming native rollback.
- [ ] S02.3.2: Record observed SharePoint versioning, model version-history support and report export route privately. Use definition backups where native versioning is unavailable; no Dataverse/capacity purchase dependency.
- [x] S02.3.3: Document one-owner routine: focused commit, full local checks, verified native candidate, release tag and manifest, optional GitHub Release. Conductor stays the backlog; no compulsory Projects/Jira/Planner duplication.
- [ ] S02.3.4: Add a version/batch display to the existing report only through the isolated authoring route with readback; otherwise leave that subtask pending.
- [ ] S02.3.5: Run full checks; demonstrate source-package verification and private snapshot restoration in an isolated target before claiming platform recovery.
- [ ] Checkpoint: write commands/results, changed paths and remaining blockers in review.md; update CURRENT_STATE. Stop dependent work on failure.
