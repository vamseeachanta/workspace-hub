#!/usr/bin/env bash
# on-complete-hook.sh — Work item completion hook
#
# Fires when a work item is archived. Checks whether marketing brochure
# updates are needed and appends tasks to the work item + creates a
# brochure sync work item for aceengineer-website.
#
# Usage:
#   ./on-complete-hook.sh <WRK-NNN> [archive-path]
#
# Behavior:
#   1. Reads the archived work item's target_repos
#   2. For each repo, checks if a marketing brochure exists at
#      <repo>/docs/marketing/*brochure*.md
#   3. If so, sets brochure_status: pending in the work item
#   4. Outputs a checklist of brochure update tasks
#
# This script is informational — it prints recommended actions.
# The actual brochure updates are done by the orchestrator agent.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
QUEUE_ROOT="$(dirname "$SCRIPT_DIR")"
WORKSPACE_ROOT="$(cd "$QUEUE_ROOT/../.." && pwd)"

# ── Args ──────────────────────────────────────────────────
WRK_ID="${1:-}"
ARCHIVE_PATH="${2:-}"

if [[ -z "$WRK_ID" ]]; then
    echo "Usage: $0 <WRK-NNN> [archive-path]" >&2
    exit 1
fi

# ── Find the work item file ──────────────────────────────
if [[ -n "$ARCHIVE_PATH" && -f "$ARCHIVE_PATH" ]]; then
    ITEM_FILE="$ARCHIVE_PATH"
else
    # Search archive and working dirs
    ITEM_FILE=""
    for dir in "$QUEUE_ROOT"/archive/*/ "$QUEUE_ROOT"/archive/ "$QUEUE_ROOT"/working/; do
        if [[ -f "${dir}${WRK_ID}.md" ]]; then
            ITEM_FILE="${dir}${WRK_ID}.md"
            break
        fi
    done
fi

if [[ -z "$ITEM_FILE" || ! -f "$ITEM_FILE" ]]; then
    echo "ERROR: Cannot find work item file for $WRK_ID" >&2
    exit 1
fi

echo "=== Work Item Completion Hook ==="
echo "Item: $WRK_ID"
echo "File: $ITEM_FILE"
echo ""

# ── Extract target repos from frontmatter ────────────────
REPOS=()
IN_REPOS=false
while IFS= read -r line; do
    # End of frontmatter
    if [[ "$line" == "---" && ${#REPOS[@]} -gt 0 || ("$IN_REPOS" == true && "$line" =~ ^[a-z] && ! "$line" =~ ^[[:space:]]*-) ]]; then
        IN_REPOS=false
    fi

    if [[ "$line" =~ ^target_repos: ]]; then
        IN_REPOS=true
        # Check for inline list: [repo1, repo2]
        if [[ "$line" =~ \[(.+)\] ]]; then
            IFS=',' read -ra inline <<< "${BASH_REMATCH[1]}"
            for r in "${inline[@]}"; do
                r=$(echo "$r" | tr -d ' "'"'"'')
                [[ -n "$r" ]] && REPOS+=("$r")
            done
            IN_REPOS=false
        fi
        continue
    fi

    if [[ "$IN_REPOS" == true && "$line" =~ ^[[:space:]]*-[[:space:]]+(.*) ]]; then
        repo=$(echo "${BASH_REMATCH[1]}" | tr -d ' "'"'"'')
        [[ -n "$repo" ]] && REPOS+=("$repo")
    fi
done < "$ITEM_FILE"

if [[ ${#REPOS[@]} -eq 0 ]]; then
    echo "No target repos found. Skipping brochure check."
    exit 0
fi

echo "Target repos: ${REPOS[*]}"
echo ""

# ── Check for marketing brochures in each repo ──────────
BROCHURE_TASKS=()
for repo in "${REPOS[@]}"; do
    REPO_PATH="$WORKSPACE_ROOT/$repo"
    if [[ ! -d "$REPO_PATH" ]]; then
        echo "SKIP: $repo — directory not found"
        continue
    fi

    # Look for existing brochure files
    BROCHURES=$(find "$REPO_PATH/docs/marketing" -name '*brochure*' -o -name '*capability*' 2>/dev/null || true)

    if [[ -n "$BROCHURES" ]]; then
        echo "FOUND brochure(s) in $repo:"
        echo "$BROCHURES" | sed 's/^/  /'
        BROCHURE_TASKS+=("UPDATE $repo brochure with $WRK_ID capabilities")
    else
        echo "NO brochure in $repo — consider creating one"
        BROCHURE_TASKS+=("CREATE marketing brochure for $repo (triggered by $WRK_ID)")
    fi
done

echo ""

# ── Always add aceengineer-website sync task ─────────────
BROCHURE_TASKS+=("SYNC $WRK_ID capabilities to aceengineer-website portfolio")

# ── Output recommended tasks ─────────────────────────────
echo "=== Recommended Brochure Tasks ==="
for task in "${BROCHURE_TASKS[@]}"; do
    echo "  [ ] $task"
done
echo ""

# ── Update brochure_status in the work item ──────────────
if grep -q "^brochure_status:" "$ITEM_FILE"; then
    sed -i "s/^brochure_status:.*/brochure_status: pending/" "$ITEM_FILE"
else
    # Insert brochure_status before synced_to (or blocked_by as fallback)
    # Avoid matching the opening/closing --- delimiters
    if grep -q "^synced_to:" "$ITEM_FILE"; then
        sed -i "/^synced_to:/i brochure_status: pending" "$ITEM_FILE"
    elif grep -q "^blocked_by:" "$ITEM_FILE"; then
        sed -i "/^blocked_by:/a brochure_status: pending" "$ITEM_FILE"
    else
        # Last resort: use python to insert before the closing ---
        python3 -c "
import re, sys
text = open('$ITEM_FILE').read()
# Find the second --- (closing frontmatter)
parts = text.split('---', 2)
if len(parts) >= 3:
    parts[1] = parts[1].rstrip() + '\nbrochure_status: pending\n'
    open('$ITEM_FILE', 'w').write('---'.join(parts))
"
    fi
fi

echo "Updated $WRK_ID brochure_status: pending"
echo ""
echo "=== Hook Complete ==="
