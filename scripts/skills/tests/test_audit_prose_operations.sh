#!/usr/bin/env bash
# test_audit_prose_operations.sh — TDD tests for audit-prose-operations.py
# Usage: bash scripts/skills/tests/test_audit_prose_operations.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel)"
SCRIPT="${REPO_ROOT}/scripts/skills/audit-prose-operations.py"
PASS=0; FAIL=0

# Create temp dir for fixtures
TMPDIR_TEST=$(mktemp -d)
trap 'rm -rf "$TMPDIR_TEST"' EXIT

run_test() {
    local name="$1" input_md="$2" expected_pattern="$3" expect_match="$4"
    local skill_dir="${TMPDIR_TEST}/${name}"
    mkdir -p "$skill_dir"
    echo "$input_md" > "${skill_dir}/test.md"
    local out exit_code=0
    out=$(uv run --no-project python "$SCRIPT" --path "$skill_dir" --output /dev/null 2>/dev/null) || exit_code=$?
    if [[ "$expect_match" == "yes" ]]; then
        if echo "$out" | grep -qE "$expected_pattern"; then
            echo "  PASS: $name"
            PASS=$((PASS + 1))
        else
            echo "  FAIL: $name — pattern '$expected_pattern' not in: '$out'"
            FAIL=$((FAIL + 1))
        fi
    else
        if echo "$out" | grep -qE "$expected_pattern" && [[ -n "$expected_pattern" ]]; then
            echo "  FAIL: $name — unexpected pattern found"
            FAIL=$((FAIL + 1))
        else
            echo "  PASS: $name"
            PASS=$((PASS + 1))
        fi
    fi
}

echo "=== test_audit_prose_operations.sh ==="

run_test "flags_count_inline" \
    "Step 1: count the files in the directory." \
    "count_ops" "yes"

run_test "flags_iteration" \
    "For each repo, check the status." \
    "iteration_ops" "yes"

run_test "flags_parse_ops" \
    "Parse the yaml configuration file to extract fields." \
    "parse_ops" "yes"

run_test "flags_generate_ops" \
    "Generate the yaml report by hand for each item." \
    "generate_ops" "yes"

run_test "flags_threshold_ops" \
    "Check if utilization is greater than 90 percent." \
    "threshold_ops" "yes"

run_test "skips_bash_block" \
    '```bash
count the files in dir
```
Normal prose without flaggable content.' \
    "count_ops" "no"

run_test "skips_python_block" \
    '```python
for each in items:
    pass
```
Normal sentence after block.' \
    "iteration_ops" "no"

run_test "empty_file_no_crash" \
    "" \
    "ERROR|error|traceback" "no"

# Test output report generation
OUT_FILE="${TMPDIR_TEST}/report.md"
echo "Count the repos and tally results." > "${TMPDIR_TEST}/probe.md"
uv run --no-project python "$SCRIPT" --path "$TMPDIR_TEST" --output "$OUT_FILE" >/dev/null 2>/dev/null || true
if [[ -f "$OUT_FILE" ]]; then
    if grep -qE "File|Category|Classification" "$OUT_FILE"; then
        echo "  PASS: generates_markdown_report"
        PASS=$((PASS + 1))
    else
        echo "  FAIL: generates_markdown_report — expected table headers"
        FAIL=$((FAIL + 1))
    fi
else
    echo "  FAIL: generates_markdown_report — output file not created"
    FAIL=$((FAIL + 1))
fi

echo ""
echo "Results: ${PASS} PASS, ${FAIL} FAIL"
[[ $FAIL -eq 0 ]] && exit 0 || exit 1
