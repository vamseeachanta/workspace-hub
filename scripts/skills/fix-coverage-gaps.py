#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""Fix skill coverage gaps by adding scripts: frontmatter to skills with known scripts.

Usage:
    uv run --no-project python scripts/skills/fix-coverage-gaps.py
    uv run --no-project python scripts/skills/fix-coverage-gaps.py --dry-run
"""

from __future__ import annotations

import argparse
import os
import re
import sys

import yaml

# Skills with direct script matches — path relative to .claude/skills/
FIXES = [
    {
        "skill": "_core/context-management/legal-sanity/SKILL.md",
        "match": "workspace-hub/legal-sanity",
        "scripts": ["scripts/legal/legal-sanity-scan.sh"],
    },
    {
        "skill": "workspace-hub/repo-sync/SKILL.md",
        "scripts": ["scripts/coordination/repo_sync_batch.sh"],
    },
    {
        "skill": "coordination/orchestration/agent-router/SKILL.md",
        "scripts": ["scripts/coordination/routing/route.sh"],
    },
    {
        "skill": "_core/core-planner/SKILL.md",
        "scripts": ["scripts/agents/plan.sh"],
    },
    {
        "skill": "_core/core-reviewer/SKILL.md",
        "scripts": ["scripts/agents/review.sh"],
    },
    {
        "skill": "workspace-hub/agent-teams/SKILL.md",
        "scripts": ["scripts/hooks/tidy-agent-teams.sh"],
    },
    {
        "skill": "workspace-hub/improve/SKILL.md",
        "scripts": ["scripts/improve/improve.sh"],
    },
    {
        "skill": "workspace-hub/ecosystem-terminology/SKILL.md",
        "scripts": ["scripts/improve/lib/ecosystem.sh"],
    },
    {
        "skill": "workspace-hub/session-end/SKILL.md",
        "scripts": ["scripts/agents/session.sh"],
    },
    {
        "skill": "development/data-pipeline-processor/SKILL.md",
        "scripts": ["scripts/data/pipeline/pipeline.py"],
    },
    {
        "skill": "coordination/workflows/usage-tracker/SKILL.md",
        "match": "development/bash/usage-tracker",
        "scripts": ["scripts/operations/monitoring/lib/usage_tracker.sh"],
    },
    {
        "skill": "workspace-hub/sync/SKILL.md",
        "scripts": ["scripts/cron-repository-sync.sh"],
    },
    {
        "skill": "workspace-hub/plan-mode/SKILL.md",
        "scripts": ["scripts/agents/plan.sh"],
    },
    {
        "skill": "coordination/workflows/legal-sanity-review/SKILL.md",
        "scripts": ["scripts/legal/legal-sanity-scan.sh"],
    },
    {
        "skill": "_core/context-management/data-validation-reporter/SKILL.md",
        "match": "workspace-hub/workspace/data-validation-reporter",
        "scripts": ["bulk_install.sh", "install_to_repo.sh"],
        "local": True,
    },
    {
        "skill": "_core/context-management/repo-readiness/SKILL.md",
        "match": "workspace-hub/workspace/repo-readiness",
        "scripts": ["check_readiness.sh", "bulk_readiness_check.sh"],
        "local": True,
    },
    {
        "skill": "workspace-hub/skill-sync/SKILL.md",
        "match": "workspace-hub/workspace/skill-learner",
        "scripts": ["analyze_commit.sh", "install_hook.sh"],
        "local": True,
    },
    {
        "skill": "data/doc-intelligence-promotion/md-to-pdf/SKILL.md",
        "scripts": ["md_to_pdf.py"],
        "local": True,
    },
]


def find_skill_path(skills_root: str, spec: dict) -> str | None:
    """Resolve skill path, trying spec path first then searching by name."""
    candidate = os.path.join(skills_root, spec["skill"])
    if os.path.exists(candidate):
        return candidate

    # Fallback: search by skill directory name
    skill_name = os.path.basename(os.path.dirname(spec["skill"]))
    for root, dirs, files in os.walk(skills_root):
        if "_diverged" in root or "incoming" in root:
            continue
        if os.path.basename(root) == skill_name and "SKILL.md" in files:
            return os.path.join(root, "SKILL.md")
    return None


def add_scripts_frontmatter(path: str, scripts: list[str], dry_run: bool) -> bool:
    """Add scripts: field to YAML frontmatter. Returns True if modified."""
    with open(path, encoding="utf-8") as f:
        content = f.read()

    # Already has scripts:
    if re.search(r"^scripts:", content, re.MULTILINE):
        return False

    stripped = content.lstrip()
    if not stripped.startswith("---"):
        return False

    end = stripped.find("---", 3)
    if end == -1:
        return False

    # Insert scripts: before closing ---
    fm_block = stripped[3:end]
    scripts_yaml = "scripts:\n" + "".join(f"  - {s}\n" for s in scripts)
    new_content = "---\n" + fm_block.rstrip() + "\n" + scripts_yaml + "---" + stripped[end + 3:]

    if dry_run:
        print(f"  [DRY RUN] Would add scripts: {scripts}")
        return True

    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Fix skill coverage gaps")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without applying")
    parser.add_argument("--skills-root", default=".claude/skills", help="Skills root dir")
    args = parser.parse_args()

    fixed = 0
    skipped = 0
    not_found = 0

    for spec in FIXES:
        path = find_skill_path(args.skills_root, spec)
        if not path:
            print(f"  NOT FOUND: {spec['skill']}")
            not_found += 1
            continue

        modified = add_scripts_frontmatter(path, spec["scripts"], args.dry_run)
        if modified:
            fixed += 1
            print(f"  FIXED: {path}")
        else:
            skipped += 1
            print(f"  SKIPPED (already has scripts:): {path}")

    print(f"\nSummary: {fixed} fixed, {skipped} skipped, {not_found} not found")
    return 0


if __name__ == "__main__":
    sys.exit(main())
