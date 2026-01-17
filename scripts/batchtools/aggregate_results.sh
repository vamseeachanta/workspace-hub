#!/bin/bash
#
# ABOUTME: Aggregator agent pattern for merging worker results
# ABOUTME: Consolidates summary-only worker responses for coordinator agents
#
# Usage: ./aggregate_results.sh [OPTIONS] [BATCH_ID]
#
# Options:
#   --batch-id ID     Aggregate results for specific batch ID
#   --latest          Aggregate results from latest batch (default)
#   --all             Aggregate all pending results
#   --format FORMAT   Output format: summary (default), json, markdown
#   --cleanup         Remove individual result files after aggregation
#   --output FILE     Write aggregated results to file (default: stdout)
#   --help, -h        Show this help message

set -e

# Defaults
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
WORKSPACE_ROOT="$SCRIPT_DIR/../.."
RESULTS_DIR="$WORKSPACE_ROOT/.claude/state/agent_results"
WORKER_CONTRACT="$WORKSPACE_ROOT/.claude/tools/worker_contract.py"
FORMAT="summary"
CLEANUP=false
OUTPUT_FILE=""
BATCH_ID=""
MODE="latest"

# Parse Args
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --batch-id) BATCH_ID="$2"; MODE="specific"; shift ;;
        --latest) MODE="latest" ;;
        --all) MODE="all" ;;
        --format) FORMAT="$2"; shift ;;
        --cleanup) CLEANUP=true ;;
        --output) OUTPUT_FILE="$2"; shift ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS] [BATCH_ID]"
            echo ""
            echo "Aggregator agent pattern for merging worker results."
            echo "Consolidates summary-only responses from parallel workers."
            echo ""
            echo "Options:"
            echo "  --batch-id ID     Aggregate results for specific batch ID"
            echo "  --latest          Aggregate results from latest batch (default)"
            echo "  --all             Aggregate all pending results"
            echo "  --format FORMAT   Output format: summary, json, markdown (default: summary)"
            echo "  --cleanup         Remove individual result files after aggregation"
            echo "  --output FILE     Write aggregated results to file (default: stdout)"
            echo "  --help, -h        Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0 --latest                    # Aggregate latest batch"
            echo "  $0 --batch-id batch_20260114   # Aggregate specific batch"
            echo "  $0 --all --format json         # Aggregate all as JSON"
            echo "  $0 --latest --cleanup          # Aggregate and cleanup files"
            exit 0
            ;;
        *)
            # Positional argument = batch ID
            if [[ -z "$BATCH_ID" ]]; then
                BATCH_ID="$1"
                MODE="specific"
            else
                echo "Unknown parameter: $1"
                exit 1
            fi
            ;;
    esac
    shift
done

# Validate format
if [[ "$FORMAT" != "summary" && "$FORMAT" != "json" && "$FORMAT" != "markdown" ]]; then
    echo "Error: Invalid format '$FORMAT'. Use: summary, json, or markdown"
    exit 1
fi

# Check results directory
if [[ ! -d "$RESULTS_DIR" ]]; then
    echo "No results directory found at $RESULTS_DIR"
    exit 0
fi

# Check for jq
if ! command -v jq &> /dev/null; then
    echo "Error: jq is required but not installed."
    exit 1
fi

# Find batch ID based on mode
find_batch_id() {
    case "$MODE" in
        latest)
            # Find most recent batch by file modification time
            local latest_file
            latest_file=$(ls -t "$RESULTS_DIR"/batch_*_worker_*.json 2>/dev/null | head -1)
            if [[ -n "$latest_file" ]]; then
                # Extract batch ID from filename (batch_YYYYMMDD_HHMMSS)
                basename "$latest_file" | sed 's/_worker_.*\.json$//'
            fi
            ;;
        specific)
            echo "$BATCH_ID"
            ;;
        all)
            # Return empty - will process all files
            echo ""
            ;;
    esac
}

# Get result files for aggregation
get_result_files() {
    local batch="$1"
    if [[ -n "$batch" ]]; then
        find "$RESULTS_DIR" -name "${batch}_worker_*.json" -type f 2>/dev/null | sort
    else
        find "$RESULTS_DIR" -name "*.json" -type f 2>/dev/null | sort
    fi
}

