#!/usr/bin/env bash
set -euo pipefail
PROMPT_FILE="$1"
LOG_FILE="$2"
MODE="${3:-bypassPermissions}"
mkdir -p "$(dirname "$LOG_FILE")"
PROMPT="$(cat "$PROMPT_FILE")"
claude -p --permission-mode "$MODE" --no-session-persistence --output-format text --max-budget-usd 20 "$PROMPT" </dev/null 2>&1 | tee "$LOG_FILE"
