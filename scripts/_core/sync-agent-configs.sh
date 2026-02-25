#!/usr/bin/env bash
# Sync managed agent configs from workspace-hub templates into home directories.
# Usage: bash scripts/_core/sync-agent-configs.sh [--force] [--dry-run]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WS_HUB="$(cd "$SCRIPT_DIR/../.." && pwd)"

FORCE=false
DRY_RUN=false
for arg in "$@"; do
    case "$arg" in
        --force) FORCE=true ;;
        --dry-run) DRY_RUN=true ;;
        --help|-h)
            cat <<'USAGE'
Usage: bash scripts/_core/sync-agent-configs.sh [--force] [--dry-run]

Options:
  --force    Overwrite plain-copy targets when merge is not possible
  --dry-run  Show planned actions without writing files
USAGE
            exit 0
            ;;
        *)
            echo "Unknown option: $arg" >&2
            exit 1
            ;;
    esac
done

CLAUDE_TEMPLATE="$WS_HUB/config/agents/claude/settings.json"
CODEX_TEMPLATE="$WS_HUB/config/agents/codex/config.toml"
GEMINI_TEMPLATE="$WS_HUB/config/agents/gemini/settings.json"

CLAUDE_TARGET="$HOME/.claude/settings.json"
CODEX_TARGET="$HOME/.codex/config.toml"
GEMINI_TARGET="$HOME/.gemini/settings.json"

changed=0
skipped=0

log_change() { echo "[UPDATED] $1"; changed=$((changed + 1)); }
log_skip() { echo "[SKIP]    $1"; skipped=$((skipped + 1)); }

ensure_parent_dir() {
    mkdir -p "$(dirname "$1")"
}

sync_json_merge() {
    local template="$1"
    local target="$2"
    local label="$3"

    ensure_parent_dir "$target"

    if ! command -v jq >/dev/null 2>&1; then
        if [[ ! -f "$target" || "$FORCE" == "true" ]]; then
            if [[ "$DRY_RUN" == "true" ]]; then
                log_change "$label -> $target (copy)"
            else
                cp "$template" "$target"
                log_change "$label -> $target (copy)"
            fi
        else
            log_skip "$label -> $target (jq missing and target exists)"
        fi
        return
    fi

    if [[ ! -f "$target" ]]; then
        if [[ "$DRY_RUN" == "true" ]]; then
            log_change "$label -> $target (create)"
        else
            cp "$template" "$target"
            log_change "$label -> $target (create)"
        fi
        return
    fi

    local tmp
    tmp="$(mktemp)"
    jq -s '.[0] * .[1]' "$target" "$template" > "$tmp"

    if cmp -s "$tmp" "$target"; then
        rm -f "$tmp"
        log_skip "$label -> $target (already current)"
    else
        if [[ "$DRY_RUN" == "true" ]]; then
            rm -f "$tmp"
            log_change "$label -> $target (merge)"
        else
            mv "$tmp" "$target"
            log_change "$label -> $target (merge)"
        fi
    fi
}

sync_codex_status_line() {
    local template="$1"
    local target="$2"
    local label="$3"

    ensure_parent_dir "$target"

    if [[ ! -f "$target" ]]; then
        if [[ "$DRY_RUN" == "true" ]]; then
            log_change "$label -> $target (create)"
        else
            cp "$template" "$target"
            log_change "$label -> $target (create)"
        fi
        return
    fi

    local tmp
    tmp="$(mktemp)"

    awk '
        BEGIN { skip = 0 }
        /^\[status_line\][[:space:]]*$/ { skip = 1; next }
        skip && /^\[[^]]+\][[:space:]]*$/ { skip = 0 }
        !skip { print }
    ' "$target" > "$tmp"

    # Ensure one trailing newline before appending managed section.
    if [[ -s "$tmp" ]]; then
        printf '\n' >> "$tmp"
    fi
    cat "$template" >> "$tmp"

    if cmp -s "$tmp" "$target"; then
        rm -f "$tmp"
        log_skip "$label -> $target (already current)"
    else
        if [[ "$DRY_RUN" == "true" ]]; then
            rm -f "$tmp"
            log_change "$label -> $target (status_line upsert)"
        else
            mv "$tmp" "$target"
            log_change "$label -> $target (status_line upsert)"
        fi
    fi
}

echo "=== Syncing Agent Configs ==="
echo "Workspace: $WS_HUB"
echo "Mode: force=$FORCE dry_run=$DRY_RUN"
echo

sync_json_merge "$CLAUDE_TEMPLATE" "$CLAUDE_TARGET" "Claude settings"
sync_codex_status_line "$CODEX_TEMPLATE" "$CODEX_TARGET" "Codex config"
sync_json_merge "$GEMINI_TEMPLATE" "$GEMINI_TARGET" "Gemini settings"

echo
echo "=== Summary ==="
echo "Updated: $changed"
echo "Skipped: $skipped"
