#!/usr/bin/env bash
# run-review-plan.sh — Stage Group 2: Review Plan (stages 5-7)
#
# Usage: bash scripts/work-queue/run-review-plan.sh WRK-NNN
#
# Runs stages 5→6→7 sequentially. Stages 5 and 7 are human gates —
# the script pauses and waits for user approval at each.
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
WRK_ID="${1:?Usage: run-review-plan.sh WRK-NNN}"

echo "╔════════════════════════════════════════════════╗"
echo "║  Stage Group 2: REVIEW PLAN (stages 5-7)       ║"
echo "║  WRK: $WRK_ID                                  ║"
echo "╚════════════════════════════════════════════════╝"

# Stage 5 — Human gate: User Review Plan Draft
echo ""
echo "━━━ Starting Stage 5: User Review - Plan Draft ━━━"
uv run --no-project python "$REPO_ROOT/scripts/work-queue/start_stage.py" "$WRK_ID" 5
echo ""
echo "  HUMAN GATE: Review the plan with the agent."
echo "  Agent walks through ACs, pseudocode, test plan."
echo "  When done, press ENTER to confirm stage 5 work complete..."
read -r
uv run --no-project python "$REPO_ROOT/scripts/work-queue/exit_stage.py" "$WRK_ID" 5

# Stage 6 — Auto: Cross-Review
echo ""
echo "━━━ Starting Stage 6: Cross-Review ━━━"
uv run --no-project python "$REPO_ROOT/scripts/work-queue/start_stage.py" "$WRK_ID" 6
echo ""
echo "  Agent dispatches cross-review to 3 providers."
echo "  Press ENTER when stage 6 work complete..."
read -r
uv run --no-project python "$REPO_ROOT/scripts/work-queue/exit_stage.py" "$WRK_ID" 6

# Stage 7 — Human gate: User Review Plan Final
echo ""
echo "━━━ Starting Stage 7: User Review - Plan Final ━━━"
uv run --no-project python "$REPO_ROOT/scripts/work-queue/start_stage.py" "$WRK_ID" 7
echo ""
echo "  HUMAN GATE: Review cross-review findings."
echo "  All P1 findings must be resolved."
echo "  When done, press ENTER to confirm stage 7 work complete..."
read -r
uv run --no-project python "$REPO_ROOT/scripts/work-queue/exit_stage.py" "$WRK_ID" 7

echo ""
echo "╔════════════════════════════════════════════════╗"
echo "║  Group 2 COMPLETE — Plan approved (stages 5-7) ║"
echo "║                                                 ║"
echo "║  HUMAN STOP: Plan is final. When ready:         ║"
echo "║    bash scripts/work-queue/run-execute.sh $WRK_ID ║"
echo "╚════════════════════════════════════════════════╝"
