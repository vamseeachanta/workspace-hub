#!/usr/bin/env bash
# tests/docs/test_build_api_docs.sh — TDD tests for scripts/docs/build-api-docs.sh (WRK-1075)
# Follows fixture + mock pattern from tests/quality/test_check_all.sh.
# Usage: bash tests/docs/test_build_api_docs.sh

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
BUILD_SCRIPT="${REPO_ROOT}/scripts/docs/build-api-docs.sh"

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

assert_file_exists() {
  local desc="$1" path="$2"
  if [[ -f "$path" ]]; then pass "$desc"
  else fail "$desc" "file not found: $path"; fi
}

# ---------------------------------------------------------------------------
# Fixtures: minimal repos + mock mkdocs/uv bins
# ---------------------------------------------------------------------------
FIXTURE_ROOT="$(mktemp -d)"
MOCK_DIR="$(mktemp -d)"
trap 'rm -rf "$FIXTURE_ROOT" "$MOCK_DIR"' EXIT

for repo in assetutilities digitalmodel worldenergydata assethold OGManufacturing; do
  mkdir -p "${FIXTURE_ROOT}/${repo}/src"
  mkdir -p "${FIXTURE_ROOT}/${repo}/docs/api"
  printf '[project]\nname = "%s"\n' "$repo" \
    > "${FIXTURE_ROOT}/${repo}/pyproject.toml"
  printf 'site_name: %s\n' "$repo" \
    > "${FIXTURE_ROOT}/${repo}/mkdocs.yml"
  printf '::: %s\n' "$repo" \
    > "${FIXTURE_ROOT}/${repo}/docs/api/index.md"
done

