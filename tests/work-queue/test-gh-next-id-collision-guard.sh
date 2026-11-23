#!/usr/bin/env bash
# test-gh-next-id-collision-guard.sh — Unit tests for _wrk_id_is_reserved() (WRK-5140)
#
# Sources the function from gh-next-id.sh and validates that known IDs are
# correctly classified as reserved or available.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
GH_SCRIPT="${REPO_ROOT}/scripts/work-queue/gh-next-id.sh"

# ── Source _wrk_id_is_reserved from gh-next-id.sh ────────────────────────────
WORKSPACE_ROOT="$REPO_ROOT"
BLOCKLIST="${WORKSPACE_ROOT}/config/work-queue/reserved-wrk-ids.txt"
eval "$(sed -n '/^_wrk_id_is_reserved/,/^}/p' "$GH_SCRIPT")"

PASS=0
FAIL=0

assert_reserved() {
  local desc="$1" id_num="$2"
  if _wrk_id_is_reserved "$id_num"; then
    echo "  PASS: $desc (WRK-${id_num} is reserved)"
    PASS=$((PASS + 1))
  else
    echo "  FAIL: $desc — WRK-${id_num} should be reserved but is not"
    FAIL=$((FAIL + 1))
  fi
}

assert_available() {
  local desc="$1" id_num="$2"
  if _wrk_id_is_reserved "$id_num"; then
    echo "  FAIL: $desc — WRK-${id_num} should be available but is reserved"
    FAIL=$((FAIL + 1))
  else
    echo "  PASS: $desc (WRK-${id_num} is available)"
    PASS=$((PASS + 1))
  fi
}

echo "=== Collision Guard Tests (WRK-5140) ==="

# ── Blocklist file exists ──
if [[ -f "$BLOCKLIST" ]]; then
  echo "  PASS: blocklist file exists"
  PASS=$((PASS + 1))
else
  echo "  FAIL: blocklist file not found at $BLOCKLIST"
  FAIL=$((FAIL + 1))
fi

# ── Known reserved ID (in blocklist) ──
assert_reserved "WRK-5097 in blocklist" "5097"

# ── Unknown ID not reserved ──
assert_available "WRK-99999 is available" "99999"

# ── Sample 5000+ IDs ──
assert_reserved "WRK-5000 (5000+ range)" "5000"
assert_reserved "WRK-5050 (5000+ range)" "5050"
assert_reserved "WRK-5140 (this WRK)" "5140"

# ── Danger zone IDs (actively used) ──
assert_reserved "WRK-1332 (danger zone)" "1332"
assert_reserved "WRK-1380 (danger zone)" "1380"

# ── Gap IDs (should NOT be reserved) ──
assert_available "WRK-1400 (gap)" "1400"
assert_available "WRK-2000 (gap)" "2000"
assert_available "WRK-3000 (gap)" "3000"

# ── Orphan asset directory ──
assert_reserved "WRK-6670 (orphan asset)" "6670"

echo ""
echo "=== Results: ${PASS} PASS, ${FAIL} FAIL ==="
[[ $FAIL -eq 0 ]]
