#!/usr/bin/env bash
# Create a fresh repository environment from an explicitly selected interpreter.
set -euo pipefail
if [[ $# != 3 ]]; then
  printf 'usage: bash scripts/create_ci_python_env.sh ABSOLUTE_PYTHON REPO_ENV EXACT_VERSION\n' >&2
  exit 2
fi
ci_python=$1
ci_env=$2
ci_version=$3
[[ "$ci_python" == /* ]] || { printf 'Absolute bootstrap interpreter required\n' >&2; exit 2; }
[[ "$ci_version" =~ ^3\.15\.[0-9]+((a|b|rc)[0-9]+)?$ ]] || { printf 'Exact Python3.15 candidate required\n' >&2; exit 2; }
ci_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)
"$ci_python" -I - "$ci_root" "$ci_env" "$ci_version" <<'PY'
import pathlib
import platform
import sys
import venv

root, destination, expected = sys.argv[1:]
if platform.python_version() != expected:
    raise SystemExit('Bootstrap Python does not match the selected exact version')
root = pathlib.Path(root).resolve(strict=True)
target = pathlib.Path(destination)
if not target.is_absolute():
    target = root / target
if target.exists() or target.is_symlink():
    raise SystemExit('Refusing to replace an existing environment')
target = target.resolve()
if not target.is_relative_to(root) or target == root:
    raise SystemExit('Environment must be inside this repository')
venv.EnvBuilder(with_pip=False).create(target)
PY
if [[ "$ci_env" != /* ]]; then ci_env="$ci_root/$ci_env"; fi
"$ci_env/bin/python" -I - "$ci_env" "$ci_version" <<'PY'
import pathlib
import platform
import sys

expected_env, expected_version = sys.argv[1:]
if (platform.python_version() != expected_version
        or pathlib.Path(sys.prefix).resolve() != pathlib.Path(expected_env).resolve()
        or sys.prefix == sys.base_prefix):
    raise SystemExit('Created repository interpreter failed actual version/prefix verification')
print(f'{sys.executable}: Python {platform.python_version()}')
PY
