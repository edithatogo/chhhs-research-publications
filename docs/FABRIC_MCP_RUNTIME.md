# Fabric MCP Python3.15 candidate and host handover

This is the existing `ms-fabric-mcp-server` client, not a replacement Fabric
service, auth method or tenant configuration. The shared launcher currently
uses an external Python3.14.6 environment. Its multiple attached processes and
other repository consumers must remain untouched until their actual operations
and host sessions are terminal. Archiving a chat does not terminate native work.

## Qualified local candidate

The24October2026 isolated repo-local candidate uses actual Python3.15.1 and the
complete hash lock in `config/tool-hosts/fabric-mcp.txt`. Current package0.8.7
and latest compatible transitive dependencies include FastMCP3.4.11, MCP1.30.0,
Azure Identity1.26.0 and Pydantic2.14.1. Local MCP initialization/tools-list
passed without tenant calls, socket connections or auth subprocess attempts;
all58 tool names match the attached host's exposed catalogue. Full authentication,
native tools and host activation are not qualified by that check.

The separate Fabric CLI1.8.0 declares Python<3.15 and is not this package.
Its existing failed qualification is reused; no CLI downgrade or duplicated
compatibility trial is justified by successful MCP qualification.

## Reproducible preparation

Use a fresh destination. Do not run these commands over an existing environment
or an active host. Verify the actual repository interpreter before preparing.

```sh
.venv/bin/python --version
.venv/bin/python -m uv venv --python "$PWD/.venv/bin/python" .venv-fabric-mcp
.venv/bin/python -m uv pip sync --python "$PWD/.venv-fabric-mcp/bin/python" --require-hashes config/tool-hosts/fabric-mcp.txt
.venv-fabric-mcp/bin/python --version
bash scripts/start_fabric_mcp.sh --version
```

The launcher selects `.venv-fabric-mcp` by default or an explicit repo-local
`RIMS_FABRIC_MCP_ENV`, checks actual3.15.1 and executes that interpreter directly.
It never invokes PATH Python, installs dependencies, logs in, restarts a host or
edits MCP configuration. It inherits the existing working directory/environment;
retain the qualified PATH/client/resource mapping. Dotenv was disabled in the
tenant-free trial only. Any difference in production dotenv lookup must be
reconciled before activation; never copy tokens, credentials or auth caches.

## Terminal handover boundary

1. Read actual configured launcher, package/runtime and relevant operation/host
   handles. Preserve running native effects and the retained Crossref run.
2. Prepare/qualify in isolation; compare actual tool names/schemas and supported
   local transport. Retain first failures and zero retries for tenant operations.
3. Require evidence that affected host sessions and native operations are
   terminal. Multiple consumers of the global profile are a separate ownership
   boundary. Do not infer release from CPU idleness, process age or chat archival.
4. Stage the exact command/args/environment diff and reversible preimage. Select
   only the intended next host/session using its supported configuration route;
   do not force a restart or change other repositories' global settings.
5. Verify actual3.15.1, identical tool contract and the exact existing permitted
   workload after a supported switch, without a new authentication method.

No handover or global profile mutation has occurred. The no-contact project rule
prevents requesting a release from G02 or another owner. Record an unresolved
terminal/ownership boundary and continue independent work, without outreach.
Private candidate, process inventory, exact commands and receipts are under
`private/ops/2026-10-24-fabric-mcp315/`.
