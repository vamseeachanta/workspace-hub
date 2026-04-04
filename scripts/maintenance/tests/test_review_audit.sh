#!/usr/bin/env bash
# ABOUTME: Test suite for review-audit.sh — validates commit classification, compliance, and JSON output.
# Run: bash scripts/maintenance/tests/test_review_audit.sh

set -uo pipefail

# ── Test Framework ────────────────────────────────────────────────────────────
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

pass() {
    TESTS_PASSED=$((TESTS_PASSED + 1))
    TESTS_RUN=$((TESTS_RUN + 1))
    echo "  PASS: $1"
}

fail() {
    TESTS_FAILED=$((TESTS_FAILED + 1))
    TESTS_RUN=$((TESTS_RUN + 1))
    echo "  FAIL: $1"
    [[ -n "${2:-}" ]] && echo "        $2"
}

assert_eq() {
    local expected="$1" actual="$2" label="$3"
    if [[ "$expected" == "$actual" ]]; then
        pass "$label"
    else
        fail "$label" "expected='$expected' actual='$actual'"
    fi
}

assert_contains() {
    local haystack="$1" needle="$2" label="$3"
    if echo "$haystack" | grep -qF "$needle"; then
        pass "$label"
    else
        fail "$label" "output does not contain '$needle'"
    fi
}

assert_not_contains() {
    local haystack="$1" needle="$2" label="$3"
    if echo "$haystack" | grep -qF "$needle"; then
        fail "$label" "output unexpectedly contains '$needle'"
    else
        pass "$label"
    fi
}

# ── Setup ─────────────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# If run from the tests/ directory, adjust
if [[ "$(basename "$SCRIPT_DIR")" == "tests" ]]; then
    AUDIT_SCRIPT="$SCRIPT_DIR/../review-audit.sh"
else
    AUDIT_SCRIPT="$SCRIPT_DIR/review-audit.sh"
fi

# Verify the script exists
if [[ ! -f "$AUDIT_SCRIPT" ]]; then
    echo "ERROR: review-audit.sh not found at $AUDIT_SCRIPT" >&2
    echo "Trying fallback paths..."
    REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo /mnt/local-analysis/workspace-hub)"
    AUDIT_SCRIPT="$REPO_ROOT/scripts/maintenance/review-audit.sh"
    if [[ ! -f "$AUDIT_SCRIPT" ]]; then
        echo "ERROR: Cannot find review-audit.sh" >&2
        exit 1
    fi
fi

echo "Testing: $AUDIT_SCRIPT"
echo ""

# Create a temporary test repo for isolated testing
TEST_DIR="$(mktemp -d)"
trap 'rm -rf "$TEST_DIR"' EXIT

setup_test_repo() {
    local repo_dir="$TEST_DIR/repo-$$-$RANDOM"
    mkdir -p "$repo_dir"
    cd "$repo_dir"
    git init -q
    git config user.email "test@test.com"
    git config user.name "Test"
    # Create required directories
    mkdir -p scripts/review/results
    mkdir -p scripts/maintenance
    mkdir -p .planning/phases/01-init
    mkdir -p .planning/quick
    mkdir -p .claude/reports
    mkdir -p logs/maintenance
    # Initial commit (outside audit window)
    echo "init" > README.md
    git add -A
    GIT_COMMITTER_DATE="2020-01-01 00:00:00" git commit -q -m "chore: initial commit" --date="2020-01-01 00:00:00"
    # Copy the audit script into the test repo
    cp "$AUDIT_SCRIPT" scripts/maintenance/review-audit.sh
    chmod +x scripts/maintenance/review-audit.sh
    echo "$repo_dir"
}

# ── Test 1: Zero commits produces 100% compliance ────────────────────────────
echo "Test 1: Zero commits in audit window => 100% compliance"

REPO1="$(setup_test_repo)"
cd "$REPO1"

# The initial commit is dated 2020, so with AUDIT_HOURS=1 there are zero recent commits
OUTPUT="$(AUDIT_HOURS=1 DRY_RUN=true bash scripts/maintenance/review-audit.sh 2>&1)"

assert_contains "$OUTPUT" "Compliance:           100%" "compliance is 100%"
assert_contains "$OUTPUT" "Total commits:        0" "zero total commits"
assert_contains "$OUTPUT" "PASS" "reports PASS"
assert_not_contains "$OUTPUT" "Would create GitHub issue" "no issue created"

# Check JSON output
JSON_FILE="$(find logs/maintenance -name 'review-audit-*.json' | head -1)"
if [[ -n "$JSON_FILE" && -f "$JSON_FILE" ]]; then
    # Validate JSON structure (basic check without jq)
    if uv run --no-project python -c "import json,sys; json.load(open(sys.argv[1]))" "$JSON_FILE" 2>/dev/null; then
        pass "JSON output is valid"
    elif uv run --no-project python -c "import json,sys; json.load(sys.stdin)" < "$JSON_FILE" 2>/dev/null; then
        pass "JSON output is valid (stdin)"
    else
        fail "JSON output is valid" "JSON parse error in $JSON_FILE"
    fi
