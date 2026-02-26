#!/usr/bin/env bash
# ABOUTME: Daily log section — session analysis status and findings summary
# ABOUTME: Reads latest session-analysis report + skill-scores.yaml + signal counts
# Usage: bash session-analysis.sh <WORKSPACE_ROOT>

set -euo pipefail
WORKSPACE_ROOT="${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)}"
SA_DIR="$WORKSPACE_ROOT/.claude/state/session-analysis"
SKILL_SCORES="$WORKSPACE_ROOT/.claude/state/skill-scores.yaml"
SIGNALS_DIR="$WORKSPACE_ROOT/.claude/state/session-signals"

echo "## Session Analysis"
echo ""

# ── Latest report ─────────────────────────────────────────────────────────────
latest_report=$(ls "$SA_DIR"/*.md 2>/dev/null | grep -v bootstrap | sort | tail -1)

if [[ -z "$latest_report" ]]; then
    echo "_No session analysis reports found — runs nightly at 3AM_"
    echo ""
else
    report_date=$(basename "$latest_report" .md)
    echo "### Latest Report: $report_date"
    echo ""

    # Extract key metrics from report
    sessions=$(grep "^Sessions analysed:" "$latest_report" | awk '{print $NF}')
    skills_scored=$(grep "^Skills scored:" "$latest_report" | awk '{print $NF}')
    candidates=$(grep "^Candidates identified:" "$latest_report" | sed 's/Candidates identified: //')
    anti_patterns=$(grep "^Anti-patterns detected:" "$latest_report" | awk '{print $NF}')
    gaps=$(grep "^Deep gaps:" "$latest_report" | awk '{print $NF}')
    quality=$(grep -A1 "## Quality Metric" "$latest_report" | tail -1 | sed 's/^[[:space:]]*//')

    echo "| Metric | Value |"
    echo "|--------|-------|"
    echo "| Sessions analysed | ${sessions:-0} |"
    echo "| Skills scored | ${skills_scored:-0} |"
    echo "| Candidates | ${candidates:-none} |"
    echo "| Anti-patterns | ${anti_patterns:-0} |"
    echo "| Deep gaps | ${gaps:-0} |"
    echo ""

    # Anti-patterns
    anti_section=$(awk '/^## Anti-patterns/,/^## /' "$latest_report" \
        | grep -v "^## " | grep -v "^$" | head -5 || true)
    if [[ -n "$anti_section" ]]; then
        echo "**Anti-patterns detected:**"
        echo "$anti_section" | while IFS= read -r line; do echo "- $line"; done
        echo ""
    fi

    # Quality metric
    [[ -n "$quality" && "$quality" != "_No sessions to analyse._" ]] \
        && echo "**Quality:** $quality" && echo ""
fi

# ── Signal file coverage ──────────────────────────────────────────────────────
echo "### Signal Coverage"
echo ""
if [[ -d "$SIGNALS_DIR" ]]; then
    total_signals=$(ls "$SIGNALS_DIR"/*.jsonl 2>/dev/null | wc -l)
    recent_signals=$(find "$SIGNALS_DIR" -name "*.jsonl" -mtime -7 2>/dev/null | wc -l)
    echo "- Total signal files: $total_signals"
    echo "- Last 7 days: $recent_signals"
    latest_signal=$(ls "$SIGNALS_DIR"/*.jsonl 2>/dev/null | sort | tail -1 | xargs basename 2>/dev/null || echo "none")
    echo "- Latest: $latest_signal"
else
    echo "_No signals directory_"
fi
echo ""

# ── Top skills by usage ───────────────────────────────────────────────────────
echo "### Top Skills by Usage"
echo ""
if [[ -f "$SKILL_SCORES" ]]; then
    python3 - "$SKILL_SCORES" <<'PYEOF'
import sys, re

scores = {}
current_skill = None
with open(sys.argv[1]) as f:
    for line in f:
        m = re.match(r'^  ([a-z][a-zA-Z0-9_-]+):$', line)
        if m:
            current_skill = m.group(1)
            scores[current_skill] = {}
        elif current_skill and ':' in line:
            k, _, v = line.strip().partition(':')
            scores[current_skill][k.strip()] = v.strip()

def to_int(val):
    """Convert YAML value to int, stripping inline comments and whitespace."""
    if not val:
        return 0
    return int(str(val).split('#')[0].strip() or 0)

rows = []
for skill, data in scores.items():
    calls = to_int(data.get('calls_in_period', 0))
    sessions = to_int(data.get('sessions_in_period', 0))
    last = data.get('last_seen', '—').strip('"')
    if calls > 0:
        rows.append((calls, sessions, skill, last))

rows.sort(reverse=True)
print("| Skill | Calls | Sessions | Last Seen |")
print("|-------|-------|----------|-----------|")
for calls, sessions, skill, last in rows[:8]:
    print(f"| {skill} | {calls} | {sessions} | {last} |")
PYEOF
else
    echo "_skill-scores.yaml not found_"
fi
echo ""

# ── Historical trend (reports available) ─────────────────────────────────────
echo "### Analysis History"
echo ""
for f in $(ls "$SA_DIR"/*.md 2>/dev/null | grep -v bootstrap | sort | tail -5); do
    d=$(basename "$f" .md)
    sessions=$(grep "^Sessions analysed:" "$f" 2>/dev/null | awk '{print $NF}' || echo "?")
    ap=$(grep "^Anti-patterns detected:" "$f" 2>/dev/null | awk '{print $NF}' || echo "0")
    echo "- **$d**: sessions=$sessions  anti-patterns=$ap"
done
