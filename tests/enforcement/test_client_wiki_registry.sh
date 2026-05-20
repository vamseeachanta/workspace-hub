#!/usr/bin/env bash
# tests/enforcement/test_client_wiki_registry.sh
# TDD test suite for scripts/enforcement/check-client-wiki-registry.sh
# (Created in T3 of workspace-hub#2746 — RED phase: checker does not exist yet.)
#
# Covers tests 1-8 of the TDD list in
# docs/plans/2026-05-20-issue-2746-llm-wiki-acma.md §TDD Test List.
#
# Test 9 (template-instantiation LICENSE grep) lives elsewhere — see
# r2-codex review finding #4: that test runs post-T6 against an instantiated
# wiki repo on disk, not against the registry checker. Intentionally excluded
# from this file.
#
# Each test loads a per-test fixture YAML via the REGISTRY_PATH env override
# so the live config/client-wikis.yml is never touched.
#
# Usage:
#   bash tests/enforcement/test_client_wiki_registry.sh
#
# Exit code: number of failing tests (0 = all pass).

set -uo pipefail   # NOT errexit — we want to capture exit codes from the checker

REPO_ROOT="$(git rev-parse --show-toplevel)"
CHECKER="${REPO_ROOT}/scripts/enforcement/check-client-wiki-registry.sh"
FIXTURE_DIR="${REPO_ROOT}/tests/enforcement/fixtures"
PASS=0
FAIL=0

run_test() {
  local name="$1" fixture="$2" expected_exit="$3" extra_check="${4:-}"
  echo -n "  test_${name}... "
  if [[ ! -x "$CHECKER" ]]; then
    echo "SKIP (no checker yet — TDD RED expected)"
    FAIL=$((FAIL + 1))
    return
  fi
  local err rc
  err=$(REGISTRY_PATH="$FIXTURE_DIR/$fixture" "$CHECKER" 2>&1 >/dev/null)
  rc=$?
  if [[ "$expected_exit" == "0" && $rc -eq 0 ]] || [[ "$expected_exit" == "nonzero" && $rc -ne 0 ]]; then
    if [[ -n "$extra_check" ]] && ! echo "$err" | grep -qE "$extra_check"; then
      echo "FAIL (exit $rc OK but stderr missing pattern: $extra_check)"
      FAIL=$((FAIL + 1))
    else
      echo "PASS"
      PASS=$((PASS + 1))
    fi
  else
    echo "FAIL (expected exit $expected_exit, got $rc)"
    FAIL=$((FAIL + 1))
  fi
}

echo "=== client-wiki-registry checker test suite ==="
run_test "01_consistent_registry_passes"  "client-wikis-consistent.yml"           "0"
run_test "02_missing_repo_field_fails"    "client-wikis-missing-repo-field.yml"   "nonzero" "missing-repo-row|repo"
run_test "03_fake_gh_repo_fails"          "client-wikis-fake-repo.yml"            "nonzero" "not found on GH|nonexistent-fake-repo"
run_test "04_wrong_visibility_fails"      "client-wikis-wrong-visibility.yml"     "nonzero" "visibility|PRIVATE"
run_test "05_missing_clone_fails"         "client-wikis-missing-clone.yml"        "nonzero" "clone.*missing|not a git repo"
run_test "06_missing_mount_skips"         "client-wikis-missing-mount.yml"        "0"
run_test "07_duplicate_shortname_fails"   "client-wikis-duplicate-shortname.yml"  "nonzero" "duplicate"
run_test "08_firewall_guard_fails"        "client-wikis-firewall-violation.yml"   "nonzero" "firewall|public.*llm-wiki|raw_roots.*overlap"

echo "=== Total: $PASS pass / $FAIL fail ==="
exit $FAIL
