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

sync_make_target_tmp() {
    local target="$1"
    local dir base
    dir="$(dirname "$target")"
    base="$(basename "$target")"
    mktemp "$dir/.${base}.tmp.XXXXXX"
}

render_hermes_template() {
    local template="$1"
    local output_path="$2"
    local ws_hub_path="$3"

    if [[ "$ws_hub_path" == *$'\n'* ]]; then
        echo "[ERROR] ws_hub_path contains newline; refusing to render Hermes template" >&2
        return 1
    fi

    if command -v python3 >/dev/null 2>&1; then
        if WS_HUB_PATH="$ws_hub_path" python3 - "$template" "$output_path" <<'PY'
import os
import pathlib
import sys

template_path = pathlib.Path(sys.argv[1])
output_path = pathlib.Path(sys.argv[2])
rendered = template_path.read_text().replace("__WS_HUB_PATH__", os.environ["WS_HUB_PATH"])
output_path.write_text(rendered)
PY
        then
            return
        fi
    fi

    if command -v uv >/dev/null 2>&1; then
        WS_HUB_PATH="$ws_hub_path" uv run --no-project python - "$template" "$output_path" <<'PY'
import os
import pathlib
import sys

template_path = pathlib.Path(sys.argv[1])
output_path = pathlib.Path(sys.argv[2])
rendered = template_path.read_text().replace("__WS_HUB_PATH__", os.environ["WS_HUB_PATH"])
output_path.write_text(rendered)
PY
        return
    fi

    echo "[ERROR] render_hermes_template requires python3 or uv" >&2
    return 1
}

validate_json_file() {
    local target="$1"
    local label="$2"

    if command -v jq >/dev/null 2>&1; then
        jq empty "$target" >/dev/null
        return
    fi

    if command -v python3 >/dev/null 2>&1; then
        if python3 - "$target" <<'PY' >/dev/null
import json
import pathlib
import sys

with pathlib.Path(sys.argv[1]).open() as fh:
    json.load(fh)
PY
        then
            return
        fi
    fi

    if command -v uv >/dev/null 2>&1; then
        uv run --no-project python - "$target" <<'PY' >/dev/null
import json
import pathlib
import sys

with pathlib.Path(sys.argv[1]).open() as fh:
    json.load(fh)
PY
        return
    fi

    echo "[WARN] Skipping JSON validation for $label -> $target (jq/python3/uv unavailable)" >&2
}

validate_yaml_file() {
    local target="$1"
    local label="$2"

    if command -v python3 >/dev/null 2>&1; then
        if python3 - "$target" <<'PY' >/dev/null
import pathlib
import sys
import yaml

with pathlib.Path(sys.argv[1]).open() as fh:
    yaml.safe_load(fh)
PY
        then
            return
        fi
    fi

    if command -v uv >/dev/null 2>&1; then
        uv run --no-project python - "$target" <<'PY' >/dev/null
import pathlib
import sys
import yaml

with pathlib.Path(sys.argv[1]).open() as fh:
    yaml.safe_load(fh)
PY
        return
    fi

    echo "[WARN] Skipping YAML validation for $label -> $target (python3/uv unavailable)" >&2
}

