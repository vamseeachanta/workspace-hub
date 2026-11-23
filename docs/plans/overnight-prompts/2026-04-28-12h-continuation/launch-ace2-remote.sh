#!/usr/bin/env bash
set -euo pipefail
ROOT=/mnt/local-analysis/workspace-hub
BASE="$ROOT/docs/plans/overnight-prompts/2026-04-28-12h-continuation"
RUNNER="$BASE/run-claude-prompt.sh"
ssh -o BatchMode=yes -o ConnectTimeout=8 ace-linux-2 "bash -lc 'set -euo pipefail; cd /mnt/local-analysis/workspace-hub; git fetch origin main >/dev/null 2>&1 || true; git checkout main >/dev/null 2>&1 || true; git pull --ff-only origin main >/dev/null 2>&1 || true; mkdir -p /mnt/local-analysis/ace2-worker-logs /mnt/local-analysis/ace2-worker-reports $BASE/results'"
launch_remote() {
  local session="$1" prompt="$2" log="$3"
  local prompt_file="$BASE/$prompt"
  local log_file="/mnt/local-analysis/ace2-worker-logs/$log"
  ssh -o BatchMode=yes -o ConnectTimeout=8 ace-linux-2 "bash -lc 'set -euo pipefail; SESSION=$session; if tmux has-session -t \"\$SESSION\" 2>/dev/null; then echo \"SKIP remote exists \$SESSION\"; exit 0; fi; tmux new-session -d -s \"\$SESSION\" -c /mnt/local-analysis/workspace-hub \"bash $RUNNER $prompt_file $log_file acceptEdits\"; echo \"STARTED remote \$SESSION\"'"
}
launch_remote ace2-digitalmodel-feed-20260428 ace2-digitalmodel-overflow.md ace2-digitalmodel-feed-20260428.log
launch_remote ace2-knowledge-feed-20260428 ace2-knowledge-docintel-overflow.md ace2-knowledge-feed-20260428.log
launch_remote ace2-review-feed-20260428 ace2-review-and-gsd.md ace2-review-feed-20260428.log
