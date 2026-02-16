#!/usr/bin/env bash
set -euo pipefail

AGENTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$AGENTS_DIR/lib/workflow-guards.sh"

provider=""
wrk_id=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        --provider) provider="$2"; shift 2 ;;
        WRK-*) wrk_id="$1"; shift ;;
        *) echo "Unknown arg: $1" >&2; exit 2 ;;
    esac
done

[[ -z "$provider" || -z "$wrk_id" ]] && { echo "Usage: execute.sh --provider <p> WRK-###" >&2; exit 2; }
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

# ── Provider dispatch ─────────────────────────────────────────────────
# Read provider from WRK frontmatter; fall back to --provider flag
wrk_file="$(resolve_wrk_file "$wrk_id")"
assigned=$(wrk_get_frontmatter_value "$wrk_file" "provider")
[[ -z "$assigned" ]] && assigned="$provider"

echo "Dispatching $wrk_id to provider: $assigned"
"$AGENTS_DIR/providers/${assigned}.sh" execute "$wrk_file"

# If dual-agent mode, also dispatch alt provider
alt=$(wrk_get_frontmatter_value "$wrk_file" "provider_alt")
if [[ -n "$alt" ]]; then
    echo "Dual-agent: also dispatching to alt provider: $alt"
    "$AGENTS_DIR/providers/${alt}.sh" execute "$wrk_file"
    echo "Dual-agent: compare outputs from $assigned and $alt"
fi
