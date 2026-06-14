#!/usr/bin/env python3
"""skill_sprawl_audit.py — NON-DESTRUCTIVE skill-retirement candidate audit.

Surfaces the skills tree's dead weight so the operator can review before any
retirement (#3062, harden-ecosystem epic #3058). Reads the scored telemetry in
.claude/state/skill-scores.yaml; moves/deletes NOTHING — emits a candidate list
+ archive-consolidation report. Mass retirement is a reviewed follow-up.

Retention rule (approved #3062 plan): a skill is a retirement CANDIDATE when
baseline_usage_rate < 0.05 AND calls_in_period < 10 (the existing skill-eval
threshold). framework_usage or child skills exempt it (structural).
"""
from __future__ import annotations

import argparse
import json
import os
import sys

try:
    import yaml
except ImportError:
    yaml = None

ARCHIVE_DIRS = [".claude/skills/_archive", ".claude/skills-archive", "_archive/skills"]


def select_candidates(skills, *, max_usage=0.05, max_calls=10):
    """skills: {name: {baseline_usage_rate, calls_in_period, framework_usage,
    child_skill_count, tier, path}}. Returns retirement candidates (sorted)."""
    out = []
    for name, s in skills.items():
        if s.get("framework_usage") or (s.get("child_skill_count") or 0) > 0:
            continue  # structural — never auto-retire
        if (s.get("baseline_usage_rate") or 0) < max_usage and (s.get("calls_in_period") or 0) < max_calls:
            out.append({
                "name": name,
                "path": s.get("path", "?"),
                "tier": s.get("tier", "?"),
                "usage": s.get("baseline_usage_rate", 0),
                "calls": s.get("calls_in_period", 0),
            })
    out.sort(key=lambda c: (c["usage"], c["calls"], c["name"]))
    return out


def tier_summary(skills):
    counts = {}
    for s in skills.values():
        counts[s.get("tier", "?")] = counts.get(s.get("tier", "?"), 0) + 1
    return counts


def audit_archives(root):
    rows = []
    for d in ARCHIVE_DIRS:
        p = os.path.join(root, d)
        if os.path.isdir(p):
            n = sum(1 for _ in _walk_skillmd(p))
            rows.append({"dir": d, "skill_md_files": n})
    return rows


def _walk_skillmd(p):
    for dp, _, fs in os.walk(p):
        for f in fs:
            if f == "SKILL.md":
                yield os.path.join(dp, f)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Non-destructive skill sprawl audit")
    ap.add_argument("--scores", default=".claude/state/skill-scores.yaml")
    ap.add_argument("--root", default=".")
    ap.add_argument("--max-usage", type=float, default=0.05)
    ap.add_argument("--max-calls", type=int, default=10)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    if yaml is None:
        print("PyYAML required: uv run --with pyyaml ...", file=sys.stderr)
        return 2
    data = yaml.safe_load(open(os.path.join(a.root, a.scores)))
    skills = data.get("skills", {})
    cands = select_candidates(skills, max_usage=a.max_usage, max_calls=a.max_calls)
    tiers = tier_summary(skills)
    archives = audit_archives(a.root)
    result = {
        "total_skills": len(skills),
        "tiers": tiers,
        "retirement_candidates": len(cands),
        "candidates": cands,
        "archive_trees": archives,
        "rule": f"usage<{a.max_usage} AND calls<{a.max_calls}; framework/parent skills exempt",
        "note": "NON-DESTRUCTIVE — review before retiring; archive (reversible), don't delete.",
    }
    if a.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"skills: {len(skills)} scored | tiers: {tiers}")
        print(f"retirement candidates: {len(cands)} (rule: {result['rule']})")
        print(f"archive trees ({len(archives)}, consolidate to one): "
              + ", ".join(f"{r['dir']}={r['skill_md_files']}" for r in archives))
    return 0


if __name__ == "__main__":
    sys.exit(main())
