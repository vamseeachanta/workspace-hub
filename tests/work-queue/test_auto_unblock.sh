#!/usr/bin/env bash
# test_auto_unblock.sh — Tests for scripts/work-queue/auto-unblock.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || (cd "$SCRIPT_DIR/../.." && pwd))"
AUTO_UNBLOCK="${REPO_ROOT}/scripts/work-queue/auto-unblock.sh"

PASS=0
FAIL=0
TOTAL=0

assert_eq() {
  local label="$1" expected="$2" actual="$3"
  TOTAL=$((TOTAL + 1))
  if [[ "$expected" == "$actual" ]]; then
    echo "PASS: ${label}"
    PASS=$((PASS + 1))
  else
    echo "FAIL: ${label} (expected='${expected}', actual='${actual}')"
    FAIL=$((FAIL + 1))
  fi
}

assert_file_exists() {
  local label="$1" path="$2"
  TOTAL=$((TOTAL + 1))
  if [[ -f "$path" ]]; then
    echo "PASS: ${label}"
    PASS=$((PASS + 1))
  else
    echo "FAIL: ${label} (file not found: ${path})"
    FAIL=$((FAIL + 1))
  fi
}

assert_file_not_exists() {
  local label="$1" path="$2"
  TOTAL=$((TOTAL + 1))
  if [[ ! -f "$path" ]]; then
    echo "PASS: ${label}"
    PASS=$((PASS + 1))
  else
    echo "FAIL: ${label} (file should not exist: ${path})"
    FAIL=$((FAIL + 1))
  fi
}

# Create a minimal WRK .md file with frontmatter
make_wrk() {
  local file="$1" id="$2" status="$3" blocked_by="$4"
  cat > "$file" <<YAML
---
id: ${id}
title: Test item ${id}
status: ${status}
blocked_by: ${blocked_by}
---
# ${id}
YAML
}

# Create a WRK with block-list (multi-line) blocked_by
make_wrk_blocklist() {
  local file="$1" id="$2" status="$3"
  shift 3
  {
    echo "---"
    echo "id: ${id}"
    echo "title: Test item ${id}"
    echo "status: ${status}"
    echo "blocked_by:"
    for dep in "$@"; do
      echo "  - ${dep}"
    done
    echo "---"
    echo "# ${id}"
  } > "$file"
}

setup_tmpdir() {
  local tmp
  tmp=$(mktemp -d)
  mkdir -p "${tmp}/.claude/work-queue/blocked"
  mkdir -p "${tmp}/.claude/work-queue/pending"
  mkdir -p "${tmp}/.claude/work-queue/archive/2026-03"
  echo "$tmp"
}

# ── Test 1: Single blocker, all resolved → unblocks ──
test_single_blocker_resolved() {
  local tmp
  tmp=$(setup_tmpdir)

  make_wrk "${tmp}/.claude/work-queue/blocked/WRK-200.md" "WRK-200" "blocked" "[WRK-100]"
  make_wrk "${tmp}/.claude/work-queue/archive/2026-03/WRK-100.md" "WRK-100" "archived" "[]"

  output=$(WORKSPACE_ROOT="$tmp" bash "$AUTO_UNBLOCK" "WRK-100" 2>&1)

  assert_file_exists "T1: WRK-200 moved to pending" "${tmp}/.claude/work-queue/pending/WRK-200.md"
  assert_file_not_exists "T1: WRK-200 removed from blocked" "${tmp}/.claude/work-queue/blocked/WRK-200.md"

  local new_status
  new_status=$(grep '^status:' "${tmp}/.claude/work-queue/pending/WRK-200.md" | head -1 | sed 's/status: //')
  assert_eq "T1: status updated to pending" "pending" "$new_status"

  rm -rf "$tmp"
}

# ── Test 2: Multiple blockers, not all resolved → stays blocked ──
test_partial_blockers() {
  local tmp
  tmp=$(setup_tmpdir)

  make_wrk "${tmp}/.claude/work-queue/blocked/WRK-300.md" "WRK-300" "blocked" "[WRK-100, WRK-101]"
  make_wrk "${tmp}/.claude/work-queue/archive/2026-03/WRK-100.md" "WRK-100" "archived" "[]"
  # WRK-101 is NOT archived

  output=$(WORKSPACE_ROOT="$tmp" bash "$AUTO_UNBLOCK" "WRK-100" 2>&1)

  assert_file_exists "T2: WRK-300 stays in blocked" "${tmp}/.claude/work-queue/blocked/WRK-300.md"
  assert_file_not_exists "T2: WRK-300 not in pending" "${tmp}/.claude/work-queue/pending/WRK-300.md"

  rm -rf "$tmp"
}

