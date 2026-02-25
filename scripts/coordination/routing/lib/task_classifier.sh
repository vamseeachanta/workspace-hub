#!/usr/bin/env bash
#
# Multi-Dimension Task Classifier
# Inspired by ClawRouter's 14-dimension scoring, adapted for CLI agents
# Version: 2.0.0
#

# --- Configuration ---
CONFIG_DIR="${CONFIG_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)/config}"

# --- Dimension weights (must sum to 1.0) ---
declare -A DIMENSION_WEIGHTS=(
    [reasoning_depth]=0.20
    [code_density]=0.18
    [architecture_scope]=0.15
    [implementation_action]=0.12
    [research_analysis]=0.10
    [task_complexity]=0.08
    [agentic_markers]=0.06
    [review_quality]=0.05
    [data_processing]=0.04
    [simple_indicators]=0.02
)

# --- Tier boundaries (calibrated for normalized [-1,1] → [0,1] scoring) ---
# Neutral base (all dims at -0.5) ≈ 0.25, so boundaries must account for this
TIER_SIMPLE=0.30
TIER_STANDARD=0.45
TIER_COMPLEX=0.55

# --- Helper: awk float math ---
_fmul() { awk "BEGIN { printf \"%.4f\", $1 * $2 }"; }
_fadd() { awk "BEGIN { printf \"%.4f\", $1 + $2 }"; }
_fsub() { awk "BEGIN { printf \"%.4f\", $1 - $2 }"; }
_fdiv() { awk "BEGIN { if ($2 == 0) printf \"0.0000\"; else printf \"%.4f\", $1 / $2 }"; }
_fgt()  { awk "BEGIN { exit !($1 > $2) }"; }
_fabs() { awk "BEGIN { v = $1; if (v < 0) v = -v; printf \"%.4f\", v }"; }

# --- Dimension scorers ---
# Each returns a float between -1.0 and +1.0

_score_reasoning_depth() {
    local text="$1"
    local score=0
    local hits=0
    local patterns=("prove" "analyze why" "trade.offs?" "compare" "contrast" "justify"
                    "explain why" "reason" "evaluate" "assess" "implications" "consequences"
                    "what if" "hypothe" "theorem" "converge" "numerical" "instability"
                    "algorithm" "mathematical" "formal" "correctness")
    for p in "${patterns[@]}"; do
        if [[ "$text" =~ $p ]]; then ((hits++)); fi
    done
    # Normalize: 0 hits = -0.5, 1 hit = 0.0, 2+ hits scale to +1.0
    if (( hits == 0 )); then score="-0.5"
    elif (( hits == 1 )); then score="0.3"
    elif (( hits == 2 )); then score="0.6"
    else score="1.0"; fi
    echo "$score"
}

_score_code_density() {
    local text="$1"
    local score=0
    local hits=0
    # Code indicators
    local patterns=('```' "function " "class " "import " "def " "return " "[.]py" "[.]sh"
                    "[.]ts" "[.]js" "[.]yaml" "[.]json" "[.]sql" "module" "package")
    for p in "${patterns[@]}"; do
        if [[ "$text" =~ $p ]]; then ((hits++)); fi
    done
    if (( hits == 0 )); then score="-0.5"
    elif (( hits <= 2 )); then score="0.3"
    elif (( hits <= 4 )); then score="0.6"
    else score="1.0"; fi
    echo "$score"
}

_score_architecture_scope() {
    local text="$1"
    local hits=0
    local patterns=("design" "architect" "system" "pattern" "pipeline" "framework"
                    "infra" "schema" "migration" "multi.repo" "cross.cutting" "interface"
                    "abstraction" "decouple" "modular" "layered")
    for p in "${patterns[@]}"; do
        if [[ "$text" =~ $p ]]; then ((hits++)); fi
    done
    if (( hits == 0 )); then echo "-0.5"
    elif (( hits == 1 )); then echo "0.2"
    elif (( hits == 2 )); then echo "0.5"
    elif (( hits <= 4 )); then echo "0.8"
    else echo "1.0"; fi
}

