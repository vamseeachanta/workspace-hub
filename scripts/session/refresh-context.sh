#!/usr/bin/env bash
# refresh-context.sh — Serialize session state to WRK items and optionally relaunch
#
# Usage:
#   scripts/session/refresh-context.sh [--wrk WRK-NNN] [--auto] [--idle-timeout SECS]
#
# Options:
#   --wrk WRK-NNN        Target a specific WRK item (default: all with computer=ace-linux-1)
#   --auto               Relaunch Claude Code after writing state
#   --idle-timeout SECS  Trigger only if no git activity for N seconds (0 = always run)
#   --turns N            Simulate N turns elapsed for testing (overrides detection)
#
# Exit codes:
#   0  State written (and optionally relaunched)
#   1  Error
#   2  Idle threshold not met (skipped cleanly)

set -euo pipefail

# ─── Paths ────────────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_HUB="${WORKSPACE_HUB:-$(cd "${SCRIPT_DIR}/../.." && pwd)}"
QUEUE_DIR="${WORKSPACE_HUB}/.claude/work-queue"
STATE_DIR="${WORKSPACE_HUB}/.claude/state"
MEMORY_FILE="${WORKSPACE_HUB}/MEMORY.md"
PYTHON_HELPER="${SCRIPT_DIR}/write-wrk-state.py"
CHECKPOINT_HELPER="${SCRIPT_DIR}/subagent-checkpoint.py"
HARNESS_CAPTURE="${SCRIPT_DIR}/capture-harness-version.sh"
LOG_FILE="${STATE_DIR}/refresh-context.log"
ACTIVE_AGENTS_FILE="${STATE_DIR}/active-agents"

# ─── Defaults ─────────────────────────────────────────────────────────────────
TARGET_WRK=""
AUTO_RELAUNCH=false
IDLE_TIMEOUT=0
TURN_COUNT_OVERRIDE=""
AGENT_ID=""

# ─── Parse args ───────────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
    case "$1" in
        --wrk)
            TARGET_WRK="$2"
            shift 2
            ;;
        --auto)
            AUTO_RELAUNCH=true
            shift
            ;;
        --idle-timeout)
            IDLE_TIMEOUT="$2"
            shift 2
            ;;
        --turns)
            TURN_COUNT_OVERRIDE="$2"
            shift 2
            ;;
        --agent-id)
            # Task tool subagent ID — written to active-agents for resume capability
            AGENT_ID="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
    esac
done

# ─── Setup ────────────────────────────────────────────────────────────────────
mkdir -p "$STATE_DIR"

log() {
    local ts
    ts="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    echo "[${ts}] $*" | tee -a "$LOG_FILE"
}

# ─── Idle-timeout check ───────────────────────────────────────────────────────
check_idle_threshold() {
    [[ "$IDLE_TIMEOUT" -eq 0 ]] && return 0

    local last_activity
    last_activity="$(git -C "$WORKSPACE_HUB" log -1 --format="%ct" 2>/dev/null || echo 0)"
    local now
    now="$(date +%s)"
    local elapsed=$(( now - last_activity ))

    if [[ "$elapsed" -lt "$IDLE_TIMEOUT" ]]; then
        log "Idle threshold not met (${elapsed}s < ${IDLE_TIMEOUT}s). Skipping."
        exit 2
    fi
    log "Idle threshold met (${elapsed}s >= ${IDLE_TIMEOUT}s). Proceeding."
}

# ─── Turn-count heuristic ─────────────────────────────────────────────────────
# Returns 0 (proceed) if turns >= threshold or override set
check_turn_heuristic() {
    local threshold=40
    local turn_file="${STATE_DIR}/session-turn-count.txt"

    if [[ -n "$TURN_COUNT_OVERRIDE" ]]; then
        log "Turn count override: ${TURN_COUNT_OVERRIDE}"
        [[ "$TURN_COUNT_OVERRIDE" -ge "$threshold" ]] && return 0
        log "Turn count ${TURN_COUNT_OVERRIDE} < threshold ${threshold}; not context-limited."
        return 1
    fi

    # Read persisted turn count written by session-logger hook
    if [[ -f "$turn_file" ]]; then
        local turns
        turns="$(cat "$turn_file" | tr -d '[:space:]')"
        if [[ "$turns" =~ ^[0-9]+$ ]] && [[ "$turns" -ge "$threshold" ]]; then
            log "Turn count ${turns} >= threshold ${threshold}. Session approaching limits."
            return 0
        fi
    fi

    log "Turn count below threshold or unknown. Running state save regardless."
    return 0
}

# ─── Collect git state ────────────────────────────────────────────────────────
collect_modified_files() {
    git -C "$WORKSPACE_HUB" status --short 2>/dev/null \
        | awk '{print $NF}' \
        | sort -u
}

