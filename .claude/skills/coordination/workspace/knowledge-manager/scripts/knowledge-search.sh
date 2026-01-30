#!/usr/bin/env bash
# knowledge-search.sh - Search knowledge entries
# Usage: knowledge-search.sh [--query TEXT] [--type TYPE] [--category CAT] [--tag TAG] [--repo REPO] [--full-text TEXT] [--status STATUS] [--min-confidence N]

set -euo pipefail

WORKSPACE_ROOT="${WORKSPACE_ROOT:-/mnt/github/workspace-hub}"
KNOWLEDGE_DIR="${WORKSPACE_ROOT}/.claude/knowledge"
INDEX_FILE="${KNOWLEDGE_DIR}/index.json"
ENTRIES_DIR="${KNOWLEDGE_DIR}/entries"

# Parse arguments
QUERY=""
TYPE=""
CATEGORY=""
TAG=""
REPO=""
FULL_TEXT=""
STATUS="active"
MIN_CONFIDENCE="0"
FORMAT="summary"  # summary|full|json

while [[ $# -gt 0 ]]; do
    case "$1" in
        --query|-q) QUERY="$2"; shift 2 ;;
        --type|-t) TYPE="$2"; shift 2 ;;
        --category|-c) CATEGORY="$2"; shift 2 ;;
        --tag) TAG="$2"; shift 2 ;;
        --repo|-r) REPO="$2"; shift 2 ;;
        --full-text|-f) FULL_TEXT="$2"; shift 2 ;;
        --status|-s) STATUS="$2"; shift 2 ;;
        --min-confidence) MIN_CONFIDENCE="$2"; shift 2 ;;
        --format) FORMAT="$2"; shift 2 ;;
        --all) STATUS=""; shift ;;
        *) QUERY="$1"; shift ;;
    esac
done

if [[ ! -f "$INDEX_FILE" ]]; then
    echo "ERROR: Index not found. Run knowledge-index.sh first." >&2
    exit 1
fi

# Build jq filter chain
JQ_FILTER='.entries'

# Filter by status
if [[ -n "$STATUS" ]]; then
    JQ_FILTER+=" | [.[] | select(.status == \"$STATUS\")]"
fi

# Filter by type
if [[ -n "$TYPE" ]]; then
    JQ_FILTER+=" | [.[] | select(.type == \"$TYPE\")]"
fi

# Filter by category
if [[ -n "$CATEGORY" ]]; then
    JQ_FILTER+=" | [.[] | select(.category == \"$CATEGORY\")]"
fi

# Filter by tag
if [[ -n "$TAG" ]]; then
    JQ_FILTER+=" | [.[] | select(.tags | index(\"$TAG\"))]"
fi

# Filter by repo
if [[ -n "$REPO" ]]; then
    JQ_FILTER+=" | [.[] | select(.repos | index(\"$REPO\"))]"
fi

# Filter by minimum confidence
if [[ "$MIN_CONFIDENCE" != "0" ]]; then
    JQ_FILTER+=" | [.[] | select(.confidence >= $MIN_CONFIDENCE)]"
fi

# Filter by query (title match)
if [[ -n "$QUERY" ]]; then
    # Case-insensitive title search
    JQ_FILTER+=" | [.[] | select(.title | ascii_downcase | contains(\"$(echo "$QUERY" | tr '[:upper:]' '[:lower:]')\"))]"
fi

# Sort by confidence descending
JQ_FILTER+=" | sort_by(-.confidence)"

# Execute index search
results=$(jq "$JQ_FILTER" "$INDEX_FILE")
result_count=$(echo "$results" | jq 'length')

# Full-text search (grep through actual files)
if [[ -n "$FULL_TEXT" ]]; then
    ft_files=()
    while IFS= read -r match_file; do
        [[ -z "$match_file" ]] && continue
        ft_files+=("$match_file")
    done < <(grep -rl "$FULL_TEXT" "$ENTRIES_DIR" --include="*.md" 2>/dev/null)

    if [[ ${#ft_files[@]} -gt 0 ]]; then
        # Filter results to only those matching full-text
        ft_filter=""
        for f in "${ft_files[@]}"; do
            rel_path="${f#$WORKSPACE_ROOT/}"
            if [[ -n "$ft_filter" ]]; then
                ft_filter+=" or "
            fi
            ft_filter+=".file == \"$rel_path\""
        done
        results=$(echo "$results" | jq "[.[] | select($ft_filter)]")
        result_count=$(echo "$results" | jq 'length')
    else
        results="[]"
        result_count=0
    fi
fi

# Output based on format
if [[ "$FORMAT" == "json" ]]; then
    echo "$results"
    exit 0
fi

if [[ $result_count -eq 0 ]]; then
    echo "No entries found."
    exit 0
fi

echo "Found $result_count entries:"
echo ""

if [[ "$FORMAT" == "full" ]]; then
    echo "$results" | jq -r '.[] | "─────────────────────────────────────────\n\(.id) | \(.title)\nType: \(.type) | Category: \(.category) | Confidence: \(.confidence)\nTags: \(.tags | join(", ")) | Repos: \(.repos | join(", "))\nFile: \(.file)\nStatus: \(.status) | Accessed: \(.access_count)x | Created: \(.created)"'
else
    # Summary table
    printf "%-10s %-45s %-12s %s\n" "ID" "TITLE" "CONFIDENCE" "CATEGORY"
    printf "%-10s %-45s %-12s %s\n" "──────────" "─────────────────────────────────────────────" "────────────" "────────────"
    echo "$results" | jq -r '.[] | "\(.id)|\(.title)|\(.confidence)|\(.category)"' | while IFS='|' read -r id title conf cat; do
        # Truncate title to 45 chars
        [[ ${#title} -gt 45 ]] && title="${title:0:42}..."
        printf "%-10s %-45s %-12s %s\n" "$id" "$title" "$conf" "$cat"
    done
fi
