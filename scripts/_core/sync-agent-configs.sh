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
HERMES_TEMPLATE="$WS_HUB/config/agents/hermes/config.yaml.template"
HERMES_SOUL_TEMPLATE="$WS_HUB/config/agents/hermes/SOUL.md"

CLAUDE_TARGET="$HOME/.claude/settings.json"
CODEX_TARGET="$HOME/.codex/config.toml"
GEMINI_TARGET="$HOME/.gemini/settings.json"
HERMES_TARGET="$HOME/.hermes/config.yaml"
HERMES_SOUL_TARGET="$HOME/.hermes/SOUL.md"

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

resolve_ws_hub_path() {
    # Determine workspace-hub path for this machine from harness-config.yaml.
    local config="$WS_HUB/scripts/readiness/harness-config.yaml"
    local hostname_short
    hostname_short="$(hostname -s)"
    local ws_path=""

    if [[ -f "$config" ]] && command -v python3 >/dev/null 2>&1; then
        ws_path=$(python3 -c "
import yaml, socket
hostname = socket.gethostname().split('.')[0]
with open('$config') as f:
    cfg = yaml.safe_load(f)
for name, ws in (cfg.get('workstations') or {}).items():
    ws_path = ws.get('ws_hub_path') or ''
    # Match by hostname prefix in workstation name, or by explicit lookup
    if ws_path and hostname.lower() in name.lower():
        print(ws_path)
        break
" 2>/dev/null || true)
    fi

    # Fallback: use the workspace-hub we're running from
    if [[ -z "$ws_path" ]]; then
        ws_path="$WS_HUB"
    fi
    echo "$ws_path"
}

sync_hermes_yaml_config() {
    local template="$1"
    local target="$2"
    local label="$3"

    ensure_parent_dir "$target"

    # Resolve __WS_HUB_PATH__ placeholder to machine-specific path
    local ws_hub_path
    ws_hub_path="$(resolve_ws_hub_path)"
    local resolved_template
    resolved_template="$(mktemp)"
    sed "s|__WS_HUB_PATH__|${ws_hub_path}|g" "$template" > "$resolved_template"

    if [[ ! -f "$target" ]]; then
        if [[ "$DRY_RUN" == "true" ]]; then
            log_change "$label -> $target (create, ws_hub=$ws_hub_path)"
        else
            cp "$resolved_template" "$target"
            log_change "$label -> $target (create, ws_hub=$ws_hub_path)"
        fi
        rm -f "$resolved_template"
        return
    fi

    # Smart merge: update managed keys from template, preserve machine-specific overrides.
    # Managed keys: model, agent, terminal (subset), browser, checkpoints, compression, skills.
    # Machine-specific (preserved): terminal.backend, terminal.cwd, anything not in template.
    if command -v python3 >/dev/null 2>&1; then
        local merged
        merged="$(mktemp)"
        python3 -c "
import yaml, sys

def deep_merge(base, overlay):
    \"\"\"Merge overlay into base. Overlay wins for scalars; recurse for dicts.\"\"\"
    result = dict(base)
    for k, v in overlay.items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = deep_merge(result[k], v)
        else:
            result[k] = v
    return result

with open('$target') as f:
    existing = yaml.safe_load(f) or {}
with open('$resolved_template') as f:
    template = yaml.safe_load(f) or {}

merged = deep_merge(existing, template)

with open('$merged', 'w') as f:
    yaml.dump(merged, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
" 2>/dev/null

        if [[ -s "$merged" ]]; then
            if cmp -s "$merged" "$target"; then
                rm -f "$merged" "$resolved_template"
                log_skip "$label -> $target (already current)"
                return
            fi
            if [[ "$DRY_RUN" == "true" ]]; then
                rm -f "$merged" "$resolved_template"
                log_change "$label -> $target (yaml merge, ws_hub=$ws_hub_path)"
            else
                mv "$merged" "$target"
                rm -f "$resolved_template"
                log_change "$label -> $target (yaml merge, ws_hub=$ws_hub_path)"
            fi
            return
        fi
        rm -f "$merged"
    fi

    # Fallback: cmp + force (no python available for merge)
    if cmp -s "$resolved_template" "$target"; then
        log_skip "$label -> $target (already current)"
    elif [[ "$FORCE" == "true" ]]; then
        if [[ "$DRY_RUN" == "true" ]]; then
            log_change "$label -> $target (overwrite, ws_hub=$ws_hub_path)"
        else
            cp "$resolved_template" "$target"
            log_change "$label -> $target (overwrite, ws_hub=$ws_hub_path)"
        fi
    else
        log_skip "$label -> $target (differs, use --force to overwrite)"
    fi
    rm -f "$resolved_template"
}

sync_hermes_plain_file() {
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

    if cmp -s "$template" "$target"; then
        log_skip "$label -> $target (already current)"
    else
        if [[ "$DRY_RUN" == "true" ]]; then
            log_change "$label -> $target (update)"
        else
            cp "$template" "$target"
            log_change "$label -> $target (update)"
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

# Hermes — sync config.yaml and SOUL.md if templates exist
if [[ -f "$HERMES_TEMPLATE" ]]; then
    sync_hermes_yaml_config "$HERMES_TEMPLATE" "$HERMES_TARGET" "Hermes config"
fi
if [[ -f "$HERMES_SOUL_TEMPLATE" ]]; then
    sync_hermes_plain_file "$HERMES_SOUL_TEMPLATE" "$HERMES_SOUL_TARGET" "Hermes SOUL.md"
fi

# ── Restore agent memory snapshots on fresh machine ───────────────────
echo
echo "=== Restoring Agent Memory Snapshots ==="

# Hermes memories (#1777)
HERMES_MEM_SNAP="$WS_HUB/config/agents/hermes/memories"
HERMES_MEM_TARGET="$HOME/.hermes/memories"
if [[ -d "$HERMES_MEM_SNAP" && -d "$HOME/.hermes" ]]; then
    if [[ ! -f "$HERMES_MEM_TARGET/MEMORY.md" ]] || [[ "$FORCE" == "true" ]]; then
        mkdir -p "$HERMES_MEM_TARGET"
        if [[ "$DRY_RUN" == "true" ]]; then
            log_change "Hermes memories -> $HERMES_MEM_TARGET (restore from snapshot)"
        else
            for f in "$HERMES_MEM_SNAP"/*.snapshot; do
                [[ -f "$f" ]] || continue
                basename="${f%.snapshot}"
                basename="$(basename "$basename")"
                cp "$f" "$HERMES_MEM_TARGET/$basename"
            done
            log_change "Hermes memories -> $HERMES_MEM_TARGET (restored)"
        fi
    else
        log_skip "Hermes memories (already exist at $HERMES_MEM_TARGET)"
    fi
else
    log_skip "Hermes memories (hermes not installed or no snapshots)"
fi

# Claude Code project memory (#1779)
CLAUDE_MEM_SNAP="$WS_HUB/config/agents/claude/memory-snapshots"
# Derive the encoded project path from WS_HUB
WS_HUB_ENCODED="$(echo "$WS_HUB" | sed 's|^/||; s|/|-|g')"
CLAUDE_MEM_TARGET="$HOME/.claude/projects/-${WS_HUB_ENCODED}/memory"
if [[ -d "$CLAUDE_MEM_SNAP" && -d "$HOME/.claude" ]]; then
    EXISTING_COUNT=$(ls "$CLAUDE_MEM_TARGET"/*.md 2>/dev/null | wc -l || echo 0)
    if [[ "$EXISTING_COUNT" -lt 5 ]] || [[ "$FORCE" == "true" ]]; then
        mkdir -p "$CLAUDE_MEM_TARGET"
        if [[ "$DRY_RUN" == "true" ]]; then
            log_change "Claude project memory -> $CLAUDE_MEM_TARGET (restore from snapshot)"
        else
            # Don't overwrite existing files — only copy missing ones
            for f in "$CLAUDE_MEM_SNAP"/*.md; do
                [[ -f "$f" ]] || continue
                basename="$(basename "$f")"
                # Skip worldenergydata snapshot — different project path
                [[ "$basename" == worldenergydata-* ]] && continue
                if [[ ! -f "$CLAUDE_MEM_TARGET/$basename" ]] || [[ "$FORCE" == "true" ]]; then
                    cp "$f" "$CLAUDE_MEM_TARGET/$basename"
                fi
            done
            log_change "Claude project memory -> $CLAUDE_MEM_TARGET (restored)"
        fi
    else
        log_skip "Claude project memory (already has $EXISTING_COUNT files)"
    fi
else
    log_skip "Claude project memory (claude not installed or no snapshots)"
fi

# Codex state (#1781)
CODEX_STATE_SNAP="$WS_HUB/config/agents/codex/state-snapshots"
if [[ -d "$CODEX_STATE_SNAP" && -d "$HOME/.codex" ]]; then
    if [[ ! -f "$HOME/.codex/rules/default.rules" ]] || [[ "$FORCE" == "true" ]]; then
        if [[ "$DRY_RUN" == "true" ]]; then
            log_change "Codex state -> ~/.codex/ (restore from snapshot)"
        else
            mkdir -p "$HOME/.codex/rules"
            cp "$CODEX_STATE_SNAP/default.rules" "$HOME/.codex/rules/" 2>/dev/null || true
            cp "$CODEX_STATE_SNAP/history.jsonl" "$HOME/.codex/" 2>/dev/null || true
            cp "$CODEX_STATE_SNAP/session_index.jsonl" "$HOME/.codex/" 2>/dev/null || true
            log_change "Codex state -> ~/.codex/ (restored)"
        fi
    else
        log_skip "Codex state (default.rules already exists)"
    fi
else
    log_skip "Codex state (codex not installed or no snapshots)"
fi

# Gemini state (#1781)
GEMINI_STATE_SNAP="$WS_HUB/config/agents/gemini/state-snapshots"
if [[ -d "$GEMINI_STATE_SNAP" && -d "$HOME/.gemini" ]]; then
    if [[ ! -f "$HOME/.gemini/state.json" ]] || [[ "$FORCE" == "true" ]]; then
        if [[ "$DRY_RUN" == "true" ]]; then
            log_change "Gemini state -> ~/.gemini/ (restore from snapshot)"
        else
            cp "$GEMINI_STATE_SNAP/state.json" "$HOME/.gemini/" 2>/dev/null || true
            cp "$GEMINI_STATE_SNAP/projects.json" "$HOME/.gemini/" 2>/dev/null || true
            log_change "Gemini state -> ~/.gemini/ (restored)"
        fi
    else
        log_skip "Gemini state (state.json already exists)"
    fi
else
    log_skip "Gemini state (gemini not installed or no snapshots)"
fi

echo
echo "=== Summary ==="
echo "Updated: $changed"
echo "Skipped: $skipped"
