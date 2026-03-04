#!/usr/bin/env bash
# test-cross-review-path-sanitization.sh
# Verifies git-range source names with slashes are sanitized for result file paths.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REVIEW_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
CROSS_REVIEW="${REVIEW_DIR}/cross-review.sh"
RESULTS_DIR="${REVIEW_DIR}/results"
TEST_DIR="$(mktemp -d)"
trap 'rm -rf "$TEST_DIR"' EXIT

PASS=0
FAIL=0
TOTAL=0

assert_true() {
  local label="$1"
  shift
  TOTAL=$((TOTAL + 1))
  if "$@"; then
    echo "  PASS: $label"
    PASS=$((PASS + 1))
  else
    echo "  FAIL: $label"
    FAIL=$((FAIL + 1))
  fi
}

MOCK_CLAUDE="$TEST_DIR/claude"
cat > "$MOCK_CLAUDE" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
cat <<'JSON'
{"verdict":"APPROVE","summary":"ok","issues_found":[],"suggestions":[],"questions_for_author":[]}
JSON
EOF
chmod +x "$MOCK_CLAUDE"

before_list="$TEST_DIR/before.txt"
after_list="$TEST_DIR/after.txt"
ls -1 "$RESULTS_DIR" | sort > "$before_list"

# Use real git-range mode (contains slash in branch name) to exercise SOURCE_NAME sanitization.
range_like='HEAD..origin/main'
PATH="$TEST_DIR:$PATH" \
CLAUDE_TIMEOUT_SECONDS=2 \
CLAUDE_RETRIES=1 \
CLAUDE_BIN="$MOCK_CLAUDE" \
"$CROSS_REVIEW" "$range_like" claude --type implementation >/dev/null 2>&1 || true

ls -1 "$RESULTS_DIR" | sort > "$after_list"
new_files="$TEST_DIR/new.txt"
comm -13 "$before_list" "$after_list" > "$new_files"

assert_true "new claude result file created" grep -qE 'implementation-claude\.md$' "$new_files"
assert_true "no nested path segments in new filenames" bash -c '! grep -q "/" "$1"' _ "$new_files"
assert_true "sanitized git-diff prefix used" grep -q 'git-diff-' "$new_files"
assert_true "slash from branch name sanitized to dash" grep -q 'origin-main' "$new_files"

echo ""
echo "Results: $PASS/$TOTAL passed; $FAIL failed"
[[ "$FAIL" -eq 0 ]]
