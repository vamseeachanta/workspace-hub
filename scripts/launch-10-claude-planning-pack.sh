#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="/mnt/local-analysis/workspace-hub"
PROMPT_DIR="$REPO_ROOT/docs/plans/overnight-prompts/2026-04-09-10claude"
LOG_DIR="$REPO_ROOT/logs/claude-2026-04-09-10pack"
mkdir -p "$LOG_DIR"
cd "$REPO_ROOT"

launch_one() {
  local terminal="$1"
  local slug="$2"
  local prompt_file="$PROMPT_DIR/terminal-${terminal}-${slug}.md"
  local log_file="$LOG_DIR/terminal-${terminal}-${slug}.log"
  local pid_file="$LOG_DIR/terminal-${terminal}-${slug}.pid"
  local prompt
  prompt=$(< "$prompt_file")
  echo "Launching T${terminal} ${slug}"
  nohup claude -p --permission-mode acceptEdits --no-session-persistence --output-format text --max-budget-usd 8 "$prompt" </dev/null > "$log_file" 2>&1 &
  echo $! > "$pid_file"
}

launch_one 1 drilling-riser-analysis
launch_one 2 drilling-rig-fleet-adapter
launch_one 3 timeline-benchmarks
launch_one 4 vessel-stability-cases
launch_one 5 architecture-patterns
launch_one 6 governance-phase3-infrastructure
launch_one 7 governance-phase2-runtime-hooks
launch_one 8 subsea-cost-benchmarking
launch_one 9 decline-curve-cashflows
launch_one 10 concept-selection-matrix

echo "Launched 10 Claude sessions. PID files:"
find "$LOG_DIR" -maxdepth 1 -name "*.pid" | sort
