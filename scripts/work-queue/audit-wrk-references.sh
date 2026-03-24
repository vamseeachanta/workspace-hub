#!/usr/bin/env bash
# audit-wrk-references.sh — Find all files referencing WRK-\d+ pattern
# Categorizes: must-update (parses/constructs IDs), display-only, historical
# Usage: bash scripts/work-queue/audit-wrk-references.sh [--summary]
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
SUMMARY_ONLY=false
[[ "${1:-}" == "--summary" ]] && SUMMARY_ONLY=true

# Scripts that parse/construct WRK IDs (must support new format)
MUST_UPDATE_PATTERNS=(
  'WRK-.*\.md'        # file path construction
  'WRK-\$'            # variable interpolation
  'WRK-\d+'           # regex patterns in code
  'WRK-.*basename'    # filename extraction
  '/WRK-'             # path construction
)

echo "═══ WRK-\\d+ Reference Audit ═══"
echo ""

# Count by directory
declare -A dir_counts
total=0

while IFS= read -r file; do
  # Skip binary files, .git, node_modules
  [[ "$file" == *".git/"* ]] && continue
  [[ "$file" == *"node_modules/"* ]] && continue
  [[ "$file" == *"wrk-status-index.json" ]] && continue

  dir=$(dirname "$file" | sed "s|$REPO_ROOT/||")
  dir_counts["$dir"]=$(( ${dir_counts["$dir"]:-0} + 1 ))
  total=$((total + 1))

  if ! $SUMMARY_ONLY; then
    echo "$file"
  fi
done < <(grep -rl 'WRK-[0-9]' "$REPO_ROOT" \
  --include="*.sh" --include="*.py" --include="*.yaml" --include="*.yml" \
  --include="*.md" --include="*.json" --include="*.txt" \
  2>/dev/null | sort)

echo ""
echo "── By directory ──"
for dir in $(echo "${!dir_counts[@]}" | tr ' ' '\n' | sort); do
  printf "  %-50s %d\n" "$dir" "${dir_counts[$dir]}"
done

echo ""
echo "── Must-update scripts (parse/construct WRK IDs) ──"
must_update=0
for file in $(grep -rl 'WRK-[0-9]\|WRK-\$\|WRK-.*\.md\|/WRK-' "$REPO_ROOT/scripts" \
  --include="*.sh" --include="*.py" 2>/dev/null | sort); do
  rel=$(echo "$file" | sed "s|$REPO_ROOT/||")
  echo "  $rel"
  must_update=$((must_update + 1))
done

echo ""
echo "── Must-update hooks ──"
for file in $(grep -rl 'WRK-[0-9]\|WRK-\$\|WRK-.*\.md' "$REPO_ROOT/.claude/hooks" \
  --include="*.sh" 2>/dev/null | sort); do
  rel=$(echo "$file" | sed "s|$REPO_ROOT/||")
  echo "  $rel"
  must_update=$((must_update + 1))
done

echo ""
echo "Total files with WRK-\\d+: $total"
echo "Must-update scripts/hooks: $must_update"
