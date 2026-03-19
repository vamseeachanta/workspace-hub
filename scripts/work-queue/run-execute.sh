#!/usr/bin/env bash
# run-execute.sh — Stage Group 3: Execute (stages 8-16)
#
# Single-session use. All stages auto-proceed (R-26).
#
# Usage:
#   bash scripts/work-queue/run-execute.sh WRK-NNN start N
#   bash scripts/work-queue/run-execute.sh WRK-NNN exit N
#   bash scripts/work-queue/run-execute.sh WRK-NNN status
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
WRK_ID="${1:?Usage: run-execute.sh WRK-NNN start|exit|status N}"
ACTION="${2:-status}"
STAGE="${3:-}"

VALID_STAGES="8 9 10 11 12 13 14 15 16"

case "$ACTION" in
    start)
        [[ -z "$STAGE" ]] && { echo "Usage: run-execute.sh $WRK_ID start N (N=8-16)" >&2; exit 1; }
        echo "$VALID_STAGES" | grep -qw "$STAGE" || { echo "Stage $STAGE not in Group 3 (8-16)" >&2; exit 1; }
        echo "━━━ Group 3 EXECUTE: Starting Stage $STAGE ━━━"
        uv run --no-project python "$REPO_ROOT/scripts/work-queue/start_stage.py" "$WRK_ID" "$STAGE"
        echo ""
        echo "━━━ Do stage $STAGE work now. When done: bash scripts/work-queue/run-execute.sh $WRK_ID exit $STAGE ━━━"
        ;;
    exit)
        [[ -z "$STAGE" ]] && { echo "Usage: run-execute.sh $WRK_ID exit N (N=8-16)" >&2; exit 1; }
        echo "━━━ Group 3 EXECUTE: Exiting Stage $STAGE ━━━"
        uv run --no-project python "$REPO_ROOT/scripts/work-queue/exit_stage.py" "$WRK_ID" "$STAGE"
        NEXT=$((STAGE + 1))
        if [[ "$NEXT" -le 16 ]]; then
            echo ""
            echo "→ Next: bash scripts/work-queue/run-execute.sh $WRK_ID start $NEXT"
        else
            echo ""
            echo "╔════════════════════════════════════════════════╗"
            echo "║  Group 3 COMPLETE — Executed (stages 8-16)      ║"
            echo "║  HUMAN STOP: Review implementation.              ║"
            echo "║  Next: bash scripts/work-queue/run-close.sh $WRK_ID start 17 ║"
            echo "╚════════════════════════════════════════════════╝"
        fi
        ;;
    status)
        echo "╔════════════════════════════════════════════════╗"
        echo "║  Stage Group 3: EXECUTE (stages 8-16)           ║"
        echo "║  WRK: $WRK_ID — all auto-proceed (R-26)        ║"
        echo "╚════════════════════════════════════════════════╝"
        ;;
    *)
        echo "Unknown action: $ACTION" >&2; exit 1 ;;
esac
