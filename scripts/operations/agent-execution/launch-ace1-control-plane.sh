#!/usr/bin/env bash
# Launch the ace-linux-1 control-plane Claude Code worker from repo-owned prompts.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_HUB="${WORKSPACE_HUB:-$(cd "${SCRIPT_DIR}/../../.." && pwd)}"
PROMPT="${WORKSPACE_HUB}/docs/plans/machine-prompts/2026-04-27/execution/ace-linux-1-execute-now.md"
LOG_DIR="${LOG_DIR:-/mnt/local-analysis/codex-burn-20260427}"
LOG="${LOG_DIR}/ace1-control-20260427.log"
SESSION="${SESSION:-ace1-control-20260427}"
DRY_RUN=false

usage() {
  cat <<USAGE
Usage: bash scripts/operations/agent-execution/launch-ace1-control-plane.sh [--tmux-session NAME] [--dry-run]

Launches Claude Code control-plane execution in ${WORKSPACE_HUB}.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --tmux-session) SESSION="$2"; shift 2 ;;
    --dry-run) DRY_RUN=true; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "ERROR: unknown arg: $1" >&2; usage >&2; exit 1 ;;
  esac
done

[[ -f "$PROMPT" ]] || { echo "ERROR: prompt missing: $PROMPT" >&2; exit 1; }
mkdir -p "$LOG_DIR"
cmd="cd $(printf '%q' "$WORKSPACE_HUB") && claude --print --dangerously-skip-permissions < $(printf '%q' "$PROMPT") 2>&1 | tee $(printf '%q' "$LOG")"

if [[ "$DRY_RUN" == true ]]; then
  printf 'session=%s\ncmd=%s\n' "$SESSION" "$cmd"
  exit 0
fi

if tmux has-session -t "$SESSION" 2>/dev/null; then
  echo "ERROR: tmux session already exists: $SESSION" >&2
  exit 1
fi

tmux new-session -d -s "$SESSION" -c "$WORKSPACE_HUB" "bash -lc $(printf '%q' "$cmd")"
echo "started session=$SESSION log=$LOG prompt=$PROMPT workdir=$WORKSPACE_HUB"
