# Sanitised private GitHub synchronisation: executable plan

Status: planned. All checkboxes below represent outstanding execution, not completed planning.

## S03.1 Inventory and safe candidate

- [x] S03.1.1: Verify origin and remote PRIVATE visibility; inspect remote branches before assuming it is still empty. Do not create a second repository.
- [x] S03.1.2: Inventory tracked files and all history intended for push. Report paths/categories, not secret values. Include tenant identifiers, connection exports, ZIP internals, cache/data exports and .git content.
- [ ] S03.1.3: Prepare a sanitised source-only candidate in a separate temporary working directory, with an exclusion/remediation manifest. Preserve the original checkout and local history.
- [ ] S03.1.4: Replace hardcoded runtime identities with private configuration and tracked example placeholders. Adapt tests/generators so the clean source package is usable without tenant credentials.
- [ ] S03.1.5: Document the concrete choice of clean initial history versus separately sanitised retained history. Check whether the user's latest instruction resolves that choice; if unclear, ask only after preparing the candidate and impact comparison.
- [ ] Checkpoint: write commands/results, changed paths and remaining blockers in review.md; update CURRENT_STATE. Stop dependent work on failure.

## S03.2 Verify and publish source

- [ ] S03.2.1: Test the exact candidate with the harness, bootstrap its pinned Conductor dependency and scan every reachable Git object intended for upload. A clean working tree alone is insufficient.
- [ ] S03.2.2: Confirm no synthetic test record is promoted into live data and no private receipts are staged. Keep authenticated configuration out of Git even though the remote is private.
- [ ] S03.2.3: After the history choice is resolved, commit the candidate with a source/version manifest and push a named branch to the existing private origin. Do not force-push or rewrite the original history implicitly.
- [ ] S03.2.4: Read back remote commit SHA and PRIVATE visibility. Clone the remote into a fresh temporary directory and run all local checks; record missing private runtime dependencies explicitly.
- [ ] S03.2.5: Document the ongoing source checkout/branch and sync command so later git push cannot accidentally upload unsanitised ancestry. Update CURRENT_STATE and GITHUB_SYNC with verified results.
- [ ] Checkpoint: write commands/results, changed paths and remaining blockers in review.md; update CURRENT_STATE. Stop dependent work on failure.
