#!/usr/bin/env bash
# Test suite for scripts/release/cut-release.sh and generate-changelog.sh
# Plain bash assertions — run directly: bash test-cut-release.sh
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORKSPACE_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
CUT_RELEASE="$WORKSPACE_ROOT/scripts/release/cut-release.sh"
GEN_CHANGELOG="$WORKSPACE_ROOT/scripts/release/generate-changelog.sh"

PASS=0
FAIL=0

# ---------------------------------------------------------------------------
# Assertion helpers
# ---------------------------------------------------------------------------

assert_exit() {
    local test_name="$1"
    local expected_exit="$2"
    shift 2
    local actual_exit=0
    "$@" >/dev/null 2>&1 || actual_exit=$?
    if [[ "$actual_exit" -eq "$expected_exit" ]]; then
        echo "PASS: $test_name"
        (( PASS++ )) || true
    else
        echo "FAIL: $test_name — expected exit $expected_exit, got $actual_exit"
        (( FAIL++ )) || true
    fi
}

assert_contains() {
    local test_name="$1"
    local haystack="$2"
    local needle="$3"
    if [[ "$haystack" == *"$needle"* ]]; then
        echo "PASS: $test_name"
        (( PASS++ )) || true
    else
        echo "FAIL: $test_name — expected to contain: '$needle'"
        echo "      actual output: '$haystack'"
        (( FAIL++ )) || true
    fi
}

assert_file_unchanged() {
    local test_name="$1"
    local file="$2"
    local before_sum="$3"
    local after_sum
    after_sum=$(md5sum "$file" 2>/dev/null | cut -d' ' -f1 || echo "missing")
    if [[ "$before_sum" == "$after_sum" ]]; then
        echo "PASS: $test_name"
        (( PASS++ )) || true
    else
        echo "FAIL: $test_name — file was modified: $file"
        (( FAIL++ )) || true
    fi
}

# ---------------------------------------------------------------------------
# Test 1: dry-run exits 0 and does not modify files
# ---------------------------------------------------------------------------
pyproject_before=$(md5sum "$WORKSPACE_ROOT/assetutilities/pyproject.toml" | cut -d' ' -f1)
manifest_before=$(md5sum "$WORKSPACE_ROOT/config/releases/release-manifest.yaml" | cut -d' ' -f1)

dry_run_exit=0
bash "$CUT_RELEASE" assetutilities 0.1.1 --dry-run >/dev/null 2>&1 || dry_run_exit=$?

if [[ "$dry_run_exit" -eq 0 ]]; then
    echo "PASS: test1_dry_run_exits_0"
    (( PASS++ )) || true
else
    echo "FAIL: test1_dry_run_exits_0 — exit $dry_run_exit"
    (( FAIL++ )) || true
fi

assert_file_unchanged "test1_dry_run_pyproject_unchanged" \
    "$WORKSPACE_ROOT/assetutilities/pyproject.toml" "$pyproject_before"
assert_file_unchanged "test1_dry_run_manifest_unchanged" \
    "$WORKSPACE_ROOT/config/releases/release-manifest.yaml" "$manifest_before"

# ---------------------------------------------------------------------------
# Test 2: bad repo exits 1, stderr contains "Unknown repo"
# ---------------------------------------------------------------------------
stderr_t2=$(bash "$CUT_RELEASE" badrepo 0.1.1 2>&1 >/dev/null || true)
exit_t2=0
bash "$CUT_RELEASE" badrepo 0.1.1 >/dev/null 2>/dev/null || exit_t2=$?

if [[ "$exit_t2" -eq 1 ]]; then
    echo "PASS: test2_bad_repo_exits_1"
    (( PASS++ )) || true
else
    echo "FAIL: test2_bad_repo_exits_1 — exit $exit_t2"
    (( FAIL++ )) || true
fi
assert_contains "test2_bad_repo_stderr_unknown_repo" "$stderr_t2" "Unknown repo"

# ---------------------------------------------------------------------------
# Test 3: invalid semver exits 1, stderr contains "Invalid semver"
# ---------------------------------------------------------------------------
stderr_t3=$(bash "$CUT_RELEASE" assetutilities 1.2 2>&1 >/dev/null || true)
exit_t3=0
bash "$CUT_RELEASE" assetutilities 1.2 >/dev/null 2>/dev/null || exit_t3=$?

if [[ "$exit_t3" -eq 1 ]]; then
    echo "PASS: test3_invalid_semver_exits_1"
    (( PASS++ )) || true
else
    echo "FAIL: test3_invalid_semver_exits_1 — exit $exit_t3"
    (( FAIL++ )) || true
fi
assert_contains "test3_invalid_semver_stderr" "$stderr_t3" "Invalid semver"

# ---------------------------------------------------------------------------
# Tests 4 & 5: generate-changelog.sh — use isolated temp git repos
# ---------------------------------------------------------------------------
tmpdir=$(mktemp -d)
trap 'rm -rf "$tmpdir"' EXIT

git init "$tmpdir" -q
git -C "$tmpdir" config user.email "test@test.com"
git -C "$tmpdir" config user.name "Test"
touch "$tmpdir/file.txt"
git -C "$tmpdir" add .
git -C "$tmpdir" commit -q -m "chore: initial"
first_commit=$(git -C "$tmpdir" rev-parse HEAD)

# Test 4: no commits since first_commit (range is empty HEAD..HEAD)
output_t4=$(bash "$GEN_CHANGELOG" "$tmpdir" "1.0.0" "$first_commit" 2>&1 || true)
assert_contains "test4_no_commits_no_notable_changes" "$output_t4" "(no notable changes)"

# Test 5: feat + fix commits
git -C "$tmpdir" commit -q --allow-empty -m "feat: add new feature"
git -C "$tmpdir" commit -q --allow-empty -m "fix: fix a bug"

output_t5=$(bash "$GEN_CHANGELOG" "$tmpdir" "1.0.0" "$first_commit" 2>&1 || true)
assert_contains "test5_feat_fix_features_section"  "$output_t5" "### Features"
assert_contains "test5_feat_fix_bugfixes_section"  "$output_t5" "### Bug Fixes"

# ---------------------------------------------------------------------------
# Test 6: integration smoke-test — dry-run output mentions repo and version
# ---------------------------------------------------------------------------
dry_run_output=$(bash "$CUT_RELEASE" assetutilities 9.9.9 --dry-run 2>&1 || true)
assert_contains "test6_dryrun_mentions_repo"    "$dry_run_output" "assetutilities"
assert_contains "test6_dryrun_mentions_version" "$dry_run_output" "9.9.9"

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo ""
echo "Results: $PASS passed, $FAIL failed"
if [[ "$FAIL" -gt 0 ]]; then
    exit 1
fi
exit 0
