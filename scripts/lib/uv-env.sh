#!/usr/bin/env bash
# Shared uv environment defaults for workspace-hub scripts and hooks.

set -euo pipefail

uv_env_repo_root() {
    if [[ -n "${WORKSPACE_HUB:-}" ]] && [[ -d "${WORKSPACE_HUB}" ]]; then
        printf '%s\n' "$WORKSPACE_HUB"
        return
    fi

    git rev-parse --show-toplevel 2>/dev/null || pwd
}

uv_env_setup() {
    local repo_root="${1:-$(uv_env_repo_root)}"
    local default_cache="${repo_root}/.claude/state/uv-cache"

    export UV_CACHE_DIR="${UV_CACHE_DIR:-$default_cache}"
    mkdir -p "$UV_CACHE_DIR"
}

