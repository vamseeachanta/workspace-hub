#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WS_HUB="$(cd "${SCRIPT_DIR}/../.." && pwd)"
source "${SCRIPT_DIR}/lib/git-safe.sh"

COMPUTER_NAME="${COMPUTERNAME:-windows-machine}"
git_safe_init "$WS_HUB"
cd "$WS_HUB"

git_safe_sync "chore: session learnings from ${COMPUTER_NAME}" \
  .claude/state/candidates/ \
  .claude/state/corrections/
