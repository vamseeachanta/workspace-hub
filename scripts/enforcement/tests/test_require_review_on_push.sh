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
TESTS_SKIPPED=0
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

skip() {
  TESTS_SKIPPED=$((TESTS_SKIPPED + 1))
  echo "  SKIPPED: $1"
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

run_gate_unset_evidence_mode() {
  local local_oid="$1"
  local remote_oid="${2:-}"
  local output rc=0
  output="$(env -u REVIEW_GATE_EVIDENCE_MODE bash "$SCRIPT_UNDER_TEST" "$local_oid" "$remote_oid" 2>&1)" || rc=$?
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

invalid_evidence_value() {
  local kind="$1"
  local commit_id="$2"
  case "$kind" in
    malformed)
      printf 'Reviewed-Bogus: %s\n' "$commit_id"
      ;;
    abbreviated)
      printf 'Reviewed-Commit: %s\n' "${commit_id:0:12}"
      ;;
    unknown)
      printf 'Reviewed-Commit: 1111111111111111111111111111111111111111\n'
      ;;
    *)
      printf 'ERROR: unknown invalid evidence kind %s\n' "$kind" >&2
      return 1
      ;;
  esac
}

invalid_range_evidence_value() {
  local kind="$1"
  local commit_id="$2"
  case "$kind" in
    malformed)
      printf 'Reviewed-Range: not-a-range\n'
      ;;
    abbreviated)
      printf 'Reviewed-Range: %s..%s\n' "${commit_id:0:12}" "${commit_id:0:12}"
      ;;
    *)
      printf 'ERROR: unknown invalid range evidence kind %s\n' "$kind" >&2
      return 1
      ;;
  esac
}

write_invalid_evidence() {
  local kind="$1"
  local commit_id="$2"
  local file="scripts/review/results/invalid-${kind}.txt"
  mkdir -p scripts/review/results
  invalid_evidence_value "$kind" "$commit_id" > "$file"
  printf '%s\n' "$file"
}

write_invalid_range_evidence() {
  local kind="$1"
  local commit_id="$2"
  local file="scripts/review/results/invalid-range-${kind}.txt"
  mkdir -p scripts/review/results
  invalid_range_evidence_value "$kind" "$commit_id" > "$file"
  printf '%s\n' "$file"
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
  assert_contains "Docs/chore/ci output contains PASS" "PASS" "$output"
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
  assert_contains "Summary shows two chore/docs/sync commits" "2 chore/docs/sync" "$output"
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
  assert_contains "Docs-only feat output contains PASS" "PASS" "$output"
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
  assert_contains "Legacy warn mode prints PASS" "PASS" "$output"
  assert_contains "Warn mode reports strict failure" "WOULD-REJECT" "$output"
  assert_contains "Warn mode names deprecated evidence" "DEPRECATED" "$output"
  rc=0
  output="$(REVIEW_GATE_EVIDENCE_MODE=strict run_gate "$head" "$base")" || rc=$?
  assert_rc "Legacy keyword evidence blocks strict evidence mode" 1 "$rc" "$output"
}

