#!/usr/bin/env bash
# ABOUTME: Test suite for equivalence-fingerprint.sh #3187 additions — the on_main
#          and index_lock_stale_min JSON fields.
# Run: bash scripts/monitoring/tests/test_equivalence_fingerprint.sh
#
# SAFETY: each test runs the emitter inside a throwaway `git init` repo (REPO_ROOT
#   resolves there), so the real checkout is never read/mutated. `pgrep` is stubbed
#   via PATH so the "is git live?" branch of the lock-age logic is deterministic.

set -uo pipefail

TESTS_RUN=0; TESTS_PASSED=0; TESTS_FAILED=0
pass() { TESTS_PASSED=$((TESTS_PASSED+1)); TESTS_RUN=$((TESTS_RUN+1)); echo "  PASS: $1"; }
fail() { TESTS_FAILED=$((TESTS_FAILED+1)); TESTS_RUN=$((TESTS_RUN+1)); echo "  FAIL: $1"; [[ -n "${2:-}" ]] && echo "        $2"; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FP="$SCRIPT_DIR/../equivalence-fingerprint.sh"
[[ -f "$FP" ]] || { echo "ERROR: equivalence-fingerprint.sh not found at $FP" >&2; exit 1; }
echo "Testing: $FP"; echo ""

TEST_DIR="$(mktemp -d)"
trap 'rm -rf "$TEST_DIR"' EXIT

make_repo() {  # arg1: branch to end on (main|handoff)
  local r="$TEST_DIR/repo-$$-$RANDOM"
  mkdir -p "$r"; git -C "$r" init -q
  git -C "$r" config user.email t@t; git -C "$r" config user.name t
  echo base > "$r/b.txt"; git -C "$r" add b.txt; git -C "$r" commit -qm init
  git -C "$r" branch -M main
  [[ "$1" == "handoff" ]] && git -C "$r" checkout -q -b handoff
  echo "$r"
}
make_pgrep_stub() {
  local code="$1" d="$TEST_DIR/bin-$$-$RANDOM"
  mkdir -p "$d"; printf '#!/usr/bin/env bash\nexit %s\n' "$code" > "$d/pgrep"; chmod +x "$d/pgrep"
  echo "$d"
}
# Run emitter in repo with pgrep stub; echo JSON.
run_fp() {
  local repo="$1" pcode="${2:-1}" stub
  stub="$(make_pgrep_stub "$pcode")"
  ( cd "$repo" && PATH="$stub:$PATH" EQUIV_ROLE=full bash "$FP" 2>/dev/null )
}
# Extract a top-level JSON field via python (prints repr; "MISSING" if absent).
field() { python3 -c 'import json,sys; d=json.load(sys.stdin); print(json.dumps(d.get(sys.argv[1],"MISSING")))' "$2" <<<"$1"; }

# ── Test 1: syntax ────────────────────────────────────────────────────────────
echo "Test 1: bash -n syntax"
bash -n "$FP" 2>/dev/null && pass "equivalence-fingerprint.sh parses cleanly" || fail "equivalence-fingerprint.sh parses cleanly" "bash -n errors"
echo ""

# ── Test 2: on_main true ──────────────────────────────────────────────────────
echo "Test 2: on_main=true when on main"
J="$(run_fp "$(make_repo main)" 1)"
[[ "$(field "$J" on_main)" == "true" ]] && pass "test_fingerprint_adds_on_main_field: on_main true" || fail "test_fingerprint_adds_on_main_field" "got on_main=$(field "$J" on_main)"
echo ""

# ── Test 3: on_main false ─────────────────────────────────────────────────────
echo "Test 3: on_main=false when off-branch"
J="$(run_fp "$(make_repo handoff)" 1)"
[[ "$(field "$J" on_main)" == "false" ]] && pass "test_fingerprint_adds_on_main_false: on_main false" || fail "test_fingerprint_adds_on_main_false" "got on_main=$(field "$J" on_main)"
echo ""

# ── Test 4: index_lock_stale_min numeric when orphan lock present ──────────────
echo "Test 4: stale-lock field numeric (lock + no live git)"
R="$(make_repo main)"; : > "$R/.git/index.lock"
J="$(run_fp "$R" 1)"   # pgrep miss => no live git => stale age reported
V="$(field "$J" index_lock_stale_min)"
if [[ "$V" != "null" && "$V" != "MISSING" ]] && python3 -c "import sys; float(sys.argv[1])" "$V" 2>/dev/null; then
  pass "test_fingerprint_stale_lock_field: numeric ($V)"
else
  fail "test_fingerprint_stale_lock_field: numeric" "got index_lock_stale_min=$V"
fi
echo ""

# ── Test 5: index_lock_stale_min null when no lock ────────────────────────────
echo "Test 5: stale-lock field null when no lock"
J="$(run_fp "$(make_repo main)" 1)"
[[ "$(field "$J" index_lock_stale_min)" == "null" ]] && pass "test_fingerprint_no_lock_null: null" || fail "test_fingerprint_no_lock_null" "got $(field "$J" index_lock_stale_min)"
echo ""

echo "============================================"
echo "Results: $TESTS_PASSED/$TESTS_RUN passed, $TESTS_FAILED failed"
echo "============================================"
[[ "$TESTS_FAILED" -gt 0 ]] && exit 1 || exit 0
