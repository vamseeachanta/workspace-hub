#!/usr/bin/env bash

# ABOUTME: Validate that child-repo skills are symlink/junction propagated from workspace-hub
# ABOUTME: Enforces no local SKILL.md files in child repos (workspace-hub is source of truth)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
MODE="warn"
REPORT_FILE=""
EXIT_CODE=0

usage() {
  cat << USAGE
Usage: $(basename "$0") [--mode warn|gate] [--report <file>]
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --mode) MODE="${2:-warn}"; shift 2 ;;
    --report) REPORT_FILE="${2:-}"; shift 2 ;;
    --scope|--base-ref) shift 2 ;; # accepted for wrapper compatibility
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage; exit 1 ;;
  esac
done

if [[ "$MODE" != "warn" && "$MODE" != "gate" ]]; then
  echo "Invalid --mode: $MODE" >&2
  exit 1
fi

issues=()
repo_count=0

while IFS= read -r -d '' skills_dir; do
  repo_root="$(dirname "$(dirname "$skills_dir")")"
  repo_name="$(basename "$repo_root")"

  if [[ "$repo_root" == "$WORKSPACE_ROOT" ]]; then
    continue
  fi

  repo_count=$((repo_count + 1))
  while IFS= read -r -d '' skill_file; do
    if [[ ! -L "$skill_file" ]]; then
      rel="${skill_file#"$WORKSPACE_ROOT/"}"
      issues+=("$rel")
    fi
  done < <(find "$skills_dir" -type f -name "SKILL.md" -print0)
done < <(find "$WORKSPACE_ROOT" -mindepth 3 -maxdepth 3 -type d -path "$WORKSPACE_ROOT/*/.claude/skills" -print0)

issue_count=${#issues[@]}

if [[ "$issue_count" -gt 0 ]]; then
  echo "Found $issue_count non-symlink SKILL.md files in child repos:"
  for i in "${issues[@]}"; do
    echo "  - $i"
  done
  [[ "$MODE" == "gate" ]] && EXIT_CODE=1
else
  echo "Skills symlink policy satisfied across $repo_count repos."
fi

if [[ -n "$REPORT_FILE" ]]; then
  {
    echo "{"
    echo "  \"checked_repos\": $repo_count,"
    echo "  \"issue_count\": $issue_count,"
    echo "  \"issues\": ["
    for i in "${!issues[@]}"; do
      comma=","
      [[ "$i" -eq $((issue_count - 1)) ]] && comma=""
      echo "    \"${issues[$i]}\"$comma"
    done
    echo "  ]"
    echo "}"
  } > "$REPORT_FILE"
fi

exit "$EXIT_CODE"
