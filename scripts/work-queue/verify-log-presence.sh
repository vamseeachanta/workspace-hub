#!/usr/bin/env bash
# verify-log-presence.sh — Pre-close gate for WRK-687
# Checks all 3 agent log dirs on the current machine.
# Exit 0 = PASS, Exit 1 = FAIL
set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
ORCH_DIR="${REPO_ROOT}/logs/orchestrator"
MACHINE=$(hostname -s 2>/dev/null || hostname | cut -d. -f1 | tr '[:upper:]' '[:lower:]')
PASS=0
FAIL=0

count_valid_json() {
  # Count valid JSON lines in a file, robustly
  local path="$1"
  python3 -c "
import json, sys
ok=0; total=0
for line in open(sys.argv[1]):
    s=line.strip()
    if not s: continue
    total+=1
    try: json.loads(s); ok+=1
    except: pass
print(f'{ok}/{total}')
" "$path" 2>/dev/null || echo "?/?"
}

check_agent() {
  local agent="$1" ext="$2"
  local dir="${ORCH_DIR}/${agent}"
  if [[ ! -d "$dir" ]]; then
    echo "  ${agent}  MISSING dir ${dir}"
    FAIL=$((FAIL + 1))
    return
  fi
  local count
  count=$(find "$dir" -name "*.${ext}" | wc -l)
  if [[ "$count" -eq 0 ]]; then
    echo "  ${agent}  NO FILES (*.${ext}) in ${dir}"
    FAIL=$((FAIL + 1))
    return
  fi
  if [[ "$ext" == "jsonl" ]]; then
    local latest
    latest=$(find "$dir" -name "*.jsonl" | sort | tail -1)
    local valid
    valid=$(count_valid_json "$latest")
    echo "  ${agent}  OK  (${count} file(s), latest: $(basename "$latest"), valid JSON: ${valid})"
  else
    echo "  ${agent}  OK  (${count} file(s))"
  fi
  PASS=$((PASS + 1))
}

echo "[verify-log-presence] Machine: ${MACHINE}"
check_agent claude jsonl
check_agent codex  log
check_agent gemini log
echo ""
if [[ $FAIL -eq 0 ]]; then
  echo "PASS"
  exit 0
else
  echo "FAIL (${FAIL} agent(s) missing/invalid)"
  exit 1
fi
