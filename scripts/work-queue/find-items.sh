#!/usr/bin/env bash
# find-items.sh — Search WRK items by keyword across all queue directories
# Usage: find-items.sh <keyword> [--archived] [--gh]
set -euo pipefail

REPO_ROOT="$(git -C "$(dirname "${BASH_SOURCE[0]}")" rev-parse --show-toplevel)"
WORK_QUEUE="${REPO_ROOT}/.claude/work-queue"

keyword=""
include_archived=false
use_gh=false

for arg in "$@"; do
    case "$arg" in
        --archived) include_archived=true ;;
        --gh) use_gh=true ;;
        *) [[ -z "$keyword" ]] && keyword="$arg" ;;
    esac
done

if [[ -z "$keyword" ]]; then
    echo "Usage: find-items.sh <keyword> [--archived] [--gh]" >&2
    echo "  --archived  Include archived local items" >&2
    echo "  --gh        Also search GitHub Issues" >&2
    exit 2
fi

# --- Local search ---
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
            local match
            match="$(grep -im1 "$keyword" "$f" | sed 's/^[[:space:]]*//' | head -c 100)"
            printf "  %-12s %-50s\n" "$id" "${title:-<no title>}"
            printf "               → %s\n" "$match"
        fi
    done
}

echo "═══ Local ═══"
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

# --- GitHub Issues search ---
if [[ "$use_gh" == true ]]; then
    if ! command -v gh &>/dev/null; then
        echo "" >&2
        echo "ERROR: gh CLI not found — install from https://cli.github.com" >&2
        exit 1
    fi
    echo ""
    echo "═══ GitHub Issues ═══"
    gh issue list --search "$keyword" --limit 25 \
        --json number,title,state,labels,url \
        --jq '.[] | "  #\(.number)\t\(.title[:60])\t[\(.state)]\(.labels | map(.name) | join(" "))\n               → \(.url)"'
    # Also search closed issues
    closed="$(gh issue list --search "$keyword" --state closed --limit 10 \
        --json number,title,state,labels,url \
        --jq '.[] | "  #\(.number)\t\(.title[:60])\t[\(.state)]\(.labels | map(.name) | join(" "))\n               → \(.url)"')"
    if [[ -n "$closed" ]]; then
        echo "── closed ──"
        echo "$closed"
    fi
fi