# Mock uv: delegates to mock mkdocs
cat > "${MOCK_DIR}/uv" << 'MOCK_UV'
#!/usr/bin/env bash
# Intercept: uv run [--group docs] mkdocs <cmd> [args...]
# Shift past all args until "mkdocs", then exec mock mkdocs with remaining args
if [[ "$*" == *"mkdocs"* ]]; then
  while [[ $# -gt 0 && "$1" != "mkdocs" ]]; do shift; done
  shift  # drop "mkdocs" itself
  exec "${MOCK_MKDOCS:-mkdocs}" "$@"
fi
exit 0
MOCK_UV
chmod +x "${MOCK_DIR}/uv"

# Mock mkdocs: controlled by MOCK_MKDOCS_EXIT + MOCK_MKDOCS_OUTPUT
cat > "${MOCK_DIR}/mkdocs" << 'MOCK_MKDOCS'
#!/usr/bin/env bash
exit_code="${MOCK_MKDOCS_EXIT:-0}"
if [[ -n "${MOCK_MKDOCS_OUTPUT:-}" ]]; then
  echo "$MOCK_MKDOCS_OUTPUT"
fi
if [[ "$1" == "build" ]]; then
  mkdir -p site
  echo "<html><body>docs</body></html>" > site/index.html
fi
exit "$exit_code"
MOCK_MKDOCS
chmod +x "${MOCK_DIR}/mkdocs"

export PATH="${MOCK_DIR}:${PATH}"
export MOCK_MKDOCS="${MOCK_DIR}/mkdocs"

run_build() {
  DOCS_REPO_ROOT="$FIXTURE_ROOT" bash "$BUILD_SCRIPT" "$@"
}

# ---------------------------------------------------------------------------
# T1: --help exits 0 and shows usage
# ---------------------------------------------------------------------------
echo "── T1: --help exits 0 ────────────────────────────────────"
t1_exit=0; t1_out="$(run_build --help 2>&1)" || t1_exit=$?
assert_exit "T1 --help exits 0" 0 "$t1_exit"
assert_contains "T1 --help shows Usage:" "Usage:" "$t1_out"
assert_contains "T1 --help shows --repo" "--repo" "$t1_out"
assert_contains "T1 --help shows --serve" "--serve" "$t1_out"
assert_contains "T1 --help shows --strict" "--strict" "$t1_out"

# ---------------------------------------------------------------------------
# T2: unknown flag exits 1
# ---------------------------------------------------------------------------
echo "── T2: unknown flag exits 1 ──────────────────────────────"
t2_exit=0; t2_out="$(run_build --bad-flag 2>&1)" || t2_exit=$?
assert_exit "T2 unknown flag exits 1" 1 "$t2_exit"
assert_contains "T2 shows ERROR" "ERROR" "$t2_out"

# ---------------------------------------------------------------------------
# T3: --repo nonexistent exits 1 with error message
# ---------------------------------------------------------------------------
echo "── T3: --repo nonexistent exits 1 ───────────────────────"
t3_exit=0; t3_out="$(run_build --repo no-such-repo 2>&1)" || t3_exit=$?
assert_exit "T3 --repo nonexistent exits 1" 1 "$t3_exit"
assert_contains "T3 error mentions 'Unknown repo'" "Unknown repo" "$t3_out"

# ---------------------------------------------------------------------------
# T4: clean build exits 0 and produces site/index.html
# ---------------------------------------------------------------------------
echo "── T4: clean build exits 0, creates site/ ────────────────"
t4_exit=0
t4_out="$(MOCK_MKDOCS_EXIT=0 run_build --repo assetutilities 2>&1)" || t4_exit=$?
assert_exit "T4 exits 0 on clean build" 0 "$t4_exit"
assert_contains "T4 PASS in output" "PASS" "$t4_out"
assert_file_exists "T4 site/index.html created" \
  "${FIXTURE_ROOT}/assetutilities/site/index.html"

# ---------------------------------------------------------------------------
# T5: mkdocs failure exits 1 with FAIL in output
# ---------------------------------------------------------------------------
echo "── T5: mkdocs failure → exit 1, FAIL ────────────────────"
t5_exit=0
t5_out="$(MOCK_MKDOCS_EXIT=1 run_build --repo assetutilities 2>&1)" || t5_exit=$?
assert_exit "T5 exits 1 on mkdocs failure" 1 "$t5_exit"
assert_contains "T5 FAIL in output" "FAIL" "$t5_out"

# ---------------------------------------------------------------------------
# T6: --repo filter runs only one repo (not all 5)
# ---------------------------------------------------------------------------
echo "── T6: --repo filter runs one repo only ──────────────────"
t6_out="$(MOCK_MKDOCS_EXIT=0 run_build --repo assetutilities 2>&1)"
assert_contains "T6 assetutilities present" "[assetutilities]" "$t6_out"
assert_not_contains "T6 digitalmodel absent" "[digitalmodel]" "$t6_out"

# ---------------------------------------------------------------------------
# T7: all 5 repos built without --repo flag
# ---------------------------------------------------------------------------
echo "── T7: all 5 repos built when no --repo given ────────────"
t7_out="$(MOCK_MKDOCS_EXIT=0 run_build 2>&1)" || true
assert_contains "T7 assetutilities present" "[assetutilities]" "$t7_out"
assert_contains "T7 ogmanufacturing present" "[ogmanufacturing]" "$t7_out"

# ---------------------------------------------------------------------------
# T8: repo without mkdocs.yml reports SKIP
# ---------------------------------------------------------------------------
echo "── T8: repo without mkdocs.yml → SKIP ───────────────────"
rm "${FIXTURE_ROOT}/assetutilities/mkdocs.yml"
t8_out="$(MOCK_MKDOCS_EXIT=0 run_build --repo assetutilities 2>&1)" || true
assert_contains "T8 SKIP when no mkdocs.yml" "SKIP" "$t8_out"
# Restore
printf 'site_name: assetutilities\n' > "${FIXTURE_ROOT}/assetutilities/mkdocs.yml"

# ---------------------------------------------------------------------------
# T9: --strict passes --strict flag to mkdocs
# ---------------------------------------------------------------------------
echo "── T9: --strict flag forwarded to mkdocs ─────────────────"
T9_FLAG_FILE="$(mktemp)"
rm -f "$T9_FLAG_FILE"
# Mock writes a side-channel flag file when --strict is seen
cat > "${MOCK_DIR}/mkdocs" << STRICT_MOCK
#!/usr/bin/env bash
if [[ "\$*" == *"--strict"* ]]; then
  touch "${T9_FLAG_FILE}"
fi
mkdir -p site && echo "<html/>" > site/index.html
exit "\${MOCK_MKDOCS_EXIT:-0}"
STRICT_MOCK
chmod +x "${MOCK_DIR}/mkdocs"
MOCK_MKDOCS_EXIT=0 run_build --repo assetutilities --strict > /dev/null 2>&1 || true
if [[ -f "$T9_FLAG_FILE" ]]; then pass "T9 --strict forwarded to mkdocs"
else fail "T9 --strict forwarded to mkdocs" "flag file not created — --strict not passed"; fi
rm -f "$T9_FLAG_FILE"

# ---------------------------------------------------------------------------
# T10: Summary line present with counts
# ---------------------------------------------------------------------------
echo "── T10: Summary line present ─────────────────────────────"
cat > "${MOCK_DIR}/mkdocs" << 'MOCK_MKDOCS2'
#!/usr/bin/env bash
mkdir -p site && echo "<html/>" > site/index.html
exit "${MOCK_MKDOCS_EXIT:-0}"
MOCK_MKDOCS2
chmod +x "${MOCK_DIR}/mkdocs"
t10_out="$(MOCK_MKDOCS_EXIT=0 run_build 2>&1)" || true
assert_contains "T10 Summary: line present" "Summary:" "$t10_out"

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo ""
echo "────────────────────────────────────────────────────────"
echo "Results: ${PASS} passed, ${FAIL} failed"
[[ $FAIL -eq 0 ]] && exit 0 || exit 1
