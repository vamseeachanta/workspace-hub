#!/bin/bash
#
# Batch Task Executor
#
# Executes tasks in parallel using the Multi-Provider Orchestrator.
# Input: JSON array of task descriptions string from Stdin.
# Usage: ./batch_runner.sh --parallel 5 < tasks.json

set -e

# Defaults
PARALLEL=1
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
ORCHESTRATOR="$SCRIPT_DIR/../routing/orchestrate.sh"

# Parse Args
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --parallel) PARALLEL="$2"; shift ;; 
        *) echo "Unknown parameter passed: $1"; exit 1 ;; 
    esac
    shift
done

if [[ ! -f "$ORCHESTRATOR" ]]; then
    echo "Error: Orchestrator script not found at $ORCHESTRATOR"
    exit 1
fi

# Check for jq
if ! command -v jq &> /dev/null; then
    echo "Error: jq is not installed."
    exit 1
fi

echo "Starting batch execution with $PARALLEL parallel workers..."

# Read input, parse JSON array, and execute
# We use a subshell to capture stdin
# xargs -I {} replaces {} with the input line (task description)
# We wrap the task in quotes for safety
jq -r '.[]' | xargs -I {} -P "$PARALLEL" bash -c "$ORCHESTRATOR \"{}\" > /dev/null"

echo "Batch execution complete. Check logs for details."
