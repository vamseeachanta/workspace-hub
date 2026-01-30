#!/usr/bin/env bash
# knowledge-advise.sh - Surface relevant knowledge for a task
# Usage: knowledge-advise.sh "task description" [--repo REPO] [--category CAT] [--top N]

set -euo pipefail

WORKSPACE_ROOT="${WORKSPACE_ROOT:-/mnt/github/workspace-hub}"
KNOWLEDGE_DIR="${WORKSPACE_ROOT}/.claude/knowledge"
INDEX_FILE="${KNOWLEDGE_DIR}/index.json"
ENTRIES_DIR="${KNOWLEDGE_DIR}/entries"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Parse arguments
TASK_DESC=""
REPO=""
CATEGORY=""
TOP_N=5
UPDATE_ACCESS=true

while [[ $# -gt 0 ]]; do
    case "$1" in
        --repo|-r) REPO="$2"; shift 2 ;;
        --category|-c) CATEGORY="$2"; shift 2 ;;
        --top|-n) TOP_N="$2"; shift 2 ;;
        --no-track) UPDATE_ACCESS=false; shift ;;
        *) [[ -z "$TASK_DESC" ]] && TASK_DESC="$1" || TASK_DESC="$TASK_DESC $1"; shift ;;
    esac
done

if [[ -z "$TASK_DESC" ]]; then
    echo "Usage: knowledge-advise.sh \"task description\" [--repo REPO] [--top N]" >&2
    exit 1
fi

if [[ ! -f "$INDEX_FILE" ]]; then
    echo "No knowledge index found. Run knowledge-index.sh first." >&2
    exit 1
fi

# Extract keywords from task description (lowercase, split on spaces/punctuation)
keywords=()
while IFS= read -r word; do
    # Skip short words and common stop words
    [[ ${#word} -lt 3 ]] && continue
    case "$word" in
        the|and|for|with|from|this|that|will|have|been|into|also|when|what|how|are|was|not|can|but) continue ;;
    esac
    keywords+=("$word")
done < <(echo "$TASK_DESC" | tr '[:upper:]' '[:lower:]' | tr -c 'a-z0-9' '\n' | sort -u)

# Score each active entry
# Scoring: tag match=3, keyword in title=2, category match=2, repo match=2, keyword in body=1
scored_entries=$(jq --arg task_lower "$(echo "$TASK_DESC" | tr '[:upper:]' '[:lower:]')" \
    --arg repo "$REPO" \
    --arg category "$CATEGORY" \
    --argjson keywords "$(printf '%s\n' "${keywords[@]}" | jq -R . | jq -s .)" \
    '
    [.entries[] | select(.status == "active")] |
    [.[] | . as $entry |
        # Score components
        ($keywords | map(. as $kw | if ($entry.tags | map(ascii_downcase) | any(contains($kw))) then 3 else 0 end) | add // 0) as $tag_score |
        ($keywords | map(. as $kw | if ($entry.title | ascii_downcase | contains($kw)) then 2 else 0 end) | add // 0) as $title_score |
        (if $category != "" and ($entry.category == $category) then 2 else 0 end) as $cat_score |
        (if $repo != "" and ($entry.repos | index($repo)) then 2 else 0 end) as $repo_score |
        ($entry.confidence * 2) as $conf_score |
        ($tag_score + $title_score + $cat_score + $repo_score + $conf_score) as $total_score |
        select($total_score > 0) |
        . + {relevance_score: $total_score}
    ] | sort_by(-.relevance_score)
    ' "$INDEX_FILE")

total_matches=$(echo "$scored_entries" | jq 'length')
showing=$((total_matches < TOP_N ? total_matches : TOP_N))

if [[ $total_matches -eq 0 ]]; then
    echo "No relevant knowledge found for: \"$TASK_DESC\""
    echo "Try broadening your search or adding entries with /knowledge capture"
    exit 0
fi

echo "═══════════════════════════════════════════════════════════"
echo "  Knowledge Advisor - Top $showing of $total_matches matches"
echo "  Task: \"$TASK_DESC\""
echo "═══════════════════════════════════════════════════════════"
echo ""

# Display top N entries with content preview
echo "$scored_entries" | jq -r --argjson top "$TOP_N" '
    .[:$top] | to_entries[] |
    "[\(.value.relevance_score | tostring | .[0:4])] \(.value.id) - \(.value.title)\n     Type: \(.value.type) | Category: \(.value.category) | Confidence: \(.value.confidence)\n     Tags: \(.value.tags | join(", "))\n     File: \(.value.file)\n"'

# Show gotchas prominently
gotcha_count=$(echo "$scored_entries" | jq --argjson top "$TOP_N" '[.[:$top][] | select(.type == "gotcha")] | length')
if [[ $gotcha_count -gt 0 ]]; then
    echo "⚠ GOTCHAS ($gotcha_count found - review before proceeding):"
    echo "$scored_entries" | jq -r --argjson top "$TOP_N" '[.[:$top][] | select(.type == "gotcha")] | .[] | "  → \(.id): \(.title)"'
    echo ""
fi

# Update access counts for surfaced entries
if [[ "$UPDATE_ACCESS" == true ]]; then
    surfaced_ids=$(echo "$scored_entries" | jq -r --argjson top "$TOP_N" '.[:$top][].id')
    if [[ -n "$surfaced_ids" ]]; then
        while IFS= read -r entry_id; do
            [[ -z "$entry_id" ]] && continue
            # Find the entry file and update access_count in frontmatter
            entry_file=$(jq -r --arg id "$entry_id" '.entries[] | select(.id == $id) | .file' "$INDEX_FILE")
            if [[ -n "$entry_file" && -f "${WORKSPACE_ROOT}/${entry_file}" ]]; then
                filepath="${WORKSPACE_ROOT}/${entry_file}"
                current_count=$(grep -E '^access_count:' "$filepath" | grep -oE '[0-9]+' | head -1)
                current_count=${current_count:-0}
                new_count=$((current_count + 1))
                sed -i "s/^access_count: ${current_count}/access_count: ${new_count}/" "$filepath"
            fi
        done <<< "$surfaced_ids"

        # Rebuild index to reflect updated access counts
        if [[ -x "${SCRIPT_DIR}/knowledge-index.sh" ]]; then
            "${SCRIPT_DIR}/knowledge-index.sh" "$WORKSPACE_ROOT" > /dev/null 2>&1 || true
        fi
    fi
fi
