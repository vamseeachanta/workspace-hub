#!/usr/bin/env bash
set -euo pipefail
REMOTE="ace-linux-2"
ROOT="/mnt/local-analysis/workspace-hub"
BASE="$ROOT/docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed"
rsync -az "$BASE/" "$REMOTE:$BASE/"
ssh "$REMOTE" "bash -lc 'set -euo pipefail; ROOT=$ROOT; BASE=$BASE; LOGDIR=/mnt/local-analysis/ace2-worker-logs; mkdir -p "$BASE/results" "$BASE/generated" "$LOGDIR"; chmod +x "$BASE/run-claude-prompt.sh"; launch(){ local session="$1" prompt="$2" log="$3"; if tmux has-session -t "$session" 2>/dev/null; then echo SKIP existing "$session"; else tmux new-session -d -s "$session" "bash '"$BASE"'/run-claude-prompt.sh '"$BASE"'/$prompt '"$LOGDIR"'/$log acceptEdits"; echo STARTED "$session"; fi; }; launch nextwave-ace2-blocker-prep-20260429 ace2-blocker-prep.md nextwave-ace2-blocker-prep-20260429.log; launch nextwave-ace2-approved-scout-20260429 ace2-approved-scout.md nextwave-ace2-approved-scout-20260429.log; tmux list-sessions | grep nextwave || true'"
