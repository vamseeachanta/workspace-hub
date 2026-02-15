#!/usr/bin/env bash
#
# Model Registry & EWMA Engine
# Loads per-provider model variants and computes adaptive ratings
# Version: 1.0.0
#

# --- Configuration ---
_MODEL_REGISTRY_FILE="${CONFIG_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)/config}/agents/model-registry.yaml"
_RATING_FILE="${LOG_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/logs}/agent-ratings.jsonl"

# --- EWMA defaults (overridden by registry YAML) ---
_EWMA_ALPHA="0.3"
_EWMA_SEED="3.0"
_EWMA_MIN_RATINGS="3"
_EWMA_POOR_THRESHOLD="2.5"

# --- Parsed registry data (populated by _load_model_registry) ---
declare -A _REG_DISPLAY_NAME=()
declare -A _REG_COST_TIER=()
declare -A _REG_CAPABILITY_TIER=()
declare -A _REG_DEFAULT_PRIORITY=()
declare -A _REG_DEFAULT_MODEL=()
declare -a _REG_ALL_MODELS=()
declare -A _REG_MODEL_PROVIDER=()
_MODEL_REGISTRY_LOADED=false

# --- Function: _load_model_registry ---
# Parse model-registry.yaml into bash arrays via awk state machine
_load_model_registry() {
    if $_MODEL_REGISTRY_LOADED; then
        return 0
    fi

    if [[ ! -f "$_MODEL_REGISTRY_FILE" ]]; then
        echo "Warning: Model registry not found at $_MODEL_REGISTRY_FILE" >&2
        _MODEL_REGISTRY_LOADED=true
        return 1
    fi

    local current_provider="" current_model=""

    # Parse EWMA settings
    _EWMA_ALPHA=$(awk '/^ewma:/{found=1} found && /alpha:/{print $2; exit}' "$_MODEL_REGISTRY_FILE")
    _EWMA_SEED=$(awk '/^ewma:/{found=1} found && /seed:/{print $2; exit}' "$_MODEL_REGISTRY_FILE")
    _EWMA_MIN_RATINGS=$(awk '/^ewma:/{found=1} found && /min_ratings:/{print $2; exit}' "$_MODEL_REGISTRY_FILE")
    _EWMA_POOR_THRESHOLD=$(awk '/^ewma:/{found=1} found && /poor_threshold:/{print $2; exit}' "$_MODEL_REGISTRY_FILE")

    # Parse providers and models via awk state machine
    while IFS='|' read -r provider model display cost cap priority default_model; do
        if [[ -n "$provider" && -n "$model" ]]; then
            local key="${provider}/${model}"
            _REG_DISPLAY_NAME["$key"]="$display"
            _REG_COST_TIER["$key"]="$cost"
            _REG_CAPABILITY_TIER["$key"]="$cap"
            _REG_DEFAULT_PRIORITY["$key"]="$priority"
            _REG_MODEL_PROVIDER["$key"]="$provider"
            _REG_ALL_MODELS+=("$key")
        fi
        if [[ -n "$provider" && -n "$default_model" ]]; then
            _REG_DEFAULT_MODEL["$provider"]="$default_model"
        fi
    done < <(awk '
    BEGIN { prov=""; mdl=""; dm="" }
    /^  [a-z]/ && /providers:/{ next }
    /^providers:/{ in_prov=1; next }
    in_prov && /^  [a-z]/ && /:$/ {
        prov=$1; sub(/:$/,"",prov); mdl=""; dm=""
        next
    }
    in_prov && /default_model:/ {
        dm=$2
        next
    }
    in_prov && /^      [a-z]/ && /:$/ {
        mdl=$1; sub(/:$/,"",mdl)
        # Trim leading whitespace
        gsub(/^[ \t]+/,"",mdl)
        next
    }
    in_prov && mdl != "" && /display_name:/ {
        dn=$0; sub(/.*display_name: *"?/,"",dn); sub(/"? *$/,"",dn)
    }
    in_prov && mdl != "" && /cost_tier:/ {
        ct=$2
    }
    in_prov && mdl != "" && /capability_tier:/ {
        cap=$2
    }
    in_prov && mdl != "" && /default_priority:/ {
        pri=$2
        # Emit record
        printf "%s|%s|%s|%s|%s|%s|%s\n", prov, mdl, dn, ct, cap, pri, dm
        dm=""
        mdl=""
        dn=""; ct=""; cap=""; pri=""
    }
    ' "$_MODEL_REGISTRY_FILE")

    _MODEL_REGISTRY_LOADED=true
    return 0
}

# --- Function: _get_models_for_provider ---
# List all model keys for a provider
# @param $1: provider name
# @output: space-separated model keys (e.g., "claude/opus-4-6 claude/sonnet-4-5")
_get_models_for_provider() {
    local provider="$1"
    local result=""
    for key in "${_REG_ALL_MODELS[@]}"; do
        if [[ "${_REG_MODEL_PROVIDER[$key]}" == "$provider" ]]; then
            result="$result $key"
        fi
    done
    echo "$result"
}

# --- Function: _compute_ewma ---
# Compute EWMA for a specific model, optionally filtered by tier
# @param $1: model key (e.g., "claude/opus-4-6")
# @param $2: tier filter (optional, e.g., "COMPLEX")
# @return: EWMA value (float)
_compute_ewma() {
    local model="$1"
    local tier="${2:-}"
    local provider="${model%%/*}"
    local model_id="${model##*/}"

    if [[ ! -f "$_RATING_FILE" ]] || [[ ! -s "$_RATING_FILE" ]]; then
        echo "$_EWMA_SEED"
        return
    fi

    local ewma
    ewma=$(awk -v model="$model_id" -v provider="$provider" -v tier="$tier" \
               -v alpha="$_EWMA_ALPHA" -v seed="$_EWMA_SEED" '
    # Portable JSON field extractor (works with mawk and gawk)
    function json_str(line, key,    i, k, v) {
        k = "\"" key "\""; i = index(line, k)
        if (i == 0) return ""
        v = substr(line, i + length(k))
        sub(/^[^"]*"/, "", v); sub(/".*/, "", v)
        return v
    }
    function json_num(line, key,    i, k, v) {
        k = "\"" key "\""; i = index(line, k)
        if (i == 0) return ""
        v = substr(line, i + length(k))
        sub(/^[^0-9]*/, "", v); sub(/[^0-9.].*/, "", v)
        return v
    }
    BEGIN { ewma = seed; found = 0 }
    {
        p = json_str($0, "provider")
        m = json_str($0, "model")
        score = json_num($0, "score")
        t = json_str($0, "tier")

        # Skip entries without model field (old format)
        if (m == "" && model != "") next

        # Match provider and model
        if (p != provider) next
        if (m != "" && m != model) next

        # Filter by tier if specified
        if (tier != "" && t != "" && t != tier) next

        if (score != "") {
            ewma = alpha * score + (1 - alpha) * ewma
            found++
        }
    }
    END { printf "%.3f", ewma }
    ' "$_RATING_FILE")

    echo "$ewma"
}

# --- Function: _count_ratings ---
# Count ratings for a model, optionally filtered by tier
# @param $1: model key (e.g., "claude/opus-4-6")
# @param $2: tier filter (optional)
# @return: count (integer)
_count_ratings() {
    local model="$1"
    local tier="${2:-}"
    local provider="${model%%/*}"
    local model_id="${model##*/}"

    if [[ ! -f "$_RATING_FILE" ]] || [[ ! -s "$_RATING_FILE" ]]; then
        echo "0"
        return
    fi

    awk -v model="$model_id" -v provider="$provider" -v tier="$tier" '
    function json_str(line, key,    i, k, v) {
        k = "\"" key "\""; i = index(line, k)
        if (i == 0) return ""
        v = substr(line, i + length(k))
        sub(/^[^"]*"/, "", v); sub(/".*/, "", v)
        return v
    }
    BEGIN { count = 0 }
    {
        p = json_str($0, "provider")
        m = json_str($0, "model")
        t = json_str($0, "tier")
        if (m == "" && model != "") next
        if (p != provider) next
        if (m != "" && m != model) next
        if (tier != "" && t != "" && t != tier) next
        count++
    }
    END { print count }
    ' "$_RATING_FILE"
}

# --- Function: select_model_for_provider ---
# Pick best model for a provider based on EWMA or default priority
# @param $1: provider name
# @param $2: task tier (SIMPLE|STANDARD|COMPLEX|REASONING)
# @return: model key (e.g., "claude/opus-4-6")
select_model_for_provider() {
    local provider="$1"
    local tier="${2:-STANDARD}"

    _load_model_registry || true

    local models
    models=$(_get_models_for_provider "$provider")
    if [[ -z "$models" ]]; then
        # No models in registry, return provider default
        echo "${provider}/${_REG_DEFAULT_MODEL[$provider]:-default}"
        return
    fi

    local best_key="" best_score="-1"

    for key in $models; do
        local count ewma score
        count=$(_count_ratings "$key" "$tier")
        ewma=$(_compute_ewma "$key" "$tier")

        if [[ "$count" -ge "$_EWMA_MIN_RATINGS" ]]; then
            # Sufficient data: use EWMA
            score="$ewma"
        else
            # Cold start: normalize default_priority to 0-5 scale
            local priority="${_REG_DEFAULT_PRIORITY[$key]:-50}"
            score=$(awk -v p="$priority" 'BEGIN { printf "%.3f", p / 25.0 }')
        fi

        # Capability-tier bonus: +0.3 if model's capability tier matches task tier
        local cap_tier="${_REG_CAPABILITY_TIER[$key]:-}"
        if [[ "$cap_tier" == "$tier" ]]; then
            score=$(awk -v s="$score" 'BEGIN { printf "%.3f", s + 0.3 }')
        fi

        # Compare scores (awk for float comparison)
        if awk -v a="$score" -v b="$best_score" 'BEGIN { exit !(a > b) }' 2>/dev/null; then
            # Check poor threshold if we have enough data
            if [[ "$count" -ge "$_EWMA_MIN_RATINGS" ]]; then
                if awk -v e="$ewma" -v t="$_EWMA_POOR_THRESHOLD" 'BEGIN { exit !(e < t) }' 2>/dev/null; then
                    continue  # Skip models below poor threshold
                fi
            fi
            best_key="$key"
            best_score="$score"
        fi
    done

    if [[ -z "$best_key" ]]; then
        # All models below threshold, fall back to default
        best_key="${provider}/${_REG_DEFAULT_MODEL[$provider]:-default}"
    fi

    echo "$best_key"
}

# --- Function: get_model_display_name ---
# Lookup display name for a model key
# @param $1: model key (e.g., "claude/opus-4-6")
# @return: display name string
get_model_display_name() {
    local key="$1"
    _load_model_registry || true
    echo "${_REG_DISPLAY_NAME[$key]:-$key}"
}

# --- Function: get_model_ewma_summary ---
# Get EWMA summary for all models (used by --stats)
# @output: lines of "provider/model ewma count"
get_model_ewma_summary() {
    _load_model_registry || true
    for key in "${_REG_ALL_MODELS[@]}"; do
        local ewma count
        ewma=$(_compute_ewma "$key")
        count=$(_count_ratings "$key")
        echo "$key $ewma $count"
    done
}

# --- Function: get_model_tier_ewma ---
# Get per-tier EWMA for a model
# @param $1: model key
# @param $2: tier
# @output: "ewma count"
get_model_tier_ewma() {
    local key="$1"
    local tier="$2"
    local ewma count
    ewma=$(_compute_ewma "$key" "$tier")
    count=$(_count_ratings "$key" "$tier")
    echo "$ewma $count"
}
