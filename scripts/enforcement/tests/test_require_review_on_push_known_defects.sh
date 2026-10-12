#!/usr/bin/env bash
# Regression tests for the fixed defects recorded in
# docs/enforcement/review-gate-defects.md.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_UNDER_TEST="${SCRIPT_DIR}/../require-review-on-push.sh"
TMP_ROOT="$(mktemp -d)"

trap 'rm -rf "$TMP_ROOT"' EXIT

PASS_COUNT=0
FAIL_COUNT=0

identity() {
  local user domain
  user="example"
  domain="example.invalid"
  git config user.name "Example User"
  git config user.email "${user}@${domain}"
}

pass() {
  PASS_COUNT=$((PASS_COUNT + 1))
  echo "PASS: $1"
}

fail() {
  FAIL_COUNT=$((FAIL_COUNT + 1))
  echo "FAIL: $1"
  [[ -n "${2:-}" ]] && echo "      $2"
}

init_pair() {
  local name="$1"
  mkdir -p "${TMP_ROOT}/${name}"
  git init --bare -q "${TMP_ROOT}/${name}/origin.git"
  git init -q "${TMP_ROOT}/${name}/repo"
  cd "${TMP_ROOT}/${name}/repo"
  identity
  git remote add origin "${TMP_ROOT}/${name}/origin.git"
  printf 'init\n' > README.md
  git add README.md
  git commit -q -m "chore: initial"
  git branch -M main
  git push -q -u origin main
}

init_single() {
  local name="$1"
  mkdir -p "${TMP_ROOT}/${name}/repo"
  git init -q "${TMP_ROOT}/${name}/repo"
  cd "${TMP_ROOT}/${name}/repo"
  identity
  printf 'init\n' > README.md
  git add README.md
  git commit -q -m "chore: initial"
}

add_commit() {
  local msg="$1"
  local path="$2"
  mkdir -p "$(dirname "$path")"
  printf '%s\n' "$msg" > "$path"
  git add "$path"
  git commit -q -m "$msg"
}

run_gate() {
  local local_oid="$1"
  local remote_oid="${2:-}"
  local output rc=0
  output="$(bash "$SCRIPT_UNDER_TEST" "$local_oid" "$remote_oid" 2>&1)" || rc=$?
  printf '%s\n' "$output"
  return "$rc"
}

assert_rc_contains() {
  local name="$1"
  local expected_rc="$2"
  local needle="$3"
  local output="$4"
  local actual_rc="$5"
  if [[ "$actual_rc" -eq "$expected_rc" ]] && grep -q "$needle" <<< "$output"; then
    pass "$name"
  else
    fail "$name" "Expected rc=${expected_rc} and '${needle}'. Actual rc=${actual_rc}. Output: ${output}"
  fi
}

case_d1_merge() {
  init_pair d1_merge
  git checkout -q -b topic
  add_commit "docs: topic notes" "docs/topic.md"
  git push -q -u origin topic
  local remote_tip output rc=0
  remote_tip="$(git rev-parse HEAD)"
  git checkout -q main
  add_commit "feat: main code" "src/main.py"
  git push -q origin main
  git checkout -q topic
  git merge --no-edit origin/main >/dev/null
  output="$(REVIEW_GATE_EVIDENCE_MODE=strict run_gate "$(git rev-parse HEAD)" "$remote_tip")" || rc=$?
  assert_rc_contains "D1 merge excludes mainline commit" 0 "PASS" "$output" "$rc"
}

case_d1_fast_forward() {
  init_pair d1_fast_forward
  git checkout -q -b topic
  git push -q -u origin topic
  local remote_tip output rc=0
  remote_tip="$(git rev-parse HEAD)"
  git checkout -q main
  add_commit "feat: main code" "src/main.py"
  git push -q origin main
  git checkout -q topic
  git merge --ff-only origin/main >/dev/null
  output="$(REVIEW_GATE_EVIDENCE_MODE=strict run_gate "$(git rev-parse HEAD)" "$remote_tip")" || rc=$?
  assert_rc_contains "D1 fast-forward excludes mainline commit" 0 "PASS" "$output" "$rc"
}

