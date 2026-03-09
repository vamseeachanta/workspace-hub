#!/usr/bin/env bash
# tests/quality/test_check_all.sh — unit tests for scripts/quality/check-all.sh (WRK-1056)
# Uses fixture repos + mock uv bin — fully deterministic, no live repo dependency.
# Usage: bash tests/quality/test_check_all.sh

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
  else fail "$desc" "'${needle}' not found in: ${haystack:0:200}"; fi
}

assert_not_contains() {
  local desc="$1" needle="$2" haystack="$3"
  if [[ "$haystack" != *"$needle"* ]]; then pass "$desc"
  else fail "$desc" "'${needle}' unexpectedly found in output"; fi
}

# ---------------------------------------------------------------------------
# Setup: fixture REPO_ROOT with 5 minimal repos + mock uv bin
# ---------------------------------------------------------------------------
FIXTURE_ROOT="$(mktemp -d)"
MOCK_DIR="$(mktemp -d)"
trap 'rm -rf "$FIXTURE_ROOT" "$MOCK_DIR"' EXIT

# Create minimal repo structure for all 5 repos
for repo in assetutilities digitalmodel worldenergydata assethold OGManufacturing; do
  mkdir -p "${FIXTURE_ROOT}/${repo}/src"
  printf '[project]\nname = "%s"\n' "$repo" > "${FIXTURE_ROOT}/${repo}/pyproject.toml"
done

# Add [tool.mypy] to repos that have it (matches resource intelligence findings)
for repo in assetutilities digitalmodel assethold; do
  printf '\n[tool.mypy]\npython_version = "3.9"\n' >> "${FIXTURE_ROOT}/${repo}/pyproject.toml"
done

# Mock uv: controlled by MOCK_RUFF_EXIT / MOCK_MYPY_EXIT env vars
cat > "${MOCK_DIR}/uv" << 'MOCK_UV'
#!/usr/bin/env bash
case "$*" in
  "tool run ruff --version"*) echo "ruff 0.3.0 (mock)"; exit 0 ;;
  "run mypy --version"*)      echo "mypy 1.9.0 (mock)"; exit 0 ;;
  "tool run ruff check"*)
    if [[ "${MOCK_RUFF_EXIT:-0}" -ne 0 ]]; then
      echo "src/foo.py:1:1: E501 Line too long (101 > 100)"
      echo "Found 1 error."
      exit 1
    fi
    echo "All checks passed."
    exit 0
    ;;
  "run mypy"*)
    if [[ "${MOCK_MYPY_EXIT:-0}" -ne 0 ]]; then
      echo "src/foo.py:1: error: Cannot find implementation or library stub"
      exit 1
    fi
    echo "Success: no issues found in 1 source file"
    exit 0
    ;;
  *) exit 0 ;;
esac
MOCK_UV
chmod +x "${MOCK_DIR}/uv"
export PATH="${MOCK_DIR}:${PATH}"

run_check() {
  QUALITY_REPO_ROOT="$FIXTURE_ROOT" bash "$CHECK_SCRIPT" "$@"
}

# ---------------------------------------------------------------------------
# T1: --help exits 0 and shows usage
# ---------------------------------------------------------------------------
echo "── T1: --help exits 0 ────────────────────────────────────"
help_exit=0; help_out="$(run_check --help 2>&1)" || help_exit=$?
assert_exit "T1 --help exits 0" 0 "$help_exit"
assert_contains "T1 --help shows Usage:" "Usage:" "$help_out"
assert_contains "T1 --help shows --fix" "--fix" "$help_out"
assert_contains "T1 --help shows --repo" "--repo" "$help_out"

# ---------------------------------------------------------------------------
# T2: --repo nonexistent exits 1 with error message
# ---------------------------------------------------------------------------
echo "── T2: --repo nonexistent exits 1 ───────────────────────"
bad_exit=0; bad_out="$(run_check --repo this-does-not-exist 2>&1)" || bad_exit=$?
assert_exit "T2 --repo nonexistent exits 1" 1 "$bad_exit"
assert_contains "T2 error mentions 'Unknown repo'" "Unknown repo" "$bad_out"

# ---------------------------------------------------------------------------
# T3: --ruff-only produces no mypy: lines
# ---------------------------------------------------------------------------
echo "── T3: --ruff-only skips mypy ────────────────────────────"
ruff_only_exit=0
ruff_only_out="$(MOCK_RUFF_EXIT=0 run_check --ruff-only --repo assetutilities 2>&1)" \
  || ruff_only_exit=$?
assert_exit "T3 --ruff-only exits 0 (clean fixture)" 0 "$ruff_only_exit"
assert_not_contains "T3 no mypy: lines in output" "mypy:" "$ruff_only_out"
assert_contains "T3 ruff: line present" "ruff:" "$ruff_only_out"

# ---------------------------------------------------------------------------
# T4: --mypy-only produces no ruff: lines
# ---------------------------------------------------------------------------
echo "── T4: --mypy-only skips ruff ────────────────────────────"
mypy_only_out="$(MOCK_MYPY_EXIT=0 run_check --mypy-only --repo assetutilities 2>&1)" || true
assert_not_contains "T4 no ruff: lines in output" "ruff:" "$mypy_only_out"
assert_contains "T4 mypy: line present" "mypy:" "$mypy_only_out"

# ---------------------------------------------------------------------------
# T5: ruff failure → aggregate exit 1, FAIL in output
# ---------------------------------------------------------------------------
echo "── T5: ruff FAIL → aggregate exit 1 ─────────────────────"
fail_exit=0
fail_out="$(MOCK_RUFF_EXIT=1 run_check --ruff-only --repo assetutilities 2>&1)" \
  || fail_exit=$?
assert_exit "T5 exit 1 on ruff failure" 1 "$fail_exit"
assert_contains "T5 FAIL in ruff result" "FAIL" "$fail_out"
assert_contains "T5 Summary line present" "Summary:" "$fail_out"
assert_contains "T5 0/1 PASS in summary" "0/1 PASS" "$fail_out"

# ---------------------------------------------------------------------------
# T6: --repo filter runs only one repo (not all 5)
# ---------------------------------------------------------------------------
echo "── T6: --repo filter runs one repo only ──────────────────"
filter_out="$(MOCK_RUFF_EXIT=0 run_check --ruff-only --repo digitalmodel 2>&1)"
assert_contains "T6 digitalmodel appears in output" "[digitalmodel]" "$filter_out"
assert_not_contains "T6 assetutilities absent" "[assetutilities]" "$filter_out"
assert_not_contains "T6 ogmanufacturing absent" "[ogmanufacturing]" "$filter_out"

# ---------------------------------------------------------------------------
# T7: unknown flag exits 1
# ---------------------------------------------------------------------------
echo "── T7: unknown flag exits 1 ──────────────────────────────"
unk_exit=0; unk_out="$(run_check --bad-flag 2>&1)" || unk_exit=$?
assert_exit "T7 unknown flag exits 1" 1 "$unk_exit"
assert_contains "T7 shows ERROR" "ERROR" "$unk_out"

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo ""
echo "────────────────────────────────────────────────────────"
echo "Results: ${PASS} passed, ${FAIL} failed"
[[ $FAIL -eq 0 ]] && exit 0 || exit 1
