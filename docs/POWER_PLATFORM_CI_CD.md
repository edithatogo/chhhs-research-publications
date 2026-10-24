# Power Platform CI/CD boundary

The local toolchain includes Microsoft Power Platform CLI (`pac`), Azure CLI
with the Azure DevOps extension, PowerShell and GitHub CLI. The repository
harness runs a read-only tooling preflight on every full local check.

The canonical repository also runs the source-only workflow at
`.github/workflows/local-quality.yml` on pushes to `main`, pull requests and
manual dispatch. It executes the unit suite, project/web-first/Conductor
validators, visual checks and the read-only Power Platform preflight. It does
not authenticate to or mutate the tenant. The workflow pins the hosted runner
to `ubuntu-24.04` and uses the Node 24-compatible `actions/checkout@v5` and
`actions/setup-python@v6` actions for reproducible source-only evidence.

Microsoft Power Platform Build Tools 2.0 are the preferred Azure DevOps task
family when this project has a Dataverse-backed, solution-aware deployment
path. PAC-based tasks should be kept on one Build Tools major version within a
pipeline. Use `pac solution pack`, `unpack`, `check`, `version` and the relevant
Build Tools tasks for solution source, static analysis and controlled import.

The current canonical unmanaged CHHHS RIMS Platform solution contains the
solution-aware flows. The 24 October export contains 35 workflows and six
connection references; see the [scoped grants reconciliation](GRANTS_SOLUTION_RECONCILIATION.md).
The PBIP/TMDL, SharePoint lists/forms/data and Power BI report/model remain
separate artefacts, not contents proved by a solution ZIP. PAC export and
source parity do not prove runtime writes, refresh, rendering or delivery.

Portable parameterized flow definitions are versioned in `config/flows/`.
Keep raw solution exports, exact connection references, environment variables
and target bindings in ignored private evidence; do not copy the native
unpacked project into this public repository. Validate the exported artefact
against source and require fresh target readback after an authorized import.
No service principal, connection, pipeline, environment, schedule or import
is created by the local harness. PAC pack/unpack are local operations;
`pac solution check` calls the online Checker service and is a separate gate.

## Microsoft action and test-engine decisions

The [`microsoft/powerplatform-actions`](https://github.com/microsoft/powerplatform-actions)
repository is a suitable GitHub Actions equivalent for the conditional
Dataverse/solution path. It should be introduced only with an isolated
solution, pinned action tags or commit SHAs, GitHub environment secrets, and a
post-import readback gate. It is not a substitute for SharePoint list,
Power BI semantic-model/report, refresh, or Power Automate run acceptance.

The [`microsoft/PowerApps-TestEngine`](https://github.com/microsoft/PowerApps-TestEngine)
is not adopted. Microsoft marks it deprecated and the repository is scheduled
for removal on 1 November 2026; it is a canvas Power Apps UI test engine, not a
Power BI or SharePoint acceptance tool. If a future RIMS canvas app is added,
use Microsoft's current Power Platform Playwright samples in a separate,
isolated regression track after confirming their support status. Browser
readback of the existing Power BI/SharePoint surfaces remains the acceptance
route for this repository.

Neither decision authorises credentials, environment creation, solution import,
publishing, schedules, or tenant writes from the local harness.

Local baseline:

```text
python3 scripts/powerplatform_tooling.py check
python3 scripts/agent_harness.py check --task all
```
