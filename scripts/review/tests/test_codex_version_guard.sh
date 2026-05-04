#!/usr/bin/env bash
# test_codex_version_guard.sh — regression tests for #2479 Codex version guard.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
LIB="${REPO_ROOT}/scripts/review/lib/codex-version-guard.sh"
PIN_SCRIPT="${REPO_ROOT}/scripts/install/pin-codex.sh"
PIN_ENV="${REPO_ROOT}/scripts/install/codex-pin.env"
VERIFY_SETUP="${REPO_ROOT}/scripts/setup/verify-setup.sh"

TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

run_test() { TESTS_RUN=$((TESTS_RUN + 1)); echo ""; echo "--- Test ${TESTS_RUN}: $1 ---"; }
pass() { TESTS_PASSED=$((TESTS_PASSED + 1)); echo "  PASS: $1"; }
fail() { TESTS_FAILED=$((TESTS_FAILED + 1)); echo "  FAIL: $1"; [[ -n "${2:-}" ]] && echo "        $2"; }

make_bin_dir() {
  local td="$1"
  mkdir -p "$td/bin"
}

write_codex_mock() {
  local bin_dir="$1" version="$2"
  cat > "$bin_dir/codex" <<MOCK
#!/usr/bin/env bash
if [[ "\${1:-}" == "--version" ]]; then
  echo "${version}"
  exit 0
fi
echo "unexpected codex invocation: \$*" >&2
exit 99
MOCK
  chmod +x "$bin_dir/codex"
}

run_guard_with_path() {
  local bin_dir="$1"
  shift
  env -i PATH="$bin_dir:/usr/bin:/bin" HOME="${HOME:-/tmp}" "$@" bash -c '. "$0"; codex_version_guard_check' "$LIB"
}

test_guard_missing_codex() {
  run_test "guard returns rc=2 when codex is absent"
  local td; td="$(mktemp -d)"
  make_bin_dir "$td"
  local out rc=0
  out="$(run_guard_with_path "$td/bin")" || rc=$?
  if [[ "$rc" -eq 2 && "$out" == *"not on PATH"* ]]; then
    pass "missing codex classified as rc=2"
  else
    fail "missing codex result mismatch" "rc=$rc out=$out"
  fi
  rm -rf "$td"
}

test_guard_pre_regression_passes() {
  run_test "guard permits 0.121.0 pre-regression version"
  local td; td="$(mktemp -d)"; make_bin_dir "$td"; write_codex_mock "$td/bin" "codex-cli 0.121.0"
  local out rc=0
  out="$(run_guard_with_path "$td/bin")" || rc=$?
  if [[ "$rc" -eq 0 && "$out" == *"OK"* && "$out" == *"pre-regression"* ]]; then
    pass "0.121.0 allowed"
  else
    fail "0.121.0 should be allowed" "rc=$rc out=$out"
  fi
  rm -rf "$td"
}

test_guard_known_good_0_123_passes() {
  run_test "guard permits pinned 0.123.0"
  local td; td="$(mktemp -d)"; make_bin_dir "$td"; write_codex_mock "$td/bin" "codex-cli 0.123.0"
  local out rc=0
  out="$(run_guard_with_path "$td/bin")" || rc=$?
  if [[ "$rc" -eq 0 && "$out" == *"OK"* ]]; then
    pass "0.123.0 allowed"
  else
    fail "0.123.0 should be allowed" "rc=$rc out=$out"
  fi
  rm -rf "$td"
}

test_guard_floor_0_124_blocks() {
  run_test "guard blocks floor version 0.124.0"
  local td; td="$(mktemp -d)"; make_bin_dir "$td"; write_codex_mock "$td/bin" "codex-cli 0.124.0"
  local out rc=0
  out="$(run_guard_with_path "$td/bin")" || rc=$?
  if [[ "$rc" -eq 3 && "$out" == *"INCOMPATIBLE"* && "$out" == *"#2479"* && "$out" == *"openai/codex#19945"* ]]; then
    pass "0.124.0 blocked with issue/upstream references"
  else
    fail "0.124.0 should be blocked" "rc=$rc out=$out"
  fi
  rm -rf "$td"
}