# ── Test 3: Multiple blockers, all resolved → unblocks ──
test_all_blockers_resolved() {
  local tmp
  tmp=$(setup_tmpdir)

  make_wrk "${tmp}/.claude/work-queue/blocked/WRK-400.md" "WRK-400" "blocked" "[WRK-100, WRK-101]"
  make_wrk "${tmp}/.claude/work-queue/archive/2026-03/WRK-100.md" "WRK-100" "archived" "[]"
  make_wrk "${tmp}/.claude/work-queue/archive/2026-03/WRK-101.md" "WRK-101" "archived" "[]"

  output=$(WORKSPACE_ROOT="$tmp" bash "$AUTO_UNBLOCK" "WRK-101" 2>&1)

  assert_file_exists "T3: WRK-400 moved to pending" "${tmp}/.claude/work-queue/pending/WRK-400.md"
  assert_file_not_exists "T3: WRK-400 removed from blocked" "${tmp}/.claude/work-queue/blocked/WRK-400.md"

  rm -rf "$tmp"
}

# ── Test 4: No matching blocked items → no-op ──
test_no_matching_items() {
  local tmp
  tmp=$(setup_tmpdir)

  make_wrk "${tmp}/.claude/work-queue/blocked/WRK-500.md" "WRK-500" "blocked" "[WRK-999]"

  output=$(WORKSPACE_ROOT="$tmp" bash "$AUTO_UNBLOCK" "WRK-100" 2>&1)

  assert_file_exists "T4: WRK-500 stays in blocked" "${tmp}/.claude/work-queue/blocked/WRK-500.md"
  assert_file_not_exists "T4: WRK-500 not moved" "${tmp}/.claude/work-queue/pending/WRK-500.md"

  rm -rf "$tmp"
}

# ── Test 5: Block-list YAML format (multi-line) ──
test_blocklist_format() {
  local tmp
  tmp=$(setup_tmpdir)

  make_wrk_blocklist "${tmp}/.claude/work-queue/blocked/WRK-600.md" "WRK-600" "blocked" "WRK-100" "WRK-101"
  make_wrk "${tmp}/.claude/work-queue/archive/2026-03/WRK-100.md" "WRK-100" "archived" "[]"
  make_wrk "${tmp}/.claude/work-queue/archive/2026-03/WRK-101.md" "WRK-101" "archived" "[]"

  output=$(WORKSPACE_ROOT="$tmp" bash "$AUTO_UNBLOCK" "WRK-100" 2>&1)

  assert_file_exists "T5: WRK-600 moved (block-list format)" "${tmp}/.claude/work-queue/pending/WRK-600.md"
  assert_file_not_exists "T5: WRK-600 removed from blocked" "${tmp}/.claude/work-queue/blocked/WRK-600.md"

  rm -rf "$tmp"
}

# ── Test 6: Empty blocked_by → not unblocked ──
test_empty_blocked_by() {
  local tmp
  tmp=$(setup_tmpdir)

  make_wrk "${tmp}/.claude/work-queue/blocked/WRK-700.md" "WRK-700" "blocked" "[]"

  output=$(WORKSPACE_ROOT="$tmp" bash "$AUTO_UNBLOCK" "WRK-100" 2>&1)

  assert_file_exists "T6: WRK-700 stays (empty blocked_by)" "${tmp}/.claude/work-queue/blocked/WRK-700.md"
  assert_file_not_exists "T6: WRK-700 not moved" "${tmp}/.claude/work-queue/pending/WRK-700.md"

  rm -rf "$tmp"
}

# ── Test 7: Archived in different month subdirectory ──
test_different_archive_month() {
  local tmp
  tmp=$(setup_tmpdir)
  mkdir -p "${tmp}/.claude/work-queue/archive/2026-01"

  make_wrk "${tmp}/.claude/work-queue/blocked/WRK-800.md" "WRK-800" "blocked" "[WRK-100]"
  make_wrk "${tmp}/.claude/work-queue/archive/2026-01/WRK-100.md" "WRK-100" "archived" "[]"

  output=$(WORKSPACE_ROOT="$tmp" bash "$AUTO_UNBLOCK" "WRK-100" 2>&1)

  assert_file_exists "T7: WRK-800 moved (blocker in different month)" "${tmp}/.claude/work-queue/pending/WRK-800.md"

  rm -rf "$tmp"
}

# ── Test 8: ID normalization (bare number) ──
test_id_normalization() {
  local tmp
  tmp=$(setup_tmpdir)

  make_wrk "${tmp}/.claude/work-queue/blocked/WRK-900.md" "WRK-900" "blocked" "[WRK-100]"
  make_wrk "${tmp}/.claude/work-queue/archive/2026-03/WRK-100.md" "WRK-100" "archived" "[]"

  output=$(WORKSPACE_ROOT="$tmp" bash "$AUTO_UNBLOCK" "100" 2>&1)

  assert_file_exists "T8: WRK-900 moved (bare ID normalized)" "${tmp}/.claude/work-queue/pending/WRK-900.md"

  rm -rf "$tmp"
}

# ── Run all tests ──
echo "=== auto-unblock.sh tests ==="
test_single_blocker_resolved
test_partial_blockers
test_all_blockers_resolved
test_no_matching_items
test_blocklist_format
test_empty_blocked_by
test_different_archive_month
test_id_normalization

echo ""
echo "Results: ${PASS}/${TOTAL} passed, ${FAIL} failed"
[[ $FAIL -eq 0 ]] && exit 0 || exit 1