else
    fail "JSON output exists" "no JSON file found in logs/maintenance/"
fi

echo ""

# ── Test 2: All-docs commits produces 100% compliance ────────────────────────
echo "Test 2: All docs/chore commits => 100% compliance"

REPO2="$(setup_test_repo)"
cd "$REPO2"

# Add several chore/docs commits
echo "doc1" > docs_file.md
git add -A && git commit -q -m "docs: update readme"
echo "doc2" >> docs_file.md
git add -A && git commit -q -m "chore: cleanup formatting"
echo "doc3" >> docs_file.md
git add -A && git commit -q -m "ci: update pipeline"
echo "doc4" >> docs_file.md
git add -A && git commit -q -m "style: fix whitespace"

OUTPUT="$(AUDIT_HOURS=1 DRY_RUN=true bash scripts/maintenance/review-audit.sh 2>&1)"

assert_contains "$OUTPUT" "Compliance:           100%" "all docs/chore => 100% compliance"
assert_contains "$OUTPUT" "Chore/docs commits:" "chore/docs count shown"
assert_not_contains "$OUTPUT" "Would create GitHub issue" "no issue for docs-only"

# Verify feature/fix count is 0
assert_contains "$OUTPUT" "Feature/fix commits:  0" "zero feature/fix commits"

echo ""

# ── Test 3: Feature commits without evidence => below threshold ───────────────
echo "Test 3: Feature commits without review evidence => below threshold"

REPO3="$(setup_test_repo)"
cd "$REPO3"

# Add feature commits without any review evidence
echo "feat1" > feature.py
git add -A && git commit -q -m "feat: add user authentication"
echo "feat2" >> feature.py
git add -A && git commit -q -m "fix: resolve login crash"
echo "feat3" >> feature.py
git add -A && git commit -q -m "feat(api): add rate limiting"
echo "feat4" >> feature.py
git add -A && git commit -q -m "perf: optimize database queries"
echo "feat5" >> feature.py
git add -A && git commit -q -m "add new payment integration"

OUTPUT="$(AUDIT_HOURS=1 DRY_RUN=true REVIEW_COMPLIANCE_THRESHOLD=80 bash scripts/maintenance/review-audit.sh 2>&1)"

assert_contains "$OUTPUT" "FAIL" "reports FAIL for unreviewed features"
assert_contains "$OUTPUT" "Would create GitHub issue" "would create issue in dry-run"
assert_contains "$OUTPUT" "Review backlog:" "issue title includes backlog count"
assert_contains "$OUTPUT" "Unreviewed commits:" "lists unreviewed commits"

# Compliance should be 0% (no evidence for any commit)
assert_contains "$OUTPUT" "Compliance:           0%" "compliance is 0%"

echo ""

# ── Test 4: Feature commits WITH review keywords in message => pass ───────────
echo "Test 4: Feature commits with review keywords => counts as reviewed"

REPO4="$(setup_test_repo)"
cd "$REPO4"

echo "f1" > feature.py
git add -A && git commit -q -m "feat: add auth - reviewed by codex"
echo "f2" >> feature.py
git add -A && git commit -q -m "fix: login - gemini adversarial review passed"

OUTPUT="$(AUDIT_HOURS=1 DRY_RUN=true bash scripts/maintenance/review-audit.sh 2>&1)"

assert_contains "$OUTPUT" "Compliance:           100%" "keyword evidence gives 100%"
assert_contains "$OUTPUT" "Reviewed:             2" "both commits counted as reviewed"
assert_contains "$OUTPUT" "PASS" "reports PASS"

echo ""

# ── Test 5: Custom AUDIT_HOURS works ─────────────────────────────────────────
echo "Test 5: Custom AUDIT_HOURS controls window size"

REPO5="$(setup_test_repo)"
cd "$REPO5"

# Create a commit now
echo "recent" > feature.py
git add -A && git commit -q -m "feat: new feature"

# With AUDIT_HOURS=0 (effectively), we should see no commits
# Use a very small window - commits just made should still appear with AUDIT_HOURS=1
OUTPUT_1H="$(AUDIT_HOURS=1 DRY_RUN=true bash scripts/maintenance/review-audit.sh 2>&1)"
assert_contains "$OUTPUT_1H" "Feature/fix commits:  1" "AUDIT_HOURS=1 finds recent commit"
assert_contains "$OUTPUT_1H" "Audit window: last 1 hours" "reports correct audit window"

# With AUDIT_HOURS=48, also finds it
OUTPUT_48H="$(AUDIT_HOURS=48 DRY_RUN=true bash scripts/maintenance/review-audit.sh 2>&1)"
assert_contains "$OUTPUT_48H" "Audit window: last 48 hours" "AUDIT_HOURS=48 shown in output"

echo ""

