#!/usr/bin/env bash
#
# Tier-to-Provider Router
# Maps classification tiers to provider chains with availability checks
# Version: 2.0.0
#

# --- Configuration ---
ROUTER_CONFIG_DIR="${CONFIG_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)/config}"
ROUTING_CONFIG="${ROUTER_CONFIG_DIR}/agents/routing-config.yaml"

# --- Default routing table (used if YAML config not found) ---
declare -A TIER_PRIMARY=(
    [SIMPLE]="codex"
    [STANDARD]="codex"
    [COMPLEX]="claude"
    [REASONING]="claude"
)

declare -A TIER_FALLBACK1=(
    [SIMPLE]="gemini"
    [STANDARD]="claude"
    [COMPLEX]="gemini"
    [REASONING]="gemini"
)

declare -A TIER_FALLBACK2=(
    [SIMPLE]="claude"
    [STANDARD]="gemini"
    [COMPLEX]="codex"
    [REASONING]="codex"
)

# --- Function: check_provider_available ---
# Checks if a provider's CLI tool is installed and reachable
# @param $1: provider name (claude|codex|gemini)
# @return: 0 if available, 1 if not
check_provider_available() {
    local provider="$1"
    case "$provider" in
        "claude") command -v claude &>/dev/null ;;
        "codex")  command -v codex &>/dev/null ;;
        "gemini") command -v gemini &>/dev/null ;;
        *) return 1 ;;
    esac
}

# --- Function: route_by_tier ---
# Routes a classified task to the best available provider
# @param $1: tier (SIMPLE|STANDARD|COMPLEX|REASONING)
# @param $2: classifier_provider (optional, from dimension analysis)
# @param $3: confidence (float)
# @return: JSON routing decision
route_by_tier() {
    local tier="$1"
    local classifier_provider="${2:-}"
    local confidence="${3:-0.5}"

    local tier_primary="${TIER_PRIMARY[$tier]}"
    local fallback1="${TIER_FALLBACK1[$tier]}"
    local fallback2="${TIER_FALLBACK2[$tier]}"

    # Always prefer classifier's provider recommendation (dimension-aware),
    # fall back to tier-based defaults if classifier provider unavailable
    local primary="${classifier_provider:-$tier_primary}"
    local auto_route="false"
    if awk "BEGIN { exit !($confidence >= 0.70) }" 2>/dev/null; then
        auto_route="true"
    fi

    # Build candidate list: classifier's pick first, then tier defaults
    local chosen=""
    local reason=""
    local -a candidates=("$primary")
    # Add tier-based fallbacks, avoiding duplicates
    for fb in "$tier_primary" "$fallback1" "$fallback2"; do
        local dup=false
        for c in "${candidates[@]}"; do
            if [[ "$c" == "$fb" ]]; then dup=true; break; fi
        done
        $dup || candidates+=("$fb")
    done

    for candidate in "${candidates[@]}"; do
        if check_provider_available "$candidate"; then
            chosen="$candidate"
            if [[ "$candidate" == "$primary" ]]; then
                reason="Classifier-preferred provider available ($chosen, tier=$tier)"
            else
                reason="Fallback: $primary unavailable, using $candidate (tier=$tier)"
            fi
            break
        fi
    done

    # Emergency: no provider available
    if [[ -z "$chosen" ]]; then
        chosen="claude"
        reason="Emergency: no CLI providers detected, defaulting to claude"
    fi

    # Select best model for chosen provider (adaptive EWMA)
    local selected_model="" model_ewma="" model_selection="default"
    if type select_model_for_provider &>/dev/null; then
        selected_model=$(select_model_for_provider "$chosen" "$tier")
        model_ewma=$(_compute_ewma "$selected_model" "$tier")
        local model_count
        model_count=$(_count_ratings "$selected_model" "$tier")
        if [[ "$model_count" -ge "$_EWMA_MIN_RATINGS" ]]; then
            model_selection="ewma"
        else
            model_selection="priority"
        fi
    fi

    jq -n \
        --arg provider "$chosen" \
        --arg tier "$tier" \
        --arg reason "$reason" \
        --argjson auto_route "$auto_route" \
        --arg confidence "$confidence" \
        --arg primary "$primary" \
        --arg fallback1 "$fallback1" \
        --arg fallback2 "$fallback2" \
        --arg model "${selected_model:-}" \
        --arg model_ewma "${model_ewma:-}" \
        --arg model_selection "$model_selection" \
        '{
            provider: $provider,
            tier: $tier,
            reason: $reason,
            auto_route: $auto_route,
            confidence: ($confidence | tonumber),
            routing_chain: [$primary, $fallback1, $fallback2],
            model: $model,
            model_ewma: $model_ewma,
            model_selection: $model_selection
        }'
}
