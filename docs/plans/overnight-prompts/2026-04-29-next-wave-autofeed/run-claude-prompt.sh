#!/usr/bin/env bash
set -euo pipefail
PROMPT_FILE="${1:?prompt file required}"
LOG_FILE="${2:?log file required}"
MODE="${3:-acceptEdits}"
ROOT="/mnt/local-analysis/workspace-hub"
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/bin:/bin:$PATH"
CLAUDE_BIN="${CLAUDE_BIN:-$HOME/.npm-global/bin/claude}"
cd "$ROOT"
mkdir -p "$(dirname "$LOG_FILE")"
PROMPT="$(<"$PROMPT_FILE")"
"$CLAUDE_BIN" --version >/dev/null
"$CLAUDE_BIN" --help | grep -q -- '--max-budget-usd'
cmd=(
  "$CLAUDE_BIN"
  -p
  --permission-mode "$MODE"
  --no-session-persistence
  --output-format text
  --max-budget-usd "20"
  "$PROMPT"
)
"${cmd[@]}" </dev/null 2>&1 | tee -- "$LOG_FILE"
