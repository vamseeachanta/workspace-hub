#!/usr/bin/env python3
"""
WRK-386: Automated Gap-to-WRK Generator
Reads specs/capability-map/<repo>.yaml for each tier-1 repo, finds all
entries with status: gap, loads Phase B summaries, and generates scoped
WRK items written to .claude/work-queue/pending/WRK-NNN.md.

Usage:
    python phase-f-gap-wrk-generator.py [--dry-run] [--max N] [--repo REPO]
"""

import argparse
import json
import logging
import re
import sys
from datetime import datetime, timezone
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
WORKSPACE = SCRIPT_DIR.parents[2]

CAP_MAP_DIR = WORKSPACE / "specs" / "capability-map"
SUMMARIES_DIR = WORKSPACE / "data" / "document-index" / "summaries"
PENDING_DIR = WORKSPACE / ".claude" / "work-queue" / "pending"
WORK_QUEUE_DIR = WORKSPACE / ".claude" / "work-queue"

TIER_1_REPOS = ["digitalmodel", "worldenergydata", "assetutilities", "assethold"]

WRK_TEMPLATE = """\
---
id: {wrk_id}
title: "feat({repo}/{module}): implement {standard_id_short} — {title_short}"
status: pending
priority: {priority}
complexity: {complexity}
compound: false
created_at: {created_at}
target_repos:
  - {repo}
commit:
spec_ref:
related:
  - WRK-386
blocked_by: []
synced_to: []
plan_reviewed: false
plan_approved: false
percent_complete: 0
brochure_status: n/a
computer: ace-linux-1
---

# feat({module}): implement {standard_id_short}

## Standard
- **ID**: {standard_id}
- **Title**: {standard_title}
- **Org**: {org}
- **Document**: `{doc_path}` (SHA: `{sha_display}`)
- **Summary**: {summary_text}
- **Discipline**: {discipline}

## Target Module
- **Repo**: {repo}
- **Module**: `{module}`
- **Current status**: gap (no implementation found)
- **Capability tier target**: Tier 1 (deterministic calculation)

## What to Implement
{what_to_implement}

## Acceptance Criteria
- [ ] Function implements {standard_id_short} calculation
- [ ] Unit tests cover nominal and edge cases
- [ ] Result validated against worked example in standard (if available)
- [ ] Module registry updated: status → implemented

## Agentic AI Horizon
- Standards implementation is direct engineering value: agents can invoke
  {standard_id_short} calculations in automated workflows
- **Disposition: invest now** — engineering standards code is foundational
  and non-perishable
"""


def find_highest_wrk_number() -> int:
    """Find highest WRK-NNN number across all work queue subdirectories."""
    highest = 0
    for subdir in ("pending", "done", "working", "archive"):
        queue_subdir = WORK_QUEUE_DIR / subdir
        if not queue_subdir.exists():
            continue
        for f in queue_subdir.glob("WRK-*.md"):
            match = re.match(r"WRK-(\d+)\.md$", f.name)
            if match:
                num = int(match.group(1))
                if num > highest:
                    highest = num
    logger.info("Highest existing WRK number: %d", highest)
    return highest


def strip_sha_prefix(sha: str) -> str:
    """Strip 'sha256:' prefix from SHA string if present."""
    return sha.replace("sha256:", "").strip()


def load_summary(sha: str) -> Optional[Dict[str, Any]]:
    """Load Phase B summary JSON for a given SHA.

    The SHA may be either 16, 32, or 64 hex characters (after stripping prefix).
    Summary files are named <sha_hex>.json.
    """
    sha_hex = strip_sha_prefix(sha)
    if not sha_hex:
        return None
    summary_path = SUMMARIES_DIR / f"{sha_hex}.json"
    if summary_path.exists():
        try:
            return json.loads(summary_path.read_text())
        except (json.JSONDecodeError, OSError) as exc:
            logger.debug("Could not load summary %s: %s", summary_path.name, exc)
    return None


