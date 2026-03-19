#!/usr/bin/env bash
# find-items.sh — Search WRK items by keyword across all queue directories
# Usage: find-items.sh <keyword> [--archived]
set -euo pipefail

REPO_ROOT="$(git -C "$(dirname "${BASH_SOURCE[0]}")" rev-parse --show-toplevel)"
WORK_QUEUE="${REPO_ROOT}/.claude/work-queue"

keyword="${1:-}"
include_archived=false

if [[ -z "$keyword" ]]; then
    echo "Usage: find-items.sh <keyword> [--archived]" >&2
    exit 2
fi

shift
for arg in "$@"; do
    [[ "$arg" == "--archived" ]] && include_archived=true
done

search_dir() {
    local dir="$1" label="$2"
    local found=false
    for f in "$dir"/WRK-*.md; do
        [[ -f "$f" ]] || continue
        if grep -qil "$keyword" "$f" 2>/dev/null; then
            if [[ "$found" == false ]]; then
                echo "── $label ──"
                found=true
            fi
            local id title
            id="$(basename "$f" .md)"
            title="$(awk '/^---$/{c++;next} c==1 && /^title:/{sub(/^title:[[:space:]]*/,""); gsub(/^"|"$/,""); print; exit}' "$f")"
            # Show matching line for context
            local match
            match="$(grep -im1 "$keyword" "$f" | sed 's/^[[:space:]]*//' | head -c 100)"
            printf "  %-12s %-50s\n" "$id" "${title:-<no title>}"
            printf "               → %s\n" "$match"
        fi
    done
}

search_dir "$WORK_QUEUE/working" "working"
search_dir "$WORK_QUEUE/pending" "pending"
search_dir "$WORK_QUEUE/blocked" "blocked"

if [[ "$include_archived" == true ]]; then
    for month_dir in "$WORK_QUEUE/archive"/*/; do
        [[ -d "$month_dir" ]] || continue
        label="archive/$(basename "$month_dir")"
        search_dir "$month_dir" "$label"
    done
fi
