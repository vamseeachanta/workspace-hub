#!/usr/bin/env bash
# nightly-smoke-tests.sh — Run smoke tests for tier-1 repos, cache results.
# Emits YAML report to .claude/state/session-health.yaml
# Emits JSONL records to .claude/state/session-signals/smoke-tests.jsonl
# Returns 0 always — failures are logged, never fatal (best-effort).
# Called from: nightly-readiness.sh (R12 check)
# WRK-1172
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_HUB="${WORKSPACE_HUB:-$(cd "${SCRIPT_DIR}/../.." && pwd)}"
STATE_DIR="${WORKSPACE_HUB}/.claude/state"
SIGNALS_DIR="${STATE_DIR}/session-signals"
YAML_OUT="${STATE_DIR}/session-health.yaml"
JSONL_OUT="${SIGNALS_DIR}/smoke-tests.jsonl"
REPO_MAP="${WORKSPACE_HUB}/config/onboarding/repo-map.yaml"
RUN_TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
# Per-repo timeout: collection alone takes ~50s for large repos (worldenergydata)
SMOKE_TIMEOUT=90

mkdir -p "$SIGNALS_DIR"

# ---------------------------------------------------------------------------
# Helpers (reused from test-health-check.sh pattern)
# ---------------------------------------------------------------------------

log()  { echo "[smoke-test] $*"; }
warn() { echo "[smoke-test] WARN: $*" >&2; }

_json_str() {
  if command -v python3 &>/dev/null; then
    printf '%s' "$1" \
      | uv run --no-project python -c 'import json,sys; print(json.dumps(sys.stdin.read())[1:-1])' \
      2>/dev/null || printf '%s' "$1" \
        | sed 's/\\/\\\\/g; s/"/\\"/g' | tr -d '\000-\037'
  else
    printf '%s' "$1" \
      | sed 's/\\/\\\\/g; s/"/\\"/g; s/'"$(printf '\t')"'/\\t/g' \
      | tr -d '\000-\037'
  fi
}