sanitize_codex_managed_keys() {
    local source_file="$1"
    local output_file="$2"
    local strip_status_line="${3:-false}"

    if command -v python3 >/dev/null 2>&1; then
        if python3 - "$source_file" "$output_file" "$strip_status_line" <<'PY'
import pathlib
import re
import sys

source_path = pathlib.Path(sys.argv[1])
output_path = pathlib.Path(sys.argv[2])
strip_status_line = sys.argv[3].lower() == 'true'
managed_keys = {'model', 'model_reasoning_effort'}
table_header_re = re.compile(r'^\[\[?[^\]]+\]\]?\s*(?:#.*)?$')
status_line_re = re.compile(r'^\[status_line\]\s*(?:#.*)?$')
managed_line_re = re.compile(r'^\s*(model|model_reasoning_effort)\s*=')


def split_top_level(text, delimiter=','):
    parts = []
    start = 0
    brace = bracket = paren = 0
    in_string = None
    escape = False
    i = 0
    while i < len(text):
        ch = text[i]
        if in_string:
            if in_string == '"' and escape:
                escape = False
            elif in_string == '"' and ch == '\\':
                escape = True
            elif ch == in_string:
                in_string = None
            i += 1
            continue
        if ch in ('"', "'"):
            in_string = ch
        elif ch == '{':
            brace += 1
        elif ch == '}':
            brace -= 1
        elif ch == '[':
            bracket += 1
        elif ch == ']':
            bracket -= 1
        elif ch == '(':
            paren += 1
        elif ch == ')':
            paren -= 1
        elif ch == delimiter and brace == 0 and bracket == 0 and paren == 0:
            parts.append(text[start:i])
            start = i + 1
        i += 1
    parts.append(text[start:])
    return parts


def sanitize_inline_tables(text):
    result = []
    i = 0
    in_string = None
    escape = False
    while i < len(text):
        ch = text[i]
        if in_string:
            result.append(ch)
            if in_string == '"' and escape:
                escape = False
            elif in_string == '"' and ch == '\\':
                escape = True
            elif ch == in_string:
                in_string = None
            i += 1
            continue
        if ch in ('"', "'"):
            in_string = ch
            result.append(ch)
            i += 1
            continue
        if ch != '{':
            result.append(ch)
            i += 1
            continue
        depth = 1
        j = i + 1
        inner_string = None
        inner_escape = False
        while j < len(text):
            cj = text[j]
            if inner_string:
                if inner_string == '"' and inner_escape:
                    inner_escape = False
                elif inner_string == '"' and cj == '\\':
                    inner_escape = True
                elif cj == inner_string:
                    inner_string = None
                j += 1
                continue
            if cj in ('"', "'"):
                inner_string = cj
            elif cj == '{':
                depth += 1
            elif cj == '}':
                depth -= 1
                if depth == 0:
                    break
            j += 1
        if depth != 0:
            result.append(ch)
            i += 1
            continue
        inner = text[i + 1:j]
        entries = split_top_level(inner)
        sanitized_entries = []
        for entry in entries:
            stripped = entry.strip()
            if not stripped:
                continue
            key, sep, value = stripped.partition('=')
            if sep and key.strip() in managed_keys:
                continue
            sanitized_entries.append(sanitize_inline_tables(stripped))
        if sanitized_entries:
            result.append('{ ' + ', '.join(sanitized_entries) + ' }')
        else:
            result.append('{}')
        i = j + 1
    return ''.join(result)


def multiline_state_after(line, current_state):
    i = 0
    in_string = current_state
    while i < len(line):
        if in_string == '"""':
            if line.startswith('"""', i) and (i == 0 or line[i - 1] != '\\'):
                in_string = None
                i += 3
            else:
                i += 1
            continue
        if in_string == "'''":
            if line.startswith("'''", i):
                in_string = None
                i += 3
            else:
                i += 1
            continue
        if line.startswith('"""', i) and (i == 0 or line[i - 1] != '\\'):
            in_string = '"""'
            i += 3
            continue
        if line.startswith("'''", i):
            in_string = "'''"
            i += 3
            continue
        i += 1
    return in_string


skip_status = False
multiline = None
output = []
for line in source_path.read_text().splitlines(keepends=True):
    if multiline is None:
        stripped = line.strip()
        if skip_status:
            if stripped and table_header_re.match(stripped):
                skip_status = False
            else:
                multiline = multiline_state_after(line, multiline)
                continue
        if strip_status_line and stripped and status_line_re.match(stripped):
            skip_status = True
            multiline = multiline_state_after(line, multiline)
            continue
        if managed_line_re.match(line):
            multiline = multiline_state_after(line, multiline)
            continue
        line = sanitize_inline_tables(line)
    output.append(line)
    multiline = multiline_state_after(line, multiline)

output_path.write_text(''.join(output))
PY
        then
            return
        fi
    fi

    if command -v uv >/dev/null 2>&1; then
        uv run --no-project python - "$source_file" "$output_file" "$strip_status_line" <<'PY'
import pathlib
import re
import sys

source_path = pathlib.Path(sys.argv[1])
output_path = pathlib.Path(sys.argv[2])
strip_status_line = sys.argv[3].lower() == 'true'
managed_keys = {'model', 'model_reasoning_effort'}
table_header_re = re.compile(r'^\[\[?[^\]]+\]\]?\s*(?:#.*)?$')
status_line_re = re.compile(r'^\[status_line\]\s*(?:#.*)?$')
managed_line_re = re.compile(r'^\s*(model|model_reasoning_effort)\s*=')


def split_top_level(text, delimiter=','):
    parts = []
    start = 0
    brace = bracket = paren = 0
    in_string = None
    escape = False
    i = 0
    while i < len(text):
        ch = text[i]
        if in_string:
            if in_string == '"' and escape:
                escape = False
            elif in_string == '"' and ch == '\\':
                escape = True
            elif ch == in_string:
                in_string = None
            i += 1
            continue
        if ch in ('"', "'"):
            in_string = ch
        elif ch == '{':
            brace += 1
        elif ch == '}':
            brace -= 1
        elif ch == '[':
            bracket += 1
        elif ch == ']':
            bracket -= 1
        elif ch == '(':
            paren += 1
        elif ch == ')':
            paren -= 1
        elif ch == delimiter and brace == 0 and bracket == 0 and paren == 0:
            parts.append(text[start:i])
            start = i + 1
        i += 1
    parts.append(text[start:])
    return parts


def sanitize_inline_tables(text):
    result = []
    i = 0
    in_string = None
    escape = False
    while i < len(text):
        ch = text[i]
        if in_string:
            result.append(ch)
            if in_string == '"' and escape:
                escape = False
            elif in_string == '"' and ch == '\\':
                escape = True
            elif ch == in_string:
                in_string = None
            i += 1
            continue
        if ch in ('"', "'"):
            in_string = ch
            result.append(ch)
            i += 1
            continue
        if ch != '{':
            result.append(ch)
            i += 1
            continue
        depth = 1
        j = i + 1
        inner_string = None
        inner_escape = False
        while j < len(text):
            cj = text[j]
            if inner_string:
                if inner_string == '"' and inner_escape:
                    inner_escape = False
                elif inner_string == '"' and cj == '\\':
                    inner_escape = True
                elif cj == inner_string:
                    inner_string = None
                j += 1
                continue
            if cj in ('"', "'"):
                inner_string = cj
            elif cj == '{':
                depth += 1
            elif cj == '}':
                depth -= 1
                if depth == 0:
                    break
            j += 1
        if depth != 0:
            result.append(ch)
            i += 1
            continue
        inner = text[i + 1:j]
        entries = split_top_level(inner)
        sanitized_entries = []
        for entry in entries:
            stripped = entry.strip()
            if not stripped:
                continue
            key, sep, value = stripped.partition('=')
            if sep and key.strip() in managed_keys:
                continue
            sanitized_entries.append(sanitize_inline_tables(stripped))
        if sanitized_entries:
            result.append('{ ' + ', '.join(sanitized_entries) + ' }')
        else:
            result.append('{}')
        i = j + 1
    return ''.join(result)


def multiline_state_after(line, current_state):
    i = 0
    in_string = current_state
    while i < len(line):
        if in_string == '"""':
            if line.startswith('"""', i) and (i == 0 or line[i - 1] != '\\'):
                in_string = None
                i += 3
            else:
                i += 1
            continue
        if in_string == "'''":
            if line.startswith("'''", i):
                in_string = None
                i += 3
            else:
                i += 1
            continue
        if line.startswith('"""', i) and (i == 0 or line[i - 1] != '\\'):
            in_string = '"""'
            i += 3
            continue
        if line.startswith("'''", i):
            in_string = "'''"
            i += 3
            continue
        i += 1
    return in_string


skip_status = False
multiline = None
output = []
for line in source_path.read_text().splitlines(keepends=True):
    if multiline is None:
        stripped = line.strip()
        if skip_status:
            if stripped and table_header_re.match(stripped):
                skip_status = False
            else:
                multiline = multiline_state_after(line, multiline)
                continue
        if strip_status_line and stripped and status_line_re.match(stripped):
            skip_status = True
            multiline = multiline_state_after(line, multiline)
            continue
        if managed_line_re.match(line):
            multiline = multiline_state_after(line, multiline)
            continue
        line = sanitize_inline_tables(line)
    output.append(line)
    multiline = multiline_state_after(line, multiline)

output_path.write_text(''.join(output))
PY
        return
    fi

    echo "[ERROR] sanitize_codex_managed_keys requires python3 or uv" >&2
    return 1
}

