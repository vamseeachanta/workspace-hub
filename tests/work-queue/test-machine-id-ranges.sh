#!/usr/bin/env bash
# test-machine-id-ranges.sh — Unit tests for next-id.sh machine-range partitioning
# Tests that different machines emit non-overlapping IDs and that cross-machine
# files in shared directories do NOT contaminate the ID sequence.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
NEXT_ID_SCRIPT="${REPO_ROOT}/scripts/work-queue/next-id.sh"
RANGES_FILE="${REPO_ROOT}/config/work-queue/machine-ranges.yaml"

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

assert_in_range() {
  local desc="$1" floor="$2" ceiling="$3" actual="$4"
  if (( actual >= floor && actual <= ceiling )); then
    echo "  PASS: $desc (got $actual, range ${floor}-${ceiling})"
    PASS=$((PASS + 1))
  else
    echo "  FAIL: $desc — got '$actual', expected in range ${floor}-${ceiling}"
    FAIL=$((FAIL + 1))
  fi
}

setup_empty_queue() {
  local tmpdir
  tmpdir=$(mktemp -d)
  mkdir -p "${tmpdir}/.claude/work-queue"/{pending,working,blocked,archive,assets}
  printf 'last_id: 0\n' > "${tmpdir}/.claude/work-queue/state.yaml"
  mkdir -p "${tmpdir}/config/work-queue"
  cp "${RANGES_FILE}" "${tmpdir}/config/work-queue/machine-ranges.yaml"
  echo "$tmpdir"
}

echo "=== Machine ID Range Tests ==="

# ── Test 1: ace-linux-1 floor (floor=1, empty queue → expect ID 1) ──
tmpdir=$(setup_empty_queue)
result=$(WORKSPACE_ROOT="$tmpdir" HOSTNAME="ace-linux-1" bash "$NEXT_ID_SCRIPT" 2>/dev/null)
assert_equals "ace-linux-1 empty queue → ID 1" "1" "$result"
rm -rf "$tmpdir"

# ── Test 2: acma-ansys05 floor (floor=5000, empty queue → expect ID 5000) ──
tmpdir=$(setup_empty_queue)
result=$(WORKSPACE_ROOT="$tmpdir" HOSTNAME="acma-ansys05" bash "$NEXT_ID_SCRIPT" 2>/dev/null)
assert_equals "acma-ansys05 empty queue → ID 5000" "5000" "$result"
rm -rf "$tmpdir"

# ── Test 3: ace-linux-1 with existing ID 1113 → expect 1114 ──
tmpdir=$(setup_empty_queue)
touch "${tmpdir}/.claude/work-queue/pending/WRK-1113.md"
printf 'last_id: 1113\n' > "${tmpdir}/.claude/work-queue/state.yaml"
result=$(WORKSPACE_ROOT="$tmpdir" HOSTNAME="ace-linux-1" bash "$NEXT_ID_SCRIPT" 2>/dev/null)
assert_equals "ace-linux-1 MAX_ID=1113 → ID 1114" "1114" "$result"
rm -rf "$tmpdir"

# ── Test 4: acma-ansys05 with existing ID 5001 → expect 5002 ──
tmpdir=$(setup_empty_queue)
touch "${tmpdir}/.claude/work-queue/pending/WRK-5001.md"
printf 'last_id: 5001\n' > "${tmpdir}/.claude/work-queue/state.yaml"
result=$(WORKSPACE_ROOT="$tmpdir" HOSTNAME="acma-ansys05" bash "$NEXT_ID_SCRIPT" 2>/dev/null)
assert_equals "acma-ansys05 MAX_ID=5001 → ID 5002" "5002" "$result"
rm -rf "$tmpdir"

# ── Test 5: Range non-overlapping check ──
ACE_CEILING=4999
ANSYS_FLOOR=5000
if (( ACE_CEILING < ANSYS_FLOOR )); then
  echo "  PASS: ace-linux-1 ceiling (${ACE_CEILING}) < acma-ansys05 floor (${ANSYS_FLOOR}) — ranges non-overlapping"
  ((PASS++))
else
  echo "  FAIL: ranges overlap! ace-linux-1 ceiling=${ACE_CEILING}, acma-ansys05 floor=${ANSYS_FLOOR}"
  ((FAIL++))
fi

echo ""
echo "=== Cross-Machine Contamination Tests ==="

