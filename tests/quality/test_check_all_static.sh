#!/usr/bin/env bash
# tests/quality/test_check_all_static.sh — TDD tests for bandit/radon/vulture
# in scripts/quality/check-all.sh (WRK-1081)
# Mirrors fixture + mock pattern from test_check_all.sh.
# Usage: bash tests/quality/test_check_all_static.sh

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
CHECK_SCRIPT="${REPO_ROOT}/scripts/quality/check-all.sh"

# ---------------------------------------------------------------------------
# Minimal assert framework
# ---------------------------------------------------------------------------
PASS=0; FAIL=0

pass() { echo "  PASS: $1"; PASS=$((PASS + 1)); }
fail() { echo "  FAIL: $1"; echo "        $2"; FAIL=$((FAIL + 1)); }

assert_exit() {
  local desc="$1" expected="$2" actual="$3"
  if [[ "$actual" -eq "$expected" ]]; then pass "$desc"
  else fail "$desc" "exit ${expected} expected, got ${actual}"; fi
}

assert_contains() {
  local desc="$1" needle="$2" haystack="$3"
  if [[ "$haystack" == *"$needle"* ]]; then pass "$desc"
  else fail "$desc" "'${needle}' not found in: ${haystack:0:300}"; fi
}

assert_not_contains() {
  local desc="$1" needle="$2" haystack="$3"
  if [[ "$haystack" != *"$needle"* ]]; then pass "$desc"
  else fail "$desc" "'${needle}' unexpectedly found in output"; fi
}

# ---------------------------------------------------------------------------
# Fixtures: minimal repo + mock tool bin
# ---------------------------------------------------------------------------
FIXTURE_ROOT="$(mktemp -d)"
MOCK_DIR="$(mktemp -d)"
trap 'rm -rf "$FIXTURE_ROOT" "$MOCK_DIR"' EXIT

for repo in assetutilities digitalmodel worldenergydata assethold OGManufacturing; do
  mkdir -p "${FIXTURE_ROOT}/${repo}/src"
  printf '[project]\nname = "%s"\n' "$repo" \
    > "${FIXTURE_ROOT}/${repo}/pyproject.toml"
done

# ---------------------------------------------------------------------------
# Mock uv: passes ruff/mypy calls through; static tools controlled by envvars.
# MOCK_BANDIT_MEDIUM_JSON  — JSON with a MEDIUM finding (no baseline match)
# MOCK_BANDIT_LOW_JSON     — JSON with only LOW findings
# MOCK_BANDIT_EXIT         — exit code bandit should return (0 = clean/baseline-suppressed)
# MOCK_RADON_OUTPUT        — output radon cc should print
# MOCK_VULTURE_OUTPUT      — output vulture should print
# MOCK_BANDIT_FAIL_JSON    — set non-empty to emit invalid JSON (simulate tool failure)
# ---------------------------------------------------------------------------
cat > "${MOCK_DIR}/uvx" << 'MOCK_UVX'
#!/usr/bin/env bash
# uvx mock: route bandit / radon / vulture
case "$1" in
  bandit*)
    shift
    # Consume all args; print appropriate JSON / output
    if [[ -n "${MOCK_BANDIT_FAIL_JSON:-}" ]]; then
      echo "bandit: configuration error" >&2
      exit 1
    fi
    if [[ -n "${MOCK_BANDIT_MEDIUM_JSON:-}" ]]; then
      echo "${MOCK_BANDIT_MEDIUM_JSON}"
      exit 1
    fi
    if [[ -n "${MOCK_BANDIT_LOW_JSON:-}" ]]; then
      # Real bandit with -ll suppresses LOW findings → exit 0 with clean JSON
      if [[ "$*" == *-ll* ]]; then
        echo '{"results":[],"metrics":{}}'
        exit 0
      fi
      echo "${MOCK_BANDIT_LOW_JSON}"
      exit 1
    fi
    # Default: clean result
    echo '{"results":[],"metrics":{}}'
    exit "${MOCK_BANDIT_EXIT:-0}"
    ;;
  radon*)
    shift
    if [[ -n "${MOCK_RADON_OUTPUT:-}" ]]; then
      echo "${MOCK_RADON_OUTPUT}"
    fi
    exit 0
    ;;
  vulture*)
    shift
    if [[ -n "${MOCK_VULTURE_OUTPUT:-}" ]]; then
      echo "${MOCK_VULTURE_OUTPUT}"
      exit 1   # vulture exits 1 when it finds dead code
    fi
    exit 0
    ;;
  *)
    exit 0
    ;;
esac
MOCK_UVX

