#!/usr/bin/env bash
# run-plan.sh — Stage Group 1: Plan (stages 1-4)
#
# Usage: bash scripts/work-queue/run-plan.sh WRK-NNN
#
# Runs stages 1→2→3→4 sequentially via start_stage/exit_stage.
# Opens HTML at Stage 1. Ends after Stage 4 — user reviews plan
# then runs run-review-plan.sh when ready.
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
WRK_ID="${1:?Usage: run-plan.sh WRK-NNN}"

echo "╔════════════════════════════════════════════════╗"
echo "║  Stage Group 1: PLAN (stages 1-4)              ║"
echo "║  WRK: $WRK_ID                                  ║"
echo "╚════════════════════════════════════════════════╝"

for STAGE in 1 2 3 4; do
    echo ""
    echo "━━━ Starting Stage $STAGE ━━━"
    uv run --no-project python "$REPO_ROOT/scripts/work-queue/start_stage.py" "$WRK_ID" "$STAGE"

    echo ""
    echo "━━━ Stage $STAGE work: agent should do the work now ━━━"
    echo "  When done, this script will call exit_stage.py $WRK_ID $STAGE"
    echo "  Press ENTER when stage $STAGE work is complete..."
    read -r

    echo "━━━ Exiting Stage $STAGE ━━━"
    uv run --no-project python "$REPO_ROOT/scripts/work-queue/exit_stage.py" "$WRK_ID" "$STAGE"
done

echo ""
echo "╔════════════════════════════════════════════════╗"
echo "║  Group 1 COMPLETE — Plan drafted (stages 1-4)  ║"
echo "║                                                 ║"
echo "║  HUMAN STOP: Review the plan in your browser.   ║"
echo "║  When ready, run:                               ║"
echo "║    bash scripts/work-queue/run-review-plan.sh $WRK_ID ║"
echo "╚════════════════════════════════════════════════╝"
