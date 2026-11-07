#!/usr/bin/env bash
# Thin entry point; the function is shared by checkout and review callers.
set -euo pipefail
script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
# shellcheck source=scripts/lib/worktree-index.sh
source "$script_dir/../lib/worktree-index.sh"
worktree_index_preflight "${1:-.}" "${2:-}"
