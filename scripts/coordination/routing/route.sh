#!/usr/bin/env bash
#
# Smart Agent Router - CLI Entry Point
# Usage: route.sh [OPTIONS] <task_description>
#
# Options:
#   --execute     Classify, recommend, and dispatch to agent
#   --wrk WRK-NNN  Route a work queue item by its ID
#   --rate <1-5> [provider/model]  Rate last routed agent (1=poor, 5=excellent)
#   --stats       Show routing decision history and agent ratings
#   --config      Show current routing table and provider status
#   -q, --quiet   Output JSON only (no progress messages)
#
# Version: 2.0.0
#

set -euo pipefail

# --- Resolve paths ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIB_DIR="$SCRIPT_DIR/lib"
export CONFIG_DIR="${CONFIG_DIR:-$(cd "$SCRIPT_DIR/../../.." && pwd)/config}"
LOG_DIR="${LOG_DIR:-$SCRIPT_DIR/logs}"
WORK_QUEUE_DIR="${WORK_QUEUE_DIR:-$(cd "$SCRIPT_DIR/../../.." && pwd)/.claude/work-queue}"

mkdir -p "$LOG_DIR"

# --- Source libraries ---
source "$LIB_DIR/usage_bootstrap.sh"
source "$LIB_DIR/task_classifier.sh"
source "$LIB_DIR/tier_router.sh"
source "$LIB_DIR/provider_filter.sh"
source "$LIB_DIR/cost_optimizer.sh"
source "$LIB_DIR/agent_dispatcher.sh"
source "$LIB_DIR/audit_logger.sh"
source "$LIB_DIR/model_registry.sh"

# --- Bootstrap usage files ---
bootstrap_usage_files

# --- Argument parsing ---
EXECUTE=false
WRK_ID=""
SHOW_STATS=false
SHOW_CONFIG=false
QUIET=false
TASK=""
RATE_SCORE=""
RATE_PROVIDER=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --execute)  EXECUTE=true; shift ;;
        --wrk)      WRK_ID="$2"; shift 2 ;;
        --rate)     RATE_SCORE="$2"; RATE_PROVIDER="${3:-}"; shift 2; [[ -n "$RATE_PROVIDER" ]] && shift ;;
        --stats)    SHOW_STATS=true; shift ;;
        --config)   SHOW_CONFIG=true; shift ;;
        -q|--quiet) QUIET=true; shift ;;
        -h|--help)
            sed -n '2,15p' "${BASH_SOURCE[0]}" | sed 's/^# \?//'
            exit 0 ;;
        *)          TASK="$1"; shift ;;
    esac
done

# --- Command: --rate ---
if [[ -n "$RATE_SCORE" ]]; then
    RATING_FILE="$LOG_DIR/agent-ratings.jsonl"
    if [[ "$RATE_SCORE" -lt 1 || "$RATE_SCORE" -gt 5 ]] 2>/dev/null; then
        echo "Error: Rating must be 1-5 (1=poor, 5=excellent)" >&2
        exit 1
    fi
    # Parse provider/model from RATE_PROVIDER (supports "claude/sonnet-4-5" syntax)
    RATE_MODEL=""
    if [[ "$RATE_PROVIDER" == *"/"* ]]; then
        RATE_MODEL="${RATE_PROVIDER##*/}"
        RATE_PROVIDER="${RATE_PROVIDER%%/*}"
    fi
    # If no provider specified, get from last audit log entry
    RATE_TIER=""
    if [[ -z "$RATE_PROVIDER" ]]; then
        AUDIT_FILE="$LOG_DIR/routing-decisions.jsonl"
        if [[ -f "$AUDIT_FILE" ]]; then
            RATE_PROVIDER=$(tail -1 "$AUDIT_FILE" | jq -r '.recommendation.provider // empty')
            RATE_MODEL=$(tail -1 "$AUDIT_FILE" | jq -r '.recommendation.model // empty')
            RATE_TIER=$(tail -1 "$AUDIT_FILE" | jq -r '.task_classification.tier // empty')
        fi
    fi
    # Auto-detect model from last audit if not specified
    if [[ -z "$RATE_MODEL" && -n "$RATE_PROVIDER" ]]; then
        AUDIT_FILE="$LOG_DIR/routing-decisions.jsonl"
        if [[ -f "$AUDIT_FILE" ]]; then
            RATE_MODEL=$(tail -1 "$AUDIT_FILE" | jq -r '.recommendation.model // empty')
            RATE_TIER=$(tail -1 "$AUDIT_FILE" | jq -r '.task_classification.tier // empty')
        fi
    fi
    if [[ -z "$RATE_PROVIDER" ]]; then
        echo "Error: No provider to rate. Specify: --rate <1-5> [provider/model]" >&2
        exit 1
    fi
    # Compute task_hash from last task if available
    RATE_TASK_HASH=""
    if [[ -f "${LOG_DIR}/routing-decisions.jsonl" ]]; then
        last_task=$(tail -1 "${LOG_DIR}/routing-decisions.jsonl" | jq -r '.task // empty')
        if [[ -n "$last_task" ]]; then
            RATE_TASK_HASH=$(echo -n "$last_task" | md5sum | cut -c1-6)
        fi
    fi
    jq -c -n \
        --arg timestamp "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
        --arg provider "$RATE_PROVIDER" \
        --arg model "$RATE_MODEL" \
        --argjson score "$RATE_SCORE" \
        --arg tier "$RATE_TIER" \
        --arg task_hash "$RATE_TASK_HASH" \
        '{
            timestamp: $timestamp,
            provider: $provider,
            model: $model,
            score: $score,
            tier: $tier,
            task_hash: $task_hash
        }' >> "$RATING_FILE"
    echo "Rated $RATE_PROVIDER${RATE_MODEL:+/$RATE_MODEL}: $RATE_SCORE/5"
    exit 0
