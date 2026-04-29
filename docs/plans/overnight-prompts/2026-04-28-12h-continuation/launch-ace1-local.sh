#!/usr/bin/env bash
set -euo pipefail
ROOT=/mnt/local-analysis/workspace-hub
BASE="$ROOT/docs/plans/overnight-prompts/2026-04-28-12h-continuation"
LOGDIR="$ROOT/logs/night-runs"
mkdir -p "$BASE/results" "$LOGDIR"
launch_local() {
  local session="$1" prompt="$2" log="$3"
  if tmux has-session -t "$session" 2>/dev/null; then echo "SKIP local exists $session"; return; fi
  tmux new-session -d -s "$session" -c "$ROOT" "bash -lc 'PROMPT=\$(< "$BASE/$prompt"); claude -p --permission-mode acceptEdits --no-session-persistence --output-format text --max-budget-usd 20 "\$PROMPT" </dev/null 2>&1 | tee "$LOGDIR/$log"'"
  echo "STARTED local $session"
}
launch_local ace1-control-feed-20260428 ace1-control-reconciler.md ace1-control-feed-20260428.log
launch_local ace1-gtm-feed-20260428 ace1-gtm-packager.md ace1-gtm-feed-20260428.log
launch_local ace1-plan-hardener-20260428 ace1-plan-review-hardener.md ace1-plan-hardener-20260428.log
