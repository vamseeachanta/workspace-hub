#!/usr/bin/env bash
# test-feature-auto-close.sh — Unit tests for feature-auto-close.sh
# Tests the logic of parent feature auto-close when children archive.
set -euo pipefail

PASS=0
FAIL=0
REPO_ROOT="$(git rev-parse --show-toplevel)"
FEATURE_AUTO_CLOSE="${REPO_ROOT}/scripts/work-queue/feature-auto-close.sh"

# ── Helpers ──────────────────────────────────────────────────────────────────

setup_tmp() {
  TMP=$(mktemp -d)
  QUEUE="${TMP}/work-queue"
  FAKE_WS="${TMP}/workspace"
  mkdir -p "${QUEUE}/pending" "${QUEUE}/working" "${QUEUE}/done"
  mkdir -p "${QUEUE}/archive/2026-03"
  # Create fake workspace with stub scripts
  mkdir -p "${FAKE_WS}/scripts/work-queue"
  # Stub feature-close-check.sh that reads WORK_QUEUE_ROOT
  cat > "${FAKE_WS}/scripts/work-queue/feature-close-check.sh" <<'STUB'
#!/usr/bin/env bash
set -euo pipefail
WRK_ID="${1:?}"
WORK_QUEUE_ROOT="${WORK_QUEUE_ROOT:?}"
# Find the WRK file
WRK_FILE=""
for dir in pending working blocked done; do
  [[ -f "${WORK_QUEUE_ROOT}/${dir}/${WRK_ID}.md" ]] && WRK_FILE="${WORK_QUEUE_ROOT}/${dir}/${WRK_ID}.md" && break
done
[[ -z "$WRK_FILE" ]] && WRK_FILE=$(find "${WORK_QUEUE_ROOT}" -name "${WRK_ID}.md" 2>/dev/null | head -1 || true)
[[ -z "$WRK_FILE" ]] && { echo "ERROR: ${WRK_ID} not found"; exit 1; }
# Parse children
children_line=$(grep '^children:' "$WRK_FILE" | head -1 || true)
inline=$(echo "$children_line" | sed 's/children: *\[//;s/\].*//')
IFS=',' read -ra CHILDREN <<< "$inline"
BLOCKED=0
for child in "${CHILDREN[@]}"; do
  child="${child// /}"
  [[ -z "$child" ]] && continue
  child_file=$(find "${WORK_QUEUE_ROOT}" -name "${child}.md" 2>/dev/null | head -1 || true)
  child_status="unknown"
  [[ -n "$child_file" ]] && child_status=$(grep '^status:' "$child_file" | head -1 | awk '{print $2}' || echo "unknown")
  [[ "$child_status" != "archived" ]] && BLOCKED=1
done
[[ $BLOCKED -eq 0 ]] && exit 0 || exit 1
STUB
  chmod +x "${FAKE_WS}/scripts/work-queue/feature-close-check.sh"
  # Stub close-item.sh that just records it was called
  cat > "${FAKE_WS}/scripts/work-queue/close-item.sh" <<'STUB'
#!/usr/bin/env bash
echo "CLOSE_CALLED:$1" >> "${CLOSE_LOG:-/dev/null}"
STUB
  chmod +x "${FAKE_WS}/scripts/work-queue/close-item.sh"
}

teardown_tmp() {
  rm -rf "$TMP"
}

assert_eq() {
  local label="$1" expected="$2" actual="$3"
  if [[ "$expected" == "$actual" ]]; then
    echo "PASS: ${label}"
    PASS=$((PASS + 1))
  else
    echo "FAIL: ${label} — expected '${expected}', got '${actual}'"
    FAIL=$((FAIL + 1))
  fi
}

assert_contains() {
  local label="$1" needle="$2" haystack="$3"
  if echo "$haystack" | grep -qF "$needle"; then
    echo "PASS: ${label}"
    PASS=$((PASS + 1))
  else
    echo "FAIL: ${label} — expected output to contain '${needle}'"
    FAIL=$((FAIL + 1))
  fi
}

write_wrk() {
  local path="$1" id="$2" extra="${3:-}"
  cat > "$path" <<EOF
---
id: ${id}
status: archived
${extra}
---
# ${id}
EOF
}

# ── Test 1: No parent field → silent exit 0 ──────────────────────────────────

test_no_parent_exits_silently() {
  setup_tmp
  write_wrk "${QUEUE}/archive/2026-03/WRK-301.md" "WRK-301"
  rc=0
  output=$(WORKSPACE_ROOT="$FAKE_WS" WORK_QUEUE_ROOT="$QUEUE" \
    bash "$FEATURE_AUTO_CLOSE" "WRK-301" 2>&1) || rc=$?
  assert_eq "no-parent exits 0" "0" "$rc"
  # Should not mention Parent
  parent_match=$(echo "$output" | grep -c "Parent" || true)
  if [[ "$parent_match" -gt 0 ]]; then
    echo "FAIL: no-parent should not mention Parent"
    FAIL=$((FAIL + 1))
  else
    echo "PASS: no-parent produces no parent message"
    PASS=$((PASS + 1))
  fi
  teardown_tmp
}