_score_implementation_action() {
    local text="$1"
    local hits=0
    local patterns=("implement" "fix" "refactor" "add " "create" "build" "write"
                    "update" "modify" "change" "rename" "move" "delete" "remove"
                    "parse" "parser" "convert" "generate")
    for p in "${patterns[@]}"; do
        if [[ "$text" =~ $p ]]; then ((hits++)); fi
    done
    if (( hits == 0 )); then echo "-0.5"
    elif (( hits == 1 )); then echo "0.3"
    elif (( hits <= 3 )); then echo "0.6"
    else echo "1.0"; fi
}

_score_research_analysis() {
    local text="$1"
    local hits=0
    local patterns=("research" "explain" "summarize" "document" "describe" "overview"
                    "investigate" "explore" "understand" "report" "survey" "literature"
                    "findings" "analysis")
    for p in "${patterns[@]}"; do
        if [[ "$text" =~ $p ]]; then ((hits++)); fi
    done
    if (( hits == 0 )); then echo "-0.5"
    elif (( hits == 1 )); then echo "0.3"
    elif (( hits <= 3 )); then echo "0.6"
    else echo "1.0"; fi
}

_score_task_complexity() {
    local text="$1"
    local word_count
    word_count=$(echo "$text" | wc -w | tr -d ' ')
    local sentence_count
    sentence_count=$(echo "$text" | grep -o '[.!?]' | wc -l | tr -d ' ')
    local question_marks
    question_marks=$(echo "$text" | grep -o '?' | wc -l | tr -d ' ')
    local constraint_words=0
    local cpatterns=("must" "should" "require" "constraint" "limit" "ensure" "guarantee"
                     "at least" "at most" "no more than" "between" "within")
    for p in "${cpatterns[@]}"; do
        if [[ "$text" =~ $p ]]; then ((constraint_words++)); fi
    done

    # Composite: word count drives base, constraints and questions add
    local base_score
    if (( word_count < 10 )); then base_score="-0.8"
    elif (( word_count < 30 )); then base_score="-0.3"
    elif (( word_count < 80 )); then base_score="0.2"
    elif (( word_count < 200 )); then base_score="0.5"
    else base_score="0.8"; fi

    # Adjust for constraints and questions
    local adjust=0
    if (( constraint_words > 2 )); then adjust="0.2"
    elif (( constraint_words > 0 )); then adjust="0.1"; fi
    if (( question_marks > 2 )); then adjust=$(_fadd "$adjust" "0.1"); fi

    local final
    final=$(_fadd "$base_score" "$adjust")
    # Clamp to [-1, 1]
    if _fgt "$final" "1.0"; then final="1.0"; fi
    echo "$final"
}

_score_agentic_markers() {
    local text="$1"
    local hits=0
    local patterns=("run tests" "deploy" "execute" "build" "install" "compile"
                    "docker" "ci/cd" "pipeline" "script" "shell" "terminal"
                    "command" "spawn" "invoke")
    for p in "${patterns[@]}"; do
        if [[ "$text" =~ $p ]]; then ((hits++)); fi
    done
    if (( hits == 0 )); then echo "-0.3"
    elif (( hits == 1 )); then echo "0.3"
    elif (( hits <= 3 )); then echo "0.6"
    else echo "1.0"; fi
}

_score_review_quality() {
    local text="$1"
    local hits=0
    local patterns=("review" "audit" "check" "validate" "security" "quality"
                    "inspect" "verify" "lint" "compliance" "standard")
    for p in "${patterns[@]}"; do
        if [[ "$text" =~ $p ]]; then ((hits++)); fi
    done
    if (( hits == 0 )); then echo "-0.3"
    elif (( hits == 1 )); then echo "0.3"
    elif (( hits <= 3 )); then echo "0.7"
    else echo "1.0"; fi
}

