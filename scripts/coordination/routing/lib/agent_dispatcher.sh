#!/bin/bash
#
# Agent Dispatcher Engine
#

# This script handles the selection of the specific agent from the pool
# and the construction of the execution command for the chosen provider.

# --- Depends on jq ---
if ! command -v jq &> /dev/null; then
    echo "Error: jq is not installed." >&2
    exit 1
fi

# --- Configuration ---
CONFIG_DIR="${CONFIG_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)/config}"

# --- Function: select_agent ---
# Selects the best agent for the task based on provider and keywords.
select_agent() {
    local provider="$1"
    local task_description="$2"
    local task_lower=$(echo "$task_description" | tr '[:upper:]' '[:lower:]')
    
    # Simplified mapping for Phase 1
    # In a full implementation, this would query a larger agent registry
    local agent="default-agent"
    
    case "$provider" in
        "claude")
            if [[ "$task_lower" == *"architect"* ]] || [[ "$task_lower" == *"design"* ]]; then
                agent="claude-architect"
            elif [[ "$task_lower" == *"spec"* ]]; then
                agent="claude-spec-writer"
            else
                agent="claude-coder"
            fi
            ;;
        "gemini")
            if [[ "$task_lower" == *"analyze"* ]] || [[ "$task_lower" == *"research"* ]]; then
                agent="gemini-researcher"
            elif [[ "$task_lower" == *"plan"* ]]; then
                agent="gemini-planner"
            else
                agent="gemini-coder"
            fi
            ;;
        "codex")
            if [[ "$task_lower" == *"fix"* ]] || [[ "$task_lower" == *"bug"* ]]; then
                agent="codex-debugger"
            else
                agent="codex-generator"
            fi
            ;;
    esac
    
    echo "$agent"
}

# --- Function: get_dispatch_command ---
# Returns the command string to execute the task with the selected provider/agent.
# @param $1: provider
# @param $2: agent
# @param $3: task description
# @param $4: model key (optional, e.g., "claude/sonnet-4-5")
get_dispatch_command() {
    local provider="$1"
    local agent="$2"
    local task="$3"
    local model="${4:-}"
    local model_id="${model##*/}"

    local cmd=""

    case "$provider" in
        "claude")
            case "$model_id" in
                "sonnet-4-5")
                    cmd="claude --model sonnet -p \"$task\"" ;;
                *)
                    cmd="claude -p \"$task\"" ;;
            esac
            ;;
        "gemini")
            case "$model_id" in
                "gemini-flash")
                    cmd="echo \"$task\" | gemini --model gemini-2.5-flash -p \"Act as $agent\" -y" ;;
                *)
                    cmd="echo \"$task\" | gemini -p \"Act as $agent\" -y" ;;
            esac
            ;;
        "codex")
            cmd="echo \"$task\" | codex exec -"
            ;;
    esac

    echo "$cmd"
}
