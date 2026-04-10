#!/usr/bin/env bash
# skill-evals.sh — Skill eval health summary for /today (WRK-1009, #1562)
set -uo pipefail
STATE_DIR="${WS_HUB:-.}/.claude/state"
EVAL_DIR="${STATE_DIR}/skill-eval-results"
RETIREMENT_DIR="${STATE_DIR}/skill-retirement-candidates"
HEALTH_DIR="${STATE_DIR}/skill-health"

echo "## Skill Eval Health"

latest_eval=$(ls "${EVAL_DIR}/"*.jsonl 2>/dev/null | sort | tail -1)
if [[ -z "$latest_eval" ]]; then
  echo "  No skill eval report yet — run nightly cron to generate."
  exit 0
fi

pass=$(grep -c '"result"[: ]*"pass"' "$latest_eval" 2>/dev/null || true)
pass=${pass:-0}; pass=$(echo "$pass" | tr -d '[:space:]'); pass=${pass:-0}
fail=$(grep -c '"result"[: ]*"fail"' "$latest_eval" 2>/dev/null || true)
fail=${fail:-0}; fail=$(echo "$fail" | tr -d '[:space:]'); fail=${fail:-0}
skip=$(grep -c '"result"[: ]*"skip"' "$latest_eval" 2>/dev/null || true)
skip=${skip:-0}; skip=$(echo "$skip" | tr -d '[:space:]'); skip=${skip:-0}
echo "  Evals: PASS=$pass FAIL=$fail SKIP=$skip ($(basename "$latest_eval"))"

latest_retire=$(ls "${RETIREMENT_DIR}/"*.json 2>/dev/null | sort | tail -1)
if [[ -n "$latest_retire" ]]; then
  count=$(uv run --no-project python -c \
    "import json,sys; d=json.load(open('$latest_retire')); print(len(d.get('candidates',[])))" \
    2>/dev/null || echo "?")
  echo "  Retirement candidates: $count (see $latest_retire)"
fi

# ---------------------------------------------------------------------------
# Skill Health Dashboard summary (#1562)
# ---------------------------------------------------------------------------
latest_health=$(ls "${HEALTH_DIR}/"*.json 2>/dev/null | sort | tail -1)
if [[ -n "$latest_health" ]]; then
  health_data=$(uv run --no-project python -c "
import json, sys
try:
    d = json.load(open('$latest_health'))
    score = d.get('overall_score', '?')
    actions = d.get('actions', [])
    print(f'SCORE:{score}')
    for a in actions[:5]:
        print(f'ACTION:{a}')
except Exception as e:
    print(f'ERROR:{e}', file=sys.stderr)
" 2>/dev/null || true)

  if [[ -n "$health_data" ]]; then
    score=$(echo "$health_data" | grep '^SCORE:' | head -1 | cut -d: -f2)
    if [[ -n "$score" ]]; then
      echo ""
      echo "  Skill Health Score: ${score}/100 ($(basename "$latest_health"))"
      action_lines=$(echo "$health_data" | grep '^ACTION:' | head -5)
      if [[ -n "$action_lines" ]]; then
        echo "  Top actions:"
        i=1
        while IFS= read -r line; do
          action="${line#ACTION:}"
          echo "    ${i}. ${action}"
          (( i++ ))
        done <<< "$action_lines"
      fi
    fi
  fi
fi
