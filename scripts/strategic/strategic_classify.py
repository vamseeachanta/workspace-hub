#!/usr/bin/env python3
"""Classify a single GitHub issue into a strategic track and compute its score.

Usage: uv run --no-project python scripts/strategic/strategic-classify.py 3999
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

import yaml

# Allow importing the scoring engine
sys.path.insert(0, str(Path(__file__).parent))
from strategic_score import (
    classify_track,
    issue_to_work_item,
    score_rice,
    score_wsjf,
)


def fetch_issue(issue_id: str) -> dict | None:
    """Fetch one issue by number or #number."""
    issue_num = issue_id.lstrip("#")
    if not issue_num.isdigit():
        return None
    result = subprocess.run(
        [
            "gh", "-R", "vamseeachanta/workspace-hub", "issue", "view",
            issue_num, "--json", "number,title,labels,state",
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode != 0:
        return None
    return json.loads(result.stdout)


def main():
    parser = argparse.ArgumentParser(
        description="Classify a single GitHub issue into a strategic track"
    )
    parser.add_argument("issue", help="GitHub issue number (e.g. 3999)")
    args = parser.parse_args()

    repo_root = Path(__file__).parents[2]
    config_dir = repo_root / "config" / "strategic-prioritization"

    with open(config_dir / "track-mapping.yaml") as f:
        track_mapping = yaml.safe_load(f)
    with open(config_dir / "scoring-weights.yaml") as f:
        weights = yaml.safe_load(f)

    issue = fetch_issue(args.issue)
    if not issue:
        print(f"ERROR: issue {args.issue} not found via GitHub labels")
        sys.exit(1)

    wrk = issue_to_work_item(issue)

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

    print(f"Issue:    {wrk['id']}")
    print(f"Title:    {wrk.get('title', 'N/A')}")
    print(f"Category: {category}")
    print(f"Track:    {track}")
    print(f"Method:   {method}")
    print(f"Base:     {base}")
    print(f"Roadmap:  {'yes (+15)' if is_roadmap else 'no'}")
    print(f"Priority: {wrk.get('priority', 'N/A')}")


if __name__ == "__main__":
    main()
