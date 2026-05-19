#!/usr/bin/env bash
# test_detect_os.sh — TDD tests for scripts/setup/lib/detect-os.sh
# Issue: vamseeachanta/workspace-hub#2751 (Phase 1)
#
# Strategy: each test creates a fake `uname` in a temp dir, prepends it to PATH,
# sources the helper, asserts output. No real OS detection — exercises the branching.
#
# Run: bash tests/setup/test_detect_os.sh

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
HELPER="${REPO_ROOT}/scripts/setup/lib/detect-os.sh"

PASS=0
FAIL=0
FAILED_TESTS=()

_assert() {
    local name="$1" expected_stdout="$2" expected_exit="$3" actual_stdout="$4" actual_exit="$5"
    if [[ "$actual_stdout" == "$expected_stdout" && "$actual_exit" == "$expected_exit" ]]; then
        echo "  PASS  $name"
        PASS=$((PASS + 1))
    else
        echo "  FAIL  $name"
        echo "        expected: stdout=$expected_stdout exit=$expected_exit"
        echo "        actual:   stdout=$actual_stdout exit=$actual_exit"
        FAIL=$((FAIL + 1))
        FAILED_TESTS+=("$name")
    fi
}

# Fake-uname runner: takes a value, sets up a fake `uname` that echoes it, sources
# helper, captures `detect_os` output + exit. Prints "<stdout>|<exit>" so the
# caller can pass both to _assert.
_run_with_fake_uname() {
    local fake_value="$1"
    local tmpdir
    tmpdir="$(mktemp -d)"
    cat > "$tmpdir/uname" <<FAKEEOF
#!/usr/bin/env bash
echo "$fake_value"
FAKEEOF
    chmod +x "$tmpdir/uname"

    # Run the helper in a subshell with PATH overridden, capture stdout + exit code.
    local stdout exit_code
    stdout="$(PATH="$tmpdir:$PATH" bash -c "source '$HELPER'; detect_os" 2>/dev/null)"
    exit_code=$?
    rm -rf "$tmpdir"
    echo "$stdout|$exit_code"
}

echo "=== test_detect_os.sh (issue #2751) ==="
echo ""

# Sanity: helper must exist
if [[ ! -f "$HELPER" ]]; then
    echo "  FAIL  helper script missing: $HELPER"
    echo "        (this is expected in TDD RED phase before implementation)"
    FAIL=$((FAIL + 1))
    FAILED_TESTS+=("helper_exists")
    echo ""
    echo "=== Summary: $PASS PASS, $FAIL FAIL ==="
    exit 1
fi

# Test cases per plan §TDD Test List (after r2 C2 token canonicalization to `macos`)

# test_detect_os_linux
result=$(_run_with_fake_uname "Linux")
_assert "test_detect_os_linux" "linux" "0" "${result%|*}" "${result##*|}"

# test_detect_os_macos (per r2 C2 — canonicalized from `darwin`)
result=$(_run_with_fake_uname "Darwin")
_assert "test_detect_os_macos" "macos" "0" "${result%|*}" "${result##*|}"

# test_detect_os_mingw
result=$(_run_with_fake_uname "MINGW64_NT-10.0")
_assert "test_detect_os_mingw" "windows" "0" "${result%|*}" "${result##*|}"

# test_detect_os_cygwin
result=$(_run_with_fake_uname "CYGWIN_NT-10.0")
_assert "test_detect_os_cygwin" "windows" "0" "${result%|*}" "${result##*|}"

# test_detect_os_msys (additional coverage — MSYS* is in the windows branch)
result=$(_run_with_fake_uname "MSYS_NT-10.0")
_assert "test_detect_os_msys" "windows" "0" "${result%|*}" "${result##*|}"

# test_detect_os_unknown — Plan9 is intentionally absurd
result=$(_run_with_fake_uname "Plan9")
_assert "test_detect_os_unknown" "unknown" "1" "${result%|*}" "${result##*|}"

echo ""
echo "=== Summary: $PASS PASS, $FAIL FAIL ==="
if [[ "$FAIL" -gt 0 ]]; then
    echo "    Failed: ${FAILED_TESTS[*]}"
    exit 1
fi
exit 0
