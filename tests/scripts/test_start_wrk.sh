#!/usr/bin/env bash
# test_start_wrk.sh — Tests for scripts/work-queue/start-wrk.sh (WRK-1141)
# Tests: simple→main, medium→branch, complex→branch,
#        compound=true→branch, branch-already-exists
set -euo pipefail

REPO_ROOT="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)"
SCRIPT="${REPO_ROOT}/scripts/work-queue/start-wrk.sh"
TMPDIR_BASE="$(mktemp -d)"
PASS_COUNT=0
FAIL_COUNT=0

cleanup() { rm -rf "${TMPDIR_BASE}"; }
trap cleanup EXIT

run_test() {
  local name="$1" ok="$2" msg="${3:-}"
  if [[ "${ok}" == "1" ]]; then
    echo "  PASS  ${name}"
    PASS_COUNT=$((PASS_COUNT + 1))
  else
    echo "  FAIL  ${name}${msg:+: ${msg}}"
    FAIL_COUNT=$((FAIL_COUNT + 1))
  fi
}

# Create a temp git repo for routing tests (avoids touching real repo)
setup_test_repo() {
  local dir="$1"
  mkdir -p "${dir}/.claude/work-queue/working"
  git -C "${dir}" init -q
  git -C "${dir}" config user.email "test@test.com"
  git -C "${dir}" config user.name "Test"
  touch "${dir}/README.md"
  git -C "${dir}" add .
  git -C "${dir}" commit -q -m "init"
}

write_wrk() {
  local dir="$1" complexity="$2" compound="$3"
  cat > "${dir}/.claude/work-queue/working/WRK-9999.md" <<EOF
---
id: WRK-9999
title: "test item for routing"
status: working
complexity: ${complexity}
compound: ${compound}
---
EOF
}

# ── Test 1: simple → commit to main, no branch created ───────────────────────
T1="${TMPDIR_BASE}/repo1"
setup_test_repo "${T1}"
write_wrk "${T1}" "simple" "false"
output="$(GIT_DIR="${T1}/.git" git -C "${T1}" \
  bash "${SCRIPT//$REPO_ROOT/.}" WRK-9999 2>&1 || \
  bash -c "cd '${T1}' && bash '${SCRIPT}' WRK-9999" 2>&1 || true)"
# Re-run from within the temp repo
output="$(cd "${T1}" && REPO_OVERRIDE="${T1}" bash "${SCRIPT}" WRK-9999 2>&1 || true)"
run_test "simple-commits-to-main" \
  "$(echo "${output}" | grep -q "main" && echo 1 || echo 0)" "${output}"

# ── Test 2: medium → feature branch created ───────────────────────────────────
T2="${TMPDIR_BASE}/repo2"
setup_test_repo "${T2}"
write_wrk "${T2}" "medium" "false"
output="$(cd "${T2}" && bash "${SCRIPT}" WRK-9999 2>&1 || true)"
branch_exists="$(git -C "${T2}" branch --list "feature/WRK-9999-*" | wc -l | tr -d ' ')"
run_test "medium-creates-branch" \
  "$([ "${branch_exists}" -ge 1 ] && echo 1 || echo 0)" \
  "branches: $(git -C "${T2}" branch --list)"

# ── Test 3: complex → feature branch created ─────────────────────────────────
T3="${TMPDIR_BASE}/repo3"
setup_test_repo "${T3}"
write_wrk "${T3}" "complex" "false"
output="$(cd "${T3}" && bash "${SCRIPT}" WRK-9999 2>&1 || true)"
branch_exists="$(git -C "${T3}" branch --list "feature/WRK-9999-*" | wc -l | tr -d ' ')"
run_test "complex-creates-branch" \
  "$([ "${branch_exists}" -ge 1 ] && echo 1 || echo 0)" \
  "branches: $(git -C "${T3}" branch --list)"

# ── Test 4: compound=true → branch regardless of simple complexity ────────────
T4="${TMPDIR_BASE}/repo4"
setup_test_repo "${T4}"
write_wrk "${T4}" "simple" "true"
output="$(cd "${T4}" && bash "${SCRIPT}" WRK-9999 2>&1 || true)"
branch_exists="$(git -C "${T4}" branch --list "feature/WRK-9999-*" | wc -l | tr -d ' ')"
run_test "compound-true-creates-branch-even-for-simple" \
  "$([ "${branch_exists}" -ge 1 ] && echo 1 || echo 0)" \
  "output: ${output}"

# ── Test 5: branch-already-exists → warn, exit 0 ─────────────────────────────
T5="${TMPDIR_BASE}/repo5"
setup_test_repo "${T5}"
write_wrk "${T5}" "medium" "false"
# Create the branch first
first_output="$(cd "${T5}" && bash "${SCRIPT}" WRK-9999 2>&1 || true)"
# Now try to create it again
second_output="$(cd "${T5}" && bash "${SCRIPT}" WRK-9999 2>&1 || true)"
exit_code=0
cd "${T5}" && bash "${SCRIPT}" WRK-9999 >/dev/null 2>&1 || exit_code=$?
run_test "branch-already-exists-exits-0" \
  "$([ "${exit_code}" -eq 0 ] && echo 1 || echo 0)" \
  "exit code: ${exit_code}, output: ${second_output}"

# ── Summary ───────────────────────────────────────────────────────────────────
echo ""
echo "Results: ${PASS_COUNT} PASS, ${FAIL_COUNT} FAIL"
[[ "${FAIL_COUNT}" -eq 0 ]]
