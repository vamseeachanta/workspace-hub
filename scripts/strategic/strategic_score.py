#!/usr/bin/env python3
"""Strategic scoring engine for WRK prioritization.

Hybrid WSJF + RICE scoring with track balance penalties and bonuses.
Usage: uv run --no-project python scripts/strategic/strategic-score.py [--top N] [--dir DIR]
"""

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

from label_queue import gh_query_label_queue, issue_to_work_item


def parse_wrk_frontmatter(path):
    """Extract YAML frontmatter from a WRK markdown file."""
    path = Path(path)
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None
    end = text.find("---", 3)
    if end == -1:
        return None
    fm = yaml.safe_load(text[3:end])
    if not isinstance(fm, dict):
        return None
    # Normalize blocked_by to list
    blocked = fm.get("blocked_by")
    if blocked is None:
        fm["blocked_by"] = []
    elif not isinstance(blocked, list):
        fm["blocked_by"] = [blocked]
    return fm


def classify_track(category, mapping):
    """Map a WRK category to a strategic track."""
    tracks = mapping.get("tracks", {})
    for track_name, track_def in tracks.items():
        if category in track_def.get("categories", []):
            return track_name
    return "other"


def score_rice(wrk, weights):
    """RICE score for items without deadline/blocked_by chains.

    RICE = (Reach * Impact * Confidence) / Effort, normalized to 0-100.
    """
    rice = weights["rice"]
    priority = wrk.get("priority", "medium")
    complexity = wrk.get("complexity", "medium")
    status = wrk.get("status", "pending")

    reach = rice["priority_to_reach"].get(priority, 3)
    impact = rice["priority_to_impact"].get(priority, 3)
    confidence = rice["status_to_confidence"].get(status, 3)
    effort = rice["complexity_to_effort"].get(complexity, 3)

    raw = (reach * impact * confidence) / effort
    # Max possible: (5*5*5)/1 = 125
    max_raw = 125.0
    return round((raw / max_raw) * 100, 1)


def score_wsjf(wrk, weights):
    """WSJF score for items with deadlines or blocked_by chains.

    WSJF = Cost_of_Delay / Job_Size, normalized to 0-100.
    """
    wsjf = weights["wsjf"]
    priority = wrk.get("priority", "medium")
    complexity = wrk.get("complexity", "medium")
    blocked_by = wrk.get("blocked_by", [])

    biz_value = wsjf["priority_to_business_value"].get(priority, 3)
    time_crit = 0
    if wrk.get("deferred_to"):
        time_crit += wsjf["has_deadline_bonus"]
    if blocked_by:
        time_crit += wsjf["has_blockers_bonus"]

    cost_of_delay = biz_value + time_crit
    job_size = wsjf["complexity_to_job_size"].get(complexity, 3)

    raw = cost_of_delay / job_size
    # Max possible: (8+3+2)/1 = 13
    max_raw = 13.0
    return round((raw / max_raw) * 100, 1)


def calculate_enablement(wrk_id, all_wrks):
    """Count how many WRKs are blocked by this item."""
    count = 0
    for other_id, other in all_wrks.items():
        if wrk_id in other.get("blocked_by", []):
            count += 1
    return count


def calculate_track_balance(track_counts, targets):
    """Calculate actual vs target allocation per track."""
    total = sum(track_counts.values())
    balance = {}
    for track, target_pct in targets.items():
        actual = track_counts.get(track, 0)
        actual_pct = round((actual / total) * 100, 1) if total > 0 else 0
        delta = round(actual_pct - target_pct, 1)
        if delta > 2:
            status = "over_served"
        elif delta < -2:
            status = "under_served"
        else:
            status = "balanced"
        balance[track] = {
            "target_pct": target_pct,
            "actual_pct": actual_pct,
            "status": status,
            "delta": delta,
        }
    return balance