_score_data_processing() {
    local text="$1"
    local hits=0
    local patterns=("parse" "transform" "csv" "json" "database" "query" "sql"
                    "dataframe" "polars" "pandas" "etl" "ingest" "export"
                    "filter" "aggregate" "pivot" "merge")
    for p in "${patterns[@]}"; do
        if [[ "$text" =~ $p ]]; then ((hits++)); fi
    done
    if (( hits == 0 )); then echo "-0.3"
    elif (( hits == 1 )); then echo "0.3"
    elif (( hits <= 3 )); then echo "0.6"
    else echo "1.0"; fi
}

_score_simple_indicators() {
    local text="$1"
    local word_count
    word_count=$(echo "$text" | wc -w | tr -d ' ')
    local hits=0
    local patterns=("what is" "define" "quick" "status" "list" "show" "tell me"
                    "how many" "where is" "which")
    for p in "${patterns[@]}"; do
        if [[ "$text" =~ $p ]]; then ((hits++)); fi
    done
    # Short tasks with simple patterns score high (inverted: high = simple)
    if (( hits > 0 && word_count < 15 )); then echo "1.0"
    elif (( hits > 0 )); then echo "0.5"
    elif (( word_count < 8 )); then echo "0.7"
    else echo "-0.5"; fi
}

# --- Tier classification ---
_classify_tier() {
    local score="$1"
    if ! _fgt "$score" "$TIER_SIMPLE"; then
        echo "SIMPLE"
    elif ! _fgt "$score" "$TIER_STANDARD"; then
        echo "STANDARD"
    elif ! _fgt "$score" "$TIER_COMPLEX"; then
        echo "COMPLEX"
    else
        echo "REASONING"
    fi
}

# --- Confidence calculation ---
# Distance from nearest tier boundary, mapped through simplified sigmoid
_calculate_confidence() {
    local score="$1"
    local min_dist="1.0"
    for boundary in $TIER_SIMPLE $TIER_STANDARD $TIER_COMPLEX; do
        local dist
        dist=$(_fsub "$score" "$boundary")
        dist=$(_fabs "$dist")
        if ! _fgt "$dist" "$min_dist" 2>/dev/null; then
            # dist is not greater than min_dist, so dist <= min_dist
            min_dist="$dist"
        fi
    done
    # Also check distance from 0.0 and 1.0 boundaries
    local d0; d0=$(_fabs "$score")
    local d1; d1=$(_fsub "1.0" "$score"); d1=$(_fabs "$d1")
    if ! _fgt "$d0" "$min_dist" 2>/dev/null; then min_dist="$d0"; fi
    if ! _fgt "$d1" "$min_dist" 2>/dev/null; then min_dist="$d1"; fi

    # Simplified sigmoid: confidence = min_dist * 4, clamped to [0, 1]
    local confidence
    confidence=$(_fmul "$min_dist" "4.0")
    if _fgt "$confidence" "1.0"; then confidence="1.0"; fi
    echo "$confidence"
}

# --- Determine primary provider from dimension scores ---
_determine_provider() {
    local reasoning="$1" code="$2" arch="$3" impl="$4" research="$5"
    local agentic="$6" review="$7" data="$8" simple="$9"

    # Claude signal: reasoning + architecture
    local claude_signal
    claude_signal=$(awk "BEGIN { printf \"%.4f\", ($reasoning * 0.4) + ($arch * 0.35) + ($review * 0.25) }")

    # Codex signal: code + implementation + agentic (impl weighted highest)
    local codex_signal
    codex_signal=$(awk "BEGIN { printf \"%.4f\", ($code * 0.30) + ($impl * 0.45) + ($agentic * 0.25) }")

    # Gemini signal: research + data + simple (research weighted highest)
    local gemini_signal
    gemini_signal=$(awk "BEGIN { printf \"%.4f\", ($research * 0.45) + ($data * 0.30) + ($simple * 0.25) }")

    # Pick highest
    local provider="codex"
    local best="$codex_signal"
    if _fgt "$claude_signal" "$best" 2>/dev/null; then
        provider="claude"
        best="$claude_signal"
    fi
    if _fgt "$gemini_signal" "$best" 2>/dev/null; then
        provider="gemini"
    fi
    echo "$provider"
}

