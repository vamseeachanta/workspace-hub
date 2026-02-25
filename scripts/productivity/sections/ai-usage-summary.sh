#!/usr/bin/env bash
# ABOUTME: Daily log section — AI agent usage summary (tool versions, sessions, models)
# Usage: bash ai-usage-summary.sh <WORKSPACE_ROOT>

set -euo pipefail
WORKSPACE_ROOT="${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)}"
STATUS_FILE="$WORKSPACE_ROOT/config/ai_agents/ai-tools-status.yaml"
PIPELINE_FILE="$WORKSPACE_ROOT/.claude/work-queue/pipeline-state.yaml"

echo "## AI Agent Usage Summary"
echo ""

# ── Tool Versions ─────────────────────────────────────────────────────────────
echo "### Tool Versions"
echo ""
if [[ -f "$STATUS_FILE" ]]; then
    updated=$(grep "^last_updated:" "$STATUS_FILE" | awk '{print $2}' | tr -d '"')
    echo "_Last checked: ${updated}_"
    echo ""
    echo "| Machine | Node | Claude | Codex | Gemini | gh | Status |"
    echo "|---------|------|--------|-------|--------|----|--------|"
    for host in ace-linux-1 ace-linux-2 acma-ansys05; do
        hfile="$WORKSPACE_ROOT/config/ai_agents/status/$host.yaml"
        [[ ! -f "$hfile" ]] && continue
        status=$(grep "^status:" "$hfile" | awk '{print $2}')
        node=$(awk  '/^versions:/{f=1} f && /  node:/{  print $2; exit}' "$hfile" | tr -d '"')
        claude=$(awk '/^versions:/{f=1} f && /  claude:/{print $2; exit}' "$hfile" | tr -d '"')
        codex=$(awk  '/^versions:/{f=1} f && /  codex:/{  print $2; exit}' "$hfile" | tr -d '"')
        gemini=$(awk '/^versions:/{f=1} f && /  gemini:/{print $2; exit}' "$hfile" | tr -d '"')
        gh=$(awk     '/^versions:/{f=1} f && /  gh:/{    print $2; exit}' "$hfile" | tr -d '"')
        icon="✓"; [[ "$status" == "needs-update" ]] && icon="⚠"; [[ "$status" == "manual-check-required" ]] && icon="?"
        echo "| $host | ${node:----} | ${claude:----} | ${codex:----} | ${gemini:----} | ${gh:----} | $icon $status |"
    done
else
    echo "_Not found — run: bash scripts/maintenance/ai-tools-status.sh_"
fi
echo ""

# ── Active Sessions ───────────────────────────────────────────────────────────
echo "### Active Sessions & Workload"
echo ""
if [[ -f "$PIPELINE_FILE" ]]; then
    session_count=$(grep -c "session_id:" "$PIPELINE_FILE" 2>/dev/null || echo 0)
    active_wrk=$(grep "active_wrk:" "$PIPELINE_FILE" | awk '{print $2}' | tr -d '"' | grep -v '^$\|null' || true)
    echo "- Registered sessions: $session_count"
    echo "- Active WRK: ${active_wrk:-none}"
else
    echo "_No pipeline state_"
fi
echo ""

# ── Models in Use ─────────────────────────────────────────────────────────────
echo "### Models in Use"
echo ""
echo "| Tool | Model | Usage Notes |"
echo "|------|-------|-------------|"
echo "| claude | claude-sonnet-4-6 | Default; Opus 4.6 for Route C planning only |"
echo "| codex | gpt-5.3-codex | Cross-review hard gate |"
echo "| gemini | gemini-2.5-pro | Secondary review; \`echo content | gemini -p \"prompt\" -y\` |"
echo ""

# ── Weekly Usage Remaining ────────────────────────────────────────────────────
# Source priority: ~/.cache/agent-quota.json (fresh, written by query-quota.sh)
#                  config/ai-tools/agent-quota-latest.json (workspace, updated by statusline/cron)
USER_QUOTA_CACHE="$HOME/.cache/agent-quota.json"
WORKSPACE_QUOTA="$WORKSPACE_ROOT/config/ai-tools/agent-quota-latest.json"
CACHE_TTL=900  # 15 min

echo "### Weekly Usage Remaining"
echo ""

# Pick freshest available file
quota_file=""
if [[ -f "$USER_QUOTA_CACHE" ]]; then
    age=$(( $(date +%s) - $(stat -c %Y "$USER_QUOTA_CACHE" 2>/dev/null || echo 0) ))
    if (( age < CACHE_TTL * 8 )); then   # within 2 hours — fresh enough for daily log
        quota_file="$USER_QUOTA_CACHE"
    fi
fi
[[ -z "$quota_file" && -f "$WORKSPACE_QUOTA" ]] && quota_file="$WORKSPACE_QUOTA"

if [[ -n "$quota_file" ]]; then
    python3 - "$quota_file" <<'PYEOF'
import json, sys, os, time

with open(sys.argv[1]) as f:
    data = json.load(f)

ts   = data.get("timestamp", "")
src  = os.path.basename(sys.argv[1])
age  = int(time.time() - os.path.getmtime(sys.argv[1]))
age_label = f"{age//60}m ago" if age < 3600 else f"{age//3600}h ago"
print(f"_Source: {src}  |  Updated: {ts} ({age_label})_")
print("")
print("| Agent | % Used | % Remaining | Bar | Resets In | Notes |")
print("|-------|--------|-------------|-----|-----------|-------|")

BARS  = "▓▓▓▓▓▓▓▓▓▓"
EMPTY = "░░░░░░░░░░"

def bar(pct_used):
    filled = min(10, round(float(pct_used) / 10))
    return BARS[:filled] + EMPTY[filled:]

def hrs_label(entry):
    h = entry.get("hours_to_reset")
    if h is not None:
        return f"{h}h"
    resets = entry.get("resets_at", "")
    return resets[:10] if resets else "—"

def warn(pct_used):
    if pct_used >= 80: return "⚠ high"
    if pct_used >= 50: return "⬆ moderate"
    return ""

for agent in data.get("agents", []):
    prov = agent.get("provider", "?")

    # Support both formats: week_pct (% used) and pct_remaining
    if "week_pct" in agent:
        pct_used = float(agent["week_pct"] or 0)
        remaining = 100 - pct_used
    else:
        remaining = float(agent.get("pct_remaining") or 0)
        pct_used  = 100 - remaining

    notes = warn(pct_used)
    if prov == "claude":
        s = agent.get("sonnet_pct")
        if s is not None:
            notes += f" sonnet {s:.0f}% used"
        reqs = agent.get("approx_requests")
        if reqs:
            notes += f" ~{reqs} reqs"

    print(f"| {prov} | {pct_used:.0f}% | {remaining:.0f}% | {bar(pct_used)} | {hrs_label(agent)} | {notes} |")
PYEOF
else
    QUERY_SCRIPT="$WORKSPACE_ROOT/scripts/ai/assessment/query-quota.sh"
    if [[ -x "$QUERY_SCRIPT" ]]; then
        echo "_No cached quota — running query-quota.sh_"
        echo ""
        bash "$QUERY_SCRIPT" 2>/dev/null || echo "_query-quota.sh failed_"
    else
        echo "_No quota data — run: bash scripts/ai/assessment/query-quota.sh_"
    fi
fi
