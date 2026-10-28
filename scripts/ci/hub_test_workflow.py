#!/usr/bin/env python3
"""Plan and execute the advisory workflow without embedding paths in shell code."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def selector_module():
    spec = importlib.util.spec_from_file_location("hub_select", Path(__file__).with_name("hub_test_select.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def matrix_plan(selected: list[str], health: dict, policy: dict) -> dict:
    included, excluded = [], {}
    for family in sorted(selected):
        row = health["families"].get(family)
        if not row:
            excluded[family] = "NOT_EVALUATED: no collection evidence"
        elif row["collection_status"] != "COLLECTABLE":
            excluded[family] = "NOT_GATING: " + row.get("error", "collection failed")
        elif row["body_status"] != "EVALUATED" or family not in policy["body_evaluated"]:
            excluded[family] = "NOT_EVALUATED: body effects not reviewed"
        else:
            included.append({"family": family})
    return {"matrix": {"include": included}, "required": bool(included), "excluded": excluded}


def aggregate_ok(discover: str, family: str, required: bool) -> bool:
    return discover == "success" and (family == "success" or (not required and family == "skipped"))


def run_family(root: Path, family: str, scratch: Path) -> int:
    selector = selector_module()
    families = selector.load_families(root / "config/ci/hub-test-families.json")
    health = json.loads((root / "config/ci/hub-test-health.json").read_text())
    policy = json.loads((root / "config/ci/hub-test-policy.json").read_text())
    if family not in families or not matrix_plan([family], health, policy)["required"]:
        raise ValueError("Family lacks collection evidence or evaluated body policy")
    paths = families[family]
    if not all((root / path).resolve().is_relative_to(root) and (root / path).is_file() for path in paths):
        raise ValueError("Family has a missing or escaping test path")
    if scratch.is_relative_to(root):
        raise ValueError("Scratch must be outside the repository")
    scratch.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    return subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
                           "--basetemp", str(scratch / "pytest"), "--", *paths],
                          cwd=root, env=env, check=False).returncode


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("plan")
    p.add_argument("--base", required=True)
    p.add_argument("--head", default="HEAD")
    p.add_argument("--root", type=Path, default=ROOT)
    p = sub.add_parser("run")
    p.add_argument("--family", required=True)
    p.add_argument("--root", type=Path, default=ROOT)
    p.add_argument("--scratch", type=Path, required=True)
    p = sub.add_parser("aggregate")
    p.add_argument("--discover", required=True)
    p.add_argument("--family", required=True)
    p.add_argument("--required", choices=["true", "false", ""], required=True)
    args = parser.parse_args()
    if args.command == "aggregate":
        return 0 if aggregate_ok(args.discover, args.family, args.required == "true") else 1
    try:
        root = args.root.resolve()
        if args.command == "run":
            return run_family(root, args.family, args.scratch.resolve())
        selector = selector_module()
        families = selector.load_families(root / "config/ci/hub-test-families.json")
        rules = selector.load_rules(root / "config/ci/hub-test-rules.json")
        changes = selector.git_changes(root, args.base, args.head)
        selection = selector.select(changes, families, rules)
        health = json.loads((root / "config/ci/hub-test-health.json").read_text())
        policy = json.loads((root / "config/ci/hub-test-policy.json").read_text())
        plan = matrix_plan(selection["families"], health, policy)
        print("matrix=" + json.dumps(plan["matrix"], separators=(",", ":")))
        print("required=" + str(plan["required"]).lower())
        summary = os.environ.get("GITHUB_STEP_SUMMARY")
        if summary:
            with Path(summary).open("a", encoding="utf-8") as handle:
                handle.write("## Advisory hub test selection\n\n")
                handle.write(f"Selected families: {len(selection['families'])}; runnable: {len(plan['matrix']['include'])}.\n\n")
                handle.writelines(f"- `{family}`: {reason}\n" for family, reason in plan["excluded"].items())
        return 0
    except (OSError, ValueError, TypeError, KeyError, subprocess.CalledProcessError):
        parser.exit(1, "Family workflow failed: check refs, inventory, health and policy\n")


if __name__ == "__main__":
    raise SystemExit(main())
