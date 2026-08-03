#!/usr/bin/env bash
# start-session.sh — Launch a 6-window tmux session tailored to the current machine.
# Usage: ./start-session.sh [session-name]
#
# Detects hostname and adjusts workspace root + window names accordingly.
# Works on all workspace-hub machines (Linux and Git Bash on Windows).

set -euo pipefail

# `main` is the ONE canonical session name (#3784). It previously defaulted to
# `work`, while ~/.bashrc carried `alias w='tmux new -A -s main'` and the live
# sessions were called `overnight` — three names for one thing, which defeats
# the whole point of `new -A` being attach-or-create.
SESSION="${1:-main}"

# Injectable so the per-host branches below are testable. A plain
# HOST="$(hostname)" OVERWRITES any inherited value, so a test that merely
# exported HOST would silently exercise the current machine's branch.
HOST="${WH_HOSTNAME:-$(hostname)}"

# Resolve workspace root per machine
case "$HOST" in
  ace-linux-1)
    WS_ROOT="/mnt/local-analysis/workspace-hub"
    ;;
  ace-linux-2)
    # Both /mnt/workspace-hub and /mnt/local-analysis/workspace-hub exist on
    # this box; the deployed ~/.tmux.conf symlink resolves to the latter, so
    # the launcher matches it. The stranded-copy problem itself is #3696.
    WS_ROOT="/mnt/local-analysis/workspace-hub"
    ;;
  gpu-claw)
    WS_ROOT="$HOME/ws/workspace-hub"   # relocation target per #3507
    ;;
  ace-win-1|ace-win-2|licensed-win-1|licensed-win-2)
    WS_ROOT="/d/workspace-hub"   # Git Bash path
    ;;
  shoerack)
    WS_ROOT="$HOME"             # not yet onboarded
    ;;
  *)
    WS_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo "$HOME")"
    ;;
esac

# Reattach if session already exists
if tmux has-session -t "$SESSION" 2>/dev/null; then
  echo "Session '$SESSION' exists — attaching."
  exec tmux attach -t "$SESSION"
fi

# Create session with 6 named windows
tmux new-session  -d -s "$SESSION" -n 'main'   -c "$WS_ROOT"
tmux new-window      -t "$SESSION" -n 'code'   -c "$WS_ROOT"
tmux new-window      -t "$SESSION" -n 'test'   -c "$WS_ROOT"
tmux new-window      -t "$SESSION" -n 'logs'   -c "$WS_ROOT"
tmux new-window      -t "$SESSION" -n 'git'    -c "$WS_ROOT"
tmux new-window      -t "$SESSION" -n 'agent'  -c "$WS_ROOT"

# Start on window 1
tmux select-window -t "$SESSION":1

echo "Session '$SESSION' ready — 6 windows at $WS_ROOT"
exec tmux attach -t "$SESSION"
