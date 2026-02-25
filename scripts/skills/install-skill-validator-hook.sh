#!/usr/bin/env bash
# install-skill-validator-hook.sh — delegates to install-all-hooks.sh (WRK-312)
# Kept for backwards compatibility; use scripts/setup/install-all-hooks.sh directly.
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel 2>/dev/null || true)"
if [[ -z "$repo_root" ]]; then
  echo "Run this script from inside a git repository." >&2
  exit 2
fi

echo "Delegating to install-all-hooks.sh (WRK-312)..."
bash "$repo_root/scripts/setup/install-all-hooks.sh"
