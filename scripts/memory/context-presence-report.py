#!/usr/bin/env python3
"""context-presence-report.py — report per-repo scoped-memory presence (epic #3082/#3084).

Scans sibling repos under a root and reports which carry their own
.claude/memory/ (scoped) vs which inherit only the global workspace-hub blob.
This is the baseline metric for `repos_scoped_memory` in the flywheel scorecard.

Usage: context-presence-report.py [--root /mnt/local-analysis]
"""
from __future__ import annotations
import argparse
import pathlib
import sys


def scan(root: pathlib.Path) -> dict:
    repos, scoped = [], []
    for child in sorted(root.iterdir()):
        if (child / ".git").exists():
            repos.append(child.name)
            if (child / ".claude" / "memory").is_dir():
                scoped.append(child.name)
    return {"total": len(repos), "scoped": scoped, "unscoped": [r for r in repos if r not in scoped]}


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="/mnt/local-analysis")
    args = ap.parse_args(argv)
    root = pathlib.Path(args.root)
    if not root.is_dir():
        print(f"root not found: {root}", file=sys.stderr)
        return 1
    r = scan(root)
    print(f"scoped-memory: {len(r['scoped'])}/{r['total']} repos")
    print(f"  scoped:   {', '.join(r['scoped']) or '(none)'}")
    print(f"  unscoped: {', '.join(r['unscoped']) or '(none)'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
