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
