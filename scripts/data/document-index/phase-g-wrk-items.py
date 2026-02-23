#!/usr/bin/env python3
# ABOUTME: Phase G — Pre-seed repo-mission WRK items independent of document indexing (WRK-309)
# ABOUTME: Creates WRK items for known engineering gaps in Tier 1/2 repos

"""
Usage:
    python phase-g-wrk-items.py [--dry-run] [--repo REPO]
"""

import argparse
import logging
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import yaml

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

SCRIPT_DIR = Path(__file__).resolve().parent
HUB_ROOT = SCRIPT_DIR.parents[2]
WRK_QUEUE_DIR = HUB_ROOT / ".claude" / "work-queue"

REPO_MISSION_ITEMS = [
    # digitalmodel
    {"repo": "digitalmodel", "group": "G-1",
     "title": "Expand S-N curve library from 17 to 20 standards",
     "standards": ["BS 7608", "ISO 19902", "DNVGL-RP-C203"],
     "priority": "high"},
    {"repo": "digitalmodel", "group": "G-2",
     "title": "Structural module — jacket and topside analysis",
     "standards": ["API RP 2A", "ISO 19902"],
     "priority": "high"},
    {"repo": "digitalmodel", "group": "G-4",
     "title": "Pipeline and flexibles module — pressure containment",
     "standards": ["DNV-ST-F101", "API RP 1111"],
     "priority": "medium"},
    {"repo": "digitalmodel", "group": "G-5",
     "title": "CP module — sacrificial anode design full calcs",
     "standards": ["DNV-RP-B401"],
     "priority": "medium"},
    {"repo": "digitalmodel", "group": "G-6",
     "title": "CALM buoy mooring fatigue — spectral from OrcaFlex time-domain",
     "standards": ["DNVGL-RP-C205"],
     "priority": "medium"},
    # worldenergydata
    {"repo": "worldenergydata", "group": "G-3",
     "title": "NDBC buoy data ingestion for metocean wave scatter",
     "standards": [],
     "priority": "medium"},
    {"repo": "worldenergydata", "group": "G-7",
     "title": "Integrated web dashboard — Plotly Dash for BSEE and FDAS",
     "standards": [],
     "priority": "medium"},
    {"repo": "worldenergydata", "group": "G-8",
     "title": "Production forecasting — Arps decline curve exponential hyperbolic harmonic",
     "standards": [],
     "priority": "medium"},
    {"repo": "worldenergydata", "group": "G-9",
     "title": "Real-time EIA and IEA feed ingestion weekly",
     "standards": [],
     "priority": "medium"},
    {"repo": "worldenergydata", "group": "G-10",
     "title": "MAIB and NTSB incident correlation with USCG MISLE for root-cause taxonomy",
     "standards": [],
     "priority": "low"},
    {"repo": "worldenergydata", "group": "G-11",
     "title": "Field development economics — MIRR NPV with carbon cost sensitivity",
     "standards": [],
     "priority": "medium"},
    # assethold
    {"repo": "assethold", "group": "G-12",
     "title": "Fundamentals scoring — P/E P/B EV/EBITDA ranking from yfinance",
     "standards": [],
     "priority": "high"},
    {"repo": "assethold", "group": "G-13",
     "title": "Covered call analyser — option chain ingestion and premium yield calculator",
     "standards": [],
     "priority": "medium"},
    {"repo": "assethold", "group": "G-14",
     "title": "Risk metrics — VaR CVaR Sharpe ratio max drawdown per position and portfolio",
     "standards": [],
     "priority": "high"},
    {"repo": "assethold", "group": "G-15",
     "title": "Sector exposure tracker — auto-classify holdings by GICS sector flag concentration",
     "standards": [],
     "priority": "medium"},
    # cross-repo
    {"repo": "workspace-hub", "group": "G-16",
     "title": "Unified CLI — single ace command routing to all repo tools",
     "standards": [],
     "priority": "medium"},
    {"repo": "workspace-hub", "group": "G-17",
     "title": "Shared engineering constants library — material properties unit conversions seawater properties",
     "standards": [],
     "priority": "medium"},
    {"repo": "workspace-hub", "group": "G-18",
     "title": "Agent-readable specs index — YAML index of all specs consumable by AI agents",
     "standards": [],
     "priority": "medium"},
    # doris
    {"repo": "doris", "group": "D-1",
     "title": "Formalise calculation workflow — migrate ad-hoc calcs to Python modules",
     "standards": [],
     "priority": "medium"},
    {"repo": "doris", "group": "D-2",
     "title": "DNV-ST-F101 pressure containment checks — system pressure test MAOP validation",
     "standards": ["DNV-ST-F101"],
     "priority": "medium"},
    {"repo": "doris", "group": "D-3",
     "title": "API RP 1111 deepwater pipeline design checks — collapse propagating buckle",
     "standards": ["API RP 1111"],
     "priority": "medium"},
    {"repo": "doris", "group": "D-4",
     "title": "On-bottom stability module — DNV-RP-F109 soil resistance calculations",
     "standards": ["DNV-RP-F109"],
     "priority": "medium"},
    # OGManufacturing
    {"repo": "OGManufacturing", "group": "O-1",
     "title": "Establish repo structure — add README src specs tests scaffold",
     "standards": [],
     "priority": "high"},
    {"repo": "OGManufacturing", "group": "O-2",
     "title": "Production surveillance module — basic well KPI tracking GOR WCT PI",
     "standards": [],
     "priority": "medium"},
    {"repo": "OGManufacturing", "group": "O-3",
     "title": "Drilling engineering module — casing design checks burst collapse tension API TR 5C3",
     "standards": ["API TR 5C3"],
     "priority": "medium"},
    # saipem / rock-oil-field
    {"repo": "saipem", "group": "S-1",
     "title": "Portable installation analysis library — extract generic OrcaFlex automation from project code",
     "standards": [],
     "priority": "medium"},
    {"repo": "saipem", "group": "S-2",
     "title": "Vessel weather-window calculator — operability analysis from Hs Tp scatter",
     "standards": [],
     "priority": "medium"},
    # acma-projects
    {"repo": "acma-projects", "group": "A-1",
     "title": "LNG tank structural checks — API 620 and EN 14620 thin-shell hoop stress",
     "standards": ["API 620", "EN 14620"],
     "priority": "medium"},
    {"repo": "acma-projects", "group": "A-2",
     "title": "Aluminium structural module — Eurocode 9 and AA ADM member capacity checks",
     "standards": ["Eurocode 9"],
     "priority": "medium"},
    {"repo": "acma-projects", "group": "A-3",
     "title": "Composite panel design tool — Classical Laminate Theory CLT strength checks",
     "standards": [],
     "priority": "medium"},
    # pdf-large-reader review
    {"repo": "pdf-large-reader", "group": "P-1",
     "title": "Review pdf-large-reader vs native AI agent PDF capabilities — assess continuation or deprecation",
     "standards": [],
     "priority": "medium"},
]


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