# Aggregate results using Python worker_contract.py if available
aggregate_with_python() {
    if [[ -f "$WORKER_CONTRACT" ]] && command -v python3 &> /dev/null; then
        python3 "$WORKER_CONTRACT" aggregate 2>/dev/null
        return $?
    fi
    return 1
}

# Manual aggregation using jq
aggregate_with_jq() {
    local files=("$@")
    local total=${#files[@]}
    local complete=0
    local failed=0
    local blocked=0
    local combined_metrics="{}"
    local next_actions="[]"

    for file in "${files[@]}"; do
        if [[ -f "$file" ]]; then
            local status
            status=$(jq -r '.status // "unknown"' "$file" 2>/dev/null)

            case "$status" in
                complete) ((complete++)) || true ;;
                failed) ((failed++)) || true ;;
                blocked) ((blocked++)) || true ;;
            esac

            # Collect metrics
            local metrics
            metrics=$(jq -c '.key_metrics // {}' "$file" 2>/dev/null)
            if [[ "$metrics" != "{}" && "$metrics" != "null" ]]; then
                combined_metrics=$(echo "$combined_metrics" "$metrics" | jq -s 'add')
            fi

            # Collect next actions for non-complete tasks
            if [[ "$status" != "complete" ]]; then
                local action
                action=$(jq -r '.next_action // empty' "$file" 2>/dev/null)
                if [[ -n "$action" ]]; then
                    next_actions=$(echo "$next_actions" | jq --arg a "$action" '. + [$a]')
                fi
            fi
        fi
    done

    # Limit next actions to 5
    next_actions=$(echo "$next_actions" | jq '.[0:5]')

    # Build aggregated result
    local all_complete="false"
    if [[ $total -gt 0 && $complete -eq $total ]]; then
        all_complete="true"
    fi

    jq -n \
        --argjson total "$total" \
        --argjson complete "$complete" \
        --argjson failed "$failed" \
        --argjson blocked "$blocked" \
        --argjson metrics "$combined_metrics" \
        --argjson actions "$next_actions" \
        --argjson all_complete "$all_complete" \
        '{
            total_workers: $total,
            status_summary: {
                complete: $complete,
                failed: $failed,
                blocked: $blocked
            },
            combined_metrics: $metrics,
            next_actions: $actions,
            all_complete: $all_complete
        }'
}

# Format output as summary
format_summary() {
    local json="$1"
    local batch="$2"

    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo "  Aggregated Worker Results"
    if [[ -n "$batch" ]]; then
        echo "  Batch: $batch"
    fi
    echo "═══════════════════════════════════════════════════════════════"
    echo ""

    local total complete failed blocked
    total=$(echo "$json" | jq -r '.total_workers')
    complete=$(echo "$json" | jq -r '.status_summary.complete // 0')
    failed=$(echo "$json" | jq -r '.status_summary.failed // 0')
    blocked=$(echo "$json" | jq -r '.status_summary.blocked // 0')

    echo "  Total workers: $total"
    echo "  ✓ Complete: $complete"
    echo "  ✗ Failed: $failed"
    echo "  ⚠ Blocked: $blocked"
    echo ""

    # Show metrics if any
    local metrics
    metrics=$(echo "$json" | jq -r '.combined_metrics // {}')
    if [[ "$metrics" != "{}" && "$metrics" != "null" ]]; then
        echo "  Key Metrics:"
        echo "$metrics" | jq -r 'to_entries[] | "    \(.key): \(.value)"' 2>/dev/null || true
        echo ""
    fi

    # Show next actions if any
    local actions
    actions=$(echo "$json" | jq -r '.next_actions // []')
    if [[ "$actions" != "[]" && "$actions" != "null" ]]; then
        echo "  Next Actions:"
        echo "$actions" | jq -r '.[] | "    • \(.)"' 2>/dev/null || true
        echo ""
    fi

    # Overall status
    local all_complete
    all_complete=$(echo "$json" | jq -r '.all_complete')
    if [[ "$all_complete" == "true" ]]; then
        echo "  Status: ✅ ALL WORKERS COMPLETE"
    elif [[ $failed -gt 0 ]]; then
        echo "  Status: ❌ SOME WORKERS FAILED"
    elif [[ $blocked -gt 0 ]]; then
        echo "  Status: ⚠️  SOME WORKERS BLOCKED"
    else
        echo "  Status: 🔄 IN PROGRESS"
    fi

    echo ""
    echo "═══════════════════════════════════════════════════════════════"
}