validate_toml_file() {
    local target="$1"
    local label="$2"

    if command -v uv >/dev/null 2>&1; then
        uv run python - "$target" <<'PY' >/dev/null
import pathlib
import sys
import tomllib

with pathlib.Path(sys.argv[1]).open('rb') as fh:
    tomllib.load(fh)
PY
        return
    fi

    if command -v python3 >/dev/null 2>&1; then
        python3 - "$target" <<'PY' >/dev/null
import pathlib
import sys
import tomllib

with pathlib.Path(sys.argv[1]).open('rb') as fh:
    tomllib.load(fh)
PY
        return
    fi

    echo "[WARN] Skipping TOML validation for $label -> $target (uv/python3 unavailable)" >&2
}

validate_codex_managed_key_scope() {
    local target="$1"
    local label="$2"

    if command -v uv >/dev/null 2>&1; then
        uv run python - "$target" <<'PY' >/dev/null
import pathlib
import sys
import tomllib

MANAGED_KEYS = {"model", "model_reasoning_effort"}


def walk_tables(value, *, is_root=False):
    if isinstance(value, list):
        for child in value:
            walk_tables(child, is_root=False)
        return
    if not isinstance(value, dict):
        return
    if not is_root:
        overlap = MANAGED_KEYS.intersection(value)
        if overlap:
            raise SystemExit(f"managed keys leaked into non-root table: {sorted(overlap)}")
    for child in value.values():
        walk_tables(child, is_root=False)


with pathlib.Path(sys.argv[1]).open('rb') as fh:
    data = tomllib.load(fh)

walk_tables(data, is_root=True)
PY
        return
    fi

    if command -v python3 >/dev/null 2>&1; then
        python3 - "$target" <<'PY' >/dev/null
import pathlib
import sys
import tomllib

MANAGED_KEYS = {"model", "model_reasoning_effort"}


def walk_tables(value, *, is_root=False):
    if isinstance(value, list):
        for child in value:
            walk_tables(child, is_root=False)
        return
    if not isinstance(value, dict):
        return
    if not is_root:
        overlap = MANAGED_KEYS.intersection(value)
        if overlap:
            raise SystemExit(f"managed keys leaked into non-root table: {sorted(overlap)}")
    for child in value.values():
        walk_tables(child, is_root=False)


with pathlib.Path(sys.argv[1]).open('rb') as fh:
    data = tomllib.load(fh)

walk_tables(data, is_root=True)
PY
        return
    fi

    echo "[WARN] Skipping Codex managed-key scope validation for $label -> $target (uv/python3 unavailable)" >&2
}

