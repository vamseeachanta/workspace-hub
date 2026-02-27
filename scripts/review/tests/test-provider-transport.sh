#!/usr/bin/env bash
# test-provider-transport.sh - Unit tests for Claude/Gemini transport parsers.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REVIEW_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

PASS=0
FAIL=0
TOTAL=0
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

echo "Test 1: Claude structured_output renders valid markdown"
cat > "$TEST_DIR/claude.json" <<'EOF'
{"type":"result","structured_output":{"verdict":"APPROVE","summary":"Looks good.","issues_found":[],"suggestions":["Ship it."],"questions_for_author":[]}}
EOF
python3 "$REVIEW_DIR/render-structured-review.py" --provider claude --input "$TEST_DIR/claude.json" > "$TEST_DIR/claude.md"
status="$("$REVIEW_DIR/validate-review-output.sh" "$TEST_DIR/claude.md")"
assert_eq "Claude markdown validates" "VALID" "$status"

echo "Test 2: Gemini fenced JSON response renders valid markdown"
cat > "$TEST_DIR/gemini.json" <<'EOF'
{
  "session_id": "abc",
  "response": "```json\n{\"verdict\":\"REQUEST_CHANGES\",\"summary\":\"Needs one fix.\",\"issues_found\":[\"[P1] Missing timeout handling\"],\"suggestions\":[\"Retry in isolated cwd\"],\"questions_for_author\":[\"Should raw output be preserved?\"]}\n```"
}
EOF
python3 "$REVIEW_DIR/render-structured-review.py" --provider gemini --input "$TEST_DIR/gemini.json" > "$TEST_DIR/gemini.md"
status="$("$REVIEW_DIR/validate-review-output.sh" "$TEST_DIR/gemini.md")"
assert_eq "Gemini markdown validates" "VALID" "$status"

echo "Test 3: Invalid provider payload fails"
cat > "$TEST_DIR/invalid.json" <<'EOF'
{"response":"not json"}
EOF
if python3 "$REVIEW_DIR/render-structured-review.py" --provider gemini --input "$TEST_DIR/invalid.json" >/dev/null 2>&1; then
    actual="unexpected-success"
else
    actual="failed"
fi
assert_eq "Invalid payload rejected" "failed" "$actual"

echo "Test 4: Invalid verdict is rejected"
cat > "$TEST_DIR/invalid-verdict.json" <<'EOF'
{"type":"result","structured_output":{"verdict":"LGTM","summary":"Looks fine.","issues_found":[],"suggestions":[],"questions_for_author":[]}}
EOF
if python3 "$REVIEW_DIR/render-structured-review.py" --provider claude --input "$TEST_DIR/invalid-verdict.json" >/dev/null 2>&1; then
    actual="unexpected-success"
else
    actual="failed"
fi
assert_eq "Invalid verdict rejected" "failed" "$actual"

echo "Test 5: Malformed JSON is rejected"
cat > "$TEST_DIR/malformed.json" <<'EOF'
{"type":"result","structured_output":{"verdict":APPROVE}}
EOF
if python3 "$REVIEW_DIR/render-structured-review.py" --provider claude --input "$TEST_DIR/malformed.json" >/dev/null 2>&1; then
    actual="unexpected-success"
else
    actual="failed"
fi
assert_eq "Malformed JSON rejected" "failed" "$actual"

echo "Test 6: Missing required key is rejected"
cat > "$TEST_DIR/missing-key.json" <<'EOF'
{"type":"result","structured_output":{"verdict":"APPROVE","issues_found":[],"suggestions":[],"questions_for_author":[]}}
EOF
if python3 "$REVIEW_DIR/render-structured-review.py" --provider claude --input "$TEST_DIR/missing-key.json" >/dev/null 2>&1; then
    actual="unexpected-success"
else
    actual="failed"
fi
assert_eq "Missing key rejected" "failed" "$actual"

echo "Test 7: String list fields are coerced"
cat > "$TEST_DIR/string-list.json" <<'EOF'
{"type":"result","structured_output":{"verdict":"APPROVE","summary":"ok","issues_found":"single issue","suggestions":"single suggestion","questions_for_author":"single question"}}
EOF
python3 "$REVIEW_DIR/render-structured-review.py" --provider claude --input "$TEST_DIR/string-list.json" > "$TEST_DIR/string-list.md"
status="$("$REVIEW_DIR/validate-review-output.sh" "$TEST_DIR/string-list.md")"
assert_eq "String-list markdown validates" "VALID" "$status"
if grep -Eq "single issue|single suggestion|single question" "$TEST_DIR/string-list.md"; then
    actual="present"
else
    actual="missing"
fi
assert_eq "String values rendered" "present" "$actual"

echo "Test 8: None list items are dropped"
cat > "$TEST_DIR/null-list.json" <<'EOF'
{"type":"result","structured_output":{"verdict":"APPROVE","summary":"ok","issues_found":[null,"real issue"],"suggestions":[],"questions_for_author":[]}}
EOF
python3 "$REVIEW_DIR/render-structured-review.py" --provider claude --input "$TEST_DIR/null-list.json" > "$TEST_DIR/null-list.md"
issues_section="$(awk '
    /^### Issues Found/ {in_issues=1; next}
    /^### / && in_issues {exit}
    in_issues {print}
' "$TEST_DIR/null-list.md")"
if grep -q "real issue" <<< "$issues_section" && ! grep -q "None" <<< "$issues_section"; then
    actual="clean"
else
    actual="dirty"
fi
assert_eq "None items dropped" "clean" "$actual"

