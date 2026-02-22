#!/usr/bin/env bash
# plan.sh --provider <p> [--model-override <model>] [--skip-ensemble] WRK-###
#
# Exit codes:
#   0  plan gate passed (ensemble done + ## Plan section present)
#   2  bad arguments
#   3  ensemble complete but ## Plan section still missing (write the plan)
#   4  ensemble ran now; synthesis ready — read it and write ## Plan, then re-run
#   1  ensemble failed / SPLIT decisions unresolved
set -euo pipefail

AGENTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$AGENTS_DIR/lib/workflow-guards.sh"

provider=""
wrk_id=""
model_override=""
skip_ensemble=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --provider)       provider="$2";        shift 2 ;;
        --model-override) model_override="$2";  shift 2 ;;
        --skip-ensemble)  skip_ensemble=true;   shift   ;;
        WRK-*)            wrk_id="$1";           shift   ;;
        *) echo "Unknown arg: $1" >&2; exit 2 ;;
    esac
done

[[ -z "$provider" || -z "$wrk_id" ]] && {
    echo "Usage: plan.sh --provider <p> [--model-override <model>] [--skip-ensemble] WRK-###" >&2
    exit 2
}
assert_provider "$provider"
assert_orchestrator_or_fail "$provider"

file="$(resolve_wrk_file "$wrk_id")" || { echo "ERROR: work item not found: $wrk_id" >&2; exit 2; }

# --- Ensemble gate (runs BEFORE ## Plan check) -------------------------------
ENSEMBLE_SCRIPT="${AGENTS_DIR}/../planning/ensemble-plan.sh"
plan_ensemble="$(wrk_get_frontmatter_value "$file" "plan_ensemble" 2>/dev/null || echo "")"

if [[ "$skip_ensemble" == "true" ]]; then
    echo "Ensemble gate skipped via --skip-ensemble"
elif [[ "$plan_ensemble" == "true" ]] || [[ "$plan_ensemble" == "skip" ]]; then
    echo "Ensemble already done for ${wrk_id} (plan_ensemble=${plan_ensemble})"
elif [[ ! -f "$ENSEMBLE_SCRIPT" ]]; then
    echo "WARN: ensemble-plan.sh not found at ${ENSEMBLE_SCRIPT} — skipping ensemble gate" >&2
else
    echo "--- Ensemble planning gate: ${wrk_id} ---"
    ensemble_exit=0
    bash "$ENSEMBLE_SCRIPT" "$wrk_id" || ensemble_exit=$?
    case $ensemble_exit in
        0)
            echo "Ensemble complete. Read synthesis, resolve any SPLIT decisions,"
            echo "then write ## Plan in ${file} and re-run plan.sh."
            exit 4
            ;;
        3)
            # Already done or skipped — continue normally
            ;;
        *)
            echo "ERROR: ensemble gate failed (exit ${ensemble_exit})" >&2
            exit 1
            ;;
    esac
fi

# --- Plan section check ------------------------------------------------------
if ! grep -q "## Plan" "$file"; then
    synth_file="${AGENTS_DIR}/../planning/results/${wrk_id}-ensemble/synthesis.md"
    if [[ -f "$synth_file" ]]; then
        echo "Ensemble synthesis is ready. Write the ## Plan section in ${file}"
        echo "using ${synth_file} as input, then re-run plan.sh."
    else
        echo "ERROR: ${wrk_id} has no ## Plan section" >&2
    fi
    exit 3
fi

# --- Model resolution --------------------------------------------------------
if [[ "$provider" == "claude" ]]; then
    plan_model="$(wrk_resolve_model_for_phase "$file" "plan" "$model_override")"
    plan_model_id="$(wrk_get_claude_model_id "$plan_model")"
    echo "Claude model for plan phase: $plan_model (${plan_model_id})"
fi

session_record_stage "$wrk_id" "plan_approval_gate"
echo "Plan gate passed for ${wrk_id} under orchestrator '${provider}'."
