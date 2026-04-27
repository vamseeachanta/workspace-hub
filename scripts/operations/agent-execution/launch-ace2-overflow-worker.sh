#!/usr/bin/env bash
# Copy repo-owned prompts to ace-linux-2 and launch the overflow Claude Code worker.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_HUB="${WORKSPACE_HUB:-$(cd "${SCRIPT_DIR}/../../.." && pwd)}"
REMOTE="${REMOTE:-ace-linux-2}"
REMOTE_WORKDIR="${REMOTE_WORKDIR:-/mnt/local-analysis/workspace-hub}"
REMOTE_LOG_DIR="${REMOTE_LOG_DIR:-/mnt/local-analysis/ace2-worker-logs}"
REMOTE_REPORT_DIR="${REMOTE_REPORT_DIR:-/mnt/local-analysis/ace2-worker-reports}"
SESSION="${SESSION:-ace2-overflow-20260427}"
BASE_PROMPT="${WORKSPACE_HUB}/docs/plans/machine-prompts/2026-04-27/ace-linux-2-continuous-parallel-work-prompt.md"
EXEC_PROMPT="${WORKSPACE_HUB}/docs/plans/machine-prompts/2026-04-27/execution/ace-linux-2-execute-now.md"
REMOTE_BASE_PROMPT="/tmp/ace-linux-2-continuous-parallel-work-prompt.md"
REMOTE_EXEC_PROMPT="/tmp/ace-linux-2-execute-now.md"
REMOTE_LOG="${REMOTE_LOG_DIR}/ace2-overflow-20260427.log"
DRY_RUN=false

usage() {
  cat <<USAGE
Usage: bash scripts/operations/agent-execution/launch-ace2-overflow-worker.sh [--remote HOST] [--tmux-session NAME] [--dry-run]

Copies repo-owned prompts to HOST and launches a remote tmux Claude Code worker.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --remote) REMOTE="$2"; shift 2 ;;
    --tmux-session) SESSION="$2"; shift 2 ;;
    --dry-run) DRY_RUN=true; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "ERROR: unknown arg: $1" >&2; usage >&2; exit 1 ;;
  esac
done

[[ -f "$BASE_PROMPT" ]] || { echo "ERROR: base prompt missing: $BASE_PROMPT" >&2; exit 1; }
[[ -f "$EXEC_PROMPT" ]] || { echo "ERROR: exec prompt missing: $EXEC_PROMPT" >&2; exit 1; }

if [[ "$DRY_RUN" == true ]]; then
  cat <<DRY
remote=$REMOTE
session=$SESSION
scp $BASE_PROMPT $REMOTE:$REMOTE_BASE_PROMPT
scp $EXEC_PROMPT $REMOTE:$REMOTE_EXEC_PROMPT
remote_log=$REMOTE_LOG
DRY
  exit 0
fi

scp "$BASE_PROMPT" "${REMOTE}:${REMOTE_BASE_PROMPT}"
scp "$EXEC_PROMPT" "${REMOTE}:${REMOTE_EXEC_PROMPT}"

ssh -o BatchMode=yes "$REMOTE" bash -lc "$(printf '%q' "
set -euo pipefail
mkdir -p '$REMOTE_LOG_DIR' '$REMOTE_REPORT_DIR'
if tmux has-session -t '$SESSION' 2>/dev/null; then
  echo 'ERROR: tmux session already exists: $SESSION' >&2
  exit 1
fi
cmd=\"cd '$REMOTE_WORKDIR' && claude --print --dangerously-skip-permissions < '$REMOTE_EXEC_PROMPT' 2>&1 | tee '$REMOTE_LOG'\"
tmux new-session -d -s '$SESSION' -c '$REMOTE_WORKDIR' \"bash -lc \\\"\$cmd\\\"\"
echo 'started remote=$REMOTE session=$SESSION log=$REMOTE_LOG report_dir=$REMOTE_REPORT_DIR'
")"