fi

# --- Command: --stats ---
if $SHOW_STATS; then
    AUDIT_FILE="$LOG_DIR/routing-decisions.jsonl"
    RATING_FILE="$LOG_DIR/agent-ratings.jsonl"
    if [[ -f "$AUDIT_FILE" ]]; then
        echo "=== Routing Decision History ==="
        echo "Total decisions: $(wc -l < "$AUDIT_FILE")"
        echo ""
        echo "Per-provider counts:"
        jq -r '.recommendation.provider' "$AUDIT_FILE" 2>/dev/null | sort | uniq -c | sort -rn
        echo ""
        echo "Per-tier counts:"
        jq -r '.task_classification.tier' "$AUDIT_FILE" 2>/dev/null | sort | uniq -c | sort -rn
    else
        echo "No routing decisions logged yet."
    fi
    echo ""
    if [[ -f "$RATING_FILE" ]] && [[ -s "$RATING_FILE" ]]; then
        echo "=== Agent Ratings (Legacy Average) ==="
        echo "Total ratings: $(wc -l < "$RATING_FILE")"
        echo ""
        echo "Average rating per provider:"
        jq -r '.provider' "$RATING_FILE" | sort -u | while read -r prov; do
            avg=$(jq -r "select(.provider == \"$prov\") | .score" "$RATING_FILE" \
                | awk '{ sum += $1; n++ } END { if (n>0) printf "%.1f", sum/n; else print "N/A" }')
            count=$(jq -r "select(.provider == \"$prov\") | .score" "$RATING_FILE" | wc -l | tr -d ' ')
            echo "  $prov: $avg/5 ($count ratings)"
        done
        echo ""
        # Per-model EWMA breakdown
        _load_model_registry || true
        echo "=== Model Performance (EWMA) ==="
        while read -r key ewma count; do
            printf "  %-25s %s/5 (%s ratings)\n" "$key:" "$ewma" "$count"
        done < <(get_model_ewma_summary)
        echo ""
        echo "=== Per-Tier Model Performance ==="
        for t in SIMPLE STANDARD COMPLEX REASONING; do
            line="  $t:"
            for key in "${_REG_ALL_MODELS[@]}"; do
                read -r ewma count <<< "$(get_model_tier_ewma "$key" "$t")"
                if [[ "$count" -gt 0 ]]; then
                    line="$line $key ($ewma)"
                fi
            done
            # Only print tiers with data
            if [[ "$line" != "  $t:" ]]; then
                echo "$line"
            fi
        done
    else
        echo "=== Agent Ratings ==="
        echo "No ratings yet. Use: route.sh --rate <1-5> [provider/model]"
    fi
    exit 0
fi

# --- Command: --config ---
if $SHOW_CONFIG; then
    echo "=== Smart Agent Router Configuration (v2.0) ==="
    echo ""
    _load_model_registry || true
    echo "Provider Status:"
    for p in claude codex gemini; do
        if command -v "$p" &>/dev/null; then
            status="AVAILABLE"
        else
            status="NOT FOUND"
        fi
        echo "  $p: $status"
        # Show models for this provider
        models=$(_get_models_for_provider "$p")
        if [[ -n "$models" ]]; then
            printf "    Models:"
            for key in $models; do
                local_ewma=$(_compute_ewma "$key")
                local_pri="${_REG_DEFAULT_PRIORITY[$key]:-?}"
                printf " %s (priority=%s, EWMA=%s)" "${key##*/}" "$local_pri" "$local_ewma"
            done
            echo ""
        fi
    done
    echo ""
    echo "Routing Table:"
    echo "  SIMPLE    -> codex  (fallback: gemini, claude)"
    echo "  STANDARD  -> codex  (fallback: claude, gemini)"
    echo "  COMPLEX   -> claude (fallback: gemini, codex)"
    echo "  REASONING -> claude (fallback: gemini, codex)"
    echo ""
    echo "Adaptive Routing: enabled (EWMA alpha=$_EWMA_ALPHA, min_ratings=$_EWMA_MIN_RATINGS)"
    echo ""
    if [[ -f "$CONFIG_DIR/agents/routing-config.yaml" ]]; then
        echo "Config: $CONFIG_DIR/agents/routing-config.yaml"
    fi
    if [[ -f "$CONFIG_DIR/agents/model-registry.yaml" ]]; then
        echo "Models: $CONFIG_DIR/agents/model-registry.yaml"
    fi
    exit 0
