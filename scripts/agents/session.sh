#!/usr/bin/env bash
set -euo pipefail

AGENTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$AGENTS_DIR/lib/session-store.sh"
source "$AGENTS_DIR/lib/workflow-guards.sh"

usage() {
    cat <<'USAGE'
Usage:
  scripts/agents/session.sh init --provider <claude|codex|gemini> [--session-id <id>]
  scripts/agents/session.sh show
USAGE
}

cmd="${1:-show}"
shift || true

case "$cmd" in
    init)
        provider=""
        sid="session-$(date +%Y%m%d%H%M%S)"
        while [[ $# -gt 0 ]]; do
            case "$1" in
                --provider) provider="$2"; shift 2 ;;
                --session-id) sid="$2"; shift 2 ;;
                *) echo "Unknown arg: $1" >&2; usage; exit 2 ;;
            esac
        done
        [[ -z "$provider" ]] && { echo "ERROR: --provider is required" >&2; exit 2; }
        assert_provider "$provider"

        ensure_session_store
        local_orchestrator="$(session_get orchestrator_agent)"
        if [[ -n "$local_orchestrator" && "$local_orchestrator" != "$provider" ]]; then
            echo "ERROR: Session already initialized with orchestrator '$local_orchestrator'." >&2
            exit 2
        fi

        session_set_scalar "session_id" "$sid"
        session_set_scalar "orchestrator_agent" "$provider"
        session_set_list "subagents_used"
        session_set_scalar "active_wrk" ""
        session_set_scalar "last_stage" ""
        session_set_bool "handoff_allowed" "false"
        session_update_timestamp

        echo "Initialized session '$sid' with orchestrator '$provider'."

        # Check for stale working items on session startup
        check_stale_items || true

        # Display agent credits and log usage snapshot
        quota_script="$AGENTS_DIR/../ai/assessment/query-quota.sh"
        if [[ -x "$quota_script" ]]; then
            "$quota_script" --refresh 2>/dev/null || true
            "$quota_script" --log 2>/dev/null || true
        fi
        ;;
    show)
        ensure_session_store
        cat "$SESSION_STATE_FILE"
        ;;
    *)
        usage
        exit 2
        ;;
esac
