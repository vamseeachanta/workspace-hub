#!/usr/bin/env bash
set -euo pipefail
ROOT=/mnt/local-analysis/workspace-hub
BASE="$ROOT/docs/plans/overnight-prompts/2026-04-28-12h-continuation"
ssh -o BatchMode=yes -o ConnectTimeout=8 ace-linux-2 "bash -lc 'set -euo pipefail; mkdir -p /mnt/local-analysis/ace2-worker-logs /mnt/local-analysis/ace2-worker-reports $BASE/results'"
launch_remote() {
  local session="$1" prompt="$2" log="$3"
  ssh -o BatchMode=yes -o ConnectTimeout=8 ace-linux-2 "bash -lc 'set -euo pipefail; ROOT=/mnt/local-analysis/workspace-hub; BASE="$BASE"; LOG=/mnt/local-analysis/ace2-worker-logs/$log; if tmux has-session -t $session 2>/dev/null; then echo SKIP remote exists $session; exit 0; fi; tmux new-session -d -s $session -c "\$ROOT" "bash -lc '''PROMPT=\\$(< \"$BASE/$prompt\"); /home/vamsee/.npm-global/bin/claude -p --permission-mode acceptEdits --no-session-persistence --output-format text --max-budget-usd 20 \"\\$PROMPT\" </dev/null 2>&1 | tee \"/mnt/local-analysis/ace2-worker-logs/$log\"'''"; echo STARTED remote $session'"
}
launch_remote ace2-digitalmodel-feed-20260428 ace2-digitalmodel-overflow.md ace2-digitalmodel-feed-20260428.log
launch_remote ace2-knowledge-feed-20260428 ace2-knowledge-docintel-overflow.md ace2-knowledge-feed-20260428.log
launch_remote ace2-review-feed-20260428 ace2-review-and-gsd.md ace2-review-feed-20260428.log