def item_already_exists(group: str) -> bool:
    """Check if a WRK item for this group code already exists."""
    for subdir in ("pending", "archive", "working"):
        d = WRK_QUEUE_DIR / subdir
        if not d.exists():
            continue
        for f in d.iterdir():
            if not f.name.endswith(".md"):
                continue
            try:
                content = f.read_text(errors="replace")
                if f"group: {group}" in content or f"group: '{group}'" in content:
                    return True
            except OSError:
                continue
    return False


def generate_wrk_content(wrk_id: int, item: Dict) -> str:
    """Generate WRK item markdown with frontmatter and body."""
    now = datetime.now().isoformat(timespec="seconds") + "Z"
    group = item["group"]
    repo = item["repo"]
    title = item["title"]
    standards = item.get("standards", [])
    priority = item.get("priority", "medium")

    full_title = f"{group}: {title}"
    if len(full_title) > 80:
        full_title = full_title[:77] + "..."

    standards_block = ""
    if standards:
        std_lines = "\n".join(f"- {s}" for s in standards)
        standards_block = f"\n## Applicable Standards\n\n{std_lines}\n"

    std_criterion = ""
    if standards:
        std_criterion = "\n- [ ] Standard reference documented in code"

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
group: {group}
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

**Repo**: `{repo}`
**Group**: {group}
**Priority**: {priority}
{standards_block}
## Description

{title}.

## Why

Pre-seeded from WRK-309 Phase G repo-mission analysis. This item
represents a known capability gap identified from current repo state
and available standards/data sources.

## Acceptance Criteria

- [ ] Core implementation with unit tests
- [ ] Input validation at boundaries{std_criterion}
- [ ] Cross-review passed
"""


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Phase G: Pre-seed repo-mission WRK items (WRK-309)"
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="Show items without creating files")
    parser.add_argument("--repo", help="Filter items by repo")
    args = parser.parse_args()

    items = REPO_MISSION_ITEMS
    if args.repo:
        items = [i for i in items if i["repo"] == args.repo]
        if not items:
            logger.error("No items found for repo: %s", args.repo)
            return 1

    next_wrk = find_highest_wrk_number() + 1
    pending_dir = WRK_QUEUE_DIR / "pending"
    pending_dir.mkdir(parents=True, exist_ok=True)

    created = 0
    skipped = 0

    for item in items:
        group = item["group"]
        if item_already_exists(group):
            logger.info("Skipping %s: already exists", group)
            skipped += 1
            continue

        wrk_id = next_wrk + created
        content = generate_wrk_content(wrk_id, item)

        if args.dry_run:
            logger.info(
                "Would create WRK-%d: %s -- %s (%s)",
                wrk_id, group, item["title"], item["repo"],
            )
        else:
            out_path = pending_dir / f"WRK-{wrk_id}.md"
            out_path.write_text(content)
            logger.info("Created %s: %s", out_path.name, group)

        created += 1

    action = "would be created" if args.dry_run else "created"
    logger.info(
        "Phase G complete: %d items %s, %d skipped (already exist)",
        created, action, skipped,
    )
    if created > 0:
        logger.info(
            "WRK range: WRK-%d through WRK-%d", next_wrk, next_wrk + created - 1
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
