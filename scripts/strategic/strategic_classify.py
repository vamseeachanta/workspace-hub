#!/usr/bin/env python3
"""Classify a single WRK item into a strategic track and compute its score.

Usage: uv run --no-project python scripts/strategic/strategic-classify.py WRK-1200
"""

import argparse
import sys
from pathlib import Path

import yaml

# Allow importing the scoring engine
sys.path.insert(0, str(Path(__file__).parent))
from strategic_score import (
    calculate_enablement,
    classify_track,
    parse_wrk_frontmatter,
    score_rice,
    score_wsjf,
)


def find_wrk_file(wrk_id, repo_root):
    """Find a WRK file by ID in pending/ or archived/."""
    wq = repo_root / ".claude" / "work-queue"
    for subdir in ["pending", "archived"]:
        path = wq / subdir / f"{wrk_id}.md"
        if path.exists():
            return path
    return None


def main():
    parser = argparse.ArgumentParser(
        description="Classify a single WRK into a strategic track"
    )
    parser.add_argument("wrk_id", help="WRK ID (e.g. WRK-1200)")
    args = parser.parse_args()

    repo_root = Path(__file__).parents[2]
    config_dir = repo_root / "config" / "strategic-prioritization"

    with open(config_dir / "track-mapping.yaml") as f:
        track_mapping = yaml.safe_load(f)
    with open(config_dir / "scoring-weights.yaml") as f:
        weights = yaml.safe_load(f)

    path = find_wrk_file(args.wrk_id, repo_root)
    if not path:
        print(f"ERROR: {args.wrk_id} not found in pending/ or archived/")
        sys.exit(1)

    wrk = parse_wrk_frontmatter(path)
    if not wrk:
        print(f"ERROR: Could not parse frontmatter for {args.wrk_id}")
        sys.exit(1)

    category = wrk.get("category", "uncategorised")
    track = wrk.get("track") or classify_track(category, track_mapping)

    has_chain = bool(wrk.get("blocked_by")) or bool(wrk.get("deferred_to"))
    if has_chain:
        base = score_wsjf(wrk, weights)
        method = "wsjf"
    else:
        base = score_rice(wrk, weights)
        method = "rice"

    critical_ids = weights.get("roadmap_critical_ids", [])
    is_roadmap = wrk["id"] in critical_ids

    print(f"WRK:      {wrk['id']}")
    print(f"Title:    {wrk.get('title', 'N/A')}")
    print(f"Category: {category}")
    print(f"Track:    {track}")
    print(f"Method:   {method}")
    print(f"Base:     {base}")
    print(f"Roadmap:  {'yes (+15)' if is_roadmap else 'no'}")
    print(f"Priority: {wrk.get('priority', 'N/A')}")


if __name__ == "__main__":
    main()