# ── Test 2: Item not found → silent exit 0 ───────────────────────────────────

test_item_not_found() {
  setup_tmp
  rc=0
  WORKSPACE_ROOT="$FAKE_WS" WORK_QUEUE_ROOT="$QUEUE" \
    bash "$FEATURE_AUTO_CLOSE" "WRK-999" 2>&1 || rc=$?
  assert_eq "item-not-found exits 0" "0" "$rc"
  teardown_tmp
}

# ── Test 3: All children archived → auto-close triggered ─────────────────────

test_all_children_archived() {
  setup_tmp

  # Parent feature WRK in pending
  cat > "${QUEUE}/pending/WRK-200.md" <<'EOF'
---
id: WRK-200
status: pending
type: feature
children: [WRK-201, WRK-202]
---
# Feature WRK
EOF

  # Both children archived
  write_wrk "${QUEUE}/archive/2026-03/WRK-201.md" "WRK-201" "parent: WRK-200"
  write_wrk "${QUEUE}/archive/2026-03/WRK-202.md" "WRK-202" "parent: WRK-200"

  CLOSE_LOG="${TMP}/close-calls.log"
  output=$(WORKSPACE_ROOT="$FAKE_WS" WORK_QUEUE_ROOT="$QUEUE" \
    CLOSE_LOG="$CLOSE_LOG" \
    bash "$FEATURE_AUTO_CLOSE" "WRK-202" 2>&1) || true
  assert_contains "all-children-archived message" \
    "All children of WRK-200 archived" "$output"
  # Verify close-item was called with parent ID
  if [[ -f "$CLOSE_LOG" ]] && grep -q "CLOSE_CALLED:WRK-200" "$CLOSE_LOG"; then
    echo "PASS: close-item.sh called for parent WRK-200"
    PASS=$((PASS + 1))
  else
    echo "FAIL: close-item.sh was not called for parent WRK-200"
    FAIL=$((FAIL + 1))
  fi
  teardown_tmp
}

# ── Test 4: Not all children archived → no close ─────────────────────────────

test_not_all_children_archived() {
  setup_tmp

  cat > "${QUEUE}/pending/WRK-200.md" <<'EOF'
---
id: WRK-200
status: pending
type: feature
children: [WRK-201, WRK-202]
---
# Feature WRK
EOF

  # Only WRK-201 archived; WRK-202 still working
  write_wrk "${QUEUE}/archive/2026-03/WRK-201.md" "WRK-201" "parent: WRK-200"
  cat > "${QUEUE}/working/WRK-202.md" <<'EOF'
---
id: WRK-202
status: working
parent: WRK-200
---
# Child WRK
EOF

  CLOSE_LOG="${TMP}/close-calls.log"
  output=$(WORKSPACE_ROOT="$FAKE_WS" WORK_QUEUE_ROOT="$QUEUE" \
    CLOSE_LOG="$CLOSE_LOG" \
    bash "$FEATURE_AUTO_CLOSE" "WRK-201" 2>&1) || true
  assert_contains "not-all-archived message" \
    "still has unarchived children" "$output"
  # Verify close-item was NOT called
  if [[ ! -f "$CLOSE_LOG" ]]; then
    echo "PASS: close-item.sh not called (parent has unarchived children)"
    PASS=$((PASS + 1))
  else
    echo "FAIL: close-item.sh should not have been called"
    FAIL=$((FAIL + 1))
  fi
  teardown_tmp
}

# ── Test 5: Bare ID normalization ────────────────────────────────────────────

test_id_normalization() {
  setup_tmp
  write_wrk "${QUEUE}/archive/2026-03/WRK-301.md" "WRK-301"
  rc=0
  WORKSPACE_ROOT="$FAKE_WS" WORK_QUEUE_ROOT="$QUEUE" \
    bash "$FEATURE_AUTO_CLOSE" "301" 2>&1 || rc=$?
  assert_eq "bare-id normalization exits 0" "0" "$rc"
  teardown_tmp
}

# ── Test 6: Missing argument → exit 1 ────────────────────────────────────────

test_missing_argument() {
  setup_tmp
  rc=0
  WORKSPACE_ROOT="$FAKE_WS" WORK_QUEUE_ROOT="$QUEUE" \
    bash "$FEATURE_AUTO_CLOSE" 2>&1 || rc=$?
  assert_eq "missing-argument exits 1" "1" "$rc"
  teardown_tmp
}

# ── Run all tests ────────────────────────────────────────────────────────────

echo "=== feature-auto-close.sh tests ==="
test_no_parent_exits_silently
test_item_not_found
test_all_children_archived
test_not_all_children_archived
test_id_normalization
test_missing_argument

echo ""
echo "Results: ${PASS} passed, ${FAIL} failed"
[[ "$FAIL" -eq 0 ]] && exit 0 || exit 1
