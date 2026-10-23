# Historical desktop scope — cancelled 21 October 2026

Retained for provenance only. All unfinished assessments below are cancelled, not pending or completed technical work.

# Plan: Finish the existing UTM Windows VM only if needed

## Timing and device choice — 13 October 2026

Later/conditional: data spaces, publications and required cloud flows continue on the Mac. If an already authorised Windows computer provides the required Desktop authoring capability, T16 VM setup is unnecessary; qualify that computer under T17 instead. Use T16 only when the existing UTM VM is explicitly chosen under its fallback/backup gates. No VM inspection/change or Windows route is activated by this plan update.

## Implementation
- Cancelled: 01. Require a fallback decision receipt identifying the exact capability that failed, actual web UI attempt, remediation considered and why local authoring would solve it. Plugin non-exposure in this chat is not an eligible technical failure.
- Cancelled: 02. Confirm an authorised Mac device and inspect host CPU architecture, macOS/UTM version, available RAM/disk and the user-selected existing VM configuration. Use scripts/Inspect-UTM-Host.sh for read-only host checks; do not recursively scan the home directory.
- Cancelled: 03. Inspect the existing Windows installation stage and ISO architecture. Use ARM64 Windows for Apple Silicon or x64 for Intel; do not infer architecture from the browser user agent.
- Cancelled: 04. Back up the powered-off VM/configuration before changing it. Review resource allocation using observed host limits. Prefer virtualisation with matching architecture; do not silently emulate the wrong architecture.
- Cancelled: 05. Complete installation and official UTM guest/SPICE tools as required, preserving TPM/Secure Boot. No installer-check bypasses, security-disabling registry edits, license-key disclosure or automatic license purchases.
- Cancelled: 06. Install normal Windows updates and verify the relevant Windows-on-ARM fix or superseding updates. Collect OS build/architecture evidence rather than relying on one historical KB appearing in Get-HotFix.
- Cancelled: 07. Configure only an explicitly chosen project exchange folder and normal networking. Test display resolution, keyboard/mouse, clipboard/shared-folder policy and public HTTPS access; do not disable endpoint controls.
- Cancelled: 08. Record VM boot and guest-tool checks. Document that UTM is a practical fallback to test, not a Microsoft-certified Power BI virtual-desktop environment.

## Review and completion
- Cancelled: Execute applicable automated checks and the separate native/tenant checks.
- Cancelled: Record defects, fixes, precise evidence references and remaining blockers in review.md.
- Cancelled: Update metadata and track register; commit local changes without claiming unperformed external actions.

## Current state
Not started. No connected device was available when this package was created. UTM configuration, licensing, storage and Windows setup stage remain unknown.
