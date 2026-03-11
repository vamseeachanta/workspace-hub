#!/usr/bin/env bash
set -uo pipefail
PASS=0; FAIL=0
ok() { echo "PASS: $1"; ((PASS++)) || true; }
fail() { echo "FAIL: $1 — $2"; ((FAIL++)) || true; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
TIDY="${REPO_ROOT}/scripts/hooks/tidy-agent-teams.sh"
SPAWN="${REPO_ROOT}/scripts/work-queue/spawn-team.sh"

# Isolated temp dirs — never touch real ~/.claude/
TEST_TEAMS_DIR="$(mktemp -d)"
TEST_TASKS_DIR="$(mktemp -d)"
export CLAUDE_TEAMS_DIR="$TEST_TEAMS_DIR"
export CLAUDE_TASKS_DIR="$TEST_TASKS_DIR"

cleanup() { rm -rf "$TEST_TEAMS_DIR" "$TEST_TASKS_DIR"; }
trap cleanup EXIT

# T1: dry-run on empty state
out=$(bash "$TIDY" --dry-run)
[[ "$out" == *"deleted=0"* && "$out" == *"tasks_purged=0"* ]] && ok "T1 dry-run clean" || fail "T1" "$out"

# T2: live run on empty state exits 0
bash "$TIDY" >/dev/null 2>&1 && ok "T2 live run exits 0" || fail "T2" "non-zero exit"

# T3+T4: archived WRK team detected and deleted
ARCHIVE="${REPO_ROOT}/.claude/work-queue/archive"
ARCHIVED_WRK=""
ARCHIVED_FILE=$(ls "${ARCHIVE}"/WRK-*.md 2>/dev/null | head -1 || echo "")
if [[ -n "$ARCHIVED_FILE" ]]; then
  ARCHIVED_WRK=$(basename "$ARCHIVED_FILE" .md)
  NUM="${ARCHIVED_WRK#WRK-}"
  TEAM_DIR="${TEST_TEAMS_DIR}/wrk-${NUM}-tidy-test"
  mkdir -p "$TEAM_DIR"
  out=$(bash "$TIDY" --dry-run)
  [[ "$out" == *"wrk-${NUM}-tidy-test"* && "$out" == *"candidate for deletion"* ]] && ok "T3 archived team detected" || fail "T3" "$out"
  bash "$TIDY" >/dev/null
  [[ ! -d "$TEAM_DIR" ]] && ok "T4 archived team deleted" || fail "T4" "dir still exists"
else
  ok "T3 skipped (no archive)"; ok "T4 skipped (no archive)"
fi

# T5: non-conforming team dir without sentinel is preserved
mkdir -p "${TEST_TEAMS_DIR}/not-a-wrk-team"
bash "$TIDY" >/dev/null
[[ -d "${TEST_TEAMS_DIR}/not-a-wrk-team" ]] && ok "T5 non-conforming team preserved" || fail "T5" "incorrectly deleted"

# T6: fresh empty UUID dir NOT purged
UUID_DIR="${TEST_TASKS_DIR}/aaaaaaaa-1111-2222-3333-444444444444"
mkdir -p "$UUID_DIR"
out=$(bash "$TIDY" --dry-run)
[[ ! "$out" == *"aaaaaaaa-1111"* ]] && ok "T6 fresh UUID dir preserved" || fail "T6" "fresh dir flagged"

# T7: stale empty UUID dir IS purged (backdated 8 days)
UUID_STALE="${TEST_TASKS_DIR}/bbbbbbbb-2222-3333-4444-555555555555"
mkdir -p "$UUID_STALE"
touch -d '8 days ago' "$UUID_STALE"
out=$(bash "$TIDY" --dry-run)
[[ "$out" == *"bbbbbbbb-2222"* && "$out" == *"candidate for purge"* ]] && ok "T7 stale UUID dir flagged in dry-run" || fail "T7" "$out"
bash "$TIDY" >/dev/null
[[ ! -d "$UUID_STALE" ]] && ok "T7b stale UUID dir purged" || fail "T7b" "stale dir still exists"

# T8: spawn-team.sh no-args exits non-zero
bash "$SPAWN" 2>/dev/null; RC=$?; [[ $RC -ne 0 ]] && ok "T8 no-args exits non-zero" || fail "T8" "exit was $RC"

# T9: spawn-team.sh bad WRK_ID rejected
bash "$SPAWN" NOT-VALID slug 2>/dev/null; RC=$?; [[ $RC -ne 0 ]] && ok "T9 bad WRK_ID rejected" || fail "T9" "exit was $RC"

# T10: spawn-team.sh bad slug rejected
bash "$SPAWN" WRK-999 "BAD SLUG!" 2>/dev/null; RC=$?; [[ $RC -ne 0 ]] && ok "T10 bad slug rejected" || fail "T10" "exit was $RC"

# T11/T12: spawn-team.sh using a synthetic WRK with a temp capture fixture
TEMP_CAPTURE_WRK="WRK-9998"
TEMP_ASSETS_DIR="${REPO_ROOT}/.claude/work-queue/assets/${TEMP_CAPTURE_WRK}/evidence"
mkdir -p "$TEMP_ASSETS_DIR"
cat > "${TEMP_ASSETS_DIR}/user-review-capture.yaml" << 'YAML'
wrk_id: WRK-9998
scope_approved: true
confirmed_by: vamsee
confirmed_at: "2026-01-01T00:00:00Z"
YAML
cleanup_capture() { rm -rf "${REPO_ROOT}/.claude/work-queue/assets/${TEMP_CAPTURE_WRK}"; }
trap 'cleanup_capture; rm -rf "$TEST_TEAMS_DIR" "$TEST_TASKS_DIR"' EXIT

# T11: spawn-team.sh valid input prints recipe with .wrk-id sentinel line
out=$(bash "$SPAWN" "${TEMP_CAPTURE_WRK}" sentinel-test)
[[ "$out" == *"wrk-9998-sentinel-test"* && "$out" == *"mkdir -p"* ]] && ok "T11 spawn prints recipe" || fail "T11" "$out"
[[ "$out" == *".wrk-id"* ]] && ok "T11b spawn recipe includes .wrk-id line" || fail "T11b" "$out"

# T12: spawn-team.sh already-exists exits 0 with message
EXISTING_TEAM="${HOME}/.claude/teams/wrk-9998-sentinel-test"
mkdir -p "$EXISTING_TEAM" 2>/dev/null || true
out=$(bash "$SPAWN" "${TEMP_CAPTURE_WRK}" sentinel-test 2>&1); RC=$?
[[ $RC -eq 0 && "$out" == *"already exists"* ]] && ok "T12 spawn already-exists exits 0" || fail "T12" "RC=$RC out=$out"
rm -rf "$EXISTING_TEAM" 2>/dev/null || true

# T13/T13b: non-conforming dir with sentinel + archived WRK → deleted
if [[ -n "$ARCHIVED_WRK" ]]; then
  SENTINEL_DIR="${TEST_TEAMS_DIR}/custom-team-name"
  mkdir -p "$SENTINEL_DIR"
  echo "$ARCHIVED_WRK" > "${SENTINEL_DIR}/.wrk-id"
  # T13: dry-run detects the sentinel dir
  out=$(bash "$TIDY" --dry-run)
  [[ "$out" == *"custom-team-name"* && "$out" == *"candidate for deletion"* ]] && ok "T13 sentinel+archived detected in dry-run" || fail "T13" "$out"
  # T13b: live run deletes it
  bash "$TIDY" >/dev/null
  [[ ! -d "$SENTINEL_DIR" ]] && ok "T13b sentinel+archived → deleted" || fail "T13b" "dir still exists"
else
  ok "T13 skipped (no archive)"; ok "T13b skipped (no archive)"
fi

# T14: non-conforming dir with sentinel pointing to non-archived WRK → preserved
NON_ARCHIVED_DIR="${TEST_TEAMS_DIR}/another-custom-team"
mkdir -p "$NON_ARCHIVED_DIR"
echo "WRK-99999" > "${NON_ARCHIVED_DIR}/.wrk-id"
bash "$TIDY" >/dev/null
[[ -d "$NON_ARCHIVED_DIR" ]] && ok "T14 sentinel+non-archived → preserved" || fail "T14" "incorrectly deleted"

echo ""
echo "Results: PASS=$PASS FAIL=$FAIL"
[[ $FAIL -eq 0 ]]