def assess_complexity(standard_id: str, title: str) -> str:
    """Heuristic: estimate implementation complexity from standard ID and title."""
    combined = (standard_id + " " + title).lower()
    high_markers = ["code of practice", "design code", "dnv-st", "api rp", "api std"]
    medium_markers = ["guideline", "dnv-rp", "technical report", "api tr", "recommended"]
    if any(marker in combined for marker in high_markers):
        return "high"
    if any(marker in combined for marker in medium_markers):
        return "medium"
    return "low"


def assess_priority(repo: str, discipline: str) -> str:
    """Assign priority based on repo tier and engineering discipline."""
    key_disciplines = {
        "structural", "pipeline", "marine", "installation", "geotechnical",
        "pressure", "mechanical",
    }
    if repo in ("digitalmodel", "assetutilities") and discipline.lower() in key_disciplines:
        return "high"
    return "medium"


def extract_entries_from_cap_map(cap_map: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract a flat list of standard entries from a capability-map YAML.

    The cap-map structure is:
        modules:
          - module: <name>
            standards:
              - id: ...
                status: gap|covered
    """
    all_entries = []
    modules = cap_map.get("modules", [])
    if isinstance(modules, dict):
        modules = list(modules.values())

    for mod_block in modules:
        if not isinstance(mod_block, dict):
            continue
        module_name = mod_block.get("module", "unknown")
        for standard in mod_block.get("standards", []):
            if not isinstance(standard, dict):
                continue
            entry = dict(standard)
            entry["module"] = module_name
            all_entries.append(entry)

    return all_entries


def truncate(text: str, max_len: int) -> str:
    """Truncate text to max_len characters, appending ellipsis if truncated."""
    if not text:
        return ""
    text = text.strip()
    if len(text) <= max_len:
        return text
    return text[:max_len - 3] + "..."


def build_wrk_item(
    wrk_id_num: int,
    repo: str,
    entry: Dict[str, Any],
    summary_data: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    """Build a dict of template variables for one WRK item."""
    standard_id = entry.get("id", entry.get("standard_id", "UNKNOWN"))
    module = entry.get("module", "unknown")
    sha_raw = entry.get("sha", "")
    sha_hex = strip_sha_prefix(sha_raw)
    sha_display = (sha_hex[:16] + "...") if len(sha_hex) > 16 else sha_hex

    title = entry.get("title", standard_id)
    discipline = entry.get("discipline", "engineering")

    # Use Phase B summary data when available, fall back to cap-map summary field
    if summary_data:
        summary_text = summary_data.get("summary", "") or entry.get("summary", "")
        doc_path = summary_data.get("path", entry.get("path", ""))
        org = summary_data.get("org", "") or entry.get("org", "")
    else:
        summary_text = entry.get("summary", "")
        doc_path = entry.get("path", "")
        org = entry.get("org", "")

    # Truncate for display
    title_short = truncate(title, 50)
    # standard_id_short: strip the long title part if id is actually a title
    standard_id_short = truncate(standard_id, 40)
    summary_short = truncate(summary_text, 200)
    what_to_implement = (
        truncate(summary_text, 400)
        or f"Implement {standard_id} as specified in the standard document."
    )

    return {
        "wrk_id": f"WRK-{wrk_id_num}",
        "repo": repo,
        "module": module,
        "standard_id": standard_id,
        "standard_id_short": standard_id_short,
        "title_short": title_short,
        "standard_title": truncate(title, 120),
        "org": org or "unknown",
        "doc_path": doc_path,
        "sha_display": sha_display,
        "summary_text": summary_short,
        "discipline": discipline,
        "priority": assess_priority(repo, discipline),
        "complexity": assess_complexity(standard_id, title),
        "what_to_implement": what_to_implement,
        "created_at": datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def collect_gap_items(
    repo_filter: Optional[str],
    max_items: int,
) -> List[Dict[str, Any]]:
    """Walk all tier-1 capability maps and collect gap entries."""
    if not CAP_MAP_DIR.exists():
        logger.warning("Capability-map directory not found: %s", CAP_MAP_DIR)
        return []

    cap_files = sorted(CAP_MAP_DIR.glob("*.yaml"))
    if not cap_files:
        logger.warning("No YAML files found in %s", CAP_MAP_DIR)
        return []

    next_id = find_highest_wrk_number() + 1
    items: List[Dict[str, Any]] = []

    for cap_file in cap_files:
        repo = cap_file.stem
        if repo_filter and repo != repo_filter:
            continue
        if repo not in TIER_1_REPOS:
            logger.info("Skipping non-tier-1 repo: %s", repo)
            continue

        try:
            cap_map = yaml.safe_load(cap_file.read_text()) or {}
        except yaml.YAMLError as exc:
            logger.error("Failed to parse %s: %s", cap_file.name, exc)
            continue

        logger.info(
            "Processing %s (%d total standards mapped)",
            repo,
            cap_map.get("total_standards_mapped", 0),
        )

        entries = extract_entries_from_cap_map(cap_map)
        gap_entries = [e for e in entries if e.get("status") == "gap"]
        logger.info("  Found %d gap entries in %s", len(gap_entries), repo)

        for entry in gap_entries:
            if len(items) >= max_items:
                logger.info("Reached max_items limit (%d), stopping.", max_items)
                return items

            sha_raw = entry.get("sha", "")
            summary_data = load_summary(sha_raw) if sha_raw else None

            wrk_item = build_wrk_item(
                wrk_id_num=next_id + len(items),
                repo=repo,
                entry=entry,
                summary_data=summary_data,
            )
            items.append(wrk_item)

    return items


def wrk_content(item: Dict[str, Any]) -> str:
    """Render WRK markdown from template variables."""
    return WRK_TEMPLATE.format(**item)


def run(dry_run: bool, max_items: int, repo_filter: Optional[str]) -> int:
    """Main execution: collect gaps, generate WRK items, write files."""
    logger.info(
        "Gap-to-WRK generator starting (dry_run=%s, max=%d)", dry_run, max_items
    )

    items = collect_gap_items(repo_filter=repo_filter, max_items=max_items)

    if not items:
        logger.info("No gap items found. Nothing to generate.")
        return 0

    logger.info("Found %d gap items to convert to WRK items", len(items))

    if dry_run:
        print(f"\nDRY RUN — {len(items)} WRK items would be created:\n")
        for item in items:
            print(
                f"  {item['wrk_id']}: [{item['repo']}/{item['module']}] "
                f"{item['standard_id_short']} (priority={item['priority']}, "
                f"complexity={item['complexity']})"
            )
        return 0

    PENDING_DIR.mkdir(parents=True, exist_ok=True)
    written = 0
    skipped = 0

    for item in items:
        out_path = PENDING_DIR / f"{item['wrk_id']}.md"
        if out_path.exists():
            logger.debug("Skipping %s — already exists", out_path.name)
            skipped += 1
            continue
        out_path.write_text(wrk_content(item))
        logger.info("Wrote %s", out_path.name)
        written += 1

    first_id = items[0]["wrk_id"] if items else "N/A"
    last_id = items[-1]["wrk_id"] if items else "N/A"
    logger.info(
        "Done: %d written, %d skipped (%s through %s) → %s",
        written,
        skipped,
        first_id,
        last_id,
        PENDING_DIR,
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="WRK-386: Generate WRK items from capability-map gap entries"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print WRK items that would be created without writing files",
    )
    parser.add_argument(
        "--max",
        type=int,
        default=50,
        metavar="N",
        help="Maximum number of WRK items to generate per run (default: 50)",
    )
    parser.add_argument(
        "--repo",
        metavar="REPO",
        help="Process only this repo's capability map (e.g. digitalmodel)",
    )
    args = parser.parse_args()

    return run(dry_run=args.dry_run, max_items=args.max, repo_filter=args.repo)


if __name__ == "__main__":
    sys.exit(main())
