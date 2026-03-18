#!/usr/bin/env bash
# run-close.sh — Stage Group 4: Close (stages 17-20)
#
# Usage: bash scripts/work-queue/run-close.sh WRK-NNN
#
# Runs stages 17→18→19→20. Stage 17 is a human gate —
# pauses for user approval before close and archive.
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
WRK_ID="${1:?Usage: run-close.sh WRK-NNN}"

echo "╔════════════════════════════════════════════════╗"
echo "║  Stage Group 4: CLOSE (stages 17-20)            ║"
echo "║  WRK: $WRK_ID                                  ║"
echo "╚════════════════════════════════════════════════╝"

# Stage 17 — Human gate: User Review Implementation
echo ""
echo "━━━ Starting Stage 17: User Review - Implementation ━━━"
uv run --no-project python "$REPO_ROOT/scripts/work-queue/start_stage.py" "$WRK_ID" 17
echo ""
echo "  HUMAN GATE: Review stages 10-16 evidence."
echo "  Agent walks through implementation, tests, cross-review, gates."
echo "  When done, press ENTER to confirm stage 17 work complete..."
read -r
uv run --no-project python "$REPO_ROOT/scripts/work-queue/exit_stage.py" "$WRK_ID" 17

# Stages 18-20 — Auto: Reclaim, Close, Archive
for STAGE in 18 19 20; do
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
echo "║  WRK $WRK_ID — LIFECYCLE COMPLETE               ║"
echo "║  All 20 stages done. Archived.                  ║"
echo "╚════════════════════════════════════════════════╝"
