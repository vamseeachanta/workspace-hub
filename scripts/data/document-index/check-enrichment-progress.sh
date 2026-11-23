#!/usr/bin/env bash
# Check readability enrichment progress
set -euo pipefail

INDEX_TMP="data/document-index/index.jsonl.tmp"
INDEX_ORIG="data/document-index/index.jsonl"
PID_FILE="logs/enrichment/enrich-readability.pid"
LOG_FILE="logs/enrichment/enrich-readability-$(date +%Y%m%d).log"

TOTAL=$(wc -l < "$INDEX_ORIG")
DONE=$(wc -l < "$INDEX_TMP" 2>/dev/null || echo 0)
PCT=$(( DONE * 100 / TOTAL ))

echo "Readability enrichment progress"
echo "  Records: ${DONE} / ${TOTAL} (${PCT}%)"
echo "  Tmp file: $(ls -lh "$INDEX_TMP" 2>/dev/null | awk '{print $5}')"

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        ELAPSED=$(ps -p "$PID" -o etime= 2>/dev/null | xargs)
        RSS=$(ps -p "$PID" -o rss= 2>/dev/null | xargs)
        echo "  Process: PID=${PID} running (${ELAPSED}, ${RSS}KB)"
    else
        echo "  Process: PID=${PID} NOT running"
    fi
fi

if [ -f "$LOG_FILE" ] && [ -s "$LOG_FILE" ]; then
    echo "  Last log lines:"
    tail -3 "$LOG_FILE" | sed 's/^/    /'
fi
