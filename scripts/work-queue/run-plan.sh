#!/usr/bin/env bash
# run-plan.sh — Stage Group 1: Plan (stages 1-4)
#
# Single-session use: agent calls this to start/exit ONE stage at a time.
#
# Usage:
#   bash scripts/work-queue/run-plan.sh WRK-NNN start N   # start stage N
#   bash scripts/work-queue/run-plan.sh WRK-NNN exit N    # exit stage N
#   bash scripts/work-queue/run-plan.sh WRK-NNN status    # show progress
#
# Agent workflow:
#   1. start 1 → do stage 1 work → exit 1
#   2. start 2 → do stage 2 work → exit 2
#   3. start 3 → do stage 3 work → exit 3
#   4. start 4 → do stage 4 work → exit 4
#   → HUMAN STOP: run run-review-plan.sh next
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
WRK_ID="${1:?Usage: run-plan.sh WRK-NNN start|exit|status N}"
ACTION="${2:-status}"
STAGE="${3:-}"

VALID_STAGES="1 2 3 4"

case "$ACTION" in
    start)
        [[ -z "$STAGE" ]] && { echo "Usage: run-plan.sh $WRK_ID start N (N=1-4)" >&2; exit 1; }
        echo "$VALID_STAGES" | grep -qw "$STAGE" || { echo "Stage $STAGE not in Group 1 (1-4)" >&2; exit 1; }
        echo "━━━ Group 1 PLAN: Starting Stage $STAGE ━━━"
        uv run --no-project python "$REPO_ROOT/scripts/work-queue/start_stage.py" "$WRK_ID" "$STAGE"
        echo ""
        echo "━━━ Do stage $STAGE work now. When done: bash scripts/work-queue/run-plan.sh $WRK_ID exit $STAGE ━━━"
        ;;
    exit)
        [[ -z "$STAGE" ]] && { echo "Usage: run-plan.sh $WRK_ID exit N (N=1-4)" >&2; exit 1; }
        echo "━━━ Group 1 PLAN: Exiting Stage $STAGE ━━━"
        uv run --no-project python "$REPO_ROOT/scripts/work-queue/exit_stage.py" "$WRK_ID" "$STAGE"
        # Suggest next step
        NEXT=$((STAGE + 1))
        if [[ "$NEXT" -le 4 ]]; then
            echo ""
            echo "→ Next: bash scripts/work-queue/run-plan.sh $WRK_ID start $NEXT"
        else
            echo ""
            echo "╔════════════════════════════════════════════════╗"
            echo "║  Group 1 COMPLETE — Plan drafted (stages 1-4)  ║"
            echo "║  HUMAN STOP: Review plan in browser.            ║"
            echo "║  Next: bash scripts/work-queue/run-review-plan.sh $WRK_ID start 5 ║"
            echo "╚════════════════════════════════════════════════╝"
        fi
        ;;
    status)
        echo "╔════════════════════════════════════════════════╗"
        echo "║  Stage Group 1: PLAN (stages 1-4)              ║"
        echo "║  WRK: $WRK_ID                                  ║"
        echo "╚════════════════════════════════════════════════╝"
        echo ""
        echo "Stages: 1=Capture 2=Resource-Intel 3=Triage 4=Plan-Draft"
        echo "Usage:"
        echo "  bash scripts/work-queue/run-plan.sh $WRK_ID start 1"
        echo "  (do work)"
        echo "  bash scripts/work-queue/run-plan.sh $WRK_ID exit 1"
        echo "  bash scripts/work-queue/run-plan.sh $WRK_ID start 2"
        echo "  ..."
        ;;
    *)
        echo "Unknown action: $ACTION (use start|exit|status)" >&2
        exit 1
        ;;
esac
