#!/usr/bin/env bash
# launch-batch.sh — Launch N parallel Phase B Claude summarisation shards (WRK-309)
#
# Run from workspace-hub root in a SEPARATE terminal (not inside Claude Code):
#   bash scripts/data/document-index/launch-batch.sh [shards=10] [source=all]
#
# Sources: all | og_standards | ace_standards | workspace_spec
# Logs:    data/document-index/logs/claude-shard-N-YYYYMMDD-HHMMSS.log
# Monitor: tail -f data/document-index/logs/claude-shard-*.log
# Status:  grep -h "COMPLETE\|progress\|shard" data/document-index/logs/claude-shard-*.log

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HUB_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
WORKER="$SCRIPT_DIR/phase-b-claude-worker.py"
LOG_DIR="$HUB_ROOT/data/document-index/logs"

TOTAL="${1:-10}"
SOURCE="${2:-all}"

mkdir -p "$LOG_DIR"

echo "=== Phase B Claude batch launch ==="
echo "  Shards : $TOTAL"
echo "  Source : $SOURCE"
echo "  Worker : $WORKER"
echo "  Logs   : $LOG_DIR"
echo "  Start  : $(date)"
echo ""

PIDS=()
for ((i=0; i<TOTAL; i++)); do
    STAMP="$(date +%Y%m%d-%H%M%S)"
    LOG="$LOG_DIR/claude-shard-${i}-${STAMP}.log"
    nohup python3 "$WORKER" \
        --shard "$i" --total "$TOTAL" --source "$SOURCE" \
        >"$LOG" 2>&1 &
    PID=$!
    PIDS+=("$PID")
    echo "  Shard $i  PID $PID  →  $LOG"
done

echo ""
echo "All $TOTAL shards launched."
echo ""
echo "Monitor progress:"
echo "  tail -f $LOG_DIR/claude-shard-*.log"
echo ""
echo "Check completion:"
echo "  grep -h 'COMPLETE' $LOG_DIR/claude-shard-*.log"
echo ""
echo "Count LLM-done summaries:"
echo "  python3 -c \""
echo "  import json; from pathlib import Path"
echo "  d=Path('$HUB_ROOT/data/document-index/summaries')"
echo "  n=sum(1 for f in d.iterdir() if f.suffix=='.json' and json.loads(f.read_text()).get('discipline') if True else False)"
echo "  print('LLM summaries:', n)"
echo "  \""
echo ""
echo "Kill all shards:"
echo "  kill ${PIDS[*]}"
