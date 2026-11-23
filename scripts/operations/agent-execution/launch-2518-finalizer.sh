#!/usr/bin/env bash
# Launch the #2518 finalizer Claude Code worker from the repo-owned prompt.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_HUB="${WORKSPACE_HUB:-$(cd "${SCRIPT_DIR}/../../.." && pwd)}"
RECONCILE_DIR="${RECONCILE_DIR:-/mnt/local-analysis/reconcile-main-20260427}"
PROMPT="${WORKSPACE_HUB}/docs/plans/machine-prompts/2026-04-27/execution/finish-land-2518-finalizer.md"
LOG_DIR="${LOG_DIR:-/mnt/local-analysis/codex-burn-20260427}"
LOG="${LOG_DIR}/finish-land-2518-finalizer.log"
SESSION="${SESSION:-finish-land-2518-finalizer}"

usage() {
  cat <<USAGE
Usage: bash scripts/operations/agent-execution/launch-2518-finalizer.sh [--tmux-session NAME] [--dry-run]

Launches Claude Code against ${PROMPT} in ${RECONCILE_DIR} and logs to ${LOG}.
USAGE
}

DRY_RUN=false
while [[ $# -gt 0 ]]; do
  case "$1" in
    --tmux-session) SESSION="$2"; shift 2 ;;
    --dry-run) DRY_RUN=true; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "ERROR: unknown arg: $1" >&2; usage >&2; exit 1 ;;
  esac
done

[[ -f "$PROMPT" ]] || { echo "ERROR: prompt missing: $PROMPT" >&2; exit 1; }
[[ -d "$RECONCILE_DIR" ]] || { echo "ERROR: reconcile dir missing: $RECONCILE_DIR" >&2; exit 1; }
mkdir -p "$LOG_DIR"

cmd="cd $(printf '%q' "$RECONCILE_DIR") && claude --print --dangerously-skip-permissions < $(printf '%q' "$PROMPT") 2>&1 | tee $(printf '%q' "$LOG")"

if [[ "$DRY_RUN" == true ]]; then
  printf 'session=%s\ncmd=%s\n' "$SESSION" "$cmd"
  exit 0
fi

if tmux has-session -t "$SESSION" 2>/dev/null; then
  echo "ERROR: tmux session already exists: $SESSION" >&2
  exit 1
fi

tmux new-session -d -s "$SESSION" -c "$RECONCILE_DIR" "bash -lc $(printf '%q' "$cmd")"
echo "started session=$SESSION log=$LOG prompt=$PROMPT workdir=$RECONCILE_DIR"
