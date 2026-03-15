#!/usr/bin/env bash
# TDD tests for skill-autoresearch-nightly.sh (WRK-5087)
set -euo pipefail

REPO_ROOT="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)"
SCRIPT="${REPO_ROOT}/scripts/cron/skill-autoresearch-nightly.sh"
PASS=0
FAIL=0

pass() { PASS=$((PASS + 1)); echo "  PASS: $1"; }
fail() { FAIL=$((FAIL + 1)); echo "  FAIL: $1"; }

echo "=== WRK-5087: skill-autoresearch-nightly tests ==="

# --- AC1: Script exists and is executable ---
echo ""
echo "--- AC1: Script exists ---"

if [ -f "$SCRIPT" ]; then
    pass "script exists at scripts/cron/skill-autoresearch-nightly.sh"
else
    fail "script missing"
fi

if [ -x "$SCRIPT" ]; then
    pass "script is executable"
else
    fail "script is not executable"
fi

# --- AC2: Script has required functions/sections ---
echo ""
echo "--- AC2: Required sections ---"

if grep -q "autoresearch/skills-" "$SCRIPT"; then
    pass "branch naming pattern present"
else
    fail "branch naming pattern missing"
fi

if grep -q "results.tsv" "$SCRIPT" || grep -q "results\.tsv" "$SCRIPT"; then
    pass "results.tsv logging present"
else
    fail "results.tsv logging missing"
fi

if grep -q "eval-skills.py" "$SCRIPT" || grep -q "run-skill-evals" "$SCRIPT"; then
    pass "skill-eval integration present"
else
    fail "skill-eval integration missing"
fi

if grep -q "timeout\|TIMEOUT\|TIME_BUDGET" "$SCRIPT"; then
    pass "time budget mechanism present"
else
    fail "time budget mechanism missing"
fi

if grep -q "git checkout\|git switch\|git branch" "$SCRIPT"; then
    pass "git branch isolation present"
else
    fail "git branch isolation missing"
fi

if grep -q "git reset\|git checkout -- \|git restore" "$SCRIPT"; then
    pass "revert mechanism present"
else
    fail "revert mechanism missing"
fi

# --- AC3: Safety checks ---
echo ""
echo "--- AC3: Safety checks ---"

if grep -q "main" "$SCRIPT" && grep -q "never\|NEVER\|protect\|safe" "$SCRIPT"; then
    pass "main branch protection mentioned"
else
    # Check for indirect protection (branch check before modifying)
    if grep -q 'git diff main' "$SCRIPT" || grep -q 'autoresearch/' "$SCRIPT"; then
        pass "main branch protection via branch isolation"
    else
        fail "no main branch protection found"
    fi
fi

# --- AC4: Dry-run mode ---
echo ""
echo "--- AC4: Dry-run / help ---"

if grep -q "\-\-dry-run\|DRY_RUN\|\-\-help\|\-h" "$SCRIPT"; then
    pass "dry-run or help flag present"
else
    fail "no dry-run or help flag"
fi

# --- Summary ---
echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="
exit $FAIL
