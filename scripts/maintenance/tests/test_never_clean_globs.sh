#!/usr/bin/env bash
# ABOUTME: Test suite for never-clean-globs.sh and repo-housekeeping.sh's clean path (#3826).
#
# The defect under test: `git clean -fd` ran with NO exclusions while the branch
# eleven lines below built -e excludes from SECRET_GLOBS, so git-ignored secrets
# were protected and untracked AUTHORED work was not. That destroyed
# .planning/plan-approved/3787.md twice.
#
# Two properties, and the second matters as much as the first:
#   1. authored, non-reconstructable work survives a sweep;
#   2. genuinely regenerable churn is STILL swept -- a denylist that swallowed
#      everything would break the housekeeping this script exists to do.
#
# SAFETY: every test runs in a throwaway `git init` repo under mktemp. The real
# checkout is never touched.

set -uo pipefail

TESTS_RUN=0; TESTS_PASSED=0; TESTS_FAILED=0
pass() { TESTS_PASSED=$((TESTS_PASSED+1)); TESTS_RUN=$((TESTS_RUN+1)); echo "  PASS: $1"; }
fail() { TESTS_FAILED=$((TESTS_FAILED+1)); TESTS_RUN=$((TESTS_RUN+1)); echo "  FAIL: $1"; [[ -n "${2:-}" ]] && echo "        $2"; }
assert_eq() { [[ "$1" == "$2" ]] && pass "$3" || fail "$3" "expected='$1' actual='$2'"; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIB="$SCRIPT_DIR/../never-clean-globs.sh"
HK="$SCRIPT_DIR/../repo-housekeeping.sh"
[[ -f "$LIB" ]] || { echo "ERROR: never-clean-globs.sh not found at $LIB" >&2; exit 1; }
# shellcheck source=/dev/null
. "$LIB"
echo "Testing: $LIB"; echo ""

TEST_DIR="$(mktemp -d)"
trap 'rm -rf "$TEST_DIR"' EXIT

make_repo() {
  local r="$TEST_DIR/repo-$$-$RANDOM"
  mkdir -p "$r"; git -C "$r" init -q
  git -C "$r" config user.email t@t; git -C "$r" config user.name t
  echo base > "$r/base.txt"; git -C "$r" add base.txt; git -C "$r" commit -qm init
  echo "$r"
}

# ── Test 1: classification ────────────────────────────────────────────────────
echo "Test 1: never_clean_match classifies authored vs generated"
for p in ".planning/plan-approved/3787.md" ".planning/research/a.md" "docs/plans/p.md" \
         "docs/session-handoffs/h.md" "scripts/fleet/tool.sh" ".claude/rules/r.md" \
         ".claude/skills/dev/s/SKILL.md"; do
  never_clean_match "$p" && pass "protected: $p" || fail "protected: $p" "classified sweepable"
done
for p in "docs/reports/dash.html" "build.log" "logs/quality/x.log" \
         "config/ai-tools/provider-kanban.json" ".claude/state/foo.json" "node_modules/x/y.js"; do
  never_clean_match "$p" && fail "sweepable: $p" "wrongly protected" || pass "sweepable: $p"
done
echo ""

# ── Test 2: never_clean_untracked finds protected untracked files ─────────────
echo "Test 2: never_clean_untracked detection"
R="$(make_repo)"; mkdir -p "$R/.planning/plan-approved"
echo marker > "$R/.planning/plan-approved/1.md"
OUT="$(never_clean_untracked "$R")"; RC=$?
assert_eq "0" "$RC" "returns 0 when protected work present"
assert_eq ".planning/plan-approved/1.md" "$OUT" "names the protected path"

R="$(make_repo)"; mkdir -p "$R/docs/reports"; echo x > "$R/docs/reports/d.html"
OUT="$(never_clean_untracked "$R")"; RC=$?
assert_eq "1" "$RC" "returns 1 when only churn present"
assert_eq "" "$OUT" "names nothing"
echo ""

# ── Test 3: a TRACKED protected file is not flagged ───────────────────────────
# The guard is about UNTRACKED work. A committed marker is already safe, and
# flagging it would block housekeeping forever on any repo that has one.
echo "Test 3: tracked protected files are not flagged"
R="$(make_repo)"; mkdir -p "$R/.planning/plan-approved"
echo marker > "$R/.planning/plan-approved/2.md"
git -C "$R" add -f .planning/plan-approved/2.md >/dev/null 2>&1
git -C "$R" commit -qm marker >/dev/null 2>&1
never_clean_untracked "$R" >/dev/null && fail "tracked marker not flagged" "flagged a committed file" \
                                      || pass "tracked marker not flagged"
echo ""

# ── Test 4: paths with spaces survive NUL iteration ───────────────────────────
# Word-splitting would fragment such a path into pieces that miss every glob and
# let the file through -- a silent hole in the protection.
echo "Test 4: a path containing spaces is still protected"
R="$(make_repo)"; mkdir -p "$R/docs/plans"
echo p > "$R/docs/plans/a plan with spaces.md"
OUT="$(never_clean_untracked "$R")"
assert_eq "docs/plans/a plan with spaces.md" "$OUT" "space-bearing path detected whole"
echo ""

# ── Test 5: repo-housekeeping PRESERVES untracked work by committing it ───────
# CORRECTION, recorded because #3826 as filed claimed otherwise. This script's
# `git clean -fd` was reported as a destroyer of untracked authored work. It is
# not, on the --apply path: step 1 (line ~182) runs `git add -A` + commit for ANY
# dirty tree, and `git status --porcelain` counts untracked files -- so by the
# time the clean at line ~297 runs, nothing untracked remains. The marker is
# committed to a housekeeping branch, not deleted.
#
# The denylist wired into the clean path is therefore DEFENCE IN DEPTH, not a
# live-bug fix: it matters only if the commit step is ever skipped, reordered, or
# made conditional. The live destroyer is return-to-main-guard.sh's `git stash -u`,
# covered by tests 9-12 of test_return_to_main_guard.sh.
echo "Test 5: repo-housekeeping preserves an untracked marker by committing it"
R="$(make_repo)"; mkdir -p "$R/.planning/plan-approved"
echo marker > "$R/.planning/plan-approved/3787.md"
OUT="$( bash "$HK" --apply --root "$(dirname "$R")" --repos "$(basename "$R")" 2>&1 )"
echo "$OUT" | grep -q "No git repos found" \
  && fail "housekeeping: the sweep actually ran" "sweep found no repos — test would pass vacuously" \
  || pass "housekeeping: the sweep actually ran"
[[ -f "$R/.planning/plan-approved/3787.md" ]] \
  && pass "housekeeping: marker survives --apply" \
  || fail "housekeeping: marker survives --apply" "the sweep removed it"
[[ -n "$(git -C "$R" ls-files .planning/plan-approved/3787.md)" ]] \
  && pass "housekeeping: marker survives by being COMMITTED (not merely skipped)" \
  || fail "housekeeping: marker is tracked afterwards" "survived untracked — the mechanism is not what this test documents"
echo ""

# ── Test 6: the denylist does not change housekeeping's behaviour ─────────────
# A denylist that made the sweep refuse wholesale would break the housekeeping
# this script exists to do. Regenerable churn must still be handled exactly as
# before -- which, per test 5, means committed rather than deleted.
echo "Test 6: regenerable churn is still handled, not refused"
R="$(make_repo)"; mkdir -p "$R/docs/reports"
echo junk > "$R/docs/reports/generated.html"
OUT="$( bash "$HK" --apply --root "$(dirname "$R")" --repos "$(basename "$R")" 2>&1 )"
echo "$OUT" | grep -q "REFUSING to clean" \
  && fail "housekeeping: churn does not trigger a refusal" "denylist too broad — it refused on pure churn" \
  || pass "housekeeping: churn does not trigger a refusal"
[[ -n "$(git -C "$R" ls-files docs/reports/generated.html)" ]] \
  && pass "housekeeping: churn still processed" \
  || fail "housekeeping: churn still processed" "the sweep did nothing with it"
echo ""

# ── Test 7: an IGNORED protected file survives --prune-ignored (#3826 r1 MAJOR) ─
# The hole the first fix missed, and the nastiest of the three. `git add -A` does
# not stage ignored files, so step 1's commit-WIP never protects them; and
# `--exclude-standard` hid them from the untracked detector, so the denylist
# could not see them either. `git clean -fdx` then deleted them outright, with
# only SECRET_GLOBS excluded. Reproduced by review before this test existed.
echo "Test 7: ignored protected file survives --prune-ignored"
R="$(make_repo)"
printf '.planning/\n' > "$R/.gitignore"
git -C "$R" add .gitignore >/dev/null 2>&1; git -C "$R" commit -qm ignore >/dev/null 2>&1
mkdir -p "$R/.planning/plan-approved"
echo marker > "$R/.planning/plan-approved/123.md"
# Precondition: git must genuinely consider it ignored, or the test proves nothing.
[[ -n "$(git -C "$R" ls-files --others --ignored --exclude-standard)" ]] \
  && pass "ignored-marker precondition: git treats it as ignored" \
  || fail "ignored-marker precondition: git treats it as ignored" "not ignored — test would be vacuous"
OUT="$( bash "$HK" --apply --prune-ignored --root "$(dirname "$R")" --repos "$(basename "$R")" 2>&1 )"
[[ -f "$R/.planning/plan-approved/123.md" ]] \
  && pass "housekeeping --prune-ignored: ignored marker SURVIVES" \
  || fail "housekeeping --prune-ignored: ignored marker SURVIVES" "deleted by git clean -fdx"
echo ""

# ── Test 8: ignored regenerable churn is STILL pruned ─────────────────────────
# The refusal must be driven by protected paths, not by the presence of any
# ignored file at all -- otherwise --prune-ignored becomes a permanent no-op.
echo "Test 8: ignored churn is still pruned"
R="$(make_repo)"
printf 'build/\n' > "$R/.gitignore"
git -C "$R" add .gitignore >/dev/null 2>&1; git -C "$R" commit -qm ignore >/dev/null 2>&1
mkdir -p "$R/build"; echo junk > "$R/build/out.o"
OUT="$( bash "$HK" --apply --prune-ignored --root "$(dirname "$R")" --repos "$(basename "$R")" 2>&1 )"
echo "$OUT" | grep -q "REFUSING to prune ignored" \
  && fail "housekeeping: pure ignored churn is not refused" "denylist too broad on the -fdx path" \
  || pass "housekeeping: pure ignored churn is not refused"
[[ -f "$R/build/out.o" ]] \
  && fail "housekeeping: ignored churn pruned" "build/out.o survived — --prune-ignored is now inert" \
  || pass "housekeeping: ignored churn pruned"
echo ""

# ── Test 9: generated scratch under scripts/ stays sweepable ──────────────────
# `scripts/*` was narrowed to source extensions at review. A blanket glob would
# refuse forever on any repo that generates json/log under scripts/, re-creating
# the stranded-off-main problem #3187 fixed.
echo "Test 9: scripts/ glob is extension-scoped, not blanket"
never_clean_match "scripts/fleet/lane-sweep.sh" && pass "scripts/*.sh protected" || fail "scripts/*.sh protected" "not matched"
never_clean_match "scripts/tools/gen.py"        && pass "scripts/*.py protected" || fail "scripts/*.py protected" "not matched"
for p in "scripts/out/report.json" "scripts/cache/run.log" "scripts/data/rows.csv"; do
  never_clean_match "$p" && fail "generated under scripts/ stays sweepable: $p" "wrongly protected" \
                        || pass "generated under scripts/ stays sweepable: $p"
done
echo ""

echo "============================================"
echo "Results: $TESTS_PASSED/$TESTS_RUN passed, $TESTS_FAILED failed"
echo "============================================"
[[ "$TESTS_FAILED" -gt 0 ]] && exit 1 || exit 0
