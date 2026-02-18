#!/usr/bin/env bash
set -euo pipefail

AGENTS_LIB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WS_HUB="$(cd "$AGENTS_LIB_DIR/../../.." && pwd)"

source "$AGENTS_LIB_DIR/session-store.sh"

WORK_ITEM_ROOT="${WORK_ITEM_ROOT:-$WS_HUB/.claude/work-queue}"

resolve_wrk_file() {
    local wrk_id="$1"
    for d in working pending blocked archive; do
        local candidate="$WORK_ITEM_ROOT/$d/${wrk_id}.md"
        [[ -f "$candidate" ]] && { echo "$candidate"; return 0; }
    done
    return 1
}

wrk_get_frontmatter_value() {
    local file="$1"
    local key="$2"
    awk -v key="$key" '
        BEGIN { in_fm=0 }
        /^---$/ { in_fm=!in_fm; next }
        in_fm && $1==key":" {
            val=$0
            sub("^[^:]+:[[:space:]]*", "", val)
            gsub(/^"|"$/, "", val)
            print val
            exit
        }
    ' "$file"
}

# ── Per-Phase Provider Routing (WRK-198) ──────────────────────────────
# Extracts the provider assigned to a specific phase from the task_agents:
# block in WRK frontmatter. Returns empty string if not found.
# Usage: wrk_get_task_agent <wrk_file> <phase_key>
#   e.g. wrk_get_task_agent "$file" "phase_2"  → "codex"
wrk_get_task_agent() {
    local file="$1"
    local phase_key="$2"
    awk -v phase="$phase_key" '
        BEGIN { in_fm=0; in_ta=0 }
        /^---$/ { in_fm=!in_fm; next }
        in_fm && /^task_agents:/ { in_ta=1; next }
        in_fm && in_ta && /^[^ ]/ { exit }
        in_fm && in_ta {
            gsub(/^[[:space:]]+/, "")
            key=$0; sub(/:.*/, "", key)
            if (key == phase) {
                val=$0; sub(/^[^:]+:[[:space:]]*/, "", val)
                gsub(/^"|"$/, "", val)
                gsub(/[[:space:]]*#.*$/, "", val)
                print val
                exit
            }
        }
    ' "$file"
}

# Resolves the provider for a WRK execution phase.
# Priority: task_agents:<phase> > provider: field > --provider flag
# Usage: wrk_resolve_phase_provider <wrk_file> <phase_key> <fallback_provider>
wrk_resolve_phase_provider() {
    local file="$1"
    local phase_key="$2"
    local fallback="$3"

    # 1. Try per-phase assignment from task_agents:
    local agent=""
    if [[ -n "$phase_key" ]]; then
        agent="$(wrk_get_task_agent "$file" "$phase_key")"
    fi

    # 2. Fall back to WRK-level provider: field
    if [[ -z "$agent" ]]; then
        agent="$(wrk_get_frontmatter_value "$file" "provider")"
    fi

    # 3. Fall back to CLI --provider flag
    if [[ -z "$agent" ]]; then
        agent="$fallback"
    fi

    echo "$agent"
}

assert_provider() {
    local provider="$1"
    case "$provider" in
        claude|codex|gemini) ;;
        *)
            echo "ERROR: Invalid provider '$provider' (expected claude|codex|gemini)" >&2
            exit 2
            ;;
    esac
}

assert_orchestrator_or_fail() {
    local provider="$1"
    ensure_session_store
    local orchestrator
    orchestrator="$(session_get orchestrator_agent)"
    if [[ -z "$orchestrator" ]]; then
        echo "ERROR: No orchestrator session initialized. Run session init first." >&2
        exit 2
    fi
    if [[ "$provider" != "$orchestrator" ]]; then
        echo "ERROR: Provider '$provider' is subagent. Orchestrator is '$orchestrator'." >&2
        exit 2
    fi
}

