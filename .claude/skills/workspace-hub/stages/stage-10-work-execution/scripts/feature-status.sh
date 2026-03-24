#!/usr/bin/env bash
# feature-status.sh WRK-NNN
# Print completion status for a Feature WRK: N/M archived (X%) with per-child list.
#
# children: parsing:
#   Handles BOTH inline-list YAML (children: [WRK-A, WRK-B]) and
#   block-list YAML (children:\n  - WRK-A\n  - WRK-B).
#
# NOTE: Only "archived" status counts as complete (not "done").
#
# Usage:
#   feature-status.sh WRK-NNN
#
# Env vars:
#   WORK_QUEUE_ROOT  Override queue directory (default: <repo-root>/.claude/work-queue)
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

WORK_QUEUE_ROOT="${WORK_QUEUE_ROOT:-${REPO_ROOT}/.claude/work-queue}"

WRK_ID="${1:?Usage: feature-status.sh WRK-NNN}"

# ── Find WRK file in any queue dir ───────────────────────────────────────────
WRK_FILE=""
for dir in pending working blocked archived archive; do
    candidate="${WORK_QUEUE_ROOT}/${dir}/${WRK_ID}.md"
    if [[ -f "$candidate" ]]; then
        WRK_FILE="$candidate"
        break
    fi
done
if [[ -z "$WRK_FILE" ]]; then
    WRK_FILE=$(find "${WORK_QUEUE_ROOT}" -name "${WRK_ID}.md" 2>/dev/null | head -1 || true)
fi
if [[ -z "$WRK_FILE" ]]; then
    echo "ERROR: ${WRK_ID} not found in ${WORK_QUEUE_ROOT}" >&2
    exit 1
fi

# ── Parse children: field (inline or block-list YAML) ────────────────────────
# Strategy:
#   1. Check for inline list:  children: [WRK-A, WRK-B]
#   2. Fallback to block-list: children:\n  - WRK-A\n  - WRK-B
#
# We read the full YAML frontmatter to handle both formats.

CHILDREN=()

# Try inline format first: line must contain '[' to be an inline list
children_line=$(grep '^children:' "$WRK_FILE" | head -1 || true)
if echo "$children_line" | grep -q '\['; then
    inline=$(echo "$children_line" | sed 's/children: *\[//;s/\].*//')
    IFS=',' read -ra raw_ids <<< "$inline"
    for id in "${raw_ids[@]}"; do
        id="${id// /}"
        [[ -z "$id" ]] && continue
        CHILDREN+=("$id")
    done
fi

# If inline found nothing, try block-list format
if [[ ${#CHILDREN[@]} -eq 0 ]]; then
    in_children=0
    while IFS= read -r line; do
        if [[ "$line" =~ ^children: ]]; then
            in_children=1
            continue
        fi
        if [[ $in_children -eq 1 ]]; then
            # Block-list item: "  - WRK-NNN"
            if [[ "$line" =~ ^[[:space:]]*-[[:space:]]+(WRK-[0-9]+) ]]; then
                CHILDREN+=("${BASH_REMATCH[1]}")
            elif [[ "$line" =~ ^[a-z] || "$line" =~ ^--- ]]; then
                # New YAML key or end of frontmatter — stop
                in_children=0
            fi
        fi
    done < "$WRK_FILE"
fi

if [[ ${#CHILDREN[@]} -eq 0 ]]; then
    echo "${WRK_ID}: no children (standalone item or empty children: field)"
    exit 0
fi

# ── Count archived children ───────────────────────────────────────────────────
TOTAL=${#CHILDREN[@]}
ARCHIVED_COUNT=0

for child in "${CHILDREN[@]}"; do
    # Find child file in any queue dir
    child_status="unknown"
    child_file=$(find "${WORK_QUEUE_ROOT}" -name "${child}.md" 2>/dev/null | head -1 || true)
    if [[ -n "$child_file" ]]; then
        child_status=$(grep '^status:' "$child_file" | head -1 | awk '{print $2}' | xargs || echo "unknown")
    fi

    if [[ "$child_status" == "archived" ]]; then
        ARCHIVED_COUNT=$((ARCHIVED_COUNT + 1))
    fi
    printf "  %-14s  %s\n" "$child" "$child_status"
done

# ── Summary line ──────────────────────────────────────────────────────────────
PCT=$(( TOTAL > 0 ? ARCHIVED_COUNT * 100 / TOTAL : 0 ))
echo ""
echo "${WRK_ID}: ${ARCHIVED_COUNT}/${TOTAL} archived (${PCT}%)"
