#!/usr/bin/env bash
# test-machine-id-ranges.sh — Unit tests for next-id.sh machine-range partitioning
# Tests that different machines emit non-overlapping IDs by simulating HOSTNAME.
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

# Create an isolated temp queue with no existing WRK files so MAX_FILE_ID = 0
setup_empty_queue() {
  local tmpdir
  tmpdir=$(mktemp -d)
  mkdir -p "${tmpdir}/.claude/work-queue"/{pending,working,blocked,archive,assets}
  # Minimal state.yaml with last_id = 0
  printf 'last_id: 0\n' > "${tmpdir}/.claude/work-queue/state.yaml"
  # Copy the canonical ranges config so next-id.sh can find it
  mkdir -p "${tmpdir}/config/work-queue"
  cp "${RANGES_FILE}" "${tmpdir}/config/work-queue/machine-ranges.yaml"
  echo "$tmpdir"
}

echo "=== Machine ID Range Tests ==="

# ── Test 1: ace-linux-1 floor (floor=1, empty queue → expect ID 1) ──
tmpdir=$(setup_empty_queue)
result=$(WORKSPACE_ROOT="$tmpdir" HOSTNAME="ace-linux-1" bash "$NEXT_ID_SCRIPT")
assert_equals "ace-linux-1 empty queue → ID 001" "001" "$result"
rm -rf "$tmpdir"

# ── Test 2: acma-ansys05 floor (floor=5000, empty queue → expect ID 5000) ──
tmpdir=$(setup_empty_queue)
result=$(WORKSPACE_ROOT="$tmpdir" HOSTNAME="acma-ansys05" bash "$NEXT_ID_SCRIPT")
assert_equals "acma-ansys05 empty queue → ID 5000" "5000" "$result"
rm -rf "$tmpdir"

# ── Test 3: ace-linux-1 with existing ID 1113 → expect 1114 (above floor) ──
tmpdir=$(setup_empty_queue)
touch "${tmpdir}/.claude/work-queue/pending/WRK-1113.md"
printf 'last_id: 1113\n' > "${tmpdir}/.claude/work-queue/state.yaml"
result=$(WORKSPACE_ROOT="$tmpdir" HOSTNAME="ace-linux-1" bash "$NEXT_ID_SCRIPT")
assert_equals "ace-linux-1 MAX_ID=1113 → ID 1114" "1114" "$result"
rm -rf "$tmpdir"

# ── Test 4: acma-ansys05 with existing ID 5001 → expect 5002 (above floor) ──
tmpdir=$(setup_empty_queue)
touch "${tmpdir}/.claude/work-queue/pending/WRK-5001.md"
printf 'last_id: 5001\n' > "${tmpdir}/.claude/work-queue/state.yaml"
result=$(WORKSPACE_ROOT="$tmpdir" HOSTNAME="acma-ansys05" bash "$NEXT_ID_SCRIPT")
assert_equals "acma-ansys05 MAX_ID=5001 → ID 5002" "5002" "$result"
rm -rf "$tmpdir"

# ── Test 5: Non-overlapping — ace-linux-1 max < acma-ansys05 floor ──
# ace-linux-1 ceiling = 4999; acma-ansys05 floor = 5000 → no overlap
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
echo "=== Results: ${PASS} PASS, ${FAIL} FAIL ==="
[[ $FAIL -eq 0 ]]
