#!/usr/bin/env bash
# capture-harness-version.sh — Capture Claude Code harness version and default model
#
# Usage:
#   scripts/session/capture-harness-version.sh [--state-dir DIR]
#
# Writes:
#   <state-dir>/harness-version.txt  — output of `claude --version` (or "unknown")
#   <state-dir>/default-model.txt    — model name from env or version output
#
# Called automatically by refresh-context.sh on every refresh cycle to ensure
# relaunched sessions use the most up-to-date Claude Code binary and model.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_HUB="${WORKSPACE_HUB:-$(cd "${SCRIPT_DIR}/../.." && pwd)}"
STATE_DIR="${WORKSPACE_HUB}/.claude/state"

# ─── Parse args ───────────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
    case "$1" in
        --state-dir)
            STATE_DIR="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
    esac
done

mkdir -p "$STATE_DIR"

# ─── Capture harness version ──────────────────────────────────────────────────
HARNESS_VERSION_FILE="${STATE_DIR}/harness-version.txt"

if command -v claude &>/dev/null; then
    HARNESS_VERSION="$(claude --version 2>/dev/null || echo "unknown")"
else
    HARNESS_VERSION="unknown"
fi

echo "$HARNESS_VERSION" > "$HARNESS_VERSION_FILE"
echo "Harness version: ${HARNESS_VERSION}"

# ─── Capture default model ────────────────────────────────────────────────────
DEFAULT_MODEL_FILE="${STATE_DIR}/default-model.txt"

# Precedence: ANTHROPIC_MODEL env var > CLAUDE_MODEL env var > parse from version
# output > fallback to "claude-opus-4-6" (current default as of 2026-02)
detect_default_model() {
    # 1. Explicit env overrides
    if [[ -n "${ANTHROPIC_MODEL:-}" ]]; then
        echo "$ANTHROPIC_MODEL"
        return
    fi
    if [[ -n "${CLAUDE_MODEL:-}" ]]; then
        echo "$CLAUDE_MODEL"
        return
    fi

    # 2. Try to parse model from `claude --version` output
    # Some builds embed the model string, e.g. "Claude Code 1.2.3 (model: claude-opus-4-6)"
    if [[ "$HARNESS_VERSION" != "unknown" ]]; then
        local parsed_model
        parsed_model="$(echo "$HARNESS_VERSION" \
            | grep -oE 'claude-[a-z0-9._-]+' \
            | head -1 || true)"
        if [[ -n "$parsed_model" ]]; then
            echo "$parsed_model"
            return
        fi
    fi

    # 3. Check existing default-model.txt to preserve a previously detected value
    if [[ -f "$DEFAULT_MODEL_FILE" ]]; then
        local existing
        existing="$(cat "$DEFAULT_MODEL_FILE" | tr -d '[:space:]')"
        if [[ -n "$existing" && "$existing" != "unknown" ]]; then
            echo "$existing"
            return
        fi
    fi

    # 4. Fallback to known current default
    echo "claude-opus-4-6"
}

DEFAULT_MODEL="$(detect_default_model)"
echo "$DEFAULT_MODEL" > "$DEFAULT_MODEL_FILE"
echo "Default model: ${DEFAULT_MODEL}"
