#!/usr/bin/env bash
# readiness.sh — Session start: lightweight verification
# Runs once per session (first tool call via PreToolUse)
# R4 (agent readiness) + R8 (environment) — quick checks only
# R1, R5, R6 are handled by ensure-readiness.sh at session EXIT
# Target: <100ms

# Drain stdin (PreToolUse hook receives tool input JSON)
if [[ ! -t 0 ]]; then
    cat > /dev/null 2>&1 || true
fi

# --- Configuration ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_HUB="${WORKSPACE_HUB:-$(cd "${SCRIPT_DIR}/../../.." && pwd)}"
STATE_DIR="${WORKSPACE_HUB}/.claude/state"

# Run once per session — lock file cleared by ensure-readiness.sh at stop
LOCK_FILE="${STATE_DIR}/.readiness-checked"
if [[ -f "$LOCK_FILE" ]]; then
    local_now=$(date +%s 2>/dev/null || echo "0")
    local_lock=$(date -r "$LOCK_FILE" +%s 2>/dev/null || echo "0")
    local_age=$(( local_now - local_lock ))
    [[ "$local_age" -lt 14400 ]] && exit 0
fi

mkdir -p "$STATE_DIR" 2>/dev/null

warnings=()
info=()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Surface last session's readiness report (from ensure-readiness.sh)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
REPORT_FILE="${STATE_DIR}/readiness-report.md"
if [[ -f "$REPORT_FILE" ]]; then
    # Check if report has warnings (not "All Clear")
    if grep -q "^## Warnings" "$REPORT_FILE" 2>/dev/null; then
        echo "Previous session flagged readiness issues:"
        # Extract warning lines
        sed -n '/^## Warnings/,/^## /{/^- /p}' "$REPORT_FILE" 2>/dev/null | head -5 | while IFS= read -r line; do
            echo "  ${line}"
        done
        # Extract fix suggestions
        sed -n '/^## Suggested Fixes/,/^## /{/^  Action:/p}' "$REPORT_FILE" 2>/dev/null | head -3 | while IFS= read -r line; do
            echo "  ${line}"
        done
    fi
fi

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# R3: Agent Capacity Pre-flight (WRK-179)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
check_agent_capacity() {
    local quota_file="${WORKSPACE_HUB}/config/ai-tools/agent-quota-latest.json"
    [[ ! -f "$quota_file" ]] && return
    command -v jq &>/dev/null || return

    # Warn if cache is stale (>4h)
    local now_epoch file_epoch age_hours
    now_epoch=$(date +%s 2>/dev/null || echo "0")
    file_epoch=$(date -r "$quota_file" +%s 2>/dev/null || echo "0")
    age_hours=$(( (now_epoch - file_epoch) / 3600 ))
    [[ "$age_hours" -gt 4 ]] && info+=("Quota: cache is ${age_hours}h old — run query-quota.sh --refresh")

    # Check each provider's weekly utilization
    local congested=""
    while IFS=$'\t' read -r provider week_pct sonnet_pct; do
        [[ -z "$provider" || "$week_pct" == "null" ]] && continue
        local effective_pct="$week_pct"
        # For Claude, use the tighter of week_pct / sonnet_pct
        if [[ "$provider" == "claude" && "$sonnet_pct" != "null" && -n "$sonnet_pct" ]]; then
            local sp="${sonnet_pct%.*}" wp="${week_pct%.*}"
            effective_pct=$(( sp > wp ? sp : wp ))
        else
            effective_pct="${week_pct%.*}"
        fi
        if [[ "$effective_pct" -ge 90 ]]; then
            warnings+=("Quota: ${provider} at ${effective_pct}% weekly — route tasks to alternative provider")
            congested="${congested} ${provider}"
        elif [[ "$effective_pct" -ge 70 ]]; then
            info+=("Quota: ${provider} at ${effective_pct}% weekly — approaching limit")
        fi
    done < <(jq -r '.agents[] | [.provider, (.week_pct // "null" | tostring), (.sonnet_pct // "null" | tostring)] | @tsv' "$quota_file" 2>/dev/null)

    # Routing suggestion if primary provider congested
    if [[ -n "$congested" ]]; then
        fixes+=("  Action: Use scripts/work-queue/assign-providers.sh to find available alternatives")
        fixes+=("  Or: Set WRK provider field to 'codex' or 'gemini' for pending tasks")
    fi
}

check_agent_capacity

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# R4: Agent Readiness (quick CLI check)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
agents_available=0
agents_missing=""
command -v claude &>/dev/null && agents_available=$((agents_available + 1)) || agents_missing="${agents_missing} claude"
command -v codex &>/dev/null && agents_available=$((agents_available + 1)) || agents_missing="${agents_missing} codex"
command -v gemini &>/dev/null && agents_available=$((agents_available + 1)) || agents_missing="${agents_missing} gemini"

if [[ -n "$agents_missing" ]]; then
    warnings+=("Agents: missing:${agents_missing}")
fi

# Check model registry freshness
registry="${WORKSPACE_HUB}/config/agents/model-registry.yaml"
if [[ -f "$registry" ]]; then
    now_epoch=$(date +%s 2>/dev/null || echo "0")
    reg_epoch=$(date -r "$registry" +%s 2>/dev/null || echo "0")
    reg_age=$(( (now_epoch - reg_epoch) / 86400 ))
    [[ "$reg_age" -gt 30 ]] && warnings+=("Agents: model-registry ${reg_age}d old — run update-model-ids.sh")
fi

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# R8: Environment (quick tool check)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
missing_tools=""
command -v jq &>/dev/null || missing_tools="${missing_tools} jq"
command -v curl &>/dev/null || missing_tools="${missing_tools} curl"
[[ -n "$missing_tools" ]] && warnings+=("Missing required:${missing_tools}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Output (only if issues found)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if [[ ${#warnings[@]} -gt 0 ]]; then
    echo "Startup Checks (${#warnings[@]} issues):"
    for w in "${warnings[@]}"; do
        echo "  ! ${w}"
    done
fi

touch "$LOCK_FILE" 2>/dev/null
exit 0
