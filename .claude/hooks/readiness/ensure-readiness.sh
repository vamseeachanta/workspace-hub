#!/usr/bin/env bash
# ensure-readiness.sh — Stop hook: ensure next session starts clean
# Runs at session exit BEFORE improve.sh
# Covers R1 (memory curation), R5 (context budget), R6 (submodule sync)
# Outputs warnings + writes readiness report for next session

# Drain stdin (stop hook pipes session data)
if [[ ! -t 0 ]]; then
    cat > /dev/null 2>&1 || true
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_HUB="${WORKSPACE_HUB:-$(cd "${SCRIPT_DIR}/../../.." && pwd)}"
STATE_DIR="${WORKSPACE_HUB}/.claude/state"
REPORT_FILE="${STATE_DIR}/readiness-report.md"

mkdir -p "$STATE_DIR" 2>/dev/null

warnings=()
fixes=()
info=()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# R1: Memory Curation
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
check_memory() {
    # Check repo-level memory
    local memory_dir="${WORKSPACE_HUB}/.claude/memory"
    if [[ -d "$memory_dir" ]]; then
        while IFS= read -r f; do
            [[ ! -f "$f" ]] && continue
            local lines name
            lines=$(wc -l < "$f" | tr -d ' ')
            name=$(basename "$f")
            if [[ "$lines" -gt 200 ]]; then
                warnings+=("R1: ${name} is ${lines} lines (limit: 200) — needs trimming")
                fixes+=("  Action: Split ${name} into topic files or archive stale entries")
            fi
        done < <(find "$memory_dir" -name "*.md" 2>/dev/null)
    fi

    # Check user-level MEMORY.md
    local user_memory
    user_memory=$(find ~/.claude/projects/ -maxdepth 3 -name "MEMORY.md" 2>/dev/null | head -1)
    if [[ -n "$user_memory" && -f "$user_memory" ]]; then
        local lines
        lines=$(wc -l < "$user_memory" | tr -d ' ')
        if [[ "$lines" -gt 200 ]]; then
            warnings+=("R1: User MEMORY.md is ${lines} lines (limit: 200, truncated beyond line 200)")
            fixes+=("  Action: Archive older entries to topic files linked from MEMORY.md")
        elif [[ "$lines" -gt 170 ]]; then
            info+=("R1: User MEMORY.md at ${lines}/200 lines — approaching limit")
        fi
    fi
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# R5: Context Budget Enforcement
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
check_context_budget() {
    local total_bytes=0
    local details=""

    # CLAUDE.md (workspace level — 4KB limit)
    local claude_md="${WORKSPACE_HUB}/CLAUDE.md"
    if [[ -f "$claude_md" ]]; then
        local bytes
        bytes=$(wc -c < "$claude_md" | tr -d ' ')
        total_bytes=$((total_bytes + bytes))
        if [[ "$bytes" -gt 4096 ]]; then
            local pct=$(( bytes * 100 / 4096 ))
            warnings+=("R5: CLAUDE.md is ${bytes} bytes (${pct}% of 4KB limit)")
            fixes+=("  Action: Move verbose docs to .claude/docs/ — CLAUDE.md should be concise index only")
            # Identify largest sections for trimming
            local largest_section
            largest_section=$(awk '/^## /{section=$0; count=0; next} {count++} END{}
                /^## /{if(count>prev_count){prev_count=count; prev_section=section}}
                END{print prev_section " (" prev_count " lines)"}' "$claude_md" 2>/dev/null)
            if [[ -n "$largest_section" ]]; then
                fixes+=("  Hint: Largest section may be a trim candidate")
            fi
        fi
        details="CLAUDE.md=${bytes}b"
    fi

    # Rules files (all loaded)
    local rules_dir="${WORKSPACE_HUB}/.claude/rules"
    if [[ -d "$rules_dir" ]]; then
        local rules_bytes
        rules_bytes=$(find "$rules_dir" -name "*.md" -exec wc -c {} + 2>/dev/null | tail -1 | awk '{print $1}')
        rules_bytes="${rules_bytes:-0}"
        total_bytes=$((total_bytes + rules_bytes))
        details="${details} rules=${rules_bytes}b"

        # Flag individual large rule files
        while IFS= read -r line; do
            local fbytes fname
            fbytes=$(echo "$line" | awk '{print $1}')
            fname=$(echo "$line" | awk '{print $2}')
            if [[ "$fbytes" -gt 3000 ]]; then
                info+=("R5: $(basename "$fname") is ${fbytes} bytes — consider splitting")
            fi
        done < <(find "$rules_dir" -name "*.md" -exec wc -c {} \; 2>/dev/null | sort -rn | head -3)
    fi

    # User memory
    local user_memory
    user_memory=$(find ~/.claude/projects/ -maxdepth 3 -name "MEMORY.md" 2>/dev/null | head -1)
    if [[ -n "$user_memory" && -f "$user_memory" ]]; then
        local mem_bytes
        mem_bytes=$(wc -c < "$user_memory" | tr -d ' ')
        total_bytes=$((total_bytes + mem_bytes))
        details="${details} memory=${mem_bytes}b"
    fi

    # Total check (16KB = 16384)
    if [[ "$total_bytes" -gt 16384 ]]; then
        local pct=$(( total_bytes * 100 / 16384 ))
        warnings+=("R5: Total context ${total_bytes} bytes (${pct}% of 16KB budget) [${details}]")
        fixes+=("  Action: Reduce to <16KB — trim CLAUDE.md first (biggest ROI), then consolidate rules")
    else
        local pct=$(( total_bytes * 100 / 16384 ))
        info+=("R5: Context budget OK — ${total_bytes}/16384 bytes (${pct}%)")
    fi
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# R6: Submodule Sync Check
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
check_submodule_sync() {
    [[ ! -f "${WORKSPACE_HUB}/.gitmodules" ]] && return

    local drift_count=0
    local drift_list=""

    # Check each submodule
    while IFS= read -r sub_path; do
        [[ -z "$sub_path" ]] && continue
        local full_path="${WORKSPACE_HUB}/${sub_path}"
        [[ ! -d "$full_path/.git" && ! -f "$full_path/.git" ]] && continue

        # Check if on detached HEAD
        local branch
        branch=$(git -C "$full_path" symbolic-ref --short HEAD 2>/dev/null)
        if [[ -z "$branch" ]]; then
            drift_count=$((drift_count + 1))
            drift_list="${drift_list}\n    ${sub_path}: detached HEAD"
            continue
        fi

        # Check if behind remote (only if remote exists)
        local behind
        behind=$(git -C "$full_path" rev-list --count HEAD..origin/"$branch" 2>/dev/null || echo "0")
        if [[ "$behind" -gt 5 ]]; then
            drift_count=$((drift_count + 1))
            drift_list="${drift_list}\n    ${sub_path}: ${behind} commits behind origin/${branch}"
        fi
    done < <(git -C "$WORKSPACE_HUB" config --file .gitmodules --get-regexp 'submodule\..*\.path' 2>/dev/null | awk '{print $2}')

    if [[ "$drift_count" -gt 0 ]]; then
        warnings+=("R6: ${drift_count} submodule(s) need attention")
        fixes+=("  Drift detected:$(echo -e "$drift_list")")
        fixes+=("  Action: Run 'git submodule update --remote' or ./scripts/repository_sync")
    else
        info+=("R6: All submodules in sync")
    fi
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# R9: Session Snapshot Surfacing
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
check_session_snapshot() {
    local snapshot="${STATE_DIR}/session-snapshot.md"
    [[ ! -f "$snapshot" ]] && return

    # Check if <48h old (48*3600 = 172800 seconds)
    local now mod_time age
    now=$(date +%s)
    mod_time=$(stat -c %Y "$snapshot" 2>/dev/null || stat -f %m "$snapshot" 2>/dev/null || echo 0)
    age=$(( now - mod_time ))

    if [[ "$age" -lt 172800 ]]; then
        local age_h=$(( age / 3600 ))
        info+=("R9: Session snapshot found (${age_h}h old) — read .claude/state/session-snapshot.md to resume last session context")
    fi
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Run all checks
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
check_memory
check_context_budget
check_submodule_sync
check_session_snapshot

# --- Terminal output ---
if [[ ${#warnings[@]} -gt 0 ]]; then
    echo "Next-Session Readiness (${#warnings[@]} issues):"
    for w in "${warnings[@]}"; do
        echo "  ! ${w}"
    done
    for f in "${fixes[@]}"; do
        echo "${f}"
    done
fi

# --- Write readiness report for next session ---
{
    echo "# Readiness Report"
    echo "Generated: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    echo ""
    if [[ ${#warnings[@]} -gt 0 ]]; then
        echo "## Warnings (${#warnings[@]})"
        for w in "${warnings[@]}"; do
            echo "- ${w}"
        done
        echo ""
        echo "## Suggested Fixes"
        for f in "${fixes[@]}"; do
            echo "${f}"
        done
    else
        echo "## Status: All Clear"
        echo "No readiness issues detected."
    fi
    echo ""
    if [[ ${#info[@]} -gt 0 ]]; then
        echo "## Info"
        for i in "${info[@]}"; do
            echo "- ${i}"
        done
    fi
} > "$REPORT_FILE" 2>/dev/null

# Clear the startup readiness lock so next session re-verifies
rm -f "${STATE_DIR}/.readiness-checked" 2>/dev/null

exit 0
