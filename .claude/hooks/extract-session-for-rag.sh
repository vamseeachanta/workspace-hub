#!/usr/bin/env bash
# extract-session-for-rag.sh - Extract Claude session transcripts for RAG
# Usage: ./extract-session-for-rag.sh [--current|--today|--recent N]

CLAUDE_HOME="${HOME}/.claude"
WS="${WORKSPACE_HUB:-$(cd "$(dirname "$0")/../.." && pwd)}"

OUTPUT_DIR="${WS}/.claude/skills/session-logs/transcripts"
mkdir -p "$OUTPUT_DIR"

extract_session() {
    local src="$1"
    local dst="$2"
    
    jq -c '
        select(.type == "user" or .type == "assistant") |
        {
            ts: .timestamp,
            role: (if .type == "user" then "human" else "ai" end),
            text: (
                if .message.content then
                    [.message.content[] | 
                        if .type == "text" then .text
                        elif .type == "tool_use" then "[tool:\(.name)]"
                        elif .type == "tool_result" then "[result]"
                        else ""
                        end
                    ] | map(select(. != "")) | join(" ")
                else ""
                end
            ),
            session: .sessionId
        } | select(.text != "")
    ' "$src" > "$dst" 2>/dev/null
    
    echo "Extracted $(wc -l < "$dst") messages -> $dst"
}

case "${1:-}" in
    --current)
        # Find most recently modified session
        latest=$(ls -t "$CLAUDE_HOME"/projects/*/*.jsonl 2>/dev/null | head -1)
        if [ -n "$latest" ]; then
            name=$(basename "$latest" .jsonl)
            extract_session "$latest" "${OUTPUT_DIR}/current_${name}.jsonl"
        fi
        ;;
    --today)
        TODAY=$(date +%Y-%m-%d)
        find "$CLAUDE_HOME/projects" -name "*.jsonl" -newermt "$TODAY" 2>/dev/null | while read f; do
            name=$(basename "$f" .jsonl)
            proj=$(basename "$(dirname "$f")")
            extract_session "$f" "${OUTPUT_DIR}/${proj}_${name}.jsonl"
        done
        ;;
    --recent)
        N="${2:-3}"
        ls -t "$CLAUDE_HOME"/projects/*/*.jsonl 2>/dev/null | head -n "$N" | while read f; do
            name=$(basename "$f" .jsonl)
            proj=$(basename "$(dirname "$f")")
            extract_session "$f" "${OUTPUT_DIR}/${proj}_${name}.jsonl"
        done
        ;;
    *)
        echo "Usage: $0 [--current|--today|--recent N]"
        echo "Output: $OUTPUT_DIR/"
        ;;
esac
