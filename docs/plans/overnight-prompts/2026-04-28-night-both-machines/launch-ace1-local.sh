#!/usr/bin/env bash
# Launch ace-linux-1 overnight lanes in local tmux sessions.
set -euo pipefail
ROOT="${ROOT:-/mnt/local-analysis/workspace-hub}"
BATCH_DIR="$ROOT/docs/plans/overnight-prompts/2026-04-28-night-both-machines"
LOG_DIR="$ROOT/logs/night-runs"
DRY_RUN=false
if [[ "${1:-}" == "--dry-run" ]]; then DRY_RUN=true; fi
mkdir -p "$LOG_DIR" "$BATCH_DIR/results"

launch_tmux() {
  local session="$1" prompt_file="$2" cmd_prefix="$3" log_file="$4"
  [[ -f "$prompt_file" ]] || { echo "missing prompt: $prompt_file" >&2; exit 1; }
  if tmux has-session -t "$session" 2>/dev/null; then
    echo "SKIP: session already exists: $session"
    return 0
  fi
  local cmd="cd '$ROOT' && PROMPT=\$(< '$prompt_file') && $cmd_prefix \"\$PROMPT\" 2>&1 | tee '$log_file'"
  echo "SESSION=$session"
  echo "CMD=$cmd"
  if [[ "$DRY_RUN" == false ]]; then
    tmux new-session -d -s "$session" -c "$ROOT" "bash -lc $(printf '%q' "$cmd")"
  fi
}

launch_tmux \
  "ace1-codex-approved-20260428" \
  "$BATCH_DIR/ace1-codex-approved-recovery.md" \
  "codex exec" \
  "$LOG_DIR/ace1-codex-approved-recovery-20260428.log"

launch_tmux \
  "ace1-gemini-recon-20260428" \
  "$BATCH_DIR/ace1-gemini-recon-batch.md" \
  "hermes chat --provider openrouter --model google/gemini-2.5-pro --quiet -q" \
  "$LOG_DIR/ace1-gemini-recon-batch-20260428.log"

launch_tmux \
  "ace1-claude-control-20260428" \
  "$BATCH_DIR/ace1-claude-control-plane-synthesis.md" \
  "claude -p --permission-mode plan --no-session-persistence --output-format text" \
  "$LOG_DIR/ace1-claude-control-plane-synthesis-20260428.log"

if [[ "$DRY_RUN" == false ]]; then
  tmux list-sessions | grep -E 'ace1-(codex-approved|gemini-recon|claude-control)-20260428' || true
fi