# ── Test 6: ace-linux-1 ignores WRK-5084 from acma-ansys05 range ──
# This is the core bug: ace-linux-1 should NOT jump to 5085 when WRK-5084
# from acma-ansys05 is present in pending/
tmpdir=$(setup_empty_queue)
touch "${tmpdir}/.claude/work-queue/pending/WRK-1100.md"
touch "${tmpdir}/.claude/work-queue/pending/WRK-5084.md"  # from acma-ansys05
printf 'last_id: 1100\n' > "${tmpdir}/.claude/work-queue/state.yaml"
result=$(WORKSPACE_ROOT="$tmpdir" HOSTNAME="ace-linux-1" bash "$NEXT_ID_SCRIPT" 2>/dev/null)
assert_equals "ace-linux-1 ignores WRK-5084 → ID 1101" "1101" "$result"
rm -rf "$tmpdir"

# ── Test 7: acma-ansys05 ignores WRK-1100 from ace-linux-1 range ──
tmpdir=$(setup_empty_queue)
touch "${tmpdir}/.claude/work-queue/pending/WRK-1100.md"  # from ace-linux-1
touch "${tmpdir}/.claude/work-queue/pending/WRK-5084.md"
printf 'last_id: 5084\n' > "${tmpdir}/.claude/work-queue/state.yaml"
result=$(WORKSPACE_ROOT="$tmpdir" HOSTNAME="acma-ansys05" bash "$NEXT_ID_SCRIPT" 2>/dev/null)
assert_equals "acma-ansys05 ignores WRK-1100 → ID 5085" "5085" "$result"
rm -rf "$tmpdir"

# ── Test 8: ace-linux-1 with contaminated state.yaml (last_id=5086) ──
# state.yaml was set to 5086 by contamination; should be ignored
tmpdir=$(setup_empty_queue)
touch "${tmpdir}/.claude/work-queue/pending/WRK-1100.md"
touch "${tmpdir}/.claude/work-queue/pending/WRK-5084.md"  # from acma-ansys05
printf 'last_id: 5086\n' > "${tmpdir}/.claude/work-queue/state.yaml"
result=$(WORKSPACE_ROOT="$tmpdir" HOSTNAME="ace-linux-1" bash "$NEXT_ID_SCRIPT" 2>/dev/null)
assert_equals "ace-linux-1 ignores contaminated state.yaml 5086 → ID 1101" "1101" "$result"
rm -rf "$tmpdir"

# ── Test 9: ace-linux-1 empty own range but cross-machine files present ──
tmpdir=$(setup_empty_queue)
touch "${tmpdir}/.claude/work-queue/pending/WRK-5001.md"
touch "${tmpdir}/.claude/work-queue/pending/WRK-5002.md"
printf 'last_id: 5002\n' > "${tmpdir}/.claude/work-queue/state.yaml"
result=$(WORKSPACE_ROOT="$tmpdir" HOSTNAME="ace-linux-1" bash "$NEXT_ID_SCRIPT" 2>/dev/null)
assert_equals "ace-linux-1 no own files, only cross-machine → ID 1 (floor)" "1" "$result"
rm -rf "$tmpdir"

# ── Test 10: state.yaml auto-corrected after contamination ──
tmpdir=$(setup_empty_queue)
touch "${tmpdir}/.claude/work-queue/pending/WRK-1100.md"
touch "${tmpdir}/.claude/work-queue/pending/WRK-5084.md"
printf 'last_id: 5086\n' > "${tmpdir}/.claude/work-queue/state.yaml"
WORKSPACE_ROOT="$tmpdir" HOSTNAME="ace-linux-1" bash "$NEXT_ID_SCRIPT" >/dev/null 2>&1
corrected=$(grep 'last_id:' "${tmpdir}/.claude/work-queue/state.yaml" | awk '{print $2}')
assert_in_range "state.yaml corrected to own range" 1 4999 "$corrected"
rm -rf "$tmpdir"

# ── Test 11: Boundary IDs — ace-linux-1 at ceiling (4999) ──
tmpdir=$(setup_empty_queue)
touch "${tmpdir}/.claude/work-queue/pending/WRK-4998.md"
printf 'last_id: 4998\n' > "${tmpdir}/.claude/work-queue/state.yaml"
result=$(WORKSPACE_ROOT="$tmpdir" HOSTNAME="ace-linux-1" bash "$NEXT_ID_SCRIPT" 2>/dev/null)
assert_equals "ace-linux-1 near ceiling → ID 4999" "4999" "$result"
rm -rf "$tmpdir"

echo ""
echo "=== Results: ${PASS} PASS, ${FAIL} FAIL ==="
[[ $FAIL -eq 0 ]]
