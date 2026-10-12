#!/usr/bin/env bash
# Documents known defects recorded in docs/enforcement/review-gate-defects.md.
# This script is not a gate. It exits 0 while every case remains XFAIL, and exits
# 1 on XPASS so the fixer can move the case into the main test and delete it here.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_UNDER_TEST="${SCRIPT_DIR}/../require-review-on-push.sh"
TMP_ROOT="$(mktemp -d)"

trap 'rm -rf "$TMP_ROOT"' EXIT

XFAIL_COUNT=0
XPASS_COUNT=0

identity() {
  local mail_user mail_domain
  mail_user="example"
  mail_domain="example.invalid"
  git config user.name "Example User"
  git config user.email "${mail_user}@${mail_domain}"
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

run_gate() {
  local local_oid="$1"
  local remote_oid="${2:-}"
  local output rc=0
  unset SKIP_REVIEW_GATE REVIEW_GATE_STRICT
  output="$(bash "$SCRIPT_UNDER_TEST" "$local_oid" "$remote_oid" 2>&1)" || rc=$?
  printf '%s\n' "$output"
  return "$rc"
}

record() {
  local name="$1"
  local result="$2"
  if [[ "$result" == "xfail" ]]; then
    XFAIL_COUNT=$((XFAIL_COUNT + 1))
    echo "XFAIL: ${name}"
  else
    XPASS_COUNT=$((XPASS_COUNT + 1))
    echo "XPASS: ${name} - move this case into the main test and delete it here"
  fi
}

assert_d1_defect() {
  local name="$1"
  local output="$2"
  local rc="$3"
  if [[ "$rc" -eq 1 ]] \
    && grep -q "Unreviewed: 1" <<< "$output" \
    && grep -q "feat: main code" <<< "$output"; then
    record "$name" xfail
  else
    record "$name" xpass
  fi
}

case_d1_merge() {
  init_pair d1_merge
  git checkout -q -b topic
  mkdir -p docs
  printf 'topic\n' > docs/topic.md
  git add docs/topic.md
  git commit -q -m "docs: topic notes"
  git push -q -u origin topic
  local remote_tip
  remote_tip="$(git rev-parse HEAD)"
  git checkout -q main
  mkdir -p src
  printf 'print(1)\n' > src/main.py
  git add src/main.py
  git commit -q -m "feat: main code"
  git push -q origin main
  git checkout -q topic
  git merge --no-edit origin/main >/dev/null
  local output rc=0
  output="$(run_gate "$(git rev-parse HEAD)" "$remote_tip")" || rc=$?
  assert_d1_defect "D1 merge rechecks mainline commit" "$output" "$rc"
}

case_d1_fast_forward() {
  init_pair d1_fast_forward
  git checkout -q -b topic
  git push -q -u origin topic
  local remote_tip
  remote_tip="$(git rev-parse HEAD)"
  git checkout -q main
  mkdir -p src
  printf 'print(2)\n' > src/main.py
  git add src/main.py
  git commit -q -m "feat: main code"
  git push -q origin main
  git checkout -q topic
  git merge --ff-only origin/main >/dev/null
  local output rc=0
  output="$(run_gate "$(git rev-parse HEAD)" "$remote_tip")" || rc=$?
  assert_d1_defect "D1 fast-forward rechecks mainline commit" "$output" "$rc"
}

case_d1_new_branch() {
  init_pair d1_new_branch
  git checkout -q -b topic
  git checkout -q main
  mkdir -p src
  printf 'print(3)\n' > src/main.py
  git add src/main.py
  git commit -q -m "feat: main code"
  git push -q origin main
  git checkout -q topic
  git merge --ff-only origin/main >/dev/null
  local output rc=0
  output="$(run_gate "$(git rev-parse HEAD)" "0000000000000000000000000000000000000000")" || rc=$?
  assert_d1_defect "D1 new branch rechecks mainline commit" "$output" "$rc"
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
  touch -d '2020-01-01 00:00:00' scripts/review/results/old.txt
  local base head
  base="$(git rev-parse HEAD)"
  printf 'print(4)\n' > src/feature.py
  git add src/feature.py
  git commit -q -m "feat: unevidenced code"
  head="$(git rev-parse HEAD)"
  local old_output old_rc=0
  old_output="$(run_gate "$head" "$base")" || old_rc=$?
  git clone -q . "${TMP_ROOT}/d2_fresh_checkout/clone"
  cd "${TMP_ROOT}/d2_fresh_checkout/clone"
  identity
  local clone_output clone_rc=0
  clone_output="$(run_gate "$head" "$base")" || clone_rc=$?
  if [[ "$old_rc" -eq 1 && "$clone_rc" -eq 0 ]] \
    && grep -q "Reviewed: 1, Unreviewed: 0" <<< "$clone_output"; then
    record "D2 fresh checkout mtime evidence" xfail
  else
    record "D2 fresh checkout mtime evidence" xpass
  fi
}

case_d2_one_for_all() {
  init_single d2_one_for_all
  local base head
  base="$(git rev-parse HEAD)"
  mkdir -p src
  for n in 1 2 3; do
    printf 'print(%s)\n' "$n" > "src/f${n}.py"
    git add "src/f${n}.py"
    git commit -q -m "feat: code $n"
  done
  head="$(git rev-parse HEAD)"
  mkdir -p scripts/review/results
  printf 'generic evidence\n' > scripts/review/results/generic.txt
  local output rc=0
  output="$(run_gate "$head" "$base")" || rc=$?
  if [[ "$rc" -eq 0 ]] && grep -q "Reviewed: 3, Unreviewed: 0" <<< "$output"; then
    record "D2 one evidence file covers all commits" xfail
  else
    record "D2 one evidence file covers all commits" xpass
  fi
}

case_d2_keyword() {
  init_single d2_keyword
  printf 'notes\n' > notes.txt
  git add notes.txt
  git commit -q -m "chore: review notes"
  local base
  base="$(git rev-parse HEAD)"
  mkdir -p src
  printf 'print(5)\n' > src/keyword.py
  git add src/keyword.py
  git commit -q -m "feat: keyword code"
  local output rc=0
  output="$(run_gate "$(git rev-parse HEAD)" "$base")" || rc=$?
  if [[ "$rc" -eq 0 ]] && grep -q "Reviewed: 1, Unreviewed: 0" <<< "$output"; then
    record "D2 unrelated keyword commit satisfies evidence" xfail
  else
    record "D2 unrelated keyword commit satisfies evidence" xpass
  fi
}

main() {
  if [[ ! -f "$SCRIPT_UNDER_TEST" ]]; then
    echo "ERROR: script under test not found" >&2
    exit 1
  fi

  case_d1_merge
  case_d1_fast_forward
  case_d1_new_branch
  case_d2_fresh_checkout
  case_d2_one_for_all
  case_d2_keyword

  echo "Results: ${XFAIL_COUNT} XFAIL, ${XPASS_COUNT} XPASS"
  [[ "$XPASS_COUNT" -eq 0 ]]
}

main "$@"
