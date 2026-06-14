#!/usr/bin/env python3
"""skill_archive_audit.py — audit the skill ARCHIVE trees for consolidation.

Scoped complement to existing retirement tooling: retirement-candidate selection
already lives in scripts/skills/check_retirement_candidates.py (same threshold)
fed by scripts/skills/skill-usage-report.py. This tool covers the gap those don't
— the multiple archive trees that duplicate each other and bloat the skills
surface (#3062, harden-ecosystem epic #3058). NON-DESTRUCTIVE.

It enumerates each archive tree, counts SKILL.md, resolves symlinks, and
fingerprints each tree's relative-path set so true duplicates (vs symlinks vs
distinct content) are distinguishable before any consolidation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

ARCHIVE_DIRS = [".claude/skills/_archive", ".claude/skills-archive", "_archive/skills"]


def _skillmd_relpaths(root_dir):
    rels = []
    for dp, _, fs in os.walk(root_dir):
        for f in fs:
            if f == "SKILL.md":
                rels.append(os.path.relpath(os.path.join(dp, f), root_dir))
    return sorted(rels)


def audit_archives(root, archive_dirs=ARCHIVE_DIRS):
    """Return per-tree {dir, exists, is_symlink, realpath, skill_md, fingerprint}."""
    rows = []
    for d in archive_dirs:
        p = os.path.join(root, d)
        if not os.path.isdir(p):
            rows.append({"dir": d, "exists": False})
            continue
        rels = _skillmd_relpaths(p)
        fp = hashlib.sha256("\n".join(rels).encode()).hexdigest()[:16]
        rows.append({
            "dir": d,
            "exists": True,
            "is_symlink": os.path.islink(p),
            "realpath": os.path.realpath(p),
            "skill_md": len(rels),
            "fingerprint": fp,
        })
    return rows


def duplicate_groups(rows):
    """Group existing trees whose SKILL.md relative-path sets are identical."""
    groups = {}
    for r in rows:
        if r.get("exists"):
            groups.setdefault(r["fingerprint"], []).append(r["dir"])
    return [dirs for dirs in groups.values() if len(dirs) > 1]


def main(argv=None):
    ap = argparse.ArgumentParser(description="Non-destructive skill archive-tree audit")
    ap.add_argument("--root", default=".")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    rows = audit_archives(a.root)
    dups = duplicate_groups(rows)
    result = {
        "archive_trees": rows,
        "duplicate_groups": dups,
        "note": "NON-DESTRUCTIVE. Retirement candidates: see scripts/skills/check_retirement_candidates.py. "
                "Consolidate duplicate groups to a single convention with a dated manifest.",
    }
    if a.json:
        print(json.dumps(result, indent=2))
    else:
        for r in rows:
            if r.get("exists"):
                tag = " (symlink)" if r["is_symlink"] else ""
                print(f"{r['dir']}: {r['skill_md']} SKILL.md fp={r['fingerprint']}{tag}")
            else:
                print(f"{r['dir']}: absent")
        if dups:
            for g in dups:
                print(f"DUPLICATE (identical SKILL.md set): {', '.join(g)} -> consolidate")
        else:
            print("no identical-content duplicate trees")
    return 0


if __name__ == "__main__":
    sys.exit(main())
