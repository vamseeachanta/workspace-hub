#!/bin/bash
#
# Batch Task Executor
#
# Executes tasks in parallel using the Multi-Provider Orchestrator.
# Supports summary-only output format for hierarchical agent coordination.
#
# Input: JSON array of task descriptions string from Stdin.
# Usage: ./batch_runner.sh --parallel 5 --output-format summary < tasks.json

set -e

# Defaults
PARALLEL=1
OUTPUT_FORMAT="full"  # full or summary
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
WORKSPACE_ROOT="$SCRIPT_DIR/../.."
ORCHESTRATOR="$SCRIPT_DIR/../routing/orchestrate.sh"
RESULTS_DIR="$WORKSPACE_ROOT/.claude/state/agent_results"
WORKER_CONTRACT="$WORKSPACE_ROOT/.claude/tools/worker_contract.py"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BATCH_ID="batch_${TIMESTAMP}"

# Parse Args
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --parallel) PARALLEL="$2"; shift ;;
        --output-format) OUTPUT_FORMAT="$2"; shift ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS] < tasks.json"
            echo ""
            echo "Options:"
            echo "  --parallel N         Number of parallel workers (default: 1)"
            echo "  --output-format FMT  Output format: 'full' or 'summary' (default: full)"
            echo "  --help, -h           Show this help message"
            echo ""
            echo "When using --output-format summary:"
            echo "  - Results are saved to .claude/state/agent_results/"
            echo "  - Each worker returns a summary-only response"
            echo "  - Aggregated summary is printed at the end"
            exit 0
            ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

# Validate output format
if [[ "$OUTPUT_FORMAT" != "full" && "$OUTPUT_FORMAT" != "summary" ]]; then
    echo "Error: Invalid output format '$OUTPUT_FORMAT'. Use 'full' or 'summary'."
    exit 1
fi

if [[ ! -f "$ORCHESTRATOR" ]]; then
    echo "Error: Orchestrator script not found at $ORCHESTRATOR"
    exit 1
fi

# Check for jq
if ! command -v jq &> /dev/null; then
    echo "Error: jq is not installed."
    exit 1
fi

# Create results directory for summary mode
if [[ "$OUTPUT_FORMAT" == "summary" ]]; then
    mkdir -p "$RESULTS_DIR"
    echo "Batch ID: $BATCH_ID"
    echo "Results directory: $RESULTS_DIR"
fi

echo "Starting batch execution with $PARALLEL parallel workers..."
echo "Output format: $OUTPUT_FORMAT"

# Capture stdin before any processing (critical for process substitution)
INPUT_JSON=$(cat)

# Function to execute a single task and capture result
execute_task() {
    local task="$1"
    local worker_id="$2"
    local output_file="$RESULTS_DIR/${BATCH_ID}_worker_${worker_id}.json"
    local start_time=$(date +%s.%N)

    if [[ "$OUTPUT_FORMAT" == "summary" ]]; then
        # Capture output and create worker response
        local result
        local exit_code=0
        result=$("$ORCHESTRATOR" "$task" 2>&1) || exit_code=$?
        local end_time=$(date +%s.%N)
        local duration=$(echo "$end_time - $start_time" | bc 2>/dev/null || echo "0")

        # Generate summary response (max 300 chars)
        local summary
        if [[ $exit_code -eq 0 ]]; then
            summary="Task completed: ${task:0:100}..."
            local status="complete"
        else
            summary="Task failed: ${result:0:100}..."
            local status="failed"
        fi

        # Create worker response JSON
        cat > "$output_file" << EOF
{
  "worker_id": "worker-${worker_id}",
  "status": "${status}",
  "summary": "${summary:0:297}",
  "output_file": "${output_file}",
  "next_action": "Review results in ${output_file}",
  "key_metrics": {
    "exit_code": ${exit_code},
    "duration_seconds": ${duration%.*:-0}
  },
  "timestamp": "$(date -Iseconds)",
  "batch_id": "${BATCH_ID}"
}
EOF
        echo "Worker ${worker_id}: ${status}"
    else
        # Full output mode - original behavior
        "$ORCHESTRATOR" "$task"
    fi
}

export -f execute_task
export ORCHESTRATOR RESULTS_DIR BATCH_ID OUTPUT_FORMAT

# Read input and execute tasks
if [[ "$OUTPUT_FORMAT" == "summary" ]]; then
    # Summary mode: capture results with worker IDs
    WORKER_COUNT=0
    while IFS= read -r task; do
        ((WORKER_COUNT++)) || true
        execute_task "$task" "$WORKER_COUNT" &

        # Respect parallel limit
        if (( WORKER_COUNT % PARALLEL == 0 )); then
            wait
        fi
    done < <(echo "$INPUT_JSON" | jq -r '.[]')
    wait

    # Aggregate results
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo "  Batch Execution Summary"
    echo "═══════════════════════════════════════════════════════════════"
    echo ""

    complete_count=0
    failed_count=0
    blocked_count=0

    for result_file in "$RESULTS_DIR/${BATCH_ID}"_worker_*.json; do
        if [[ -f "$result_file" ]]; then
            status=$(jq -r '.status' "$result_file" 2>/dev/null || echo "unknown")
            case "$status" in
                complete) ((complete_count++)) || true ;;
                failed) ((failed_count++)) || true ;;
                blocked) ((blocked_count++)) || true ;;
            esac
        fi
    done

    echo "  Total workers: $WORKER_COUNT"
    echo "  ✓ Complete: $complete_count"
    echo "  ✗ Failed: $failed_count"
    echo "  ⚠ Blocked: $blocked_count"
    echo ""
    echo "  Results saved to: $RESULTS_DIR/"
    echo "  Batch ID: $BATCH_ID"
    echo ""

    # Validate with worker contract if available
    if [[ -f "$WORKER_CONTRACT" ]] && command -v python3 &> /dev/null; then
        echo "Aggregating results with worker contract validator..."
        python3 "$WORKER_CONTRACT" aggregate 2>/dev/null || true
    fi

    echo "═══════════════════════════════════════════════════════════════"
else
    # Full output mode - original behavior
    echo "$INPUT_JSON" | jq -r '.[]' | xargs -I {} -P "$PARALLEL" bash -c "$ORCHESTRATOR \"{}\" > /dev/null"
fi

echo "Batch execution complete."