assert_plan_approved_or_fail() {
    local wrk_id="$1"
    local file
    file="$(resolve_wrk_file "$wrk_id")" || {
        echo "ERROR: Work item not found: $wrk_id" >&2
        exit 2
    }
    local approved
    approved="$(wrk_get_frontmatter_value "$file" "plan_approved")"
    if [[ "$approved" != "true" ]]; then
        echo "ERROR: Plan gate failed for $wrk_id (plan_approved != true)." >&2
        exit 3
    fi

    local complexity reviewed spec_ref
    complexity="$(wrk_get_frontmatter_value "$file" "complexity")"
    reviewed="$(wrk_get_frontmatter_value "$file" "plan_reviewed")"
    spec_ref="$(wrk_get_frontmatter_value "$file" "spec_ref")"
    case "$complexity" in
        medium|complex|high)
            if [[ "$reviewed" != "true" ]]; then
                echo "ERROR: Plan review gate failed for $wrk_id (complexity=$complexity requires plan_reviewed=true)." >&2
                exit 3
            fi
            ;;
    esac
    case "$complexity" in
        complex|high)
            if [[ -z "$spec_ref" || "$spec_ref" == "null" ]]; then
                echo "ERROR: Spec gate failed for $wrk_id (complexity=$complexity requires spec_ref in specs/wrk/WRK-NNN/)." >&2
                exit 3
            fi
            ;;
    esac
}

session_record_stage() {
    local wrk_id="$1"
    local stage="$2"
    session_set_scalar "active_wrk" "$wrk_id"
    session_set_scalar "last_stage" "$stage"
    session_update_timestamp
    # WRK-161: Update pipeline state if available
    local sid
    sid="$(session_get session_id 2>/dev/null || true)"
    if [[ -n "$sid" ]]; then
        pipeline_update_session "$sid" "$wrk_id" "$stage" 2>/dev/null || true
    fi
}

# ── WRK Item Locking (WRK-157) ──────────────────────────────────────

LOCK_TTL_SECONDS="${LOCK_TTL_SECONDS:-7200}"  # 2 hours default

wrk_set_frontmatter_value() {
    local file="$1"
    local key="$2"
    local value="$3"
    local tmp
    tmp="$(mktemp)"
    awk -v key="$key" -v value="$value" '
        BEGIN { in_fm=0; replaced=0 }
        /^---$/ {
            if (in_fm && !replaced) {
                print key ": \"" value "\""
                replaced=1
            }
            in_fm=!in_fm
            print
            next
        }
        in_fm && $1==key":" {
            print key ": \"" value "\""
            replaced=1
            next
        }
        { print }
    ' "$file" > "$tmp"
    mv "$tmp" "$file"
}

_lock_age_seconds() {
    local locked_at="$1"
    [[ -z "$locked_at" ]] && { echo "999999"; return; }
    local lock_epoch now_epoch
    lock_epoch="$(date -u -d "$locked_at" +%s 2>/dev/null || echo 0)"
    now_epoch="$(date -u +%s)"
    echo $(( now_epoch - lock_epoch ))
}

wrk_claim() {
    local wrk_id="$1"
    local file
    file="$(resolve_wrk_file "$wrk_id")" || {
        echo "ERROR: Work item not found: $wrk_id" >&2
        return 1
    }

    ensure_session_store
    local my_session
    my_session="$(session_get session_id)"
    [[ -z "$my_session" ]] && { echo "ERROR: No session initialized. Run session.sh init first." >&2; return 2; }

    local current_lock
    current_lock="$(wrk_get_frontmatter_value "$file" "locked_by")"

    if [[ -n "$current_lock" && "$current_lock" != "$my_session" ]]; then
        local locked_at
        locked_at="$(wrk_get_frontmatter_value "$file" "locked_at")"
        local age
        age="$(_lock_age_seconds "$locked_at")"

        if [[ "$age" -ge "$LOCK_TTL_SECONDS" ]]; then
            echo "WARN: Stale lock on $wrk_id by '$current_lock' (${age}s old). Reclaiming." >&2
        else
            echo "ERROR: $wrk_id is locked by session '$current_lock' (${age}s ago). Cannot claim." >&2
            return 4
        fi
    fi

    wrk_set_frontmatter_value "$file" "locked_by" "$my_session"
    wrk_set_frontmatter_value "$file" "locked_at" "$(session_now_iso)"
    echo "Claimed $wrk_id for session $my_session"
}

wrk_release() {
    local wrk_id="$1"
    local file
    file="$(resolve_wrk_file "$wrk_id")" || {
        echo "WARN: Work item not found for release: $wrk_id" >&2
        return 0
    }

    wrk_set_frontmatter_value "$file" "locked_by" ""
    wrk_set_frontmatter_value "$file" "locked_at" ""
    echo "Released lock on $wrk_id"
}

# ── Staleness Enforcement (WRK-158) ─────────────────────────────────

STALE_WARN_DAYS="${STALE_WARN_DAYS:-7}"
STALE_CRITICAL_DAYS="${STALE_CRITICAL_DAYS:-14}"

