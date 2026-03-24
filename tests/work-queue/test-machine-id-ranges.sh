#!/usr/bin/env bash
# test-machine-id-ranges.sh — Verify next-id.sh is a hard-error stub (WRK-5140)
#
# next-id.sh has been replaced by gh-next-id.sh. This test confirms that the
# stub exits 1, mentions gh-next-id.sh in stderr, and produces no stdout.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
NEXT_ID_SCRIPT="${REPO_ROOT}/scripts/work-queue/next-id.sh"

PASS=0
FAIL=0

assert_equals() {
  local desc="$1" expected="$2" actual="$3"
  if [[ "$actual" == "$expected" ]]; then
    echo "  PASS: $desc"
    PASS=$((PASS + 1))
  else
    echo "  FAIL: $desc — expected '$expected', got '$actual'"
    FAIL=$((FAIL + 1))
  fi
}

echo "=== next-id.sh Stub Tests (WRK-5140) ==="

# ── Test 1: next-id.sh exits with code 1 ──
rc=0
stdout=$(bash "$NEXT_ID_SCRIPT" 2>/dev/null) || rc=$?
assert_equals "next-id.sh exits 1" "1" "$rc"

# ── Test 2: next-id.sh produces no stdout ──
assert_equals "next-id.sh produces no stdout" "" "$stdout"

# ── Test 3: next-id.sh mentions gh-next-id.sh in stderr ──
stderr=$(bash "$NEXT_ID_SCRIPT" 2>&1 >/dev/null) || true
if echo "$stderr" | grep -q "gh-next-id.sh"; then
  echo "  PASS: stderr mentions gh-next-id.sh"
  PASS=$((PASS + 1))
else
  echo "  FAIL: stderr does not mention gh-next-id.sh — got: $stderr"
  FAIL=$((FAIL + 1))
fi

echo ""
echo "=== Results: ${PASS} PASS, ${FAIL} FAIL ==="
[[ $FAIL -eq 0 ]]
