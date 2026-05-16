#!/usr/bin/env bash
# install-soul-runtime.sh — Create/retarget runtime symlinks for SOUL artifacts.
#
# Idempotent. Safe to re-run on any machine. Operates on:
#   ~/.hermes/SOUL.md   → config/agents/hermes/SOUL.runtime.md
#   ~/.codex/AGENTS.md  → config/agents/codex/AGENTS.runtime.md   (replaces any broken-sed copy)
#   ~/.codex/SOUL.md    → config/agents/codex/SOUL.runtime.md    (loader-pending; see Phase 5)
#   ~/.gemini/SOUL.md   → config/agents/gemini/SOUL.runtime.md   (loader-pending; see Phase 5)
#
# Pre-existing non-symlink files at these paths are backed up to
#   <path>.pre-install-backup.<timestamp>
# before being replaced — so a broken sed-derived ~/.codex/AGENTS.md
# is preserved for forensics, not silently overwritten.
#
# Source build: scripts/agents/build-soul-runtime.sh must have been run
# (or the committed *.runtime.md artifacts must be present and current).
# Use scripts/enforcement/check-soul-runtime-drift.sh to verify before install.
#
# Refs: workspace-hub#2719 Phase 4.

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
TS="$(date +%Y%m%dT%H%M%SZ)"
created=0
unchanged=0
backed_up=0
skipped=0

link_if_needed() {
    local repo_relative_target="$1" runtime_path="$2"
    local resolved="${REPO_ROOT}/${repo_relative_target}"

    if [[ ! -f "${resolved}" ]]; then
        echo "SKIP   ${runtime_path} — source ${repo_relative_target} missing (run build-soul-runtime.sh first?)"
        skipped=$((skipped + 1))
        return 0
    fi

    if [[ -L "${runtime_path}" ]]; then
        local cur="$(readlink "${runtime_path}")"
        if [[ "${cur}" == "${resolved}" ]]; then
            echo "OK     ${runtime_path} → already points to ${repo_relative_target}"
            unchanged=$((unchanged + 1))
            return 0
        fi
    fi

    if [[ -e "${runtime_path}" || -L "${runtime_path}" ]]; then
        local backup="${runtime_path}.pre-install-backup.${TS}"
        mv "${runtime_path}" "${backup}"
        echo "BACKUP ${runtime_path} → ${backup}"
        backed_up=$((backed_up + 1))
    fi

    ln -s "${resolved}" "${runtime_path}"
    echo "LINK   ${runtime_path} → ${resolved}"
    created=$((created + 1))
}

# Hermes
if [[ -d "${HOME}/.hermes" ]]; then
    link_if_needed config/agents/hermes/SOUL.runtime.md   "${HOME}/.hermes/SOUL.md"
else
    echo "SKIP   ~/.hermes/ not present"
fi

# Codex
if [[ -d "${HOME}/.codex" ]]; then
    link_if_needed config/agents/codex/AGENTS.runtime.md  "${HOME}/.codex/AGENTS.md"
    link_if_needed config/agents/codex/SOUL.runtime.md    "${HOME}/.codex/SOUL.md"
else
    echo "SKIP   ~/.codex/ not present"
fi

# Gemini
if [[ -d "${HOME}/.gemini" ]]; then
    link_if_needed config/agents/gemini/SOUL.runtime.md   "${HOME}/.gemini/SOUL.md"
else
    echo "SKIP   ~/.gemini/ not present"
fi

echo
echo "Summary: ${created} created, ${unchanged} unchanged, ${backed_up} backed-up, ${skipped} skipped."
