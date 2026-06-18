#!/usr/bin/env bash
#
# Tier-to-Provider Router
# Maps classification tiers to provider chains with availability checks
# Version: 2.0.0
#

# --- Configuration ---
ROUTER_CONFIG_DIR="${CONFIG_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)/config}"
ROUTING_CONFIG="${ROUTER_CONFIG_DIR}/agents/routing-config.yaml"

# Single routing resolver (#3205) — the only forbid-policy interpreter.
RESOLVER="${RESOLVER:-$(dirname "$ROUTER_CONFIG_DIR")/scripts/ai/routing_resolver.py}"

# Invoke the resolver per the repo `uv run` contract, with a python3 fallback
# (the resolver self-bootstraps pyyaml). Returns the resolver's exit code so
# callers can fail closed on an unknown context (exit 3).
_resolver() {
    if command -v uv >/dev/null 2>&1; then
        uv run --quiet "$RESOLVER" "$@"
    else
        python3 "$RESOLVER" "$@"
    fi
}

# >>> GENERATED FROM config/agents/routing-config.yaml tiers.* — DO NOT HAND-EDIT (#3209)
# Regenerate:  uv run scripts/ai/routing_resolver.py --emit-bash-table
# Drift-guard: tests/coordination/test_tier_table_no_drift.py (fails CI on divergence)
# Cost-aligned single source: cheap tiers route to codex, not claude.
declare -A TIER_PRIMARY=( [SIMPLE]="codex" [STANDARD]="codex" [COMPLEX]="claude" [REASONING]="claude" )
declare -A TIER_FALLBACK1=( [SIMPLE]="gemini" [STANDARD]="claude" [COMPLEX]="gemini" [REASONING]="gemini" )
declare -A TIER_FALLBACK2=( [SIMPLE]="claude" [STANDARD]="gemini" [COMPLEX]="codex" [REASONING]="codex" )
# <<< END GENERATED

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

    # Cost-ceiling enforcement (#3205): drop providers forbidden for the active
    # execution context. Fail closed on an unknown/invalid context — never fall
    # through to claude. Interactive path (no ROUTE_CONTEXT) is unchanged.
    local forbidden=""
    if [[ -n "${ROUTE_CONTEXT:-}" && ${#candidates[@]} -gt 0 ]]; then
        local _csv; _csv="$(IFS=,; echo "${candidates[*]}")"
        local _filtered
        if ! _filtered="$(_resolver --context "$ROUTE_CONTEXT" --filter "$_csv")"; then
            echo "route_by_tier: unknown/invalid context '$ROUTE_CONTEXT' — aborting (fail closed)" >&2
            return 3
        fi
        mapfile -t candidates <<< "$_filtered"
        # Defensive: drop any empty element introduced by a trailing newline.
        local _clean=(); local c
        for c in "${candidates[@]}"; do [[ -n "$c" ]] && _clean+=("$c"); done
        candidates=("${_clean[@]}")
        forbidden="$(_resolver --context "$ROUTE_CONTEXT" --forbidden | tr '\n' ' ' | sed 's/ *$//')"
    fi

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

    # Emergency: no provider available. Under a cost-ceiling context, NEVER
    # default to claude — use the context's (CLI-normalized) primary instead.
    if [[ -z "$chosen" ]]; then
        if [[ -n "${ROUTE_CONTEXT:-}" ]]; then
            chosen="$(_resolver --context "$ROUTE_CONTEXT" --chain | head -1)"
            reason="Emergency under context $ROUTE_CONTEXT: defaulting to context primary $chosen"
        else
            chosen="claude"
            reason="Emergency: no CLI providers detected, defaulting to claude"
        fi
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
        --arg context "${ROUTE_CONTEXT:-}" \
        --arg forbidden "${forbidden:-}" \
        '{
            provider: $provider,
            tier: $tier,
            reason: $reason,
            auto_route: $auto_route,
            confidence: ($confidence | tonumber),
            routing_chain: [$primary, $fallback1, $fallback2],
            model: $model,
            model_ewma: $model_ewma,
            model_selection: $model_selection,
            context: $context,
            forbidden: ($forbidden | if . == "" then [] else split(" ") end)
        }'
}
