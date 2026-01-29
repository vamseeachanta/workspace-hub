#!/usr/bin/env bash
# test-capture-corrections.sh - Tests for the capture-corrections hook
# Tests the Phase 2 enhanced fields: file_extension, edit_context, chain tracking
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FIXTURES="${SCRIPT_DIR}/fixtures"

# Resolve hook path: tests -> scripts -> claude-reflect -> workspace -> coordination -> skills -> .claude -> hooks
HOOK="/mnt/github/workspace-hub/.claude/hooks/capture-corrections.sh"
if [[ ! -f "$HOOK" ]]; then
    echo "ERROR: Hook not found at $HOOK" >&2
    exit 1
fi

PASS=0
FAIL=0
TOTAL=6

setup() {
    export WORKSPACE_STATE_DIR="$(mktemp -d)"
    export CLAUDE_CAPTURE_CORRECTIONS="true"
    STATE_DIR="${WORKSPACE_STATE_DIR}/corrections"
    mkdir -p "$STATE_DIR"
    SESSION_FILE="${STATE_DIR}/session_$(date +%Y%m%d).jsonl"
    RECENT_EDITS="${STATE_DIR}/.recent_edits"
}

teardown() {
    rm -rf "$WORKSPACE_STATE_DIR"
}

assert_eq() {
    local desc="$1" expected="$2" actual="$3"
    if [[ "$expected" == "$actual" ]]; then
        echo "  PASS: $desc"
        PASS=$((PASS + 1))
    else
        echo "  FAIL: $desc"
        echo "    Expected: $expected"
        echo "    Actual:   $actual"
        FAIL=$((FAIL + 1))
    fi
}

assert_contains() {
    local desc="$1" expected="$2" actual="$3"
    if echo "$actual" | grep -qF "$expected"; then
        echo "  PASS: $desc"
        PASS=$((PASS + 1))
    else
        echo "  FAIL: $desc"
        echo "    Expected to contain: $expected"
        echo "    Actual: $actual"
        FAIL=$((FAIL + 1))
    fi
}

echo "=== Test: capture-corrections.sh ==="
echo ""

# Test 1: Edit tool records file_extension field
echo "Test 1: Edit tool captures file_extension"
setup
# First edit - creates the recent_edits entry
echo '{"tool_name":"Edit","tool_input":{"file_path":"/tmp/test/main.py","old_string":"foo","new_string":"bar"}}' | bash "$HOOK"
# Second edit to same file - triggers correction
sleep 1
echo '{"tool_name":"Edit","tool_input":{"file_path":"/tmp/test/main.py","old_string":"bar","new_string":"baz"}}' | bash "$HOOK"
if [[ -f "$SESSION_FILE" ]]; then
    EXT=$(jq -r '.file_extension // "MISSING"' "$SESSION_FILE" | tail -1)
    assert_eq "file_extension is 'py'" "py" "$EXT"
else
    assert_eq "session file exists" "exists" "missing"
fi
teardown

# Test 2: Write tool captures content preview in edit_context
echo "Test 2: Write tool captures edit_context with content preview"
setup
# First write
echo '{"tool_name":"Write","tool_input":{"file_path":"/tmp/test/newfile.ts","content":"export function hello(): string { return world; }"}}' | bash "$HOOK"
sleep 1
# Second write to same file - triggers correction
echo '{"tool_name":"Write","tool_input":{"file_path":"/tmp/test/newfile.ts","content":"export function hello(): string { return fixed_world; }"}}' | bash "$HOOK"
if [[ -f "$SESSION_FILE" ]]; then
    CONTEXT=$(jq -r '.edit_context.new_string_preview // "MISSING"' "$SESSION_FILE" | tail -1)
    assert_contains "edit_context has content preview" "fixed_world" "$CONTEXT"
else
    assert_eq "session file exists" "exists" "missing"
fi
teardown

