"""Read a bounded owner-maintained checkpoint; never execute its contents."""
import argparse
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = ('owner', 'updated_at', 'owned_scope', 'outcome', 'finish_line',
            'last_accepted', 'current_operation', 'next_action', 'blocker',
            'failures', 'completion')


def read_checkpoint(root, lane):
    if not re.fullmatch(r'[a-z][a-z0-9-]{0,47}', lane):
        raise ValueError('Use a simple lane name, not a path')
    base = (root / 'private/ops/execution-lanes').resolve()
    path = (base / (lane + '.json')).resolve()
    if not base.is_relative_to(root.resolve()) or not path.is_relative_to(base):
        raise ValueError('Checkpoint escapes its repository directory')
    if path.stat().st_size > 12000:
        raise ValueError('Checkpoint exceeds 12000 bytes; retain history separately')
    data = json.loads(path.read_text())
    if not isinstance(data, dict) or data.get('schema_version') != 1:
        raise ValueError('Unsupported checkpoint schema')
    if any(key not in data for key in REQUIRED):
        raise ValueError('Incomplete execution checkpoint')
    for key in REQUIRED[:-2]:
        if not isinstance(data[key], str) or not data[key].strip():
            raise ValueError('Checkpoint text fields must be nonempty strings')
    if not isinstance(data['failures'], list) or not isinstance(data['completion'], list):
        raise ValueError('Failures and completion must be lists')
    for failure in data['failures']:
        if not isinstance(failure, dict) or any(not isinstance(failure.get(k), str)
                or not failure[k].strip() for k in ('operation', 'observed', 'changed_hypothesis', 'retry_condition')):
            raise ValueError('Failure must explain the changed hypothesis and retry condition')
    for row in data['completion']:
        if not isinstance(row, dict) or any(not isinstance(row.get(k), str) or not row[k].strip()
                for k in ('name', 'deployed', 'runtime_proven', 'enabled', 'scheduled_proven', 'evidence')):
            raise ValueError('Completion must distinguish deployment, runtime, activation and scheduling')
    return data


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lane', required=True)
    parser.add_argument('--checkpoint-root', type=Path, default=ROOT,
                        help='Explicit owner evidence checkout; defaults to this code checkout')
    args = parser.parse_args(argv)
    try:
        data = read_checkpoint(args.checkpoint_root.resolve(), args.lane)
    except (OSError, ValueError) as exc:
        parser.exit(1, f'FAIL: {exc}\n')
    print('OWNER REPORT ONLY — verify changed native facts before dependent actions.')
    print(json.dumps(data, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
