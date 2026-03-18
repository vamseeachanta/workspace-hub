#!/usr/bin/env bash
# auto-unblock.sh — After a WRK archives, check blocked/ items
# and unblock any whose dependencies are all resolved.
# Usage: auto-unblock.sh <WRK-NNN>
set -euo pipefail

WORKSPACE_ROOT="${WORKSPACE_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
QUEUE_DIR="${WORKSPACE_ROOT}/.claude/work-queue"
BLOCKED_DIR="${QUEUE_DIR}/blocked"
PENDING_DIR="${QUEUE_DIR}/pending"
ARCHIVE_DIR="${QUEUE_DIR}/archive"

ARCHIVED_ID="${1:-}"
if [[ -z "$ARCHIVED_ID" ]]; then
  echo "Usage: $0 <WRK-NNN>" >&2
  exit 1
fi

# Normalize ID format
[[ "$ARCHIVED_ID" =~ ^WRK- ]] || ARCHIVED_ID="WRK-${ARCHIVED_ID}"

if [[ ! -d "$BLOCKED_DIR" ]]; then
  exit 0
fi

# Parse blocked_by from a WRK .md file's YAML frontmatter.
# Handles both inline [WRK-A, WRK-B] and block-list formats.
parse_blocked_by() {
  local file="$1"
  local in_frontmatter=false
  local in_blocked_by=false
  local result=()

  while IFS= read -r line; do
    # Track frontmatter boundaries
    if [[ "$line" == "---" ]]; then
      if $in_frontmatter; then
        break  # end of frontmatter
      fi
      in_frontmatter=true
      continue
    fi
    $in_frontmatter || continue

    # Inline format: blocked_by: [WRK-A, WRK-B]
    if [[ "$line" =~ ^blocked_by:\ *\[(.*)\] ]]; then
      local inner="${BASH_REMATCH[1]}"
      # Split on comma, trim whitespace
      IFS=',' read -ra items <<< "$inner"
      for item in "${items[@]}"; do
        item=$(echo "$item" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
        [[ -n "$item" ]] && result+=("$item")
      done
      in_blocked_by=false
      continue
    fi

    # Block-list start: blocked_by: (with nothing or empty after colon)
    if [[ "$line" =~ ^blocked_by: ]]; then
      in_blocked_by=true
      continue
    fi

    # Block-list continuation: lines starting with "  - WRK-"
    if $in_blocked_by; then
      if [[ "$line" =~ ^[[:space:]]*-[[:space:]]*(WRK-[0-9]+) ]]; then
        result+=("${BASH_REMATCH[1]}")
      else
        in_blocked_by=false
      fi
    fi
  done < "$file"

  printf '%s\n' "${result[@]}"
}

# Check if a WRK-NNN exists anywhere under archive/
is_archived() {
  local wrk_id="$1"
  local found
  found=$(find "$ARCHIVE_DIR" -name "${wrk_id}.md" -type f 2>/dev/null | head -1)
  [[ -n "$found" ]]
}

unblocked_count=0

for blocked_file in "${BLOCKED_DIR}"/*.md; do
  [[ -f "$blocked_file" ]] || continue

  # Parse the blocked_by list
  mapfile -t blockers < <(parse_blocked_by "$blocked_file")

  # Skip if no blockers or archived ID not in the list
  [[ ${#blockers[@]} -eq 0 ]] && continue
  local_match=false
  for b in "${blockers[@]}"; do
    if [[ "$b" == "$ARCHIVED_ID" ]]; then
      local_match=true
      break
    fi
  done
  $local_match || continue

  # Check if ALL blockers are archived
  all_resolved=true
  for b in "${blockers[@]}"; do
    if ! is_archived "$b"; then
      all_resolved=false
      break
    fi
  done

  if $all_resolved; then
    item_name=$(basename "$blocked_file")
    item_id="${item_name%.md}"

    # Update status from blocked to pending via sed
    sed -i 's/^status: blocked$/status: pending/' "$blocked_file"

    # Move to pending/
    mv "$blocked_file" "${PENDING_DIR}/${item_name}"
    echo "Unblocked: ${item_id} -> pending/ (all blockers archived)"
    unblocked_count=$((unblocked_count + 1))
  fi
done

if [[ $unblocked_count -eq 0 ]]; then
  echo "No blocked items unblocked by ${ARCHIVED_ID}"
else
  echo "Unblocked ${unblocked_count} item(s) after archiving ${ARCHIVED_ID}"
fi
