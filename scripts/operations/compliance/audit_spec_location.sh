#!/usr/bin/env bash

# ABOUTME: Identify specification files in child repos instead of centralized location
# ABOUTME: Allows only pointer README.md in child repo specs/ directories

set -euo pipefail

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
    --scope|--base-ref) shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage; exit 1 ;;
  esac
done

WORKSPACE_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
echo "Checking for specifications in child repos..."

issues=()

# Find all files in any directory named 'specs' that is not at the root
# and is not a README.md or .gitkeep.
# Exclude .venv, node_modules, .git, and other common non-source dirs.
while IFS= read -r -d '' spec_file; do
  rel="${spec_file#"$WORKSPACE_ROOT/"}"
  
  # Exclude root specs directory
  if [[ "$rel" =~ ^specs/ ]]; then continue; fi
  
  # Exclude pointer READMEs and gitkeep
  filename=$(basename "$spec_file")
  if [[ "$filename" == "README.md" || "$filename" == ".gitkeep" ]]; then continue; fi
  
  # Exclude non-specification directories that happen to be named 'specs' (e.g. in library dependencies)
  if [[ "$rel" =~ /\.venv/ ]] || [[ "$rel" =~ /node_modules/ ]] || [[ "$rel" =~ /\.git/ ]]; then continue; fi

  issues+=("$rel")
done < <(find "$WORKSPACE_ROOT" -type f -path "*/specs/*" -print0)

issue_count=${#issues[@]}

if [[ "$issue_count" -gt 0 ]]; then
  echo "Found $issue_count specification files in prohibited child repo locations:"
  for i in "${issues[@]}"; do
    echo "  - $i"
  done
  [[ "$MODE" == "gate" ]] && EXIT_CODE=1
else
  echo "Specification location policy satisfied."
fi

if [[ -n "$REPORT_FILE" ]]; then
  {
    echo "{"
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
