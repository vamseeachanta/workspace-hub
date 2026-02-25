#!/usr/bin/env bash
# ABOUTME: Smoke tests for the ace unified CLI entry point
# ABOUTME: Verifies routing to dm, we, au, wrk, docs, and help subcommands

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ACE="$SCRIPT_DIR/../ace"

PASS=0
FAIL=0

# Colours (safe fallback if no tty)
if [ -t 1 ]; then
    GREEN="\033[0;32m"; RED="\033[0;31m"; RESET="\033[0m"
else
    GREEN=""; RED=""; RESET=""
fi

pass() { echo -e "${GREEN}PASS${RESET} $1"; PASS=$((PASS + 1)); }
fail() { echo -e "${RED}FAIL${RESET} $1: $2"; FAIL=$((FAIL + 1)); }

assert_exit_0() {
    local label="$1"; shift
    if output=$("$@" 2>&1); then
        pass "$label"
    else
        fail "$label" "exit code $? — output: $output"
    fi
}

assert_exit_nonzero() {
    local label="$1"; shift
    if output=$("$@" 2>&1); then
        fail "$label" "expected non-zero exit but got 0 — output: $output"
    else
        pass "$label"
    fi
}

assert_contains() {
    local label="$1"
    local pattern="$2"
    local actual="$3"
    if echo "$actual" | grep -q "$pattern"; then
        pass "$label"
    else
        fail "$label" "pattern '$pattern' not found in output"
    fi
}

# ---------------------------------------------------------------------------
# Test: ace is executable
# ---------------------------------------------------------------------------
if [ -x "$ACE" ]; then
    pass "ace script is executable"
else
    fail "ace script is executable" "$ACE not found or not executable"
fi

# ---------------------------------------------------------------------------
# Test: ace help exits 0 and lists repos
# ---------------------------------------------------------------------------
help_out=$("$ACE" help 2>&1) && help_exit=0 || help_exit=$?
if [ "$help_exit" -eq 0 ]; then
    pass "ace help exits 0"
else
    fail "ace help exits 0" "exit code $help_exit"
fi

assert_contains "ace help mentions dm"  "dm"  "$help_out"
assert_contains "ace help mentions we"  "we"  "$help_out"
assert_contains "ace help mentions au"  "au"  "$help_out"
assert_contains "ace help mentions wrk" "wrk" "$help_out"
assert_contains "ace help mentions docs" "docs" "$help_out"

# ---------------------------------------------------------------------------
# Test: ace (no args) exits non-zero and shows usage
# ---------------------------------------------------------------------------
no_args_out=$("$ACE" 2>&1) && no_args_exit=0 || no_args_exit=$?
if [ "$no_args_exit" -ne 0 ]; then
    pass "ace with no args exits non-zero"
else
    fail "ace with no args exits non-zero" "exit 0 is not expected without a subcommand"
fi
assert_contains "ace no-args shows usage hint" "ace" "$no_args_out"

# ---------------------------------------------------------------------------
# Test: ace dm --help exits 0 and shows dm usage text
# (digitalmodel is a YAML-driven engine; ace intercepts --help)
# ---------------------------------------------------------------------------
dm_out=$("$ACE" dm --help 2>&1) && dm_exit=0 || dm_exit=$?
if [ "$dm_exit" -eq 0 ]; then
    pass "ace dm --help exits 0"
else
    fail "ace dm --help exits 0" "exit code $dm_exit — $dm_out"
fi
assert_contains "ace dm --help mentions digitalmodel" "digitalmodel" "$dm_out"

# ---------------------------------------------------------------------------
# Test: ace we --help exits 0 (worldenergydata has a real Typer CLI)
# ---------------------------------------------------------------------------
we_out=$("$ACE" we --help 2>&1) && we_exit=0 || we_exit=$?
if [ "$we_exit" -eq 0 ]; then
    pass "ace we --help exits 0"
