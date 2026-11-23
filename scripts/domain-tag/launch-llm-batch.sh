#!/usr/bin/env bash
# launch-llm-batch.sh — Launch N parallel LLM classification shards for riser-eng-job
#
# Run from workspace-hub root in a SEPARATE terminal (not inside Claude Code):
#   bash scripts/domain-tag/launch-llm-batch.sh [shards=10]
#
# Logs:    data/domain-tag/logs/llm-shard-N-YYYYMMDD-HHMMSS.log
# Monitor: tail -f data/domain-tag/logs/llm-shard-*.log

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HUB_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
WORKER="$SCRIPT_DIR/llm-batch-worker.py"
LOG_DIR="$HUB_ROOT/data/domain-tag/logs"

TOTAL="${1:-10}"

mkdir -p "$LOG_DIR"

echo "=== Riser Eng Job LLM Batch Launch ==="
echo "  Shards : $TOTAL"
echo "  Worker : $WORKER"
echo "  Logs   : $LOG_DIR"
echo "  Start  : $(date)"
echo ""

PIDS=()

for ((i=0; i<TOTAL; i++)); do
    STAMP="$(date +%Y%m%d-%H%M%S)"
    LOG="$LOG_DIR/llm-shard-${i}-${STAMP}.log"
    nohup python3 "$WORKER" --shard "$i" --total "$TOTAL" >"$LOG" 2>&1 &
    PID=$!
    PIDS+=("$PID")
    echo "  Shard $i  PID $PID  →  $LOG"
done

echo ""
echo "All $TOTAL shards launched."
echo ""
echo "Monitor progress:"
echo "  tail -f $LOG_DIR/llm-shard-*.log"
echo ""
echo "Kill all shards:"
echo "  kill ${PIDS[*]}"
