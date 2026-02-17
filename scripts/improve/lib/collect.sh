#!/usr/bin/env bash
# collect.sh — Phase 1: Merge all JSONL signals into unified format
# 100% shell, 0% API

phase_collect() {
    local merged="${IMPROVE_WORKDIR}/merged_signals.jsonl"
    local signal_count=0

    : > "$merged"  # Start fresh

    # --- Merge pending-reviews JSONL files ---
    for f in "${REVIEW_DIR}"/*.jsonl; do
        [[ ! -f "$f" ]] && continue
        [[ ! -s "$f" ]] && continue
        local basename_f
        basename_f=$(basename "$f" .jsonl)
        # Skip session-summaries (consumed by consume-signals.sh)
        [[ "$basename_f" == "session-summaries" ]] && continue

        # Tag each line with its source type
        while IFS= read -r line; do
            [[ -z "$line" ]] && continue
            # Validate JSON
            if echo "$line" | jq empty 2>/dev/null; then
                echo "$line" | jq -c --arg src "$basename_f" '. + {signal_source: $src}' >> "$merged"
                signal_count=$((signal_count + 1))
            fi
        done < "$f"
    done

    # --- Add correction chain signals ---
    local corrections="${STATE_DIR}/corrections/.recent_edits"
    if [[ -f "$corrections" && -s "$corrections" ]]; then
        while IFS= read -r line; do
            [[ -z "$line" ]] && continue
            if echo "$line" | jq empty 2>/dev/null; then
                echo "$line" | jq -c '. + {signal_source: "correction_chain"}' >> "$merged"
                signal_count=$((signal_count + 1))
            fi
        done < "$corrections"
    fi

    # --- Add mature skill patterns from accumulator ---
    local accumulator="${STATE_DIR}/accumulator.json"
    if [[ -f "$accumulator" ]]; then
        jq -c '
            .skill_patterns // {}
            | to_entries[]
            | select(.value.mature == true)
            | {signal_source: "mature_pattern", pattern: .key,
               sessions: (.value.sessions | length), total: .value.total}
        ' "$accumulator" 2>/dev/null >> "$merged" || true
    fi

    echo "$signal_count" > "${IMPROVE_WORKDIR}/signal_count"

    if [[ "$signal_count" -eq 0 ]]; then
        echo "improve/collect: no signals found"
        return 1
    fi

    echo "improve/collect: merged ${signal_count} signals"
    return 0
}
