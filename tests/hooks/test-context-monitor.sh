#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
SCRIPT="$REPO_ROOT/scripts/hooks/context-monitor.sh"

PASS=0
FAIL=0

pass() { echo "PASS: $1"; (( PASS++ )) || true; }
fail() { echo "FAIL: $1"; (( FAIL++ )) || true; }

# Setup temp dir
TMPDIR_TEST="$(mktemp -d)"
trap 'rm -rf "$TMPDIR_TEST"' EXIT

# Helper: run script with overridden REPO_ROOT and PATH
run_monitor() {
  local fake_root="$1"; shift
  REPO_ROOT="$fake_root" PATH="$TMPDIR_TEST/bin:$PATH" bash "$SCRIPT" "$@"
}

setup_wrk() {
  local fake_root="$1"
  local wrk_id="${2:-WRK-9999}"
  mkdir -p "$fake_root/.claude/state"
  echo "$wrk_id" > "$fake_root/.claude/state/active-wrk"
  mkdir -p "$fake_root/logs"
  mkdir -p "$fake_root/.claude/work-queue/assets/$wrk_id"
}

# Mock checkpoint.sh — success by default
setup_mock_checkpoint() {
  local fake_root="$1"
  local should_fail="${2:-0}"
  mkdir -p "$TMPDIR_TEST/bin"
  # Write a mock that mimics the real checkpoint.sh interface
  cat > "$TMPDIR_TEST/bin/checkpoint_mock.sh" <<MOCKEOF
#!/usr/bin/env bash
if [[ "${should_fail}" == "1" ]]; then
  echo "checkpoint.sh: simulated failure" >&2
  exit 1
fi
exit 0
MOCKEOF
  chmod +x "$TMPDIR_TEST/bin/checkpoint_mock.sh"

  # Override checkpoint.sh in a scripts/work-queue subdir inside fake_root
  mkdir -p "$fake_root/scripts/work-queue"
  if [[ "$should_fail" == "1" ]]; then
    cat > "$fake_root/scripts/work-queue/checkpoint.sh" <<'EOF'
#!/usr/bin/env bash
echo "checkpoint.sh: simulated failure" >&2
exit 1
EOF
  else
    cat > "$fake_root/scripts/work-queue/checkpoint.sh" <<EOF
#!/usr/bin/env bash
touch "$TMPDIR_TEST/checkpoint_called"
exit 0
EOF
  fi
  chmod +x "$fake_root/scripts/work-queue/checkpoint.sh"
}

# -------------------------------------------------------------------
# Test 1: usage_pct=70 → WARN at threshold=70; no checkpoint; no yaml
# -------------------------------------------------------------------
T1_ROOT="$TMPDIR_TEST/t1"
setup_wrk "$T1_ROOT" "WRK-9001"
setup_mock_checkpoint "$T1_ROOT" "0"

REPO_ROOT="$T1_ROOT" bash "$SCRIPT" --usage-pct 70

LOG="$T1_ROOT/logs/context-monitor.log"
YAML="$T1_ROOT/.claude/work-queue/assets/WRK-9001/context-warning.yaml"

if grep -q "LEVEL=WARN.*threshold=70" "$LOG" 2>/dev/null; then
  if [[ ! -f "$YAML" ]]; then
    pass "Test 1: usage_pct=70 writes WARN threshold=70, no yaml"
  else
    fail "Test 1: context-warning.yaml should not exist at pct=70"
  fi
else
  fail "Test 1: WARN threshold=70 not found in log"
fi

# -------------------------------------------------------------------
# Test 2: usage_pct=80 → WARN at threshold=80; yaml written; checkpoint called
# -------------------------------------------------------------------
T2_ROOT="$TMPDIR_TEST/t2"
setup_wrk "$T2_ROOT" "WRK-9002"
setup_mock_checkpoint "$T2_ROOT" "0"

REPO_ROOT="$T2_ROOT" bash "$SCRIPT" --usage-pct 80

LOG="$T2_ROOT/logs/context-monitor.log"
YAML="$T2_ROOT/.claude/work-queue/assets/WRK-9002/context-warning.yaml"

WARN80=0
YAML_OK=0
CHECKPOINT_CALLED=0
grep -q "LEVEL=WARN.*threshold=80" "$LOG" 2>/dev/null && WARN80=1
[[ -f "$YAML" ]] && grep -q "threshold: 80" "$YAML" && YAML_OK=1
[[ -f "$TMPDIR_TEST/checkpoint_called" ]] && CHECKPOINT_CALLED=1

if [[ $WARN80 -eq 1 && $YAML_OK -eq 1 && $CHECKPOINT_CALLED -eq 1 ]]; then
  pass "Test 2: usage_pct=80 writes WARN threshold=80, context-warning.yaml, and called checkpoint"