else
    fail "ace we --help exits 0" "exit code $we_exit — $we_out"
fi
assert_contains "ace we --help shows commands" "worldenergydata" "$we_out"

# ---------------------------------------------------------------------------
# Test: ace au --help exits 0 and shows au usage text
# (assetutilities is a YAML-driven engine; ace intercepts --help)
# ---------------------------------------------------------------------------
au_out=$("$ACE" au --help 2>&1) && au_exit=0 || au_exit=$?
if [ "$au_exit" -eq 0 ]; then
    pass "ace au --help exits 0"
else
    fail "ace au --help exits 0" "exit code $au_exit — $au_out"
fi
assert_contains "ace au --help mentions assetutilities" "assetutilities" "$au_out"

# ---------------------------------------------------------------------------
# Test: ace wrk list exits 0 and shows WRK items
# ---------------------------------------------------------------------------
wrk_out=$("$ACE" wrk list 2>&1) && wrk_exit=0 || wrk_exit=$?
if [ "$wrk_exit" -eq 0 ]; then
    pass "ace wrk list exits 0"
else
    fail "ace wrk list exits 0" "exit code $wrk_exit — $wrk_out"
fi
assert_contains "ace wrk list shows WRK items" "WRK-" "$wrk_out"

# ---------------------------------------------------------------------------
# Test: ace wrk show with valid ID exits 0
# ---------------------------------------------------------------------------
first_wrk=$(ls /mnt/local-analysis/workspace-hub/.claude/work-queue/pending/ 2>/dev/null | \
    grep -E '^WRK-[0-9]+\.md$' | sort | head -1 | sed 's/\.md$//')
if [ -n "$first_wrk" ]; then
    wrk_show_out=$("$ACE" wrk show "$first_wrk" 2>&1) && wrk_show_exit=0 || wrk_show_exit=$?
    if [ "$wrk_show_exit" -eq 0 ]; then
        pass "ace wrk show $first_wrk exits 0"
    else
        fail "ace wrk show $first_wrk exits 0" "exit code $wrk_show_exit — $wrk_show_out"
    fi
else
    pass "ace wrk show (skipped — no pending WRK items)"
fi

# ---------------------------------------------------------------------------
# Test: ace wrk show with missing ID exits non-zero
# ---------------------------------------------------------------------------
bad_out=$("$ACE" wrk show WRK-99999 2>&1) && bad_exit=0 || bad_exit=$?
if [ "$bad_exit" -ne 0 ]; then
    pass "ace wrk show missing ID exits non-zero"
else
    fail "ace wrk show missing ID exits non-zero" "expected failure but got exit 0"
fi

# ---------------------------------------------------------------------------
# Test: ace docs query --help exits 0
# ---------------------------------------------------------------------------
docs_out=$("$ACE" docs query --help 2>&1) && docs_exit=0 || docs_exit=$?
if [ "$docs_exit" -eq 0 ]; then
    pass "ace docs query --help exits 0"
else
    fail "ace docs query --help exits 0" "exit code $docs_exit — $docs_out"
fi

# ---------------------------------------------------------------------------
# Test: ace unknown subcommand exits non-zero
# ---------------------------------------------------------------------------
unk_out=$("$ACE" _unknown_cmd_ 2>&1) && unk_exit=0 || unk_exit=$?
if [ "$unk_exit" -ne 0 ]; then
    pass "ace unknown subcommand exits non-zero"
else
    fail "ace unknown subcommand exits non-zero" "expected failure but got exit 0"
fi
assert_contains "ace unknown shows error message" "Unknown" "$unk_out"

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
TOTAL=$((PASS + FAIL))
echo ""
echo "Results: $PASS/$TOTAL passed"
if [ "$FAIL" -gt 0 ]; then
    echo -e "${RED}$FAIL test(s) failed.${RESET}"
    exit 1
else
    echo -e "${GREEN}All tests passed.${RESET}"
    exit 0
fi