collect_recent_commits() {
    git -C "$WORKSPACE_HUB" log --oneline -5 2>/dev/null || echo "(no commits)"
}

# ─── Discover active WRK items ────────────────────────────────────────────────
find_active_wrk_items() {
    local pending_dir="${QUEUE_DIR}/pending"
    local working_dir="${QUEUE_DIR}/working"

    local results=()

    for dir in "$pending_dir" "$working_dir"; do
        [[ -d "$dir" ]] || continue
        while IFS= read -r f; do
            [[ -f "$f" ]] || continue
            # Filter by computer assignment
            if grep -qE "^computer:[[:space:]]*ace-linux-1" "$f" 2>/dev/null; then
                results+=("$f")
            fi
        done < <(find "$dir" -name "WRK-*.md" | sort)
    done

    printf '%s\n' "${results[@]:-}"
}

# ─── Build progress notes from WRK file ──────────────────────────────────────
extract_progress_notes() {
    local wrk_file="$1"
    local done_steps
    done_steps="$(grep -E '^\s*-\s*\[x\]' "$wrk_file" 2>/dev/null | sed 's/^\s*- \[x\] //' | head -5 || true)"
    if [[ -n "$done_steps" ]]; then
        echo "Completed steps: ${done_steps}"
    else
        echo "No completed steps detected."
    fi
}

extract_next_steps() {
    local wrk_file="$1"
    grep -E '^\s*-\s*\[\s\]' "$wrk_file" 2>/dev/null \
        | sed 's/^\s*- \[ \] //' \
        | head -5 \
        || true
}

# ─── Write state to a single WRK item ────────────────────────────────────────
write_state_to_wrk() {
    local wrk_file="$1"
    local modified_files="$2"
    local recent_commits="$3"

    local wrk_id
    wrk_id="$(basename "$wrk_file" .md)"

    local progress_notes
    progress_notes="$(extract_progress_notes "$wrk_file")"

    local next_steps_raw
    next_steps_raw="$(extract_next_steps "$wrk_file")"

    local ts
    ts="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

    # Delegate YAML frontmatter update to Python helper
    python3 "$PYTHON_HELPER" \
        --wrk-path "$wrk_file" \
        --last-updated "$ts" \
        --progress-notes "$progress_notes" \
        --modified-files "$modified_files" \
        --next-steps "$next_steps_raw" \
        --recent-commits "$recent_commits"

    log "State written to ${wrk_id} (${wrk_file})"
}

# ─── Update MEMORY.md with session findings ───────────────────────────────────
update_memory_md() {
    local ts
    ts="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

    if [[ ! -f "$MEMORY_FILE" ]]; then
        log "MEMORY.md not found at ${MEMORY_FILE}; skipping."
        return 0
    fi

    local entry="<!-- session-refresh: ${ts} -->"

    # Append only if no entry for this timestamp already present
    if ! grep -qF "$ts" "$MEMORY_FILE" 2>/dev/null; then
        printf '\n%s\n' "$entry" >> "$MEMORY_FILE"
        log "MEMORY.md updated with refresh timestamp."
    fi
}

# ─── Write subagent checkpoint ────────────────────────────────────────────────
write_subagent_checkpoint() {
    local active_wrk_ids="$1"
    local modified_files="$2"

    python3 "$CHECKPOINT_HELPER" \
        --workspace "$WORKSPACE_HUB" \
        --active-wrk "$active_wrk_ids" \
        --modified-files "$modified_files" \
        --output "${STATE_DIR}/subagent-checkpoint.json"

    log "Subagent checkpoint written to ${STATE_DIR}/subagent-checkpoint.json"
}

