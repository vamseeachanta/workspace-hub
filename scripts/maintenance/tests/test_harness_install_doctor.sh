#!/usr/bin/env bash
# ABOUTME: Test suite for harness-install-doctor.sh — validates dry-run safety, the
#          ~/.codex/skills guardrail (OK + NEEDS-ATTENTION), exit codes, and idempotency.
# Run: bash scripts/maintenance/tests/test_harness_install_doctor.sh
#
# SAFETY: every invocation of the doctor runs with HOME pointed at a per-test
#   sandbox tmpdir, so the operator's real ~/.codex, ~/.gemini, and ~/.hermes are
#   NEVER read or mutated. The doctor still resolves REPO_ROOT via `git rev-parse`,
#   so we run it from inside the real repo; the only HOME-side effect is the
#   install-soul-runtime.sh step creating symlinks under the sandbox HOME's
#   ~/.codex / ~/.hermes, which is disposable.

set -uo pipefail

# ── Test Framework ────────────────────────────────────────────────────────────
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

pass() {
    TESTS_PASSED=$((TESTS_PASSED + 1))
    TESTS_RUN=$((TESTS_RUN + 1))
    echo "  PASS: $1"
}

fail() {
    TESTS_FAILED=$((TESTS_FAILED + 1))
    TESTS_RUN=$((TESTS_RUN + 1))
    echo "  FAIL: $1"
    [[ -n "${2:-}" ]] && echo "        $2"
}

assert_eq() {
    local expected="$1" actual="$2" label="$3"
    if [[ "$expected" == "$actual" ]]; then
        pass "$label"
    else
        fail "$label" "expected='$expected' actual='$actual'"
    fi
}

assert_contains() {
    local haystack="$1" needle="$2" label="$3"
    if echo "$haystack" | grep -qF "$needle"; then
        pass "$label"
    else
        fail "$label" "output does not contain '$needle'"
    fi
}

assert_not_contains() {
    local haystack="$1" needle="$2" label="$3"
    if echo "$haystack" | grep -qF "$needle"; then
        fail "$label" "output unexpectedly contains '$needle'"
    else
        pass "$label"
    fi
}

# ── Locate the script + repo ──────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ "$(basename "$SCRIPT_DIR")" == "tests" ]]; then
    DOCTOR="$SCRIPT_DIR/../harness-install-doctor.sh"
else
    DOCTOR="$SCRIPT_DIR/harness-install-doctor.sh"
fi

REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null || echo /mnt/local-analysis/workspace-hub)"

if [[ ! -f "$DOCTOR" ]]; then
    echo "ERROR: harness-install-doctor.sh not found at $DOCTOR" >&2
    DOCTOR="$REPO_ROOT/scripts/maintenance/harness-install-doctor.sh"
    if [[ ! -f "$DOCTOR" ]]; then
        echo "ERROR: Cannot find harness-install-doctor.sh" >&2
        exit 1
    fi
fi

echo "Testing: $DOCTOR"
echo "Repo:    $REPO_ROOT"
echo ""

# ── Sandbox infrastructure ────────────────────────────────────────────────────
TEST_DIR="$(mktemp -d)"
trap 'rm -rf "$TEST_DIR"' EXIT

# Build a fresh sandbox HOME with a healthy ~/.codex/skills/.system layout.
# Returns the path to the new sandbox HOME on stdout.
make_sandbox_home() {
    local home="$TEST_DIR/home-$$-$RANDOM"
    mkdir -p "$home/.codex/skills/.system/example-skill"
    echo "stub native system skill" > "$home/.codex/skills/.system/example-skill/SKILL.md"
    mkdir -p "$home/.hermes"
    echo "$home"
}

# Run the doctor with a sandbox HOME, from inside the repo so git rev-parse works.
# Usage: run_doctor <home> [DRY=0|1]   → prints combined stdout+stderr.
run_doctor() {
    local home="$1" dry="${2:-0}"
    ( cd "$REPO_ROOT" && HOME="$home" DOCTOR_DRY_RUN="$dry" bash "$DOCTOR" 2>&1 )
}