# Format output as markdown
format_markdown() {
    local json="$1"
    local batch="$2"

    echo "## Aggregated Worker Results"
    if [[ -n "$batch" ]]; then
        echo ""
        echo "**Batch:** \`$batch\`"
    fi
    echo ""

    local total complete failed blocked
    total=$(echo "$json" | jq -r '.total_workers')
    complete=$(echo "$json" | jq -r '.status_summary.complete // 0')
    failed=$(echo "$json" | jq -r '.status_summary.failed // 0')
    blocked=$(echo "$json" | jq -r '.status_summary.blocked // 0')

    echo "### Summary"
    echo ""
    echo "| Status | Count |"
    echo "|--------|-------|"
    echo "| Total | $total |"
    echo "| ✓ Complete | $complete |"
    echo "| ✗ Failed | $failed |"
    echo "| ⚠ Blocked | $blocked |"
    echo ""

    # Show metrics if any
    local metrics
    metrics=$(echo "$json" | jq -r '.combined_metrics // {}')
    if [[ "$metrics" != "{}" && "$metrics" != "null" ]]; then
        echo "### Key Metrics"
        echo ""
        echo "$metrics" | jq -r 'to_entries[] | "- **\(.key):** \(.value)"' 2>/dev/null || true
        echo ""
    fi

    # Show next actions if any
    local actions
    actions=$(echo "$json" | jq -r '.next_actions // []')
    if [[ "$actions" != "[]" && "$actions" != "null" ]]; then
        echo "### Next Actions"
        echo ""
        echo "$actions" | jq -r '.[] | "- [ ] \(.)"' 2>/dev/null || true
        echo ""
    fi

    # Overall status
    local all_complete
    all_complete=$(echo "$json" | jq -r '.all_complete')
    echo "### Overall Status"
    echo ""
    if [[ "$all_complete" == "true" ]]; then
        echo "✅ **ALL WORKERS COMPLETE**"
    elif [[ $failed -gt 0 ]]; then
        echo "❌ **SOME WORKERS FAILED** - Review failed workers and retry"
    elif [[ $blocked -gt 0 ]]; then
        echo "⚠️ **SOME WORKERS BLOCKED** - Address blocking issues"
    else
        echo "🔄 **IN PROGRESS**"
    fi
}

# Main execution
main() {
    # Determine batch ID
    local batch
    batch=$(find_batch_id)

    if [[ "$MODE" == "specific" && -z "$batch" ]]; then
        echo "Error: No batch ID specified"
        exit 1
    fi

    # Get result files
    local files
    mapfile -t files < <(get_result_files "$batch")

    if [[ ${#files[@]} -eq 0 ]]; then
        echo "No result files found"
        if [[ -n "$batch" ]]; then
            echo "Batch ID: $batch"
        fi
        exit 0
    fi

    # Aggregate results
    local aggregated
    aggregated=$(aggregate_with_jq "${files[@]}")

    # Format output
    local output
    case "$FORMAT" in
        json)
            output="$aggregated"
            ;;
        markdown)
            output=$(format_markdown "$aggregated" "$batch")
            ;;
        summary|*)
            output=$(format_summary "$aggregated" "$batch")
            ;;
    esac

    # Write or print output
    if [[ -n "$OUTPUT_FILE" ]]; then
        echo "$output" > "$OUTPUT_FILE"
        echo "Aggregated results written to: $OUTPUT_FILE"
    else
        echo "$output"
    fi

    # Cleanup if requested
    if [[ "$CLEANUP" == true ]]; then
        echo ""
        echo "Cleaning up ${#files[@]} result files..."
        for file in "${files[@]}"; do
            rm -f "$file"
        done
        echo "Cleanup complete."
    fi

    # Return status based on results
    local all_complete
    all_complete=$(echo "$aggregated" | jq -r '.all_complete')
    if [[ "$all_complete" == "true" ]]; then
        exit 0
    else
        local failed
        failed=$(echo "$aggregated" | jq -r '.status_summary.failed // 0')
        if [[ $failed -gt 0 ]]; then
            exit 2  # Some workers failed
        fi
        exit 1  # Some workers blocked or incomplete
    fi
}

main