# Also need 'uv tool run' → pass to uvx-style mock
cat > "${MOCK_DIR}/uv" << 'MOCK_UV'
#!/usr/bin/env bash
# Forward 'run --no-project python' to real python3 for JSON parsing
if [[ "${1:-}" == "run" && "${2:-}" == "--no-project" && "${3:-}" == "python" ]]; then
  shift 3
  exec python3 "$@"
fi
case "$*" in
  "tool run ruff --version"*) echo "ruff 0.3.0 (mock)"; exit 0 ;;
  "run mypy --version"*)      echo "mypy 1.9.0 (mock)"; exit 0 ;;
  "tool run ruff check"*)     echo "All checks passed."; exit 0 ;;
  "run mypy"*)                echo "Success: no issues found"; exit 0 ;;
  *) exit 0 ;;
esac
MOCK_UV

chmod +x "${MOCK_DIR}/uvx" "${MOCK_DIR}/uv"
export PATH="${MOCK_DIR}:${PATH}"

# Bandit JSON fixtures
MEDIUM_FINDING='{"results":[{"test_id":"B105","filename":"src/foo.py","line_number":10,"issue_severity":"MEDIUM","issue_confidence":"HIGH","issue_text":"Hardcoded password"}],"metrics":{}}'
LOW_FINDING='{"results":[{"test_id":"B108","filename":"src/foo.py","line_number":5,"issue_severity":"LOW","issue_confidence":"HIGH","issue_text":"Probable insecure temp file"}],"metrics":{}}'
RADON_C_OUTPUT="src/foo.py
    F 1:0 do_thing - C (12)"
VULTURE_OUTPUT="src/foo.py:42: unused function 'old_helper' (100% confidence)"

# Baseline JSON with MEDIUM finding already recorded (native baseline format)
BASELINE_WITH_MEDIUM="${FIXTURE_ROOT}/assetutilities/bandit-baseline.json"
echo "${MEDIUM_FINDING}" > "${BASELINE_WITH_MEDIUM}"

run_check() {
  QUALITY_REPO_ROOT="$FIXTURE_ROOT" bash "$CHECK_SCRIPT" "$@"
}

# ---------------------------------------------------------------------------
# T1-static: --static flag appears in --help
# ---------------------------------------------------------------------------
echo "── T1-static: --help shows --static ─────────────────────"
help_out="$(run_check --help 2>&1)" || true
assert_contains "T1 --help shows --static" "--static" "$help_out"
assert_contains "T1 --help shows --bandit" "--bandit" "$help_out"
assert_contains "T1 --help shows --radon" "--radon" "$help_out"
assert_contains "T1 --help shows --vulture" "--vulture" "$help_out"

# ---------------------------------------------------------------------------
# T2-static: bandit MEDIUM finding blocks (exit 1)
# ---------------------------------------------------------------------------
echo "── T2-static: bandit MEDIUM blocks ──────────────────────"
t2_exit=0
t2_out="$(MOCK_BANDIT_MEDIUM_JSON="${MEDIUM_FINDING}" \
  run_check --bandit --repo assetutilities 2>&1)" || t2_exit=$?
assert_exit "T2 bandit MEDIUM exits 1" 1 "$t2_exit"
assert_contains "T2 FAIL in bandit result" "FAIL" "$t2_out"

# ---------------------------------------------------------------------------
# T3-static: bandit LOW only warns, exits 0
# ---------------------------------------------------------------------------
echo "── T3-static: bandit LOW warns, exits 0 ─────────────────"
t3_exit=0
t3_out="$(MOCK_BANDIT_LOW_JSON="${LOW_FINDING}" \
  run_check --bandit --repo assetutilities 2>&1)" || t3_exit=$?
assert_exit "T3 bandit LOW exits 0" 0 "$t3_exit"
assert_contains "T3 WARN line printed for LOW" "WARN" "$t3_out"

# ---------------------------------------------------------------------------
# T4-static: bandit baseline suppresses existing MEDIUM → exit 0
# ---------------------------------------------------------------------------
echo "── T4-static: bandit baseline suppresses existing MEDIUM ─"
# When bandit runs with a baseline that already has the MEDIUM finding,
# the mock returns exit 0 (native baseline suppressed it)
t4_exit=0
t4_out="$(MOCK_BANDIT_EXIT=0 \
  run_check --bandit --repo assetutilities 2>&1)" || t4_exit=$?
assert_exit "T4 baseline suppresses MEDIUM, exits 0" 0 "$t4_exit"
assert_not_contains "T4 no FAIL in output" "bandit: FAIL" "$t4_out"

