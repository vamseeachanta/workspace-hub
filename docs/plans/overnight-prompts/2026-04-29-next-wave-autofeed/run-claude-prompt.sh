#!/usr/bin/env bash
set -euo pipefail
PROMPT_FILE="$1"
LOG_FILE="$2"
MODE="${3:-acceptEdits}"
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
ROOT="/mnt/local-analysis/workspace-hub"
cd "$ROOT"
mkdir -p "$(dirname "$LOG_FILE")"
PROMPT="$(cat "$PROMPT_FILE")"
claude -p --permission-mode "$MODE" --no-session-persistence --output-format text --max-budget-usd 20 "$PROMPT" </dev/null 2>&1 | tee "$LOG_FILE"
