#!/usr/bin/env bash
# run-review-plan.sh — Stage Group 2: Review Plan (stages 5-7)
#
# Single-session use. Stages 5 and 7 are human gates.
#
# Usage:
#   bash scripts/work-queue/run-review-plan.sh WRK-NNN start N
#   bash scripts/work-queue/run-review-plan.sh WRK-NNN exit N
#   bash scripts/work-queue/run-review-plan.sh WRK-NNN status
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
WRK_ID="${1:?Usage: run-review-plan.sh WRK-NNN start|exit|status N}"
ACTION="${2:-status}"
STAGE="${3:-}"

VALID_STAGES="5 6 7"

case "$ACTION" in
    start)
        [[ -z "$STAGE" ]] && { echo "Usage: run-review-plan.sh $WRK_ID start N (N=5-7)" >&2; exit 1; }
        echo "$VALID_STAGES" | grep -qw "$STAGE" || { echo "Stage $STAGE not in Group 2 (5-7)" >&2; exit 1; }
        echo "━━━ Group 2 REVIEW PLAN: Starting Stage $STAGE ━━━"
        if [[ "$STAGE" == "5" || "$STAGE" == "7" ]]; then
            echo "  *** HUMAN GATE — user approval required before exit ***"
        fi
        uv run --no-project python "$REPO_ROOT/scripts/work-queue/start_stage.py" "$WRK_ID" "$STAGE"
        echo ""
        echo "━━━ Do stage $STAGE work now. When done: bash scripts/work-queue/run-review-plan.sh $WRK_ID exit $STAGE ━━━"
        ;;
    exit)
        [[ -z "$STAGE" ]] && { echo "Usage: run-review-plan.sh $WRK_ID exit N (N=5-7)" >&2; exit 1; }
        echo "━━━ Group 2 REVIEW PLAN: Exiting Stage $STAGE ━━━"
        uv run --no-project python "$REPO_ROOT/scripts/work-queue/exit_stage.py" "$WRK_ID" "$STAGE"
        NEXT=$((STAGE + 1))
        if [[ "$NEXT" -le 7 ]]; then
            echo ""
            echo "→ Next: bash scripts/work-queue/run-review-plan.sh $WRK_ID start $NEXT"
        else
            echo ""
            echo "╔════════════════════════════════════════════════╗"
            echo "║  Group 2 COMPLETE — Plan approved (stages 5-7) ║"
            echo "║  HUMAN STOP: Plan is final.                     ║"
            echo "║  Next: bash scripts/work-queue/run-execute.sh $WRK_ID start 8 ║"
            echo "╚════════════════════════════════════════════════╝"
        fi
        ;;
    status)
        echo "╔════════════════════════════════════════════════╗"
        echo "║  Stage Group 2: REVIEW PLAN (stages 5-7)       ║"
        echo "║  WRK: $WRK_ID                                  ║"
        echo "║  Stages 5,7 = HUMAN GATES                      ║"
        echo "╚════════════════════════════════════════════════╝"
        ;;
    *)
        echo "Unknown action: $ACTION" >&2; exit 1 ;;
esac
