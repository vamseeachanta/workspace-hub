#!/usr/bin/env bash
# validate-wrk-frontmatter.sh — Validate required WRK frontmatter fields
#
# Usage: validate-wrk-frontmatter.sh WRK-NNN
#   Env: QUEUE_DIR (optional) — override queue directory
#
# Exit codes:
#   0 = all required fields present and non-empty
#   1 = one or more required fields missing or empty
#   2 = infrastructure error (file not found, bad args)
set -euo pipefail

WRK_ID="${1:-}"
if [[ -z "$WRK_ID" ]]; then
  echo "Usage: $0 <WRK-NNN>" >&2
  exit 2
fi

WORKSPACE_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
QUEUE_DIR="${QUEUE_DIR:-${WORKSPACE_ROOT}/.claude/work-queue}"

# Locate WRK file in pending/ or working/
FILE_PATH=""
for folder in pending working; do
  candidate="${QUEUE_DIR}/${folder}/${WRK_ID}.md"
  if [[ -f "$candidate" ]]; then
    FILE_PATH="$candidate"
    break
  fi
done

if [[ -z "$FILE_PATH" ]]; then
  echo "✖ ${WRK_ID}.md not found in pending/ or working/" >&2
  exit 2
fi

# Required fields per work-queue SKILL.md §Work Item Format
REQUIRED_FIELDS=(
  id
  title
  status
  priority
  complexity
  created_at
  target_repos
  computer
  plan_workstations
  execution_workstations
  category
  subcategory
)

# Optional fields (documented here for schema reference; not validated)
# github_issue_ref — URL to linked GitHub Issue (WRK-1333)

# Extract frontmatter (between first --- and second ---)
frontmatter="$(awk '/^---$/{n++; next} n==1{print} n>=2{exit}' "$FILE_PATH")"

missing=()
for field in "${REQUIRED_FIELDS[@]}"; do
  # Check if field exists and has a value (inline or YAML list/block below)
  has_value="$(echo "$frontmatter" | awk -v f="$field" '
    BEGIN { found=0 }
    $0 ~ "^"f":" {
      # Get inline value after "field: "
      sub(/^[^:]+:[ \t]*/, "")
      val = $0
      # Strip quotes
      gsub(/^"/, "", val); gsub(/"$/, "", val)
      gsub(/^[ \t]+/, "", val); gsub(/[ \t]+$/, "", val)
      if (val != "" && val != "[]") { found=1; exit }
      # Empty inline — check next lines for YAML list items or inline array
      getline
      if ($0 ~ /^[ \t]+-/) { found=1 }
      exit
    }
    END { print found }
  ')"
  if [[ "$has_value" != "1" ]]; then
    missing+=("$field")
  fi
done

if [[ ${#missing[@]} -gt 0 ]]; then
  echo "✖ ${WRK_ID}: missing or empty fields: ${missing[*]}" >&2
  exit 1
fi

echo "✔ ${WRK_ID}: all required frontmatter fields present"
exit 0