case_d1_new_branch() {
  init_pair d1_new_branch
  git checkout -q -b topic
  git checkout -q main
  add_commit "feat: main code" "src/main.py"
  git push -q origin main
  git checkout -q topic
  git merge --ff-only origin/main >/dev/null
  local output rc=0
  output="$(REVIEW_GATE_EVIDENCE_MODE=strict run_gate "$(git rev-parse HEAD)" "0000000000000000000000000000000000000000")" || rc=$?
  assert_rc_contains "D1 new branch excludes mainline commit" 0 "PASS" "$output" "$rc"
}

case_d2_fresh_checkout() {
  init_single d2_fresh_checkout
  mkdir -p scripts/review/results src
  printf 'old evidence\n' > scripts/review/results/old.txt
  touch -d '2020-01-01 00:00:00' scripts/review/results/old.txt
  git add scripts/review/results/old.txt
  GIT_AUTHOR_DATE='2020-01-01T00:00:00Z' \
    GIT_COMMITTER_DATE='2020-01-01T00:00:00Z' \
    git commit -q -m "chore: old evidence fixture"
  local base head output rc=0
  base="$(git rev-parse HEAD)"
  add_commit "feat: unevidenced code" "src/feature.py"
  head="$(git rev-parse HEAD)"
  git clone -q . "${TMP_ROOT}/d2_fresh_checkout/clone"
  cd "${TMP_ROOT}/d2_fresh_checkout/clone"
  identity
  git update-ref refs/remotes/origin/main "$base"
  git symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/main
  output="$(REVIEW_GATE_EVIDENCE_MODE=strict run_gate "$head" "$base")" || rc=$?
  assert_rc_contains "D2 fresh checkout blocks in strict mode" 1 "Unreviewed: 1" "$output" "$rc"
  rc=0
  output="$(REVIEW_GATE_EVIDENCE_MODE=warn run_gate "$head" "$base")" || rc=$?
  assert_rc_contains "D2 fresh checkout warns in migration mode" 0 "WOULD-REJECT" "$output" "$rc"
}

case_d2_one_for_all() {
  init_pair d2_one_for_all
  local base head output rc=0
  base="$(git rev-parse HEAD)"
  add_commit "feat: code 1" "src/f1.py"
  add_commit "feat: code 2" "src/f2.py"
  add_commit "feat: code 3" "src/f3.py"
  head="$(git rev-parse HEAD)"
  mkdir -p scripts/review/results
  printf 'generic evidence\n' > scripts/review/results/generic.txt
  output="$(REVIEW_GATE_EVIDENCE_MODE=strict run_gate "$head" "$base")" || rc=$?
  assert_rc_contains "D2 generic evidence blocks in strict mode" 1 "Unreviewed: 3" "$output" "$rc"
  rc=0
  output="$(REVIEW_GATE_EVIDENCE_MODE=warn run_gate "$head" "$base")" || rc=$?
  assert_rc_contains "D2 generic evidence warns in migration mode" 0 "WOULD-REJECT" "$output" "$rc"
}

case_d2_keyword() {
  init_pair d2_keyword
  add_commit "chore: review notes" "notes.txt"
  local base head output rc=0
  base="$(git rev-parse HEAD)"
  add_commit "feat: keyword code" "src/keyword.py"
  head="$(git rev-parse HEAD)"
  output="$(REVIEW_GATE_EVIDENCE_MODE=strict run_gate "$head" "$base")" || rc=$?
  assert_rc_contains "D2 unrelated keyword blocks in strict mode" 1 "Unreviewed: 1" "$output" "$rc"
  rc=0
  output="$(REVIEW_GATE_EVIDENCE_MODE=warn run_gate "$head" "$base")" || rc=$?
  assert_rc_contains "D2 unrelated keyword warns in migration mode" 0 "DEPRECATED" "$output" "$rc"
}

main() {
  [[ -f "$SCRIPT_UNDER_TEST" ]] || { echo "ERROR: script under test not found" >&2; exit 1; }
  case_d1_merge
  case_d1_fast_forward
  case_d1_new_branch
  case_d2_fresh_checkout
  case_d2_one_for_all
  case_d2_keyword
  echo "Results: ${PASS_COUNT} PASS, ${FAIL_COUNT} FAIL"
  [[ "$FAIL_COUNT" -eq 0 ]]
}

main "$@"
