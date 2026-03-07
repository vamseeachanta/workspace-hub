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

log_gate_event_if_available "$wrk_id" "plan" "plan_wrapper_start" "$provider" "plan gate entered"

file="$(resolve_wrk_file "$wrk_id")" || { echo "ERROR: work item not found: $wrk_id" >&2; exit 2; }

# --- Stage 5 evidence gate (canonical checker — Phase 1A guard) ---------------
# plan.sh is an official Stage 6 entrypoint. Both exit 1 (predicate failure) and
# exit 2 (infrastructure failure) are fail-closed blocking outcomes.
STAGE5_CHECKER="${WS_HUB}/scripts/work-queue/verify-gate-evidence.py"
if [[ -f "$STAGE5_CHECKER" ]]; then
    stage5_exit=0
    stage5_output="$(uv run --no-project python "$STAGE5_CHECKER" \
        --stage5-check "$wrk_id" 2>&1)" || stage5_exit=$?
    if [[ "$stage5_exit" -eq 1 ]]; then
        echo "✖ Stage 5 evidence gate FAILED (predicate failure) for ${wrk_id}:" >&2
        echo "$stage5_output" >&2
        echo "Complete Stage 5 interactive review and evidence before entering Stage 6." >&2
        log_gate_event_if_available "$wrk_id" "plan" "stage5_gate_fail" "$provider" "predicate failure"
        exit 1
    elif [[ "$stage5_exit" -eq 2 ]]; then
        echo "✖ Stage 5 evidence gate FAILED (infrastructure failure) for ${wrk_id}:" >&2
        echo "$stage5_output" >&2
        echo "Repair the Stage 5 gate infrastructure before proceeding." >&2
        log_gate_event_if_available "$wrk_id" "plan" "stage5_gate_infra_fail" "$provider" "infrastructure failure"
        exit 2
    fi
    # exit 0 = gate passes or disabled; continue
fi

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
            log_gate_event_if_available "$wrk_id" "plan" "plan_wrapper_blocked" "$provider" "ensemble complete; write plan and re-run"
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
    log_gate_event_if_available "$wrk_id" "plan" "plan_wrapper_blocked" "$provider" "missing ## Plan section"
    exit 3
fi

# --- Model resolution --------------------------------------------------------
if [[ "$provider" == "claude" ]]; then
    plan_model="$(wrk_resolve_model_for_phase "$file" "plan" "$model_override")"
    plan_model_id="$(wrk_get_claude_model_id "$plan_model")"
    echo "Claude model for plan phase: $plan_model (${plan_model_id})"
fi

session_record_stage "$wrk_id" "plan_approval_gate"
gate_logger="${WS_HUB}/scripts/work-queue/log-gate-event.sh"
if [[ -x "$gate_logger" ]]; then
    bash "$gate_logger" "$wrk_id" "plan" "plan_draft_complete" "$provider" "plan gate passed"
fi
log_gate_event_if_available "$wrk_id" "plan" "plan_wrapper_complete" "$provider" "plan gate passed"
echo "Plan gate passed for ${wrk_id} under orchestrator '${provider}'."
