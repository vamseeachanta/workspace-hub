#!/usr/bin/env bash
# install-hooks.sh — Install pre-push hook for hub and all tier-1 submodules.
# WRK-1064
#
# For the hub:    writes a symlink .git/hooks/pre-push → ../../scripts/hooks/pre-push.sh
# For submodules: writes a shim that locates hub root and delegates to hub hook.
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
TIER1_REPOS=(assetutilities digitalmodel worldenergydata assethold OGManufacturing)

# ── Install hub hook ──────────────────────────────────────────────────────────
HUB_HOOKS_DIR="${REPO_ROOT}/.git/hooks"
mkdir -p "$HUB_HOOKS_DIR"

HOOK_TARGET="${HUB_HOOKS_DIR}/pre-push"
if [[ -L "$HOOK_TARGET" ]]; then
    rm "$HOOK_TARGET"
fi
ln -s "../../scripts/hooks/pre-push.sh" "$HOOK_TARGET"
chmod +x "${REPO_ROOT}/scripts/hooks/pre-push.sh"
echo "[install-hooks] Hub hook installed: ${HOOK_TARGET} → ../../scripts/hooks/pre-push.sh"

# ── Install submodule shims ───────────────────────────────────────────────────
for repo in "${TIER1_REPOS[@]}"; do
    SUB_PATH="${REPO_ROOT}/${repo}"
    if [[ ! -d "$SUB_PATH" ]]; then
        echo "[install-hooks] Skipping ${repo} — directory not found." >&2
        continue
    fi

    # Resolve the git dir correctly (handles .git-as-file for submodules)
    GIT_DIR="$(git -C "$SUB_PATH" rev-parse --git-dir 2>/dev/null || true)"
    if [[ -z "$GIT_DIR" ]]; then
        echo "[install-hooks] Skipping ${repo} — could not resolve git dir." >&2
        continue
    fi

    # If git dir is relative, make it absolute relative to the submodule path
    if [[ "$GIT_DIR" != /* ]]; then
        GIT_DIR="${SUB_PATH}/${GIT_DIR}"
    fi

    SUB_HOOKS_DIR="${GIT_DIR}/hooks"
    mkdir -p "$SUB_HOOKS_DIR"

    SHIM="${SUB_HOOKS_DIR}/pre-push"
    cat > "$SHIM" << 'SHIM_EOF'
#!/usr/bin/env bash
# Auto-generated shim by install-hooks.sh (WRK-1064).
# Delegates to hub's pre-push.sh, walking up from the submodule root.
set -euo pipefail

_sub_root="$(git rev-parse --show-toplevel)"

# Walk up until we find workspace-hub root (has scripts/hooks/pre-push.sh)
_hub_root="$_sub_root"
while [[ "$_hub_root" != "/" ]]; do
    _hub_root="$(dirname "$_hub_root")"
    if [[ -f "${_hub_root}/scripts/hooks/pre-push.sh" ]]; then
        break
    fi
done

if [[ ! -f "${_hub_root}/scripts/hooks/pre-push.sh" ]]; then
    echo "[pre-push shim] Could not locate hub pre-push.sh — skipping hook." >&2
    exit 0
fi

exec bash "${_hub_root}/scripts/hooks/pre-push.sh" "$@"
SHIM_EOF
    chmod +x "$SHIM"
    echo "[install-hooks] Submodule shim installed: ${SHIM}"
done

echo "[install-hooks] Done."
