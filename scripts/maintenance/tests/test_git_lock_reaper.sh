#!/usr/bin/env bash
# ABOUTME: Test suite for git-lock-reaper.sh — validates the safe-reap decision tree:
#          no-lock / fresh-lock / live-git / orphan-confirmed / age-env-override.
# Run: bash scripts/maintenance/tests/test_git_lock_reaper.sh
#
# SAFETY: every test operates on a throwaway `git init` repo under a mktemp dir.
#   The reaper resolves REPO_ROOT via `git rev-parse --show-toplevel`, so each test
#   runs from inside its own sandbox repo — the real workspace-hub .git is never read
#   or mutated. `pgrep` is stubbed via a PATH-prepended shim so "is a git process
#   live?" is fully controlled, never depending on what is actually running.

set -uo pipefail

# ── Test framework (matches test_harness_install_doctor.sh) ────────────────────
TESTS_RUN=0; TESTS_PASSED=0; TESTS_FAILED=0
pass() { TESTS_PASSED=$((TESTS_PASSED+1)); TESTS_RUN=$((TESTS_RUN+1)); echo "  PASS: $1"; }
fail() { TESTS_FAILED=$((TESTS_FAILED+1)); TESTS_RUN=$((TESTS_RUN+1)); echo "  FAIL: $1"; [[ -n "${2:-}" ]] && echo "        $2"; }
assert_eq() { [[ "$1" == "$2" ]] && pass "$3" || fail "$3" "expected='$1' actual='$2'"; }
assert_contains() { echo "$1" | grep -qF "$2" && pass "$3" || fail "$3" "output missing '$2'"; }

# ── Locate the script ─────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REAPER="$SCRIPT_DIR/../git-lock-reaper.sh"
if [[ ! -f "$REAPER" ]]; then echo "ERROR: git-lock-reaper.sh not found at $REAPER" >&2; exit 1; fi
echo "Testing: $REAPER"; echo ""

TEST_DIR="$(mktemp -d)"
trap 'rm -rf "$TEST_DIR"' EXIT

# Build a throwaway git repo; echo its path.
make_repo() {
  local r="$TEST_DIR/repo-$$-$RANDOM"
  mkdir -p "$r"; git -C "$r" init -q 2>/dev/null
  echo "$r"
}

# Build a PATH shim dir whose `pgrep` exits with the requested code (0=hit, 1=miss).
# Echoes the shim dir to prepend to PATH.
make_pgrep_stub() {
  local code="$1" d="$TEST_DIR/bin-$$-$RANDOM"
  mkdir -p "$d"
  cat > "$d/pgrep" <<EOF
#!/usr/bin/env bash
exit $code
EOF
  chmod +x "$d/pgrep"
  echo "$d"
}

# Run reaper inside a repo with a given pgrep stub + optional AGE override.
# Usage: run_reaper <repo> <pgrep_code> [age_min] -> stdout+stderr; RC via file.
RC_FILE="$TEST_DIR/last_rc"
run_reaper() {
  local repo="$1" pcode="$2" age="${3:-5}" stub out rc
  stub="$(make_pgrep_stub "$pcode")"
  out="$( cd "$repo" && PATH="$stub:$PATH" LOCK_REAPER_AGE_MINUTES="$age" bash "$REAPER" 2>&1 )"
  rc=$?; echo "$rc" > "$RC_FILE"; printf '%s' "$out"
}
read_rc() { cat "$RC_FILE" 2>/dev/null || echo 99; }

lock_of() { echo "$1/.git/index.lock"; }

# ── Test 1: syntax ────────────────────────────────────────────────────────────
echo "Test 1: bash -n syntax"
bash -n "$REAPER" 2>/dev/null && pass "git-lock-reaper.sh parses cleanly" || fail "git-lock-reaper.sh parses cleanly" "bash -n errors"
echo ""

# ── Test 2: no lock present -> exit 0, no reap ────────────────────────────────
echo "Test 2: no lock present"
R="$(make_repo)"
OUT="$(run_reaper "$R" 1)"; RC="$(read_rc)"
assert_eq "0" "$RC" "test_reaper_no_lock: exits 0"
[[ ! -e "$(lock_of "$R")" ]] && pass "test_reaper_no_lock: no lock created" || fail "test_reaper_no_lock: no lock created"
echo ""

# ── Test 3: fresh lock (< AGE_MIN) -> skip ────────────────────────────────────
echo "Test 3: fresh lock skipped"
R="$(make_repo)"; L="$(lock_of "$R")"; : > "$L"; touch -d '1 minute ago' "$L"
OUT="$(run_reaper "$R" 1)"; RC="$(read_rc)"
assert_eq "0" "$RC" "test_reaper_fresh_lock: exits 0"
[[ -e "$L" ]] && pass "test_reaper_fresh_lock: lock preserved (too fresh)" || fail "test_reaper_fresh_lock: lock preserved" "reaped a fresh lock!"
assert_contains "$OUT" "fresh" "test_reaper_fresh_lock: logs 'fresh'"
echo ""

# ── Test 4: live git process -> skip even if old ──────────────────────────────
echo "Test 4: live git process skipped"
R="$(make_repo)"; L="$(lock_of "$R")"; : > "$L"; touch -d '10 minutes ago' "$L"
OUT="$(run_reaper "$R" 0)"; RC="$(read_rc)"   # pgrep code 0 = git is live
assert_eq "0" "$RC" "test_reaper_live_git_process: exits 0"
[[ -e "$L" ]] && pass "test_reaper_live_git_process: lock preserved (live git)" || fail "test_reaper_live_git_process: lock preserved" "reaped a live op's lock!"
assert_contains "$OUT" "live git" "test_reaper_live_git_process: logs 'live git'"
echo ""

# ── Test 5: orphan confirmed (old + no git) -> reap ───────────────────────────
echo "Test 5: orphan confirmed -> reaped"
R="$(make_repo)"; L="$(lock_of "$R")"; : > "$L"; touch -d '10 minutes ago' "$L"
OUT="$(run_reaper "$R" 1)"; RC="$(read_rc)"   # pgrep code 1 = no git
assert_eq "0" "$RC" "test_reaper_orphan_confirmed: exits 0"
[[ ! -e "$L" ]] && pass "test_reaper_orphan_confirmed: orphan lock removed" || fail "test_reaper_orphan_confirmed: orphan lock removed" "stale lock survived"
assert_contains "$OUT" "REAPER" "test_reaper_orphan_confirmed: alert logged"
echo ""

# ── Test 6: AGE env override ──────────────────────────────────────────────────
echo "Test 6: LOCK_REAPER_AGE_MINUTES override"
R="$(make_repo)"; L="$(lock_of "$R")"; : > "$L"; touch -d '3 minutes ago' "$L"
OUT="$(run_reaper "$R" 1 2)"; RC="$(read_rc)"  # age=2 -> 3>2 reaps
assert_eq "0" "$RC" "test_reaper_age_env_override: exits 0"
[[ ! -e "$L" ]] && pass "test_reaper_age_env_override: reaped (3m > AGE=2m)" || fail "test_reaper_age_env_override: reaped" "override not honored"
echo ""

echo "============================================"
echo "Results: $TESTS_PASSED/$TESTS_RUN passed, $TESTS_FAILED failed"
echo "============================================"
[[ "$TESTS_FAILED" -gt 0 ]] && exit 1 || exit 0
