#!/usr/bin/env bash
# test-submit-to-gemini-robustness.sh
# Comprehensive tests for submit-to-gemini.sh edge cases.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel)"
SUBMIT_SCRIPT="${REPO_ROOT}/scripts/review/submit-to-gemini.sh"

echo "=== Testing submit-to-gemini.sh ==="

fails=0
passes=0

assert_fail() {
  local name="$1"
  shift
  echo -n "Test: $name... "
  if "$@" >/dev/null 2>&1; then
    echo "FAIL (Expected non-zero exit code, got 0)"
    fails=$((fails + 1))
  else
    echo "PASS"
    passes=$((passes + 1))
  fi
}

assert_success() {
  local name="$1"
  shift
  echo -n "Test: $name... "
  if "$@" >/dev/null 2>&1; then
    echo "PASS"
    passes=$((passes + 1))
  else
    echo "FAIL (Expected 0 exit code, got non-zero)"
    fails=$((fails + 1))
  fi
}

# 1. Missing arguments
assert_fail "Missing --file or --commit" "$SUBMIT_SCRIPT"
assert_fail "Empty --file" "$SUBMIT_SCRIPT" --file ""
assert_fail "Empty --commit" "$SUBMIT_SCRIPT" --commit ""

# 2. Invalid inputs
assert_fail "Non-existent file" "$SUBMIT_SCRIPT" --file "/tmp/does-not-exist-12345"
assert_fail "Invalid commit SHA format" "$SUBMIT_SCRIPT" --commit "invalid-sha"
assert_fail "Valid format but non-existent commit SHA" "$SUBMIT_SCRIPT" --commit "1111111111111111111111111111111111111111"

# 3. Simple functional test (with real Gemini CLI if installed)
if command -v gemini &>/dev/null; then
  dummy_file="$(mktemp)"
  echo "console.log('hello world');" > "$dummy_file"
  
  # Run a real but tiny request
  echo -n "Test: Simple real file (Integration)... "
  output_file="$(mktemp)"
  if "$SUBMIT_SCRIPT" --file "$dummy_file" --prompt "Review this code." > "$output_file" 2>/dev/null; then
    if grep -q '### Verdict:' "$output_file"; then
      echo "PASS"
      passes=$((passes + 1))
    else
      echo "FAIL (Did not output rendered Markdown with Verdict)"
      fails=$((fails + 1))
      cat "$output_file"
    fi
  else
    echo "FAIL (Command returned non-zero)"
    fails=$((fails + 1))
  fi
  rm -f "$dummy_file" "$output_file"
else
  echo "Test: Simple real file (Integration)... SKIPPED (gemini CLI not found)"
fi

# 4. Large file test
if command -v gemini &>/dev/null; then
  large_file="${REPO_ROOT}/.claude/work-queue/assets/WRK-624/workflow-governance-review.html"
  if [[ -f "$large_file" ]]; then
    echo -n "Test: Large file (WRK-624 workflow-governance-review.html)... "
    output_file="$(mktemp)"
    # Using strict cross-reviewer prompt
    PROMPT="You are a strict cross-reviewer. Evaluate the provided document."
    if "$SUBMIT_SCRIPT" --file "$large_file" --prompt "$PROMPT" > "$output_file" 2>/dev/null; then
      if grep -q '### Verdict:' "$output_file"; then
        echo "PASS"
        passes=$((passes + 1))
      else
        echo "FAIL (Did not output rendered Markdown with Verdict)"
        fails=$((fails + 1))
        cat "$output_file"
      fi
    else
      echo "FAIL (Command returned non-zero)"
      fails=$((fails + 1))
    fi
    rm -f "$output_file"
  else
    echo "Test: Large file... SKIPPED (File not found: $large_file)"
  fi
fi

echo ""
echo "Results: $passes passed, $fails failed."
if [[ "$fails" -gt 0 ]]; then
  exit 1
fi
exit 0
