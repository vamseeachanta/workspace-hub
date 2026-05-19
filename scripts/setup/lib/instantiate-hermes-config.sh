#!/usr/bin/env bash
# instantiate-hermes-config.sh — Render ~/.hermes/config.yaml from the canonical template.
# Issue: vamseeachanta/workspace-hub#2751 (Phase 2, G4)
#
# Reads config/agents/hermes/config.yaml.template and renders it to
# ~/.hermes/config.yaml with `__WS_HUB_PATH__` substituted with the repo root.
#
# UX Contract Phase D (side-effect emission, NOT browser-blocking):
# - Idempotent by default — skip if target already exists (preserves user edits).
# - `--force` flag overwrites unconditionally.
# - Target written with mode 600 (Hermes config may reference machine-specific paths).
# - Does NOT prompt for any secrets — those live in ~/.hermes/.env (handled by orchestrate-auth.sh).
#
# Usage:
#   source scripts/setup/lib/instantiate-hermes-config.sh
#   instantiate_hermes_config "$REPO_ROOT"           # idempotent default
#   instantiate_hermes_config "$REPO_ROOT" --force   # overwrite

instantiate_hermes_config() {
    local repo_root="$1"
    local force=0
    shift
    for arg in "$@"; do
        case "$arg" in
            --force) force=1 ;;
        esac
    done

    local template="${repo_root}/config/agents/hermes/config.yaml.template"
    local target="${HOME}/.hermes/config.yaml"

    if [[ ! -f "$template" ]]; then
        echo "[instantiate-hermes-config] template not found: $template" >&2
        return 1
    fi

    if [[ -f "$target" && "$force" != "1" ]]; then
        echo "[instantiate-hermes-config] target exists; skipping render: $target (use --force to overwrite)"
        return 0
    fi

    mkdir -p "$(dirname "$target")"

    # Render: substitute __WS_HUB_PATH__ with the actual repo root.
    sed "s|__WS_HUB_PATH__|${repo_root}|g" "$template" > "$target"
    chmod 600 "$target"

    echo "[instantiate-hermes-config] wrote $target (mode 600, repo_root=${repo_root})"
}
