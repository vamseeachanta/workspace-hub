#!/usr/bin/env bash
# audit-data-formats.sh — Detect structured data files using wrong format
# Rule: .claude/rules/coding-style.md §Data Format Selection
#
# Usage: bash scripts/work-queue/audit-data-formats.sh [--fix-counts]
#   --fix-counts  Show violation counts only (for CI gate)
#
# Exit codes: 0 = clean, 1 = violations found

set -euo pipefail
REPO_ROOT="$(git rev-parse --show-toplevel)"
ASSETS_DIR="${REPO_ROOT}/.claude/work-queue/assets"

RED='\033[0;31m'
YELLOW='\033[0;33m'
GREEN='\033[0;32m'
NC='\033[0m'

violations=0
warnings=0

log_violation() {
    echo -e "${RED}VIOLATION${NC}: $1"
    echo "  Current:     $2"
    echo "  Recommended: $3"
    echo "  Reason:      $4"
    ((violations++)) || true
}

log_warning() {
    echo -e "${YELLOW}WARNING${NC}: $1"
    ((warnings++)) || true
}

echo "=== Data Format Audit ==="
echo "Rule: YAML for agent-written structured data; Markdown for prose only"
echo ""

# 1. ac-test-matrix.md files (should be .yaml)
echo "--- AC Test Matrices ---"
while IFS= read -r -d '' f; do
    wrk=$(basename "$(dirname "$f")")
    log_violation "$wrk/ac-test-matrix.md" "Markdown table" "YAML list-of-dicts" \
        "Agent-written structured verdicts; MD tables silently corrupt"
done < <(find "${ASSETS_DIR}" -name "ac-test-matrix.md" -print0 2>/dev/null)

# 2. test-results.md files (should be .yaml)
echo ""
echo "--- Test Results ---"
while IFS= read -r -d '' f; do
    wrk=$(basename "$(dirname "$f")")
    log_violation "$wrk/test-results.md" "Markdown table" "YAML list-of-dicts" \
        "Structured PASS/FAIL data; YAML enables machine parsing"
done < <(find "${ASSETS_DIR}" -name "test-results.md" -print0 2>/dev/null)

# 3. tdd-test-results.md and variation-test-results.md
while IFS= read -r -d '' f; do
    wrk=$(basename "$(dirname "$f")")
    base=$(basename "$f")
    log_violation "$wrk/$base" "Markdown table" "YAML list-of-dicts" \
        "Structured test outcomes; should be YAML"
done < <(find "${ASSETS_DIR}" \( -name "tdd-test-results.md" -o -name "variation-test-results.md" \) -print0 2>/dev/null)

# 4. gate-evidence-summary.md alongside .json (redundant .md)
echo ""
echo "--- Gate Evidence (dual-format check) ---"
while IFS= read -r -d '' f; do
    json_sibling="${f%.md}.json"
    wrk=$(basename "$(dirname "$(dirname "$f")")")
    if [[ -f "$json_sibling" ]]; then
        log_warning "$wrk/gate-evidence-summary.md is redundant — .json exists as authoritative source"
    else
        log_violation "$wrk/gate-evidence-summary.md" "Markdown only" "JSON (script-generated)" \
            "Gate evidence is consumed programmatically; should be JSON"
    fi
done < <(find "${ASSETS_DIR}" -path "*/evidence/gate-evidence-summary.md" -print0 2>/dev/null)

# 5. legal-scan.md files (should be .yaml)
echo ""
echo "--- Legal Scan Results ---"
while IFS= read -r -d '' f; do
    wrk=$(basename "$(dirname "$f")")
    log_violation "$wrk/legal-scan.md" "Markdown prose" "YAML" \
        "Scan verdict (pass/fail + count) is structured; should be YAML"
done < <(find "${ASSETS_DIR}" -name "legal-scan.md" -print0 2>/dev/null)

# 6. Confirm correct formats (positive checks)
echo ""
echo "--- Correct Format Checks ---"
yaml_evidence=$(find "${ASSETS_DIR}" -path "*/evidence/*.yaml" 2>/dev/null | wc -l)
json_evidence=$(find "${ASSETS_DIR}" -path "*/evidence/*.json" 2>/dev/null | wc -l)
echo -e "${GREEN}OK${NC}: ${yaml_evidence} YAML evidence files (correct)"
echo -e "${GREEN}OK${NC}: ${json_evidence} JSON evidence files (correct)"

# Summary
echo ""
echo "=== Summary ==="
echo -e "Violations: ${RED}${violations}${NC}"
echo -e "Warnings:   ${YELLOW}${warnings}${NC}"

if [[ "${1:-}" == "--fix-counts" ]]; then
    echo ""
    echo "COUNTS_ONLY: violations=${violations} warnings=${warnings}"
fi

if [[ $violations -gt 0 ]]; then
    echo ""
    echo "To fix: migrate .md structured files to .yaml (WRK-1177)"
    echo "New files: use .yaml for structured data per .claude/rules/coding-style.md"
    exit 1
fi

exit 0
