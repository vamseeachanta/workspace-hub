#!/usr/bin/env bash
set -euo pipefail
ROOT="/mnt/local-analysis/workspace-hub"
BASE="$ROOT/docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed"
LOGDIR="$ROOT/logs/night-runs"
mkdir -p "$LOGDIR" "$BASE/results" "$BASE/generated"
launch() {
  local session="$1" prompt="$2" log="$3" mode="${4:-acceptEdits}"
  if tmux has-session -t "$session" 2>/dev/null; then
    echo "SKIP existing $session"
  else
    tmux new-session -d -s "$session" "bash '$BASE/run-claude-prompt.sh' '$BASE/$prompt' '$LOGDIR/$log' '$mode'"
    echo "STARTED $session -> $LOGDIR/$log"
  fi
}
launch nextwave-gtm-review-a-20260429 gtm-review-2554-2555.md nextwave-gtm-review-a-20260429.log acceptEdits
launch nextwave-gtm-review-b-20260429 gtm-review-2556-2557.md nextwave-gtm-review-b-20260429.log acceptEdits
launch nextwave-approval-synthesis-20260429 approval-synthesis-10.md nextwave-approval-synthesis-20260429.log acceptEdits
launch nextwave-autofeed-fix-20260429 autofeed-fix-and-queue.md nextwave-autofeed-fix-20260429.log acceptEdits
