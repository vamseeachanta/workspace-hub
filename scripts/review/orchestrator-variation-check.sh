#!/usr/bin/env bash
# orchestrator-variation-check.sh — Run orchestrator scripts and emit a standardised
# variation-test-results.md under assets/WRK-NNN/
#
# Usage:
#   bash scripts/review/orchestrator-variation-check.sh \
#     --wrk WRK-1002 \
#     --orchestrator claude \
#     --scripts "scripts/work-queue/verify-gate-evidence.py WRK-1002" \
#               "bash tests/work-queue/test-lifecycle-gates.sh" \
#               "uv run --no-project python -m pytest tests/unit/test_circle.py -v"
#
# Output:
#   assets/WRK-NNN/variation-test-results.md  (markdown report)
#   exit 0 if all scripts pass, exit 1 if any fail
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"

# ── argument parsing ────────────────────────────────────────────────────────────

WRK=""
ORCHESTRATOR="claude"
declare -a SCRIPTS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --wrk)        WRK="$2";          shift 2 ;;
    --orchestrator) ORCHESTRATOR="$2"; shift 2 ;;
    --scripts)    shift; while [[ $# -gt 0 && "$1" != --* ]]; do SCRIPTS+=("$1"); shift; done ;;
    *) echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

[ -z "$WRK" ]          && { echo "ERROR: --wrk required" >&2; exit 1; }
[ ${#SCRIPTS[@]} -eq 0 ] && { echo "ERROR: --scripts required" >&2; exit 1; }

ASSET_DIR="${REPO_ROOT}/.claude/work-queue/assets/${WRK}"
OUT="${ASSET_DIR}/variation-test-results.md"
mkdir -p "$ASSET_DIR"

# ── report header ───────────────────────────────────────────────────────────────

RUN_DATE="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
{
  echo "# Variation Tests — ${WRK}"
  echo "wrk_id: ${WRK}"
  echo "run_date: ${RUN_DATE}"
  echo "runner: ${ORCHESTRATOR}"
  echo ""
} > "$OUT"

# ── run each script ─────────────────────────────────────────────────────────────

PASS=0
FAIL=0
TOTAL=0

for script_cmd in "${SCRIPTS[@]}"; do
  TOTAL=$((TOTAL + 1))
  echo "## Test ${TOTAL}: ${script_cmd}" >> "$OUT"
  echo "command: \`${script_cmd}\`" >> "$OUT"

  # Execute; capture output + exit code
  set +e
  output=$(cd "$REPO_ROOT" && eval "$script_cmd" 2>&1)
  exit_code=$?
  set -e

  if [ $exit_code -eq 0 ]; then
    PASS=$((PASS + 1))
    echo "result: PASS" >> "$OUT"
  else
    FAIL=$((FAIL + 1))
    echo "result: FAIL (exit ${exit_code})" >> "$OUT"
  fi

  # Include first 20 lines of output as evidence
  evidence=$(echo "$output" | head -20)
  echo "evidence: |" >> "$OUT"
  while IFS= read -r line; do
    echo "  ${line}" >> "$OUT"
  done <<< "$evidence"
  echo "" >> "$OUT"
done

# ── summary ─────────────────────────────────────────────────────────────────────

{
  echo "## Summary"
  echo "${PASS}/${TOTAL} tests passed."
  if [ $FAIL -eq 0 ]; then
    echo "All gate scripts behave correctly for orchestrator '${ORCHESTRATOR}'."
  else
    echo "⚠ ${FAIL} test(s) failed — review evidence above."
  fi
} >> "$OUT"

echo "→ Report written to ${OUT}" >&2
echo "→ Result: ${PASS}/${TOTAL} passed" >&2

[ $FAIL -eq 0 ]
