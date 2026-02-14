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
