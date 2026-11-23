#!/usr/bin/env bash
set -euo pipefail
ROOT=/mnt/local-analysis/workspace-hub
BASE="$ROOT/docs/plans/overnight-prompts/2026-04-29-credit-burn-approval-readiness"
LOGDIR=/mnt/local-analysis/ace2-worker-logs
mkdir -p "$LOGDIR"
launch() {
  local session="$1" prompt="$2" log="$3"
  if tmux has-session -t "$session" 2>/dev/null; then echo "exists $session"; return; fi
  tmux new-session -d -s "$session" "cd '$ROOT' && '$BASE/run-claude-prompt.sh' '$BASE/$prompt' '$LOGDIR/$log'"
  echo "launched $session -> $log"
}
launch ace2-plan-draft-next5-20260429 ace2-plan-draft-next5.md ace2-plan-draft-next5-20260429.log
launch ace2-execution-scout-20260429 ace2-execution-queue-scout.md ace2-execution-scout-20260429.log