else
  fail "Test 2: expected WARN threshold=80 ($WARN80), yaml ($YAML_OK), checkpoint_called ($CHECKPOINT_CALLED)"
fi

# -------------------------------------------------------------------
# Test 3: no active-wrk → exits 0; logs SKIP
# -------------------------------------------------------------------
T3_ROOT="$TMPDIR_TEST/t3"
mkdir -p "$T3_ROOT/.claude/state" "$T3_ROOT/logs"
setup_mock_checkpoint "$T3_ROOT" "0"
# No active-wrk file written

REPO_ROOT="$T3_ROOT" bash "$SCRIPT" --usage-pct 80
LOG="$T3_ROOT/logs/context-monitor.log"

if grep -q "LEVEL=SKIP.*no_active_wrk" "$LOG" 2>/dev/null; then
  pass "Test 3: no active-wrk logs SKIP and exits 0"
else
  fail "Test 3: expected SKIP log for no active-wrk"
fi

# -------------------------------------------------------------------
# Test 4: duplicate call at 80 with existing context-warning.yaml → idempotent (SKIP)
# -------------------------------------------------------------------
T4_ROOT="$TMPDIR_TEST/t4"
setup_wrk "$T4_ROOT" "WRK-9004"
setup_mock_checkpoint "$T4_ROOT" "0"

# First call
REPO_ROOT="$T4_ROOT" bash "$SCRIPT" --usage-pct 80

LOG="$T4_ROOT/logs/context-monitor.log"
YAML="$T4_ROOT/.claude/work-queue/assets/WRK-9004/context-warning.yaml"
MTIME1="$(stat -c %Y "$YAML" 2>/dev/null || echo 0)"

sleep 1

# Second call — should be idempotent
REPO_ROOT="$T4_ROOT" bash "$SCRIPT" --usage-pct 80
MTIME2="$(stat -c %Y "$YAML" 2>/dev/null || echo 0)"

SKIP_LOGGED=0
MTIME_UNCHANGED=0
grep -q "LEVEL=SKIP.*context-warning.yaml_already_exists" "$LOG" 2>/dev/null && SKIP_LOGGED=1
[[ "$MTIME1" == "$MTIME2" ]] && MTIME_UNCHANGED=1

if [[ $SKIP_LOGGED -eq 1 && $MTIME_UNCHANGED -eq 1 ]]; then
  pass "Test 4: duplicate 80% call logs SKIP and yaml not rewritten (mtime unchanged)"
else
  fail "Test 4: expected SKIP log ($SKIP_LOGGED) and unchanged mtime ($MTIME1==$MTIME2, unchanged=$MTIME_UNCHANGED)"
fi

# -------------------------------------------------------------------
# Test 5: checkpoint.sh fails → logs ERROR but exits 0
# -------------------------------------------------------------------
T5_ROOT="$TMPDIR_TEST/t5"
setup_wrk "$T5_ROOT" "WRK-9005"
setup_mock_checkpoint "$T5_ROOT" "1"

EXIT_CODE=0
REPO_ROOT="$T5_ROOT" bash "$SCRIPT" --usage-pct 80 || EXIT_CODE=$?

LOG="$T5_ROOT/logs/context-monitor.log"

if [[ $EXIT_CODE -eq 0 ]] && grep -q "LEVEL=ERROR.*checkpoint.sh_failed" "$LOG" 2>/dev/null; then
  pass "Test 5: checkpoint.sh failure logs ERROR but exits 0"
else
  fail "Test 5: expected exit 0 ($EXIT_CODE) and ERROR log ($(grep 'LEVEL=ERROR' "$LOG" 2>/dev/null || echo none))"
fi

# -------------------------------------------------------------------
# Test 6: invalid usage-pct → exits 1
# -------------------------------------------------------------------
T6_ROOT="$TMPDIR_TEST/t6"
mkdir -p "$T6_ROOT/.claude/state" "$T6_ROOT/logs"

EXIT_CODE=0
REPO_ROOT="$T6_ROOT" bash "$SCRIPT" --usage-pct abc 2>/dev/null || EXIT_CODE=$?

if [[ $EXIT_CODE -eq 1 ]]; then
  pass "Test 6: invalid usage-pct 'abc' exits 1"
else
  fail "Test 6: expected exit 1, got $EXIT_CODE"
fi

# -------------------------------------------------------------------
# Summary
# -------------------------------------------------------------------
TOTAL=$(( PASS + FAIL ))
echo ""
echo "Results: $PASS/$TOTAL passed"
if [[ $FAIL -gt 0 ]]; then
  exit 1
fi
exit 0