# ─── Relaunch Claude Code ─────────────────────────────────────────────────────
relaunch_claude() {
    local prompt_file="${STATE_DIR}/refresh-prompt.md"
    local active_wrk_ids="$1"

    # Read harness metadata for the prompt (best-effort)
    local harness_version model_name
    harness_version="$(cat "${STATE_DIR}/harness-version.txt" 2>/dev/null || echo "unknown")"
    model_name="$(cat "${STATE_DIR}/default-model.txt" 2>/dev/null || echo "unknown")"

    # Read active agent IDs for Task tool resume guidance (last 5 entries)
    local agent_ids_section=""
    if [[ -f "$ACTIVE_AGENTS_FILE" ]]; then
        local agent_ids
        agent_ids="$(tail -5 "$ACTIVE_AGENTS_FILE" 2>/dev/null || true)"
        if [[ -n "$agent_ids" ]]; then
            agent_ids_section="## Active Agent IDs (Task tool resume)
${agent_ids}
Pass the relevant ID as the \`resume\` parameter when re-spawning a subagent
via the Task tool to re-attach to an in-flight subagent context.

"
        fi
    fi

    # Build a handoff prompt pointing to the WRK items
    cat > "$prompt_file" <<PROMPT
# Session Refresh — Context Handoff

A previous Claude Code session serialized its working state to avoid context
degradation. Resume from the WRK items listed below. Run /session-start first.

## Harness Info
- Claude Code version: ${harness_version}
- Default model: ${model_name}

## Active WRK Items
${active_wrk_ids}

${agent_ids_section}## Instructions
1. Read each WRK item file listed above — focus on the \`session_state\` block
   in the YAML frontmatter.
2. Review \`${STATE_DIR}/subagent-checkpoint.json\` for fine-grained state.
3. Continue work from the \`next_steps\` listed in each item.
4. Do NOT re-do steps already marked [x].
5. If resuming a Task tool subagent, pass its agent ID as the \`resume\`
   parameter in the Task tool call.

PROMPT

    log "Refresh prompt written to ${prompt_file}"

    if command -v claude &>/dev/null; then
        log "Relaunching Claude Code..."
        # Use --resume if available (Claude Code >= 1.x); fall back to piping prompt
        if claude --help 2>&1 | grep -q -- "--resume"; then
            exec claude --resume --print "$(cat "$prompt_file")"
        else
            exec claude --print "$(cat "$prompt_file")"
        fi
    else
        log "WARNING: 'claude' binary not found. Manual relaunch needed."
        log "Prompt saved to: ${prompt_file}"
    fi
}

# ─── Task tool resume: register agent ID ──────────────────────────────────────
# When a subagent is spawned via the Task tool, the caller can pass --agent-id
# to record its ID in .claude/state/active-agents.  A parent session (or the
# next refresh cycle) can read this file and, where the Task tool supports a
# `resume` parameter, pass the stored ID to re-attach to an in-flight agent.
register_agent_id() {
    [[ -z "$AGENT_ID" ]] && return 0

    local ts
    ts="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    # Format: <timestamp> <agent-id>
    echo "${ts} ${AGENT_ID}" >> "$ACTIVE_AGENTS_FILE"
    log "Agent ID '${AGENT_ID}' registered in ${ACTIVE_AGENTS_FILE}"
}

# ─── Harness version capture ──────────────────────────────────────────────────
capture_harness_version() {
    if [[ -x "$HARNESS_CAPTURE" ]]; then
        log "Capturing Claude Code harness version..."
        if "$HARNESS_CAPTURE" --state-dir "$STATE_DIR" >> "$LOG_FILE" 2>&1; then
            local version model
            version="$(cat "${STATE_DIR}/harness-version.txt" 2>/dev/null || echo "unknown")"
            model="$(cat "${STATE_DIR}/default-model.txt" 2>/dev/null || echo "unknown")"
            log "Harness version: ${version} | Default model: ${model}"
        else
            log "WARNING: capture-harness-version.sh failed (non-fatal)."
        fi
    else
        log "WARNING: ${HARNESS_CAPTURE} not found or not executable; skipping harness capture."
    fi
}

# ─── Main ─────────────────────────────────────────────────────────────────────
main() {
    log "=== refresh-context.sh START ==="

    # AC: Task tool resume — register this agent's ID before any state work
    register_agent_id

    # AC: Harness refresh — capture current Claude Code version + default model
    capture_harness_version

    check_idle_threshold
    check_turn_heuristic

    # Collect global state
    local modified_files
    modified_files="$(collect_modified_files | tr '\n' ',' | sed 's/,$//')"
    local recent_commits
    recent_commits="$(collect_recent_commits)"

    log "Modified files: ${modified_files:-none}"

    # Resolve target WRK items
    local wrk_files=()
    if [[ -n "$TARGET_WRK" ]]; then
        # User specified a single WRK item; search pending/ and working/
        local found
        found="$(find "${QUEUE_DIR}" -name "${TARGET_WRK}.md" 2>/dev/null | head -1 || true)"
        if [[ -z "$found" ]]; then
            log "ERROR: ${TARGET_WRK}.md not found in work queue." >&2
            exit 1
        fi
        wrk_files=("$found")
    else
        while IFS= read -r f; do
            [[ -n "$f" ]] && wrk_files+=("$f")
        done < <(find_active_wrk_items)
    fi

    if [[ "${#wrk_files[@]}" -eq 0 ]]; then
        log "No active WRK items found assigned to ace-linux-1. Nothing to persist."
        exit 0
    fi

    local active_ids=""
    for wrk_file in "${wrk_files[@]}"; do
        write_state_to_wrk "$wrk_file" "$modified_files" "$recent_commits"
        local wrk_id
        wrk_id="$(basename "$wrk_file" .md)"
        active_ids="${active_ids}${wrk_id} (${wrk_file})\n"
    done

    update_memory_md

    write_subagent_checkpoint "$active_ids" "$modified_files"

    log "=== refresh-context.sh DONE ==="

    if [[ "$AUTO_RELAUNCH" == "true" ]]; then
        relaunch_claude "$active_ids"
    fi
}

main "$@"