# ── Test 6: JSON output is valid and complete ─────────────────────────────────
echo "Test 6: JSON output validity and completeness"

REPO6="$(setup_test_repo)"
cd "$REPO6"

echo "f" > feature.py
git add -A && git commit -q -m "feat: something new"

AUDIT_HOURS=1 DRY_RUN=true bash scripts/maintenance/review-audit.sh > /dev/null 2>&1

JSON_FILE="$(find logs/maintenance -name 'review-audit-*.json' | head -1)"
if [[ -n "$JSON_FILE" && -f "$JSON_FILE" ]]; then
    # Validate JSON with Python
    if uv run --no-project python - "$JSON_FILE" <<'PY' 2>&1; then
import json, sys
with open(sys.argv[1]) as f:
    data = json.load(f)
# Check required fields
required = ['date', 'audit_hours', 'total_commits', 'feature_fix_commits',
            'chore_doc_commits', 'reviewed_commits', 'unreviewed_commits',
            'compliance_percent', 'threshold_percent', 'pass', 'unreviewed']
missing = [k for k in required if k not in data]
if missing:
    print(f'Missing fields: {missing}', file=sys.stderr)
    sys.exit(1)
# Validate types
assert isinstance(data['total_commits'], int), 'total_commits not int'
assert isinstance(data['compliance_percent'], int), 'compliance_percent not int'
assert isinstance(data['pass'], bool), 'pass not bool'
assert isinstance(data['unreviewed'], list), 'unreviewed not list'
print('All fields present and valid')
PY
then
        pass "JSON has all required fields with correct types"
    else
        fail "JSON has all required fields with correct types" "validation failed"
    fi

    # Check unreviewed entries have hash and message
    if uv run --no-project python - "$JSON_FILE" <<'PY' 2>&1; then
import json, sys
with open(sys.argv[1]) as f:
    data = json.load(f)
for entry in data.get('unreviewed', []):
    assert 'hash' in entry, f'missing hash in {entry}'
    assert 'message' in entry, f'missing message in {entry}'
print('Unreviewed entries valid')
PY
then
        pass "JSON unreviewed entries have hash and message"
    else
        fail "JSON unreviewed entries have hash and message"
    fi
else
    fail "JSON output exists for completeness check" "file not found"
    fail "JSON unreviewed entries" "skipped - no JSON file"
fi

echo ""

# ── Test 7: Mixed commits — partial compliance ───────────────────────────────
echo "Test 7: Mixed commits — partial compliance calculation"

REPO7="$(setup_test_repo)"
cd "$REPO7"

# 2 feature commits: 1 with review keyword, 1 without
echo "f1" > feature.py
git add -A && git commit -q -m "feat: add auth - codex reviewed"
echo "f2" >> feature.py
git add -A && git commit -q -m "feat: add payments"
# 1 chore commit
echo "c1" > notes.md
git add -A && git commit -q -m "chore: update deps"

OUTPUT="$(AUDIT_HOURS=1 DRY_RUN=true bash scripts/maintenance/review-audit.sh 2>&1)"

assert_contains "$OUTPUT" "Feature/fix commits:  2" "2 feature/fix detected"
assert_contains "$OUTPUT" "Reviewed:             1" "1 reviewed"
assert_contains "$OUTPUT" "Unreviewed:           1" "1 unreviewed"
assert_contains "$OUTPUT" "Compliance:           50%" "50% compliance"

echo ""

# ── Test 8: Commit classification edge cases ──────────────────────────────────
echo "Test 8: Commit classification edge cases"

REPO8="$(setup_test_repo)"
cd "$REPO8"

# These should all be classified as chore/docs (no review needed)
echo "1" > f.txt; git add -A; git commit -q -m "docs: update changelog"
echo "2" >> f.txt; git add -A; git commit -q -m "chore(deps): bump version"
echo "3" >> f.txt; git add -A; git commit -q -m "ci: fix workflow"
echo "4" >> f.txt; git add -A; git commit -q -m "test: add unit tests"
echo "5" >> f.txt; git add -A; git commit -q -m "style: fix linting"
echo "6" >> f.txt; git add -A; git commit -q -m "build: update config"
echo "7" >> f.txt; git add -A; git commit -q -m "Merge branch 'feature' into main"
echo "8" >> f.txt; git add -A; git commit -q -m "revert: undo last change"

OUTPUT="$(AUDIT_HOURS=1 DRY_RUN=true bash scripts/maintenance/review-audit.sh 2>&1)"

assert_contains "$OUTPUT" "Feature/fix commits:  0" "all edge cases classified as chore/docs"
assert_contains "$OUTPUT" "Compliance:           100%" "100% compliance for all chore/docs"

echo ""

# ── Results ───────────────────────────────────────────────────────────────────
echo "============================================"
echo "Results: $TESTS_PASSED/$TESTS_RUN passed, $TESTS_FAILED failed"
echo "============================================"

if [[ "$TESTS_FAILED" -gt 0 ]]; then
    exit 1
fi
exit 0
