#!/usr/bin/env bash
# test_orchestrate_auth.sh — TDD tests for scripts/setup/lib/orchestrate-auth.sh
# Issue: vamseeachanta/workspace-hub#2751 (Phase 2, G3)
#
# Strategy: same wrapper-function override pattern as test_install_provider_clis.sh.
# Source the helper, override its `auth_present` + `run_auth_login` + `prompt_hermes_env`
# wrappers, then call orchestrate_auth and assert on the action log.
#
# Run: bash tests/setup/test_orchestrate_auth.sh

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
HELPER="${REPO_ROOT}/scripts/setup/lib/orchestrate-auth.sh"

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

# $1: present_auths (space-separated: claude, codex, gh, gemini, hermes)
# $2: non_interactive flag (0 or 1)
_run_orchestrate() {
    local present_auths="$1" non_interactive="${2:-0}"
    local tmpdir; tmpdir="$(mktemp -d)"
    local logfile="$tmpdir/invoke.log"
    : > "$logfile"

    bash <<TESTEOF 2>/dev/null
        set -u
        source "$HELPER"
        WH_TEST_AUTHED="$present_auths"
        WH_TEST_LOG="$logfile"
        WH_NON_INTERACTIVE="$non_interactive"

        auth_present() {
            case " \$WH_TEST_AUTHED " in
                *" \$1 "*) return 0 ;;
                *)         return 1 ;;
            esac
        }
        run_auth_login() {
            echo "FAKE_INVOKE auth_login cli=\$1 cmd='\$2'" >> "\$WH_TEST_LOG"
        }
        prompt_hermes_env() {
            echo "FAKE_INVOKE prompt_hermes_env" >> "\$WH_TEST_LOG"
        }

        orchestrate_auth
TESTEOF
    cat "$logfile"
    rm -rf "$tmpdir"
}

echo "=== test_orchestrate_auth.sh (issue #2751 Phase 2 G3) ==="
echo ""

if [[ ! -f "$HELPER" ]]; then
    echo "  FAIL  helper script missing: $HELPER"
    echo "        (expected in TDD RED phase before implementation)"
    echo ""
    echo "=== Summary: 0 PASS, 1 FAIL ==="
    exit 1
fi

# Test 1: nothing authed → expect all 4 auth_login invocations + Hermes env prompt
log="$(_run_orchestrate "")"
_assert_contains "all_unauthed_claude_login"  "FAKE_INVOKE auth_login cli=claude cmd='claude auth login'" "$log"
_assert_contains "all_unauthed_codex_login"   "FAKE_INVOKE auth_login cli=codex cmd='codex auth login'" "$log"
_assert_contains "all_unauthed_gh_login"      "FAKE_INVOKE auth_login cli=gh cmd='gh auth login'" "$log"
# Gemini per r1 m1: NO `gemini auth` subcommand; use `gemini -p ping` first-run trigger
_assert_contains "all_unauthed_gemini_ping"   "FAKE_INVOKE auth_login cli=gemini cmd='gemini -p ping'" "$log"
_assert_not_contains "all_unauthed_no_gemini_auth_subcmd" "cmd='gemini auth'" "$log"
_assert_contains "all_unauthed_hermes_prompt" "FAKE_INVOKE prompt_hermes_env" "$log"

# Test 2: all authed → no auth_login invocations
log="$(_run_orchestrate "claude codex gh gemini hermes")"
_assert_not_contains "all_authed_no_claude"  "FAKE_INVOKE auth_login cli=claude" "$log"
_assert_not_contains "all_authed_no_codex"   "FAKE_INVOKE auth_login cli=codex" "$log"
_assert_not_contains "all_authed_no_gh"      "FAKE_INVOKE auth_login cli=gh" "$log"
_assert_not_contains "all_authed_no_gemini"  "FAKE_INVOKE auth_login cli=gemini" "$log"
_assert_not_contains "all_authed_no_hermes"  "FAKE_INVOKE prompt_hermes_env" "$log"

# Test 3: partial authed (claude + gh) → only codex + gemini + hermes prompt
log="$(_run_orchestrate "claude gh")"
_assert_not_contains "partial_no_claude"  "FAKE_INVOKE auth_login cli=claude" "$log"
_assert_not_contains "partial_no_gh"      "FAKE_INVOKE auth_login cli=gh" "$log"
_assert_contains "partial_yes_codex"      "FAKE_INVOKE auth_login cli=codex" "$log"
_assert_contains "partial_yes_gemini"     "FAKE_INVOKE auth_login cli=gemini cmd='gemini -p ping'" "$log"
_assert_contains "partial_yes_hermes"     "FAKE_INVOKE prompt_hermes_env" "$log"

# Test 4: --non-interactive mode → skip all auth_login + skip Hermes prompt
log="$(_run_orchestrate "" 1)"
_assert_not_contains "noninteractive_no_claude" "FAKE_INVOKE auth_login" "$log"
_assert_not_contains "noninteractive_no_hermes" "FAKE_INVOKE prompt_hermes_env" "$log"

echo ""
echo "=== Summary: $PASS PASS, $FAIL FAIL ==="
if [[ "$FAIL" -gt 0 ]]; then
    echo "    Failed: ${FAILED_TESTS[*]}"
    exit 1
fi
exit 0
