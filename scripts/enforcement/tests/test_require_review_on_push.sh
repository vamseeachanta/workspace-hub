#!/usr/bin/env bash
# test_require_review_on_push.sh — Tests for the review enforcement pre-push hook
# Uses a temporary git repo to simulate push scenarios.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_UNDER_TEST="${SCRIPT_DIR}/../require-review-on-push.sh"

# --- Test infrastructure ---
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0
TMPDIR_BASE=""

pass() {
  TESTS_PASSED=$((TESTS_PASSED + 1))
  echo "  PASS: $1"
}

fail() {
  TESTS_FAILED=$((TESTS_FAILED + 1))
  echo "  FAIL: $1"
  if [[ -n "${2:-}" ]]; then
    echo "        $2"
  fi
}

run_test() {
  TESTS_RUN=$((TESTS_RUN + 1))
  echo ""
  echo "--- Test ${TESTS_RUN}: $1 ---"
}

# --- Setup / Teardown ---
setup_test_repo() {
  TMPDIR_BASE="$(mktemp -d)"
  local repo_dir="${TMPDIR_BASE}/repo"
  mkdir -p "$repo_dir"
  cd "$repo_dir"
  git init -q
  git config user.email "test@test.com"
  git config user.name "Test User"
  # Initial commit so we have a base
  echo "init" > README.md
  git add README.md
  git commit -q -m "chore: initial commit"
}

teardown_test_repo() {
  if [[ -n "$TMPDIR_BASE" ]] && [[ -d "$TMPDIR_BASE" ]]; then
    rm -rf "$TMPDIR_BASE"
  fi
  TMPDIR_BASE=""
}

# Helper: add a commit with a given message
add_commit() {
  local msg="$1"
  local filename
  filename="file-$(date +%s%N)-${RANDOM}.txt"
  echo "$msg" > "$filename"
  git add "$filename"
  git commit -q -m "$msg"
}

# Helper: run the script and capture output + exit code
run_script() {
  local local_oid="${1:-HEAD}"
  local remote_oid="${2:-}"
  local exit_code=0
  local output
  output="$(bash "$SCRIPT_UNDER_TEST" "$local_oid" "$remote_oid" 2>&1)" || exit_code=$?
  echo "$output"
  return $exit_code
}

# =============================================================================
# Test 1: Docs-only commits produce PASS
# =============================================================================
test_docs_only_pass() {
  run_test "Docs-only commits produce PASS (no review needed)"
  setup_test_repo

  local base_oid
  base_oid="$(git rev-parse HEAD)"

  add_commit "docs: update README"
  add_commit "chore: bump version"
  add_commit "ci: fix pipeline"

  local head_oid
  head_oid="$(git rev-parse HEAD)"

  local output exit_code=0
  output="$(run_script "$head_oid" "$base_oid")" || exit_code=$?

  if [[ $exit_code -eq 0 ]] && echo "$output" | grep -q "PASS"; then
    pass "Docs/chore/ci commits pass without review"
  else
    fail "Expected PASS exit 0, got exit ${exit_code}" "Output: $output"
  fi

  teardown_test_repo
}

# =============================================================================
# Test 2: Feature commits without review evidence produce WARNING
# =============================================================================
test_feature_no_evidence_warns() {
  run_test "Feature commits without review evidence produce WARNING"
  setup_test_repo

  local base_oid
  base_oid="$(git rev-parse HEAD)"

  add_commit "feat: add user authentication"
  add_commit "fix: resolve login bug"

  local head_oid
  head_oid="$(git rev-parse HEAD)"

  local output exit_code=0
  output="$(run_script "$head_oid" "$base_oid")" || exit_code=$?

  if [[ $exit_code -eq 0 ]] && echo "$output" | grep -q "WARNING"; then
    pass "Feature commits without evidence produce WARNING (exit 0)"
  else
    fail "Expected WARNING with exit 0, got exit ${exit_code}" "Output: $output"
  fi

  # Verify it lists the unreviewed commits
  if echo "$output" | grep -q "feat: add user authentication"; then
    pass "Output lists the unreviewed feat commit"
  else
    fail "Output should list the unreviewed feat commit" "Output: $output"
  fi

  teardown_test_repo
}

