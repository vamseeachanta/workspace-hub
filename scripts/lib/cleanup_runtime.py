"""Read-only preflight for daily cleanup; see cleanup-safety.html protocol v1."""
import argparse
import json
import math
import re
import sys
import time
from pathlib import Path


def coverage(hub, sibling_root, registry, execution_names=None):
    names = ["workspace-hub"]
    for line in Path(registry).read_text().splitlines():
        slug = line.split("#", 1)[0].strip()
        if not slug:
            continue
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", slug):
            raise ValueError("invalid repository slug")
        if slug in names:
            raise ValueError("duplicate repository slug")
        names.append(slug)
    if len(names) == 1:
        raise ValueError("empty repository registry")
    if execution_names is not None and names != execution_names:
        raise ValueError("registry changed between configuration and preflight")
    visited, missing = [], []
    for name in names:
        directory = Path(hub) if name == "workspace-hub" else Path(sibling_root) / name
        marker = directory / ".git"
        (visited if marker.is_dir() or marker.is_file() else missing).append(name)
    return {"expected": names, "visited": visited, "missing": missing}


def automation(path, bound, now=None):
    if not math.isfinite(bound) or bound <= 0:
        raise ValueError("a positive staleness bound in seconds is required")
    result = {"configured": "unknown", "liveness": "automation unavailable",
              "last_run": None, "staleness_bound_seconds": bound}
    try:
        state = json.loads(Path(path).read_text())
        if not isinstance(state, dict):
            raise TypeError("automation state must be an object")
        result["configured"] = state.get("configured", "unknown")
        result["last_run"] = state.get("last_run")
        if type(state.get("last_run")) not in (int, float):
            raise TypeError("last run must be numeric epoch seconds")
        age = (time.time() if now is None else now) - state["last_run"]
        if (state.get("gateway") is True and state.get("scheduler") is True
                and state.get("configured") is True and math.isfinite(age) and age >= 0):
            result["liveness"] = "recent" if age <= bound else "stale"
    except (OSError, ValueError, TypeError, KeyError):
        pass
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    check = commands.add_parser("coverage")
    check.add_argument("hub", type=Path)
    check.add_argument("siblings", type=Path)
    check.add_argument("registry", type=Path)
    check.add_argument("execution_names", nargs="*")
    live = commands.add_parser("automation")
    live.add_argument("state", type=Path)
    live.add_argument("bound", type=float)
    args = parser.parse_args()
    try:
        if args.command == "coverage":
            result = coverage(args.hub, args.siblings, args.registry,
                              args.execution_names or None)
            print(json.dumps(result))
            return bool(result["missing"])
        print(json.dumps(automation(args.state, args.bound)))
        return 0
    except (OSError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
