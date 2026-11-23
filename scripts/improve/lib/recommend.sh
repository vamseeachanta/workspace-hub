#!/usr/bin/env bash
# recommend.sh — Phase 5.5: Surface recommendations to user
# 100% shell — reads classified improvements + ecosystem metrics, prints actionable summary

phase_recommend() {
    local guarded="${IMPROVE_WORKDIR}/guarded.json"
    local classified="${IMPROVE_WORKDIR}/classified.json"
    local metrics="${IMPROVE_WORKDIR}/ecosystem_metrics.json"
    local merged="${IMPROVE_WORKDIR}/merged_signals.jsonl"

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  /improve — Session Recommendations"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    # --- 1. Changes applied this session ---
    local changes_count
    changes_count=$(cat "${IMPROVE_WORKDIR}/changes_count" 2>/dev/null || echo "0")

    if [[ "$changes_count" -gt 0 ]] && [[ -f "$guarded" ]]; then
        echo ""
        echo "  Changes Applied (${changes_count}):"
        jq -r '.[] | "    \(.action): \(.target_file) — \(.reason // "n/a")"' "$guarded" 2>/dev/null
    fi

    # --- 2. Ecosystem health warnings ---
    if [[ -f "$metrics" ]]; then
        local warning_count
        warning_count=$(jq '.warnings | length' "$metrics" 2>/dev/null || echo "0")
        if [[ "$warning_count" -gt 0 ]]; then
            echo ""
            echo "  Ecosystem Warnings:"
            jq -r '.warnings[] | "    ! \(.)"' "$metrics" 2>/dev/null
        fi

        # Context budget check
        local memory_lines
        memory_lines=$(jq -r '.memory_lines // 0' "$metrics" 2>/dev/null || echo "0")
        if [[ "$memory_lines" -gt 150 ]]; then
            echo "    ! memory approaching limit: ${memory_lines}/200 lines"
        fi
    fi

    # --- 3. Skill gap recommendations ---
    _recommend_skills

    # --- 4. Tool/plugin recommendations ---
    _recommend_tools

    # --- 5. Quick stats ---
    local signal_count
    signal_count=$(cat "${IMPROVE_WORKDIR}/signal_count" 2>/dev/null || echo "0")
    local total_skills
    total_skills=$(jq -r '.total_skills // "?"' "$metrics" 2>/dev/null || echo "?")

    echo ""
    echo "  Stats: ${signal_count} signals processed | ${total_skills} active skills | ${changes_count} changes"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    return 0
}

# Analyze session signals for skill gaps
_recommend_skills() {
    local merged="${IMPROVE_WORKDIR}/merged_signals.jsonl"
    [[ ! -f "$merged" || ! -s "$merged" ]] && return 0

    local recommendations=()

    # Check for skill-candidate signals
    local skill_candidates
    skill_candidates=$(jq -sc '[.[] | select(.signal_source == "skill-candidates")]' "$merged" 2>/dev/null)
    local candidate_count
    candidate_count=$(echo "$skill_candidates" | jq 'length' 2>/dev/null || echo "0")

    if [[ "$candidate_count" -gt 0 ]]; then
        echo ""
        echo "  Skill Gaps Detected (${candidate_count}):"
        echo "$skill_candidates" | jq -r '.[] | "    + \(.name // .pattern // .description // "unnamed skill gap")"' 2>/dev/null
    fi

    # Check for repeated tool patterns that suggest missing skills
    local error_patterns
    error_patterns=$(jq -sc '[.[] | select(.signal_source == "errors")] | length' "$merged" 2>/dev/null || echo "0")
    if [[ "$error_patterns" -gt 3 ]]; then
        echo ""
        echo "  Suggestion: ${error_patterns} error signals detected — consider creating"
        echo "    a debugging skill for the recurring pattern."
    fi

    # Check for correction chains suggesting missing rules
    local correction_count
    correction_count=$(jq -sc '[.[] | select(.signal_source == "correction_chain")] | length' "$merged" 2>/dev/null || echo "0")
    if [[ "$correction_count" -gt 2 ]]; then
        echo ""
        echo "  Suggestion: ${correction_count} correction chains — repeated edits to same file."
        echo "    Consider adding a rule to .claude/rules/ to prevent these patterns."
    fi

    # Check for mature patterns not yet promoted to skills
    local mature_count
    mature_count=$(jq -sc '[.[] | select(.signal_source == "mature_pattern")] | length' "$merged" 2>/dev/null || echo "0")
    if [[ "$mature_count" -gt 0 ]]; then
        echo ""
        echo "  Mature Patterns Ready for Promotion (${mature_count}):"
        jq -r 'select(.signal_source == "mature_pattern") | "    * \(.pattern) (seen \(.sessions // "?") sessions)"' "$merged" 2>/dev/null
    fi
}

# Check for missing tools and recommend plugins
_recommend_tools() {
    local tool_warnings=()

    # Check essential tools
    if ! command -v jq &>/dev/null; then
        tool_warnings+=("jq (JSON processor) — required for signal processing")
    fi
    if ! command -v yq &>/dev/null; then
        tool_warnings+=("yq (YAML processor) — needed for model-registry and changelog")
    fi
    if ! command -v curl &>/dev/null; then
        tool_warnings+=("curl — required for Anthropic API calls in classify/apply phases")
    fi

    # Check AI CLIs
    if ! command -v codex &>/dev/null; then
        tool_warnings+=("codex CLI — required for cross-review hard gate")
    fi
    if ! command -v gemini &>/dev/null; then
        tool_warnings+=("gemini CLI — needed for cross-review (3-reviewer minimum)")
    fi

    # Check for MCP servers that could help
    local settings_file="${WORKSPACE_HUB}/.claude/settings.json"
    if [[ -f "$settings_file" ]]; then
        local mcp_count
        mcp_count=$(jq '.enabledMcpjsonServers | length' "$settings_file" 2>/dev/null || echo "0")
        if [[ "$mcp_count" -eq 0 ]]; then
            tool_warnings+=("MCP servers: none configured — consider filesystem, git, or web-search MCP plugins")
        fi
    fi

    # Check API credentials
    local has_oauth has_api_key
    has_oauth=$(jq -r '.claudeAiOauth.accessToken // empty' ~/.claude/.credentials.json 2>/dev/null)
    has_api_key="${ANTHROPIC_API_KEY:-}"
    if [[ -z "$has_oauth" && -z "$has_api_key" ]]; then
        tool_warnings+=("API credentials: neither OAuth token nor ANTHROPIC_API_KEY found — /improve API phases will be skipped")
    fi

    if [[ ${#tool_warnings[@]} -gt 0 ]]; then
        echo ""
        echo "  Tool/Plugin Recommendations:"
        for w in "${tool_warnings[@]}"; do
            echo "    > Install: ${w}"
        done
    fi
}
