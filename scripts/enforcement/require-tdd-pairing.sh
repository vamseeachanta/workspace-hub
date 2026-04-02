#!/usr/bin/env bash
# require-tdd-pairing.sh — Gate: verify test files exist alongside implementation changes
# Enforcement Level 2 (script) per .claude/rules/patterns.md
# Issue: #1428
#
# Checks staged or recent commits for implementation file changes and warns
# if no corresponding test file was changed in the same commit/staging area.
#
# Usage:
#   bash scripts/enforcement/require-tdd-pairing.sh [--strict] [--staged]
#
# --strict: exit 1 on unpaired changes (blocks commit)
# --staged: check git staging area instead of last commit

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
STRICT_MODE=false
CHECK_STAGED=false

for arg in "$@"; do
  case "$arg" in
    --strict) STRICT_MODE=true ;;
    --staged) CHECK_STAGED=true ;;
  esac
done

# Get changed files
if $CHECK_STAGED; then
  CHANGED_FILES=$(git diff --cached --name-only 2>/dev/null || true)
else
  CHANGED_FILES=$(git diff --name-only HEAD~1..HEAD 2>/dev/null || true)
fi

if [[ -z "$CHANGED_FILES" ]]; then
  echo "[tdd-gate] No changed files detected."
  exit 0
fi

# Identify implementation files (Python, JS, TS — excluding tests, configs, docs)
IMPL_FILES=()
TEST_FILES=()

while IFS= read -r f; do
  # Skip non-code files
  case "$f" in
    *.md|*.json|*.yml|*.yaml|*.toml|*.cfg|*.ini|*.txt|*.csv|*.lock|*.sh) continue ;;
    *.png|*.jpg|*.svg|*.gif|*.ico) continue ;;
  esac

  # Classify as test or implementation
  if echo "$f" | grep -qE '(test_|_test\.|\.test\.|tests/|__tests__/|spec\.)'; then
    TEST_FILES+=("$f")
  elif echo "$f" | grep -qE '\.(py|js|ts|jsx|tsx)$'; then
    # Skip __init__.py, conftest.py, setup files
    case "$(basename "$f")" in
      __init__.py|conftest.py|setup.py|setup.cfg) continue ;;
    esac
    IMPL_FILES+=("$f")
  fi
done <<< "$CHANGED_FILES"

IMPL_COUNT=${#IMPL_FILES[@]}
TEST_COUNT=${#TEST_FILES[@]}

if [[ $IMPL_COUNT -eq 0 ]]; then
  echo "[tdd-gate] No implementation files changed. Gate passes."
  exit 0
fi

# Calculate pairing ratio
if [[ $TEST_COUNT -eq 0 ]]; then
  PAIRING_PCT=0
else
  PAIRING_PCT=$(( (TEST_COUNT * 100) / (IMPL_COUNT + TEST_COUNT) ))
fi

echo "[tdd-gate] Implementation files: $IMPL_COUNT | Test files: $TEST_COUNT | Pairing: ${PAIRING_PCT}%"

# Check for unpaired implementation files
UNPAIRED=()
for impl in "${IMPL_FILES[@]}"; do
  # Derive expected test file name patterns
  base=$(basename "$impl" | sed 's/\.[^.]*$//')
  dir=$(dirname "$impl")

  found=false
  for test in "${TEST_FILES[@]}"; do
    if echo "$test" | grep -qiE "(test_${base}|${base}_test|${base}\.test)"; then
      found=true
      break
    fi
  done

  if ! $found; then
    UNPAIRED+=("$impl")
  fi
done

if [[ ${#UNPAIRED[@]} -eq 0 ]]; then
  echo "[tdd-gate] All implementation files have test coverage. PASS"
  exit 0
fi

echo ""
echo "[tdd-gate] WARNING: ${#UNPAIRED[@]} implementation file(s) without corresponding test changes:"
for f in "${UNPAIRED[@]}"; do
  echo "  - $f"
done

if $STRICT_MODE; then
  echo ""
  echo "[tdd-gate] FAIL — TDD policy requires test files alongside implementation changes."
  echo "[tdd-gate] Add test_* files or use --no-strict to bypass."
  exit 1
else
  echo ""
  echo "[tdd-gate] WARN — Consider adding tests. Use --strict to enforce."
  exit 0
fi
