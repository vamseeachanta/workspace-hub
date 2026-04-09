#!/bin/bash
# Thin wrapper: delegates to the Python queue refresh module.
# Run weekly on Sunday, regenerates notes/agent-work-queue.md.
#
# Usage:
#   ./scripts/refresh-agent-work-queue.sh            # write to file
#   ./scripts/refresh-agent-work-queue.sh --dry-run   # print to stdout
set -e
REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

uv run scripts/refresh-agent-work-queue.py "$@"

if [ "$1" != "--dry-run" ]; then
  git add notes/agent-work-queue.md 2>/dev/null || true
  echo "Queue file staged for commit."
fi
