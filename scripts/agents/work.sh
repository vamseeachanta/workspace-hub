#!/usr/bin/env bash
set -euo pipefail

AGENTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$AGENTS_DIR/lib/workflow-guards.sh"
gate_logger="${WS_HUB}/scripts/work-queue/log-gate-event.sh"

provider=""
subcmd=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        --provider) provider="$2"; shift 2 ;;
        *) subcmd="$1"; shift; break ;;
    esac
done

[[ -z "$provider" ]] && { echo "ERROR: --provider required" >&2; exit 2; }
assert_provider "$provider"
assert_orchestrator_or_fail "$provider"

case "$subcmd" in
    run|"" )
        active_wrk="$(session_get active_wrk 2>/dev/null || true)"
        # Fallback: read from state file written by set-active-wrk.sh
        if [[ -z "$active_wrk" ]]; then
            _state_file="${WS_HUB}/.claude/state/active-wrk"
            [[ -f "$_state_file" ]] && active_wrk="$(cat "$_state_file" | tr -d '[:space:]')"
        fi
        log_gate_event_if_available "$active_wrk" "routing" "work_wrapper_start" "$provider" "/work routing invoked"
        log_gate_event_if_available "$active_wrk" "routing" "work_queue_skill" "$provider" "/work routing invoked"
        echo "Workflow orchestrator '$provider' acknowledged /work run contract."
        # Auto-load checkpoint if available for active WRK
        if [[ -n "$active_wrk" ]]; then
            _cp="${WS_HUB}/.claude/work-queue/assets/${active_wrk}/checkpoint.yaml"
            if [[ -f "$_cp" ]]; then
                echo ""
                echo "$(grep -E '^(wrk_id|stage|stage_name|next_action)' "$_cp" | head -4)"
                echo "  → Checkpoint found. context loaded via start_stage.py"
            fi
        fi
        # Task classifier routing recommendation (WRK-118 Phase 3)
        _classifier="${WS_HUB}/scripts/coordination/routing/lib/task_classifier.sh"
        if [[ -n "$active_wrk" && -f "$_classifier" ]] && command -v jq &>/dev/null; then
            _wrk_file="$(find "${WS_HUB}/.claude/work-queue" -maxdepth 2 \
                -name "${active_wrk}.md" 2>/dev/null | head -1)"
            if [[ -n "$_wrk_file" ]]; then
                _title="$(wrk_get_frontmatter_value "$_wrk_file" "title" 2>/dev/null || true)"
                _complexity="$(wrk_get_frontmatter_value "$_wrk_file" "complexity" 2>/dev/null || true)"
                if [[ -n "$_title" ]]; then
                    _classification="$(bash -c "source '$_classifier' && classify_task '$_title'" 2>/dev/null || true)"
                    if [[ -n "$_classification" ]]; then
                        _tier="$(echo "$_classification" | jq -r '.tier' 2>/dev/null || true)"
                        _primary="$(echo "$_classification" | jq -r '.primary_provider' 2>/dev/null || true)"
                        _conf="$(echo "$_classification" | jq -r '.confidence' 2>/dev/null || true)"
                        _scores="$(echo "$_classification" | jq -r \
                            '"claude=\(.all_scores.claude) codex=\(.all_scores.codex) gemini=\(.all_scores.gemini)"' \
                            2>/dev/null || true)"
                        echo ""
                        echo "  ┌─ Routing Recommendation ─────────────────────────────────┐"
                        printf  "  │  WRK: %-52s │\n" "$active_wrk"
                        printf  "  │  Complexity: %-43s │\n" "${_complexity:-unknown}"
                        printf  "  │  Classifier tier: %-36s │\n" "${_tier:-?} (confidence: ${_conf:-?})"
                        printf  "  │  Recommended primary: %-33s │\n" "${_primary:-?}"
                        printf  "  │  Scores: %-46s │\n" "${_scores:-?}"
                        echo    "  └───────────────────────────────────────────────────────────┘"
                        log_gate_event_if_available "$active_wrk" "routing" \
                            "task_classifier" "$provider" \
                            "tier=${_tier} primary=${_primary} confidence=${_conf}"
                    fi
                fi
            fi
        fi
        log_gate_event_if_available "$active_wrk" "routing" "work_wrapper_complete" "$provider" "/work routing acknowledged"
        ;;
    list)
        echo "── pending/ ──"
        for f in "$WORK_ITEM_ROOT/pending"/WRK-*.md; do
            [[ -f "$f" ]] || continue
            local_id="$(basename "$f" .md)"
            local_stale="$(wrk_get_frontmatter_value "$f" "stale")"
            local_lock="$(wrk_get_frontmatter_value "$f" "locked_by")"
            marker=""
            [[ -n "$local_stale" ]] && marker=" [STALE:$local_stale]"
            [[ -n "$local_lock" ]] && marker="$marker [LOCKED:$local_lock]"
            echo "  $local_id$marker"
        done
        echo "── working/ ──"
        for f in "$WORK_ITEM_ROOT/working"/WRK-*.md; do
            [[ -f "$f" ]] || continue
            local_id="$(basename "$f" .md)"
            local_stale="$(wrk_get_frontmatter_value "$f" "stale")"
            local_lock="$(wrk_get_frontmatter_value "$f" "locked_by")"
            marker=""
            [[ -n "$local_stale" ]] && marker=" [STALE:$local_stale]"
            [[ -n "$local_lock" ]] && marker="$marker [LOCKED:$local_lock]"
            echo "  $local_id$marker"
        done
        echo "── blocked/ ──"
        ls -1 "$WORK_ITEM_ROOT/blocked" 2>/dev/null || true
        if dep_summary=$(uv run --no-project python "$(dirname "$AGENTS_DIR")/work-queue/dep_graph.py" --summary 2>/dev/null); then
            echo "$dep_summary"
        fi
        ;;
    approve-batch)
        # WRK-159: List approvable items and approve selected ones
        local_items="$(list_approvable_items)"
        if [[ -z "$local_items" ]]; then
            echo "No items eligible for batch approval (need ## Plan but no plan_approved: true)."
            exit 0
        fi

        echo "═══ Approvable Items ═══"
        local_idx=0
        while IFS='|' read -r f wid title complexity plan_line; do
            local_idx=$((local_idx + 1))
            echo "  [$local_idx] $wid ($complexity) — $title"
            echo "       Plan: $plan_line"
        done <<< "$local_items"
        echo ""

        # Check for --approve-all flag
        approve_all=false
        for arg in "$@"; do
            [[ "$arg" == "--approve-all" ]] && approve_all=true
        done

        if [[ "$approve_all" == "true" ]]; then
            echo "Approving all $local_idx item(s)..."
            approve_items "$local_items"
        else
            echo "Pass --approve-all to approve all, or use interactively."
            echo "Items listed: $local_idx"
        fi
        ;;
    next)
        # WRK-161: Recommend next item based on pipeline balance
        ensure_pipeline_store
        recommended_stage="$(pipeline_recommend_stage)"
        echo "Pipeline recommendation: stage with fewest sessions = $recommended_stage"
        echo ""

        # Find highest-priority pending item
        best_file="" best_id="" best_priority="" best_prio_rank=99
        for f in "$WORK_ITEM_ROOT/pending"/WRK-*.md; do
            [[ -f "$f" ]] || continue
            local_lock="$(wrk_get_frontmatter_value "$f" "locked_by")"
            [[ -n "$local_lock" ]] && continue  # skip locked items

            local_prio="$(wrk_get_frontmatter_value "$f" "priority")"
            local_rank=50
            case "$local_prio" in
                high) local_rank=10 ;;
                medium) local_rank=30 ;;
                low) local_rank=50 ;;
            esac

            if [[ "$local_rank" -lt "$best_prio_rank" ]]; then
                best_prio_rank="$local_rank"
                best_file="$f"
                best_id="$(basename "$f" .md)"
                best_priority="$local_prio"
            fi
        done

        if [[ -n "$best_id" ]]; then
            local_title="$(wrk_get_frontmatter_value "$best_file" "title")"
            echo "Recommended: $best_id ($best_priority) — $local_title"
        else
            echo "No unlocked pending items available."
        fi
        ;;
    status)
        # WRK-161: Show pipeline status dashboard
        ensure_pipeline_store
        echo "═══ Pipeline Dashboard ═══"
        echo ""
        printf "%-30s %-8s %-10s %-25s %s\n" "SESSION" "PROVIDER" "WRK" "STAGE" "REGISTERED"
        echo "────────────────────────────── ──────── ────────── ───────────────────────── ────────────────────"
        pipeline_list_sessions
        echo ""
        pipeline_balance
        ;;
    *)
        echo "Unsupported subcommand for wrapper: $subcmd" >&2
        echo "Available: run, list, approve-batch, next, status" >&2
        exit 2
        ;;
esac
