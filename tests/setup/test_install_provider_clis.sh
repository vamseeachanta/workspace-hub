#!/usr/bin/env bash
# test_install_provider_clis.sh — TDD tests for scripts/setup/lib/install-provider-clis.sh
# Issue: vamseeachanta/workspace-hub#2751 (Phase 2, G2)
#
# Strategy: source the helper, then redefine its `has_cli` wrapper to use a fixture
# variable. Redefine the channel-runner wrappers (`run_pkg_install`, `run_npm_install`,
# `run_pin_codex`) to log invocations instead of executing. Call install_provider_clis
# and assert on the log.
#
# Run: bash tests/setup/test_install_provider_clis.sh

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
HELPER="${REPO_ROOT}/scripts/setup/lib/install-provider-clis.sh"

PASS=0
FAIL=0
FAILED_TESTS=()

_assert_contains() {
    local name="$1" needle="$2" haystack="$3"
    if grep -qF -- "$needle" <<<"$haystack"; then
        echo "  PASS  $name"
        PASS=$((PASS + 1))
    else
        echo "  FAIL  $name"
        echo "        expected substring: $needle"
        echo "        actual log:"
        echo "$haystack" | sed 's/^/          /'
        FAIL=$((FAIL + 1))
        FAILED_TESTS+=("$name")
    fi
}

_assert_not_contains() {
    local name="$1" needle="$2" haystack="$3"
    if grep -qF -- "$needle" <<<"$haystack"; then
        echo "  FAIL  $name"
        echo "        forbidden substring present: $needle"
        FAIL=$((FAIL + 1))
        FAILED_TESTS+=("$name")
    else
        echo "  PASS  $name"
        PASS=$((PASS + 1))
    fi
}

# Run install_provider_clis with mocked wrappers and capture the action log.
# $1: os_name (linux/macos/windows)
# $2: present_clis (space-separated)
_run_install() {
    local os_name="$1" present_clis="$2"
    local tmpdir; tmpdir="$(mktemp -d)"
    local logfile="$tmpdir/invoke.log"
    : > "$logfile"

    # Run helper in a subshell so function overrides don't pollute caller state.
    bash <<TESTEOF 2>/dev/null
        set -u
        source "$HELPER"
        WH_TEST_PRESENT="$present_clis"
        WH_TEST_LOG="$logfile"

        # Override the helper's wrappers (the helper defines them as functions
        # that the test can hook).
        has_cli() {
            case " \$WH_TEST_PRESENT " in
                *" \$1 "*) return 0 ;;
                *)         return 1 ;;
            esac
        }
        run_pkg_install() {
            echo "FAKE_INVOKE pkg_install os=\$1 cli=\$2" >> "\$WH_TEST_LOG"
        }
        run_npm_install_global() {
            echo "FAKE_INVOKE npm install -g \$1" >> "\$WH_TEST_LOG"
        }
        run_pin_codex() {
            echo "FAKE_INVOKE pin-codex.sh" >> "\$WH_TEST_LOG"
        }
        run_node_install() {
            echo "FAKE_INVOKE node_install os=\$1" >> "\$WH_TEST_LOG"
        }
        elevate_check() { :; }   # bypass sudo check in tests

        install_provider_clis "$os_name"
TESTEOF
    cat "$logfile"
    rm -rf "$tmpdir"
}

echo "=== test_install_provider_clis.sh (issue #2751 Phase 2 G2) ==="
echo ""

# Sanity: helper must exist
if [[ ! -f "$HELPER" ]]; then
    echo "  FAIL  helper script missing: $HELPER"
    echo "        (expected in TDD RED phase before implementation)"
    echo ""
    echo "=== Summary: 0 PASS, 1 FAIL ==="
    exit 1
fi

# Test 1: linux, nothing installed → expect node install + gh via pkg + claude+gemini via npm + pin-codex
log="$(_run_install linux "")"
_assert_contains "linux_all_missing_pkg_gh" "FAKE_INVOKE pkg_install os=linux cli=gh" "$log"
_assert_contains "linux_all_missing_npm_claude" "FAKE_INVOKE npm install -g @anthropic-ai/claude-code" "$log"
_assert_contains "linux_all_missing_pin_codex" "FAKE_INVOKE pin-codex.sh" "$log"
_assert_contains "linux_all_missing_node_install" "FAKE_INVOKE node_install os=linux" "$log"

# Test 2: macos, nothing installed → expect brew (via pkg_install os=macos) for gh
log="$(_run_install macos "")"
_assert_contains "macos_all_missing_pkg_gh" "FAKE_INVOKE pkg_install os=macos cli=gh" "$log"

# Test 3: windows, nothing installed → expect choco/winget (via pkg_install os=windows) for gh
log="$(_run_install windows "")"
_assert_contains "windows_all_missing_pkg_gh" "FAKE_INVOKE pkg_install os=windows cli=gh" "$log"

# Test 4: linux with gh + claude already present → no install for them; codex+gemini still install
log="$(_run_install linux "gh claude node npm")"
_assert_not_contains "linux_gh_present_no_pkg_install" "FAKE_INVOKE pkg_install os=linux cli=gh" "$log"
_assert_not_contains "linux_claude_present_no_npm" "FAKE_INVOKE npm install -g @anthropic-ai/claude-code" "$log"
_assert_contains "linux_codex_missing_pin_codex" "FAKE_INVOKE pin-codex.sh" "$log"

# Test 5: linux with all 4 + node + npm present → no install invocations at all
log="$(_run_install linux "gh claude codex gemini node npm")"
_assert_not_contains "linux_all_present_no_pkg"   "FAKE_INVOKE pkg_install" "$log"
_assert_not_contains "linux_all_present_no_npm"   "FAKE_INVOKE npm install" "$log"
_assert_not_contains "linux_all_present_no_pin"   "FAKE_INVOKE pin-codex.sh" "$log"
_assert_not_contains "linux_all_present_no_node"  "FAKE_INVOKE node_install" "$log"

# Test 6: linux missing node but with gh + codex present → node must install before any npm install
log="$(_run_install linux "gh codex")"
_assert_contains "linux_missing_node_install" "FAKE_INVOKE node_install os=linux" "$log"
_assert_contains "linux_npm_install_after_node" "FAKE_INVOKE npm install -g @anthropic-ai/claude-code" "$log"

echo ""
echo "=== Summary: $PASS PASS, $FAIL FAIL ==="
if [[ "$FAIL" -gt 0 ]]; then
    echo "    Failed: ${FAILED_TESTS[*]}"
    exit 1
fi
exit 0