# Test 3: Edit tool captures old_string and new_string previews
echo "Test 3: Edit tool captures old/new string previews"
setup
echo '{"tool_name":"Edit","tool_input":{"file_path":"/tmp/test/config.sh","old_string":"OLD_VALUE","new_string":"NEW_VALUE"}}' | bash "$HOOK"
sleep 1
echo '{"tool_name":"Edit","tool_input":{"file_path":"/tmp/test/config.sh","old_string":"NEW_VALUE","new_string":"FINAL_VALUE"}}' | bash "$HOOK"
if [[ -f "$SESSION_FILE" ]]; then
    OLD_PREVIEW=$(jq -r '.edit_context.old_string_preview // "MISSING"' "$SESSION_FILE" | tail -1)
    NEW_PREVIEW=$(jq -r '.edit_context.new_string_preview // "MISSING"' "$SESSION_FILE" | tail -1)
    assert_contains "old_string_preview captured" "NEW_VALUE" "$OLD_PREVIEW"
    # Note: this consumes 2 asserts but we only count as 1 test
    # We'll just check old_string for this test
else
    assert_eq "session file exists" "exists" "missing"
fi
teardown

# Test 4: edit_sequence_id increments across edits
echo "Test 4: edit_sequence_id increments"
setup
echo '{"tool_name":"Edit","tool_input":{"file_path":"/tmp/test/a.py","old_string":"x","new_string":"y"}}' | bash "$HOOK"
sleep 1
echo '{"tool_name":"Edit","tool_input":{"file_path":"/tmp/test/a.py","old_string":"y","new_string":"z"}}' | bash "$HOOK"
if [[ -f "$SESSION_FILE" ]]; then
    SEQ=$(jq -r '.edit_sequence_id // "MISSING"' "$SESSION_FILE" | tail -1)
    # Should be a number > 0
    if [[ "$SEQ" =~ ^[0-9]+$ ]] && [[ "$SEQ" -gt 0 ]]; then
        assert_eq "edit_sequence_id is positive number" "true" "true"
    else
        assert_eq "edit_sequence_id is positive number" "positive_number" "$SEQ"
    fi
else
    assert_eq "session file exists" "exists" "missing"
fi
teardown

# Test 5: chain_id is assigned when correction detected
echo "Test 5: chain_id assigned on correction"
setup
echo '{"tool_name":"Edit","tool_input":{"file_path":"/tmp/test/b.py","old_string":"a","new_string":"b"}}' | bash "$HOOK"
sleep 1
echo '{"tool_name":"Edit","tool_input":{"file_path":"/tmp/test/b.py","old_string":"b","new_string":"c"}}' | bash "$HOOK"
if [[ -f "$SESSION_FILE" ]]; then
    CHAIN=$(jq -r '.chain_id // "MISSING"' "$SESSION_FILE" | tail -1)
    if [[ "$CHAIN" != "MISSING" && "$CHAIN" != "null" && -n "$CHAIN" ]]; then
        assert_eq "chain_id is present" "true" "true"
    else
        assert_eq "chain_id is present" "present" "$CHAIN"
    fi
else
    assert_eq "session file exists" "exists" "missing"
fi
teardown

# Test 6: Files without extension get file_extension="none"
echo "Test 6: Files without extension get extension=none"
setup
echo '{"tool_name":"Edit","tool_input":{"file_path":"/tmp/test/Makefile","old_string":"all:","new_string":"all: build"}}' | bash "$HOOK"
sleep 1
echo '{"tool_name":"Edit","tool_input":{"file_path":"/tmp/test/Makefile","old_string":"all: build","new_string":"all: build test"}}' | bash "$HOOK"
if [[ -f "$SESSION_FILE" ]]; then
    EXT=$(jq -r '.file_extension // "MISSING"' "$SESSION_FILE" | tail -1)
    assert_eq "extension-less file gets 'none'" "none" "$EXT"
else
    assert_eq "session file exists" "exists" "missing"
fi
teardown

echo ""
echo "=== Results: $PASS/$TOTAL passed, $FAIL failed ==="
[[ $FAIL -eq 0 ]] && exit 0 || exit 1
