#!/usr/bin/env bash
# feature-close-check.sh WRK-NNN
# Gate check: exit 0 iff ALL children are archived; exit 1 otherwise.
# Intended as a blocking condition in Stage 19 close process for Feature WRKs.
#
# children: parsing:
#   Handles BOTH inline-list YAML (children: [WRK-A, WRK-B]) and
#   block-list YAML (children:\n  - WRK-A\n  - WRK-B).
#
# NOTE: Only "archived" status satisfies the gate (not "done").
#
# Usage:
#   feature-close-check.sh WRK-NNN
#   echo $?   # 0 = all archived (feature may close), 1 = blocked
#
# Env vars:
#   WORK_QUEUE_ROOT  Override queue directory (default: <repo-root>/.claude/work-queue)
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

WORK_QUEUE_ROOT="${WORK_QUEUE_ROOT:-${REPO_ROOT}/.claude/work-queue}"

WRK_ID="${1:?Usage: feature-close-check.sh WRK-NNN}"

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
# (Same dual-format handling as feature-status.sh — see that script for commentary)
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

if [[ ${#CHILDREN[@]} -eq 0 ]]; then
    in_children=0
    while IFS= read -r line; do
        if [[ "$line" =~ ^children: ]]; then
            in_children=1
            continue
        fi
        if [[ $in_children -eq 1 ]]; then
            if [[ "$line" =~ ^[[:space:]]*-[[:space:]]+(WRK-[0-9]+) ]]; then
                CHILDREN+=("${BASH_REMATCH[1]}")
            elif [[ "$line" =~ ^[a-z] || "$line" =~ ^--- ]]; then
                in_children=0
            fi
        fi
    done < "$WRK_FILE"
fi

if [[ ${#CHILDREN[@]} -eq 0 ]]; then
    echo "PASS: ${WRK_ID} has no children — feature may close"
    exit 0
fi

# ── Check each child ──────────────────────────────────────────────────────────
BLOCKED=0
for child in "${CHILDREN[@]}"; do
    child_file=$(find "${WORK_QUEUE_ROOT}" -name "${child}.md" 2>/dev/null | head -1 || true)
    child_status="unknown"
    if [[ -n "$child_file" ]]; then
        child_status=$(grep '^status:' "$child_file" | head -1 | awk '{print $2}' | xargs || echo "unknown")
    fi

    if [[ "$child_status" != "archived" ]]; then
        echo "BLOCK: ${child} is ${child_status} (not archived)"
        BLOCKED=1
    fi
done

if [[ $BLOCKED -eq 0 ]]; then
    echo "PASS: all children archived — feature ${WRK_ID} may close"
    exit 0
else
    exit 1
fi
