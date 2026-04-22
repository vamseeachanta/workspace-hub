#!/usr/bin/env bash
set -euo pipefail

LOG_DIR=/mnt/local-analysis/workspace-hub/logs/nightly-2026-04-21
PROMPT_DIR=/mnt/local-analysis/worktrees/ws-nightly-2026-04-21/docs/plans/overnight-prompts/2026-04-21
mkdir -p "$LOG_DIR"

launch() {
  local workdir=$1
  local prompt_file=$2
  local log_file=$3
  cd "$workdir"
  local prompt
  prompt=$(< "$prompt_file")
  claude -p \
    --permission-mode acceptEdits \
    --no-session-persistence \
    --output-format text \
    --max-budget-usd 25 \
    "$prompt" </dev/null | tee "$log_file"
}

launch /mnt/local-analysis/worktrees/assethold-2442 "$PROMPT_DIR/terminal-1-assethold-2442.md" "$LOG_DIR/terminal-1-assethold-2442.log"