# Same as run_doctor but also exposes the doctor's exit code via the global RC.
# NOTE: callers use `OUT="$(run_doctor_rc ...)"`, which runs this function in a
# command-substitution SUBSHELL — a plain `RC=$?` set here would not survive back
# to the parent. So we persist the code to a file the parent reads after capture.
RC=0
RC_FILE="$TEST_DIR/last_rc"
run_doctor_rc() {
    local home="$1" dry="${2:-0}"
    local out rc
    out="$( cd "$REPO_ROOT" && HOME="$home" DOCTOR_DRY_RUN="$dry" bash "$DOCTOR" 2>&1 )"
    rc=$?
    echo "$rc" > "$RC_FILE"
    printf '%s' "$out"
}
# Read the exit code persisted by the most recent run_doctor_rc call.
read_rc() { RC="$(cat "$RC_FILE" 2>/dev/null || echo 99)"; }

# Strip ANSI color/escape sequences so status-line greps match the plain text.
strip_ansi() { sed -E 's/\x1b\[[0-9;]*m//g'; }

# Deterministic snapshot of the sandbox ~/.codex tree (type + symlink target).
snapshot_codex() {
    local home="$1"
    ( cd "$home" && find .codex -printf '%y %p -> %l\n' 2>/dev/null | LC_ALL=C sort )
}

# ── Test 1: syntax is clean (bash -n) ─────────────────────────────────────────
echo "Test 1: bash -n syntax check"
if bash -n "$DOCTOR" 2>/dev/null; then
    pass "harness-install-doctor.sh parses cleanly"
else
    fail "harness-install-doctor.sh parses cleanly" "bash -n reported syntax errors"
fi
echo ""

# ── Test 2: DOCTOR_DRY_RUN=1 mutates nothing ──────────────────────────────────
echo "Test 2: DOCTOR_DRY_RUN=1 changes nothing under the sandbox ~/.codex"
HOME2="$(make_sandbox_home)"
BEFORE="$(snapshot_codex "$HOME2")"
OUT2="$(run_doctor "$HOME2" 1)"
AFTER="$(snapshot_codex "$HOME2")"

assert_eq "$BEFORE" "$AFTER" "dry-run leaves ~/.codex tree byte-identical"
assert_contains "$OUT2" "dry-run: 1" "header reports dry-run mode"
# On the dry-run path the doctor never executes the installer; it reports a SKIP
# with the intended action instead of running it (no live mutation).
assert_contains "$OUT2" "would run install-soul-runtime.sh" "dry-run announces intended action without running it"
# In dry-run the soul-runtime step must be SKIP (installer is NOT executed),
# so no AGENTS.md symlink should appear.
assert_not_contains "$AFTER" ".codex/AGENTS.md" "dry-run did not create AGENTS.md symlink"
echo ""

# ── Test 3: guardrail OK — real ~/.codex/skills with .system stays a real dir ──
echo "Test 3: guardrail OK — healthy ~/.codex/skills/.system reported OK and left intact"
HOME3="$(make_sandbox_home)"
OUT3="$(run_doctor_rc "$HOME3" 0)"
read_rc; RC3="$RC"
OUT3_PLAIN="$(printf '%s' "$OUT3" | strip_ansi)"

assert_contains "$OUT3" "codex-skills" "doctor reports a codex-skills line"
# Healthy real dir with .system => OK status on the codex-skills line.
if echo "$OUT3_PLAIN" | grep -E 'OK[[:space:]]+codex-skills' >/dev/null; then
    pass "codex-skills reported OK"
else
    fail "codex-skills reported OK" "no 'OK ... codex-skills' line; got:
$(echo "$OUT3_PLAIN" | grep -i codex-skills)"
fi
# Post-run: still a real directory (NOT a symlink), with .system present.
if [[ -d "$HOME3/.codex/skills" && ! -L "$HOME3/.codex/skills" ]]; then
    pass "~/.codex/skills is still a real directory (not a symlink)"
