#!/usr/bin/env bash
# stage5-plan-dispatch.sh — Stage 5 multi-agent planning dispatch (Route B/C)
# Dispatches Codex and Gemini in parallel using the same patterns as
# scripts/planning/ensemble-plan.sh (tested, failure-hardened).
#
# Usage: bash scripts/work-queue/stage5-plan-dispatch.sh WRK-NNN
#
# Prerequisites:
#   - specs/wrk/WRK-NNN/plan.md exists (Claude's interactive plan draft)
#
# Outputs:
#   .claude/work-queue/assets/WRK-NNN/plan_codex.md
#   .claude/work-queue/assets/WRK-NNN/plan_gemini.md
#
# After both land, trigger synthesis session interactively with Claude.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WS_HUB="$(cd "${SCRIPT_DIR}/../.." && pwd)"
PROMPTS_DIR="${WS_HUB}/scripts/planning/prompts"
ENSEMBLE_TIMEOUT="${ENSEMBLE_TIMEOUT:-300}"

# Portable timeout (mirrors ensemble-plan.sh)
if command -v timeout >/dev/null 2>&1; then
    _timeout() { timeout "$@"; }
elif command -v gtimeout >/dev/null 2>&1; then
    _timeout() { gtimeout "$@"; }
else
    echo "WARN: timeout command not found — calls will run without time limit" >&2
    _timeout() { shift; "$@"; }
fi

WRK_ID="${1:?Usage: stage5-plan-dispatch.sh WRK-NNN}"
ASSETS_DIR="${WS_HUB}/.claude/work-queue/assets/${WRK_ID}"
PLAN_DRAFT="${WS_HUB}/specs/wrk/${WRK_ID}/plan.md"

if [[ ! -f "$PLAN_DRAFT" ]]; then
    echo "ERROR: Claude draft not found: $PLAN_DRAFT" >&2
    echo "Claude must complete its own interactive planning session first." >&2
    exit 1
fi
mkdir -p "$ASSETS_DIR"

# Shared context = the Claude plan draft
SHARED_CONTEXT="$(cat "$PLAN_DRAFT")"

# --- Agent dispatch (same pattern as ensemble-plan.sh) -----------------------

_run_codex() {
    local stance="$1"
    local out="${ASSETS_DIR}/plan_codex.md"
    local prompt_file="${PROMPTS_DIR}/codex-${stance}.md"
    [[ -f "$prompt_file" ]] || { echo "ERROR: missing prompt ${prompt_file}" > "$out"; return 0; }
    command -v codex >/dev/null 2>&1 || { echo "NO_OUTPUT: codex CLI unavailable" > "$out"; return 0; }
    printf "%s\n\n---\nCLAUDE DRAFT PLAN:\n%s" "$(cat "$prompt_file")" "$SHARED_CONTEXT" \
        | _timeout "$ENSEMBLE_TIMEOUT" codex exec - \
        > "$out" 2>&1 \
        || echo "ERROR: codex ${stance} exited $?" >> "$out"
    echo "[codex] done → $out ($(wc -l < "$out") lines)"
}

_run_gemini() {
    local stance="$1"
    local out="${ASSETS_DIR}/plan_gemini.md"
    local prompt_file="${PROMPTS_DIR}/gemini-${stance}.md"
    [[ -f "$prompt_file" ]] || { echo "ERROR: missing prompt ${prompt_file}" > "$out"; return 0; }
    command -v gemini >/dev/null 2>&1 || { echo "NO_OUTPUT: gemini CLI unavailable" > "$out"; return 0; }
    echo "$SHARED_CONTEXT" \
        | _timeout "$ENSEMBLE_TIMEOUT" gemini -p "$(cat "$prompt_file")" -y \
        > "$out" 2>&1 \
        || echo "ERROR: gemini ${stance} exited $?" >> "$out"
    echo "[gemini] done → $out ($(wc -l < "$out") lines)"
}

# --- Parallel execution (mirrors ensemble-plan.sh) ---------------------------
echo "=== Stage 5 plan dispatch: ${WRK_ID} (timeout ${ENSEMBLE_TIMEOUT}s) ==="
echo "Draft: $PLAN_DRAFT"

_run_codex  plan-draft &
_run_gemini plan-draft &

wait
echo "--- All agents finished ---"

echo ""
echo "=== Dispatch complete ==="
echo "  plan_codex.md:  ${ASSETS_DIR}/plan_codex.md"
echo "  plan_gemini.md: ${ASSETS_DIR}/plan_gemini.md"
echo ""
echo "Next: send synthesis prompt to Claude for interactive conflict resolution with user."