upsert_codex_root_model_defaults() {
    local target="$1"
    local label="$2"
    local tmp_clean=""
    local tmp_final=""

    trap 'rm -f "$tmp_clean" "$tmp_final"' RETURN

    tmp_clean="$(mktemp)"
    tmp_final="$(mktemp)"

    sanitize_codex_managed_keys "$target" "$tmp_clean"

    cat > "$tmp_final" <<'EOF'
model = "gpt-5.4"
model_reasoning_effort = "medium"

EOF
    cat "$tmp_clean" >> "$tmp_final"

    if ! validate_toml_file "$tmp_final" "$label"; then
        trap - RETURN
        rm -f "$tmp_clean" "$tmp_final"
        return 1
    fi
    if ! validate_codex_managed_key_scope "$tmp_final" "$label"; then
        trap - RETURN
        rm -f "$tmp_clean" "$tmp_final"
        return 1
    fi

    if cmp -s "$tmp_final" "$target"; then
        log_skip "$label (already current)"
    else
        if [[ "$DRY_RUN" == "true" ]]; then
            log_change "$label (model defaults upsert)"
        else
            mv "$tmp_final" "$target"
            tmp_final=""
            log_change "$label (model defaults upsert)"
        fi
    fi

    trap - RETURN
    rm -f "$tmp_clean" "$tmp_final"
}

