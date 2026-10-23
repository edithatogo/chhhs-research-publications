# Python3.15 dependency qualification

## Attached Fabric MCP candidate — 24 October 2026

The isolated Python3.15.1 candidate for existing MCP package0.8.7 passes
in-memory and stdio initialization/tools-list with exact58-tool schema parity
between transports and unchanged names against the attached catalogue. All74
locked packages pass dependency consistency. No tenant tool/network/auth call,
global profile edit or active host restart occurred. See
`fabric-mcp-python315-20261024.json` and [host handover guide](../../docs/FABRIC_MCP_RUNTIME.md).
The existing external3.14.6 hosts remain active pending actual terminal/ownership
evidence; this is a qualified local replacement, not completed host migration.

The23October2026 candidate targets Python3.15.1 and uv0.13.5. Exact hash locks
include direct and transitive dependencies, allowing development candidates.
See `python315-20261023.json` for actual local checks and version inventory.

Current canonical source has no Node package manifest or package-manager lock.
Node26.12.1 matches the latest official distribution observed. npm12.2.1 was
qualified using an isolated private cache; shared global npm11.20.0 remains
untouched because this repository has no npm build/runtime to promote.

Only clean canonical source is qualified here. In-flight native flows, raw
archives, checkpoints, authentication, unrelated dirty work, schedules and email
controls remain unchanged. Hosted exact-head checks and main verification are
separate promotion evidence; do not infer them from this local receipt.

The old shared reusable security workflow hardcodes3.15.0 without a runtime
parameter. RIMS now owns that job, retaining full-history gitleaks, immutable
shared pin-checker, actionlint and zizmor while using its3.15.1 hash-locked
tools. The development canary resolves RIMS direct inputs and permits isolated
source builds: PyYAML6.0.3 is current but lacks a cp315 Linux wheel, so a
wheel-only install was rejected rather than silently falling back to3.14.