fi

# --- Command: --wrk ---
if [[ -n "$WRK_ID" ]]; then
    # Find WRK item in work queue (working or pending directories)
    wrk_file=""
    for dir in "$WORK_QUEUE_DIR/working" "$WORK_QUEUE_DIR/pending" "$WORK_QUEUE_DIR/archive"; do
        candidate="$dir/${WRK_ID}.md"
        if [[ -f "$candidate" ]]; then
            wrk_file="$candidate"
            break
        fi
    done
    # Also check archive subdirectories
    if [[ -z "$wrk_file" ]]; then
        wrk_file=$(find "$WORK_QUEUE_DIR/archive" -name "${WRK_ID}.md" -type f 2>/dev/null | head -1)
    fi
    if [[ -z "$wrk_file" ]]; then
        echo "Error: Work item $WRK_ID not found in work queue" >&2
        exit 1
    fi
    # Extract title from YAML frontmatter or first heading
    TASK=$(grep -m1 '^title:' "$wrk_file" 2>/dev/null | sed 's/^title: *"*//; s/"*$//')
    if [[ -z "$TASK" ]]; then
        TASK=$(sed -n '/^# /{ s/^# //; p; q; }' "$wrk_file")
    fi
    if [[ -z "$TASK" ]]; then
        TASK="$WRK_ID"
    fi
    $QUIET || echo "Work item: $WRK_ID" >&2
    $QUIET || echo "Task: $TASK" >&2
fi

# --- Validate task ---
if [[ -z "$TASK" ]]; then
    echo "Error: No task description provided" >&2
    echo "Usage: $(basename "$0") [--execute] [--wrk WRK-NNN] \"<task description>\"" >&2
    exit 1
fi

# --- Pipeline ---
$QUIET || echo "--- Classifying task ---" >&2
classification_json=$(classify_task "$TASK")
tier=$(echo "$classification_json" | jq -r '.tier')
confidence=$(echo "$classification_json" | jq -r '.confidence')
classifier_provider=$(echo "$classification_json" | jq -r '.primary_provider')

$QUIET || echo "Tier: $tier | Confidence: $confidence | Classifier suggests: $classifier_provider" >&2

# Route by tier with availability check
routing_json=$(route_by_tier "$tier" "$classifier_provider" "$confidence")
selected_provider=$(echo "$routing_json" | jq -r '.provider')
auto_route=$(echo "$routing_json" | jq -r '.auto_route')
reason=$(echo "$routing_json" | jq -r '.reason')

$QUIET || echo "Routed to: $selected_provider ($reason)" >&2

# Select model for provider (adaptive EWMA-based)
selected_model=$(echo "$routing_json" | jq -r '.model // empty')
model_ewma=$(echo "$routing_json" | jq -r '.model_ewma // empty')

$QUIET || echo "Model: $selected_model (EWMA: ${model_ewma:-N/A})" >&2

# Select agent and get dispatch command (model-aware)
selected_agent=$(select_agent "$selected_provider" "$TASK")
dispatch_cmd=$(get_dispatch_command "$selected_provider" "$selected_agent" "$TASK" "$selected_model")

# Build final output
output=$(jq -n \
    --arg task "$TASK" \
    --argjson classification "$classification_json" \
    --argjson routing "$routing_json" \
    --arg agent "$selected_agent" \
    --arg model "$selected_model" \
    --arg dispatch_cmd "$dispatch_cmd" \
    --argjson auto_route "$auto_route" \
    '{
        task: $task,
        classification: $classification,
        routing: $routing,
        agent: $agent,
        model: $model,
        dispatch_command: $dispatch_cmd,
        auto_route: $auto_route
    }')

echo "$output"

# --- Audit log ---
AUDIT_LOG="$LOG_DIR/routing-decisions.jsonl"
jq -c -n \
    --arg timestamp "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
    --arg task "$TASK" \
    --argjson classification "$classification_json" \
    --argjson routing "$routing_json" \
    --arg agent "$selected_agent" \
    --arg model "$selected_model" \
    '{
        timestamp: $timestamp,
        task: $task,
        task_classification: $classification,
        recommendation: ($routing + {model: $model}),
        agent_assigned: $agent
    }' >> "$AUDIT_LOG"

# --- Execute if requested ---
if $EXECUTE; then
    $QUIET || echo "" >&2
    $QUIET || echo "--- Executing via $selected_provider ---" >&2
    eval "$dispatch_cmd"
fi