test_guard_current_0_128_blocks() {
  run_test "guard blocks known-bad current 0.128.0"
  local td; td="$(mktemp -d)"; make_bin_dir "$td"; write_codex_mock "$td/bin" "codex-cli 0.128.0"
  local out rc=0
  out="$(run_guard_with_path "$td/bin")" || rc=$?
  if [[ "$rc" -eq 3 && "$out" == *"INCOMPATIBLE"* && "$out" == *"#2479"* ]]; then
    pass "0.128.0 blocked"
  else
    fail "0.128.0 should be blocked" "rc=$rc out=$out"
  fi
  rm -rf "$td"
}

test_guard_ceiling_whitelist_band() {
  run_test "guard permits versions at or above verified ceiling"
  local td; td="$(mktemp -d)"; make_bin_dir "$td"; write_codex_mock "$td/bin" "codex-cli 0.130.0"
  local out rc=0
  out="$(run_guard_with_path "$td/bin" CODEX_VERSION_GUARD_CEILING=0.130.0)" || rc=$?
  if [[ "$rc" -eq 0 && "$out" == *"past whitelisted regression band"* ]]; then
    pass "0.130.0 allowed with ceiling"
  else
    fail "0.130.0 should be allowed with ceiling" "rc=$rc out=$out"
  fi
  rm -rf "$td"
}

test_guard_unparseable_version() {
  run_test "guard classifies unparseable version as rc=2"
  local td; td="$(mktemp -d)"; make_bin_dir "$td"; write_codex_mock "$td/bin" "codex pre-release banana"
  local out rc=0
  out="$(run_guard_with_path "$td/bin")" || rc=$?
  if [[ "$rc" -eq 2 && "$out" == *"unparseable"* ]]; then
    pass "garbage version rejected as probe failure"
  else
    fail "garbage version should be rc=2" "rc=$rc out=$out"
  fi
  rm -rf "$td"
}

test_guard_alpha_blocks() {
  run_test "guard blocks alpha versions at-or-above floor"
  local td; td="$(mktemp -d)"; make_bin_dir "$td"; write_codex_mock "$td/bin" "codex-cli 0.129.0-alpha.1"
  local out rc=0
  out="$(run_guard_with_path "$td/bin")" || rc=$?
  if [[ "$rc" -eq 3 && "$out" == *"pre-release"* ]]; then
    pass "0.129.0-alpha.1 blocked"
  else
    fail "0.129.0-alpha.1 should be blocked" "rc=$rc out=$out"
  fi
  rm -rf "$td"
}

test_guard_alpha_below_floor_passes() {
  run_test "guard permits alpha below known-bad floor"
  local td; td="$(mktemp -d)"; make_bin_dir "$td"; write_codex_mock "$td/bin" "codex-cli 0.123.0-alpha.1"
  local out rc=0
  out="$(run_guard_with_path "$td/bin")" || rc=$?
  if [[ "$rc" -eq 0 && "$out" == *"OK"* ]]; then
    pass "0.123.0-alpha.1 allowed because base is below floor"
  else
    fail "0.123.0-alpha.1 should be allowed" "rc=$rc out=$out"
  fi
  rm -rf "$td"
}

test_guard_version_command_timeout() {
  run_test "guard returns rc=2 when codex --version times out"
  local td; td="$(mktemp -d)"; make_bin_dir "$td"
  cat > "$td/bin/codex" <<'MOCK'
#!/usr/bin/env bash
if [[ "${1:-}" == "--version" ]]; then sleep 10; fi
MOCK
  chmod +x "$td/bin/codex"
  local out rc=0
  out="$(run_guard_with_path "$td/bin")" || rc=$?
  if [[ "$rc" -eq 2 && "$out" == *"timed out"* ]]; then
    pass "version timeout classified as rc=2"
  else
    fail "version timeout should be rc=2" "rc=$rc out=$out"
  fi
  rm -rf "$td"
}

test_pin_codex_idempotent() {
  run_test "pin script is idempotent when codex is already pinned"
  local td; td="$(mktemp -d)"; make_bin_dir "$td"; write_codex_mock "$td/bin" "codex-cli 0.123.0"
  cat > "$td/bin/npm" <<'MOCK'
#!/usr/bin/env bash
echo "npm should not be invoked for already-pinned codex" >&2
exit 99
MOCK
  chmod +x "$td/bin/npm"
  local out rc=0
  out="$(env -i PATH="$td/bin:/usr/bin:/bin" HOME="${HOME:-/tmp}" bash "$PIN_SCRIPT")" || rc=$?
  if [[ "$rc" -eq 0 && "$out" == *"already at pin"* ]]; then
    pass "pin script no-op at pin"
  else
    fail "pin script should no-op at pin" "rc=$rc out=$out"
  fi
  rm -rf "$td"
}

