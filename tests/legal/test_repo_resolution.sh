#!/usr/bin/env bash
# =============================================================================
# Resolution-contract tests for scripts/legal/legal-sanity-scan.sh
# (llm-wiki-acma#299 — sibling/env/walk-up repo resolution; --all refuses
# empty enumeration).
#
# Builds a temp sandbox with fake WORKSPACE_ROOT + nested/sibling layouts and
# drives the scanner through the LEGAL_SCAN_RESOLVE_ONLY=1 dry-run hook, which
# prints the resolved path(s) and exits before any scanning happens.
#
# Run under bash (git-bash on Windows): bash tests/legal/test_repo_resolution.sh
# Exit 0 = all assertions passed.
# =============================================================================
set -u

TEST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$TEST_DIR/../.." && pwd)"
SCANNER_SRC="$REPO_ROOT/scripts/legal/legal-sanity-scan.sh"

if [[ ! -f "$SCANNER_SRC" ]]; then
  echo "FATAL: scanner not found at $SCANNER_SRC" >&2
  exit 1
fi

SANDBOX="$(mktemp -d)"
trap 'rm -rf "$SANDBOX"' EXIT

PASS=0
FAIL=0

pass() { PASS=$((PASS + 1)); echo "  PASS: $1"; }
fail() { FAIL=$((FAIL + 1)); echo "  FAIL: $1"; }

# The scanner derives WORKSPACE_ROOT from its own location (scripts/legal/../..)
# so we install a copy inside a fake workspace root two levels deep.
# Layout:
#   $SANDBOX/grand/parent/fakews/scripts/legal/legal-sanity-scan.sh
#   $SANDBOX/grand/parent/fakews/<nested repos>
#   $SANDBOX/grand/parent/<sibling repos>
#   $SANDBOX/grand/<walk-up repo>
#   $SANDBOX/envroots/{rootA,rootB}/<env repos>
FAKEWS="$SANDBOX/grand/parent/fakews"
mkdir -p "$FAKEWS/scripts/legal"
cp "$SCANNER_SRC" "$FAKEWS/scripts/legal/legal-sanity-scan.sh"
SCANNER="$FAKEWS/scripts/legal/legal-sanity-scan.sh"

run_scanner() {
  # run_scanner [args...] — stdout to $OUT, stderr to $ERR, exit code to $RC
  OUT="$(bash "$SCANNER" "$@" 2>"$SANDBOX/stderr.txt")"
  RC=$?
  ERR="$(cat "$SANDBOX/stderr.txt")"
}

echo "=== legal-sanity-scan repo-resolution contract ==="

# ---------------------------------------------------------------------------
# 1. nested-wins: repo exists both nested and as sibling -> nested resolves
# ---------------------------------------------------------------------------
mkdir -p "$FAKEWS/dualrepo" "$SANDBOX/grand/parent/dualrepo"
LEGAL_SCAN_RESOLVE_ONLY=1 run_scanner --repo=dualrepo --quiet
expected="$(cd "$FAKEWS/dualrepo" && pwd)"
if [[ $RC -eq 0 && "$OUT" == "$expected" ]]; then
  pass "nested-wins (resolved $OUT)"
else
  fail "nested-wins (rc=$RC out='$OUT' expected='$expected')"
fi

# ---------------------------------------------------------------------------
# 2. sibling-fallback: repo exists only beside the workspace root
# ---------------------------------------------------------------------------
mkdir -p "$SANDBOX/grand/parent/sibonly"
LEGAL_SCAN_RESOLVE_ONLY=1 run_scanner --repo=sibonly --quiet
expected="$(cd "$SANDBOX/grand/parent/sibonly" && pwd)"
if [[ $RC -eq 0 && "$OUT" == "$expected" ]]; then
  pass "sibling-fallback (resolved $OUT)"
else
  fail "sibling-fallback (rc=$RC out='$OUT' expected='$expected')"
fi

# ---------------------------------------------------------------------------
# 3. walk-up: repo exists only two levels above the workspace root
# ---------------------------------------------------------------------------
mkdir -p "$SANDBOX/grand/walkrepo"
LEGAL_SCAN_RESOLVE_ONLY=1 run_scanner --repo=walkrepo --quiet
expected="$(cd "$SANDBOX/grand/walkrepo" && pwd)"
if [[ $RC -eq 0 && "$OUT" == "$expected" ]]; then
  pass "walk-up (resolved $OUT)"
else
  fail "walk-up (rc=$RC out='$OUT' expected='$expected')"
fi

# ---------------------------------------------------------------------------
# 4. env-override-wins: repo exists nested AND under an env root -> env wins
# ---------------------------------------------------------------------------
mkdir -p "$FAKEWS/envrepo" "$SANDBOX/envroots/rootA/envrepo"
LEGAL_SCAN_RESOLVE_ONLY=1 LEGAL_SCAN_REPO_ROOTS="$SANDBOX/envroots/rootA" \
  run_scanner --repo=envrepo --quiet
