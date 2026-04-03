#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""skill-usage-report.py — Skill usage tracking and tier classification (#1559).

Scans multiple data sources to classify skills into HOT/WARM/COLD/DEAD tiers
based on cross-references and git activity.

Data sources:
  1. .claude/state/skill-scores.yaml (if exists) — baseline_usage_rate, calls_in_period
  2. SKILL.md related_skills / see_also fields — cross-reference graph
  3. Git log — recent commit messages mentioning skill names (last 90 days)
  4. $skill-name invocation patterns in SKILL.md bodies

Tier classification:
  HOT:  referenced by 5+ other skills OR mentioned in recent git commits
  WARM: referenced by 2-4 other skills
  COLD: referenced by 1 other skill
  DEAD: 0 references AND not in any recent git commits (last 90 days)

Output:
  - JSON report to stdout
  - .claude/state/skill-usage-report/YYYY-MM-DD.json
  - .claude/state/skill-scores.yaml (created/updated)

Usage:
    uv run --no-project python scripts/skills/skill-usage-report.py [--skills-dir DIR] [--days N]

Always exits 0 (non-blocking).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import yaml


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_frontmatter(text: str) -> dict:
    """Extract YAML frontmatter from a SKILL.md file."""
    if not text.startswith("---"):
        return {}
    end = text.find("---", 3)
    if end == -1:
        return {}
    try:
        return yaml.safe_load(text[3:end]) or {}
    except yaml.YAMLError:
        return {}


def _skill_name_from_path(path: Path, skills_root: Path) -> str:
    """Derive skill name from directory path relative to skills root.

    Returns the leaf directory name (e.g. 'dspy', 'gsd-plan-phase').
    """
    rel = path.parent.relative_to(skills_root)
    return str(rel).replace(os.sep, "/")


# ---------------------------------------------------------------------------
# Data source: SKILL.md cross-references
# ---------------------------------------------------------------------------

def scan_skills(skills_dir: Path) -> dict[str, dict]:
    """Scan all SKILL.md files, returning {skill_name: {path, related_skills, see_also, body_refs}}.

    Excludes _archive/, _core/, and _internal/ directories.
    """
    skills: dict[str, dict] = {}

    for skill_md in sorted(skills_dir.rglob("SKILL.md")):
        parts = skill_md.parts
        if any(excluded in parts for excluded in {"_archive", "_core", "_internal"}):
            continue

        rel_path = str(skill_md.relative_to(skills_dir))
        # Skill name is the parent directory name
        skill_name = skill_md.parent.name
        # Full path for uniqueness
        full_rel = str(skill_md.parent.relative_to(skills_dir)).replace(os.sep, "/")

        try:
            text = skill_md.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        fm = _parse_frontmatter(text)

        # Extract related_skills (list of skill names)
        related = fm.get("related_skills") or []
        if isinstance(related, str):
            related = [related]
        related = [r.strip() for r in related if isinstance(r, str) and r.strip()]

        # Extract see_also (list)
        see_also = fm.get("see_also") or []
        if isinstance(see_also, str):
            see_also = [see_also]
        see_also = [s.strip() for s in see_also if isinstance(s, str) and s.strip()]

        # Extract $skill-name invocation references and markdown links from body text
        body_refs: list[str] = []
        body_match = re.findall(r'\$([a-z][a-z0-9_-]{2,})', text)
        for ref in body_match:
            if ref not in {"repo", "json", "file", "key", "message", "default",
                           "value", "output", "total", "path", "line", "dir",
                           "branch", "period", "input", "env", "count", "status",
                           "item", "text", "if", "endif", "score", "date",
                           "version", "text_lower", "service", "command",
                           "name", "url", "data", "response", "result", "args",
                           "config", "home", "user", "pwd", "shell", "null",
                           "true", "false", "index", "type", "mode", "format",
                           "error", "warning", "info", "debug", "log", "tmp",
                           "temp", "src", "dest", "target", "source", "origin",
                           "base", "root", "node", "port", "host", "api", "ref",
                           "tag", "label", "title", "body", "header", "footer",
                           "width", "height", "size", "color", "font", "image",
                           "video", "audio", "schema", "table", "column", "row",
                           "field", "record", "query", "param", "option", "flag"}:
                body_refs.append(ref)
        for label, link_target in re.findall(r'\[([^\]]+)\]\(([^)]+SKILL\.md)\)', text, flags=re.IGNORECASE):
            label_name = label.strip().replace('_', '-').lower()
            if label_name:
                body_refs.append(label_name)
            path_ref = Path(link_target)
            target_name = path_ref.parent.name.replace('_', '-').lower()
            if target_name:
                body_refs.append(target_name)

        child_skill_count = sum(
            1
            for child in skill_md.parent.rglob("SKILL.md")
            if child != skill_md and not any(excluded in child.parts for excluded in {"_archive", "_core", "_internal"})
        )

        canonical_name = str(fm.get("name", skill_name)).strip() or skill_name
        skills[full_rel] = {
            "name": canonical_name,
            "short_name": canonical_name.lower(),
            "path": rel_path,
            "full_rel": full_rel,
            "related_skills": related,
            "see_also": see_also,
            "body_refs": list(set(body_refs)),
            "child_skill_count": child_skill_count,
        }

    return skills


