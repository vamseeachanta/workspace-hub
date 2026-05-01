#!/usr/bin/env bash
set -euo pipefail
ROOT=/mnt/local-analysis/workspace-hub
BASE="$ROOT/docs/plans/overnight-prompts/2026-04-29-weekly-gtm-targets"
LOGDIR="$ROOT/logs/night-runs"
mkdir -p "$LOGDIR" "$BASE/results"
launch_lane() {
  local session="$1" prompt="$2" log="$3"
  if tmux has-session -t "$session" 2>/dev/null; then
    echo "skip existing $session"
  else
    tmux new-session -d -s "$session" "cd '$ROOT' && bash '$BASE/run-claude-prompt.sh' '$BASE/$prompt' '$LOGDIR/$log' bypassPermissions"
    echo "started $session -> $LOGDIR/$log"
  fi
}
launch_lane weekly-gtm-2554-20260429 2554-contractor-matrix.md weekly-gtm-2554-20260429.log
launch_lane weekly-gtm-2555-20260429 2555-capability-charts.md weekly-gtm-2555-20260429.log
launch_lane weekly-gtm-2556-20260429 2556-brochure-send.md weekly-gtm-2556-20260429.log
launch_lane weekly-productivity-2557-20260429 2557-productivity-review.md weekly-productivity-2557-20260429.log