_item_age_days() {
    local file="$1"
    local created_at
    created_at="$(wrk_get_frontmatter_value "$file" "created_at")"
    [[ -z "$created_at" ]] && { echo "0"; return; }
    local created_epoch now_epoch
    created_epoch="$(date -u -d "$created_at" +%s 2>/dev/null || echo 0)"
    now_epoch="$(date -u +%s)"
    echo $(( (now_epoch - created_epoch) / 86400 ))
}

check_stale_items() {
    local working_dir="${WORK_ITEM_ROOT}/working"
    [[ ! -d "$working_dir" ]] && return 0

    local stale_count=0
    for file in "$working_dir"/WRK-*.md; do
        [[ -f "$file" ]] || continue
        local wrk_id
        wrk_id="$(basename "$file" .md)"
        local age_days
        age_days="$(_item_age_days "$file")"
        local current_stale
        current_stale="$(wrk_get_frontmatter_value "$file" "stale")"

        if [[ "$age_days" -ge "$STALE_CRITICAL_DAYS" ]]; then
            if [[ "$current_stale" != "critical" ]]; then
                wrk_set_frontmatter_value "$file" "stale" "critical"
            fi
            # Move back to pending
            wrk_set_frontmatter_value "$file" "status" "pending"
            wrk_set_frontmatter_value "$file" "locked_by" ""
            wrk_set_frontmatter_value "$file" "locked_at" ""
            mv "$file" "${WORK_ITEM_ROOT}/pending/"
            echo "CRITICAL: $wrk_id stale (${age_days}d). Moved to pending." >&2
            stale_count=$((stale_count + 1))
        elif [[ "$age_days" -ge "$STALE_WARN_DAYS" ]]; then
            if [[ "$current_stale" != "warning" && "$current_stale" != "critical" ]]; then
                wrk_set_frontmatter_value "$file" "stale" "warning"
            fi
            echo "WARN: $wrk_id stale (${age_days}d in working)." >&2
            stale_count=$((stale_count + 1))
        fi
    done
    [[ "$stale_count" -gt 0 ]] && echo "Staleness check: $stale_count item(s) flagged." >&2
    return 0
}

# ── Batch Plan Approval (WRK-159) ────────────────────────────────────

_file_has_plan_section() {
    local file="$1"
    grep -q '^## Plan' "$file" 2>/dev/null
}

