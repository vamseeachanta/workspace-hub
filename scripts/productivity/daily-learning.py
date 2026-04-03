#!/usr/bin/env python3
"""Daily learning cadence — picks 2 tips, tracks progress, suggests hands-on practice.

Usage:
    uv run scripts/productivity/daily-learning.py              # Show today's tips
    uv run scripts/productivity/daily-learning.py --practice   # Show practice exercise
    uv run scripts/productivity/daily-learning.py --progress   # Show learning progress
    uv run scripts/productivity/daily-learning.py --categories # Show tips by category
    uv run scripts/productivity/daily-learning.py --all        # List all tips
"""
import sys
import os
import random
import hashlib
from datetime import datetime, timedelta
from pathlib import Path

# ── Config ──────────────────────────────────────────────────────────────────
WORKSPACE = os.environ.get("WORKSPACE_ROOT", "/mnt/local-analysis/workspace-hub")
CATALOG = Path(WORKSPACE) / "config/workflow-tips/tips-catalog.yaml"
HISTORY = Path(WORKSPACE) / "config/workflow-tips/tip-history.yaml"
PROGRESS = Path(WORKSPACE) / "config/workflow-tips/learning-progress.yaml"
NO_REPEAT_DAYS = 30
TIPS_PER_DAY = 2


def parse_tips_yaml(path):
    """Minimal YAML parser for tips catalog (avoids PyYAML dependency)."""
    tips = []
    current = {}
    with open(path) as f:
        for line in f:
            stripped = line.strip()
            if stripped.startswith("- id:"):
                if current:
                    tips.append(current)
                current = {"id": stripped.split(":", 1)[1].strip()}
            elif ":" in stripped and current and not stripped.startswith("#"):
                key, _, val = stripped.partition(":")
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                if key in ("category", "name", "oneliner", "try_it", "source", "added"):
                    current[key] = val
                elif key == "tags":
                    current["tags"] = val
    if current:
        tips.append(current)
    return tips


def parse_history_yaml(path):
    """Parse shown tip IDs with dates."""
    shown = {}  # id -> [dates]
    if not path.exists():
        return shown
    current_date = None
    with open(path) as f:
        for line in f:
            stripped = line.strip()
            if stripped.startswith("- date:"):
                current_date = stripped.split(":", 1)[1].strip()
            elif stripped.startswith("tips:") and current_date:
                ids_str = stripped.split("[", 1)[1].rstrip("]").strip()
                for tid in ids_str.split(","):
                    tid = tid.strip()
                    if tid:
                        shown.setdefault(tid, []).append(current_date)
    return shown


def parse_progress_yaml(path):
    """Parse learning progress: practiced tips and scores."""
    progress = {}
    if not path.exists():
        return progress
    current = {}
    with open(path) as f:
        for line in f:
            stripped = line.strip()
            if stripped.startswith("- id:"):
                if current and "id" in current:
                    progress[current["id"]] = current
                current = {"id": stripped.split(":", 1)[1].strip()}
            elif ":" in stripped and current:
                key, _, val = stripped.partition(":")
                current[key.strip()] = val.strip()
    if current and "id" in current:
        progress[current["id"]] = current
    return progress


def select_tips(tips, history, n=TIPS_PER_DAY):
    """Select tips not shown in last NO_REPEAT_DAYS, weighted toward newer tips."""
    cutoff = (datetime.now() - timedelta(days=NO_REPEAT_DAYS)).strftime("%Y-%m-%d")
    recent_ids = set()
    for tid, dates in history.items():
        for d in dates:
            if d >= cutoff:
                recent_ids.add(tid)

    eligible = [t for t in tips if t["id"] not in recent_ids]
    if len(eligible) < n:
        eligible = tips  # fallback: show any

    # Weight newer tips slightly higher
    today = datetime.now()
    weights = []
    for t in eligible:
        added = t.get("added", "2026-01-01")
        try:
            days_old = (today - datetime.strptime(added, "%Y-%m-%d")).days
        except ValueError:
            days_old = 180
        weight = max(1, 365 - days_old)  # newer = higher weight
        weights.append(weight)

    # Deterministic seed per date so same tips show all day
    seed = int(hashlib.md5(datetime.now().strftime("%Y-%m-%d").encode()).hexdigest()[:8], 16)
    rng = random.Random(seed)

    selected = []
    pool = list(zip(eligible, weights))
    for _ in range(min(n, len(pool))):
        total = sum(w for _, w in pool)
        r = rng.uniform(0, total)
        cumulative = 0
        for i, (tip, w) in enumerate(pool):
            cumulative += w
            if cumulative >= r:
                selected.append(tip)
                pool.pop(i)
                break
    return selected


