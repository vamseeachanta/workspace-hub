#!/usr/bin/env bash
set -euo pipefail

AGENTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$AGENTS_DIR/lib/workflow-guards.sh"

provider=""
wrk_id=""
phase=""
model_override=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        --provider)       provider="$2";       shift 2 ;;
        --phase)          phase="$2";          shift 2 ;;
        --model-override) model_override="$2"; shift 2 ;;
        WRK-*)            wrk_id="$1";          shift   ;;
        *) echo "Unknown arg: $1" >&2; exit 2 ;;
    esac
done

[[ -z "$provider" || -z "$wrk_id" ]] && {
    echo "Usage: execute.sh --provider <p> [--phase <phase_N>] [--model-override <model>] WRK-###" >&2
    exit 2
}
assert_provider "$provider"
assert_plan_approved_or_fail "$wrk_id"
wrk_claim "$wrk_id" || exit $?

ensure_session_store
orchestrator="$(session_get orchestrator_agent)"
if [[ -z "$orchestrator" ]]; then
    echo "ERROR: session not initialized" >&2
    exit 2
fi

if [[ "$provider" != "$orchestrator" ]]; then
    session_add_subagent "$provider"
    mode="subagent"
else
    mode="orchestrator"
fi

session_record_stage "$wrk_id" "implement_tdd"
echo "Execution contract accepted for $wrk_id as $mode ('$provider')."

# ── Provider dispatch (WRK-198: per-phase task_agents routing) ───────
# Priority: task_agents:<phase> > provider: field > --provider flag
wrk_file="$(resolve_wrk_file "$wrk_id")"
assigned="$(wrk_resolve_phase_provider "$wrk_file" "$phase" "$provider")"

# Validate the resolved provider name
assert_provider "$assigned"

# Health check: verify CLI is available; fall back through preference order
_provider_available() {
    local p="$1"
    local result
    result="$("$AGENTS_DIR/providers/${p}.sh" check 2>/dev/null)"
    [[ "$result" == "OK" ]]
}

if ! _provider_available "$assigned"; then
    echo "WARN: provider '$assigned' CLI not available — trying fallback" >&2
    fallback_found=false
    for candidate in claude codex gemini; do
        [[ "$candidate" == "$assigned" ]] && continue
        if _provider_available "$candidate"; then
            echo "WARN: falling back to '$candidate'" >&2
            assigned="$candidate"
            fallback_found=true
            break
        fi
    done
    if [[ "$fallback_found" == "false" ]]; then
        echo "ERROR: no available provider CLI found (tried claude, codex, gemini)" >&2
        exit 1
    fi
fi

# ── Model resolution for Claude (WRK-207) ───────────────────────────
# Resolve model and pass --model flag when dispatching to claude.sh.
claude_model_args=()
if [[ "$assigned" == "claude" ]]; then
    model_key="$(wrk_resolve_model_for_phase "$wrk_file" "execute" "$model_override")"
    model_id="$(wrk_get_claude_model_id "$model_key")"
    claude_model_args=(--model "$model_id")
    echo "Claude model for execute phase: $model_key ($model_id)"
fi

if [[ -n "$phase" ]]; then
    echo "Dispatching $wrk_id ($phase) to provider: $assigned"
else
    echo "Dispatching $wrk_id to provider: $assigned"
fi
"$AGENTS_DIR/providers/${assigned}.sh" execute "$wrk_file" "${claude_model_args[@]}"

# If dual-agent mode, also dispatch alt provider
alt=$(wrk_get_frontmatter_value "$wrk_file" "provider_alt")
if [[ -n "$alt" ]]; then
    echo "Dual-agent: also dispatching to alt provider: $alt"
    "$AGENTS_DIR/providers/${alt}.sh" execute "$wrk_file"
    echo "Dual-agent: compare outputs from $assigned and $alt"
fi
