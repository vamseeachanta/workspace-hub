#!/usr/bin/env bash
set -euo pipefail
ROOT=/mnt/local-analysis/workspace-hub
BASE="$ROOT/docs/plans/overnight-prompts/2026-04-29-credit-burn-approval-readiness"
LOGDIR="$ROOT/logs/night-runs"
mkdir -p "$LOGDIR"
launch() {
  local session="$1" prompt="$2" log="$3"
  if tmux has-session -t "$session" 2>/dev/null; then echo "exists $session"; return; fi
  tmux new-session -d -s "$session" "cd '$ROOT' && '$BASE/run-claude-prompt.sh' '$BASE/$prompt' '$LOGDIR/$log'"
  echo "launched $session -> $log"
}
launch ace1-approval-elements-20260429 ace1-approval-elements-2540-2544.md ace1-approval-elements-20260429.log
launch ace1-approval-additional5-20260429 ace1-approval-additional-5.md ace1-approval-additional5-20260429.log
launch ace1-readiness-review-20260429 ace1-codex-review-readiness.md ace1-readiness-review-20260429.log
