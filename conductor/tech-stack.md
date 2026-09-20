# Technology

Primary: the user's Microsoft Power BI browser workflow plugin plus ordinary Power BI Service report/model/Power Query web editors. Installed workflow v0.1.4 and local Chrome access were observed on 2026-09-12. Bind operations to actual controls and verify permissions and persistence independently; no dedicated Power BI API authoring schemas were exposed.

Source control: existing PBIP, PBIR, TMDL, M and DAX files. Microsoft schema URLs may contain the namespace "fabric"; this is not a requirement to deploy Fabric Git or purchase capacity.

Local support: Python 3.11+ standard library; unittest, source validation, route/isolation checks and full-register CSV/HTML renderer. These do not execute M/DAX. Power Automate for a monthly orchestration is planned, not deployed.

Fallback only: existing UTM on the user's Mac, correctly matched Windows 11 architecture and regular Power BI Desktop. Host/guest/installer compatibility must be verified and a native smoke test performed. No implication that UTM is an officially supported Power BI VDI environment.

Conductor protocol: upstream `main` is pinned by the `.agents/plugins/conductor` submodule at `6e8f9a860bcdd6a2c423473c12e745200688c633` (`conductor-v0.4.1-18`, verified 2026-09-20). After cloning, run `git submodule update --init .agents/plugins/conductor`. GitHub synchronization is now requested; see `handoff/GITHUB_SYNC.md` for its privacy boundary.

Native implementation decision (2026-09-13): [Power Platform architecture, observed licences and fallbacks](../docs/POWER_PLATFORM_NATIVE_PLAN.md). Prefer the existing Power BI workspace, standard cloud connectors and native M/DAX; Python remains local verification tooling. Native and unattended acceptance gates remain open.
