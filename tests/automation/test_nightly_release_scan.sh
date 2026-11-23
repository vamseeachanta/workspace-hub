#!/usr/bin/env bash
# Integration test for nightly-release-scan.sh
# Mocks CLI --version commands via PATH override, verifies dry-run output.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SCRIPT="${REPO_ROOT}/scripts/automation/nightly-release-scan.sh"
FAILURES=0

# ── Setup temp mock environment ──────────────────────────────────────
MOCK_DIR=$(mktemp -d)
trap 'rm -rf "$MOCK_DIR"' EXIT

# Mock claude CLI
cat > "${MOCK_DIR}/claude" << 'MOCK'
#!/usr/bin/env bash
if [[ "${1:-}" == "--version" ]]; then
    echo "claude 2.1.99"
else
    echo "mock claude"
fi
MOCK
chmod +x "${MOCK_DIR}/claude"

# Mock codex CLI
cat > "${MOCK_DIR}/codex" << 'MOCK'
#!/usr/bin/env bash
if [[ "${1:-}" == "--version" ]]; then
    echo "codex 0.120.0"
else
    echo "mock codex"
fi
MOCK
chmod +x "${MOCK_DIR}/codex"

# Mock gemini CLI (not installed)
# Intentionally absent — tests "provider not found" path

# ── Test 1: Script exists and is executable ──────────────────────────
echo "TEST 1: Script exists"
if [[ -f "$SCRIPT" && -x "$SCRIPT" ]]; then
    echo "  PASS"
else
    echo "  FAIL: $SCRIPT not found or not executable"
    FAILURES=$((FAILURES + 1))
fi

# ── Test 2: Dry-run produces output without errors ───────────────────
echo "TEST 2: Dry-run mode"
OUTPUT=$(PATH="${MOCK_DIR}:${PATH}" bash "$SCRIPT" --dry-run --provider all 2>&1) || {
    echo "  FAIL: script exited non-zero"
    echo "  OUTPUT: $OUTPUT"
    FAILURES=$((FAILURES + 1))
}
if echo "$OUTPUT" | grep -qiE "(change|detect|dry.run|no version)"; then
    echo "  PASS: dry-run produced expected output"
else
    echo "  FAIL: unexpected output: $OUTPUT"
    FAILURES=$((FAILURES + 1))
fi

# ── Test 3: Dry-run does not modify state file ──────────────────────
echo "TEST 3: Dry-run does not modify state"
STATE_FILE="${REPO_ROOT}/config/ai-tools/release-scan-state.yaml"
if [[ -f "$STATE_FILE" ]]; then
    BEFORE=$(md5sum "$STATE_FILE" | awk '{print $1}')
    PATH="${MOCK_DIR}:${PATH}" bash "$SCRIPT" --dry-run --provider all 2>&1 >/dev/null
    AFTER=$(md5sum "$STATE_FILE" | awk '{print $1}')
    if [[ "$BEFORE" == "$AFTER" ]]; then
        echo "  PASS: state file unchanged"
    else
        echo "  FAIL: state file was modified during dry-run"
        FAILURES=$((FAILURES + 1))
    fi
else
    echo "  SKIP: state file not found"
fi

# ── Test 4: --provider flag filters correctly ────────────────────────
echo "TEST 4: Provider filter"
OUTPUT=$(PATH="${MOCK_DIR}:${PATH}" bash "$SCRIPT" --dry-run --provider claude 2>&1) || true
if echo "$OUTPUT" | grep -qiE "(claude|no version)"; then
    echo "  PASS: provider filter works"
else
    echo "  FAIL: provider filter not working: $OUTPUT"
    FAILURES=$((FAILURES + 1))
fi

# ── Summary ──────────────────────────────────────────────────────────
echo ""
if [[ $FAILURES -eq 0 ]]; then
    echo "ALL TESTS PASSED"
    exit 0
else
    echo "FAILURES: $FAILURES"
    exit 1
fi
