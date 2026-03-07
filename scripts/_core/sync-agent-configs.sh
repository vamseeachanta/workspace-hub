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

upsert_codex_root_model_defaults() {
    local target="$1"
    local label="$2"
    local tmp_clean tmp_final
    tmp_clean="$(mktemp)"
    tmp_final="$(mktemp)"

    awk '
        BEGIN { in_root = 1 }
        in_root && /^\[[^]]+\][[:space:]]*$/ { in_root = 0 }
        in_root && /^model[[:space:]]*=/ { next }
        in_root && /^model_reasoning_effort[[:space:]]*=/ { next }
        { print }
    ' "$target" > "$tmp_clean"

    cat > "$tmp_final" <<'EOF'
model = "gpt-5.4"
model_reasoning_effort = "medium"

EOF
    cat "$tmp_clean" >> "$tmp_final"

    if cmp -s "$tmp_final" "$target"; then
        rm -f "$tmp_clean" "$tmp_final"
        log_skip "$label (already current)"
    else
        if [[ "$DRY_RUN" == "true" ]]; then
            rm -f "$tmp_clean" "$tmp_final"
            log_change "$label (model defaults upsert)"
        else
            mv "$tmp_final" "$target"
            rm -f "$tmp_clean"
            log_change "$label (model defaults upsert)"
        fi
    fi
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

sync_codex_managed_config() {
    local template="$1"
    local target="$2"
    local label="$3"

    ensure_parent_dir "$target"

    if [[ ! -f "$target" ]]; then
        if [[ "$DRY_RUN" == "true" ]]; then
            log_change "$label -> $target (create)"
        else
            cat > "$target" <<'EOF'
model = "gpt-5.4"
model_reasoning_effort = "medium"

EOF
            cat "$template" >> "$target"
            log_change "$label -> $target (create)"
        fi
        return
    fi

    local tmp
    tmp="$(mktemp)"

    # Remove managed root keys before first table and remove existing managed status_line section.
    awk '
        BEGIN { in_root = 1; skip_status = 0 }
        /^\[[^]]+\][[:space:]]*$/ {
            in_root = 0
            if (skip_status == 1) {
                skip_status = 0
            }
        }
        in_root && /^model[[:space:]]*=/ { next }
        in_root && /^model_reasoning_effort[[:space:]]*=/ { next }
        /^\[status_line\][[:space:]]*$/ { skip_status = 1; next }
        skip_status == 1 {
            if (/^\[[^]]+\][[:space:]]*$/) {
                skip_status = 0
                print
            }
            next
        }
        { print }
    ' "$target" > "$tmp"

    cat > "$tmp.new" <<'EOF'
model = "gpt-5.4"
model_reasoning_effort = "medium"

EOF
    cat "$tmp" >> "$tmp.new"

    if [[ -s "$tmp.new" ]]; then
        printf '\n' >> "$tmp.new"
    fi
    cat "$template" >> "$tmp.new"

    if cmp -s "$tmp.new" "$target"; then
        rm -f "$tmp" "$tmp.new"
        log_skip "$label -> $target (already current)"
    else
        if [[ "$DRY_RUN" == "true" ]]; then
            rm -f "$tmp" "$tmp.new"
            log_change "$label -> $target (managed settings upsert)"
        else
            mv "$tmp.new" "$target"
            rm -f "$tmp"
            log_change "$label -> $target (managed settings upsert)"
        fi
    fi
}

sync_repo_codex_configs() {
    local ws_root="$1"
    local list_file="$ws_root/config/sync-items.json"
    local repo_cfg

    # Always sync the current workspace repo-local Codex config if present.
    repo_cfg="$ws_root/.codex/config.toml"
    if [[ -f "$repo_cfg" ]]; then
        upsert_codex_root_model_defaults "$repo_cfg" "Repo Codex config $repo_cfg"
    fi

    # Optionally sync additional repos declared in sync-items.json when available locally.
    if command -v jq >/dev/null 2>&1 && [[ -f "$list_file" ]]; then
        while IFS= read -r repo_cfg; do
            [[ -n "$repo_cfg" ]] || continue
            [[ -f "$repo_cfg" ]] || continue
            upsert_codex_root_model_defaults "$repo_cfg" "Repo Codex config $repo_cfg"
        done < <(
            jq -r '
              .sync_items.git_repositories.base_path as $base
              | .sync_items.git_repositories.repos[]
              | ($base + "/" + . + "/.codex/config.toml")
            ' "$list_file"
        )
    fi
}

echo "=== Syncing Agent Configs ==="
echo "Workspace: $WS_HUB"
echo "Mode: force=$FORCE dry_run=$DRY_RUN"
echo

sync_json_merge "$CLAUDE_TEMPLATE" "$CLAUDE_TARGET" "Claude settings"
sync_codex_managed_config "$CODEX_TEMPLATE" "$CODEX_TARGET" "Codex config"
sync_json_merge "$GEMINI_TEMPLATE" "$GEMINI_TARGET" "Gemini settings"
sync_repo_codex_configs "$WS_HUB"

echo
echo "=== Summary ==="
echo "Updated: $changed"
echo "Skipped: $skipped"
