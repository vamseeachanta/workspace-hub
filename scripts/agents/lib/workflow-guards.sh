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
}

session_record_stage() {
    local wrk_id="$1"
    local stage="$2"
    session_set_scalar "active_wrk" "$wrk_id"
    session_set_scalar "last_stage" "$stage"
    session_update_timestamp
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
