#!/usr/bin/env bash
# refresh-fixtures.sh — Verify or document refresh process for Python-level fixture data
# Usage: refresh-fixtures.sh [--dry-run] [--repo <repo>]
#
# --dry-run (default): verify fixture JSON files exist and are valid JSON
# --repo <name>: only check fixtures for specified repo (default: assethold)
#
# When to refresh:
#   Run with --force-update when yfinance domain model changes (e.g., new API fields)
#   or when test assertions start failing due to fixture data being stale.
#
# How to update fixture data:
#   1. Identify which fixture file needs updating (tests/fixtures/data/*.json)
#   2. Run the live test once to observe the actual data structure:
#      cd assethold && uv run python -m pytest tests/modules/stocks/data/test_data_AAPL.py --noconftest -v
#   3. Update the JSON fixture file with the new expected shape
#   4. Re-run without live_data exclusion to verify:
#      cd assethold && uv run python -m pytest tests/ --noconftest -q

set -euo pipefail
REPO_ROOT="$(git rev-parse --show-toplevel)"
DRY_RUN=true
REPO="assethold"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run) DRY_RUN=true; shift ;;
        --repo) REPO="$2"; shift 2 ;;
        *) echo "Unknown arg: $1"; exit 1 ;;
    esac
done

FIXTURE_DIR="${REPO_ROOT}/${REPO}/tests/fixtures/data"

echo "=== refresh-fixtures.sh ==="
echo "Repo: ${REPO}"
echo "Fixture dir: ${FIXTURE_DIR}"
echo ""

if [[ ! -d "$FIXTURE_DIR" ]]; then
    echo "ERROR: fixture directory not found: $FIXTURE_DIR"
    exit 1
fi

# Verify all JSON files are valid
ERRORS=0
FOUND=0
for f in "${FIXTURE_DIR}"/*.json; do
    [[ -f "$f" ]] || continue
    FOUND=$((FOUND + 1))
    if uv run --no-project python -c "import json; json.load(open('$f'))" 2>/dev/null; then
        echo "  OK: $(basename $f)"
    else
        echo "  ERROR: invalid JSON: $(basename $f)"
        ERRORS=$((ERRORS + 1))
    fi
done

if [[ $FOUND -eq 0 ]]; then
    echo "  WARN: no fixture files found in $FIXTURE_DIR"
fi

if [[ $ERRORS -gt 0 ]]; then
    echo ""
    echo "FAIL: $ERRORS fixture file(s) have JSON errors"
    exit 1
fi

echo ""
echo "PASS: all fixture files are valid JSON (${FOUND} files checked)"