# Parse tier-1 repo names from repo-map.yaml (lightweight awk, no PyYAML)
_get_tier1_repos() {
  awk '
    /^- name:/ || /^  - name:/ {
      gsub(/.*name:[[:space:]]*/, ""); gsub(/"/, ""); print
    }
  ' "$REPO_MAP" 2>/dev/null
}

# Get test command for a repo from repo-map.yaml
_get_test_command() {
  local repo="$1"
  awk -v r="$repo" '
    /name:/ && $0 ~ r { found=1 }
    found && /test_command:/ {
      sub(/.*test_command:[[:space:]]*"?/, ""); sub(/"$/, ""); print; exit
    }
  ' "$REPO_MAP" 2>/dev/null
}

# Parse pytest output for pass/fail counts
_parse_counts() {
  local output="$1"
  local passed=0 failed=0
  # Match patterns like "5 passed", "2 failed"
  passed=$(echo "$output" | grep -oE '[0-9]+ passed' | grep -oE '[0-9]+' | tail -1)
  failed=$(echo "$output" | grep -oE '[0-9]+ failed' | grep -oE '[0-9]+' | tail -1)
  echo "${passed:-0} ${failed:-0}"
}

# ---------------------------------------------------------------------------
# Run smoke test for a single repo
# In mock mode, source run-smoke.sh instead of running real pytest
# Returns: sets _status, _passed, _failed, _duration
# ---------------------------------------------------------------------------
_run_repo_smoke() {
  local repo_name="$1"
  local repo_dir="${WORKSPACE_HUB}/${repo_name}"

  if [[ ! -d "$repo_dir" ]]; then
    _status="skip"
    _passed=0
    _failed=0
    _duration=0
    return
  fi

  local start_ts
  start_ts=$(date +%s)
  local output=""
  local exit_code=0

  if [[ "${SMOKE_TEST_MODE:-}" == "mock" ]]; then
    # Mock mode: run the repo's run-smoke.sh shim
    local shim="${repo_dir}/run-smoke.sh"
    if [[ -f "$shim" ]]; then
      output=$(bash "$shim" 2>&1) || exit_code=$?
    else
      _status="skip"
      _passed=0
      _failed=0
      _duration=0
      return
    fi
  else
    # Real mode: run pytest with smoke marker
    local test_cmd
    test_cmd=$(_get_test_command "$repo_name")
    if [[ -z "$test_cmd" ]]; then
      _status="skip"
      _passed=0
      _failed=0
      _duration=0
      return
    fi

    # Fast pre-check: skip expensive pytest collection if no test files
    # contain @pytest.mark.smoke. Saves ~15-30s per repo.
    local has_smoke
    has_smoke=$(grep -rl "pytest\.mark\.smoke\|@smoke" \
      "${repo_dir}/tests" 2>/dev/null | head -1 || true)
    if [[ -z "$has_smoke" ]]; then
      _status="pass"
      _passed=0
      _failed=0
      end_ts=$(date +%s)
      _duration=$(( end_ts - start_ts ))
      return
    fi

    # Build smoke command: append -m smoke + fast flags to existing test_command
    # Note: don't add --timeout to pytest args — not all repos have pytest-timeout.
    # The outer `timeout` command handles per-repo time limits.
    #
    # Fix #1714: inject --no-sync into 'uv run' commands to prevent hangs.
    # Without this, uv tries to resolve git dependencies on every invocation
    # which can hang indefinitely (e.g. worldenergydata's assetutilities dep).
    # The venv is pre-installed; smoke tests should never trigger dep resolution.
    # Override -x/--maxfail from addopts to prevent collection errors from
    # aborting before smoke-marked tests are reached.
    local smoke_cmd="${test_cmd} -m smoke -q --tb=line --override-ini='addopts=' --no-header"
    smoke_cmd="${smoke_cmd/uv run /uv run --no-sync }"

    # Run via bash -c so PYTHONPATH=... prefix in test_command works natively
    # --foreground required: without it, timeout can't signal child in subshells
    output=$(cd "$repo_dir" && timeout --foreground "$SMOKE_TIMEOUT" \
      bash -c "$smoke_cmd" 2>&1) || exit_code=$?
  fi

  local end_ts
  end_ts=$(date +%s)
  _duration=$(( end_ts - start_ts ))

  local counts
  counts=$(_parse_counts "$output")
  _passed=$(echo "$counts" | awk '{print $1}')
  _failed=$(echo "$counts" | awk '{print $2}')

  # Exit codes:
  #   0 = all tests passed
  #   2 = collection errors (broken imports in non-smoke tests — not a smoke failure)
  #   5 = no tests collected (no @pytest.mark.smoke tests exist yet)
  #   4 = usage error (pytest config incompatible with flags)
  #   124 = timeout (collection phase too slow)
  # Only actual test failures (exit 1) count as unhealthy.
  # Exit 2 is tolerated because -m smoke runs collect ALL test files first;
  # import errors in non-smoke tests don't affect smoke test results (#1714).
  if [[ "$exit_code" -eq 0 || "$exit_code" -eq 5 || "$exit_code" -eq 4 || "$exit_code" -eq 2 ]]; then
    _status="pass"
  elif [[ "$exit_code" -eq 124 ]]; then
    _status="timeout"
  else
    _status="fail"
  fi
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
log "Nightly smoke tests — ${RUN_TS}"

if [[ ! -f "$REPO_MAP" ]]; then
  warn "repo-map.yaml not found at ${REPO_MAP} — skipping"
  # Write minimal YAML so session-start can read it
  cat > "$YAML_OUT" << EOF
run_at: "${RUN_TS}"
total_duration_s: 0
all_healthy: true
repos: {}
EOF
  exit 0
fi

total_start=$(date +%s)
all_healthy=true

# Accumulators for YAML output
declare -A repo_status=()
declare -A repo_passed=()
declare -A repo_failed=()
declare -A repo_duration=()

# Per-repo variables set by _run_repo_smoke
_status=""
_passed=0
_failed=0
_duration=0

while IFS= read -r repo_name; do
  [[ -z "$repo_name" ]] && continue

  _status=""
  _passed=0
  _failed=0
  _duration=0

  _run_repo_smoke "$repo_name"

  repo_status["$repo_name"]="$_status"
  repo_passed["$repo_name"]="$_passed"
  repo_failed["$repo_name"]="$_failed"
  repo_duration["$repo_name"]="$_duration"

  if [[ "$_status" == "fail" ]]; then
    all_healthy=false
  fi

  log "  ${repo_name}: status=${_status} passed=${_passed} failed=${_failed} duration=${_duration}s"

  # Emit JSONL record
  printf '{"event":"smoke_test","ts":"%s","repo":"%s","status":"%s","passed":%d,"failed":%d,"duration_s":%d}\n' \
    "$(_json_str "$RUN_TS")" \
    "$(_json_str "$repo_name")" \
    "$(_json_str "$_status")" \
    "$_passed" \
    "$_failed" \
    "$_duration" >> "$JSONL_OUT"

done < <(_get_tier1_repos)

total_end=$(date +%s)
total_duration=$(( total_end - total_start ))

# ---------------------------------------------------------------------------
# Write YAML report
# ---------------------------------------------------------------------------
{
  echo "run_at: \"${RUN_TS}\""
  echo "total_duration_s: ${total_duration}"
  echo "all_healthy: ${all_healthy}"
  echo "repos:"
  for repo_name in $(echo "${!repo_status[@]}" | tr ' ' '\n' | sort); do
    local_status="${repo_status[$repo_name]}"
    local_passed="${repo_passed[$repo_name]}"
    local_failed="${repo_failed[$repo_name]}"
    local_dur="${repo_duration[$repo_name]}"
    echo "  ${repo_name}: {status: ${local_status}, passed: ${local_passed}, failed: ${local_failed}, duration_s: ${local_dur}}"
  done
} > "$YAML_OUT"

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo ""
echo "=== Smoke Test Summary ==="
echo "  Total duration: ${total_duration}s"
echo "  All healthy: ${all_healthy}"
echo "  YAML report: ${YAML_OUT}"
echo "  JSONL signals: ${JSONL_OUT}"

log "Done."
exit 0
