#!/usr/bin/env bash
# knowledge-capture.sh — Phase 3: Extract domain facts from session signals
# Reads today's signal files, appends new facts to state/learned-patterns.jsonl
# WRK-1102 Fix 4: standalone Phase 3 script for comprehensive-learning.sh
set -euo pipefail

WORKSPACE="${WORKSPACE_HUB:-$(git rev-parse --show-toplevel 2>/dev/null || echo ".")}"
DATE="${KNOWLEDGE_DATE:-$(date -d yesterday +%Y-%m-%d 2>/dev/null || date -v-1d +%Y-%m-%d)}"
DRY_RUN=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --workspace) WORKSPACE="$2"; shift 2 ;;
        --date)      DATE="$2"; shift 2 ;;
        --dry-run)   DRY_RUN=true; shift ;;
        --help|-h)   echo "Usage: $0 [--workspace DIR] [--date YYYY-MM-DD] [--dry-run]"; exit 0 ;;
        *) shift ;;
    esac
done

SIGNALS_DIR="${WORKSPACE}/state/session-signals"
PATTERNS_FILE="${WORKSPACE}/state/learned-patterns.jsonl"

[[ "$DRY_RUN" == "true" ]] && { echo "knowledge-capture: dry-run mode — no writes"; exit 0; }

mkdir -p "$(dirname "$PATTERNS_FILE")"

# Find signal files for the target date
SIGNAL_FILE="${SIGNALS_DIR}/${DATE}.jsonl"
if [[ ! -f "$SIGNAL_FILE" ]]; then
    echo "knowledge-capture: no signal file for ${DATE} — skipping"
    exit 0
fi

command -v jq &>/dev/null || { echo "knowledge-capture: jq required"; exit 0; }

COUNT=0
while IFS= read -r line; do
    [[ -z "$line" ]] && continue
    event=$(echo "$line" | jq -r '.event // empty' 2>/dev/null || true)
    case "$event" in
        skill_invoked)
            skill=$(echo "$line" | jq -r '.skill // empty' 2>/dev/null || true)
            [[ -z "$skill" ]] && continue
            fact=$(jq -n \
                --arg date "$DATE" \
                --arg skill "$skill" \
                --arg event "$event" \
                '{"date":$date,"fact_type":"skill_usage","skill":$skill,"event":$event}')
            echo "$fact" >> "$PATTERNS_FILE"
            COUNT=$((COUNT + 1))
            ;;
        stage_exit)
            wrk=$(echo "$line" | jq -r '.wrk // empty' 2>/dev/null || true)
            stage=$(echo "$line" | jq -r '.stage // empty' 2>/dev/null || true)
            [[ -z "$wrk" ]] && continue
            fact=$(jq -n \
                --arg date "$DATE" \
                --arg wrk "$wrk" \
                --argjson stage "${stage:-0}" \
                '{"date":$date,"fact_type":"stage_exit","wrk":$wrk,"stage":$stage}')
            echo "$fact" >> "$PATTERNS_FILE"
            COUNT=$((COUNT + 1))
            ;;
        *) true ;;
    esac
done < "$SIGNAL_FILE"

echo "knowledge-capture: extracted ${COUNT} fact(s) from ${DATE} → ${PATTERNS_FILE}"