sync_json_merge() {
    local template="$1"
    local target="$2"
    local label="$3"
    local tmp=""

    trap 'rm -f "$tmp"' RETURN

    if ! command -v jq >/dev/null 2>&1; then
        if [[ ! -f "$target" || "$FORCE" == "true" ]]; then
            if [[ "$DRY_RUN" == "true" ]]; then
                log_change "$label -> $target (copy)"
                trap - RETURN
                rm -f "$tmp"
                return
            fi
            ensure_parent_dir "$target"
            tmp="$(sync_make_target_tmp "$target")"
            cp "$template" "$tmp"
            if ! validate_json_file "$tmp" "$label"; then
                trap - RETURN
                rm -f "$tmp"
                return 1
            fi
            log_change "$label -> $target (copy)"
            mv -f "$tmp" "$target"
            tmp=""
        else
            log_skip "$label -> $target (jq missing and target exists)"
        fi
        trap - RETURN
        rm -f "$tmp"
        return
    fi

    if [[ ! -f "$target" ]]; then
        if [[ "$DRY_RUN" == "true" ]]; then
            log_change "$label -> $target (create)"
            trap - RETURN
            rm -f "$tmp"
            return
        fi
        ensure_parent_dir "$target"
        tmp="$(sync_make_target_tmp "$target")"
        cp "$template" "$tmp"
        if ! validate_json_file "$tmp" "$label"; then
            trap - RETURN
            rm -f "$tmp"
            return 1
        fi
        mv -f "$tmp" "$target"
        tmp=""
        log_change "$label -> $target (create)"
        trap - RETURN
        rm -f "$tmp"
        return
    fi

    if [[ "$DRY_RUN" == "true" ]]; then
        if jq -s '.[0] * .[1]' "$target" "$template" | cmp -s - "$target"; then
            log_skip "$label -> $target (already current)"
        else
            log_change "$label -> $target (merge)"
        fi
        trap - RETURN
        rm -f "$tmp"
        return
    fi

    ensure_parent_dir "$target"
    tmp="$(sync_make_target_tmp "$target")"
    if ! jq -s '.[0] * .[1]' "$target" "$template" > "$tmp"; then
        trap - RETURN
        rm -f "$tmp"
        return 1
    fi
    if ! validate_json_file "$tmp" "$label"; then
        trap - RETURN
        rm -f "$tmp"
        return 1
    fi

    if cmp -s "$tmp" "$target"; then
        log_skip "$label -> $target (already current)"
    else
        mv -f "$tmp" "$target"
        tmp=""
        log_change "$label -> $target (merge)"
    fi

    trap - RETURN
    rm -f "$tmp"
}