# =============================================================================
# Test 3: SKIP_REVIEW_GATE=1 bypasses and logs
# =============================================================================
test_skip_bypass_logs() {
  run_test "SKIP_REVIEW_GATE=1 bypasses and logs"
  setup_test_repo

  local base_oid
  base_oid="$(git rev-parse HEAD)"

  add_commit "feat: dangerous feature without review"

  local head_oid
  head_oid="$(git rev-parse HEAD)"

  local repo_dir
  repo_dir="$(pwd)"

  local output exit_code=0
  output="$(SKIP_REVIEW_GATE=1 run_script "$head_oid" "$base_oid")" || exit_code=$?

  if [[ $exit_code -eq 0 ]]; then
    pass "SKIP_REVIEW_GATE=1 exits 0"
  else
    fail "Expected exit 0 with SKIP_REVIEW_GATE=1, got exit ${exit_code}" "Output: $output"
  fi

  if echo "$output" | grep -qi "bypass\|skip"; then
    pass "Output mentions bypass/skip"
  else
    fail "Output should mention bypass" "Output: $output"
  fi

  local bypass_log="${repo_dir}/logs/hooks/review-gate-bypass.jsonl"
  if [[ -f "$bypass_log" ]] && grep -q "bypass" "$bypass_log"; then
    pass "Bypass logged to review-gate-bypass.jsonl"
  else
    fail "Expected bypass log at ${bypass_log}" "File exists: $(test -f "$bypass_log" && echo yes || echo no)"
  fi

  teardown_test_repo
}

# =============================================================================
# Test 4: REVIEW_GATE_STRICT=1 with no evidence exits 1
# =============================================================================
test_strict_mode_blocks() {
  run_test "REVIEW_GATE_STRICT=1 with no evidence exits 1"
  setup_test_repo

  local base_oid
  base_oid="$(git rev-parse HEAD)"

  add_commit "feat: critical feature"

  local head_oid
  head_oid="$(git rev-parse HEAD)"

  local output exit_code=0
  output="$(REVIEW_GATE_STRICT=1 run_script "$head_oid" "$base_oid")" || exit_code=$?

  if [[ $exit_code -eq 1 ]]; then
    pass "REVIEW_GATE_STRICT=1 exits 1 (blocks push)"
  else
    fail "Expected exit 1 with REVIEW_GATE_STRICT=1, got exit ${exit_code}" "Output: $output"
  fi

  if echo "$output" | grep -q "BLOCKED"; then
    pass "Output mentions BLOCKED"
  else
    fail "Output should mention BLOCKED" "Output: $output"
  fi

  teardown_test_repo
}

# =============================================================================
# Test 5: Mixed commits (feat + docs) still warns about the feat one
# =============================================================================
test_mixed_commits_warn_feat() {
  run_test "Mixed commits (feat + docs) still warns about the feat one"
  setup_test_repo

  local base_oid
  base_oid="$(git rev-parse HEAD)"

  add_commit "docs: update changelog"
  add_commit "feat: implement search"
  add_commit "chore: lint fixes"

  local head_oid
  head_oid="$(git rev-parse HEAD)"

  local output exit_code=0
  output="$(run_script "$head_oid" "$base_oid")" || exit_code=$?

  if [[ $exit_code -eq 0 ]]; then
    pass "Mixed commits exit 0 (default warn mode)"
  else
    fail "Expected exit 0, got exit ${exit_code}" "Output: $output"
  fi

  if echo "$output" | grep -q "WARNING"; then
    pass "Output warns about unreviewed commits"
  else
    fail "Expected WARNING for the feat commit" "Output: $output"
  fi

  if echo "$output" | grep -q "feat: implement search"; then
    pass "Output specifically lists the feat commit"
  else
    fail "Should list 'feat: implement search'" "Output: $output"
  fi

  # Check summary counts
  if echo "$output" | grep -q "1 feature/fix"; then
    pass "Summary shows 1 feature/fix commit"
  else
    fail "Summary should show 1 feature/fix commit" "Output: $output"
  fi

  if echo "$output" | grep -q "2 chore/docs/sync"; then
    pass "Summary shows 2 chore/docs/sync commits"
  else
    fail "Summary should show 2 chore/docs/sync commits" "Output: $output"
  fi

  teardown_test_repo
}