def build_reference_graph(skills: dict[str, dict]) -> dict[str, int]:
    """Count how many other skills reference each skill.

    Returns {skill_short_name: reference_count}.
    """
    # Build a set of all known short names and full paths for matching
    known_short_names: dict[str, list[str]] = defaultdict(list)
    for full_rel, info in skills.items():
        known_short_names[info["short_name"]].append(full_rel)

    ref_counts: dict[str, int] = defaultdict(int)

    for full_rel, info in skills.items():
        source_short = info["short_name"]
        referenced: set[str] = set()

        # related_skills references
        for ref in info["related_skills"]:
            ref_lower = ref.lower().strip()
            if ref_lower != source_short and ref_lower in known_short_names:
                referenced.add(ref_lower)

        # see_also references
        for ref in info["see_also"]:
            ref_lower = ref.lower().strip()
            if ref_lower != source_short and ref_lower in known_short_names:
                referenced.add(ref_lower)

        # body $skill-name references
        for ref in info["body_refs"]:
            ref_lower = ref.lower().strip()
            if ref_lower != source_short and ref_lower in known_short_names:
                referenced.add(ref_lower)

        for target in referenced:
            ref_counts[target] += 1

    return dict(ref_counts)


# ---------------------------------------------------------------------------
# Data source: git log
# ---------------------------------------------------------------------------

def scan_git_log(repo_dir: Path, days: int = 90) -> set[str]:
    """Scan git log for skill names mentioned in commit messages (last N days).

    Returns set of skill short names found in recent commits.
    """
    mentioned: set[str] = set()
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", f"--since={days} days ago", "--all"],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            return mentioned
        log_text = result.stdout
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return mentioned

    return log_text


def match_skills_in_git_log(log_text: str, skill_short_names: set[str]) -> set[str]:
    """Match skill names that appear in skill-scoped git log output."""
    mentioned: set[str] = set()
    if not log_text:
        return mentioned

    for line in log_text.lower().splitlines():
        if "skill" not in line and "/skills/" not in line and ".claude/skills" not in line:
            continue
        for name in skill_short_names:
            if len(name) < 4:
                continue
            pattern = rf'(?<![a-z0-9_-]){re.escape(name.lower())}(?![a-z0-9_-])'
            if re.search(pattern, line):
                mentioned.add(name)
    return mentioned


# ---------------------------------------------------------------------------
# Data source: skill-scores.yaml
# ---------------------------------------------------------------------------

