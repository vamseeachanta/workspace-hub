#!/usr/bin/env bash
#
# Adaptive Selection Optimizer
# Shows effective routing table after EWMA adjustments,
# flags models below poor_threshold, suggests tier-specific swaps.
# Version: 2.0.0
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIB_DIR="$SCRIPT_DIR/lib"
export CONFIG_DIR="${CONFIG_DIR:-$(cd "$SCRIPT_DIR/../../.." && pwd)/config}"
LOG_DIR="${LOG_DIR:-$SCRIPT_DIR/logs}"

source "$LIB_DIR/model_registry.sh"

_load_model_registry || { echo "Error: Cannot load model registry" >&2; exit 1; }

echo "=== Adaptive Routing Optimizer ==="
echo "EWMA alpha=$_EWMA_ALPHA | seed=$_EWMA_SEED | min_ratings=$_EWMA_MIN_RATINGS | poor_threshold=$_EWMA_POOR_THRESHOLD"
echo ""

# --- Effective routing table ---
echo "=== Effective Routing Table ==="
for tier in SIMPLE STANDARD COMPLEX REASONING; do
    for provider in claude codex gemini; do
        model=$(select_model_for_provider "$provider" "$tier")
        ewma=$(_compute_ewma "$model" "$tier")
        count=$(_count_ratings "$model" "$tier")
        if [[ "$count" -ge "$_EWMA_MIN_RATINGS" ]]; then
            src="ewma"
        else
            src="priority"
        fi
        printf "  %-10s %-8s -> %-25s (EWMA=%s, n=%s, src=%s)\n" "$tier" "$provider" "$model" "$ewma" "$count" "$src"
    done
done
echo ""

# --- Flag models below poor threshold ---
echo "=== Model Health ==="
poor_found=false
while read -r key ewma count; do
    if [[ "$count" -ge "$_EWMA_MIN_RATINGS" ]]; then
        if awk -v e="$ewma" -v t="$_EWMA_POOR_THRESHOLD" 'BEGIN { exit !(e < t) }' 2>/dev/null; then
            echo "  WARNING: $key EWMA=$ewma < threshold=$_EWMA_POOR_THRESHOLD ($count ratings)"
            poor_found=true
        fi
    fi
done < <(get_model_ewma_summary)

if ! $poor_found; then
    echo "  All models above poor threshold ($_EWMA_POOR_THRESHOLD)"
fi
echo ""

# --- Suggest tier-specific swaps ---
echo "=== Tier-Specific Recommendations ==="
for tier in SIMPLE STANDARD COMPLEX REASONING; do
    best_key="" best_ewma="-1" best_count="0"
    for key in "${_REG_ALL_MODELS[@]}"; do
        read -r ewma count <<< "$(get_model_tier_ewma "$key" "$tier")"
        if [[ "$count" -ge "$_EWMA_MIN_RATINGS" ]]; then
            if awk -v a="$ewma" -v b="$best_ewma" 'BEGIN { exit !(a > b) }' 2>/dev/null; then
                best_key="$key"
                best_ewma="$ewma"
                best_count="$count"
            fi
        fi
    done
    if [[ -n "$best_key" ]]; then
        echo "  $tier: Best performer = $best_key (EWMA=$best_ewma, n=$best_count)"
    else
        echo "  $tier: Insufficient data for recommendation (need >= $_EWMA_MIN_RATINGS ratings)"
    fi
done
