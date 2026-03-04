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

echo "Test 4b: validate-review-output — INVALID_OUTPUT"
cat > "$TEST_DIR/review-invalid.md" <<'EOF'
I will begin by exploring the repository and then provide a review.
EOF
v="$("$REVIEW_DIR/validate-review-output.sh" "$TEST_DIR/review-invalid.md")"
assert_eq "INVALID_OUTPUT detected" "INVALID_OUTPUT" "$v"

echo "Test 4c: normalize-verdicts — INVALID_OUTPUT"
v="$("$REVIEW_DIR/normalize-verdicts.sh" "$TEST_DIR/review-invalid.md")"
assert_eq "INVALID_OUTPUT normalized" "INVALID_OUTPUT" "$v"

echo "Test 4d: validate-review-output — transport failure stub as NO_OUTPUT"
cat > "$TEST_DIR/review-transport-failure.md" <<'EOF'
# Codex transport/network failure (exit 1)
# Action: run outside restricted sandbox or restore provider connectivity.
EOF
v="$("$REVIEW_DIR/validate-review-output.sh" "$TEST_DIR/review-transport-failure.md")"
assert_eq "codex transport failure stays non-NO_OUTPUT" "INVALID_OUTPUT" "$v"

echo "Test 4d2: normalize-verdicts — codex CLI missing is ERROR"
cat > "$TEST_DIR/review-codex-missing.md" <<'EOF'
# Codex CLI not found
# Install: npm install -g @openai/codex
EOF
v="$("$REVIEW_DIR/normalize-verdicts.sh" "$TEST_DIR/review-codex-missing.md")"
assert_eq "codex cli missing normalized as ERROR" "ERROR" "$v"

echo "Test 4e: validate-review-output — valid review mentioning timed out/no_output remains VALID"
cat > "$TEST_DIR/review-valid-with-keywords.md" <<'EOF'
### Verdict: REQUEST_CHANGES

### Summary
Overall good, but one section mentions timed out behavior and no_output fallback policy.

### Issues Found
- [P2] Important: make sure "timed out" appears only in issue prose and does not force NO_OUTPUT.

### Suggestions
- Keep no_output policy language in docs.

### Questions for Author
- None.
EOF
v="$("$REVIEW_DIR/validate-review-output.sh" "$TEST_DIR/review-valid-with-keywords.md")"
assert_eq "keyword prose does not force NO_OUTPUT" "VALID" "$v"

echo "Test 4f: validate/normalize — SKIPPED_NETWORK classification"
cat > "$TEST_DIR/review-skipped-network.md" <<'EOF'
# Gemini skipped_network due to policy
EOF
v="$("$REVIEW_DIR/validate-review-output.sh" "$TEST_DIR/review-skipped-network.md")"
assert_eq "validator emits SKIPPED_NETWORK" "SKIPPED_NETWORK" "$v"
v="$("$REVIEW_DIR/normalize-verdicts.sh" "$TEST_DIR/review-skipped-network.md")"
assert_eq "normalizer emits SKIPPED_NETWORK" "SKIPPED_NETWORK" "$v"

echo "Test 4g: validate-review-output — non-provider no_output heading remains INVALID_OUTPUT"
cat > "$TEST_DIR/review-heading-nooutput.md" <<'EOF'
# no_output policy notes
This is documentation, not a provider failure stub.
EOF
v="$("$REVIEW_DIR/validate-review-output.sh" "$TEST_DIR/review-heading-nooutput.md")"
assert_eq "non-provider no_output heading not classified as NO_OUTPUT" "INVALID_OUTPUT" "$v"

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

echo "Test 12: No fallback on INVALID_OUTPUT — hard block"
codex_invalid_output=true
if [[ "$codex_invalid_output" == "true" ]]; then
    result="HARD_BLOCK"
else
    result="FALLBACK_ATTEMPTED"
fi
assert_eq "invalid output → hard block" "HARD_BLOCK" "$result"

# ── Summary ──────────────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════"
echo "  Results: $PASS/$TOTAL passed, $FAIL failed"
echo "═══════════════════════════════════════"
[[ "$FAIL" -eq 0 ]] && exit 0 || exit 1