expected="$(cd "$SANDBOX/envroots/rootA/envrepo" && pwd)"
if [[ $RC -eq 0 && "$OUT" == "$expected" ]]; then
  pass "env-override-wins (resolved $OUT)"
else
  fail "env-override-wins (rc=$RC out='$OUT' expected='$expected')"
fi

# ---------------------------------------------------------------------------
# 5. env semicolon list: repo only under the second of two roots
# ---------------------------------------------------------------------------
mkdir -p "$SANDBOX/envroots/rootB/semirepo"
LEGAL_SCAN_RESOLVE_ONLY=1 \
  LEGAL_SCAN_REPO_ROOTS="$SANDBOX/envroots/rootA;$SANDBOX/envroots/rootB" \
  run_scanner --repo=semirepo --quiet
expected="$(cd "$SANDBOX/envroots/rootB/semirepo" && pwd)"
if [[ $RC -eq 0 && "$OUT" == "$expected" ]]; then
  pass "env semicolon-separated roots (resolved $OUT)"
else
  fail "env semicolon-separated roots (rc=$RC out='$OUT' expected='$expected')"
fi

# ---------------------------------------------------------------------------
# 6. env-set-but-missing: env set, repo exists nested but NOT under env roots
#    -> exit 2 (no fallthrough to defaults), candidates listed
# ---------------------------------------------------------------------------
mkdir -p "$FAKEWS/nestedonly"
LEGAL_SCAN_RESOLVE_ONLY=1 LEGAL_SCAN_REPO_ROOTS="$SANDBOX/envroots/rootA" \
  run_scanner --repo=nestedonly --quiet
if [[ $RC -eq 2 && "$ERR" == *"ERROR: Repository not found: nestedonly"* \
      && "$ERR" == *"$SANDBOX/envroots/rootA/nestedonly"* ]]; then
  pass "env-set-but-missing refuses with exit 2 + candidates"
else
  fail "env-set-but-missing (rc=$RC err='$ERR')"
fi

# ---------------------------------------------------------------------------
# 7. not-found: no env, repo nowhere -> exit 2, candidates listed
# ---------------------------------------------------------------------------
LEGAL_SCAN_RESOLVE_ONLY=1 run_scanner --repo=no-such-repo --quiet
if [[ $RC -eq 2 && "$ERR" == *"ERROR: Repository not found: no-such-repo"* \
      && "$ERR" == *"Candidates tried:"* ]]; then
  pass "not-found exit 2 + candidates listed"
else
  fail "not-found (rc=$RC err='$ERR')"
fi

# ---------------------------------------------------------------------------
# 8. --all with no submodules and no env -> exit 2 (never pass scanning nothing)
# ---------------------------------------------------------------------------
LEGAL_SCAN_RESOLVE_ONLY=1 run_scanner --all --quiet
if [[ $RC -eq 2 && "$ERR" == *"ERROR: --all found no repositories to scan"* ]]; then
  pass "--all empty enumeration refuses with exit 2"
else
  fail "--all empty enumeration (rc=$RC err='$ERR')"
fi

# ---------------------------------------------------------------------------
# 9. --all with env roots -> enumerates child dirs holding a .git entry
#    (rootA: gitrepo1 [.git dir], nogit [no .git]; rootB: gitrepo2 [.git file])
# ---------------------------------------------------------------------------
mkdir -p "$SANDBOX/envroots/rootA/gitrepo1/.git" \
         "$SANDBOX/envroots/rootA/nogit" \
         "$SANDBOX/envroots/rootB/gitrepo2"
echo "gitdir: elsewhere" > "$SANDBOX/envroots/rootB/gitrepo2/.git"
LEGAL_SCAN_RESOLVE_ONLY=1 \
  LEGAL_SCAN_REPO_ROOTS="$SANDBOX/envroots/rootA;$SANDBOX/envroots/rootB" \
  run_scanner --all --quiet
exp1="$(cd "$SANDBOX/envroots/rootA/gitrepo1" && pwd)"
exp2="$(cd "$SANDBOX/envroots/rootB/gitrepo2" && pwd)"
if [[ $RC -eq 0 && "$OUT" == *"$exp1"* && "$OUT" == *"$exp2"* \
      && "$OUT" != *"nogit"* ]]; then
  pass "--all with env roots enumerates .git children only"
else
  fail "--all with env roots (rc=$RC out='$OUT')"
fi

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo "=== $PASS passed, $FAIL failed ==="
[[ $FAIL -eq 0 ]] || exit 1
exit 0
