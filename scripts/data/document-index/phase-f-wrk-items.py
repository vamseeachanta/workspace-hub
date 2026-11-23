#!/usr/bin/env python3
# ABOUTME: Phase F — Create WRK items from document gaps identified in enhancement plan (WRK-309)
# ABOUTME: Reads enhancement-plan.yaml, creates pending WRK items for unimplemented standards

"""
Usage:
    python phase-f-wrk-items.py [--config config.yaml] [--repo REPO] [--dry-run] [--priority PRIO]
"""

import argparse
import logging
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

SCRIPT_DIR = Path(__file__).resolve().parent
HUB_ROOT = SCRIPT_DIR.parents[2]
DEFAULT_CONFIG = SCRIPT_DIR / "config.yaml"
WRK_QUEUE_DIR = HUB_ROOT / ".claude" / "work-queue"

TIER_1_REPOS = ["digitalmodel", "worldenergydata", "assethold"]


def load_config(config_path: Path) -> Dict[str, Any]:
    """Load pipeline configuration from YAML."""
    with open(config_path) as f:
        return yaml.safe_load(f)


def load_enhancement_plan(plan_path: Path) -> Dict[str, Any]:
    """Load enhancement plan YAML, or empty dict if absent (gaps not yet classified)."""
    if not plan_path.exists():
        logger.info("Enhancement plan not found — no gaps classified yet. Skipping gap WRK creation.")
        return {}
    with open(plan_path) as f:
        return yaml.safe_load(f) or {}


def find_highest_wrk_number() -> int:
    """Find the highest WRK-NNN number across all queue dirs."""
    highest = 0
    for subdir in ("pending", "archive", "working"):
        d = WRK_QUEUE_DIR / subdir
        if not d.exists():
            continue
        for f in d.iterdir():
            match = re.match(r"WRK-(\d+)\.md$", f.name)
            if match:
                num = int(match.group(1))
                if num > highest:
                    highest = num
    logger.info("Highest existing WRK number: %d", highest)
    return highest


def collect_gap_items(
    plan: Dict, repo_filter: Optional[str],
) -> List[Dict]:
    """Collect gap items from enhancement plan for Tier 1 repos."""
    items: List[Dict] = []
    by_domain = plan.get("by_domain", {})

    for domain_name, domain_data in by_domain.items():
        repos = domain_data.get("repos", [])
        for item in domain_data.get("items", []):
            if item.get("status") != "gap":
                continue
            for repo in repos:
                if repo not in TIER_1_REPOS:
                    continue
                if repo_filter and repo != repo_filter:
                    continue
                items.append({
                    "repo": repo,
                    "domain": domain_name,
                    "doc_number": item.get("doc_number", ""),
                    "title": item.get("title", ""),
                    "path": item.get("path", ""),
                })

    logger.info("Found %d gap items for WRK creation", len(items))
    return items


def generate_wrk_content(wrk_id: int, gap: Dict, priority: str) -> str:
    """Generate WRK item markdown content with frontmatter."""
    doc_num = gap["doc_number"]
    title_suffix = gap["title"]
    repo = gap["repo"]
    domain = gap["domain"]

    if doc_num:
        full_title = f"Implement {doc_num}: {title_suffix} in {repo}"
    else:
        full_title = f"Implement {title_suffix} in {repo}"
    if len(full_title) > 80:
        full_title = full_title[:77] + "..."

    now = datetime.now().isoformat(timespec="seconds") + "Z"

    return f"""---
id: WRK-{wrk_id}
title: "{full_title}"
status: pending
priority: {priority}
complexity: medium
compound: false
created_at: {now}
target_repos:
  - {repo}
commit:
spec_ref:
related:
  - WRK-309
blocked_by: []
synced_to: []
plan_reviewed: false
plan_approved: false
percent_complete: 0
brochure_status: n/a
---

# {full_title}

**Domain**: {domain}
**Repo**: {repo}
{f"**Standard**: {doc_num}" if doc_num else ""}

## Description

Implement engineering calculations from {doc_num or title_suffix} \
in the `{repo}` repository.

## Why

This standard was identified during Phase C classification as a gap --
the document exists on the drives but its content has not been
implemented or integrated into the target repo.

## Acceptance Criteria

- [ ] Core calculations implemented with tests
- [ ] Input validation at boundaries
- [ ] Example usage in docstring or test
- [ ] Cross-review passed
"""


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Phase F: WRK items from document gaps (WRK-309)"
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--repo", help="Create items for this repo only")
    parser.add_argument("--dry-run", action="store_true", help="Print without creating")
    parser.add_argument(
        "--priority", default="medium",
        choices=["high", "medium", "low"],
        help="Priority for created items (default: medium)",
    )
    args = parser.parse_args()

    cfg = load_config(args.config)
    plan_path = HUB_ROOT / cfg["output"]["enhancement_plan"]

    plan = load_enhancement_plan(plan_path)
    gap_items = collect_gap_items(plan, args.repo)

    if not gap_items:
        logger.info("No gap items found. Nothing to create.")
        return 0

    next_wrk = find_highest_wrk_number() + 1
    pending_dir = WRK_QUEUE_DIR / "pending"
    pending_dir.mkdir(parents=True, exist_ok=True)

    created = 0
    for gap in gap_items:
        wrk_id = next_wrk + created
        content = generate_wrk_content(wrk_id, gap, args.priority)

        if args.dry_run:
            logger.info(
                "Would create WRK-%d: %s (%s)",
                wrk_id, gap["doc_number"] or gap["title"], gap["repo"],
            )
        else:
            out_path = pending_dir / f"WRK-{wrk_id}.md"
            out_path.write_text(content)
            logger.info("Created %s", out_path.name)

        created += 1

    action = "would be created" if args.dry_run else "created"
    logger.info(
        "Phase F complete: %d WRK items %s (WRK-%d through WRK-%d)",
        created, action, next_wrk, next_wrk + created - 1,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
