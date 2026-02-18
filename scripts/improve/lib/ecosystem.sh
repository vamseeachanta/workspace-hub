#!/usr/bin/env bash
# ecosystem.sh — Phase 3: Filesystem health checks + API analysis
# 70% shell, 30% API

phase_ecosystem() {
    local metrics="${IMPROVE_WORKDIR}/ecosystem_metrics.json"

    # --- Shell-based metrics collection ---
    local total_skills=0 archived_skills=0 memory_lines=0 rules_lines=0
    local skill_dir="${WORKSPACE_HUB}/.claude/skills"
    local memory_dir="${WORKSPACE_HUB}/.claude/memory"
    local rules_dir="${WORKSPACE_HUB}/.claude/rules"

    # Count active skills (SKILL.md files, excluding _archive)
    if [[ -d "$skill_dir" ]]; then
        total_skills=$(find "$skill_dir" -name "SKILL.md" -not -path "*/_archive/*" 2>/dev/null | wc -l | tr -d ' ')
        archived_skills=$(find "$skill_dir/_archive" -name "SKILL.md" 2>/dev/null | wc -l | tr -d ' ')
    fi

    # Count memory lines
    if [[ -d "$memory_dir" ]]; then
        memory_lines=$(find "$memory_dir" -name "*.md" -exec wc -l {} + 2>/dev/null | tail -1 | awk '{print $1}')
        memory_lines="${memory_lines:-0}"
    fi

    # Count rules lines
    if [[ -d "$rules_dir" ]]; then
        rules_lines=$(find "$rules_dir" -name "*.md" -exec wc -l {} + 2>/dev/null | tail -1 | awk '{print $1}')
        rules_lines="${rules_lines:-0}"
    fi

    # Check pending signal backlog
    local pending_signals=0
    for f in "${REVIEW_DIR}"/*.jsonl; do
        [[ -f "$f" && -s "$f" ]] && pending_signals=$((pending_signals + $(wc -l < "$f" | tr -d ' ')))
    done

    # Write metrics
    jq -n \
        --argjson total_skills "$total_skills" \
        --argjson archived_skills "$archived_skills" \
        --argjson memory_lines "$memory_lines" \
        --argjson rules_lines "$rules_lines" \
        --argjson pending_signals "$pending_signals" \
        --arg timestamp "$TIMESTAMP" \
        '{
            timestamp: $timestamp,
            total_skills: $total_skills,
            archived_skills: $archived_skills,
            archived_ratio: (if $total_skills > 0 then ($archived_skills / ($total_skills + $archived_skills) * 100 | floor) else 0 end),
            memory_lines: $memory_lines,
            rules_lines: $rules_lines,
            pending_signals: $pending_signals,
            warnings: [
                (if $total_skills > 350 then "skill_sprawl: \($total_skills) active skills (threshold: 350)" else empty end),
                (if $memory_lines > 800 then "memory_bloat: \($memory_lines) total lines across memory files" else empty end),
                (if $pending_signals > 50 then "signal_backlog: \($pending_signals) unprocessed signals" else empty end)
            ]
        }' > "$metrics" 2>/dev/null

    local warning_count
    warning_count=$(jq '.warnings | length' "$metrics" 2>/dev/null || echo "0")
    echo "improve/ecosystem: ${total_skills} skills, ${memory_lines} memory lines, ${warning_count} warnings"

    return 0
}
