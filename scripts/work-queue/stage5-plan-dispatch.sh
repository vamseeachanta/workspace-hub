#!/usr/bin/env bash
# stage5-plan-dispatch.sh — Stage 5 multi-agent interactive planning dispatch
# Dispatches Codex and Gemini in parallel to produce independent plan drafts.
# Claude's plan_claude.md must already exist (produced by Claude's own Stage 5 session).
#
# Usage: bash scripts/work-queue/stage5-plan-dispatch.sh WRK-NNN
#
# Outputs:
#   .claude/work-queue/assets/WRK-NNN/plan_codex.md
#   .claude/work-queue/assets/WRK-NNN/plan_gemini.md
#
# After both land, run synthesis interactively with Claude.
set -euo pipefail

WS_HUB="$(git rev-parse --show-toplevel)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROVIDERS_DIR="${WS_HUB}/scripts/agents/providers"

WRK_ID="${1:?Usage: stage5-plan-dispatch.sh WRK-NNN}"
ASSETS_DIR="${WS_HUB}/.claude/work-queue/assets/${WRK_ID}"
PLAN_DRAFT="${WS_HUB}/specs/wrk/${WRK_ID}/plan.md"

# Validate inputs
if [[ ! -f "$PLAN_DRAFT" ]]; then
    echo "ERROR: Claude draft not found: $PLAN_DRAFT" >&2
    echo "Claude must complete its own interactive planning session first." >&2
    exit 1
fi
mkdir -p "$ASSETS_DIR"

CODEX_OUT="${ASSETS_DIR}/plan_codex.md"
GEMINI_OUT="${ASSETS_DIR}/plan_gemini.md"
CODEX_LOG=$(mktemp /tmp/stage5-codex.XXXXXX)
GEMINI_LOG=$(mktemp /tmp/stage5-gemini.XXXXXX)
cleanup() { rm -f "$CODEX_LOG" "$GEMINI_LOG"; }
trap cleanup EXIT

PLAN_CONTENT="$(cat "$PLAN_DRAFT")"

build_prompt() {
    local agent="$1"
    local out_path="$2"
    cat <<PROMPT
Stage 5 interactive planning — ${WRK_ID} (Route B)

Read the Claude draft below. Walk it section-by-section. Challenge assumptions,
surface edge cases, identify gaps. Produce your own refined plan version.
Save your output to: ${out_path}

The file must be saved — do not just print it.

${PLAN_CONTENT}

Add a "${agent} Notes" section at the end with specific findings/recommendations.
Include any concerns about: implementation approach, edge cases, AC gaps, risks,
test coverage, or integration complexity.
PROMPT
}

# --- Dispatch Codex ---
dispatch_codex() {
    echo "[codex] starting..."
    local prompt
    prompt="$(build_prompt "Codex" "$CODEX_OUT")"
    if ! command -v codex >/dev/null 2>&1; then
        echo "WARN: codex CLI not found — skipping Codex dispatch" >&2
        echo "# Codex not available on this machine" > "$CODEX_OUT"
        return 0
    fi
    echo "$prompt" | timeout 300 codex --full-auto -q - > "$CODEX_LOG" 2>&1 || true
    if [[ -f "$CODEX_OUT" ]]; then
        echo "[codex] plan_codex.md written ($(wc -l < "$CODEX_OUT") lines)"
    else
        echo "WARN: codex did not write $CODEX_OUT — saving log output" >&2
        cp "$CODEX_LOG" "$CODEX_OUT"
    fi
}

# --- Dispatch Gemini ---
dispatch_gemini() {
    echo "[gemini] starting..."
    local prompt
    prompt="$(build_prompt "Gemini" "$GEMINI_OUT")"
    if ! command -v gemini >/dev/null 2>&1; then
        echo "WARN: gemini CLI not found — skipping Gemini dispatch" >&2
        echo "# Gemini not available on this machine" > "$GEMINI_OUT"
        return 0
    fi
    echo "$prompt" | timeout 300 gemini -p "$(cat)" -y > "$GEMINI_LOG" 2>&1 || true
    if [[ -f "$GEMINI_OUT" ]]; then
        echo "[gemini] plan_gemini.md written ($(wc -l < "$GEMINI_OUT") lines)"
    else
        # Gemini printed to stdout — capture log as output
        echo "WARN: gemini did not write $GEMINI_OUT — saving log output" >&2
        cp "$GEMINI_LOG" "$GEMINI_OUT"
    fi
}

echo "=== Stage 5 plan dispatch: ${WRK_ID} ==="
echo "Draft: $PLAN_DRAFT"
echo "Dispatching Codex and Gemini in parallel..."

dispatch_codex &
CODEX_PID=$!
dispatch_gemini &
GEMINI_PID=$!

wait "$CODEX_PID" && echo "[codex] done" || echo "[codex] WARN: non-zero exit"
wait "$GEMINI_PID" && echo "[gemini] done" || echo "[gemini] WARN: non-zero exit"

echo ""
echo "=== Dispatch complete ==="
echo "  plan_codex.md:  $CODEX_OUT"
echo "  plan_gemini.md: $GEMINI_OUT"
echo ""
echo "Next: send synthesis prompt to Claude for interactive conflict resolution with user."
