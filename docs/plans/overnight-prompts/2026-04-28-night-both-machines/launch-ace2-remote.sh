#!/usr/bin/env bash
# Copy prompts to ace-linux-2 and launch overnight lanes in remote tmux sessions.
set -euo pipefail
ROOT="${ROOT:-/mnt/local-analysis/workspace-hub}"
REMOTE="${REMOTE:-ace-linux-2}"
REMOTE_ROOT="${REMOTE_ROOT:-/mnt/local-analysis/workspace-hub}"
BATCH_DIR="$ROOT/docs/plans/overnight-prompts/2026-04-28-night-both-machines"
REMOTE_PROMPT_DIR="/tmp/night-20260428-prompts"
REMOTE_LOG_DIR="/mnt/local-analysis/ace2-worker-logs"
REMOTE_REPORT_DIR="/mnt/local-analysis/ace2-worker-reports"
DRY_RUN=false
if [[ "${1:-}" == "--dry-run" ]]; then DRY_RUN=true; fi

copy_prompt() {
  local file="$1"
  [[ -f "$BATCH_DIR/$file" ]] || { echo "missing prompt: $BATCH_DIR/$file" >&2; exit 1; }
  echo "scp $BATCH_DIR/$file $REMOTE:$REMOTE_PROMPT_DIR/$file"
  if [[ "$DRY_RUN" == false ]]; then
    ssh -o BatchMode=yes "$REMOTE" "bash -lc 'mkdir -p $REMOTE_PROMPT_DIR $REMOTE_LOG_DIR $REMOTE_REPORT_DIR /mnt/local-analysis/night-runs/ace2-digitalmodel /mnt/local-analysis/night-runs/ace2-knowledge'"
    scp "$BATCH_DIR/$file" "$REMOTE:$REMOTE_PROMPT_DIR/$file"
  fi
}

launch_remote_tmux() {
  local session="$1" prompt_file="$2" cmd_prefix="$3" log_file="$4"
  local remote_prompt="$REMOTE_PROMPT_DIR/$prompt_file"
  local remote_cmd
  remote_cmd="set -euo pipefail; cd '$REMOTE_ROOT'; mkdir -p '$REMOTE_LOG_DIR' '$REMOTE_REPORT_DIR'; if tmux has-session -t '$session' 2>/dev/null; then echo 'SKIP: session exists: $session'; exit 0; fi; tmux new-session -d -s '$session' -c '$REMOTE_ROOT' \"bash -lc 'PROMPT=\\\$(< $remote_prompt); $cmd_prefix \\\"\\\$PROMPT\\\" </dev/null 2>&1 | tee $log_file'\"; tmux list-sessions | grep '$session'"
  echo "REMOTE_SESSION=$session"
  echo "REMOTE_CMD=$remote_cmd"
  if [[ "$DRY_RUN" == false ]]; then
    ssh -o BatchMode=yes "$REMOTE" "bash -lc $(printf '%q' "$remote_cmd")"
  fi
}

copy_prompt "ace2-codex-digitalmodel-approved.md"
copy_prompt "ace2-knowledge-docintel-approved.md"
copy_prompt "ace2-claude-adversarial-review.md"

launch_remote_tmux \
  "ace2-claude-digitalmodel-20260428" \
  "ace2-codex-digitalmodel-approved.md" \
  "claude -p --permission-mode acceptEdits --no-session-persistence --output-format text" \
  "$REMOTE_LOG_DIR/ace2-claude-digitalmodel-20260428.log"

launch_remote_tmux \
  "ace2-knowledge-docintel-20260428" \
  "ace2-knowledge-docintel-approved.md" \
  "claude -p --permission-mode acceptEdits --no-session-persistence --output-format text" \
  "$REMOTE_LOG_DIR/ace2-knowledge-docintel-20260428.log"

launch_remote_tmux \
  "ace2-claude-review-20260428" \
  "ace2-claude-adversarial-review.md" \
  "claude -p --permission-mode plan --no-session-persistence --output-format text" \
  "$REMOTE_LOG_DIR/ace2-claude-review-20260428.log"
