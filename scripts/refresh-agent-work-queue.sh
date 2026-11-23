#!/bin/bash
# Thin wrapper: delegates to the Python queue refresh module.
# Run weekly on Sunday, regenerates notes/agent-work-queue.md.
#
# Usage:
#   ./scripts/refresh-agent-work-queue.sh                  # write to file
#   ./scripts/refresh-agent-work-queue.sh --dry-run        # print to stdout
#   ./scripts/refresh-agent-work-queue.sh --check-staleness  # check if >7 days old
#   ./scripts/refresh-agent-work-queue.sh --parity-check     # compare file vs live GitHub
set -e
REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

uv run scripts/refresh-agent-work-queue.py "$@"

# Only stage file on a normal refresh (not dry-run or check modes)
case "$1" in
  --dry-run|--check-staleness|--parity-check)
    ;;
  *)
    git add notes/agent-work-queue.md 2>/dev/null || true
    echo "Queue file staged for commit."
    ;;
esac