def apply_bonuses(base, wrk, critical_ids, enablement_count,
                  track_balance, track, weights):
    """Apply roadmap bonus, enablement bonus, and track penalty."""
    score = base

    # Roadmap bonus
    if wrk["id"] in critical_ids:
        score += weights["roadmap_bonus"]

    # Enablement bonus (capped)
    enable_bonus = min(
        enablement_count * weights["enablement_bonus_per_dep"],
        weights["enablement_bonus_cap"],
    )
    score += enable_bonus

    # Track penalty (over-served tracks penalized)
    delta = track_balance.get(track, {}).get("delta", 0)
    if delta > 0:
        score -= delta * weights["track_penalty_coefficient"]

    return max(score, 0)


def rank_wrks(wrk_dir, track_mapping, scoring_weights,
              include_archived=True):
    """Parse, score, and rank all WRK items in a directory."""
    wrk_dir = Path(wrk_dir)
    all_wrks = {}

    for p in sorted(wrk_dir.glob("WRK-*.md")):
        fm = parse_wrk_frontmatter(p)
        if fm and "id" in fm:
            all_wrks[fm["id"]] = fm

    if not all_wrks:
        return []

    # Build track counts for balance calculation
    track_counts = {}
    for wrk in all_wrks.values():
        cat = wrk.get("category", "uncategorised")
        if wrk.get("track"):
            t = wrk["track"]
        else:
            t = classify_track(cat, track_mapping)
        track_counts[t] = track_counts.get(t, 0) + 1

    targets = scoring_weights["track_targets"]
    balance = calculate_track_balance(track_counts, targets)
    critical_ids = scoring_weights.get("roadmap_critical_ids", [])

    ranked = []
    for wrk_id, wrk in all_wrks.items():
        ranked.append(rank_wrk_item(
            wrk_id, wrk, all_wrks, track_mapping,
            scoring_weights, balance, critical_ids,
        ))

    ranked.sort(key=lambda x: x["strategic_score"], reverse=True)
    return ranked


def rank_wrk_item(wrk_id, wrk, all_wrks, track_mapping,
                  scoring_weights, balance, critical_ids):
    cat = wrk.get("category", "uncategorised")
    track = wrk.get("track") or classify_track(cat, track_mapping)
    has_chain = bool(wrk.get("blocked_by")) or bool(wrk.get("deferred_to"))
    if has_chain:
        base = score_wsjf(wrk, scoring_weights)
        method = "wsjf"
    else:
        base = score_rice(wrk, scoring_weights)
        method = "rice"
    enablement = calculate_enablement(wrk_id, all_wrks)
    final = apply_bonuses(
        base=base, wrk=wrk, critical_ids=critical_ids,
        enablement_count=enablement, track_balance=balance,
        track=track, weights=scoring_weights,
    )
    delta = balance.get(track, {}).get("delta", 0)
    return {
        "id": wrk_id,
        "track": track,
        "strategic_score": round(final, 1),
        "score_breakdown": {
            "base": base,
            "roadmap": scoring_weights["roadmap_bonus"]
            if wrk_id in critical_ids else 0,
            "enablement": min(
                enablement * scoring_weights["enablement_bonus_per_dep"],
                scoring_weights["enablement_bonus_cap"],
            ),
            "track_penalty": round(
                -(delta * scoring_weights["track_penalty_coefficient"]), 1
            ) if delta > 0 else 0,
        },
        "scoring_method": method,
    }


def rank_issues(issues, track_mapping, scoring_weights):
    """Score GitHub issues from the label queue."""
    items = {
        item["id"]: item
        for item in (issue_to_work_item(issue) for issue in issues)
    }
    if not items:
        return []

    track_counts = {}
    for item in items.values():
        track = item.get("track") or classify_track(
            item.get("category", "uncategorised"),
            track_mapping,
        )
        track_counts[track] = track_counts.get(track, 0) + 1

    balance = calculate_track_balance(track_counts, scoring_weights["track_targets"])
    critical_ids = scoring_weights.get("roadmap_critical_ids", [])

    ranked = [
        rank_issue_item(item_id, item, track_mapping, scoring_weights,
                        balance, critical_ids)
        for item_id, item in items.items()
    ]

    ranked.sort(key=lambda x: x["strategic_score"], reverse=True)
    return ranked