test_pin_codex_drift_detection() {
  run_test "pin script installs @openai/codex@0.123.0 when drifted"
  local td; td="$(mktemp -d)"; make_bin_dir "$td"
  cat > "$td/bin/codex" <<'MOCK'
#!/usr/bin/env bash
state="${MOCK_CODEX_STATE:?}"
if [[ "${1:-}" == "--version" ]]; then
  if [[ -f "$state" ]]; then echo "codex-cli 0.123.0"; else echo "codex-cli 0.128.0"; fi
  exit 0
fi
MOCK
  cat > "$td/bin/npm" <<'MOCK'
#!/usr/bin/env bash
capture="${MOCK_NPM_CAPTURE:?}"
if [[ "${1:-}" == "bin" && "${2:-}" == "-g" ]]; then echo "$(dirname "$0")"; exit 0; fi
printf '%s\n' "$*" >> "$capture"
touch "${MOCK_CODEX_STATE:?}"
exit 0
MOCK
  chmod +x "$td/bin/codex" "$td/bin/npm"
  local out rc=0
  out="$(env -i PATH="$td/bin:/usr/bin:/bin" HOME="${HOME:-/tmp}" MOCK_NPM_CAPTURE="$td/npm.capture" MOCK_CODEX_STATE="$td/pinned" bash "$PIN_SCRIPT")" || rc=$?
  if [[ "$rc" -eq 0 && "$out" == *"PINNED: codex-cli 0.123.0"* && "$(cat "$td/npm.capture")" == *"install -g @openai/codex@0.123.0"* ]]; then
    pass "pin script installed pinned version"
  else
    fail "pin script should install pinned version" "rc=$rc out=$out npm=$(cat "$td/npm.capture" 2>/dev/null || true)"
  fi
  rm -rf "$td"
}

test_verify_setup_warns_on_unpinned() {
  run_test "verify-setup warns when codex version drifts from pin"
  local td; td="$(mktemp -d)"; make_bin_dir "$td"; write_codex_mock "$td/bin" "codex-cli 0.128.0"
  for cli in git claude gemini crontab tmux; do
    cat > "$td/bin/$cli" <<'MOCK'
#!/usr/bin/env bash
case "$(basename "$0")" in
  git) /usr/bin/git "$@" ;;
  claude) [[ "${1:-}" == "--version" ]] && echo "claude mock" || exit 0 ;;
  *) exit 1 ;;
esac
MOCK
    chmod +x "$td/bin/$cli"
  done
  local out rc=0
  out="$(env -i PATH="$td/bin:/usr/bin:/bin" HOME="${HOME:-/tmp}" bash "$VERIFY_SETUP")" || rc=$?
  if [[ "$out" == *"WARN  codex CLI version drift"* && "$out" == *"0.128.0"* && "$out" == *"0.123.0"* ]]; then
    pass "verify-setup warned on Codex pin drift"
  else
    fail "verify-setup should warn on Codex pin drift" "rc=$rc out=$(printf '%s' "$out" | grep -i codex || true)"
  fi
  rm -rf "$td"
}

if [[ ! -f "$PIN_ENV" ]]; then
  echo "NOTE: expected pin env missing before GREEN: $PIN_ENV"
fi

test_guard_missing_codex
test_guard_pre_regression_passes
test_guard_known_good_0_123_passes
test_guard_floor_0_124_blocks
test_guard_current_0_128_blocks
test_guard_ceiling_whitelist_band
test_guard_unparseable_version
test_guard_alpha_blocks
test_guard_alpha_below_floor_passes
test_guard_version_command_timeout
test_pin_codex_idempotent
test_pin_codex_drift_detection
test_verify_setup_warns_on_unpinned

echo ""
echo "=================================="
echo "Tests run:    $TESTS_RUN"
echo "Tests passed: $TESTS_PASSED"
echo "Tests failed: $TESTS_FAILED"
echo "=================================="

if [[ $TESTS_FAILED -gt 0 ]]; then
  exit 1
fi
