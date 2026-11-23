#!/usr/bin/env bash
# ABOUTME: Daily log section — data health status across tier-1 repositories
# ABOUTME: Checks test coverage, data index freshness, spec completeness, git status
# Usage: bash data-health.sh <WORKSPACE_ROOT>

set -euo pipefail
WORKSPACE_ROOT="${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)}"

echo "## Data Health"
echo ""

# ── Tier-1 repository definitions ────────────────────────────────────────────
declare -A REPOS=(
    [workspace-hub]="$WORKSPACE_ROOT"
    [assethold]="$WORKSPACE_ROOT/assethold"
    [assetutilities]="$WORKSPACE_ROOT/assetutilities"
    [digitalmodel]="$WORKSPACE_ROOT/digitalmodel"
    [worldenergydata]="$WORKSPACE_ROOT/worldenergydata"
)

# ── Git status per repo ───────────────────────────────────────────────────────
echo "### Repository Status"
echo ""
echo "| Repo | Branch | Dirty | Unpushed | Last Commit |"
echo "|------|--------|-------|----------|-------------|"

for name in workspace-hub assethold assetutilities digitalmodel worldenergydata; do
    dir="${REPOS[$name]}"
    if [[ ! -d "$dir/.git" ]] && [[ ! -f "$dir/.git" ]]; then
        echo "| $name | — | — | — | _not found_ |"
        continue
    fi
    branch=$(cd "$dir" && git branch --show-current 2>/dev/null || echo "?")
    dirty=$(cd "$dir" && git status --porcelain 2>/dev/null | wc -l | tr -d ' ')
    unpushed=$(cd "$dir" && git log --oneline "@{u}.." 2>/dev/null | wc -l | tr -d ' ') || unpushed="?"
    last=$(cd "$dir" && git log -1 --format="%as" 2>/dev/null || echo "?")
    dirty_icon="${dirty}"
    [[ "$dirty" -gt 0 ]] 2>/dev/null && dirty_icon="⚠ $dirty" || dirty_icon="✓ 0"
    echo "| $name | $branch | $dirty_icon | $unpushed | $last |"
done
echo ""

# ── Test health per repo ──────────────────────────────────────────────────────
echo "### Test Coverage Snapshot"
echo ""
echo "| Repo | Test Files | Last Run |"
echo "|------|-----------|---------|"

for name in assethold assetutilities digitalmodel worldenergydata; do
    dir="${REPOS[$name]}"
    [[ ! -d "$dir" ]] && echo "| $name | — | _not found_ |" && continue
    test_count=$(find "$dir/tests" -name "test_*.py" -o -name "*_test.py" 2>/dev/null | wc -l | tr -d ' ')
    # find most recent test result file
    last_result=$(find "$dir" -name ".pytest_cache" -maxdepth 3 2>/dev/null | head -1)
    if [[ -n "$last_result" ]]; then
        last_run=$(stat -c %y "$last_result" 2>/dev/null | cut -d' ' -f1 || echo "?")
    else
        last_run="never"
    fi
    echo "| $name | $test_count | $last_run |"
done
echo ""

# ── Data index health ─────────────────────────────────────────────────────────
INDEX_FILE="$WORKSPACE_ROOT/data/document-index/index.jsonl"
REGISTRY_FILE="$WORKSPACE_ROOT/data/document-index/registry.yaml"
echo "### Document Index"
echo ""
if [[ -f "$INDEX_FILE" ]]; then
    record_count=$(wc -l < "$INDEX_FILE" | tr -d ' ')
    index_age=$(( ( $(date +%s) - $(stat -c %Y "$INDEX_FILE" 2>/dev/null || echo 0) ) / 86400 ))
    echo "- Records: $record_count"
    echo "- Index age: ${index_age}d"
else
    echo "- Index: _not found_"
fi
if [[ -f "$REGISTRY_FILE" ]]; then
    source_count=$(grep -c "^  [a-z]" "$REGISTRY_FILE" 2>/dev/null || echo 0)
    echo "- Registered sources: $source_count"
fi
echo ""

# ── Spec completeness ─────────────────────────────────────────────────────────
SPEC_DIR="$WORKSPACE_ROOT/specs/data-sources"
echo "### Data-Source Specs"
echo ""
if [[ -d "$SPEC_DIR" ]]; then
    total_specs=$(find "$SPEC_DIR" -name "*.yaml" 2>/dev/null | wc -l | tr -d ' ')
    echo "- Spec files: $total_specs"
    # list them
    find "$SPEC_DIR" -name "*.yaml" 2>/dev/null | sort | while read -r f; do
        base=$(basename "$f" .yaml)
        age=$(( ( $(date +%s) - $(stat -c %Y "$f" 2>/dev/null || echo 0) ) / 86400 ))
        echo "  - $base (${age}d ago)"
    done
else
    echo "_No data-source specs directory_"
fi
echo ""