def rank_issue_item(item_id, item, track_mapping, scoring_weights,
                    balance, critical_ids):
    track = item.get("track") or classify_track(
        item.get("category", "uncategorised"),
        track_mapping,
    )
    base = score_rice(item, scoring_weights)
    final = apply_bonuses(
        base=base,
        wrk=item,
        critical_ids=critical_ids,
        enablement_count=0,
        track_balance=balance,
        track=track,
        weights=scoring_weights,
    )
    delta = balance.get(track, {}).get("delta", 0)
    return {
        "id": item_id,
        "title": item.get("title", ""),
        "track": track,
        "strategic_score": round(final, 1),
        "score_breakdown": {
            "base": base,
            "roadmap": scoring_weights["roadmap_bonus"]
            if item_id in critical_ids else 0,
            "enablement": 0,
            "track_penalty": round(
                -(delta * scoring_weights["track_penalty_coefficient"]), 1
            ) if delta > 0 else 0,
        },
        "scoring_method": "rice",
        "source": "github-labels",
    }


def build_output(ranked, track_balance, top_n=None):
    """Build the full output dict."""
    if top_n:
        display = ranked[:top_n]
    else:
        display = ranked

    # Top 3 per track
    top_by_track = {}
    for item in ranked:
        t = item["track"]
        if t not in top_by_track:
            top_by_track[t] = []
        if len(top_by_track[t]) < 3:
            top_by_track[t].append(item["id"])

    # Recommendation
    rec = {}
    if ranked:
        best = ranked[0]
        rec = {
            "next_item": best["id"],
            "rationale": (
                f"{best['track'].title()} track. "
                f"Score {best['strategic_score']}. "
                f"Method: {best['scoring_method']}."
            ),
        }

    return {
        "generated_at": datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        ),
        "track_balance": track_balance,
        "ranked_items": display,
        "top_3_by_track": top_by_track,
        "recommendation": rec,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Strategic WRK scoring engine"
    )
    parser.add_argument(
        "--top", type=int, default=None,
        help="Show only top N items",
    )
    parser.add_argument(
        "--dir", type=str, default=None,
        help="Legacy WRK directory. Omit to read GitHub labels.",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).parents[2]
    config_dir = repo_root / "config" / "strategic-prioritization"

    with open(config_dir / "track-mapping.yaml") as f:
        track_mapping = yaml.safe_load(f)
    with open(config_dir / "scoring-weights.yaml") as f:
        scoring_weights = yaml.safe_load(f)

    if args.dir:
        wrk_dir = Path(args.dir)
        ranked = rank_wrks(wrk_dir, track_mapping, scoring_weights)
        all_wrks = {}
        for p in sorted(wrk_dir.glob("WRK-*.md")):
            fm = parse_wrk_frontmatter(p)
            if fm and "id" in fm:
                cat = fm.get("category", "uncategorised")
                t = fm.get("track") or classify_track(cat, track_mapping)
                all_wrks[t] = all_wrks.get(t, 0) + 1
    else:
        issues = gh_query_label_queue()
        ranked = rank_issues(issues, track_mapping, scoring_weights)
        all_wrks = {}
        for item in (issue_to_work_item(issue) for issue in issues):
            track = item.get("track") or classify_track(
                item.get("category", "uncategorised"),
                track_mapping,
            )
            all_wrks[track] = all_wrks.get(track, 0) + 1

    balance = calculate_track_balance(
        all_wrks, scoring_weights["track_targets"]
    )
    output = build_output(ranked, balance, args.top)
    print(yaml.dump(output, default_flow_style=False, sort_keys=False))


if __name__ == "__main__":
    main()
