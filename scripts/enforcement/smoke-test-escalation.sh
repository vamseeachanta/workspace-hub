#!/usr/bin/env bash
# smoke-test-escalation.sh — Escalate persistent smoke test failures
# Issue: #1428 — Nyquist verification gates
#
# Scans session-signals for consecutive smoke test failures per repo.
# If a repo has failed N+ consecutive days, outputs a warning with
# the failure streak. Can be run by cron or manually.
#
# Usage:
#   bash scripts/enforcement/smoke-test-escalation.sh [--threshold N] [--json]
#
# Default threshold: 3 consecutive failures before escalation.

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
SIGNAL_DIR="${REPO_ROOT}/.claude/state/session-signals"
THRESHOLD=3
JSON_MODE=false

for arg in "$@"; do
  case "$arg" in
    --threshold) shift; THRESHOLD="${1:-3}" ;;
    --json) JSON_MODE=true ;;
  esac
done

if [[ ! -d "$SIGNAL_DIR" ]]; then
  echo "[smoke-escalation] No session-signals directory found."
  exit 0
fi

# Extract smoke test results, group by repo, find streaks
uv run --no-project python - "$SIGNAL_DIR" "$THRESHOLD" "$JSON_MODE" <<'PYTHON'
import sys, json, os, glob
from collections import defaultdict
from datetime import datetime

signal_dir = sys.argv[1]
threshold = int(sys.argv[2])
json_mode = sys.argv[3] == "True"

# Parse all smoke test events
smoke_tests = []
for f in sorted(glob.glob(os.path.join(signal_dir, "*.jsonl"))):
    with open(f) as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except:
                continue
            if d.get("event") == "smoke_test":
                smoke_tests.append(d)

# Group by repo and date, find consecutive failure streaks
repo_results = defaultdict(list)
for t in smoke_tests:
    repo = t.get("repo", "unknown")
    ts = t.get("ts", "")
    status = t.get("status", "unknown")
    date = ts[:10] if ts else "unknown"
    repo_results[repo].append({"date": date, "status": status})

# Calculate current consecutive failure streak per repo
escalations = []
for repo, results in sorted(repo_results.items()):
    # Deduplicate by date (take worst status per day)
    by_date = {}
    fail_statuses = {"fail", "timeout", "error"}
    for r in results:
        d = r["date"]
        if d not in by_date or r["status"] in fail_statuses:
            by_date[d] = r["status"]

    # Count consecutive failures from most recent
    sorted_dates = sorted(by_date.keys(), reverse=True)
    streak = 0
    last_fail_date = None
    first_fail_date = None
    for date in sorted_dates:
        if by_date[date] in fail_statuses:
            streak += 1
            if last_fail_date is None:
                last_fail_date = date
            first_fail_date = date
        else:
            break

    if streak >= threshold:
        escalations.append({
            "repo": repo,
            "consecutive_failures": streak,
            "first_failure": first_fail_date,
            "last_failure": last_fail_date,
            "total_tests": len(results),
        })

if json_mode:
    print(json.dumps({"threshold": threshold, "escalations": escalations}, indent=2))
else:
    if not escalations:
        print(f"[smoke-escalation] No repos with {threshold}+ consecutive failures. All clear.")
    else:
        print(f"[smoke-escalation] {len(escalations)} repo(s) with {threshold}+ consecutive smoke test failures:")
        print()
        for e in escalations:
            print(f"  ESCALATION: {e['repo']}")
            print(f"    Consecutive failures: {e['consecutive_failures']}")
            print(f"    Failure period: {e['first_failure']} to {e['last_failure']}")
            print(f"    Total smoke tests recorded: {e['total_tests']}")
            print()
        print(f"[smoke-escalation] Action required: investigate test runner in these repos.")
        print(f"[smoke-escalation] Failures show passed=0 failed=0 — likely test discovery/runner crash.")

sys.exit(1 if escalations else 0)
PYTHON
