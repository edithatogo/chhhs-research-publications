#!/usr/bin/env bash
# Explicit repo-local Python; never replace/restart an attached host here.
set -euo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
host_env="${RIMS_FABRIC_MCP_ENV:-$repo_root/.venv-fabric-mcp}"
if [[ ! -d "$host_env" ]]; then
  echo "Fabric MCP environment is absent: prepare the locked candidate first." >&2
  exit 2
fi
host_env="$(cd "$host_env" && pwd -P)"
case "$host_env" in
  "$repo_root"/*) ;;
  *) echo "Fabric MCP must use an explicitly selected repo-local environment." >&2; exit 2 ;;
esac
host_python="$host_env/bin/python"
if [[ ! -x "$host_python" ]]; then
  echo "Fabric MCP environment has no executable Python." >&2
  exit 2
fi
"$host_python" -c 'import sys; required=(3,15,1); actual=sys.version_info[:3]; sys.exit(0 if actual == required else "Fabric MCP requires actual Python 3.15.1; got " + str(actual))'
exec "$host_python" -m ms_fabric_mcp_server "$@"
