#!/usr/bin/env bash
# cleanup.sh — Phase 7: Archive processed signals, truncate pending
# 100% shell, 0% API

phase_cleanup() {
    [[ "$DRY_RUN" == "true" ]] && { echo "improve/cleanup: dry-run mode, skipping cleanup"; return 0; }

    local archive_dir="${STATE_DIR}/archive/${DATE_TAG}/improve"
    mkdir -p "$archive_dir" 2>/dev/null

    # Archive the merged signals used by this run
    if [[ -f "${IMPROVE_WORKDIR}/merged_signals.jsonl" ]]; then
        cp "${IMPROVE_WORKDIR}/merged_signals.jsonl" \
            "${archive_dir}/merged_signals_$(date +%H%M%S).jsonl" 2>/dev/null
    fi

    # Archive classified results
    if [[ -f "${IMPROVE_WORKDIR}/classified.json" ]]; then
        cp "${IMPROVE_WORKDIR}/classified.json" \
            "${archive_dir}/classified_$(date +%H%M%S).json" 2>/dev/null
    fi

    # Archive ecosystem metrics
    if [[ -f "${IMPROVE_WORKDIR}/ecosystem_metrics.json" ]]; then
        cp "${IMPROVE_WORKDIR}/ecosystem_metrics.json" \
            "${archive_dir}/ecosystem_$(date +%H%M%S).json" 2>/dev/null
    fi

    # NOTE: We do NOT truncate pending-reviews/*.jsonl here because
    # consume-signals.sh (Stop hook #4) already handles that.
    # We only archive our own work products.

    echo "improve/cleanup: archived to ${archive_dir}"
    return 0
}
