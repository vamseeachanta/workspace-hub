#!/usr/bin/env python3
"""Explain changed paths as deterministic test-family selections; never run tests."""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import subprocess
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[2]


def load_families(path: Path) -> dict[str, list[str]]:
    families = json.loads(path.read_text(encoding="utf-8"))["families"]
    seen: set[str] = set()
    if not isinstance(families, dict):
        raise TypeError("Invalid family inventory")
    for family, paths in families.items():
        if not isinstance(family, str) or not isinstance(paths, list) or not paths:
            raise ValueError("Invalid family entry")
        for name in paths:
            if not isinstance(name, str):
                raise TypeError("Invalid test path")
            rel = PurePosixPath(name)
            if (rel.is_absolute() or ".." in rel.parts or name.startswith("-")
                    or "\\" in name or rel.as_posix() != name or name in seen):
                raise ValueError("Unsafe or duplicate test path")
            seen.add(name)
    return families


def load_rules(path: Path) -> list[dict]:
    rules = json.loads(path.read_text(encoding="utf-8"))["rules"]
    for rule in rules:
        if not rule.get("comment") or not rule.get("id") or not isinstance(rule["families"], list):
            raise ValueError("Each rule needs an id, comment and family targets")
        re.compile(rule["pattern"])
    if not rules or rules[-1]["id"] != "unmapped-code":
        raise ValueError("Rules need a final full-selection fallback")
    return rules


def select(changes: list[tuple[str, str]], families: dict, rules: list[dict]) -> dict:
    selected: set[str] = set()
    rows = []
    for status, path in changes:
        for rule in rules:
            match = re.fullmatch(rule["pattern"], path)
            if not match:
                continue
            targets = {target.format(**match.groupdict()) for target in rule["families"]}
            names = set(families) if "*" in targets else targets.intersection(families)
            rule_id = rule["id"]
            if targets and not names:
                names, rule_id = set(families), "unmapped-code"
            selected.update(names)
            rows.append({"status": status, "path": path, "rule": rule_id,
                         "families": sorted(names)})
            break
        else:
            raise ValueError("No rule matched a changed path")
    files = sorted({path for name in selected for path in families[name]})
    return {"paths": rows, "families": sorted(selected), "files": files,
            "file_count": len(files)}


def explain(result: dict) -> str:
    lines = []
    for row in result["paths"]:
        # Escape control characters in Git filenames without changing ordinary paths.
        path = row["path"].encode("unicode_escape").decode("ascii")
        lines.extend([f"{row['status']} {path}", f"  rule: {row['rule']}",
                      "  families: " + (", ".join(row["families"]) or "none")])
    command = shlex.join(["python", "-m", "pytest", "-q", "--", *result["files"]])
    lines.extend(["Selected families: " + (", ".join(result["families"]) or "none"),
                  f"Test files: {result['file_count']}",
                  "Pytest: " + (command if result["files"] else "none")])
    return "\n".join(lines) + "\n"


def parse_diff(raw: bytes) -> list[tuple[str, str]]:
    """Parse Git --name-status -z, retaining both sides of renames/copies.

    Source: git-diff manual, -z and --name-status (accessed 2026-10-22).
    """
    if not raw:
        return []
    if not raw.endswith(b"\0"):
        raise ValueError("Diff must be NUL terminated")
    fields = raw[:-1].decode("utf-8", errors="surrogateescape").split("\0")
    changes = []
    while fields:
        status = fields.pop(0)
        if not re.fullmatch(r"(?:[ACDMRTUXB]|[RC][0-9]+)", status):
            raise ValueError("Invalid diff status")
        count = 2 if status.startswith(("R", "C")) else 1
        if len(fields) < count or not all(fields[:count]):
            raise ValueError("Incomplete diff record")
        changes.extend((status, path) for path in fields[:count])
        del fields[:count]
    return changes


def git_changes(root: Path, base: str, head: str) -> list[tuple[str, str]]:
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    # --end-of-options prevents a user-supplied ref from becoming an option.
    result = subprocess.run(
        ["git", "diff", "--name-status", "-z", "--find-renames", "--end-of-options",
         f"{base}...{head}", "--"], cwd=root, env=env, capture_output=True, check=True,
    )
    return parse_diff(result.stdout)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["explain", "json"])
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--inventory", type=Path, default=Path("config/ci/hub-test-families.json"))
    parser.add_argument("--rules", type=Path, default=Path("config/ci/hub-test-rules.json"))
    parser.add_argument("--base", default="origin/main")
    parser.add_argument("--head", default="HEAD")
    parser.add_argument("--diff-file", type=Path, help="Read saved Git name-status -z bytes")
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        families = load_families(root / args.inventory)
        rules = load_rules(root / args.rules)
        changes = (parse_diff(args.diff_file.read_bytes()) if args.diff_file
                   else git_changes(root, args.base, args.head))
        result = select(changes, families, rules)
    except (ValueError, TypeError, KeyError, OSError, subprocess.CalledProcessError):
        parser.exit(1, "Selection failed: check refs, inventory, rules and diff format\n")
    print(explain(result) if args.command == "explain" else json.dumps(result, sort_keys=True), end="\n" if args.command == "json" else "")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