else
    fail "~/.codex/skills is still a real directory (not a symlink)" \
         "doctor mutated the skills dir into a symlink or removed it"
fi
if [[ -d "$HOME3/.codex/skills/.system" ]]; then
    pass "~/.codex/skills/.system still present after run"
else
    fail "~/.codex/skills/.system still present after run" ".system was clobbered"
fi
assert_eq "0" "$RC3" "healthy sandbox exits 0"
echo ""

# ── Test 4: guardrail NEEDS-ATTENTION — stray symlink flagged, not clobbered ───
echo "Test 4: guardrail NEEDS-ATTENTION — stray ~/.codex/skills symlink flagged, exit 1, untouched"
HOME4="$(make_sandbox_home)"
# Replace the real skills dir with a stray symlink pointing elsewhere.
STRAY_TARGET="$TEST_DIR/stray-target-$$-$RANDOM"
mkdir -p "$STRAY_TARGET"
echo "decoy" > "$STRAY_TARGET/decoy.txt"
rm -rf "$HOME4/.codex/skills"
ln -s "$STRAY_TARGET" "$HOME4/.codex/skills"

OUT4="$(run_doctor_rc "$HOME4" 0)"
read_rc; RC4="$RC"
OUT4_PLAIN="$(printf '%s' "$OUT4" | strip_ansi)"

if echo "$OUT4_PLAIN" | grep -E 'NEEDS-ATTENTION[[:space:]]+codex-skills' >/dev/null; then
    pass "stray symlink reported NEEDS-ATTENTION for codex-skills"
else
    fail "stray symlink reported NEEDS-ATTENTION for codex-skills" \
         "got:
$(echo "$OUT4_PLAIN" | grep -i codex-skills)"
fi
assert_eq "1" "$RC4" "NEEDS-ATTENTION drives overall exit code 1"
# The doctor must NOT delete/clobber the stray symlink — guardrail check only.
if [[ -L "$HOME4/.codex/skills" ]]; then
    pass "stray symlink left in place (doctor did not delete it)"
else
    fail "stray symlink left in place (doctor did not delete it)" \
         "doctor mutated/removed the symlink it was only supposed to flag"
fi
if [[ "$(readlink "$HOME4/.codex/skills")" == "$STRAY_TARGET" ]]; then
    pass "stray symlink target unchanged"
else
    fail "stray symlink target unchanged" "target was rewritten"
fi
if [[ -f "$STRAY_TARGET/decoy.txt" ]]; then
    pass "stray symlink's pointee contents untouched"
else
    fail "stray symlink's pointee contents untouched" "doctor wrote through the symlink"
fi
echo ""

# ── Test 5: idempotency — two consecutive real runs both exit 0 ───────────────
echo "Test 5: idempotency — two consecutive non-dry runs in a healthy sandbox both exit 0"
HOME5="$(make_sandbox_home)"

OUT5A="$(run_doctor_rc "$HOME5" 0)"; read_rc; RC5A="$RC"
OUT5B="$(run_doctor_rc "$HOME5" 0)"; read_rc; RC5B="$RC"

assert_eq "0" "$RC5A" "first real run exits 0"
assert_eq "0" "$RC5B" "second real run exits 0 (idempotent)"
assert_contains "$OUT5A" "healthy" "first run reports healthy"
assert_contains "$OUT5B" "healthy" "second run reports healthy"
# Second run's soul-runtime step should report the symlink already correct (OK),
# proving re-run does not churn.
assert_contains "$OUT5B" "soul-runtime-symlinks" "second run still checks soul-runtime symlinks"
echo ""

# ── Results ───────────────────────────────────────────────────────────────────
echo "============================================"
echo "Results: $TESTS_PASSED/$TESTS_RUN passed, $TESTS_FAILED failed"
echo "============================================"

if [[ "$TESTS_FAILED" -gt 0 ]]; then
    exit 1
fi
exit 0
