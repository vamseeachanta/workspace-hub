#!/usr/bin/env bash
# ABOUTME: Daily log section — roll-up outcomes from comprehensive-learning pipeline
# Usage: bash learning-outcomes.sh <WORKSPACE_ROOT>

set -euo pipefail
WORKSPACE_ROOT="${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)}"
REPORTS_DIR="$WORKSPACE_ROOT/.claude/state/learning-reports"

echo "## Learning Outcomes & Ecosystem Trends"
echo ""

# Locate the most recent report
latest_report=$(ls -t "$REPORTS_DIR"/*.md 2>/dev/null | head -n 1)

if [[ -z "$latest_report" ]]; then
    echo "_No comprehensive learning reports found — run /comprehensive-learning to generate._"
    echo ""
    exit 0
fi

report_date=$(basename "$latest_report" .md)
echo "### Latest Pipeline Run: $report_date"
echo ""

# 1. Orchestrator Compliance
skips=$(grep "Gate-skips:" "$latest_report" | sed -E 's/.*Gate-skips: ([0-9]+).*/\1/' || echo "0")
drift=$(grep "Scope-drift:" "$latest_report" | sed -E 's/.*Scope-drift: ([0-9]+).*/\1/' || echo "0")

echo "**Orchestrator Compliance:**"
if [[ "$skips" -gt 0 || "$drift" -gt 0 ]]; then
    [[ "$skips" -gt 0 ]] && echo "- ⚠ **Gate Skips:** $skips detected"
    [[ "$drift" -gt 0 ]] && echo "- ⚠ **Scope Drift:** $drift detected"
else
    echo "- ✅ All orchestrators compliant with WRK-624 gates."
fi
echo ""

# 2. Work Quality & System Health
tdd_rate=$(grep "TDD pairing rate:" "$latest_report" | sed -E 's/.*TDD pairing rate: ([0-9]+%).*/\1/' || echo "unknown")
ri_coverage=$(grep "Resource Intelligence Coverage:" "$latest_report" | sed -E 's/.*Resource Intelligence Coverage: ([0-9]+%).*/\1/' || echo "unknown")
stale_mem=$(grep "Stale memory entries:" "$latest_report" | sed -E 's/.*Stale memory entries: ([0-9]+).*/\1/' || echo "0")
readiness=$(grep "AI agent readiness:" "$latest_report" | sed -E 's/.*AI agent readiness: (.*)/\1/' || echo "unknown")

echo "**Quality & Health Metrics:**"
echo "- **TDD Pairing Rate:** $tdd_rate"
echo "- **Resource Intelligence:** $ri_coverage coverage"
echo "- **Memory Staleness:** $stale_mem entries flagged"
echo "- **AI Readiness:** $readiness"
echo ""

# 3. Ecosystem Improvement Trends (Action Candidates)
echo "**Improvement Candidates:**"
candidates=$(sed -n '/Improvement Trends:/,/^$/p' "$latest_report" | grep "^-" | head -5 || true)
if [[ -n "$candidates" ]]; then
    echo "$candidates"
else
    echo "- No new improvement candidates identified this run."
fi
echo ""
