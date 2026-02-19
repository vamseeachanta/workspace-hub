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
                (if $memory_lines > 800 then "memory_bloat: \($memory_lines) total lines across memory files" else empty end),
                (if $pending_signals > 50 then "signal_backlog: \($pending_signals) unprocessed signals" else empty end)
            ]
        }' > "$metrics" 2>/dev/null

    local warning_count
    warning_count=$(jq '.warnings | length' "$metrics" 2>/dev/null || echo "0")
    echo "improve/ecosystem: ${total_skills} skills, ${memory_lines} memory lines, ${warning_count} warnings"

    # --- Bidirectional skill-link audit ---
    # Find related_skills: entries in hub SKILL.md files and check for asymmetry.
    # If A lists B in related_skills: but B does not list A, emit as improvement candidate.
    local skills_dir="${WORKSPACE_HUB}/.claude/skills"
    declare -A skill_refs
    local skill_file skill_path rel_skill

    # Build map: skill-path → space-separated related_skills values
    while IFS= read -r skill_file; do
        skill_path="${skill_file%/SKILL.md}"
        skill_path="${skill_path#${skills_dir}/}"
        # Extract related_skills: list items (handles both "- item" and "[ item, item ]" YAML)
        local refs
        refs=$(awk '/^related_skills:/,/^[a-z]/' "$skill_file" 2>/dev/null | \
               grep -oE '[a-z][a-z0-9/-]+' | grep -v 'related_skills' || true)
        [[ -n "$refs" ]] && skill_refs["$skill_path"]="$refs"
    done < <(find "$skills_dir" -name "SKILL.md" -not -path "*/_archive/*" -not -path "*/_diverged/*" 2>/dev/null)

    local asymmetric=0
    for src_path in "${!skill_refs[@]}"; do
        for tgt_ref in ${skill_refs[$src_path]}; do
            # Check if target skill exists and lists source in its related_skills
            local tgt_file="${skills_dir}/${tgt_ref}/SKILL.md"
            [[ ! -f "$tgt_file" ]] && continue
            if ! grep -q "$src_path" "$tgt_file" 2>/dev/null; then
                asymmetric=$((asymmetric + 1))
                printf '{"timestamp":"%s","type":"skill","signal":"Missing back-link: %s should list %s in related_skills","severity":"info","source":"ecosystem-asymmetric-audit","auto_apply":true,"score":0.7}\n' \
                    "$TIMESTAMP" "$tgt_ref" "$src_path" >> "${REVIEW_DIR}/skill-candidates.jsonl" 2>/dev/null || true
            fi
        done
    done

    [[ "$asymmetric" -gt 0 ]] && echo "improve/ecosystem: ${asymmetric} asymmetric skill link(s) found — emitted to skill-candidates.jsonl"

    return 0
}
