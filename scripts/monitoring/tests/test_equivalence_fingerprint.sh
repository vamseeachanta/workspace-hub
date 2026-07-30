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
field() {
  source "$SCRIPT_DIR/../../lib/python-resolver.sh" || return 1
  "${PYTHON_CMD[@]}" -c 'import json,sys; d=json.load(sys.stdin); print(json.dumps(d.get(sys.argv[1],"MISSING")))' "$2" <<<"$1"
}
is_number() {
  source "$SCRIPT_DIR/../../lib/python-resolver.sh" || return 1
  "${PYTHON_CMD[@]}" -c 'import sys; float(sys.argv[1])' "$1" 2>/dev/null
}

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
if [[ "$V" != "null" && "$V" != "MISSING" ]] && is_number "$V"; then
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

# ── Test 6: exact schema includes nullable prior-publish duration ─────────────
echo "Test 6: exact schema validates and includes null prior duration"
J="$(run_fp "$(make_repo main)" 1)"
if [[ "$(field "$J" last_publish_duration_s)" == "null" ]]; then
  pass "test_fingerprint_exact_schema_has_null_duration"
else
  fail "test_fingerprint_exact_schema_has_null_duration" "got $(field "$J" last_publish_duration_s)"
fi
echo ""

# ── Test 7: failed validation preserves prior valid output ──────────────────
echo "Test 7: invalid generated identity preserves prior output"
R="$(make_repo main)"; OUT="$R/fingerprint.json"; printf '%s' 'prior-valid-bytes' > "$OUT"
stub="$(make_pgrep_stub 1)"
if (cd "$R" && PATH="$stub:$PATH" EQUIV_ROLE=full EQUIV_MACHINE='../unsafe' \
    bash "$FP" --out "$OUT" >/dev/null 2>&1); then
  fail "test_fingerprint_failure_preserves_previous_valid_output" "invalid identity returned zero"
elif [[ "$(cat "$OUT")" == "prior-valid-bytes" ]]; then
  pass "test_fingerprint_failure_preserves_previous_valid_output"
else
  fail "test_fingerprint_failure_preserves_previous_valid_output" "prior output changed"
fi
echo ""

# ── Test 8: uv-only resolution preserves the legacy scalar API ──────────────
echo "Test 8: uv-only resolver keeps legacy scalar callers working"
direct_python="$(command -v python)"
if (
  uv() { [[ "$1 $2 $3" == "run --no-project python" ]] || return 2; shift 3; "$direct_python" "$@"; }
  python3() { return 1; }
  python() { return 1; }
  source "$SCRIPT_DIR/../../lib/python-resolver.sh" &&
    [[ -n "${PYTHON:-}" ]] && ${PYTHON} -c 'print("legacy-ok")' | grep -q '^legacy-ok$'
); then
  pass "test_resolver_uv_only_preserves_legacy_scalar"
else
  fail "test_resolver_uv_only_preserves_legacy_scalar" "legacy PYTHON command failed"
fi
echo ""

# ── Test 9: resolution fails when every candidate is broken ─────────────────
echo "Test 9: resolver fails when all candidates are broken"
if (
  uv() { return 1; }
  python3() { return 1; }
  python() { return 1; }
  source "$SCRIPT_DIR/../../lib/python-resolver.sh" 2>/dev/null
); then
  fail "test_resolver_fails_when_all_candidates_broken" "resolver returned zero"
else
  pass "test_resolver_fails_when_all_candidates_broken"
fi
echo ""

echo "============================================"
echo "Results: $TESTS_PASSED/$TESTS_RUN passed, $TESTS_FAILED failed"
echo "============================================"
[[ "$TESTS_FAILED" -gt 0 ]] && exit 1 || exit 0
