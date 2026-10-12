#!/usr/bin/env bash
# test_require_review_on_push.sh — Tests for the review enforcement pre-push hook.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_UNDER_TEST="${SCRIPT_DIR}/../require-review-on-push.sh"
KNOWN_DEFECTS_TEST="${SCRIPT_DIR}/test_require_review_on_push_known_defects.sh"
TMP_ROOT="$(mktemp -d)"

trap 'rm -rf "$TMP_ROOT"' EXIT

TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

pass() {
  TESTS_PASSED=$((TESTS_PASSED + 1))
  echo "  PASS: $1"
}

fail() {
  TESTS_FAILED=$((TESTS_FAILED + 1))
  echo "  FAIL: $1"
  [[ -n "${2:-}" ]] && echo "        $2"
}

run_test() {
  TESTS_RUN=$((TESTS_RUN + 1))
  echo ""
  echo "--- Test ${TESTS_RUN}: $1 ---"
}

identity() {
  local user domain
  user="test"
  domain="example.invalid"
  git config user.email "${user}@${domain}"
  git config user.name "Test User"
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
  git commit -q -m "chore: initial commit"
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
  git commit -q -m "chore: initial commit"
}

add_commit() {
  local msg="$1"
  local path="${2:-file-${RANDOM}.txt}"
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

write_reviewed_commit() {
  local commit_id="$1"
  mkdir -p scripts/review/results
  printf 'Reviewed-Commit: %s\n' "$commit_id" > "scripts/review/results/${commit_id}.txt"
}

write_reviewed_range() {
  local start_id="$1"
  local end_id="$2"
  mkdir -p scripts/review/results
  printf 'Reviewed-Range: %s..%s\n' "$start_id" "$end_id" > "scripts/review/results/range.txt"
}

assert_rc() {
  local name="$1"
  local expected="$2"
  local actual="$3"
  local output="$4"
  if [[ "$actual" -eq "$expected" ]]; then
    pass "$name"
  else
    fail "$name" "Expected exit ${expected}, got ${actual}. Output: ${output}"
  fi
}

assert_contains() {
  local name="$1"
  local needle="$2"
  local output="$3"
  if grep -q "$needle" <<< "$output"; then
    pass "$name"
  else
    fail "$name" "Missing '${needle}'. Output: ${output}"
  fi
}

case_docs_only_pass() {
  run_test "Docs-only commits pass"
  init_pair docs_only
  local base head output rc=0
  base="$(git rev-parse HEAD)"
  add_commit "docs: update README" "docs/readme.md"
  add_commit "chore: bump version" "VERSION"
  add_commit "ci: fix pipeline" ".github-ci.txt"
  head="$(git rev-parse HEAD)"
  output="$(run_gate "$head" "$base")" || rc=$?
  assert_rc "Docs/chore/ci commits pass without review" 0 "$rc" "$output"
}

case_feature_without_evidence_blocks() {
  run_test "Feature commits without any evidence block"
  init_pair no_evidence
  local base head output rc=0
  base="$(git rev-parse HEAD)"
  add_commit "feat: add user authentication" "src/auth.py"
  add_commit "fix: resolve login bug" "src/login.py"
  head="$(git rev-parse HEAD)"
  output="$(run_gate "$head" "$base")" || rc=$?
  assert_rc "No-evidence feature commits block under current settings" 1 "$rc" "$output"
  assert_contains "Output lists the feat commit" "feat: add user authentication" "$output"
}

case_skip_bypass_logs() {
  run_test "SKIP_REVIEW_GATE=1 bypasses and logs"
  init_pair skip_bypass
  local base head repo_dir output rc=0
  base="$(git rev-parse HEAD)"
  add_commit "feat: dangerous feature without review" "src/danger.py"
  head="$(git rev-parse HEAD)"
  repo_dir="$(pwd)"
  output="$(SKIP_REVIEW_GATE=1 run_gate "$head" "$base")" || rc=$?
  assert_rc "SKIP_REVIEW_GATE=1 exits 0" 0 "$rc" "$output"
  assert_contains "Output mentions bypass" "SKIP" "$output"
  if [[ -f "${repo_dir}/logs/hooks/review-gate-bypass.jsonl" ]] \
    && grep -q "bypass" "${repo_dir}/logs/hooks/review-gate-bypass.jsonl"; then
    pass "Bypass logged"
  else
    fail "Expected bypass log" "Output: $output"
  fi
}

case_strict_mode_blocks() {
  run_test "REVIEW_GATE_STRICT=1 blocks no-evidence commits"
  init_pair strict_blocks
  local base head output rc=0
  base="$(git rev-parse HEAD)"
  add_commit "feat: critical feature" "src/critical.py"
  head="$(git rev-parse HEAD)"
  output="$(REVIEW_GATE_STRICT=1 run_gate "$head" "$base")" || rc=$?
  assert_rc "Strict mode exits 1" 1 "$rc" "$output"
  assert_contains "Output mentions BLOCKED" "BLOCKED" "$output"
}

case_mixed_commits_block_feat() {
  run_test "Mixed commits block only the feature commit"
  init_pair mixed
  local base head output rc=0
  base="$(git rev-parse HEAD)"
  add_commit "docs: update changelog" "docs/changelog.md"
  add_commit "feat: implement search" "src/search.py"
  add_commit "chore: lint fixes" "lint.txt"
  head="$(git rev-parse HEAD)"
  output="$(run_gate "$head" "$base")" || rc=$?
  assert_rc "Mixed commits block without evidence" 1 "$rc" "$output"
  assert_contains "Output lists the feat commit" "feat: implement search" "$output"
  assert_contains "Summary shows one feature commit" "1 feature/fix" "$output"
}

case_docs_path_supplement_passes() {
  run_test "Feature-labeled docs-only commit is low risk"
  init_pair docs_path
  local base head output rc=0
  base="$(git rev-parse HEAD)"
  add_commit "feat: update docs guide" "docs/guide.md"
  head="$(git rev-parse HEAD)"
  output="$(run_gate "$head" "$base")" || rc=$?
  assert_rc "Docs-only feat commit passes" 0 "$rc" "$output"
}

case_latency_log_written() {
  run_test "Latency log is written"
  init_pair latency
  local base head repo_dir output rc=0
  base="$(git rev-parse HEAD)"
  add_commit "feat: latency check" "src/latency.py"
  head="$(git rev-parse HEAD)"
  repo_dir="$(pwd)"
  output="$(run_gate "$head" "$base")" || rc=$?
  if [[ -f "${repo_dir}/logs/hooks/review-gate-latency.jsonl" ]] \
    && grep -q 'latency_ms' "${repo_dir}/logs/hooks/review-gate-latency.jsonl"; then
    pass "Latency log created"
  else
    fail "Expected latency log" "Output: $output; rc=$rc"
  fi
}

case_legacy_warn_and_strict() {
  run_test "Legacy evidence warns in evidence-warn mode and blocks in evidence-strict mode"
  init_pair legacy
  local base head output rc=0
  base="$(git rev-parse HEAD)"
  add_commit "chore: codex adversarial review completed" "review-note.txt"
  add_commit "feat: add payment processing" "src/payments.py"
  head="$(git rev-parse HEAD)"
  output="$(REVIEW_GATE_EVIDENCE_MODE=warn run_gate "$head" "$base")" || rc=$?
  assert_rc "Legacy keyword evidence passes warn mode" 0 "$rc" "$output"
  assert_contains "Warn mode reports strict failure" "WOULD-REJECT" "$output"
  assert_contains "Warn mode names deprecated evidence" "DEPRECATED" "$output"
  rc=0
  output="$(REVIEW_GATE_EVIDENCE_MODE=strict run_gate "$head" "$base")" || rc=$?
  assert_rc "Legacy keyword evidence blocks strict evidence mode" 1 "$rc" "$output"
}

case_d1_mainline_excluded() {
  local mode_name="$1"
  local update_cmd="$2"
  run_test "D1 ${mode_name}: mainline commit is excluded"
  init_pair "d1_${mode_name}"
  git checkout -q -b topic
  if [[ "$mode_name" != "fast_forward" ]]; then
    add_commit "docs: topic notes" "docs/topic.md"
  fi
  git push -q -u origin topic
  local remote_tip output rc=0
  remote_tip="$(git rev-parse HEAD)"
  git checkout -q main
  add_commit "feat: main code" "src/main.py"
  git push -q origin main
  git checkout -q topic
  eval "$update_cmd"
  output="$(REVIEW_GATE_EVIDENCE_MODE=strict run_gate "$(git rev-parse HEAD)" "$remote_tip")" || rc=$?
  assert_rc "D1 ${mode_name} passes because mainline commit is excluded" 0 "$rc" "$output"
}

case_d1_new_branch() {
  run_test "D1 new branch: commits reachable from origin/main are excluded"
  init_pair d1_new_branch
  git checkout -q -b topic
  git checkout -q main
  add_commit "feat: main code" "src/main.py"
  git push -q origin main
  git checkout -q topic
  git merge --ff-only origin/main >/dev/null
  local output rc=0
  output="$(REVIEW_GATE_EVIDENCE_MODE=strict run_gate "$(git rev-parse HEAD)" "0000000000000000000000000000000000000000")" || rc=$?
  assert_rc "D1 new branch passes because mainline commit is excluded" 0 "$rc" "$output"
}

case_d2_fresh_checkout() {
  run_test "D2 fresh checkout: mtime-only evidence is legacy only"
  init_single d2_fresh_checkout
  mkdir -p scripts/review/results src
  printf 'old evidence\n' > scripts/review/results/old.txt
  touch -d '2020-01-01 00:00:00' scripts/review/results/old.txt
  git add scripts/review/results/old.txt
  GIT_AUTHOR_DATE='2020-01-01T00:00:00Z' \
    GIT_COMMITTER_DATE='2020-01-01T00:00:00Z' \
    git commit -q -m "chore: old evidence fixture"
  touch -d '2020-01-01 00:00:00' scripts/review/results/old.txt
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
  assert_rc "Fresh checkout blocks in strict evidence mode" 1 "$rc" "$output"
  rc=0
  output="$(REVIEW_GATE_EVIDENCE_MODE=warn run_gate "$head" "$base")" || rc=$?
  assert_rc "Fresh checkout legacy evidence passes warn mode" 0 "$rc" "$output"
  assert_contains "Fresh checkout warn mode reports WOULD-REJECT" "WOULD-REJECT" "$output"
}

case_d2_one_for_all() {
  run_test "D2 one-for-all: generic evidence does not bind commits"
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
  assert_rc "Generic evidence blocks strict evidence mode" 1 "$rc" "$output"
  rc=0
  output="$(REVIEW_GATE_EVIDENCE_MODE=warn run_gate "$head" "$base")" || rc=$?
  assert_rc "Generic evidence passes warn mode as legacy" 0 "$rc" "$output"
  assert_contains "Generic evidence warn mode reports WOULD-REJECT" "WOULD-REJECT" "$output"
}

case_d2_keyword() {
  run_test "D2 unrelated keyword: subject keyword is legacy only"
  init_pair d2_keyword
  add_commit "chore: review notes" "notes.txt"
  local base head output rc=0
  base="$(git rev-parse HEAD)"
  add_commit "feat: keyword code" "src/keyword.py"
  head="$(git rev-parse HEAD)"
  output="$(REVIEW_GATE_EVIDENCE_MODE=strict run_gate "$head" "$base")" || rc=$?
  assert_rc "Unrelated keyword blocks strict evidence mode" 1 "$rc" "$output"
  rc=0
  output="$(REVIEW_GATE_EVIDENCE_MODE=warn run_gate "$head" "$base")" || rc=$?
  assert_rc "Unrelated keyword passes warn mode as legacy" 0 "$rc" "$output"
  assert_contains "Keyword warn mode reports DEPRECATED" "DEPRECATED" "$output"
}

case_correct_evidence_and_range() {
  run_test "Correct commit-bound evidence and reviewed range pass"
  init_pair correct_evidence
  local base c1 c2 head output rc=0
  base="$(git rev-parse HEAD)"
  add_commit "feat: code 1" "src/c1.py"
  c1="$(git rev-parse HEAD)"
  add_commit "feat: code 2" "src/c2.py"
  c2="$(git rev-parse HEAD)"
  head="$c2"
  write_reviewed_commit "$c1"
  write_reviewed_range "$c1" "$c2"
  output="$(REVIEW_GATE_EVIDENCE_MODE=strict run_gate "$head" "$base")" || rc=$?
  assert_rc "Commit-bound and range evidence pass strict mode" 0 "$rc" "$output"
}

case_amended_or_squashed_blocks() {
  run_test "Amended commit id is not covered by old evidence"
  init_pair amended
  local base old_id new_id output rc=0
  base="$(git rev-parse HEAD)"
  add_commit "feat: amendable code" "src/amend.py"
  old_id="$(git rev-parse HEAD)"
  write_reviewed_commit "$old_id"
  printf 'changed\n' >> src/amend.py
  git add src/amend.py
  git commit -q --amend --no-edit
  new_id="$(git rev-parse HEAD)"
  output="$(REVIEW_GATE_EVIDENCE_MODE=strict run_gate "$new_id" "$base")" || rc=$?
  assert_rc "Old evidence does not cover amended commit id" 1 "$rc" "$output"
}

case_partial_evidence() {
  run_test "Partial evidence reports only unevidenced commits"
  init_pair partial
  local base c1 head output rc=0
  base="$(git rev-parse HEAD)"
  add_commit "feat: partial 1" "src/p1.py"
  c1="$(git rev-parse HEAD)"
  add_commit "feat: partial 2" "src/p2.py"
  add_commit "feat: partial 3" "src/p3.py"
  head="$(git rev-parse HEAD)"
  write_reviewed_commit "$c1"
  output="$(REVIEW_GATE_EVIDENCE_MODE=strict run_gate "$head" "$base")" || rc=$?
  assert_rc "Partial evidence blocks strict mode" 1 "$rc" "$output"
  assert_contains "Partial evidence leaves two unreviewed" "Unreviewed: 2" "$output"
  mkdir -p scripts/review/results
  printf 'legacy\n' > scripts/review/results/legacy.txt
  rc=0
  output="$(REVIEW_GATE_EVIDENCE_MODE=warn run_gate "$head" "$base")" || rc=$?
  assert_rc "Partial evidence plus legacy passes warn mode" 0 "$rc" "$output"
  assert_contains "Partial evidence warn mode reports WOULD-REJECT" "WOULD-REJECT" "$output"
}

case_new_branch_feature_blocks() {
  run_test "New branch with unevidenced feature commits blocks"
  init_pair new_branch_feature
  local base head output rc=0
  base="0000000000000000000000000000000000000000"
  git checkout -q -b topic
  add_commit "feat: branch feature" "src/branch.py"
  head="$(git rev-parse HEAD)"
  output="$(REVIEW_GATE_EVIDENCE_MODE=strict run_gate "$head" "$base")" || rc=$?
  assert_rc "New branch feature commit blocks strict mode" 1 "$rc" "$output"
}

case_malformed_evidence() {
  run_test "Malformed evidence is rejected with diagnostics"
  init_pair malformed
  local base head output rc=0
  base="$(git rev-parse HEAD)"
  add_commit "feat: malformed target" "src/malformed.py"
  head="$(git rev-parse HEAD)"
  mkdir -p scripts/review/results
  {
    printf 'Reviewed-Commit: abc123\n'
    printf 'Reviewed-Commit: zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz\n'
    printf 'Reviewed-Commit: 1111111111111111111111111111111111111111\n'
  } > scripts/review/results/bad.txt
  output="$(REVIEW_GATE_EVIDENCE_MODE=strict run_gate "$head" "$base")" || rc=$?
  assert_rc "Malformed evidence exits 1" 1 "$rc" "$output"
  assert_contains "Malformed evidence reports file and line" "INVALID-EVIDENCE" "$output"
}

case_default_branch_absent() {
  run_test "Absent default branch ref falls back only in evidence-warn mode"
  init_single default_absent
  local base head output rc=0
  base="$(git rev-parse HEAD)"
  add_commit "docs: absent default branch" "docs/absent.md"
  head="$(git rev-parse HEAD)"
  output="$(REVIEW_GATE_EVIDENCE_MODE=warn run_gate "$head" "$base")" || rc=$?
  assert_rc "Absent default branch ref falls back in warn mode" 0 "$rc" "$output"
  assert_contains "Warn fallback tells developer to fetch" "fetch the default branch" "$output"
  rc=0
  output="$(REVIEW_GATE_EVIDENCE_MODE=strict run_gate "$head" "$base")" || rc=$?
  assert_rc "Absent default branch ref fails closed in strict mode" 1 "$rc" "$output"
}

case_default_mode_line() {
  run_test "Default evidence mode is warn on one dated line"
  local output
  output="$(grep -n 'REVIEW_GATE_EVIDENCE_MODE=\"${REVIEW_GATE_EVIDENCE_MODE:-warn}\".*2026-10-26' "$SCRIPT_UNDER_TEST" || true)"
  if [[ "$(wc -l <<< "$output" | tr -d ' ')" -eq 1 ]]; then
    pass "Default evidence mode has one warn-first line"
  else
    fail "Expected exactly one default evidence mode line" "Output: $output"
  fi
}

case_sigpipe_regression() {
  run_test "SIGPIPE regression: early matching evidence passes"
  init_pair sigpipe
  local base head output rc=0
  base="$(git rev-parse HEAD)"
  add_commit "feat: sigpipe code" "src/sigpipe.py"
  head="$(git rev-parse HEAD)"
  write_reviewed_commit "$head"
  output="$(REVIEW_GATE_EVIDENCE_MODE=strict run_gate "$head" "$base")" || rc=$?
  assert_rc "Commit-bound evidence passes without pipefail false negative" 0 "$rc" "$output"
}

main() {
  echo "========================================"
  echo "Tests for require-review-on-push.sh"
  echo "========================================"

  [[ -f "$SCRIPT_UNDER_TEST" ]] || { echo "ERROR: script under test not found"; exit 1; }

  case_docs_only_pass
  case_feature_without_evidence_blocks
  case_skip_bypass_logs
  case_strict_mode_blocks
  case_mixed_commits_block_feat
  case_docs_path_supplement_passes
  case_latency_log_written
  case_legacy_warn_and_strict
  case_d1_mainline_excluded "merge" "git merge --no-edit origin/main >/dev/null"
  case_d1_mainline_excluded "fast_forward" "git merge --ff-only origin/main >/dev/null"
  case_d1_new_branch
  case_d2_fresh_checkout
  case_d2_one_for_all
  case_d2_keyword
  case_correct_evidence_and_range
  case_amended_or_squashed_blocks
  case_partial_evidence
  case_new_branch_feature_blocks
  case_malformed_evidence
  case_default_branch_absent
  case_default_mode_line
  case_sigpipe_regression

  if [[ "${RUN_KNOWN_DEFECTS_FROM_MAIN:-1}" == "1" ]]; then
    run_test "Known-defects regression script is wired through the main test"
    if RUN_KNOWN_DEFECTS_FROM_MAIN=0 bash "$KNOWN_DEFECTS_TEST"; then
      pass "Known-defects regression script passes"
    else
      fail "Known-defects regression script failed"
    fi
  fi

  echo ""
  echo "========================================"
  echo "Results: ${TESTS_RUN} tests, ${TESTS_PASSED} passed, ${TESTS_FAILED} failed"
  echo "========================================"

  [[ "$TESTS_FAILED" -eq 0 ]]
}

main "$@"
