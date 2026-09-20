# GitHub synchronization

Requested and created on 2026-09-20: https://github.com/edithatogo/chhhs-research-publications (private).

Initial upload is pending privacy remediation. Existing tracked history contains `downloads/canonical_live_artifacts/` tenant exports, a flow ZIP, seeded registry data and tenant identifiers in source/configuration/documents. AGENTS.md requires actual tenant identifiers, snapshots and caches to remain in ignored private storage. A private repository does not remove that requirement, and `.gitignore` does not remove past commits.

Do not push existing branches/tags until this is resolved. Preserve local history and uncommitted report changes. Two options need the owner's choice: create a sanitized source-only initial history for GitHub while retaining local history privately, or sanitize a separate copy of the full history and verify all reachable objects. Neither requires deleting the current checkout.

Before first upload, move runtime targets to private configuration, exclude archived tenant exports and scan the exact proposed Git objects including history. Verify remote visibility and branch head after upload. Do not automate background pushes or upload private receipts.
