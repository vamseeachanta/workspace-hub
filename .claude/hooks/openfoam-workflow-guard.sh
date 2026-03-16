#!/usr/bin/env bash
# openfoam-workflow-guard.sh — PreToolUse hook for Bash tool
# Warns when agent runs OpenFOAM commands directly instead of via run-analysis.sh
#
# Enforcement: Level 3 (hook — fires automatically, can't be silently skipped)

INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // empty')
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

# Only check Bash tool calls
[[ "$TOOL_NAME" != "Bash" ]] && exit 0
[[ -z "$COMMAND" ]] && exit 0

# OpenFOAM solver commands that should go through run-analysis.sh
BARE_OF_COMMANDS="blockMesh|simpleFoam|pimpleFoam|interFoam|icoFoam|snappyHexMesh|decomposePar|reconstructPar|setFields|potentialFoam|checkMesh"

# Allow if called via run-analysis.sh or run-openfoam-tutorials.sh
if echo "$COMMAND" | grep -qE "run-analysis\.sh|run-openfoam-tutorials\.sh"; then
    exit 0
fi

# Allow if it's inside a script (bash scripts/..., bash .claude/...)
if echo "$COMMAND" | grep -qE "^bash\s+(scripts/|\.claude/)"; then
    exit 0
fi

# Allow if sourcing bashrc only (environment check, not running solver)
if echo "$COMMAND" | grep -qE "^(source|\.)\s+.*openfoam.*bashrc" && ! echo "$COMMAND" | grep -qE "$BARE_OF_COMMANDS"; then
    exit 0
fi

# Allow foamToVTK (post-processing, not solver execution)
if echo "$COMMAND" | grep -qE "^foamToVTK" && ! echo "$COMMAND" | grep -qE "simpleFoam|interFoam|pimpleFoam|icoFoam"; then
    exit 0
fi

# Detect bare OpenFOAM commands
if echo "$COMMAND" | grep -qE "(^|\s|&&|\|)($BARE_OF_COMMANDS)(\s|$|>|2>|;)"; then
    # Check if it's inside a bash -c with sourcing (likely from run-analysis.sh)
    if echo "$COMMAND" | grep -qE "bash -c.*source.*openfoam"; then
        exit 0
    fi
    
    echo "OPENFOAM_WORKFLOW_GUARD: Direct OpenFOAM command detected."
    echo "  Command: $(echo "$COMMAND" | head -c 120)"
    echo ""
    echo "  Use the openfoam-analysis workflow instead:"
    echo "    bash scripts/openfoam-analysis/run-analysis.sh <analysis.yaml>"
    echo ""
    echo "  This ensures: mesh quality gates, convergence monitoring,"
    echo "  calculation-methodology compliance, and report generation."
    echo ""
    echo "  Exceptions: run-openfoam-tutorials.sh (benchmarks),"
    echo "  scripts that call OpenFOAM internally."
    # Exit 0 — warn but don't block (agent can proceed if justified)
    exit 0
fi

exit 0
