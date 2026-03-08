#!/usr/bin/env bash
# test-cross-review-codex-hardgate.sh
# Integration-style regression for Codex compulsory gate behavior.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REVIEW_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
TEST_DIR="$(mktemp -d)"
trap 'rm -rf "$TEST_DIR"' EXIT

PASS=0
FAIL=0
TOTAL=0

assert_eq() {
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

# Copy required scripts to isolated sandbox and patch paths.
mkdir -p "$TEST_DIR/review/prompts" "$TEST_DIR/review/results"
cp "$REVIEW_DIR/cross-review.sh" "$TEST_DIR/review/"
cp "$REVIEW_DIR/validate-review-output.sh" "$TEST_DIR/review/"
cp "$REVIEW_DIR/normalize-verdicts.sh" "$TEST_DIR/review/"
cp "$REVIEW_DIR/prompts/implementation-review.md" "$TEST_DIR/review/prompts/"

cat > "$TEST_DIR/review/submit-to-codex.sh" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
echo "# Codex CLI not found"
echo "# Install: npm install -g @openai/codex"
exit 2
EOF

cat > "$TEST_DIR/review/submit-to-claude.sh" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
cat <<'MD'
### Verdict: APPROVE

### Summary
ok

### Issues Found
- None.

### Suggestions
- None.

### Questions for Author
- None.
MD
EOF

cat > "$TEST_DIR/review/submit-to-gemini.sh" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
cat <<'MD'
### Verdict: APPROVE

### Summary
ok

### Issues Found
- None.

### Suggestions
- None.

### Questions for Author
- None.
MD
EOF

chmod +x "$TEST_DIR/review/"*.sh

# Avoid dependency on external stop-hook script from parent tree.
sed -i 's|if \[\[ -f "${SCRIPT_DIR}/check-stop-hooks.sh" \]\]; then|if false; then|' "$TEST_DIR/review/cross-review.sh"

rc=0
"$TEST_DIR/review/cross-review.sh" "inline sample content" all --type implementation >"$TEST_DIR/out-codex-missing.log" 2>"$TEST_DIR/err-codex-missing.log" || rc=$?

assert_eq "codex missing enforces hard gate" "1" "$rc"
assert_eq "no fallback file created when codex missing" "0" "$(find "$TEST_DIR/review/results" -maxdepth 1 -name '*FALLBACK.md' | wc -l | tr -d ' ')"
assert_eq "codex result file contains hard gate marker" "1" "$(rg -n 'HARD GATE: Codex CLI not found' "$TEST_DIR/review/results" -g '*.md' | wc -l | tr -d ' ')"

# Scenario 2: Codex generic non-zero failure also hard-blocks (no fallback)
cat > "$TEST_DIR/review/submit-to-codex.sh" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
echo "# Codex review failed (exit 3)"
echo "# Codex provider crash"
exit 3
EOF
chmod +x "$TEST_DIR/review/submit-to-codex.sh"

rm -f "$TEST_DIR/review/results/"*.md 2>/dev/null || true
rc=0
"$TEST_DIR/review/cross-review.sh" "inline sample content" all --type implementation >"$TEST_DIR/out-codex-generic-fail.log" 2>"$TEST_DIR/err-codex-generic-fail.log" || rc=$?
assert_eq "codex generic failure enforces hard gate" "1" "$rc"
assert_eq "no fallback file created on generic failure" "0" "$(find "$TEST_DIR/review/results" -maxdepth 1 -name '*FALLBACK.md' | wc -l | tr -d ' ')"
assert_eq "generic failure recorded as hard gate" "1" "$(rg -n 'HARD GATE: Codex review is compulsory' "$TEST_DIR/review/results" -g '*.md' | wc -l | tr -d ' ')"

# Scenario 3: Explicit NO_OUTPUT stub is fallback-eligible, even with non-zero exit.
cat > "$TEST_DIR/review/submit-to-codex.sh" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
echo "# Codex returned NO_OUTPUT"
exit 5
EOF
chmod +x "$TEST_DIR/review/submit-to-codex.sh"

rm -f "$TEST_DIR/review/results/"*.md 2>/dev/null || true
rc=0
"$TEST_DIR/review/cross-review.sh" "inline sample content" all --type implementation >"$TEST_DIR/out-codex-nooutput.log" 2>"$TEST_DIR/err-codex-nooutput.log" || rc=$?
assert_eq "codex explicit NO_OUTPUT allows fallback consensus" "0" "$rc"
assert_eq "fallback file created for codex NO_OUTPUT" "1" "$(find "$TEST_DIR/review/results" -maxdepth 1 -name '*FALLBACK.md' | wc -l | tr -d ' ')"

# Scenario 4: CLI missing without --allow-no-codex exits non-zero (new explicit message)
cat > "$TEST_DIR/review/submit-to-codex.sh" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
echo "# Codex CLI not found"
echo "# Install: npm install -g @openai/codex"
exit 2
EOF
chmod +x "$TEST_DIR/review/submit-to-codex.sh"

rm -f "$TEST_DIR/review/results/"*.md 2>/dev/null || true
rc=0
"$TEST_DIR/review/cross-review.sh" "inline sample content" all --type implementation \
  >"$TEST_DIR/out-codex-missing-no-flag.log" 2>"$TEST_DIR/err-codex-missing-no-flag.log" || rc=$?
assert_eq "codex missing without --allow-no-codex exits non-zero" "1" "$rc"
assert_eq "specific CLI-missing error shown" "1" \
  "$(grep -c 'CODEX HARD GATE BLOCKED: Codex CLI not installed' \
     "$TEST_DIR/err-codex-missing-no-flag.log" || echo 0)"

# Scenario 5: CLI missing with --allow-no-codex + Claude+Gemini APPROVE → should pass
rm -f "$TEST_DIR/review/results/"*.md 2>/dev/null || true
rc=0
"$TEST_DIR/review/cross-review.sh" "inline sample content" all --type implementation \
  --allow-no-codex \
  >"$TEST_DIR/out-codex-missing-with-flag.log" 2>"$TEST_DIR/err-codex-missing-with-flag.log" || rc=$?
assert_eq "codex missing with --allow-no-codex exits 0 via 2-of-3" "0" "$rc"
assert_eq "fallback file created when --allow-no-codex used" "1" \
  "$(find "$TEST_DIR/review/results" -maxdepth 1 -name '*FALLBACK.md' | wc -l | tr -d ' ')"

echo ""
echo "Results: $PASS/$TOTAL passed; $FAIL failed"
[[ "$FAIL" -eq 0 ]]
