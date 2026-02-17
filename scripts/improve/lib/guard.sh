#!/usr/bin/env bash
# guard.sh — Phase 4: Safety checks before writing
# 100% shell, 0% API

phase_guard() {
    local classified="${IMPROVE_WORKDIR}/classified.json"
    local guarded="${IMPROVE_WORKDIR}/guarded.json"

    # If no classified improvements (quick mode or API failure), check ecosystem warnings
    if [[ ! -f "$classified" || ! -s "$classified" ]] || [[ "$(jq 'length' "$classified" 2>/dev/null)" == "0" ]]; then
        # In quick mode, still pass through if there are ecosystem warnings to log
        echo "[]" > "$guarded"
        echo "0" > "${IMPROVE_WORKDIR}/changes_count"
        echo "improve/guard: no improvements to guard"
        return 0
    fi

    local accepted=0 rejected=0

    # Filter improvements through safety checks
    jq -c '.[]' "$classified" | while IFS= read -r item; do
        local target_file action score
        target_file=$(echo "$item" | jq -r '.target_file // ""')
        action=$(echo "$item" | jq -r '.action // ""')
        score=$(echo "$item" | jq -r '.score // 0')

        local reject_reason=""

        # --- Score threshold ---
        if (( $(echo "$score < 0.6" | bc -l 2>/dev/null || echo "1") )); then
            reject_reason="score_below_threshold"
        fi

        # --- Size guard: check target file won't exceed limits ---
        if [[ -z "$reject_reason" && -n "$target_file" ]]; then
            local full_path="${WORKSPACE_HUB}/.claude/${target_file}"
            if [[ -f "$full_path" ]]; then
                local current_lines
                current_lines=$(wc -l < "$full_path" | tr -d ' ')

                # CLAUDE.md: 4KB budget (~100 lines)
                if [[ "$target_file" == *"CLAUDE.md"* && "$current_lines" -ge 100 ]]; then
                    reject_reason="claude_md_size_limit"
                fi
                # Memory/Knowledge: 200-line limit
                if [[ "$target_file" == memory/* && "$current_lines" -ge 200 ]]; then
                    reject_reason="memory_line_limit"
                fi
                # Rules/Skills: 400-line limit
                if [[ "$target_file" == rules/* && "$current_lines" -ge 400 ]]; then
                    reject_reason="rules_line_limit"
                fi
            fi
        fi

        # --- No-clobber: skip files with uncommitted changes ---
        if [[ -z "$reject_reason" && -n "$target_file" ]]; then
            local full_path="${WORKSPACE_HUB}/.claude/${target_file}"
            if [[ -f "$full_path" ]]; then
                if git -C "$WORKSPACE_HUB" diff --name-only 2>/dev/null | grep -q "${target_file}"; then
                    reject_reason="uncommitted_changes"
                fi
            fi
        fi

        # --- Dedup check ---
        if [[ -z "$reject_reason" && -n "$target_file" ]]; then
            local content
            content=$(echo "$item" | jq -r '.content // ""')
            local full_path="${WORKSPACE_HUB}/.claude/${target_file}"
            if [[ -f "$full_path" && -n "$content" ]]; then
                # Check if first 40 chars of content already exist in file
                local snippet="${content:0:40}"
                if grep -qF "$snippet" "$full_path" 2>/dev/null; then
                    reject_reason="duplicate_content"
                fi
            fi
        fi

        if [[ -n "$reject_reason" ]]; then
            echo "$item" | jq -c --arg reason "$reject_reason" '. + {rejected: true, reject_reason: $reason}'
        else
            echo "$item" | jq -c '. + {rejected: false}'
        fi
    done > "${guarded}.tmp"

    # Split accepted and rejected
    jq -sc '[.[] | select(.rejected == false)]' "${guarded}.tmp" > "$guarded" 2>/dev/null
    accepted=$(jq 'length' "$guarded" 2>/dev/null || echo "0")
    rejected=$(jq -sc '[.[] | select(.rejected == true)] | length' "${guarded}.tmp" 2>/dev/null || echo "0")

    echo "$accepted" > "${IMPROVE_WORKDIR}/changes_count"
    rm -f "${guarded}.tmp"

    echo "improve/guard: ${accepted} accepted, ${rejected} rejected"

    # Return failure only if ALL were rejected AND no ecosystem data
    [[ "$accepted" -eq 0 ]] && return 1
    return 0
}
