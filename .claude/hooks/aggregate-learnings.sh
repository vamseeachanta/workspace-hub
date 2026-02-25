#!/usr/bin/env bash
# aggregate-learnings.sh - Aggregate session transcripts for RAG

WS="${WORKSPACE_HUB:-$(cd "$(dirname "$0")/../.." && pwd)}"

TRANSCRIPT_DIR="${WS}/.claude/skills/session-logs/transcripts"
OUTPUT_DIR="${WS}/.claude/skills/session-logs/aggregated"
mkdir -p "$OUTPUT_DIR"

TODAY=$(date +%Y%m%d)

echo "Extracting human prompts..."
cat "$TRANSCRIPT_DIR"/*.jsonl 2>/dev/null | \
    jq -r 'select(.role == "human" and .text != "[result]") | "\(.ts)\t\(.text)"' | \
    sort -u > "${OUTPUT_DIR}/human_prompts_${TODAY}.tsv"

echo "Extracting AI explanations..."
cat "$TRANSCRIPT_DIR"/*.jsonl 2>/dev/null | \
    jq -r 'select(.role == "ai" and (.text | startswith("[tool:") | not)) | "\(.ts)\t\(.text)"' | \
    sort -u > "${OUTPUT_DIR}/ai_explanations_${TODAY}.tsv"

echo "Calculating tool usage..."
cat "$TRANSCRIPT_DIR"/*.jsonl 2>/dev/null | \
    jq -r 'select(.text | startswith("[tool:")) | .text' | \
    sort | uniq -c | sort -rn > "${OUTPUT_DIR}/tool_stats_${TODAY}.txt"

echo "Summary..."
cat > "${OUTPUT_DIR}/summary_${TODAY}.json" << SUMMARY
{
  "generated": "$(date -Iseconds)",
  "transcripts": $(ls "$TRANSCRIPT_DIR"/*.jsonl 2>/dev/null | wc -l),
  "messages": $(cat "$TRANSCRIPT_DIR"/*.jsonl 2>/dev/null | wc -l)
}
SUMMARY

echo "Done: $OUTPUT_DIR/"
ls -la "$OUTPUT_DIR"/*_${TODAY}* 2>/dev/null
