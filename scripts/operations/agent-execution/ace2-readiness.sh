#!/usr/bin/env bash
# Probe ace-linux-2 readiness for overflow AI worker execution.
set -euo pipefail

REMOTE="${REMOTE:-ace-linux-2}"

usage() {
  cat <<USAGE
Usage: bash scripts/operations/agent-execution/ace2-readiness.sh [--remote HOST]

Runs a login-shell readiness probe on the remote worker host.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --remote) REMOTE="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "ERROR: unknown arg: $1" >&2; usage >&2; exit 1 ;;
  esac
done

ssh -o BatchMode=yes -o ConnectTimeout=5 "$REMOTE" 'bash -lc '\''
set -euo pipefail
hostname
for c in claude codex hermes gh git python uv tmux; do
  printf "%s=" "$c"
  command -v "$c" || true
done
echo "--- gh auth ---"
gh auth status 2>&1 | sed -n "1,12p" || true
echo "--- workspace ---"
if cd /mnt/local-analysis/workspace-hub 2>/dev/null; then
  git status --short --branch | sed -n "1,30p"
else
  echo no-workspace
fi
'\'''
