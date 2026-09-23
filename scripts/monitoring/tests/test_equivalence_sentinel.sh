#!/usr/bin/env bash
# End-to-end sentinel transaction tests for #3511. All Git refs and state live
# in throwaway repositories; the production equivalence-state ref is untouched.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel)"
PASS=0; FAIL=0
pass() { PASS=$((PASS + 1)); echo "  PASS: $1"; }
fail() { FAIL=$((FAIL + 1)); echo "  FAIL: $1 — $2"; }

TEST_DIR="$(mktemp -d)"
trap 'rm -rf "$TEST_DIR"' EXIT

make_repo() {
  local name="$1" repo="$TEST_DIR/$1" origin="$TEST_DIR/$1-origin.git"
  mkdir -p "$repo/scripts/monitoring/tests" "$repo/scripts/lib"
  cp "$SOURCE_ROOT/scripts/monitoring/equivalence-sentinel.sh" "$repo/scripts/monitoring/"
  cp "$SOURCE_ROOT/scripts/monitoring/equivalence-fingerprint.sh" "$repo/scripts/monitoring/"
  cp "$SOURCE_ROOT/scripts/monitoring/equivalence_state.py" "$repo/scripts/monitoring/"
  cp "$SOURCE_ROOT/scripts/monitoring/equivalence_schema.py" "$repo/scripts/monitoring/"
  cp "$SOURCE_ROOT/scripts/monitoring/equivalence_compare.py" "$repo/scripts/monitoring/"
  cp "$SOURCE_ROOT/scripts/lib/python-resolver.sh" "$repo/scripts/lib/"
  git init -q --bare "$origin"
  git -C "$repo" init -q
  git -C "$repo" config user.email sentinel@test.invalid
  git -C "$repo" config user.name sentinel-test
  git -C "$repo" add scripts
  git -C "$repo" commit -qm init
  git -C "$repo" branch -M main
  git -C "$repo" remote add origin "$origin"
  echo "$repo"
}

run_cycle() {
  local repo="$1" machine="${2:-ace-win-2}"
  (cd "$repo" && EQUIV_ROLE=contribute-minimal EQUIV_MACHINE="$machine" \
    bash scripts/monitoring/equivalence-sentinel.sh)
}

echo "Test 1: successful isolated cycle publishes and records exact health"
repo="$(make_repo success)"
if run_cycle "$repo"; then
  health="$repo/.claude/state/equivalence/publish-health.json"
  if uv run --no-project python "$repo/scripts/monitoring/equivalence_state.py" validate \
      --file "$repo/.claude/state/equivalence/local-fingerprint.json" >/dev/null &&
      uv run --no-project python -c \
        'import json,sys; d=json.load(open(sys.argv[1])); assert d == {"schema_version":1,"ts":d["ts"],"phase":"publish","duration_s":d["duration_s"],"rc":0}' \
        "$health"; then
    pass "successful cycle has validated fingerprint and publish health"
  else
    fail "successful cycle" "invalid fingerprint or health"
  fi
else
  fail "successful cycle" "sentinel returned nonzero"
fi

echo "Test 2: publish failure stops before comparison and exits 3"
repo="$(make_repo publish-failure)"
git -C "$repo" remote set-url origin "$TEST_DIR/missing-origin.git"
run_cycle "$repo"; rc=$?
if [[ "$rc" -eq 3 && ! -e "$repo/.claude/state/equivalence/divergences-latest.json" ]]; then
  pass "publish failure cannot be masked by comparison"
else
  fail "publish failure precedence" "rc=$rc or comparison artifact exists"
fi

echo "Test 3: invalid fingerprint blocks publish and preserves exit 3"
repo="$(make_repo invalid-fingerprint)"
run_cycle "$repo" '../unsafe'; rc=$?
if [[ "$rc" -eq 3 ]] && ! git --git-dir="$TEST_DIR/invalid-fingerprint-origin.git" \
    show-ref --verify --quiet refs/heads/equivalence-state; then
  pass "invalid fingerprint never publishes"
else
  fail "invalid fingerprint blocks publish" "rc=$rc or ref exists"
fi

echo "Test 4: publish-health persistence failure exits 4"
repo="$(make_repo health-failure)"
mkdir -p "$repo/.claude/state/equivalence/publish-health.json"
run_cycle "$repo"; rc=$?
if [[ "$rc" -eq 4 ]]; then
  pass "health persistence failure exits four"
else
  fail "health persistence failure" "rc=$rc"
fi

echo "Results: $PASS passed, $FAIL failed"
exit "$FAIL"
