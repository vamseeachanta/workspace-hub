#!/usr/bin/env bash
# ABOUTME: Test suite for return-to-main-guard.sh — validates the branch-restore
#          decision tree: already-main / off-main-clean / off-main-staged (refuse) /
#          off-main-untracked-only (stash+restore) / off-main-live-git (skip).
# Run: bash scripts/maintenance/tests/test_return_to_main_guard.sh
#
# SAFETY: each test runs in a throwaway `git init` repo with a real `main` branch
#   and a `handoff` feature branch. The guard resolves REPO_ROOT via git, so it acts
#   only on the sandbox; the real workspace-hub checkout is never touched. `pgrep` is
#   stubbed via PATH so "is a git op live?" is fully controlled.

set -uo pipefail

TESTS_RUN=0; TESTS_PASSED=0; TESTS_FAILED=0
pass() { TESTS_PASSED=$((TESTS_PASSED+1)); TESTS_RUN=$((TESTS_RUN+1)); echo "  PASS: $1"; }
fail() { TESTS_FAILED=$((TESTS_FAILED+1)); TESTS_RUN=$((TESTS_RUN+1)); echo "  FAIL: $1"; [[ -n "${2:-}" ]] && echo "        $2"; }
assert_eq() { [[ "$1" == "$2" ]] && pass "$3" || fail "$3" "expected='$1' actual='$2'"; }
assert_contains() { echo "$1" | grep -qF "$2" && pass "$3" || fail "$3" "output missing '$2'"; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GUARD="$SCRIPT_DIR/../return-to-main-guard.sh"
[[ -f "$GUARD" ]] || { echo "ERROR: return-to-main-guard.sh not found at $GUARD" >&2; exit 1; }
echo "Testing: $GUARD"; echo ""

TEST_DIR="$(mktemp -d)"
trap 'rm -rf "$TEST_DIR"' EXIT

# Repo with a real main branch + a handoff feature branch; checked out on handoff.
make_guard_repo() {
  local r="$TEST_DIR/repo-$$-$RANDOM"
  mkdir -p "$r"
  git -C "$r" init -q
  git -C "$r" config user.email t@t; git -C "$r" config user.name t
  echo base > "$r/base.txt"; git -C "$r" add base.txt; git -C "$r" commit -qm init
  git -C "$r" branch -M main
  git -C "$r" checkout -q -b handoff
  echo "$r"
}

make_pgrep_stub() {
  local code="$1" d="$TEST_DIR/bin-$$-$RANDOM"
  mkdir -p "$d"; printf '#!/usr/bin/env bash\nexit %s\n' "$code" > "$d/pgrep"; chmod +x "$d/pgrep"
  echo "$d"
}

RC_FILE="$TEST_DIR/last_rc"
run_guard() {
  local repo="$1" pcode="$2" stub out rc
  stub="$(make_pgrep_stub "$pcode")"
  out="$( cd "$repo" && PATH="$stub:$PATH" bash "$GUARD" 2>&1 )"
  rc=$?; echo "$rc" > "$RC_FILE"; printf '%s' "$out"
}
read_rc() { cat "$RC_FILE" 2>/dev/null || echo 99; }
branch_of() { git -C "$1" symbolic-ref --short HEAD 2>/dev/null; }

# ── Test 1: syntax ────────────────────────────────────────────────────────────
echo "Test 1: bash -n syntax"
bash -n "$GUARD" 2>/dev/null && pass "return-to-main-guard.sh parses cleanly" || fail "return-to-main-guard.sh parses cleanly" "bash -n errors"
echo ""

# ── Test 2: already on main -> no-op ──────────────────────────────────────────
echo "Test 2: already on main"
R="$(make_guard_repo)"; git -C "$R" checkout -q main
OUT="$(run_guard "$R" 1)"; RC="$(read_rc)"
assert_eq "0" "$RC" "test_guard_already_main: exits 0"
assert_eq "main" "$(branch_of "$R")" "test_guard_already_main: stays on main"
echo ""

# ── Test 3: off main, clean -> checkout main ──────────────────────────────────
echo "Test 3: off main + clean"
R="$(make_guard_repo)"
OUT="$(run_guard "$R" 1)"; RC="$(read_rc)"
assert_eq "0" "$RC" "test_guard_off_main_clean: exits 0"
assert_eq "main" "$(branch_of "$R")" "test_guard_off_main_clean: returned to main"
echo ""

# ── Test 4: off main, staged changes -> refuse (exit 1), stay put ─────────────
echo "Test 4: off main + staged changes"
R="$(make_guard_repo)"; echo work > "$R/feature.txt"; git -C "$R" add feature.txt
OUT="$(run_guard "$R" 1)"; RC="$(read_rc)"
assert_eq "1" "$RC" "test_guard_off_main_staged: exits 1 (refuse)"
assert_eq "handoff" "$(branch_of "$R")" "test_guard_off_main_staged: stays on handoff (no auto-restore)"
assert_contains "$OUT" "staged" "test_guard_off_main_staged: logs 'staged'"
echo ""

# ── Test 5: off main, untracked only -> stash + checkout main ─────────────────
echo "Test 5: off main + untracked-only"
R="$(make_guard_repo)"; echo regen > "$R/cache.json"   # untracked, regenerable
OUT="$(run_guard "$R" 1)"; RC="$(read_rc)"
assert_eq "0" "$RC" "test_guard_off_main_only_untracked: exits 0"
assert_eq "main" "$(branch_of "$R")" "test_guard_off_main_only_untracked: returned to main"
[[ "$(git -C "$R" stash list | wc -l | tr -d ' ')" -ge 1 ]] && pass "test_guard_off_main_only_untracked: stash created" || fail "test_guard_off_main_only_untracked: stash created" "no stash"
echo ""

# ── Test 6: off main, live git op -> skip ─────────────────────────────────────
echo "Test 6: off main + live git op"
R="$(make_guard_repo)"
OUT="$(run_guard "$R" 0)"; RC="$(read_rc)"   # pgrep code 0 = git live
assert_eq "0" "$RC" "test_guard_off_main_live_git: exits 0"
assert_eq "handoff" "$(branch_of "$R")" "test_guard_off_main_live_git: stays put (active op)"
assert_contains "$OUT" "active git" "test_guard_off_main_live_git: logs 'active git'"
echo ""

# Repo left mid-merge with an unresolved conflict (MERGE_HEAD present, conflict
# file UNSTAGED), checked out on feature branch `feat`.
make_merge_conflict_repo() {
  local r="$TEST_DIR/repo-$$-$RANDOM"
  mkdir -p "$r"; git -C "$r" init -q
  git -C "$r" config user.email t@t; git -C "$r" config user.name t
  echo base > "$r/c.txt"; git -C "$r" add c.txt; git -C "$r" commit -qm init
  git -C "$r" branch -M main
  git -C "$r" checkout -q -b feat
  echo feat > "$r/c.txt"; git -C "$r" add c.txt; git -C "$r" commit -qm feat
  git -C "$r" checkout -q main
  echo main > "$r/c.txt"; git -C "$r" add c.txt; git -C "$r" commit -qm main
  git -C "$r" checkout -q feat
  git -C "$r" merge main >/dev/null 2>&1 || true   # conflict -> MERGE_HEAD, c.txt unmerged
  echo "$r"
}

# ── Test 7: mid-merge conflict -> REFUSE (do not stash away the resolution) ────
echo "Test 7: off main + merge in progress (MERGE_HEAD)"
R="$(make_merge_conflict_repo)"
[[ -f "$R/.git/MERGE_HEAD" ]] && pass "test_guard_merge_in_progress: precondition MERGE_HEAD present" || fail "test_guard_merge_in_progress: precondition MERGE_HEAD present"
OUT="$(run_guard "$R" 1)"; RC="$(read_rc)"
assert_eq "1" "$RC" "test_guard_merge_in_progress: exits 1 (refuse)"
assert_eq "feat" "$(branch_of "$R")" "test_guard_merge_in_progress: stays on feat (work preserved)"
[[ -f "$R/.git/MERGE_HEAD" ]] && pass "test_guard_merge_in_progress: MERGE_HEAD not abandoned" || fail "test_guard_merge_in_progress: MERGE_HEAD not abandoned" "in-flight merge destroyed"
[[ "$(git -C "$R" stash list | wc -l | tr -d ' ')" -eq 0 ]] && pass "test_guard_merge_in_progress: no stash created" || fail "test_guard_merge_in_progress: no stash created" "resolution stashed away"
echo ""

# ── Test 8: detached HEAD (mid-rebase shape) -> REFUSE ────────────────────────
echo "Test 8: detached HEAD"
R="$(make_guard_repo)"; git -C "$R" checkout -q --detach
OUT="$(run_guard "$R" 1)"; RC="$(read_rc)"
assert_eq "1" "$RC" "test_guard_detached_head: exits 1 (refuse)"
[[ -z "$(branch_of "$R")" ]] && pass "test_guard_detached_head: stays detached (not yanked to main)" || fail "test_guard_detached_head: stays detached" "switched to $(branch_of "$R")"
assert_contains "$OUT" "in-flight" "test_guard_detached_head: logs in-flight refusal"
echo ""

# ── Test 9: untracked GATE EVIDENCE is not "regenerable churn" (#3826) ────────
# The guard's decision tree equated untracked with regenerable and stashed it via
# `git stash -u` on a 30-minute cron. That destroyed .planning/plan-approved/3787.md
# twice. An approval marker records a user-in-loop decision: it is not derivable
# from the repo and no agent may re-issue one, so losing it silently un-approves
# approved work. The guard must take its existing staged-changes branch instead --
# refuse, alert, leave the tree alone.
echo "Test 9: untracked approval-gate marker is protected"
R="$(make_guard_repo)"
mkdir -p "$R/.planning/plan-approved"
printf '# Plan approval — #4242
Approved by: owner, in session chat.
' > "$R/.planning/plan-approved/4242.md"
OUT="$(run_guard "$R" 1)"; RC="$(read_rc)"
assert_eq "1" "$RC" "test_guard_gate_marker: exits 1 (refuse)"
assert_eq "handoff" "$(branch_of "$R")" "test_guard_gate_marker: stays on handoff"
[[ -f "$R/.planning/plan-approved/4242.md" ]] \
  && pass "test_guard_gate_marker: marker SURVIVES on disk" \
  || fail "test_guard_gate_marker: marker SURVIVES on disk" "the guard removed it"
assert_eq "0" "$(git -C "$R" stash list | wc -l | tr -d ' ')" "test_guard_gate_marker: nothing stashed"
echo ""

# ── Test 10: authored plans and scripts are protected too ─────────────────────
# An approval whose plan has been deleted approves nothing, and a script is never
# build output. Both were among the six files stranded on one disk on 2026-09-03.
echo "Test 10: untracked plans and scripts are protected"
for path in "docs/plans/2026-01-01-a-plan.md" "docs/session-handoffs/2026-01-01-exit.md" "scripts/fleet/some-tool.sh"; do
  R="$(make_guard_repo)"
  mkdir -p "$R/$(dirname "$path")"; echo "content" > "$R/$path"
  OUT="$(run_guard "$R" 1)"; RC="$(read_rc)"
  assert_eq "1" "$RC" "test_guard_protects[$path]: exits 1"
  [[ -f "$R/$path" ]] && pass "test_guard_protects[$path]: survives" \
                      || fail "test_guard_protects[$path]: survives" "removed"
done
echo ""

# ── Test 11: genuinely regenerable churn STILL gets stashed ───────────────────
# The fix is only an improvement if it does not disable the guard. A denylist that
# swallows everything would strand sessions off main, which is what #3187 fixed.
echo "Test 11: regenerable untracked churn still stashes and returns"
R="$(make_guard_repo)"
mkdir -p "$R/docs/reports"; echo "<html>" > "$R/docs/reports/dashboard.html"
echo "log line" > "$R/build.log"
OUT="$(run_guard "$R" 1)"; RC="$(read_rc)"
assert_eq "0" "$RC" "test_guard_churn_still_stashes: exits 0"
assert_eq "main" "$(branch_of "$R")" "test_guard_churn_still_stashes: returned to main"
assert_eq "1" "$(git -C "$R" stash list | wc -l | tr -d ' ')" "test_guard_churn_still_stashes: churn was stashed"
echo ""

# ── Test 12: a protected path beside churn still refuses ──────────────────────
# The dangerous shape: one marker hidden among 200 regenerable files. The decision
# must be driven by the presence of ANY protected path, not by the majority.
echo "Test 12: one protected file among churn still refuses"
R="$(make_guard_repo)"
mkdir -p "$R/docs/reports" "$R/.planning/plan-approved"
for i in 1 2 3 4 5; do echo "x" > "$R/docs/reports/gen-$i.html"; done
echo "marker" > "$R/.planning/plan-approved/9999.md"
OUT="$(run_guard "$R" 1)"; RC="$(read_rc)"
assert_eq "1" "$RC" "test_guard_mixed: exits 1 despite mostly-churn"
[[ -f "$R/.planning/plan-approved/9999.md" ]] \
  && pass "test_guard_mixed: marker survives" || fail "test_guard_mixed: marker survives" "removed"
echo ""

echo "============================================"
echo "Results: $TESTS_PASSED/$TESTS_RUN passed, $TESTS_FAILED failed"
echo "============================================"
[[ "$TESTS_FAILED" -gt 0 ]] && exit 1 || exit 0
