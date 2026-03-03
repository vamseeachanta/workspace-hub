#!/usr/bin/env bash
# verify-log-presence.sh — Pre-close gate for WRK-687
# Checks all 3 agent log sources on the current machine.
# Checks native session dirs (primary) and orchestrator dirs (cross-review).
# Exit 0 = PASS, Exit 1 = FAIL
set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
ORCH_DIR="${REPO_ROOT}/logs/orchestrator"
MACHINE=$(hostname -s 2>/dev/null || hostname | cut -d. -f1 | tr '[:upper:]' '[:lower:]')
PASS=0
FAIL=0

count_valid_json() {
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

check_claude() {
  local dir="${ORCH_DIR}/claude"
  if [[ ! -d "$dir" ]]; then
    echo "  claude  MISSING dir ${dir}"
    FAIL=$((FAIL + 1)); return
  fi
  local count
  count=$(find "$dir" -name "*.jsonl" | wc -l)
  if [[ "$count" -eq 0 ]]; then
    echo "  claude  NO FILES (*.jsonl) in ${dir}"
    FAIL=$((FAIL + 1)); return
  fi
  local latest
  latest=$(find "$dir" -name "*.jsonl" | sort | tail -1)
  local valid
  valid=$(count_valid_json "$latest")
  echo "  claude  OK  (${count} file(s), latest: $(basename "$latest"), valid JSON: ${valid})"
  PASS=$((PASS + 1))
}

check_codex() {
  # Primary: native ~/.codex/sessions/YYYY/MM/DD/*.jsonl
  local native_dir="${HOME}/.codex/sessions"
  local orch_dir="${ORCH_DIR}/codex"
  local native_count=0
  local orch_count=0

  [[ -d "$native_dir" ]] && native_count=$(find "$native_dir" -name "*.jsonl" | wc -l)
  [[ -d "$orch_dir" ]]   && orch_count=$(find "$orch_dir" -name "*.log" | wc -l)

  if [[ "$native_count" -gt 0 ]]; then
    local latest
    latest=$(find "$native_dir" -name "*.jsonl" | sort | tail -1)
    echo "  codex   OK  (native: ${native_count} session(s), latest: $(basename "$latest"); orchestrator: ${orch_count} cross-review(s))"
    PASS=$((PASS + 1))
  elif [[ "$orch_count" -gt 0 ]]; then
    echo "  codex   OK  (native: 0, orchestrator: ${orch_count} cross-review(s))"
    PASS=$((PASS + 1))
  else
    echo "  codex   NO FILES — native ${native_dir} empty, orchestrator ${orch_dir} empty"
    FAIL=$((FAIL + 1))
  fi
}

check_gemini() {
  # Primary: native ~/.gemini/tmp/<project>/chats/session-*.json
  local project
  project=$(basename "$REPO_ROOT")
  local native_dir="${HOME}/.gemini/tmp/${project}/chats"
  local orch_dir="${ORCH_DIR}/gemini"
  local native_count=0
  local orch_count=0

  [[ -d "$native_dir" ]] && native_count=$(find "$native_dir" -name "session-*.json" | wc -l)
  [[ -d "$orch_dir" ]]   && orch_count=$(find "$orch_dir" -name "*.log" | wc -l)

  if [[ "$native_count" -gt 0 ]]; then
    local latest
    latest=$(find "$native_dir" -name "session-*.json" | sort | tail -1)
    echo "  gemini  OK  (native: ${native_count} session(s), latest: $(basename "$latest"); orchestrator: ${orch_count} cross-review(s))"
    PASS=$((PASS + 1))
  elif [[ "$orch_count" -gt 0 ]]; then
    echo "  gemini  OK  (native: 0, orchestrator: ${orch_count} cross-review(s))"
    PASS=$((PASS + 1))
  else
    echo "  gemini  NO FILES — native ${native_dir} empty, orchestrator ${orch_dir} empty"
    FAIL=$((FAIL + 1))
  fi
}

echo "[verify-log-presence] Machine: ${MACHINE}"
check_claude
check_codex
check_gemini
echo ""
if [[ $FAIL -eq 0 ]]; then
  echo "PASS"
  exit 0
else
  echo "FAIL (${FAIL} agent(s) missing/invalid)"
  exit 1
fi
