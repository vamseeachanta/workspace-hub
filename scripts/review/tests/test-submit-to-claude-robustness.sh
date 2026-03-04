#!/usr/bin/env bash
# test-submit-to-claude-robustness.sh
# Deterministic regression tests for submit-to-claude.sh.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REVIEW_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SUBMIT_SCRIPT="${REVIEW_DIR}/submit-to-claude.sh"

PASS=0
FAIL=0
TOTAL=0
TEST_DIR="$(mktemp -d)"
trap 'rm -rf "$TEST_DIR"' EXIT

assert_status() {
  local label="$1" expected="$2" actual="$3"
  TOTAL=$((TOTAL + 1))
  if [[ "$expected" == "$actual" ]]; then
    echo "  PASS: $label"
    PASS=$((PASS + 1))
  else
    echo "  FAIL: $label (expected=$expected got=$actual)"
    FAIL=$((FAIL + 1))
  fi
}

assert_contains() {
  local label="$1" file="$2" pattern="$3"
  TOTAL=$((TOTAL + 1))
  if grep -qE "$pattern" "$file"; then
    echo "  PASS: $label"
    PASS=$((PASS + 1))
  else
    echo "  FAIL: $label (pattern not found: $pattern)"
    FAIL=$((FAIL + 1))
  fi
}

echo "Test group: Argument parsing"
out="$TEST_DIR/out.txt"
err="$TEST_DIR/err.txt"

rc=0
"$SUBMIT_SCRIPT" --file >"$out" 2>"$err" || rc=$?
assert_status "Missing file value fails" "1" "$rc"
assert_contains "Missing file message" "$err" "ERROR: --file requires a value"

rc=0
"$SUBMIT_SCRIPT" --commit >"$out" 2>"$err" || rc=$?
assert_status "Missing commit value fails" "1" "$rc"
assert_contains "Missing commit message" "$err" "ERROR: --commit requires a value"

echo "Test group: DNS Fallback Path"
# Create a dummy getent that fails
dummy_getent="$TEST_DIR/getent"
echo '#!/usr/bin/env bash' > "$dummy_getent"
echo 'exit 1' >> "$dummy_getent"
chmod +x "$dummy_getent"

export PATH="$TEST_DIR:$PATH"

# Give a fake file to run the script against
dummy_file="$TEST_DIR/dummy.txt"
echo "data" > "$dummy_file"

rc=0
"$SUBMIT_SCRIPT" --file "$dummy_file" --prompt "test" >"$out" 2>"$err" || rc=$?
assert_status "DNS failure exits 3" "3" "$rc"
assert_contains "DNS failure message in stderr" "$err" "WARN: DNS resolution failed"

echo ""
echo "Results: $PASS/$TOTAL passed; $FAIL failed"
[[ "$FAIL" -eq 0 ]]