def append_history(tips, path):
    """Append today's selections to history."""
    today = datetime.now().strftime("%Y-%m-%d")
    ids = ", ".join(t["id"] for t in tips)
    with open(path, "a") as f:
        f.write(f"  - date: {today}\n    tips: [{ids}]\n")


def generate_practice(tip):
    """Generate a hands-on practice exercise for a tip."""
    cat = tip.get("category", "")
    tid = tip.get("id", "")
    name = tip.get("name", "")
    try_it = tip.get("try_it", "")

    exercises = {
        "cc-powerup":     "Run /powerup and complete lesson #1 (Talk to your codebase). Note 1 thing you didn't know.",
        "cc-insights":    "Run /insights and read the full report. Write down the top friction point.",
        "cc-stats":       "Run /stats. How many sessions this week? What's your streak?",
        "cc-context":     "Run /context mid-session. Note what percentage you're at. If > 50%, run /compact.",
        "cc-simplify":    "After your next code change, run /simplify. Accept or reject each suggestion.",
        "cc-debug":       "Next time a test fails, try /debug instead of manual investigation.",
        "cc-diff":        "Run /diff right now. Use arrow keys to browse per-turn diffs.",
        "cc-security-review": "Run /security-review on your current branch. Any findings?",
        "cc-cost":        "Run /cost. How many tokens used this session? Compare to yesterday.",
        "cc-effort":      "Try /effort low for a quick question, then /effort high for planning.",
        "cc-compact-focus": "Run /compact focus on [your current task]. Compare to plain /compact.",
        "cc-branch-fork": "Before trying a risky approach, run /branch first. Explore freely.",
        "cc-rename-resume": "Run /rename with a descriptive name. Tomorrow, try /resume to find it.",
        "cc-rewind":      "Make a small change, then /rewind to undo it. Faster than Ctrl-Z.",
        "cc-loop":        "Set up /loop 10m /gsd:progress to auto-check your project status.",
        "cc-schedule-cloud": "Run /schedule to see the cloud task setup flow. Schedule a test task.",
        "cc-permissions":  "Run /permissions. Add one wildcard allow rule for your common commands.",
        "cc-sandbox":     "Run /sandbox to toggle on. Note how many fewer permission prompts you get.",
        "cc-doctor":      "Run /doctor. Fix any warnings it reports.",
        "cc-pr-comments":  "On a branch with a PR, run /pr-comments. Review inline.",
        "bp-compact-50pct": "Check /context now. If > 50%, practice the discipline: /compact immediately.",
        "bp-challenge-claude": "On your next PR, tell Claude: 'prove to me this works before I merge.'",
        "bp-squash-merge": "Check your repo settings: is squash merge enforced? If not, enable it.",
        "bp-skill-gotchas": "Pick one skill you use often. Add a ## Gotchas section with 2-3 known pitfalls.",
        "bp-skill-triggers": "Pick one skill. Rewrite its description as a trigger: 'Use when...'",
    }
    if tid in exercises:
        return exercises[tid]
    if try_it:
        return f"Try it now: {try_it}\nAfter running, note what you learned."
    return f"Explore the {name} feature. Spend 2 minutes trying it in your current session."