sync_codex_managed_config() {
    local template="$1"
    local target="$2"
    local label="$3"
    local tmp=""
    local tmp_new=""
    local template_clean=""

    trap 'rm -f "$tmp" "$tmp_new" "$template_clean"' RETURN

    template_clean="$(mktemp)"
    sanitize_codex_managed_keys "$template" "$template_clean"

    if [[ ! -f "$target" ]]; then
        if [[ "$DRY_RUN" == "true" ]]; then
            log_change "$label -> $target (create)"
            trap - RETURN
            rm -f "$tmp" "$tmp_new" "$template_clean"
            return
        fi

        ensure_parent_dir "$target"
        tmp_new="$(mktemp)"
        cat > "$tmp_new" <<'EOF'
model = "gpt-5.4"
model_reasoning_effort = "medium"

EOF
        cat "$template_clean" >> "$tmp_new"
        if ! validate_toml_file "$tmp_new" "$label"; then
            trap - RETURN
            rm -f "$tmp" "$tmp_new" "$template_clean"
            return 1
        fi
        if ! validate_codex_managed_key_scope "$tmp_new" "$label"; then
            trap - RETURN
            rm -f "$tmp" "$tmp_new" "$template_clean"
            return 1
        fi
        mv "$tmp_new" "$target"
        tmp_new=""
        log_change "$label -> $target (create)"
        trap - RETURN
        rm -f "$tmp" "$tmp_new" "$template_clean"
        return
    fi

    tmp="$(mktemp)"
    tmp_new="$(mktemp)"

    # Remove managed keys from any scope and replace the managed status_line section.
    sanitize_codex_managed_keys "$target" "$tmp" true

    cat > "$tmp_new" <<'EOF'
model = "gpt-5.4"
model_reasoning_effort = "medium"

EOF
    cat "$tmp" >> "$tmp_new"

    if [[ -s "$tmp_new" ]]; then
        printf '\n' >> "$tmp_new"
    fi
    cat "$template_clean" >> "$tmp_new"

    if ! validate_toml_file "$tmp_new" "$label"; then
        trap - RETURN
        rm -f "$tmp" "$tmp_new" "$template_clean"
        return 1
    fi
    if ! validate_codex_managed_key_scope "$tmp_new" "$label"; then
        trap - RETURN
        rm -f "$tmp" "$tmp_new" "$template_clean"
        return 1
    fi

    if cmp -s "$tmp_new" "$target"; then
        log_skip "$label -> $target (already current)"
    else
        if [[ "$DRY_RUN" == "true" ]]; then
            log_change "$label -> $target (managed settings upsert)"
        else
            mv "$tmp_new" "$target"
            tmp_new=""
            log_change "$label -> $target (managed settings upsert)"
        fi
    fi

    trap - RETURN
    rm -f "$tmp" "$tmp_new" "$template_clean"
}

