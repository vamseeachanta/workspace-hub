#!/usr/bin/env bash
# deploy-tmux.sh — Symlink workspace-hub tmux config to ~/.tmux.conf
# Usage: ./deploy-tmux.sh
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SRC="${REPO_ROOT}/config/tmux/tmux.conf"
DEST="$HOME/.tmux.conf"

if [ ! -f "$SRC" ]; then
  echo "ERROR: tmux.conf not found at $SRC" >&2
  exit 1
fi

if [ -L "$DEST" ] && [ "$(readlink -f "$DEST")" = "$(readlink -f "$SRC")" ]; then
  echo "Already linked: $DEST -> $SRC"
else
  ln -sf "$SRC" "$DEST"
  echo "Linked: $DEST -> $SRC"
fi

# Reload config if tmux is running
if tmux list-sessions &>/dev/null; then
  tmux source-file "$DEST"
  echo "Config reloaded in running tmux server."
fi

echo "Done. tmux $(tmux -V) configured."
