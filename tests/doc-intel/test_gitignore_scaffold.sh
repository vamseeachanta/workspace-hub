#!/usr/bin/env bash
# TDD tests for WRK-5035: gitignore pre-conditions + data/standards/promoted/ scaffold
set -euo pipefail

REPO_ROOT="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)"
PASS=0
FAIL=0

pass() { PASS=$((PASS + 1)); echo "  PASS: $1"; }
fail() { FAIL=$((FAIL + 1)); echo "  FAIL: $1"; }

echo "=== WRK-5035: gitignore + scaffold tests ==="

# --- AC1: .gitignore has doc-intel promotion output pattern ---
echo ""
echo "--- AC1: .gitignore patterns ---"

if grep -q 'data/standards/promoted/' "$REPO_ROOT/.gitignore"; then
    pass "data/standards/promoted/ pattern in .gitignore"
else
    fail "data/standards/promoted/ pattern missing from .gitignore"
fi

# --- AC2: data/standards/promoted/ directory exists with .gitkeep ---
echo ""
echo "--- AC2: directory scaffold ---"

if [ -d "$REPO_ROOT/data/standards/promoted" ]; then
    pass "data/standards/promoted/ directory exists"
else
    fail "data/standards/promoted/ directory missing"
fi

if [ -f "$REPO_ROOT/data/standards/promoted/.gitkeep" ]; then
    pass "data/standards/promoted/.gitkeep exists"
else
    fail "data/standards/promoted/.gitkeep missing"
fi

# --- AC3: gitignore correctly excludes promoted files ---
echo ""
echo "--- AC3: gitignore exclusion verification ---"

# Test that a hypothetical CSV in promoted/ would be ignored
if git -C "$REPO_ROOT" check-ignore -q "data/standards/promoted/example.csv" 2>/dev/null; then
    pass "data/standards/promoted/example.csv is gitignored"
else
    fail "data/standards/promoted/example.csv NOT gitignored"
fi

# Test that .gitkeep is NOT ignored (negation pattern)
if git -C "$REPO_ROOT" check-ignore -q "data/standards/promoted/.gitkeep" 2>/dev/null; then
    fail "data/standards/promoted/.gitkeep should NOT be gitignored"
else
    pass "data/standards/promoted/.gitkeep is tracked (not ignored)"
fi

# --- AC4: existing gitignore patterns not broken ---
echo ""
echo "--- AC4: regression check on existing patterns ---"

# Verify pre-existing doc-intel patterns still work
if git -C "$REPO_ROOT" check-ignore -q "data/doc-intelligence/some-file.json" 2>/dev/null; then
    pass "data/doc-intelligence/ still gitignored"
else
    fail "data/doc-intelligence/ pattern broken"
fi

if git -C "$REPO_ROOT" check-ignore -q "data/document-index/index.jsonl" 2>/dev/null; then
    pass "data/document-index/index.jsonl still gitignored"
else
    fail "data/document-index/index.jsonl pattern broken"
fi

if git -C "$REPO_ROOT" check-ignore -q "data/standards-index/chunks.jsonl" 2>/dev/null; then
    pass "data/standards-index/chunks.jsonl still gitignored"
else
    fail "data/standards-index/chunks.jsonl pattern broken"
fi

# --- Summary ---
echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="
exit $FAIL
