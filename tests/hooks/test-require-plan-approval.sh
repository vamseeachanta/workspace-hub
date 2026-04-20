#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
SCRIPT="$REPO_ROOT/scripts/enforcement/require-plan-approval.sh"

PASS=0
FAIL=0
pass() { echo "PASS: $1"; PASS=$((PASS + 1)); }
fail() { echo "FAIL: $1"; FAIL=$((FAIL + 1)); }

TMPDIR_TEST="$(mktemp -d)"
trap 'rm -rf "$TMPDIR_TEST"' EXIT

make_repo() {
  local repo="$1"
  mkdir -p "$repo"
  git init -q "$repo"
  git -C "$repo" config user.email test@example.com
  git -C "$repo" config user.name test
  mkdir -p "$repo/.planning/plan-approved"
  printf 'state\n' > "$repo/.planning/STATE.md"
  touch -d '2026-04-20 02:26:00 UTC' "$repo/.planning/STATE.md"
  for i in $(seq 1 5000); do
    printf '# approved %s\n' "$i" > "$repo/.planning/plan-approved/$i.md"
    touch -d '2026-04-20 09:53:00 UTC' "$repo/.planning/plan-approved/$i.md"
  done
  mkdir -p "$repo/src"
  printf 'print("x")\n' > "$repo/src/demo.py"
  git -C "$repo" add src/demo.py .planning/STATE.md .planning/plan-approved/
}

T1_ROOT="$TMPDIR_TEST/t1"
make_repo "$T1_ROOT"

EXIT_CODE=0
(
  cd "$T1_ROOT"
  bash "$SCRIPT" --strict
) || EXIT_CODE=$?

if [[ $EXIT_CODE -eq 0 ]]; then
  pass "plan approval marker newer than STATE allows implementation commit"
else
  fail "expected exit 0 with valid approval marker, got $EXIT_CODE"
fi

echo ""
echo "Results: $PASS passed, $FAIL failed"
if [[ $FAIL -gt 0 ]]; then
  exit 1
fi
exit 0
