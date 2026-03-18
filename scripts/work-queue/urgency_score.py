#!/usr/bin/env python3
"""Compute urgency scores for WRK items.

Usage:
  python urgency_score.py WRK-NNN        # score single item
  python urgency_score.py --all          # score all pending, sorted
  python urgency_score.py --all --json   # JSON output
"""
import argparse, json, os, re, sys
from datetime import datetime, timezone

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
QUEUE_DIR = os.path.join(REPO_ROOT, ".claude", "work-queue")
WEIGHTS_PATH = os.path.join(REPO_ROOT, "config", "work-queue", "urgency-weights.yaml")

def parse_weights(path):
    defaults = {"priority": {"high": 6.0, "medium": 3.9, "low": 1.8},
                "blocking_count": 8.0, "age_factor": 2.0,
                "blocked_penalty": -5.0, "has_checkpoint": 4.0, "due_proximity": 12.0}
    if not os.path.isfile(path):
        return defaults
    text = open(path).read()
    weights = dict(defaults)
    pri = {}
    for m in re.finditer(r"^\s+(high|medium|low):\s*([\d.+-]+)", text, re.M):
        pri[m.group(1)] = float(m.group(2))
    if pri:
        weights["priority"] = pri
    for key in ("blocking_count", "age_factor", "blocked_penalty",
                "has_checkpoint", "due_proximity"):
        m = re.search(rf"^{key}:\s*([\d.+-]+)", text, re.M)
        if m:
            weights[key] = float(m.group(1))
    return weights

def get_field(text, field):
    m = re.search(rf"^{field}:\s*(.+)", text, re.M)
    return m.group(1).strip().strip('"').strip("'") if m else ""

def parse_list_field(text, field):
    raw = get_field(text, field)
    if not raw or raw == "[]":
        return []
    return [s.strip() for s in raw.strip("[]").split(",") if s.strip()]

def _parse_date(s):
    s = s.split(".")[0]
    for fmt in ("%Y-%m-%d %H:%M:%S%z", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(s.strip(), fmt)
            return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None

def score_priority(priority_str, weights):
    return weights.get("priority", {}).get(priority_str.lower(), 0.0)

def score_age(created_at_str, weights, now=None):
    if not created_at_str:
        return 0.0
    now = now or datetime.now(timezone.utc)
    dt = _parse_date(created_at_str)
    if not dt:
        return 0.0
    days = max((now - dt).days, 0)
    return min(days / 30.0, 10.0) * weights.get("age_factor", 2.0) / 10.0

def score_blocking_count(wrk_id, all_files_text, weights):
    count = sum(1 for _, t in all_files_text if wrk_id in parse_list_field(t, "blocked_by"))
    return count * weights.get("blocking_count", 8.0)

def score_blocked(blocked_by_list, weights, archive_dirs=None):
    if not blocked_by_list:
        return 0.0
    if archive_dirs is None:
        archive_dirs = [os.path.join(QUEUE_DIR, d) for d in ("archive", "archived")]
    for dep in blocked_by_list:
        num = re.search(r"\d+", dep)
        if not num:
            continue
        if not any(os.path.isfile(os.path.join(a, f"WRK-{num.group()}.md")) for a in archive_dirs):
            return weights.get("blocked_penalty", -5.0)
    return 0.0

def score_checkpoint(wrk_id, weights, queue_dir=None):
    cp = os.path.join(queue_dir or QUEUE_DIR, "assets", wrk_id, "checkpoint.yaml")
    return weights.get("has_checkpoint", 4.0) if os.path.isfile(cp) else 0.0

def score_due(due_date_str, weights, now=None):
    if not due_date_str:
        return 0.0
    now = now or datetime.now(timezone.utc)
    dt = _parse_date(due_date_str)
    if not dt:
        return 0.0
    days_until = (dt - now).days
    factor = weights.get("due_proximity", 12.0)
    if days_until <= 0:
        return factor
    return 0.0 if days_until >= 30 else factor * (30 - days_until) / 30.0

def compute_score(wrk_id, text, weights, all_files_text, queue_dir=None, now=None):
    qd = queue_dir or QUEUE_DIR
    blocked_by = parse_list_field(text, "blocked_by")
    archive_dirs = [os.path.join(qd, d) for d in ("archive", "archived")]
    bd = {
        "priority": score_priority(get_field(text, "priority"), weights),
        "age": round(score_age(get_field(text, "created_at"), weights, now), 1),
        "blocking": score_blocking_count(wrk_id, all_files_text, weights),
        "blocked": score_blocked(blocked_by, weights, archive_dirs),
        "checkpoint": score_checkpoint(wrk_id, weights, qd),
        "due": round(score_due(get_field(text, "due_date"), weights, now), 1),
    }
    return round(sum(bd.values()), 1), bd

def scan_wrk_files(queue_dir=None):
    qd = queue_dir or QUEUE_DIR
    results = []
    for subdir in ("pending", "blocked"):
        d = os.path.join(qd, subdir)
        if not os.path.isdir(d):
            continue
        for fn in os.listdir(d):
            if fn.endswith(".md") and fn.startswith("WRK-"):
                fp = os.path.join(d, fn)
                results.append((fp, open(fp).read()))
    return results

def score_all(queue_dir=None, now=None):
    qd = queue_dir or QUEUE_DIR
    weights = parse_weights(WEIGHTS_PATH)
    all_files = scan_wrk_files(qd)
    results = []
    for fp, text in all_files:
        wid = get_field(text, "id")
        if not wid:
            continue
        total, bd = compute_score(wid, text, weights, all_files, qd, now=now)
        results.append({"id": wid, "score": total, "breakdown": bd})
    results.sort(key=lambda x: x["score"], reverse=True)
    return results

def main():
    ap = argparse.ArgumentParser(description="WRK urgency scores")
    ap.add_argument("wrk_id", nargs="?", help="WRK-NNN to score")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--queue-dir", help="Override queue directory")
    args = ap.parse_args()
    qd = args.queue_dir or QUEUE_DIR
    if args.all:
        results = score_all(qd)
        if args.json:
            json.dump(results, sys.stdout, indent=2)
            print()
        else:
            for r in results:
                parts = [f"{k}={v}" for k, v in r["breakdown"].items() if v != 0]
                print(f"{r['id']:<12} {r['score']:>6.1f}  [{', '.join(parts)}]")
        return
    if not args.wrk_id:
        ap.error("Provide WRK-NNN or --all")
    weights = parse_weights(WEIGHTS_PATH)
    all_files = scan_wrk_files(qd)
    target = next((t for _, t in all_files if get_field(t, "id") == args.wrk_id), None)
    if target is None:
        print(f"Error: {args.wrk_id} not found in pending/blocked", file=sys.stderr)
        sys.exit(1)
    total, bd = compute_score(args.wrk_id, target, weights, all_files, qd)
    parts = [f"{k}={v}" for k, v in bd.items() if v != 0]
    print(f"{args.wrk_id}  {total:.1f}  [{', '.join(parts)}]")

if __name__ == "__main__":
    main()