resolve_ws_hub_path() {
    # Determine workspace-hub path for this machine from harness-config.yaml.
    # Resolution order: hostname field match → hostname_aliases match → key substring → fallback.
    local config="$WS_HUB/scripts/readiness/harness-config.yaml"
    local ws_path=""

    if [[ -f "$config" ]]; then
        if command -v python3 >/dev/null 2>&1; then
            ws_path=$(python3 - "$config" <<'PY' 2>/dev/null || true
import yaml, socket, sys
hostname_short = socket.gethostname().split(".")[0].lower()
with open(sys.argv[1]) as f:
    cfg = yaml.safe_load(f)
for name, ws in (cfg.get("workstations") or {}).items():
    ws_path = ws.get("ws_hub_path") or ""
    if not ws_path:
        continue
    cfg_hostname = (ws.get("hostname") or "").lower()
    if cfg_hostname and cfg_hostname == hostname_short:
        print(ws_path); sys.exit(0)
    for alias in (ws.get("hostname_aliases") or []):
        if alias.split(".")[0].lower() == hostname_short:
            print(ws_path); sys.exit(0)
    if hostname_short in name.lower():
        print(ws_path); sys.exit(0)
PY
)
        fi
        if [[ -z "$ws_path" ]] && command -v uv >/dev/null 2>&1; then
            ws_path=$(uv run --no-project python - "$config" <<'PY' 2>/dev/null || true
import yaml, socket, sys
hostname_short = socket.gethostname().split(".")[0].lower()
with open(sys.argv[1]) as f:
    cfg = yaml.safe_load(f)
for name, ws in (cfg.get("workstations") or {}).items():
    ws_path = ws.get("ws_hub_path") or ""
    if not ws_path:
        continue
    cfg_hostname = (ws.get("hostname") or "").lower()
    if cfg_hostname and cfg_hostname == hostname_short:
        print(ws_path); sys.exit(0)
    for alias in (ws.get("hostname_aliases") or []):
        if alias.split(".")[0].lower() == hostname_short:
            print(ws_path); sys.exit(0)
    if hostname_short in name.lower():
        print(ws_path); sys.exit(0)
PY
)
        fi
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
    local ws_hub_path
    local resolved_template=""
    local merged=""

    trap 'rm -f "$resolved_template" "$merged"' RETURN

    ws_hub_path="$(resolve_ws_hub_path)"

    if [[ "$DRY_RUN" != "true" ]]; then
        ensure_parent_dir "$target"
        resolved_template="$(sync_make_target_tmp "$target")"
    else
        resolved_template="$(mktemp)"
    fi

    if ! render_hermes_template "$template" "$resolved_template" "$ws_hub_path"; then
        trap - RETURN
        rm -f "$resolved_template" "$merged"
        return 1
    fi

    if ! validate_yaml_file "$resolved_template" "$label"; then
        trap - RETURN
        rm -f "$resolved_template" "$merged"
        return 1
    fi

    if [[ ! -f "$target" ]]; then
        if [[ "$DRY_RUN" == "true" ]]; then
            log_change "$label -> $target (create, ws_hub=$ws_hub_path)"
        else
            mv -f "$resolved_template" "$target"
            resolved_template=""
            log_change "$label -> $target (create, ws_hub=$ws_hub_path)"
        fi
        trap - RETURN
        rm -f "$resolved_template" "$merged"
        return
    fi

    # Smart merge: update managed keys from template, preserve machine-specific overrides.
    # Managed keys: model, agent, browser, checkpoints, compression, skills, plus terminal except backend/cwd.
    if [[ "$DRY_RUN" != "true" ]]; then
        merged="$(sync_make_target_tmp "$target")"
    else
        merged="$(mktemp)"
    fi

    if command -v python3 >/dev/null 2>&1; then
        if ! python3 - "$target" "$resolved_template" "$merged" <<'PY' 2>/dev/null
import yaml, sys

MANAGED_KEYS = {
    "model",
    "fallback_providers",
    "credential_pool_strategies",
    "toolsets",
    "agent",
    "browser",
    "checkpoints",
    "compression",
    "skills",
}
TERMINAL_PRESERVE_KEYS = {"backend", "cwd"}

target_path, template_path, merged_path = sys.argv[1], sys.argv[2], sys.argv[3]
with open(target_path) as f:
    existing = yaml.safe_load(f) or {}
with open(template_path) as f:
    template = yaml.safe_load(f) or {}

merged = dict(existing)
for key, value in template.items():
    if key == "terminal" and isinstance(value, dict):
        existing_terminal = existing.get("terminal") if isinstance(existing.get("terminal"), dict) else {}
        merged_terminal = dict(value)
        for preserve_key in TERMINAL_PRESERVE_KEYS:
            if preserve_key in existing_terminal:
                merged_terminal[preserve_key] = existing_terminal[preserve_key]
        merged[key] = merged_terminal
    elif key in MANAGED_KEYS:
        merged[key] = value
    elif key not in merged:
        merged[key] = value

with open(merged_path, 'w') as f:
    yaml.dump(merged, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
PY
        then
            rm -f "$merged"
            merged=""
        fi
    fi

    if [[ -z "$merged" || ! -s "$merged" ]] && command -v uv >/dev/null 2>&1; then
        if [[ "$DRY_RUN" != "true" ]]; then
            merged="$(sync_make_target_tmp "$target")"
        else
            merged="$(mktemp)"
        fi
        if ! uv run --no-project python - "$target" "$resolved_template" "$merged" <<'PY' 2>/dev/null
import yaml, sys

MANAGED_KEYS = {
    "model",
    "fallback_providers",
    "credential_pool_strategies",
    "toolsets",
    "agent",
    "browser",
    "checkpoints",
    "compression",
    "skills",
}
TERMINAL_PRESERVE_KEYS = {"backend", "cwd"}

target_path, template_path, merged_path = sys.argv[1], sys.argv[2], sys.argv[3]
with open(target_path) as f:
    existing = yaml.safe_load(f) or {}
with open(template_path) as f:
    template = yaml.safe_load(f) or {}

merged = dict(existing)
for key, value in template.items():
    if key == "terminal" and isinstance(value, dict):
        existing_terminal = existing.get("terminal") if isinstance(existing.get("terminal"), dict) else {}
        merged_terminal = dict(value)
        for preserve_key in TERMINAL_PRESERVE_KEYS:
            if preserve_key in existing_terminal:
                merged_terminal[preserve_key] = existing_terminal[preserve_key]
        merged[key] = merged_terminal
    elif key in MANAGED_KEYS:
        merged[key] = value
    elif key not in merged:
        merged[key] = value

with open(merged_path, 'w') as f:
    yaml.dump(merged, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
PY
        then
            trap - RETURN
            rm -f "$resolved_template" "$merged"
            return 1
        fi
    fi

    if [[ -n "$merged" ]] && [[ -s "$merged" ]]; then
        if ! validate_yaml_file "$merged" "$label"; then
            trap - RETURN
            rm -f "$resolved_template" "$merged"
            return 1
        fi
        if cmp -s "$merged" "$target"; then
            log_skip "$label -> $target (already current)"
        elif [[ "$DRY_RUN" == "true" ]]; then
            log_change "$label -> $target (yaml merge, ws_hub=$ws_hub_path)"
        else
            mv -f "$merged" "$target"
            merged=""
            log_change "$label -> $target (yaml merge, ws_hub=$ws_hub_path)"
        fi
        trap - RETURN
        rm -f "$resolved_template" "$merged"
        return
    fi

    # Fallback: cmp + force (no python available for merge)
    if cmp -s "$resolved_template" "$target"; then
        log_skip "$label -> $target (already current)"
    elif [[ "$FORCE" == "true" ]]; then
        if [[ "$DRY_RUN" == "true" ]]; then
            log_change "$label -> $target (overwrite, ws_hub=$ws_hub_path)"
        else
            mv -f "$resolved_template" "$target"
            resolved_template=""
            log_change "$label -> $target (overwrite, ws_hub=$ws_hub_path)"
        fi
    else
        log_skip "$label -> $target (differs, use --force to overwrite)"
    fi

    trap - RETURN
    rm -f "$resolved_template" "$merged"
}

sync_hermes_plain_file() {
    local template="$1"
    local target="$2"
    local label="$3"
    local tmp=""

    trap 'rm -f "$tmp"' RETURN

    if [[ ! -f "$target" ]]; then
        if [[ "$DRY_RUN" == "true" ]]; then
            log_change "$label -> $target (create)"
        else
            ensure_parent_dir "$target"
            tmp="$(sync_make_target_tmp "$target")"
            cp "$template" "$tmp"
            mv -f "$tmp" "$target"
            tmp=""
            log_change "$label -> $target (create)"
        fi
        trap - RETURN
        rm -f "$tmp"
        return
    fi

    if cmp -s "$template" "$target"; then
        log_skip "$label -> $target (already current)"
    else
        if [[ "$DRY_RUN" == "true" ]]; then
            log_change "$label -> $target (update)"
        else
            ensure_parent_dir "$target"
            tmp="$(sync_make_target_tmp "$target")"
            cp "$template" "$tmp"
            mv -f "$tmp" "$target"
            tmp=""
            log_change "$label -> $target (update)"
        fi
    fi

    trap - RETURN
    rm -f "$tmp"
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
