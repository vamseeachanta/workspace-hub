#!/usr/bin/env bash
set -euo pipefail
ROOT=/mnt/local-analysis/workspace-hub
BASE="$ROOT/docs/plans/overnight-prompts/2026-04-28-12h-continuation"
ssh -o BatchMode=yes -o ConnectTimeout=8 ace-linux-2 "bash -lc 'set -euo pipefail; cd /mnt/local-analysis/workspace-hub; git fetch origin main >/dev/null 2>&1 || true; git checkout main >/dev/null 2>&1 || true; git pull --ff-only origin main >/dev/null 2>&1 || true; mkdir -p /mnt/local-analysis/ace2-worker-logs /mnt/local-analysis/ace2-worker-reports $BASE/results'"
launch_remote() {
  local session="$1" prompt="$2" log="$3"
  local remote_cmd
  remote_cmd=$(printf 'set -euo pipefail; ROOT=%q; BASE=%q; SESSION=%q; PROMPT_FILE=%q; LOG=%q; if tmux has-session -t "$SESSION" 2>/dev/null; then echo "SKIP remote exists $SESSION"; exit 0; fi; tmux new-session -d -s "$SESSION" -c "$ROOT" "bash -lc '\''PROMPT=\$(< \"$PROMPT_FILE\"); /home/vamsee/.npm-global/bin/claude -p --permission-mode acceptEdits --no-session-persistence --output-format text --max-budget-usd 20 \"\$PROMPT\" </dev/null 2>&1 | tee \"$LOG\"'\''"; echo "STARTED remote $SESSION"' "$ROOT" "$BASE" "$session" "$BASE/$prompt" "/mnt/local-analysis/ace2-worker-logs/$log")
  ssh -o BatchMode=yes -o ConnectTimeout=8 ace-linux-2 "bash -lc $remote_cmd"
}
launch_remote ace2-digitalmodel-feed-20260428 ace2-digitalmodel-overflow.md ace2-digitalmodel-feed-20260428.log
launch_remote ace2-knowledge-feed-20260428 ace2-knowledge-docintel-overflow.md ace2-knowledge-feed-20260428.log
launch_remote ace2-review-feed-20260428 ace2-review-and-gsd.md ace2-review-feed-20260428.log
