#!/usr/bin/env bash
# skill-evals.sh — Skill eval health summary for /today (WRK-1009)
set -uo pipefail
STATE_DIR="${WS_HUB:-.}/.claude/state"
EVAL_DIR="${STATE_DIR}/skill-eval-results"
RETIREMENT_DIR="${STATE_DIR}/skill-retirement-candidates"

echo "## Skill Eval Health"

latest_eval=$(ls "${EVAL_DIR}/"*.jsonl 2>/dev/null | sort | tail -1)
if [[ -z "$latest_eval" ]]; then
  echo "  No skill eval report yet — run nightly cron to generate."
  exit 0
fi

pass=$(grep -c '"result":"pass"' "$latest_eval" 2>/dev/null || echo 0)
fail=$(grep -c '"result":"fail"' "$latest_eval" 2>/dev/null || echo 0)
skip=$(grep -c '"result":"skip"' "$latest_eval" 2>/dev/null || echo 0)
echo "  Evals: PASS=$pass FAIL=$fail SKIP=$skip ($(basename "$latest_eval"))"

latest_retire=$(ls "${RETIREMENT_DIR}/"*.json 2>/dev/null | sort | tail -1)
if [[ -n "$latest_retire" ]]; then
  count=$(uv run --no-project python -c \
    "import json,sys; d=json.load(open('$latest_retire')); print(len(d.get('candidates',[])))" \
    2>/dev/null || echo "?")
  echo "  Retirement candidates: $count (see $latest_retire)"
fi
