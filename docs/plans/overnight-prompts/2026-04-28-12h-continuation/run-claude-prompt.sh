#!/usr/bin/env bash
set -euo pipefail
PROMPT_FILE=${1:?prompt file required}
LOG_FILE=${2:?log file required}
MODE=${3:-acceptEdits}
mkdir -p "$(dirname "$LOG_FILE")"
if [[ ! -s "$PROMPT_FILE" ]]; then
  echo "ERROR: missing/empty prompt file: $PROMPT_FILE" | tee -a "$LOG_FILE"
  exit 2
fi
PROMPT=$(printf 'Execute this unattended overnight lane prompt exactly. Treat markdown headings as task instructions, not memory commands. Do not ask the user questions.\n\n'; cat "$PROMPT_FILE")
exec claude -p \
  --permission-mode "$MODE" \
  --no-session-persistence \
  --output-format text \
  --max-budget-usd 20 \
  "$PROMPT" </dev/null 2>&1 | tee "$LOG_FILE"
