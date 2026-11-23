#!/usr/bin/env bash
# ingest-codex-sessions.sh — Convert Codex JSONL sessions to session-signal format
# Usage: ingest-codex-sessions.sh [--date YYYY-MM-DD] [--codex-dir DIR] [--signals-dir DIR]
# WRK-1102 Fix 6: feeds Codex activity into Phase 1 signal pipeline
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo ".")"
DATE="${1:-$(date -d yesterday +%Y-%m-%d 2>/dev/null || date -v-1d +%Y-%m-%d)}"
CODEX_SESSIONS_DIR="${HOME}/.codex/sessions"
SIGNALS_DIR="${REPO_ROOT}/state/session-signals"

# Parse flags
while [[ $# -gt 0 ]]; do
    case "$1" in
        --date)       DATE="$2"; shift 2 ;;
        --codex-dir)  CODEX_SESSIONS_DIR="$2"; shift 2 ;;
        --signals-dir) SIGNALS_DIR="$2"; shift 2 ;;
        --help|-h)    echo "Usage: $0 [--date YYYY-MM-DD] [--codex-dir DIR] [--signals-dir DIR]"; exit 0 ;;
        *) shift ;;
    esac
done

mkdir -p "$SIGNALS_DIR"

# Derive year/month/day from DATE for codex path convention
YEAR="${DATE:0:4}"
MONTH="${DATE:5:2}"
DAY="${DATE:8:2}"
SESSION_DATE_DIR="${CODEX_SESSIONS_DIR}/${YEAR}/${MONTH}/${DAY}"

SIGNAL_FILE="${SIGNALS_DIR}/${DATE}.jsonl"
INGESTED=0

if [[ ! -d "$SESSION_DATE_DIR" ]]; then
    echo "ingest-codex: no codex sessions dir for ${DATE} (${SESSION_DATE_DIR}) — skipping"
    exit 0
fi

for session_file in "${SESSION_DATE_DIR}"/rollout-*.jsonl; do
    [[ -f "$session_file" ]] || continue
    # Count message turns
    turns=$(grep -c '"type":"message"' "$session_file" 2>/dev/null || echo 0)
    session_id=$(basename "$session_file" .jsonl)
    signal=$(printf '{"event":"codex_session","date":"%s","session_id":"%s","turns":%d,"source":"codex"}\n' \
        "$DATE" "$session_id" "$turns")
    echo "$signal" >> "$SIGNAL_FILE"
    INGESTED=$((INGESTED + 1))
done

echo "ingest-codex: ingested ${INGESTED} codex session(s) for ${DATE} → ${SIGNAL_FILE}"
