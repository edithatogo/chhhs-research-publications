"""Remove explicitly selected response-copy cards without changing archive bytes.

Offline only. A fresh native preimage, supported save and exact readback remain
required. This does not alter scopes, requests, schedules or archive contracts.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re


def fingerprint(value: dict) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def prepare(definition: dict, paths: list[str], expected_sha256: str) -> dict:
    if fingerprint(definition) != expected_sha256:
        raise ValueError("Native definition preimage changed")
    if not paths or len(paths) != len(set(paths)):
        raise ValueError("Select unique exact action paths")
    result = deepcopy(definition)
    removed = []
    for path in paths:
        parts = path.split("/")
        actions = result["actions"]
        for part in parts[:-1]:
            actions = actions[part]["actions"]
        name = parts[-1]
        action = actions[name]
        expression = action.get("inputs")
        match = (re.fullmatch(r"@string\(body\('([A-Za-z0-9_]+)'\)\)", expression)
                 if isinstance(expression, str) else None)
        if (not match or action.get("type") != "Compose"
                or set(action) != {"type", "inputs", "runAfter"}):
            raise ValueError("Only plain string(body()) response copies are eligible")
        source = match.group(1)
        if (action["runAfter"] != {source: ["Succeeded"]}
                or actions.get(source, {}).get("type") != "Http"):
            raise ValueError("Copy must depend directly on one successful same-scope HTTP action")
        # Any other use of action status, body(), result() or metadata needs its
        # own reviewed transform. Do not silently weaken failure observation.
        serialized = json.dumps(result)
        if re.search(r"(?:actions|body|result)\('" + re.escape(name) + r"'\)", serialized):
            raise ValueError("Copy has status/body/result consumers")
        reference = f"outputs('{name}')"
        replacement = expression[1:]

        def rewrite(value):
            if isinstance(value, str):
                if reference in value and not value.startswith("@"):
                    raise ValueError("Reference appears outside an expression")
                return value.replace(reference, replacement)
            if isinstance(value, list):
                return [rewrite(item) for item in value]
            if isinstance(value, dict):
                out = {key: rewrite(item) for key, item in value.items()}
                deps = out.get("runAfter")
                if isinstance(deps, dict) and name in deps:
                    if deps[name] != ["Succeeded"] or source in deps:
                        raise ValueError("Non-success or conflicting downstream dependency")
                    deps[source] = deps.pop(name)
                return out
            return value

        del actions[name]
        result = rewrite(result)
        removed.append({"path": path, "source": source, "substitution": replacement})
    return {"definition": result, "preimage_sha256": expected_sha256,
            "definition_sha256": fingerprint(result), "removed": removed,
            "scope_schedule_connections_changed": False, "native_deployed": False}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--definition", type=Path, required=True)
    parser.add_argument("--expected-sha256", required=True)
    parser.add_argument("--action", action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = prepare(json.loads(args.definition.read_text()), args.action, args.expected_sha256)
    with args.output.open("x") as stream:
        json.dump(result, stream, indent=2)


if __name__ == "__main__":
    main()
