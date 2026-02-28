#!/usr/bin/env bash
set -euo pipefail

AGENTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$AGENTS_DIR/lib/workflow-guards.sh"

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
        echo "Workflow orchestrator '$provider' acknowledged /work run contract."
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