def show_daily_tips():
    """Main: show today's 2 tips with practice exercises."""
    tips = parse_tips_yaml(CATALOG)
    history = parse_history_yaml(HISTORY)
    selected = select_tips(tips, history)

    print("=" * 68)
    print(f"  DAILY LEARNING — {datetime.now().strftime('%A, %B %d, %Y')}")
    print("=" * 68)
    print()

    for i, tip in enumerate(selected, 1):
        cat = tip.get("category", "?")
        cat_label = {"claude-code": "CC", "ecosystem": "ECO", "gsd": "GSD", "practice": "PRACTICE"}.get(cat, cat.upper())
        print(f"  TIP {i} [{cat_label}] — {tip.get('name', '?')}")
        print(f"  {tip.get('oneliner', '')}")
        print(f"  Try it: {tip.get('try_it', 'N/A')}")
        print(f"  Source: {tip.get('source', 'N/A')}")
        print()
        print(f"  PRACTICE: {generate_practice(tip)}")
        print()
        print("-" * 68)
        print()

    append_history(selected, HISTORY)

    # Summary stats
    progress = parse_progress_yaml(PROGRESS)
    total_tips = len(tips)
    shown_unique = len(set(tid for tid in history))
    remaining = total_tips - shown_unique
    print(f"  Progress: {shown_unique}/{total_tips} tips seen")
    print(f"  ({remaining} remaining in rotation, {NO_REPEAT_DAYS}-day no-repeat window)")
    print(f"  Categories: {sum(1 for t in tips if t.get('category') == 'claude-code')} CC"
          f" | {sum(1 for t in tips if t.get('category') == 'ecosystem')} ECO"
          f" | {sum(1 for t in tips if t.get('category') == 'gsd')} GSD"
          f" | {sum(1 for t in tips if t.get('category') == 'practice')} PRACTICE")
    print()


def show_progress():
    """Show learning progress overview."""
    tips = parse_tips_yaml(CATALOG)
    history = parse_history_yaml(HISTORY)
    progress = parse_progress_yaml(PROGRESS)

    by_cat = {}
    for t in tips:
        cat = t.get("category", "other")
        by_cat.setdefault(cat, {"total": 0, "shown": 0})
        by_cat[cat]["total"] += 1
        if t["id"] in history:
            by_cat[cat]["shown"] += 1

    print("=" * 68)
    print("  LEARNING PROGRESS")
    print("=" * 68)
    print()
    print(f"  {'Category':<15} {'Seen':>5} / {'Total':>5}   {'Coverage':>8}")
    print(f"  {'-'*15} {'-'*5}   {'-'*5}   {'-'*8}")
    for cat in sorted(by_cat):
        d = by_cat[cat]
        pct = (d["shown"] / d["total"] * 100) if d["total"] > 0 else 0
        bar = "#" * int(pct / 5) + "." * (20 - int(pct / 5))
        print(f"  {cat:<15} {d['shown']:>5} / {d['total']:>5}   {pct:>6.0f}%  [{bar}]")
    print()

    total = sum(d["total"] for d in by_cat.values())
    shown = sum(d["shown"] for d in by_cat.values())
    pct = (shown / total * 100) if total > 0 else 0
    print(f"  Overall: {shown}/{total} ({pct:.0f}%)")
    days_to_complete = max(0, (total - shown)) // TIPS_PER_DAY
    print(f"  At {TIPS_PER_DAY} tips/day: ~{days_to_complete} days to full rotation")
    print()


def show_categories():
    """List all tips grouped by category."""
    tips = parse_tips_yaml(CATALOG)
    by_cat = {}
    for t in tips:
        by_cat.setdefault(t.get("category", "other"), []).append(t)

    for cat in sorted(by_cat):
        label = {"claude-code": "Claude Code Native", "ecosystem": "Ecosystem Commands",
                 "gsd": "GSD Framework", "practice": "Workflow Practices"}.get(cat, cat)
        print(f"\n  [{label}] ({len(by_cat[cat])} tips)")
        print(f"  {'-' * 50}")
        for t in by_cat[cat]:
            print(f"    {t['id']:<25} {t.get('name', '?')}")


def show_all():
    """List every tip with full details."""
    tips = parse_tips_yaml(CATALOG)
    for t in tips:
        print(f"  [{t.get('category', '?')}] {t['id']}")
        print(f"    {t.get('name', '?')}: {t.get('oneliner', '?')}")
        print(f"    Try: {t.get('try_it', 'N/A')}")
        print()


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--progress" in args:
        show_progress()
    elif "--categories" in args:
        show_categories()
    elif "--all" in args:
        show_all()
    elif "--practice" in args:
        # Show today's tips with extra practice focus
        show_daily_tips()
    else:
        show_daily_tips()
