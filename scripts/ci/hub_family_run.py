#!/usr/bin/env python3
"""Run hub test families in the project environment, one pytest process each.

Used by two workflows:

* ``pr-fast-gate.yml`` runs only the families selected by the changed paths
  (``--select-base``), so a pull request waits minutes, not hours. A path no
  family rule maps adds the core families in ``config/ci/fast-gate.json``
  instead of every family.
* ``main-full-run.yml`` runs every family (``--all``) once a day on main.

Each family runs in its own process so modules with the same basename in
different directories cannot collide. Exit status 5 (nothing collected, for
example a family whose only module skips at import) counts as a pass. Tests
listed in ``tests/quarantine.txt`` are marked xfail(strict=False) by the root
``conftest.py``; they still run and are reported, but they cannot fail the run.
The inventory is regenerated in memory so new test files are always covered.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NO_TESTS_COLLECTED = 5


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(f"{name}.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def plan(root: Path, base: str | None, head: str) -> tuple[dict[str, list[str]], str]:
    """Return the families to run and a one-line reason."""
    families = _load("hub_test_inventory").inventory(root)["families"]
    if base is None:
        return families, "all families (full run)"
    selector = _load("hub_test_select")
    rules = selector.load_rules(root / "config/ci/hub-test-rules.json")
    result = selector.select(selector.git_changes(root, base, head), families, rules)
    names = set()
    unmapped = [row["path"] for row in result["paths"] if row["rule"] == "unmapped-code"]
    for row in result["paths"]:
        if row["rule"] != "unmapped-code":
            names.update(row["families"])
    note = ""
    if unmapped:
        config = json.loads((root / "config/ci/fast-gate.json").read_text(encoding="utf-8"))
        names.update(config["unmapped_fallback"])
        note = (f"; {len(unmapped)} unmapped path(s) add the core fallback families"
                " (every family runs daily on main)")
    chosen = {name: families[name] for name in sorted(names) if name in families}
    return chosen, f"{len(chosen)} of {len(families)} families selected by changed paths{note}"


def run(root: Path, families: dict[str, list[str]], scratch: Path, junit_dir: Path | None,
        extra: list[str]) -> list[dict]:
    scratch.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    rows = []
    for family, paths in families.items():
        slug = family.replace("/", "_")
        cmd = [sys.executable, "-m", "pytest", "-q", "-rfE", "-p", "no:cacheprovider",
               "--basetemp", str(scratch / slug), *extra]
        if junit_dir is not None:
            junit_dir.mkdir(parents=True, exist_ok=True)
            cmd += ["--junitxml", str(junit_dir / f"{slug}.xml")]
        cmd += ["--", *paths]
        print(f"::group::{family} ({len(paths)} files)", flush=True)
        started = time.monotonic()
        code = subprocess.run(cmd, cwd=root, env=env, check=False).returncode
        seconds = time.monotonic() - started
        print("::endgroup::", flush=True)
        ok = code in (0, NO_TESTS_COLLECTED)
        if not ok:
            print(f"::error::Family {family} failed (pytest exit {code})", flush=True)
        rows.append({"family": family, "files": len(paths), "exit": code, "ok": ok,
                     "seconds": round(seconds, 1)})
    return rows


def summary(reason: str, rows: list[dict]) -> str:
    failed = [row for row in rows if not row["ok"]]
    lines = ["## Hub test families", "", f"{reason}; {len(failed)} failed.", ""]
    if rows:
        lines += ["| Family | Files | Exit | Seconds |", "|---|---:|---:|---:|"]
        lines += [f"| `{r['family']}` | {r['files']} | {r['exit']} | {r['seconds']} |" for r in rows]
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    scope = parser.add_mutually_exclusive_group(required=True)
    scope.add_argument("--all", action="store_true", help="Run every family")
    scope.add_argument("--select-base", help="Run families selected by base...head changes")
    parser.add_argument("--head", default="HEAD")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--scratch", type=Path, required=True)
    parser.add_argument("--junit-dir", type=Path)
    parser.add_argument("--json", type=Path, help="Write per-family results here")
    parser.add_argument("--plan-only", action="store_true", help="Print the selection and exit")
    parser.add_argument("pytest_args", nargs="*", help="Extra pytest arguments (after --)")
    args = parser.parse_args()
    root = args.root.resolve()
    scratch = args.scratch.resolve()
    if scratch.is_relative_to(root):
        parser.exit(2, "Scratch must be outside the repository\n")
    families, reason = plan(root, None if args.all else args.select_base, args.head)
    print(reason, flush=True)
    if args.plan_only:
        print(json.dumps(sorted(families), indent=1))
        return 0
    rows = run(root, families, scratch, args.junit_dir, args.pytest_args)
    text = summary(reason, rows)
    print(text)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with Path(os.environ["GITHUB_STEP_SUMMARY"]).open("a", encoding="utf-8") as handle:
            handle.write(text + "\n")
    if args.json:
        args.json.write_text(json.dumps(rows, indent=1) + "\n", encoding="utf-8")
    return 0 if all(row["ok"] for row in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
