#!/usr/bin/env bash
# run-close.sh — Stage Group 4: Close (stages 17-20)
#
# Single-session use. Stage 17 is a human gate.
#
# Usage:
#   bash scripts/work-queue/run-close.sh WRK-NNN start N
#   bash scripts/work-queue/run-close.sh WRK-NNN exit N
#   bash scripts/work-queue/run-close.sh WRK-NNN status
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
WRK_ID="${1:?Usage: run-close.sh WRK-NNN start|exit|status N}"
ACTION="${2:-status}"
STAGE="${3:-}"

VALID_STAGES="17 18 19 20"

case "$ACTION" in
    start)
        [[ -z "$STAGE" ]] && { echo "Usage: run-close.sh $WRK_ID start N (N=17-20)" >&2; exit 1; }
        echo "$VALID_STAGES" | grep -qw "$STAGE" || { echo "Stage $STAGE not in Group 4 (17-20)" >&2; exit 1; }
        echo "━━━ Group 4 CLOSE: Starting Stage $STAGE ━━━"
        if [[ "$STAGE" == "17" ]]; then
            echo "  *** HUMAN GATE — user approval required before exit ***"
        fi
        uv run --no-project python "$REPO_ROOT/scripts/work-queue/start_stage.py" "$WRK_ID" "$STAGE"
        echo ""
        echo "━━━ Do stage $STAGE work now. When done: bash scripts/work-queue/run-close.sh $WRK_ID exit $STAGE ━━━"
        ;;
    exit)
        [[ -z "$STAGE" ]] && { echo "Usage: run-close.sh $WRK_ID exit N (N=17-20)" >&2; exit 1; }
        echo "━━━ Group 4 CLOSE: Exiting Stage $STAGE ━━━"
        uv run --no-project python "$REPO_ROOT/scripts/work-queue/exit_stage.py" "$WRK_ID" "$STAGE"
        NEXT=$((STAGE + 1))
        if [[ "$NEXT" -le 20 ]]; then
            echo ""
            echo "→ Next: bash scripts/work-queue/run-close.sh $WRK_ID start $NEXT"
        else
            echo ""
            echo "╔════════════════════════════════════════════════╗"
            echo "║  WRK $WRK_ID — LIFECYCLE COMPLETE               ║"
            echo "║  All 20 stages done. Archived.                  ║"
            echo "╚════════════════════════════════════════════════╝"
        fi
        ;;
    status)
        echo "╔════════════════════════════════════════════════╗"
        echo "║  Stage Group 4: CLOSE (stages 17-20)            ║"
        echo "║  WRK: $WRK_ID — Stage 17 = HUMAN GATE          ║"
        echo "╚════════════════════════════════════════════════╝"
        ;;
    *)
        echo "Unknown action: $ACTION" >&2; exit 1 ;;
esac
