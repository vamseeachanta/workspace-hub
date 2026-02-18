#!/usr/bin/env bash
set -euo pipefail

AGENTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$AGENTS_DIR/lib/workflow-guards.sh"

provider=""
wrk_id=""
phase=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        --provider) provider="$2"; shift 2 ;;
        --phase) phase="$2"; shift 2 ;;
        WRK-*) wrk_id="$1"; shift ;;
        *) echo "Unknown arg: $1" >&2; exit 2 ;;
    esac
done

[[ -z "$provider" || -z "$wrk_id" ]] && { echo "Usage: execute.sh --provider <p> [--phase <phase_N>] WRK-###" >&2; exit 2; }
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

# Validate the resolved provider
assert_provider "$assigned"

if [[ -n "$phase" ]]; then
    echo "Dispatching $wrk_id ($phase) to provider: $assigned"
else
    echo "Dispatching $wrk_id to provider: $assigned"
fi
"$AGENTS_DIR/providers/${assigned}.sh" execute "$wrk_file"

# If dual-agent mode, also dispatch alt provider
alt=$(wrk_get_frontmatter_value "$wrk_file" "provider_alt")
if [[ -n "$alt" ]]; then
    echo "Dual-agent: also dispatching to alt provider: $alt"
    "$AGENTS_DIR/providers/${alt}.sh" execute "$wrk_file"
    echo "Dual-agent: compare outputs from $assigned and $alt"
fi
