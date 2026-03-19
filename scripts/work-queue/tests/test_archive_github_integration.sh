#!/usr/bin/env bash
# Test that archive-item.sh contains the GitHub Issue integration
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
SCRIPT="${REPO_ROOT}/scripts/work-queue/archive-item.sh"
FAILURES=0

# Test 1: Script contains issue close call
if grep -q "update-github-issue.py" "$SCRIPT" && grep -q "\-\-close" "$SCRIPT"; then
  echo "PASS: issue close found"
else
  echo "FAIL: issue close not found"
  FAILURES=$((FAILURES + 1))
fi

# Test 2: Script contains future-work issue creation
if grep -q "future-work.yaml" "$SCRIPT"; then
  echo "PASS: future-work parsing found"
else
  echo "FAIL: future-work parsing not found"
  FAILURES=$((FAILURES + 1))
fi

# Test 3: Close call is non-blocking (|| true)
if grep "\\-\\-close" "$SCRIPT" | grep -q "|| true"; then
  echo "PASS: close is non-blocking"
else
  echo "FAIL: close may block"
  FAILURES=$((FAILURES + 1))
fi

# Test 4: Future-work block is non-blocking (|| true)
if grep -A30 "future-work.yaml" "$SCRIPT" | grep -q "|| true"; then
  echo "PASS: future-work creation is non-blocking"
else
  echo "FAIL: future-work creation may block"
  FAILURES=$((FAILURES + 1))
fi

# Test 5: Category extraction exists
if grep -q 'CATEGORY=.*category:' "$SCRIPT"; then
  echo "PASS: category extraction found"
else
  echo "FAIL: category extraction not found"
  FAILURES=$((FAILURES + 1))
fi

echo ""
echo "All archive GitHub integration tests complete (${FAILURES} failure(s))"
exit "$FAILURES"
