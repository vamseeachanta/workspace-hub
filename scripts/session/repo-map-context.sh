#!/usr/bin/env bash
# repo-map-context.sh — Output repo-map entries for a WRK item's target_repos.
# Reads target_repos from WRK frontmatter, looks up each in repo-map.yaml.
# Non-blocking: always exits 0. workspace-hub is gracefully skipped.
# Usage: repo-map-context.sh [--wrk-file <path>] [--repo-map <path>]
#        If --wrk-file omitted: auto-detects sole active WRK from working/ dir.
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

# Auto-detect active WRK if not specified
if [[ -z "$WRK_FILE" ]]; then
  WORKING_DIR="${REPO_ROOT}/.claude/work-queue/working"
  if [[ -d "$WORKING_DIR" ]]; then
    mapfile -t WORKING_FILES < <(find "$WORKING_DIR" -maxdepth 1 -name "WRK-*.md" 2>/dev/null | sort)
    if [[ ${#WORKING_FILES[@]} -eq 1 ]]; then
      WRK_FILE="${WORKING_FILES[0]}"
    fi
    # Multiple or zero active WRKs: silent no-op
  fi
fi

# Non-blocking: no WRK file or file missing → exit 0 silently
[[ -n "$WRK_FILE" ]] || exit 0
[[ -f "$WRK_FILE" ]] || exit 0
[[ -f "$REPO_MAP" ]] || exit 0

# Delegate to Python helper for parsing
uv run --no-project python "${SCRIPT_DIR}/repo-map-context.py" "$WRK_FILE" "$REPO_MAP" 2>/dev/null || true
exit 0
