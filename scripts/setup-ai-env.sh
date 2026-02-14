#!/usr/bin/env bash
# Workspace-Hub AI environment setup (Claude, Codex, Gemini)
# Usage: ./scripts/setup-ai-env.sh [--force] [--dry-run]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

FORCE=false
DRY_RUN=false
for arg in "$@"; do
    case "$arg" in
        --force) FORCE=true ;;
        --dry-run) DRY_RUN=true ;;
        --help|-h)
            cat <<'USAGE'
Usage: ./scripts/setup-ai-env.sh [--force] [--dry-run]

Options:
  --force    Apply stricter overwrite behavior where supported
  --dry-run  Show actions without writing files
USAGE
            exit 0
            ;;
        *)
            echo "Unknown option: $arg" >&2
            exit 1
            ;;
    esac
done

echo "=== Workspace-Hub AI Environment Setup ==="
echo "Workspace: $WORKSPACE_ROOT"
echo "Mode: force=$FORCE dry_run=$DRY_RUN"
echo

check_cli() {
    local bin="$1"
    local install_hint="$2"
    if command -v "$bin" >/dev/null 2>&1; then
        echo "[OK] $bin detected"
    else
        echo "[WARN] $bin not found"
        echo "       Install hint: $install_hint"
    fi
}

check_cli claude "npm install -g @anthropic-ai/claude-code"
check_cli codex "npm install -g @openai/codex"
check_cli gemini "install Gemini CLI per your platform"

echo

args=()
[[ "$FORCE" == "true" ]] && args+=(--force)
[[ "$DRY_RUN" == "true" ]] && args+=(--dry-run)

bash "$WORKSPACE_ROOT/scripts/_core/sync-agent-configs.sh" "${args[@]}"

if [[ "$DRY_RUN" == "true" ]]; then
    echo "[dry-run] Would run: sync_statusline.sh --all"
else
    bash "$WORKSPACE_ROOT/scripts/_core/sync_statusline.sh" --all
fi

echo
echo "Setup complete."
