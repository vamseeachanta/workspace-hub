#!/usr/bin/env bash
# test-uv-readiness.sh — Tests for uv readiness probe in submit-to-codex.sh
# Covers: uv working, uv present-but-broken, uv absent
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REVIEW_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SUBMIT_SCRIPT="${REVIEW_DIR}/submit-to-codex.sh"

PASS=0; FAIL=0; TOTAL=0
TEST_DIR="$(mktemp -d)"
trap 'rm -rf "$TEST_DIR"' EXIT

# ── Helpers ──────────────────────────────────────────────────────────────────

assert_status() {
  local label="$1" expected="$2" actual="$3"
  TOTAL=$((TOTAL + 1))
  if [[ "$expected" == "$actual" ]]; then
    echo "  PASS: $label"; PASS=$((PASS + 1))
  else
    echo "  FAIL: $label (expected=$expected got=$actual)"; FAIL=$((FAIL + 1))
  fi
}

assert_contains() {
  local label="$1" file="$2" pattern="$3"
  TOTAL=$((TOTAL + 1))
  if grep -qE "$pattern" "$file"; then
    echo "  PASS: $label"; PASS=$((PASS + 1))
  else
    echo "  FAIL: $label (pattern not found: $pattern)"; FAIL=$((FAIL + 1))
  fi
}

assert_not_contains() {
  local label="$1" file="$2" pattern="$3"
  TOTAL=$((TOTAL + 1))
  if ! grep -qE "$pattern" "$file"; then
    echo "  PASS: $label"; PASS=$((PASS + 1))
  else
    echo "  FAIL: $label (unexpected pattern found: $pattern)"; FAIL=$((FAIL + 1))
  fi
}

# ── Fixtures ─────────────────────────────────────────────────────────────────

SAMPLE_FILE="$TEST_DIR/sample.txt"
echo "test content" > "$SAMPLE_FILE"

# Mock codex: writes success JSON to --output-last-message file
cat > "$TEST_DIR/codex" <<'EOF'
#!/usr/bin/env bash
raw_file=""
while [[ $# -gt 0 ]]; do
  case "$1" in --output-last-message) raw_file="$2"; shift 2 ;; *) shift ;; esac
done
[[ -n "$raw_file" ]] && \
  echo '{"verdict":"APPROVE","summary":"ok","issues_found":[],"suggestions":[],"questions_for_author":[]}' \
  > "$raw_file"
exit 0
EOF
chmod +x "$TEST_DIR/codex"

# Mock renderer: prints a valid review ignoring --input
cat > "$TEST_DIR/renderer.py" <<'EOF'
#!/usr/bin/env python3
print("### Verdict: APPROVE\n\n### Summary\nok\n\n### Issues Found\n- None.\n\n### Suggestions\n- None.\n\n### Questions for Author\n- None.")
EOF

# Mock validator: always returns VALID
cat > "$TEST_DIR/validator.sh" <<'EOF'
#!/usr/bin/env bash
echo "VALID"
EOF
chmod +x "$TEST_DIR/validator.sh"

# Patched submit script with test renderer/validator paths
PATCHED="$TEST_DIR/submit-to-codex.sh"
cp "$SUBMIT_SCRIPT" "$PATCHED"
chmod +w "$PATCHED"
sed -i "s|^RENDERER=.*|RENDERER=\"$TEST_DIR/renderer.py\"|" "$PATCHED"
sed -i "s|^VALIDATOR=.*|VALIDATOR=\"$TEST_DIR/validator.sh\"|" "$PATCHED"
chmod +x "$PATCHED"

# Mock uv: passes through to python3 (simulates: uv run --no-project python <args>)
cat > "$TEST_DIR/uv-working" <<'EOF'
#!/usr/bin/env bash
# Strip "run --no-project python" prefix, then exec python3 with remaining args
shift 3 2>/dev/null || true
exec python3 "$@"
EOF
chmod +x "$TEST_DIR/uv-working"

# Mock uv: always fails the readiness probe and all calls
cat > "$TEST_DIR/uv-broken" <<'EOF'
#!/usr/bin/env bash
echo "error: uv cache corrupted, cannot start" >&2
exit 1
EOF
chmod +x "$TEST_DIR/uv-broken"

# ── Scenario 1: uv present and working ───────────────────────────────────────
echo "Scenario 1: uv present and working"
ln -sf "$TEST_DIR/uv-working" "$TEST_DIR/uv"
out1="$TEST_DIR/out1.txt"; err1="$TEST_DIR/err1.txt"; rc1=0
PATH="$TEST_DIR:$PATH" CODEX_BIN="$TEST_DIR/codex" \
  "$PATCHED" --file "$SAMPLE_FILE" --prompt "review" >"$out1" 2>"$err1" || rc1=$?
assert_status "uv working: exits 0" "0" "$rc1"
assert_not_contains "uv working: no 'not functional' message" "$err1" "uv is installed but not functional"

# ── Scenario 2: uv present but broken ────────────────────────────────────────
echo "Scenario 2: uv present but broken (readiness probe fails)"
ln -sf "$TEST_DIR/uv-broken" "$TEST_DIR/uv"
out2="$TEST_DIR/out2.txt"; err2="$TEST_DIR/err2.txt"; rc2=0
PATH="$TEST_DIR:$PATH" CODEX_BIN="$TEST_DIR/codex" \
  "$PATCHED" --file "$SAMPLE_FILE" --prompt "review" >"$out2" 2>"$err2" || rc2=$?
assert_status "uv broken: exits non-zero" "1" "$rc2"
assert_contains "uv broken: surfaces error to stderr" "$err2" "uv is installed but not functional"
assert_not_contains "uv broken: no python3 fallback attempt" "$err2" "Renderer runtime unavailable"

# ── Scenario 3: uv absent (python3 fallback) ─────────────────────────────────
echo "Scenario 3: uv absent (falls back to python3)"
rm -f "$TEST_DIR/uv"
out3="$TEST_DIR/out3.txt"; err3="$TEST_DIR/err3.txt"; rc3=0
# Remove TEST_DIR from PATH so no mock uv is found; keep system tools
SYSTEM_PATH="$(echo "$PATH" | tr ':' '\n' | grep -v "^$TEST_DIR$" | tr '\n' ':' | sed 's/:$//')"
CODEX_BIN="$TEST_DIR/codex" \
  env PATH="$SYSTEM_PATH" "$PATCHED" --file "$SAMPLE_FILE" --prompt "review" >"$out3" 2>"$err3" || rc3=$?
# uv absent → should NOT surface "uv not functional" error (different code path)
assert_not_contains "uv absent: no 'not functional' error" "$err3" "uv is installed but not functional"

echo ""
echo "Results: $PASS/$TOTAL passed; $FAIL failed"
[[ "$FAIL" -eq 0 ]]