list_approvable_items() {
    # Returns lines: FILE_PATH|WRK_ID|TITLE|COMPLEXITY|PLAN_FIRST_LINE
    local count=0
    for d in pending working; do
        local dir="${WORK_ITEM_ROOT}/$d"
        [[ -d "$dir" ]] || continue
        for f in "$dir"/WRK-*.md; do
            [[ -f "$f" ]] || continue
            local approved
            approved="$(wrk_get_frontmatter_value "$f" "plan_approved")"
            [[ "$approved" == "true" ]] && continue
            _file_has_plan_section "$f" || continue

            local wrk_id title complexity plan_line
            wrk_id="$(basename "$f" .md)"
            title="$(wrk_get_frontmatter_value "$f" "title")"
            complexity="$(wrk_get_frontmatter_value "$f" "complexity")"
            plan_line="$(awk '/^## Plan/{getline; while(/^[[:space:]]*$/) getline; print; exit}' "$f")"
            [[ ${#plan_line} -gt 80 ]] && plan_line="${plan_line:0:77}..."

            echo "${f}|${wrk_id}|${title}|${complexity}|${plan_line}"
            count=$((count + 1))
        done
    done
    return 0
}

approve_items() {
    # Takes a newline-separated list of FILE_PATH|WRK_ID|... lines to approve
    local items="$1"
    local approved_count=0
    while IFS='|' read -r file wrk_id title complexity plan_line; do
        [[ -z "$file" ]] && continue
        wrk_set_frontmatter_value "$file" "plan_approved" "true"
        echo "  Approved: $wrk_id — $title"
        approved_count=$((approved_count + 1))
    done <<< "$items"
    echo "Approved $approved_count item(s)."
}

reject_items() {
    local items="$1"
    local rejected_count=0
    while IFS='|' read -r file wrk_id title complexity plan_line; do
        [[ -z "$file" ]] && continue
        wrk_set_frontmatter_value "$file" "plan_rejected" "true"
        echo "  Rejected: $wrk_id — $title"
        rejected_count=$((rejected_count + 1))
    done <<< "$items"
    echo "Rejected $rejected_count item(s)."
}

# ── Multi-Session Pipeline (WRK-161) ────────────────────────────────

PIPELINE_STATE_FILE="${PIPELINE_STATE_FILE:-$WORK_ITEM_ROOT/pipeline-state.yaml}"

ensure_pipeline_store() {
    if [[ ! -f "$PIPELINE_STATE_FILE" ]]; then
        cat > "$PIPELINE_STATE_FILE" <<'YAML'
sessions: []
YAML
    fi
}

pipeline_register_session() {
    local sid="$1" provider="$2" wrk_id="${3:-}" stage="${4:-}"
    ensure_pipeline_store
    # Remove existing entry for this session then append
    pipeline_deregister_session "$sid" 2>/dev/null || true
    local now
    now="$(session_now_iso)"
    local tmp
    tmp="$(mktemp)"
    # Replace empty array marker and append entry
    awk '
        /^sessions: \[\]/ { print "sessions:"; next }
        { print }
    ' "$PIPELINE_STATE_FILE" > "$tmp"
    {
        cat "$tmp"
        printf '  - session_id: %s\n' "$sid"
        printf '    provider: %s\n' "$provider"
        printf '    active_wrk: %s\n' "$wrk_id"
        printf '    last_stage: %s\n' "$stage"
        printf '    registered_at: %s\n' "$now"
    } > "${tmp}.2"
    mv "${tmp}.2" "$PIPELINE_STATE_FILE"
    rm -f "$tmp"
}

pipeline_deregister_session() {
    local sid="$1"
    ensure_pipeline_store
    local tmp
    tmp="$(mktemp)"
    awk -v sid="$sid" '
        BEGIN { skip=0 }
        /^  - session_id:/ {
            if (index($0, sid) > 0) { skip=1; next }
            else { skip=0 }
        }
        skip && /^    [a-z]/ { next }
        skip && /^  - / { skip=0 }
        skip && /^[^ ]/ { skip=0 }
        { print }
    ' "$PIPELINE_STATE_FILE" > "$tmp"
    mv "$tmp" "$PIPELINE_STATE_FILE"
}

pipeline_update_session() {
    local sid="$1" wrk_id="$2" stage="$3"
    local provider
    provider="$(session_get orchestrator_agent)"
    pipeline_register_session "$sid" "$provider" "$wrk_id" "$stage"
}

pipeline_list_sessions() {
    ensure_pipeline_store
    awk '
        function strip(s) { sub(/^[[:space:]]*[^:]+:[[:space:]]*/, "", s); gsub(/"/, "", s); return s }
        /session_id:/ { sid=strip($0) }
        /provider:/ { prov=strip($0) }
        /active_wrk:/ { wrk=strip($0) }
        /last_stage:/ { stg=strip($0) }
        /registered_at:/ {
            ts=strip($0)
            printf "%-30s %-8s %-10s %-25s %s\n", sid, prov, wrk, stg, ts
        }
    ' "$PIPELINE_STATE_FILE"
}

pipeline_balance() {
    # Count items per stage from active sessions
    ensure_pipeline_store
    local planning=0 executing=0 reviewing=0 idle=0
    while IFS= read -r line; do
        [[ -z "$line" ]] && continue
        case "$line" in
            *plan_approval_gate*) planning=$((planning + 1)) ;;
            *implement_tdd*) executing=$((executing + 1)) ;;
            *cross_review*) reviewing=$((reviewing + 1)) ;;
            *) idle=$((idle + 1)) ;;
        esac
    done < <(awk '/last_stage:/{sub(/^[[:space:]]*last_stage:[[:space:]]*/, ""); gsub(/"/, ""); print}' "$PIPELINE_STATE_FILE")
    echo "planning=$planning executing=$executing reviewing=$reviewing idle=$idle"
}

pipeline_recommend_stage() {
    # Returns the stage with fewest active sessions (for work selection)
    local balance
    balance="$(pipeline_balance)"
    local planning executing reviewing
    planning="$(echo "$balance" | grep -o 'planning=[0-9]*' | cut -d= -f2)"
    executing="$(echo "$balance" | grep -o 'executing=[0-9]*' | cut -d= -f2)"
    reviewing="$(echo "$balance" | grep -o 'reviewing=[0-9]*' | cut -d= -f2)"

    if [[ "$planning" -le "$executing" && "$planning" -le "$reviewing" ]]; then
        echo "plan_approval_gate"
    elif [[ "$executing" -le "$reviewing" ]]; then
        echo "implement_tdd"
    else
        echo "cross_review"
    fi
}
