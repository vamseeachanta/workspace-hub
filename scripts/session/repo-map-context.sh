#!/usr/bin/env bash
# repo-map-context.sh — Output repo-map entries for a WRK item's target_repos.
# Reads target_repos from WRK frontmatter, looks up each in repo-map.yaml.
# Non-blocking: always exits 0. workspace-hub is gracefully skipped.
# Usage: repo-map-context.sh [--wrk-file <path>] [--repo-map <path>]
#        If --wrk-file omitted: no-op; retired local WRK auto-detect is disabled.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo ".")"
WRK_FILE=""
REPO_MAP="${REPO_ROOT}/config/onboarding/repo-map.yaml"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --wrk-file)  WRK_FILE="$2"; shift 2 ;;
    --repo-map)  REPO_MAP="$2"; shift 2 ;;
    *) shift ;;
  esac
done

# Auto-detect active WRK if not specified. Retired: labels are queue truth.
if [[ -z "$WRK_FILE" ]]; then
  exit 0
fi

# Non-blocking: no WRK file or file missing → exit 0 silently
[[ -n "$WRK_FILE" ]] || exit 0
[[ -f "$WRK_FILE" ]] || exit 0
[[ -f "$REPO_MAP" ]] || exit 0

# Delegate to Python helper for parsing
uv run --no-project python "${SCRIPT_DIR}/repo-map-context.py" "$WRK_FILE" "$REPO_MAP" 2>/dev/null || true
exit 0
