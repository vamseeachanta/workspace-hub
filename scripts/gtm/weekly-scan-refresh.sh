#!/usr/bin/env bash
# weekly-scan-refresh.sh — Weekly GTM job market scan
# Scheduled: Monday 5AM UTC via cron (schedule-tasks.yaml: gtm-job-market-scan)
# Related: GitHub issues #1669, #1670, #1671
#
# What this does:
#   1. Pulls latest main
#   2. Runs the job market scanner (all 22 keywords + 30 career pages)
#   3. Generates dashboard, priority targets, new-this-week, trend report
#   4. Commits and pushes results to the PRIVATE repository that holds the
#      output directory (C19). Nothing is committed to this public repository.
#
# The output directory comes from the private overlay key
# outputs.job_market_dir (scripts/lib/private_overlay.py). The scanner resolves
# it and fails closed when it is unset, relative, missing or inside this
# repository; this wrapper then stops before scanning.
#
# The scanner tracks history across runs:
#   - cumulative-index.json persists all-time seen jobs
#   - new-this-week.md shows only NEW postings since last scan
#   - trend-report.md shows companies trending up/down in hiring
#   - Persistent openings (seen 2+ weeks) flagged as "consulting gold"

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "=== GTM Weekly Scan Refresh ==="
echo "Date: $(date -u +'%Y-%m-%d %H:%M:%S UTC')"
echo "Repo: $REPO_ROOT"

# 1. Ensure we're on main and up to date
cd "$REPO_ROOT"
git checkout main 2>/dev/null || true
git pull --ff-only origin main 2>/dev/null || true

# 2. Create log directory
mkdir -p "$REPO_ROOT/logs/gtm"

# 3. Find Python (prefer miniforge, fall back to system)
PYTHON=""
for candidate in \
    "$HOME/miniforge3/bin/python" \
    "$HOME/.local/bin/python3" \
    "$(command -v python3 2>/dev/null)" \
    "$(command -v python 2>/dev/null)"; do
    if [ -n "$candidate" ] && [ -x "$candidate" ]; then
        PYTHON="$candidate"
        break
    fi
done

if [ -z "$PYTHON" ]; then
    echo "ERROR: No Python found"
    exit 1
fi

echo "Python: $PYTHON"

# 4. Verify dependencies
$PYTHON -c "import requests; from bs4 import BeautifulSoup; print('deps ok')" || {
    echo "Installing dependencies..."
    $PYTHON -m pip install --quiet beautifulsoup4 requests lxml 2>/dev/null || true
}

# 5. Resolve the private output directory (fails closed), then run the scanner
OUT_DIR="$($PYTHON "$REPO_ROOT/scripts/gtm/job-market-scanner.py" --print-output-dir)" || {
    echo "ERROR: private output directory not configured (outputs.job_market_dir); nothing scanned"
    exit 2
}
REPO_REAL="$(cd "$REPO_ROOT" && pwd -P)"
OUT_REAL="$(cd "$OUT_DIR" && pwd -P)"
case "$OUT_REAL/" in
    "$REPO_REAL"/*)
        echo "ERROR: output directory lies inside this public repository; refusing"
        exit 2
        ;;
esac

echo ""
echo "Running job market scan..."
$PYTHON "$REPO_ROOT/scripts/gtm/job-market-scanner.py" --refresh --output-dir "$OUT_REAL"

# 6. Commit and push results in the private repository that holds OUT_DIR
echo ""
echo "Committing results to the private output repository..."
PRIVATE_ROOT="$(git -C "$OUT_REAL" rev-parse --show-toplevel 2>/dev/null)" || {
    echo "ERROR: output directory is not inside a git checkout; results left uncommitted"
    exit 2
}
case "$(cd "$PRIVATE_ROOT" && pwd -P)/" in
    "$REPO_REAL"/*)
        echo "ERROR: output repository is inside this public repository; refusing"
        exit 2
        ;;
esac

git -C "$PRIVATE_ROOT" add -- "$OUT_REAL" 2>/dev/null || true

if git -C "$PRIVATE_ROOT" diff --staged --quiet; then
    echo "No changes to commit (identical results to last scan)"
else
    DATE_STR=$(date -u +'%Y-%m-%d')
    # Extract counts from the dashboard for commit message
    TOTAL=$(grep -oP 'Total job postings found \| \*\*\K[0-9]+' \
        "$OUT_REAL/dashboard.md" 2>/dev/null || echo "?")
    COMPANIES=$(grep -oP 'Unique companies \| \*\*\K[0-9]+' \
        "$OUT_REAL/dashboard.md" 2>/dev/null || echo "?")

    git -C "$PRIVATE_ROOT" commit -m "chore(gtm): weekly job market scan refresh $DATE_STR

Scan: $TOTAL jobs across $COMPANIES companies" -- "$OUT_REAL"

    git -C "$PRIVATE_ROOT" push origin HEAD
    echo "✓ Pushed to the private output repository"
fi

echo ""
echo "=== GTM Weekly Scan Complete ==="
