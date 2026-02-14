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

[[ -z "$provider" || -z "$wrk_id" ]] && { echo "Usage: plan.sh --provider <p> WRK-###" >&2; exit 2; }
assert_provider "$provider"
assert_orchestrator_or_fail "$provider"

file="$(resolve_wrk_file "$wrk_id")" || { echo "ERROR: work item not found: $wrk_id" >&2; exit 2; }
if ! grep -q "## Plan" "$file"; then
    echo "ERROR: $wrk_id has no ## Plan section" >&2
    exit 3
fi

session_record_stage "$wrk_id" "plan_approval_gate"
echo "Plan gate ready for $wrk_id under orchestrator '$provider'."
