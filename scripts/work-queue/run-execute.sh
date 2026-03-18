#!/usr/bin/env bash
# run-execute.sh — Stage Group 3: Execute (stages 8-16)
#
# Usage: bash scripts/work-queue/run-execute.sh WRK-NNN
#
# Runs stages 8→9→10→11→12→13→14→15→16 sequentially.
# All auto-proceed (R-26). Agent does the bulk of the work here.
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
WRK_ID="${1:?Usage: run-execute.sh WRK-NNN}"

echo "╔════════════════════════════════════════════════╗"
echo "║  Stage Group 3: EXECUTE (stages 8-16)           ║"
echo "║  WRK: $WRK_ID                                  ║"
echo "║  All stages auto-proceed (R-26).                ║"
echo "╚════════════════════════════════════════════════╝"

for STAGE in 8 9 10 11 12 13 14 15 16; do
    echo ""
    echo "━━━ Starting Stage $STAGE ━━━"
    uv run --no-project python "$REPO_ROOT/scripts/work-queue/start_stage.py" "$WRK_ID" "$STAGE"

    echo ""
    echo "  Agent does stage $STAGE work."
    echo "  Press ENTER when stage $STAGE work is complete..."
    read -r

    echo "━━━ Exiting Stage $STAGE ━━━"
    uv run --no-project python "$REPO_ROOT/scripts/work-queue/exit_stage.py" "$WRK_ID" "$STAGE"
done

echo ""
echo "╔════════════════════════════════════════════════╗"
echo "║  Group 3 COMPLETE — Executed (stages 8-16)      ║"
echo "║                                                 ║"
echo "║  HUMAN STOP: Review implementation. When ready: ║"
echo "║    bash scripts/work-queue/run-close.sh $WRK_ID ║"
echo "╚════════════════════════════════════════════════╝"
