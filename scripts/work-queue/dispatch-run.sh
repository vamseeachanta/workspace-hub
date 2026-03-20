#!/usr/bin/env bash
# dispatch-run.sh — Bridge between /work run and group runners
#
# Reads checkpoint.yaml, maps stage to group runner, prints exact command.
# Eliminates agent sub-skill browsing by giving a single actionable instruction.
#
# Usage:
#   bash scripts/work-queue/dispatch-run.sh [WRK-NNN]
#   (if no arg, reads from .claude/state/active-wrk)
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
SCRIPTS="$REPO_ROOT/scripts/work-queue"

# ── Resolve WRK ID ───────────────────────────────────────────────────────────
WRK_ID="${1:-}"
if [[ -z "$WRK_ID" ]]; then
    _state="$REPO_ROOT/.claude/state/active-wrk"
    [[ -f "$_state" ]] && WRK_ID="$(head -n1 "$_state" | tr -d '[:space:]')"
fi
if [[ -z "$WRK_ID" ]]; then
    echo "ERROR: No WRK ID. Run: bash scripts/work-queue/set-active-wrk.sh WRK-NNN" >&2
    exit 1
fi

# ── Check if archived ────────────────────────────────────────────────────────
QUEUE="$REPO_ROOT/.claude/work-queue"
if find "$QUEUE/archive" -maxdepth 2 -name "${WRK_ID}.md" 2>/dev/null | grep -q .; then
    echo "✔ $WRK_ID is already archived — nothing to do."
    exit 0
fi

# ── Check item exists ────────────────────────────────────────────────────────
_found=false
for _dir in pending working blocked done; do
    [[ -f "$QUEUE/$_dir/${WRK_ID}.md" ]] && { _found=true; break; }
done
if [[ "$_found" == "false" ]]; then
    echo "ERROR: $WRK_ID not found in pending/working/blocked/done" >&2
    exit 1
fi

# ── Read checkpoint ──────────────────────────────────────────────────────────
ASSETS="$QUEUE/assets/$WRK_ID"
CP="$ASSETS/checkpoint.yaml"
STAGE=1
STAGE_NAME="Capture"
if [[ -f "$CP" ]]; then
    _raw="$(awk -F': ' '/^current_stage:/{print $2}' "$CP" | tr -d '"' | tr -d "'" | tr -d '[:space:]')"
    if [[ "$_raw" == "complete" ]]; then
        echo "✔ $WRK_ID lifecycle complete — archive if not done."
        exit 0
    fi
    if [[ -n "$_raw" ]]; then
        STAGE="$_raw"
        _name="$(awk -F': ' '/^stage_name:/{print $2}' "$CP" | tr -d '"' | tr -d "'")"
        [[ -n "$_name" ]] && STAGE_NAME="$_name"
    fi
fi

# ── Map stage to group runner ────────────────────────────────────────────────
case "$STAGE" in
    1|2|3|4)         RUNNER="run-plan.sh"        ; GROUP="PLAN (1-4)" ;;
    5|6|7)           RUNNER="run-review-plan.sh"  ; GROUP="REVIEW PLAN (5-7)" ;;
    8|9|10|11|12|13|14|15|16) RUNNER="run-execute.sh" ; GROUP="EXECUTE (8-16)" ;;
    17|18|19|20)     RUNNER="run-close.sh"        ; GROUP="CLOSE (17-20)" ;;
    *) echo "ERROR: Unknown stage $STAGE" >&2; exit 1 ;;
esac

# ── Check human gate ─────────────────────────────────────────────────────────
HUMAN_GATE="no"
if bash "$SCRIPTS/is-human-gate.sh" "$STAGE" 2>/dev/null; then
    HUMAN_GATE="yes"
fi

# ── Print dispatch ───────────────────────────────────────────────────────────
echo "━━━ DISPATCH: $WRK_ID ━━━"
echo "Stage: $STAGE ($STAGE_NAME) | Group: $GROUP | Human gate: $HUMAN_GATE"
echo ""
if [[ "$HUMAN_GATE" == "yes" ]]; then
    echo "WAITING: Stage $STAGE requires user approval before proceeding."
    echo "→ When approved: bash $SCRIPTS/$RUNNER $WRK_ID start $STAGE"
else
    echo "→ bash $SCRIPTS/$RUNNER $WRK_ID start $STAGE"
fi