echo "Test 9: Later fenced JSON block is parsed"
cat > "$TEST_DIR/multi-fence.json" <<'EOF'
```text
not json
```
```json
{"verdict":"APPROVE","summary":"ok","issues_found":[],"suggestions":[],"questions_for_author":[]}
```
EOF
python3 "$REVIEW_DIR/render-structured-review.py" --provider gemini --input "$TEST_DIR/multi-fence.json" > "$TEST_DIR/multi-fence.md"
status="$("$REVIEW_DIR/validate-review-output.sh" "$TEST_DIR/multi-fence.md")"
assert_eq "Later fenced JSON validates" "VALID" "$status"

echo "Test 10: Raw JSON fallback is parsed"
cat > "$TEST_DIR/raw.json" <<'EOF'
prefix noise
{"verdict":"APPROVE","summary":"ok","issues_found":[],"suggestions":[],"questions_for_author":[]}
EOF
python3 "$REVIEW_DIR/render-structured-review.py" --provider gemini --input "$TEST_DIR/raw.json" > "$TEST_DIR/raw.md"
status="$("$REVIEW_DIR/validate-review-output.sh" "$TEST_DIR/raw.md")"
assert_eq "Raw JSON fallback validates" "VALID" "$status"

echo "Test 11: Claude result-string path is parsed"
cat > "$TEST_DIR/claude-result-string.json" <<'EOF'
{"result":"{\"verdict\":\"APPROVE\",\"summary\":\"ok\",\"issues_found\":[],\"suggestions\":[],\"questions_for_author\":[]}"}
EOF
python3 "$REVIEW_DIR/render-structured-review.py" --provider claude --input "$TEST_DIR/claude-result-string.json" > "$TEST_DIR/claude-result-string.md"
status="$("$REVIEW_DIR/validate-review-output.sh" "$TEST_DIR/claude-result-string.md")"
assert_eq "Claude result-string validates" "VALID" "$status"

echo "Test 12: Non-object JSON is rejected"
cat > "$TEST_DIR/non-object.json" <<'EOF'
[1, 2, 3]
EOF
if python3 "$REVIEW_DIR/render-structured-review.py" --provider claude --input "$TEST_DIR/non-object.json" >/dev/null 2>&1; then
    actual="unexpected-success"
else
    actual="failed"
fi
assert_eq "Non-object JSON rejected" "failed" "$actual"

echo "Test 13: Broken leading object falls through to later valid JSON"
cat > "$TEST_DIR/broken-leading-object.json" <<'EOF'
prefix {broken
{"verdict":"APPROVE","summary":"ok","issues_found":[],"suggestions":[],"questions_for_author":[]}
EOF
python3 "$REVIEW_DIR/render-structured-review.py" --provider gemini --input "$TEST_DIR/broken-leading-object.json" > "$TEST_DIR/broken-leading-object.md"
status="$("$REVIEW_DIR/validate-review-output.sh" "$TEST_DIR/broken-leading-object.md")"
assert_eq "Broken leading object skipped" "VALID" "$status"

echo "Test 14: Nested list item is rejected"
cat > "$TEST_DIR/nested-list-item.json" <<'EOF'
{"type":"result","structured_output":{"verdict":"APPROVE","summary":"ok","issues_found":[{"bad":"item"}],"suggestions":[],"questions_for_author":[]}}
EOF
if python3 "$REVIEW_DIR/render-structured-review.py" --provider claude --input "$TEST_DIR/nested-list-item.json" >/dev/null 2>&1; then
    actual="unexpected-success"
else
    actual="failed"
fi
assert_eq "Nested list item rejected" "failed" "$actual"

echo "Test 15: Gemini direct-payload path (no response key)"
cat > "$TEST_DIR/gemini-direct.json" <<'EOF'
{"verdict":"APPROVE","summary":"Direct payload ok.","issues_found":[],"suggestions":["Keep it."],"questions_for_author":[]}
EOF
python3 "$REVIEW_DIR/render-structured-review.py" --provider gemini --input "$TEST_DIR/gemini-direct.json" > "$TEST_DIR/gemini-direct.md"
status="$("$REVIEW_DIR/validate-review-output.sh" "$TEST_DIR/gemini-direct.md")"
assert_eq "Gemini direct-payload validates" "VALID" "$status"

echo "Test 16: Empty file is rejected"
: > "$TEST_DIR/empty.json"
if python3 "$REVIEW_DIR/render-structured-review.py" --provider claude --input "$TEST_DIR/empty.json" >/dev/null 2>&1; then
    actual="unexpected-success"
else
    actual="failed"
fi
assert_eq "Empty file rejected" "failed" "$actual"

echo "Test 17: Whitespace-only summary is rejected"
cat > "$TEST_DIR/whitespace-summary.json" <<'EOF'
{"verdict":"APPROVE","summary":"   ","issues_found":[],"suggestions":[],"questions_for_author":[]}
EOF
if python3 "$REVIEW_DIR/render-structured-review.py" --provider gemini --input "$TEST_DIR/whitespace-summary.json" >/dev/null 2>&1; then
    actual="unexpected-success"
else
    actual="failed"
fi
assert_eq "Whitespace-only summary rejected" "failed" "$actual"

echo "Test 18: Integer for issues_found is rejected"
cat > "$TEST_DIR/int-list.json" <<'EOF'
{"verdict":"APPROVE","summary":"ok","issues_found":42,"suggestions":[],"questions_for_author":[]}
EOF
if python3 "$REVIEW_DIR/render-structured-review.py" --provider gemini --input "$TEST_DIR/int-list.json" >/dev/null 2>&1; then
    actual="unexpected-success"
else
    actual="failed"
fi
assert_eq "Integer issues_found rejected" "failed" "$actual"

echo ""
echo "======================================="
echo "  Results: $PASS/$TOTAL passed, $FAIL failed"
echo "======================================="
[[ "$FAIL" -eq 0 ]] && exit 0 || exit 1