def load_skill_scores(path: Path) -> dict[str, dict]:
    """Load existing skill-scores.yaml if it exists."""
    if not path.exists():
        return {}
    try:
        with path.open(encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return data.get("skills", {})
    except (yaml.YAMLError, OSError):
        return {}


# ---------------------------------------------------------------------------
# Tier classification
# ---------------------------------------------------------------------------

def classify_tiers(
    skills: dict[str, dict],
    ref_counts: dict[str, int],
    git_mentioned: set[str],
) -> dict[str, list[dict]]:
    """Classify skills into HOT/WARM/COLD/DEAD tiers.

    HOT:  referenced by 5+ other skills OR mentioned in recent git commits
    WARM: referenced by 2-4 other skills
    COLD: referenced by 1 other skill
    DEAD: 0 references AND not in any recent git commits
    """
    tiers: dict[str, list[dict]] = {
        "hot": [],
        "warm": [],
        "cold": [],
        "dead": [],
    }

    for full_rel, info in skills.items():
        short_name = info["short_name"]
        refs = ref_counts.get(short_name, 0)
        child_skill_count = int(info.get("child_skill_count", 0) or 0)
        effective_refs = max(refs, child_skill_count)
        in_git = short_name in git_mentioned
        framework_usage = short_name.startswith("gsd-")

        entry = {
            "skill": short_name,
            "path": info["full_rel"],
            "reference_count": refs,
            "child_skill_count": child_skill_count,
            "effective_reference_count": effective_refs,
            "in_recent_commits": in_git,
            "framework_usage": framework_usage,
        }

        if effective_refs >= 5 or in_git:
            entry["tier"] = "hot"
            tiers["hot"].append(entry)
        elif effective_refs >= 2 or framework_usage:
            entry["tier"] = "warm"
            tiers["warm"].append(entry)
        elif effective_refs == 1:
            entry["tier"] = "cold"
            tiers["cold"].append(entry)
        else:
            entry["tier"] = "dead"
            tiers["dead"].append(entry)

    # Sort each tier by reference count descending
    for tier in tiers.values():
        tier.sort(key=lambda x: (-x["reference_count"], x["skill"]))

    return tiers


# ---------------------------------------------------------------------------
# Output: skill-scores.yaml
# ---------------------------------------------------------------------------

def generate_skill_scores(
    skills: dict[str, dict],
    ref_counts: dict[str, int],
    tiers: dict[str, list[dict]],
    existing_scores: dict[str, dict],
) -> dict:
    """Generate skill-scores.yaml data from usage report."""
    # Build a tier lookup
    tier_lookup: dict[str, str] = {}
    for tier_name, entries in tiers.items():
        for entry in entries:
            tier_lookup[entry["skill"]] = tier_name

    # Compute baseline_usage_rate from effective discoverability counts
    effective_ref_values = [max(ref_counts.get(info["short_name"], 0), int(info.get("child_skill_count", 0) or 0)) for info in skills.values()]
    max_refs = max(effective_ref_values) if effective_ref_values else 1
    if max_refs == 0:
        max_refs = 1

    skills_data: dict[str, dict] = {}
    for full_rel, info in skills.items():
        short_name = info["short_name"]
        refs = ref_counts.get(short_name, 0)
        child_skill_count = int(info.get("child_skill_count", 0) or 0)
        effective_refs = max(refs, child_skill_count)
        tier = tier_lookup.get(short_name, "dead")

        # Merge with existing scores if available
        existing = existing_scores.get(short_name, {})

        framework_usage = short_name.startswith("gsd-")
        skills_data[short_name] = {
            "baseline_usage_rate": round(effective_refs / max_refs, 4) if max_refs > 0 else 0.0,
            "calls_in_period": existing.get("calls_in_period", effective_refs),
            "reference_count": refs,
            "child_skill_count": child_skill_count,
            "effective_reference_count": effective_refs,
            "framework_usage": framework_usage,
            "tier": tier,
            "path": info["full_rel"],
        }

    return {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "total_skills": len(skills_data),
        "skills": dict(sorted(skills_data.items())),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="Skill usage tracking and tier classification")
    parser.add_argument("--skills-dir", default=".claude/skills", help="Skills directory")
    parser.add_argument("--days", type=int, default=90, help="Git log lookback in days")
    parser.add_argument("--scores-file", default=".claude/state/skill-scores.yaml", help="Skill scores YAML")
    parser.add_argument("--output-dir", default=".claude/state/skill-usage-report", help="Output directory")
    args = parser.parse_args()

    repo_root = Path.cwd()
    skills_dir = repo_root / args.skills_dir
    scores_file = repo_root / args.scores_file
    output_dir = repo_root / args.output_dir

    if not skills_dir.is_dir():
        print(f"WARN: Skills directory not found: {skills_dir}")
        return 0

    # --- Step 1: Scan all SKILL.md files ---
    print(f"Scanning skills in {skills_dir} ...")
    skills = scan_skills(skills_dir)
    print(f"  Found {len(skills)} skills (excluding _archive)")

    # --- Step 2: Build reference graph ---
    ref_counts = build_reference_graph(skills)
    total_refs = sum(ref_counts.values())
    skills_with_refs = sum(1 for v in ref_counts.values() if v > 0)
    print(f"  Cross-references: {total_refs} total, {skills_with_refs} skills have >=1 reference")

    # --- Step 3: Scan git log ---
    short_names = {info["short_name"] for info in skills.values()}
    log_text = scan_git_log(repo_root, days=args.days)
    if isinstance(log_text, str):
        git_mentioned = match_skills_in_git_log(log_text, short_names)
    else:
        git_mentioned = log_text  # already a set from error path
    print(f"  Git mentions (last {args.days} days): {len(git_mentioned)} skills")

    # --- Step 4: Load existing skill scores ---
    existing_scores = load_skill_scores(scores_file)
    if existing_scores:
        print(f"  Existing skill-scores.yaml: {len(existing_scores)} entries")

    # --- Step 5: Classify tiers ---
    tiers = classify_tiers(skills, ref_counts, git_mentioned)
    print(f"\nTier Classification:")
    print(f"  HOT:  {len(tiers['hot'])} skills")
    print(f"  WARM: {len(tiers['warm'])} skills")
    print(f"  COLD: {len(tiers['cold'])} skills")
    print(f"  DEAD: {len(tiers['dead'])} skills")

    # --- Step 6: Build report ---
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    date_str = timestamp[:10]

    report = {
        "generated_at": timestamp,
        "total_skills": len(skills),
        "git_lookback_days": args.days,
        "summary": {
            "hot": len(tiers["hot"]),
            "warm": len(tiers["warm"]),
            "cold": len(tiers["cold"]),
            "dead": len(tiers["dead"]),
        },
        "hot": tiers["hot"],
        "warm": tiers["warm"],
        "cold": tiers["cold"],
        "dead": tiers["dead"],
    }

    # Write JSON report
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / f"{date_str}.json"
    tmp = report_path.with_suffix(".tmp")
    tmp.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.rename(report_path)
    print(f"\nReport written: {report_path}")

    # --- Step 7: Generate/update skill-scores.yaml ---
    scores_data = generate_skill_scores(skills, ref_counts, tiers, existing_scores)
    scores_file.parent.mkdir(parents=True, exist_ok=True)
    scores_tmp = scores_file.with_suffix(".tmp")
    with scores_tmp.open("w", encoding="utf-8") as f:
        yaml.dump(scores_data, f, default_flow_style=False, sort_keys=False, width=120)
    scores_tmp.rename(scores_file)
    print(f"Scores written: {scores_file} ({scores_data['total_skills']} skills)")

    # --- Step 8: Print top skills ---
    print("\nTop 10 HOT skills:")
    for entry in tiers["hot"][:10]:
        git_flag = " [git]" if entry["in_recent_commits"] else ""
        print(f"  {entry['skill']}: {entry['reference_count']} refs{git_flag} ({entry['path']})")

    print(f"\nTop 10 DEAD skills (candidates for retirement):")
    for entry in tiers["dead"][:10]:
        print(f"  {entry['skill']}: {entry['reference_count']} refs ({entry['path']})")

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(0)  # Always exit 0 (non-blocking)
