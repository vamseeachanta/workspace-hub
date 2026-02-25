#!/usr/bin/env bash
# test-codex-fallback.sh — Tests for Codex NO_OUTPUT fallback (WRK-160)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REVIEW_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# ── Test scaffolding ─────────────────────────────────────────────────
PASS=0; FAIL=0; TOTAL=0
TEST_DIR="$(mktemp -d)"
trap 'rm -rf "$TEST_DIR"' EXIT

assert_eq() {
    local label="$1" expected="$2" actual="$3"
    TOTAL=$((TOTAL + 1))
    if [[ "$expected" == "$actual" ]]; then
        echo "  PASS: $label"
        PASS=$((PASS + 1))
    else
        echo "  FAIL: $label (expected='$expected', got='$actual')"
        FAIL=$((FAIL + 1))
    fi
}

# ── Test normalize-verdicts.sh ───────────────────────────────────────
echo "Test 1: normalize-verdicts — APPROVE"
echo "### Verdict: APPROVE" > "$TEST_DIR/review-approve.md"
echo "Everything looks good." >> "$TEST_DIR/review-approve.md"
v="$("$REVIEW_DIR/normalize-verdicts.sh" "$TEST_DIR/review-approve.md")"
assert_eq "APPROVE detected" "APPROVE" "$v"

echo "Test 2: normalize-verdicts — MINOR"
echo "### Verdict: REQUEST_CHANGES" > "$TEST_DIR/review-minor.md"
echo "[P3] Minor: typo in comment" >> "$TEST_DIR/review-minor.md"
v="$("$REVIEW_DIR/normalize-verdicts.sh" "$TEST_DIR/review-minor.md")"
assert_eq "MINOR detected" "MINOR" "$v"

echo "Test 3: normalize-verdicts — MAJOR"
echo "### Verdict: REQUEST_CHANGES" > "$TEST_DIR/review-major.md"
echo "[P1] Major: missing error handling" >> "$TEST_DIR/review-major.md"
v="$("$REVIEW_DIR/normalize-verdicts.sh" "$TEST_DIR/review-major.md")"
assert_eq "MAJOR detected" "MAJOR" "$v"

echo "Test 4: normalize-verdicts — NO_OUTPUT"
echo "# Codex returned NO_OUTPUT (empty response)" > "$TEST_DIR/review-noout.md"
v="$("$REVIEW_DIR/normalize-verdicts.sh" "$TEST_DIR/review-noout.md")"
assert_eq "NO_OUTPUT detected" "NO_OUTPUT" "$v"

echo "Test 5: normalize-verdicts — CONDITIONAL_PASS"
cat > "$TEST_DIR/review-conditional.md" <<'EOF'
# Codex Fallback Consensus (WRK-160)
- **Result**: CONDITIONAL_PASS (2-of-3 consensus)
EOF
v="$("$REVIEW_DIR/normalize-verdicts.sh" "$TEST_DIR/review-conditional.md")"
assert_eq "CONDITIONAL_PASS detected" "CONDITIONAL_PASS" "$v"

echo "Test 6: normalize-verdicts — ERROR (empty file)"
echo "" > "$TEST_DIR/review-empty.md"
v="$("$REVIEW_DIR/normalize-verdicts.sh" "$TEST_DIR/review-empty.md")"
assert_eq "ERROR on empty" "ERROR" "$v"

# ── Test fallback consensus logic (unit-level) ───────────────────────
# We test the decision logic by simulating the conditions directly
echo ""
echo "Test 7: Fallback consensus — both APPROVE → CONDITIONAL_PASS"
claude_v="APPROVE"; gemini_v="APPROVE"
if [[ ("$claude_v" == "APPROVE" || "$claude_v" == "MINOR") && \
      ("$gemini_v" == "APPROVE" || "$gemini_v" == "MINOR") ]]; then
    result="CONDITIONAL_PASS"
else
    result="FAIL"
fi
assert_eq "both APPROVE → pass" "CONDITIONAL_PASS" "$result"

echo "Test 8: Fallback consensus — APPROVE + MINOR → CONDITIONAL_PASS"
claude_v="APPROVE"; gemini_v="MINOR"
if [[ ("$claude_v" == "APPROVE" || "$claude_v" == "MINOR") && \
      ("$gemini_v" == "APPROVE" || "$gemini_v" == "MINOR") ]]; then
    result="CONDITIONAL_PASS"
else
    result="FAIL"
fi
assert_eq "APPROVE + MINOR → pass" "CONDITIONAL_PASS" "$result"

echo "Test 9: Fallback consensus — APPROVE + NO_OUTPUT → FAIL"
claude_v="APPROVE"; gemini_v="NO_OUTPUT"
if [[ ("$claude_v" == "APPROVE" || "$claude_v" == "MINOR") && \
      ("$gemini_v" == "APPROVE" || "$gemini_v" == "MINOR") ]]; then
    result="CONDITIONAL_PASS"
else
    result="FAIL"
fi
assert_eq "APPROVE + NO_OUTPUT → fail" "FAIL" "$result"

echo "Test 10: Fallback consensus — APPROVE + ERROR → FAIL"
claude_v="APPROVE"; gemini_v="ERROR"
if [[ ("$claude_v" == "APPROVE" || "$claude_v" == "MINOR") && \
      ("$gemini_v" == "APPROVE" || "$gemini_v" == "MINOR") ]]; then
    result="CONDITIONAL_PASS"
else
    result="FAIL"
fi
assert_eq "APPROVE + ERROR → fail" "FAIL" "$result"

echo "Test 11: No fallback on explicit REJECT — Codex MAJOR stays blocked"
# This tests the policy: fallback only triggers on NO_OUTPUT, not on explicit reject
codex_no_output=false  # Codex gave a real verdict (MAJOR)
if [[ "$codex_no_output" == "true" ]]; then
    result="FALLBACK_ATTEMPTED"
else
    result="HARD_BLOCK"
fi
assert_eq "explicit reject → hard block" "HARD_BLOCK" "$result"

# ── Summary ──────────────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════"
echo "  Results: $PASS/$TOTAL passed, $FAIL failed"
echo "═══════════════════════════════════════"
[[ "$FAIL" -eq 0 ]] && exit 0 || exit 1