# --- Main classifier function ---
# @param $1: Task description (string)
# @return: JSON with tier, confidence, dimensions, primary_provider
classify_task() {
    local task_description="$1"
    local task_lower
    task_lower=$(echo "$task_description" | tr '[:upper:]' '[:lower:]')

    # Score each dimension
    local d_reasoning; d_reasoning=$(_score_reasoning_depth "$task_lower")
    local d_code; d_code=$(_score_code_density "$task_lower")
    local d_arch; d_arch=$(_score_architecture_scope "$task_lower")
    local d_impl; d_impl=$(_score_implementation_action "$task_lower")
    local d_research; d_research=$(_score_research_analysis "$task_lower")
    local d_complexity; d_complexity=$(_score_task_complexity "$task_lower")
    local d_agentic; d_agentic=$(_score_agentic_markers "$task_lower")
    local d_review; d_review=$(_score_review_quality "$task_lower")
    local d_data; d_data=$(_score_data_processing "$task_lower")
    local d_simple; d_simple=$(_score_simple_indicators "$task_lower")

    # Weighted sum (normalize from [-1,1] to [0,1] first: (score + 1) / 2)
    local weighted_sum
    weighted_sum=$(awk "BEGIN {
        sum = 0
        sum += (($d_reasoning + 1) / 2) * 0.20
        sum += (($d_code + 1) / 2) * 0.18
        sum += (($d_arch + 1) / 2) * 0.15
        sum += (($d_impl + 1) / 2) * 0.12
        sum += (($d_research + 1) / 2) * 0.10
        sum += (($d_complexity + 1) / 2) * 0.08
        sum += (($d_agentic + 1) / 2) * 0.06
        sum += (($d_review + 1) / 2) * 0.05
        sum += (($d_data + 1) / 2) * 0.04
        sum += (($d_simple + 1) / 2) * 0.02
        printf \"%.4f\", sum
    }")

    local tier; tier=$(_classify_tier "$weighted_sum")
    local confidence; confidence=$(_calculate_confidence "$weighted_sum")
    local provider; provider=$(_determine_provider "$d_reasoning" "$d_code" "$d_arch" \
        "$d_impl" "$d_research" "$d_agentic" "$d_review" "$d_data" "$d_simple")

    # Build JSON output
    jq -n \
        --arg tier "$tier" \
        --arg confidence "$confidence" \
        --arg score "$weighted_sum" \
        --arg provider "$provider" \
        --arg d_reasoning "$d_reasoning" \
        --arg d_code "$d_code" \
        --arg d_arch "$d_arch" \
        --arg d_impl "$d_impl" \
        --arg d_research "$d_research" \
        --arg d_complexity "$d_complexity" \
        --arg d_agentic "$d_agentic" \
        --arg d_review "$d_review" \
        --arg d_data "$d_data" \
        --arg d_simple "$d_simple" \
        '{
            tier: $tier,
            confidence: ($confidence | tonumber),
            weighted_score: ($score | tonumber),
            primary_provider: $provider,
            dimensions: {
                reasoning_depth: ($d_reasoning | tonumber),
                code_density: ($d_code | tonumber),
                architecture_scope: ($d_arch | tonumber),
                implementation_action: ($d_impl | tonumber),
                research_analysis: ($d_research | tonumber),
                task_complexity: ($d_complexity | tonumber),
                agentic_markers: ($d_agentic | tonumber),
                review_quality: ($d_review | tonumber),
                data_processing: ($d_data | tonumber),
                simple_indicators: ($d_simple | tonumber)
            },
            all_scores: {
                codex: (((($d_code | tonumber) * 0.35) + (($d_impl | tonumber) * 0.35) + (($d_agentic | tonumber) * 0.30)) * 100 | floor),
                claude: (((($d_reasoning | tonumber) * 0.4) + (($d_arch | tonumber) * 0.35) + (($d_review | tonumber) * 0.25)) * 100 | floor),
                gemini: (((($d_research | tonumber) * 0.40) + (($d_data | tonumber) * 0.35) + (($d_simple | tonumber) * 0.25)) * 100 | floor)
            }
        }'
}
