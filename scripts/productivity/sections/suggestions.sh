#!/usr/bin/env bash
# ABOUTME: Daily log section — aggregates signals from cron outputs into 3-5 actionable suggestions
# Usage: bash suggestions.sh <WORKSPACE_ROOT>

set -euo pipefail
WORKSPACE_ROOT="${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)}"
LOGS="$WORKSPACE_ROOT/logs/quality"

echo "## Suggestions"
echo ""

suggestions=()
# ── 1. Benchmark regressions ────────────────────────────────────────────────
latest_bench=$(ls -t "$LOGS"/benchmark-*.log 2>/dev/null | head -1)
if [[ -n "$latest_bench" ]]; then
    reg_count=$(grep -ci "REGRESSION" "$latest_bench" 2>/dev/null) || reg_count=0
    if [[ "$reg_count" -gt 0 ]]; then
        suggestions+=("[perf] $reg_count benchmark regression(s) detected — review $(basename "$latest_bench") and investigate before next release.")
    fi
fi

# ── 2. Dependency health ────────────────────────────────────────────────────
dep_log="$LOGS/dep-health-cron.log"
if [[ -f "$dep_log" ]]; then
    stale=$(grep -ci "STALE\|OUTDATED" "$dep_log" 2>/dev/null) || stale=0
    cve=$(grep -ci "CVE" "$dep_log" 2>/dev/null) || cve=0
    if [[ "$cve" -gt 0 ]]; then
        suggestions+=("[deps] $cve CVE reference(s) in dep-health log — run dependency audit and patch affected packages.")
    elif [[ "$stale" -gt 0 ]]; then
        suggestions+=("[deps] $stale stale/outdated dependency flag(s) — schedule a dependency refresh cycle.")
    fi
fi

# ── 3. Doc drift ────────────────────────────────────────────────────────────
latest_drift=$(ls -t "$LOGS"/doc-drift-*.yaml 2>/dev/null | head -1)
if [[ -n "$latest_drift" ]]; then
    high_drift=$(grep -cE "score:\s*0\.(8[0-9]|9[0-9])|score:\s*1\.0" "$latest_drift" 2>/dev/null) || high_drift=0
    if [[ "$high_drift" -gt 0 ]]; then
        suggestions+=("[docs] $high_drift file(s) with doc-drift score above 0.8 — update docs to match recent code changes.")
    fi
fi

# ── 4. Stale branches ──────────────────────────────────────────────────────
stale_branches=$(cd "$WORKSPACE_ROOT" && git branch --merged main 2>/dev/null \
    | grep -cv '^\*\|main$\|master$' 2>/dev/null) || stale_branches=0
if [[ "$stale_branches" -gt 2 ]]; then
    suggestions+=("[hygiene] $stale_branches merged branches still exist locally — clean up with git branch -d.")
fi

# ── 5. Failed cron jobs ────────────────────────────────────────────────────
recent_errors=0
for logfile in "$LOGS"/*.log; do
    [[ -f "$logfile" ]] || continue
    if [[ $(find "$logfile" -mtime -2 2>/dev/null) ]]; then
        errs=$(grep -ci "ERROR\|FAIL" "$logfile" 2>/dev/null) || errs=0
        recent_errors=$((recent_errors + errs))
    fi
done
if [[ "$recent_errors" -gt 0 ]]; then
    suggestions+=("[hygiene] $recent_errors ERROR/FAIL occurrence(s) in recent quality logs — check logs/quality/ for failing cron jobs.")
fi

# ── 6. Unread research ─────────────────────────────────────────────────────
research_dir="$WORKSPACE_ROOT/.planning/research"
if [[ -d "$research_dir" ]]; then
    new_research=$(find "$research_dir" -name "*.md" -not -name ".gitkeep" -mtime -1 2>/dev/null | wc -l | tr -d ' ')
    if [[ "$new_research" -gt 0 ]]; then
        suggestions+=("[docs] $new_research new overnight research file(s) in .planning/research/ — review findings and promote action items.")
    fi
fi

# ── Render ──────────────────────────────────────────────────────────────────
if [[ ${#suggestions[@]} -eq 0 ]]; then
    echo "_No actionable suggestions today — all signals green._"
else
    for i in "${!suggestions[@]}"; do
        echo "$((i + 1)). ${suggestions[$i]}"
    done
fi
echo ""
