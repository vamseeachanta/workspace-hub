#!/usr/bin/env bash
set -euo pipefail
REPO_ROOT="/mnt/local-analysis/workspace-hub"
PROMPT_DIR="$REPO_ROOT/docs/plans/claude-ops-2026-04-09"
LOG_DIR="$REPO_ROOT/logs/claude-ops-2026-04-09"
mkdir -p "$LOG_DIR"
cd "$REPO_ROOT"
launch_one() {
  local slug="$1"
  local prompt_file="$PROMPT_DIR/${slug}.md"
  local log_file="$LOG_DIR/${slug}.log"
  local pid_file="$LOG_DIR/${slug}.pid"
  local prompt
  prompt=$(< "$prompt_file")
  nohup claude -p --permission-mode acceptEdits --no-session-persistence --output-format text --max-budget-usd 5 "$prompt" </dev/null > "$log_file" 2>&1 &
  echo $! > "$pid_file"
  echo "Launched ${slug}"
}
launch_one terminal-1-plan-review-command-pack
launch_one terminal-2-refinement-application-pack
launch_one terminal-3-implementation-launch-pack