# =============================================================================
# Test 6: Feature commit WITH review evidence passes
# =============================================================================
test_path_based_low_risk_docs_commit_passes() {
  run_test "Feature-labeled docs-only commit is downgraded by path supplement"
  setup_test_repo

  local base_oid
  base_oid="$(git rev-parse HEAD)"

  mkdir -p docs
  echo "doc change" > docs/guide.md
  git add docs/guide.md
  git commit -q -m "feat: update docs guide"

  local head_oid
  head_oid="$(git rev-parse HEAD)"

  local output exit_code=0
  output="$(run_script "$head_oid" "$base_oid")" || exit_code=$?

  if [[ $exit_code -eq 0 ]] && echo "$output" | grep -q "PASS"; then
    pass "Docs-only feat commit passes via path supplement"
  else
    fail "Expected PASS for docs-only feat commit, got exit ${exit_code}" "Output: $output"
  fi

  teardown_test_repo
}

# =============================================================================
# Test 7: latency log is written
# =============================================================================
test_latency_log_written() {
  run_test "Latency log written for review gate runs"
  setup_test_repo

  local base_oid
  base_oid="$(git rev-parse HEAD)"
  add_commit "feat: latency check"
  local head_oid
  head_oid="$(git rev-parse HEAD)"
  local repo_dir
  repo_dir="$(pwd)"

  local output exit_code=0
  output="$(run_script "$head_oid" "$base_oid")" || exit_code=$?

  local latency_log="${repo_dir}/logs/hooks/review-gate-latency.jsonl"
  if [[ -f "$latency_log" ]] && grep -q 'latency_ms' "$latency_log"; then
    pass "Latency log created with latency_ms"
  else
    fail "Expected latency log at ${latency_log}" "Output: $output"
  fi

  teardown_test_repo
}

# =============================================================================
# Test 8: Feature commit WITH review evidence passes
# =============================================================================
test_feature_with_evidence_passes() {
  run_test "Feature commit with git review evidence passes"
  setup_test_repo

  local base_oid
  base_oid="$(git rev-parse HEAD)"

  # Add a review-evidence commit first
  add_commit "chore: codex adversarial review completed"
  add_commit "feat: add payment processing"

  local head_oid
  head_oid="$(git rev-parse HEAD)"

  local output exit_code=0
  output="$(run_script "$head_oid" "$base_oid")" || exit_code=$?

  if [[ $exit_code -eq 0 ]] && echo "$output" | grep -q "PASS"; then
    pass "Feature commit with review evidence passes"
  else
    fail "Expected PASS with review evidence, got exit ${exit_code}" "Output: $output"
  fi

  teardown_test_repo
}

# =============================================================================
# Run all tests
# =============================================================================
main() {
  echo "========================================"
  echo "Tests for require-review-on-push.sh"
  echo "========================================"

  if [[ ! -f "$SCRIPT_UNDER_TEST" ]]; then
    echo "ERROR: Script under test not found at: $SCRIPT_UNDER_TEST"
    echo "Run from scripts/enforcement/tests/ directory."
    exit 1
  fi

  test_docs_only_pass
  test_feature_no_evidence_warns
  test_skip_bypass_logs
  test_strict_mode_blocks
  test_mixed_commits_warn_feat
  test_path_based_low_risk_docs_commit_passes
  test_latency_log_written
  test_feature_with_evidence_passes

  echo ""
  echo "========================================"
  echo "Results: ${TESTS_RUN} tests, ${TESTS_PASSED} passed, ${TESTS_FAILED} failed"
  echo "========================================"

  if [[ $TESTS_FAILED -gt 0 ]]; then
    exit 1
  fi
  exit 0
}

main "$@"
