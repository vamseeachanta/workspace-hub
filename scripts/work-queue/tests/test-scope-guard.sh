#!/usr/bin/env bash
# test-scope-guard.sh — Tests for set-active-wrk.sh scope guard (WRK-1174)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
QUEUE_DIR="${REPO_ROOT}/.claude/work-queue"
SET_ACTIVE="${SCRIPT_DIR}/../set-active-wrk.sh"

# ── Test scaffolding ──────────────────────────────────────────────────────────
PASS=0; FAIL=0; TOTAL=0
TEST_DIR="$(mktemp -d)"
trap 'rm -rf "$TEST_DIR"' EXIT

# Save and restore real active-wrk
REAL_ACTIVE="${REPO_ROOT}/.claude/state/active-wrk"
BACKUP_ACTIVE="${TEST_DIR}/active-wrk.backup"
[[ -f "$REAL_ACTIVE" ]] && cp "$REAL_ACTIVE" "$BACKUP_ACTIVE"
restore_active() {
    if [[ -f "$BACKUP_ACTIVE" ]]; then
        cp "$BACKUP_ACTIVE" "$REAL_ACTIVE"
    else
        rm -f "$REAL_ACTIVE"
    fi
}
trap 'restore_active; rm -rf "$TEST_DIR"' EXIT

assert_exit() {
    local label="$1" expected="$2"
    shift 2
    TOTAL=$((TOTAL + 1))
    local actual=0
    "$@" >/dev/null 2>&1 || actual=$?
    if [[ "$expected" == "$actual" ]]; then
        echo "  PASS: $label"
        PASS=$((PASS + 1))
    else
        echo "  FAIL: $label (expected exit=$expected, got exit=$actual)"
        FAIL=$((FAIL + 1))
    fi
}

assert_file_contains() {
    local label="$1" file="$2" pattern="$3"
    TOTAL=$((TOTAL + 1))
    if grep -q "$pattern" "$file" 2>/dev/null; then
        echo "  PASS: $label"
        PASS=$((PASS + 1))
    else
        echo "  FAIL: $label (pattern '$pattern' not found in $file)"
        FAIL=$((FAIL + 1))
    fi
}

assert_stderr_contains() {
    local label="$1" pattern="$2"
    shift 2
    TOTAL=$((TOTAL + 1))
    local stderr_file="${TEST_DIR}/stderr.tmp"
    "$@" >/dev/null 2>"$stderr_file" || true
    if grep -q "$pattern" "$stderr_file" 2>/dev/null; then
        echo "  PASS: $label"
        PASS=$((PASS + 1))
    else
        echo "  FAIL: $label (pattern '$pattern' not in stderr)"
        echo "  stderr: $(cat "$stderr_file")"
        FAIL=$((FAIL + 1))
    fi
}

# ── T1: Empty active-wrk → allows setting new WRK ───────────────────────────
echo "T1: empty active-wrk → exit 0, writes WRK + timestamp"
> "$REAL_ACTIVE"
assert_exit "T1a exit 0" 0 bash "$SET_ACTIVE" WRK-999
assert_file_contains "T1b WRK-999 written" "$REAL_ACTIVE" "^WRK-999$"
assert_file_contains "T1c started_at written" "$REAL_ACTIVE" "^started_at:"

# ── T2: Active WRK (status: working) blocks new WRK ─────────────────────────
echo "T2: active WRK-888 (working) blocks WRK-999 → exit 1"
# Create a stub WRK file with status: working
mkdir -p "${QUEUE_DIR}/working"
cat > "${QUEUE_DIR}/working/WRK-888.md" << 'STUB'
---
id: WRK-888
title: "test blocker"
status: working
---
STUB
printf 'WRK-888\nstarted_at: 2026-03-14T00:00:00Z\n' > "$REAL_ACTIVE"
assert_exit "T2a exit 1" 1 bash "$SET_ACTIVE" WRK-999
assert_stderr_contains "T2b SCOPE_GUARD_WARNING" "SCOPE_GUARD_WARNING" bash "$SET_ACTIVE" WRK-999
rm -f "${QUEUE_DIR}/working/WRK-888.md"

# ── T3: --force bypasses guard ───────────────────────────────────────────────
echo "T3: --force bypasses scope guard"
# Re-create blocker
cat > "${QUEUE_DIR}/working/WRK-888.md" << 'STUB'
---
id: WRK-888
title: "test blocker"
status: working
---
STUB
printf 'WRK-888\nstarted_at: 2026-03-14T00:00:00Z\n' > "$REAL_ACTIVE"
assert_exit "T3a --force exit 0" 0 bash "$SET_ACTIVE" WRK-999 --force
assert_file_contains "T3b WRK-999 written" "$REAL_ACTIVE" "^WRK-999$"
rm -f "${QUEUE_DIR}/working/WRK-888.md"

# ── T4: Active WRK (status: done) allows overwrite ──────────────────────────
echo "T4: active WRK-888 (done) allows WRK-999 → exit 0"
mkdir -p "${QUEUE_DIR}/working"
cat > "${QUEUE_DIR}/working/WRK-888.md" << 'STUB'
---
id: WRK-888
title: "test done"
status: done
---
STUB
printf 'WRK-888\nstarted_at: 2026-03-14T00:00:00Z\n' > "$REAL_ACTIVE"
assert_exit "T4a exit 0" 0 bash "$SET_ACTIVE" WRK-999
assert_file_contains "T4b WRK-999 written" "$REAL_ACTIVE" "^WRK-999$"
rm -f "${QUEUE_DIR}/working/WRK-888.md"

# ── T5: Active WRK (status: archived) allows overwrite ──────────────────────
echo "T5: active WRK-888 in archive/ allows WRK-999 → exit 0"
mkdir -p "${QUEUE_DIR}/archive/2026-03"
cat > "${QUEUE_DIR}/archive/2026-03/WRK-888.md" << 'STUB'
---
id: WRK-888
title: "test archived"
status: archived
---
STUB
printf 'WRK-888\nstarted_at: 2026-03-14T00:00:00Z\n' > "$REAL_ACTIVE"
assert_exit "T5a exit 0" 0 bash "$SET_ACTIVE" WRK-999
rm -f "${QUEUE_DIR}/archive/2026-03/WRK-888.md"

# ── T6: Same WRK re-activation allowed ──────────────────────────────────────
echo "T6: re-activating same WRK-999 → exit 0 (no guard)"
printf 'WRK-999\nstarted_at: 2026-03-14T00:00:00Z\n' > "$REAL_ACTIVE"
assert_exit "T6a same WRK exit 0" 0 bash "$SET_ACTIVE" WRK-999

# ── T7: No WRK file found but status unknown → blocks (conservative) ────────
echo "T7: active WRK-888 with no .md file found → blocks"
printf 'WRK-888\nstarted_at: 2026-03-14T00:00:00Z\n' > "$REAL_ACTIVE"
# Don't create any WRK-888.md — the script should block conservatively
assert_exit "T7a exit 1" 1 bash "$SET_ACTIVE" WRK-999

# ── Summary ──────────────────────────────────────────────────────────────────
echo ""
echo "Results: $PASS passed, $FAIL failed, $TOTAL total"
[[ $FAIL -eq 0 ]] && exit 0 || exit 1