case_legacy_unset_default_passes() {
  run_test "Legacy evidence passes when evidence mode is unset"
  init_pair legacy_unset_default
  local base head output rc=0
  base="$(git rev-parse HEAD)"
  add_commit "chore: codex adversarial review completed" "review-note.txt"
  add_commit "feat: add default-mode legacy check" "src/default-legacy.py"
  head="$(git rev-parse HEAD)"
  output="$(run_gate_unset_evidence_mode "$head" "$base")" || rc=$?
  assert_rc "Legacy keyword evidence passes with evidence mode unset" 0 "$rc" "$output"
  assert_contains "Unset default legacy output contains PASS" "PASS" "$output"
  assert_contains "Unset default legacy output reports WOULD-REJECT" "WOULD-REJECT" "$output"
  assert_contains "Unset default legacy output reports DEPRECATED" "DEPRECATED" "$output"
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

case_empty_range_passes() {
  run_test "Empty range passes with no commits to check"
  init_pair empty_range
  local head output rc=0
  head="$(git rev-parse HEAD)"
  output="$(REVIEW_GATE_EVIDENCE_MODE=strict run_gate "$head" "$head")" || rc=$?
  assert_rc "Empty range exits 0" 0 "$rc" "$output"
  assert_contains "Empty range prints no-commits PASS" "PASS: No commits to check" "$output"
}

case_uncomputable_range_blocks() {
  run_test "Uncomputable range fails closed"
  init_pair bad_range
  local base head missing output rc=0
  base="$(git rev-parse HEAD)"
  add_commit "feat: needs computed range" "src/bad-range.py"
  head="$(git rev-parse HEAD)"
  missing="1111111111111111111111111111111111111111"
  output="$(REVIEW_GATE_EVIDENCE_MODE=warn REVIEW_GATE_STRICT=0 run_gate "$head" "$missing")" || rc=$?
  assert_rc "Unknown remote id exits 1 despite non-strict switch" 1 "$rc" "$output"
  assert_contains "Unknown remote id prints range diagnostic" "failed to compute commit range" "$output"
  assert_contains "Unknown remote id prints BLOCKED" "BLOCKED" "$output"
  if grep -q "PASS" <<< "$output"; then
    fail "Unknown remote id must not print PASS" "Output: ${output}"
  else
    pass "Unknown remote id does not print PASS"
  fi
}

case_invalid_evidence_warn_with_legacy() {
  local kind="$1"
  run_test "Invalid ${kind} evidence reports but legacy evidence still passes warn mode"
  init_pair "invalid_${kind}_warn_legacy"
  local base head evidence_file output rc=0
  base="$(git rev-parse HEAD)"
  add_commit "chore: codex adversarial review completed" "review-note.txt"
  add_commit "feat: invalid ${kind} target" "src/${kind}.py"
  head="$(git rev-parse HEAD)"
  evidence_file="$(write_invalid_evidence "$kind" "$head")"
  output="$(REVIEW_GATE_EVIDENCE_MODE=warn run_gate "$head" "$base")" || rc=$?
  assert_rc "Invalid ${kind} plus legacy passes warn mode" 0 "$rc" "$output"
  assert_contains "Invalid ${kind} reports INVALID-EVIDENCE" "INVALID-EVIDENCE" "$output"
  assert_contains "Invalid ${kind} diagnostic names file and line" "${evidence_file}:1" "$output"
  assert_contains "Invalid ${kind} warn mode reports WOULD-REJECT" "WOULD-REJECT ${head}" "$output"
  assert_contains "Invalid ${kind} warn mode reports DEPRECATED" "DEPRECATED" "$output"
}

case_invalid_evidence_warn_without_legacy() {
  local kind="$1"
  run_test "Invalid ${kind} evidence does not replace missing evidence in warn mode"
  init_pair "invalid_${kind}_warn_none"
  local base head evidence_file output rc=0
  base="$(git rev-parse HEAD)"
  add_commit "feat: invalid ${kind} target" "src/${kind}.py"
  head="$(git rev-parse HEAD)"
  evidence_file="$(write_invalid_evidence "$kind" "$head")"
  output="$(REVIEW_GATE_EVIDENCE_MODE=warn run_gate "$head" "$base")" || rc=$?
  assert_rc "Invalid ${kind} without other evidence blocks in warn mode" 1 "$rc" "$output"
  assert_contains "Invalid ${kind} reports diagnostic in warn mode" "INVALID-EVIDENCE" "$output"
  assert_contains "Invalid ${kind} diagnostic names file and line in warn mode" "${evidence_file}:1" "$output"
  assert_contains "Invalid ${kind} warning path reports BLOCKED" "BLOCKED" "$output"
}

case_invalid_evidence_strict_with_legacy() {
  local kind="$1"
  run_test "Invalid ${kind} evidence does not count in strict mode"
  init_pair "invalid_${kind}_strict"
  local base head evidence_file output rc=0
  base="$(git rev-parse HEAD)"
  add_commit "chore: codex adversarial review completed" "review-note.txt"
  add_commit "feat: invalid ${kind} target" "src/${kind}.py"
  head="$(git rev-parse HEAD)"
  evidence_file="$(write_invalid_evidence "$kind" "$head")"
  output="$(REVIEW_GATE_EVIDENCE_MODE=strict run_gate "$head" "$base")" || rc=$?
  assert_rc "Invalid ${kind} plus legacy blocks in strict mode" 1 "$rc" "$output"
  assert_contains "Invalid ${kind} reports diagnostic in strict mode" "INVALID-EVIDENCE" "$output"
  assert_contains "Invalid ${kind} diagnostic names file and line in strict mode" "${evidence_file}:1" "$output"
  assert_contains "Invalid ${kind} strict path reports BLOCKED" "BLOCKED" "$output"
  assert_contains "Invalid ${kind} strict path lists the feature commit" "feat: invalid ${kind} target" "$output"
}

case_invalid_evidence_with_valid_commit() {
  local mode="$1"
  run_test "Invalid evidence beside valid Reviewed-Commit passes in ${mode} mode"
  init_pair "invalid_valid_${mode}"
  local base head evidence_file output rc=0
  base="$(git rev-parse HEAD)"
  add_commit "feat: valid target beside invalid evidence" "src/valid-${mode}.py"
  head="$(git rev-parse HEAD)"
  evidence_file="$(write_invalid_evidence malformed "$head")"
  printf 'Reviewed-Commit: %s\n' "$head" >> "$evidence_file"
  output="$(REVIEW_GATE_EVIDENCE_MODE="$mode" run_gate "$head" "$base")" || rc=$?
  assert_rc "Valid Reviewed-Commit wins despite invalid line in ${mode} mode" 0 "$rc" "$output"
  assert_contains "Invalid line is still diagnosed in ${mode} mode" "INVALID-EVIDENCE" "$output"
  assert_contains "Invalid diagnostic names file and line in ${mode} mode" "${evidence_file}:1" "$output"
}

case_invalid_range_evidence_warn_without_legacy() {
  local kind="$1"
  run_test "Invalid ${kind} Reviewed-Range does not replace missing evidence in warn mode"
  init_pair "invalid_range_${kind}_warn_none"
  local base head evidence_file output rc=0
  base="$(git rev-parse HEAD)"
  add_commit "feat: invalid range ${kind} target" "src/range-${kind}.py"
  head="$(git rev-parse HEAD)"
  evidence_file="$(write_invalid_range_evidence "$kind" "$head")"
  output="$(REVIEW_GATE_EVIDENCE_MODE=warn run_gate "$head" "$base")" || rc=$?
  assert_rc "Invalid ${kind} Reviewed-Range without other evidence blocks in warn mode" 1 "$rc" "$output"
  assert_contains "Invalid ${kind} Reviewed-Range reports diagnostic in warn mode" "INVALID-EVIDENCE" "$output"
  assert_contains "Invalid ${kind} Reviewed-Range diagnostic names file and line" "${evidence_file}:1" "$output"
  assert_contains "Invalid ${kind} Reviewed-Range warning path reports BLOCKED" "BLOCKED" "$output"
}

case_invalid_range_evidence_with_valid_commit() {
  local kind="$1"
  run_test "Invalid ${kind} Reviewed-Range beside valid Reviewed-Commit passes"
  init_pair "invalid_range_valid_${kind}"
  local base head evidence_file output rc=0
  base="$(git rev-parse HEAD)"
  add_commit "feat: valid target beside invalid range ${kind}" "src/range-valid-${kind}.py"
  head="$(git rev-parse HEAD)"
  evidence_file="$(write_invalid_range_evidence "$kind" "$head")"
  printf 'Reviewed-Commit: %s\n' "$head" >> "$evidence_file"
  output="$(REVIEW_GATE_EVIDENCE_MODE=warn run_gate "$head" "$base")" || rc=$?
  assert_rc "Valid Reviewed-Commit wins despite invalid ${kind} Reviewed-Range" 0 "$rc" "$output"
  assert_contains "Invalid ${kind} Reviewed-Range is still diagnosed" "INVALID-EVIDENCE" "$output"
  assert_contains "Invalid ${kind} Reviewed-Range diagnostic names file and line" "${evidence_file}:1" "$output"
}

case_unreadable_result_blocks() {
  run_test "Unreadable review result fails closed"
  init_pair unreadable_result
  local base head evidence_file output rc=0
  base="$(git rev-parse HEAD)"
  add_commit "feat: unreadable evidence target" "src/unreadable.py"
  head="$(git rev-parse HEAD)"
  mkdir -p scripts/review/results
  evidence_file="scripts/review/results/unreadable.txt"
  printf 'Reviewed-Commit: %s\n' "$head" > "$evidence_file"
  chmod 000 "$evidence_file"
  if [[ "${REVIEW_GATE_TEST_FORCE_UNREADABLE_SKIP:-0}" == "1" || -r "$evidence_file" ]]; then
    chmod 600 "$evidence_file"
    skip "Unreadable review result not applicable on this host" "host cannot make the evidence file unreadable"
    return
  fi
  output="$(REVIEW_GATE_EVIDENCE_MODE=strict run_gate "$head" "$base")" || rc=$?
  chmod 600 "$evidence_file"
  assert_rc "Unreadable review result exits 1" 1 "$rc" "$output"
  assert_contains "Unreadable review result diagnostic names file" "cannot read evidence file" "$output"
  assert_contains "Unreadable review result prints BLOCKED" "BLOCKED" "$output"
}

case_invalid_evidence_strict_switch_zero_matches_absent() {
  run_test "Invalid evidence with REVIEW_GATE_STRICT=0 behaves like absent evidence"
  init_pair invalid_strict_zero
  local base head invalid_output absent_output invalid_rc=0 absent_rc=0 invalid_warning absent_warning
  base="$(git rev-parse HEAD)"
  add_commit "feat: invalid strict-zero target" "src/strict-zero.py"
  head="$(git rev-parse HEAD)"
  invalid_evidence_value unknown "$head" > "${TMP_ROOT}/invalid-only-line.txt"
  mkdir -p scripts/review/results
  cp "${TMP_ROOT}/invalid-only-line.txt" scripts/review/results/invalid-only.txt
  invalid_output="$(REVIEW_GATE_STRICT=0 REVIEW_GATE_EVIDENCE_MODE=warn run_gate "$head" "$base")" || invalid_rc=$?
  rm scripts/review/results/invalid-only.txt
  absent_output="$(REVIEW_GATE_STRICT=0 REVIEW_GATE_EVIDENCE_MODE=warn run_gate "$head" "$base")" || absent_rc=$?
  invalid_warning="$(grep 'WARNING:' <<< "$invalid_output" || true)"
  absent_warning="$(grep 'WARNING:' <<< "$absent_output" || true)"
  assert_rc "Invalid-only strict-zero exit matches absent evidence" "$absent_rc" "$invalid_rc" "$invalid_output"
  assert_rc "Absent evidence exits 0 with REVIEW_GATE_STRICT=0" 0 "$absent_rc" "$absent_output"
  assert_contains "Absent evidence strict-zero reports WARNING" "WARNING" "$absent_output"
  if [[ "$invalid_warning" == "$absent_warning" && -n "$invalid_warning" ]]; then
    pass "Invalid-only strict-zero WARNING text matches absent evidence"
  else
    fail "Invalid-only strict-zero WARNING text differs" "Invalid: ${invalid_warning}; absent: ${absent_warning}"
  fi
  assert_contains "Invalid-only strict-zero reports diagnostic" "INVALID-EVIDENCE" "$invalid_output"
}

case_unknown_mode_docs_only_blocks_first() {
  run_test "Unknown REVIEW_GATE_EVIDENCE_MODE blocks before docs-only classification"
  init_pair unknown_mode_docs
  local base head output rc=0
  base="$(git rev-parse HEAD)"
  add_commit "docs: mode validation still runs" "docs/mode.md"
  head="$(git rev-parse HEAD)"
  output="$(REVIEW_GATE_EVIDENCE_MODE=surprise run_gate "$head" "$base")" || rc=$?
  assert_rc "Unknown evidence mode exits 1 on docs-only push" 1 "$rc" "$output"
  assert_contains "Unknown evidence mode prints ERROR" "ERROR: REVIEW_GATE_EVIDENCE_MODE" "$output"
  assert_contains "Unknown evidence mode prints BLOCKED" "BLOCKED" "$output"
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

case_default_branch_absent_fallback_failure_blocks() {
  run_test "Absent default branch fallback fails closed when lookup fails"
  init_single default_absent_bad_fallback
  local base head missing output rc=0
  base="$(git rev-parse HEAD)"
  add_commit "feat: absent default bad fallback" "src/absent-default-bad-fallback.py"
  head="$(git rev-parse HEAD)"
  missing="1111111111111111111111111111111111111111"
  output="$(REVIEW_GATE_EVIDENCE_MODE=warn REVIEW_GATE_STRICT=0 run_gate "$head" "$missing")" || rc=$?
  assert_rc "Absent default bad fallback exits 1 despite non-strict switch" 1 "$rc" "$output"
  assert_contains "Absent default bad fallback reports missing default ref" "fetch the default branch" "$output"
  assert_contains "Absent default bad fallback prints range diagnostic" "failed to compute commit range" "$output"
  assert_contains "Absent default bad fallback prints BLOCKED" "BLOCKED" "$output"
  if grep -q "PASS" <<< "$output"; then
    fail "Absent default bad fallback must not print PASS" "Output: ${output}"
  else
    pass "Absent default bad fallback does not print PASS"
  fi
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

case_evidence_filename_boundaries() {
  # Independent oracle: one feature commit is named in the evidence, so strict
  # mode has no unreviewed commits (docs/enforcement/review-gate-defects.md,
  # Evidence file format). A filename separator cannot change that binding.
  run_test "Evidence filenames preserve whitespace and newline boundaries"
  init_pair filename_boundaries
  local base head output rc=0
  base="$(git rev-parse HEAD)"
  add_commit "feat: filename evidence target" "src/filename.py"
  head="$(git rev-parse HEAD)"
  mkdir -p scripts/review/results
  printf 'Reviewed-Commit: %s\n' "$head" > $'scripts/review/results/review notes\nfinal.txt'
  output="$(REVIEW_GATE_EVIDENCE_MODE=strict run_gate "$head" "$base")" || rc=$?
  assert_rc "Newline filename preserves commit-bound evidence" 0 "$rc" "$output"
  assert_contains "Newline filename covers the feature commit" "Reviewed: 1, Unreviewed: 0" "$output"
  # A generic result at the same path is legacy evidence only. The migration
  # contract permits warn mode and denies strict mode for this same feature.
  printf 'generic result\n' > $'scripts/review/results/review notes\nfinal.txt'
  rc=0
  output="$(REVIEW_GATE_EVIDENCE_MODE=warn run_gate "$head" "$base")" || rc=$?
  assert_rc "Newline filename preserves legacy migration evidence" 0 "$rc" "$output"
  assert_contains "Legacy newline result reports migration warning" "WOULD-REJECT" "$output"
  rc=0
  output="$(REVIEW_GATE_EVIDENCE_MODE=strict run_gate "$head" "$base")" || rc=$?
  assert_rc "Newline filename does not turn legacy evidence into a binding" 1 "$rc" "$output"
}

case_crlf_evidence() {
  # Independent hand calculation: A -> B are the only feature commits.
  # Reviewed-Range A..B includes both endpoints by the repository's Evidence
  # file format contract; Reviewed-Commit A alone leaves only B unreviewed.
  run_test "CRLF evidence preserves exact commit and inclusive range bindings"
  init_pair crlf_evidence
  local base first head output rc=0
  base="$(git rev-parse HEAD)"
  add_commit "feat: first CRLF target" "src/first.py"
  first="$(git rev-parse HEAD)"
  add_commit "feat: second CRLF target" "src/second.py"
  head="$(git rev-parse HEAD)"
  mkdir -p scripts/review/results
  printf 'Reviewed-Commit: %s\r\n' "$first" > scripts/review/results/crlf.txt
  output="$(REVIEW_GATE_EVIDENCE_MODE=strict run_gate "$head" "$base")" || rc=$?
  assert_rc "Partial CRLF evidence still blocks" 1 "$rc" "$output"
  assert_contains "CRLF commit binding covers only the named commit" "Reviewed: 1, Unreviewed: 1" "$output"
  printf 'Reviewed-Range: %s..%s\r\n' "$first" "$head" >> scripts/review/results/crlf.txt
  rc=0
  output="$(REVIEW_GATE_EVIDENCE_MODE=strict run_gate "$head" "$base")" || rc=$?
  assert_rc "CRLF range evidence passes" 0 "$rc" "$output"
  assert_contains "CRLF range covers both feature commits" "Reviewed: 2, Unreviewed: 0" "$output"
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
  case_legacy_unset_default_passes
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
  case_empty_range_passes
  case_uncomputable_range_blocks
  for invalid_kind in malformed abbreviated unknown; do
    case_invalid_evidence_warn_with_legacy "$invalid_kind"
    case_invalid_evidence_warn_without_legacy "$invalid_kind"
    case_invalid_evidence_strict_with_legacy "$invalid_kind"
  done
  case_invalid_evidence_with_valid_commit "warn"
  case_invalid_evidence_with_valid_commit "strict"
  for invalid_range_kind in malformed abbreviated; do
    case_invalid_range_evidence_warn_without_legacy "$invalid_range_kind"
    case_invalid_range_evidence_with_valid_commit "$invalid_range_kind"
  done
  case_unreadable_result_blocks
  case_invalid_evidence_strict_switch_zero_matches_absent
  case_unknown_mode_docs_only_blocks_first
  case_default_branch_absent
  case_default_branch_absent_fallback_failure_blocks
  case_default_mode_line
  case_sigpipe_regression
  case_evidence_filename_boundaries
  case_crlf_evidence

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
  echo "Results: ${TESTS_RUN} tests, ${TESTS_PASSED} passed, ${TESTS_SKIPPED} skipped, ${TESTS_FAILED} failed"
  echo "========================================"

  [[ "$TESTS_FAILED" -eq 0 ]]
}

main "$@"