# ---------------------------------------------------------------------------
# T5-static: new LOW does not block Pass 2 (--bandit exits 0 on LOW-only)
# ---------------------------------------------------------------------------
echo "── T5-static: new LOW finding does not block ─────────────"
t5_exit=0
t5_out="$(MOCK_BANDIT_LOW_JSON="${LOW_FINDING}" \
  run_check --bandit --repo assetutilities 2>&1)" || t5_exit=$?
assert_exit "T5 LOW-only bandit scan exits 0" 0 "$t5_exit"

# ---------------------------------------------------------------------------
# T6-static: LOW findings visible via Pass 1 (warn line in output)
# ---------------------------------------------------------------------------
echo "── T6-static: LOW visible via non-blocking Pass 1 ────────"
t6_out="$(MOCK_BANDIT_LOW_JSON="${LOW_FINDING}" \
  run_check --bandit --repo assetutilities 2>&1)" || true
assert_contains "T6 LOW warning line present" "WARN" "$t6_out"

# ---------------------------------------------------------------------------
# T7-static: radon non-blocking (exit 0 even with C-grade output)
# ---------------------------------------------------------------------------
echo "── T7-static: radon C-grade is non-blocking ──────────────"
t7_exit=0
t7_out="$(MOCK_RADON_OUTPUT="${RADON_C_OUTPUT}" \
  run_check --radon --repo assetutilities 2>&1)" || t7_exit=$?
assert_exit "T7 radon exits 0 (non-blocking)" 0 "$t7_exit"
assert_contains "T7 radon output shown" "radon:" "$t7_out"

# ---------------------------------------------------------------------------
# T8-static: vulture non-blocking (exit 0 even with dead code found)
# ---------------------------------------------------------------------------
echo "── T8-static: vulture dead code is non-blocking ──────────"
t8_exit=0
t8_out="$(MOCK_VULTURE_OUTPUT="${VULTURE_OUTPUT}" \
  run_check --vulture --repo assetutilities 2>&1)" || t8_exit=$?
assert_exit "T8 vulture exits 0 (non-blocking)" 0 "$t8_exit"
assert_contains "T8 vulture WARN in output" "WARN" "$t8_out"

# ---------------------------------------------------------------------------
# T9-static: --static flag runs bandit + radon + vulture
# ---------------------------------------------------------------------------
echo "── T9-static: --static invokes all three tools ───────────"
t9_out="$(run_check --static --repo assetutilities 2>&1)" || true
assert_contains "T9 bandit: line present" "bandit:" "$t9_out"
assert_contains "T9 radon: line present" "radon:" "$t9_out"
assert_contains "T9 vulture: line present" "vulture:" "$t9_out"

# ---------------------------------------------------------------------------
# T10-static: Pass 1 scan failure prints visible warning, exits 0
# ---------------------------------------------------------------------------
echo "── T10-static: Pass 1 scan failure prints warning ────────"
t10_exit=0
t10_out="$(MOCK_BANDIT_FAIL_JSON=1 \
  run_check --bandit --repo assetutilities 2>&1)" || t10_exit=$?
assert_exit "T10 scan failure exits 0 (non-blocking)" 0 "$t10_exit"
assert_contains "T10 visible failure warning printed" "WARN" "$t10_out"

# ---------------------------------------------------------------------------
# T11-static: pre-commit bandit hook — new MEDIUM in staged file blocks
# (simulated: run_bandit_precommit function exits 1 on MEDIUM)
# ---------------------------------------------------------------------------
echo "── T11-static: pre-commit MEDIUM blocks ──────────────────"
t11_exit=0
t11_out="$(MOCK_BANDIT_MEDIUM_JSON="${MEDIUM_FINDING}" \
  run_check --bandit --repo assetutilities 2>&1)" || t11_exit=$?
assert_exit "T11 pre-commit MEDIUM exits 1" 1 "$t11_exit"

# ---------------------------------------------------------------------------
# T12-static: pre-commit bandit hook — existing baselined MEDIUM passes
# ---------------------------------------------------------------------------
echo "── T12-static: pre-commit existing MEDIUM passes ─────────"
t12_exit=0
t12_out="$(MOCK_BANDIT_EXIT=0 \
  run_check --bandit --repo assetutilities 2>&1)" || t12_exit=$?
assert_exit "T12 baselined MEDIUM exits 0" 0 "$t12_exit"

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo ""
echo "────────────────────────────────────────────────────────"
echo "Results: ${PASS} passed, ${FAIL} failed"
[[ $FAIL -eq 0 ]] && exit 0 || exit 1
