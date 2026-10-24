"""Check offline comparator entrypoints and exact synthetic test selections.

Run with repo-local Python (optionally -S); no native data or network required.
"""
import argparse
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ('reconcile_model_registry_identity', 'reconcile_registry_model_provenance',
         'reconcile_full_month_exports', 'reconcile_publication_sources',
         'reconcile_pubmed_registry_keys')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--smoke-only', action='store_true', help='CLI imports only; full CI already runs the tests')
    args = parser.parse_args()
    env = {k: v for k, v in os.environ.items() if k not in {'PYTHONPATH', 'PYTHONHOME'}}
    failed = False
    with tempfile.TemporaryDirectory() as outside:
        for tool in TOOLS:
            # Direct invocation must work outside the checkout; module invocation
            # must work from its normal repository root, without site-packages.
            for command, cwd in (([sys.executable, '-S', str(ROOT/'scripts'/(tool+'.py')), '--help'], outside),
                                 ([sys.executable, '-S', '-m', 'scripts.'+tool, '--help'], ROOT)):
                result = subprocess.run(command, cwd=cwd, env=env, capture_output=True, text=True, timeout=30)
                if result.returncode:
                    print(result.stderr)
                    failed = True
            if not args.smoke_only:
                result = subprocess.run([sys.executable, '-S', '-m', 'unittest', 'discover', '-s', 'tests',
                                         '-p', 'test_'+tool+'.py', '-v'], cwd=ROOT, env=env, check=False, timeout=90)
                failed |= result.returncode != 0
    print('FAIL' if failed else 'PASS_PORTABLE_SOURCE_ONLY — synthetic checks, no native acceptance')
    return 1 if failed else 0


if __name__ == '__main__':
    raise SystemExit(main())
