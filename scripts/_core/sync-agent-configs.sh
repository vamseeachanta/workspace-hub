#!/usr/bin/env bash
# Sync managed agent configs from workspace-hub templates into home directories.
# Usage: bash scripts/_core/sync-agent-configs.sh [--force] [--dry-run] [--machine <name>]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WS_HUB="$(cd "$SCRIPT_DIR/../.." && pwd)"

FORCE=false
DRY_RUN=false
MACHINE=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        --force) FORCE=true; shift ;;
        --dry-run) DRY_RUN=true; shift ;;
        --machine)
            if [[ $# -lt 2 ]]; then
                echo "Missing value for --machine" >&2
                exit 1
            fi
            MACHINE="$2"
            shift 2
            ;;
        --help|-h)
            cat <<'USAGE'
Usage: bash scripts/_core/sync-agent-configs.sh [--force] [--dry-run] [--machine <name>]

Options:
  --force      Overwrite plain-copy targets when merge is not possible
  --dry-run    Show planned actions without writing files
  --machine N  Resolve machine roots from config/workstations/registry.yaml
USAGE
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
    esac
done

CLAUDE_TEMPLATE="$WS_HUB/config/agents/claude/settings.json"
CODEX_TEMPLATE="$WS_HUB/config/agents/codex/config.toml"
GEMINI_TEMPLATE="$WS_HUB/config/agents/gemini/settings.json"
HERMES_TEMPLATE="$WS_HUB/config/agents/hermes/config.yaml.template"
# NOTE: ~/.hermes/SOUL.md is intentionally NOT synced here (#2864). It is a
# symlink owned solely by scripts/agents/install-soul-runtime.sh, which points
# it at the built runtime artifact config/agents/hermes/SOUL.runtime.md (NOT the
# delta config/agents/hermes/SOUL.md). A plain-file copy here would clobber that
# symlink nightly with the 4 KB delta, giving Hermes a gutted identity.

CLAUDE_TARGET="$HOME/.claude/settings.json"
CODEX_TARGET="$HOME/.codex/config.toml"
GEMINI_TARGET="$HOME/.gemini/settings.json"
HERMES_TARGET="$HOME/.hermes/config.yaml"

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

run_config_python() {
    if command -v uv >/dev/null 2>&1; then
        uv run --with pyyaml --no-project python "$@"
        return
    fi
    if command -v python3 >/dev/null 2>&1; then
        if python3 -c 'import yaml' >/dev/null 2>&1; then
            python3 "$@"
            return
        fi
        echo "[ERROR] python3 is available but PyYAML is missing, and uv is unavailable for agent config sync" >&2
        return 1
    fi
    echo "[ERROR] python3 or uv is required for agent config sync" >&2
    return 127
}

render_hermes_template() {
    local template="$1"
    local output_path="$2"
    local machine_name="$3"
    local ws_hub_path="$4"
    local tier1_repo_root="$5"

    if [[ "$ws_hub_path" == *$'\n'* || "$tier1_repo_root" == *$'\n'* ]]; then
        echo "[ERROR] machine root contains newline; refusing to render Hermes template" >&2
        return 1
    fi

    local registry_path="$WS_HUB/config/workstations/registry.yaml"

    WS_HUB_PATH="$ws_hub_path" TIER1_REPO_ROOT="$tier1_repo_root" MACHINE_NAME="$machine_name" REGISTRY_PATH="$registry_path" run_config_python - "$template" "$output_path" <<'PY'
import json, os
import pathlib
import re
import sys
import yaml

template_path = pathlib.Path(sys.argv[1])
output_path = pathlib.Path(sys.argv[2])
ws_hub = os.environ["WS_HUB_PATH"]
tier1 = os.environ["TIER1_REPO_ROOT"]
machine_name = os.environ["MACHINE_NAME"]
registry_path = pathlib.Path(os.environ["REGISTRY_PATH"])
if registry_path.exists():
    registry = yaml.safe_load(registry_path.read_text()) or {}
    repos = ((registry.get("machines") or {}).get(machine_name) or {}).get("repos") or []
else:
    repos = []
repo_skill_dirs = []
for repo in repos:
    if repo == "workspace-hub":
        continue
    path = pathlib.Path(tier1) / str(repo) / ".claude" / "skills"
    if path.exists() and any(path.rglob("SKILL.md")):
        repo_skill_dirs.append(f"- {json.dumps(str(path))}")
registry_repo_skill_dirs = "\n    ".join(repo_skill_dirs) if repo_skill_dirs else ""
rendered = (
    template_path.read_text()
    .replace("__WS_HUB_PATH__", ws_hub)
    .replace("__TIER1_REPO_ROOT__", tier1)
    .replace("__REGISTRY_REPO_SKILL_DIRS__", registry_repo_skill_dirs)
)
remaining = sorted(set(re.findall(r"__[A-Z_][A-Z0-9_]*__", rendered)))
if remaining:
    raise SystemExit(f"unresolved token(s): {', '.join(remaining)}")
stale = re.findall(re.escape(ws_hub) + r"/(?!\.claude/)[^\n]+/\.claude/skills", rendered)
if stale:
    raise SystemExit("stale nested workspace-hub skill path(s): " + ", ".join(stale))
output_path.write_text(rendered)
PY
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

    if run_config_python - "$target" <<'PY' >/dev/null
import pathlib
import sys
import yaml

with pathlib.Path(sys.argv[1]).open() as fh:
    yaml.safe_load(fh)
PY
    then
        return
    fi

    echo "[ERROR] YAML validation failed for $label -> $target" >&2
    return 1
}

read -r -d '' CODEX_TOML_MERGER <<'PY' || true
import json
import pathlib
import re
import sys
import tomllib

template_path, target_path, output_path = map(pathlib.Path, sys.argv[1:])
OWNED = {
    (): ("plan_mode_reasoning_effort", "personality", "web_search"),
    ("features",): ("default_mode_request_user_input", "goals", "multi_agent", "hooks"),
    ("agents",): ("enabled", "interrupt_message"),
    ("tui",): ("resume_cwd", "status_line"),
}


def flatten(value, prefix=()):
    paths = set()
    for key, child in value.items():
        path = prefix + (key,)
        if isinstance(child, dict):
            paths.update(flatten(child, path))
        else:
            paths.add(path)
    return paths


def encode(value):
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, str):
        return json.dumps(value)
    if isinstance(value, list):
        return "[" + ", ".join(encode(item) for item in value) + "]"
    raise TypeError(f"unsupported owned value: {value!r}")


def owned_lines(data, table):
    values = data
    for part in table:
        values = values[part]
    return [f"{key} = {encode(values[key])}\n" for key in OWNED[table]]


def basic_quote_escaped(line, pos):
    backslashes = 0
    while pos > backslashes and line[pos - backslashes - 1] == "\\":
        backslashes += 1
    return backslashes % 2 == 1


def scan_toml_line(line, quote, square, curly):
    pos = 0
    while pos < len(line):
        if quote in ('"""', "'''"):
            closes = line.startswith(quote, pos)
            if quote == '"""' and closes:
                closes = not basic_quote_escaped(line, pos)
            if closes:
                quote = None; pos += 3
            else:
                pos += 1
            continue
        char = line[pos]
        if quote:
            if char == quote and (quote == "'" or not basic_quote_escaped(line, pos)):
                quote = None
            pos += 1; continue
        if line.startswith('"""', pos) or line.startswith("'''", pos):
            quote = line[pos:pos + 3]; pos += 3; continue
        if char in ('"', "'"): quote = char
        elif char == '#': break
        elif char == '[': square += 1
        elif char == ']': square -= 1
        elif char == '{': curly += 1
        elif char == '}': curly -= 1
        pos += 1
    return quote, square, curly


def statement_end(lines, start):
    quote = None
    square = curly = 0
    for index in range(start, len(lines)):
        quote, square, curly = scan_toml_line(lines[index], quote, square, curly)
        if quote not in ('"""', "'''") and square == 0 and curly == 0:
            return index + 1
    return len(lines)


def statements(text):
    lines = text.splitlines(keepends=True)
    result = []
    index = 0
    while index < len(lines):
        end = statement_end(lines, index)
        result.append(lines[index:end])
        index = end
    return result


def header_path(value):
    path = []
    while isinstance(value, dict) and len(value) == 1:
        key, value = next(iter(value.items()))
        path.append(key)
    if isinstance(value, list) and len(value) == 1:
        value = value[0]
    if value != {}:
        raise ValueError("TOML table header structure is ambiguous")
    return tuple(path)


def header_kind(statement):
    if len(statement) != 1 or not statement[0].lstrip().startswith("["):
        return None, None
    kind = "array" if statement[0].lstrip().startswith("[[") else "normal"
    try:
        parsed = tomllib.loads(statement[0].rstrip("\r\n") + "\n")
    except tomllib.TOMLDecodeError as error:
        raise ValueError("unsupported valid TOML table header") from error
    return kind, header_path(parsed)


def leaf_path(value, prefix=()):
    for key, child in value.items():
        path = prefix + (key,)
        if isinstance(child, dict):
            return leaf_path(child, path)
        return path
    return None


def assignment_info(statement):
    line, quote, escape = statement[0], None, False
    for index, char in enumerate(line):
        if quote:
            if quote == '"' and escape: escape = False
            elif quote == '"' and char == "\\": escape = True
            elif char == quote: quote = None
        elif char in ('"', "'"): quote = char
        elif char == "=":
            token = line[:index].strip()
            try: path = leaf_path(tomllib.loads(f"{token} = 0"))
            except tomllib.TOMLDecodeError: return None, None
            return token, path
        elif char == "#": return None, None
    return None, None


def line_comment(line):
    quote = None
    escape = False
    for index, char in enumerate(line.rstrip("\r\n")):
        if quote:
            if quote == '"' and escape:
                escape = False
            elif quote == '"' and char == "\\":
                escape = True
            elif char == quote:
                quote = None
        elif char in ('"', "'"):
            quote = char
        elif char == "#":
            return line[index:].rstrip("\r\n")
    return None


def render_assignment(token, value, statement):
    indent = re.match(r'^\s*', statement[0]).group(0)
    comments = [(index, line_comment(line)) for index, line in enumerate(statement)]
    comments = [(index, comment) for index, comment in comments if comment]
    suffix = ""
    if comments and comments[-1][0] == len(statement) - 1:
        suffix = " " + comments.pop()[1]
    preserved = [f"{indent}{comment}\n" for _, comment in comments]
    return preserved + [f"{indent}{token} = {encode(value)}{suffix}\n"]


def split_inline(text):
    parts, start, braces, brackets = [], 0, 0, 0
    quote = None
    escape = False
    for index, char in enumerate(text):
        if quote:
            if quote == '"' and escape: escape = False
            elif quote == '"' and char == "\\": escape = True
            elif char == quote: quote = None
            continue
        if char in ('"', "'"): quote = char
        elif char == "{": braces += 1
        elif char == "}": braces -= 1
        elif char == "[": brackets += 1
        elif char == "]": brackets -= 1
        elif char == "," and braces == 0 and brackets == 0:
            parts.append(text[start:index]); start = index + 1
    parts.append(text[start:])
    return parts


def matching_brace(text, opening):
    depth, quote, escape = 0, None, False
    for index in range(opening, len(text)):
        char = text[index]
        if quote:
            if quote == '"' and escape: escape = False
            elif quote == '"' and char == "\\": escape = True
            elif char == quote: quote = None
            continue
        if char in ('"', "'"): quote = char
        elif char == "#": break
        elif char == "{": depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0: return index
    raise ValueError("inline table closing brace not found")


def merge_inline(statement, table, canonical):
    text = "".join(statement)
    opening = text.find("{")
    closing = matching_brace(text, opening)
    entries, seen = [], set()
    values = canonical[table]
    for raw in split_inline(text[opening + 1:closing]):
        entry = raw.strip()
        token, path = assignment_info([entry])
        if path and len(path) == 1 and path[0] in OWNED[(table,)]:
            key = path[0]; seen.add(key)
            entries.append(f"{token} = {encode(values[key])}")
        elif entry:
            entries.append(entry)
    entries.extend(f"{key} = {encode(values[key])}" for key in OWNED[(table,)] if key not in seen)
    return [text[:opening] + "{ " + ", ".join(entries) + " }" + text[closing + 1:]]


def inspect_layout(parts, local):
    modes, seen = {}, {table: set() for table in OWNED}
    context = ()
    skip_legacy = False
    for statement in parts:
        kind, path = header_kind(statement)
        if kind:
            context = path if kind == "normal" else ("array",) + path
            skip_legacy = kind == "normal" and path == ("status_line",)
            if kind == "normal" and context in OWNED:
                modes[context] = "normal"
            continue
        token, path = assignment_info(statement)
        if skip_legacy or not path:
            continue
        semantic_path = context + path
        if semantic_path[:-1] in OWNED and semantic_path[-1] in OWNED[semantic_path[:-1]]:
            seen[semantic_path[:-1]].add(semantic_path[-1])
        if (context == () and len(path) == 1 and path in OWNED
                and isinstance(local.get(path[0]), dict)):
            modes[path] = "inline"
        if context == () and len(path) > 1 and path[:1] in OWNED:
            modes[path[:1]] = "dotted"
    return modes, seen


def merge_text(text, canonical, local):
    parts = statements(text)
    modes, seen = inspect_layout(parts, local)
    output = [line for key, line in zip(OWNED[()], owned_lines(canonical, ())) if key not in seen[()]]
    for table, mode in modes.items():
        if table and mode == "dotted":
            output.extend(f"{table[0]}.{key} = {encode(canonical[table[0]][key])}\n"
                          for key in OWNED[table] if key not in seen[table])
    context, skip_legacy = (), False
    for statement in parts:
        kind, path = header_kind(statement)
        if kind:
            context = path if kind == "normal" else ("array",) + path
            skip_legacy = kind == "normal" and path == ("status_line",)
            if skip_legacy: continue
            output.extend(statement)
            if context in OWNED and modes.get(context) == "normal":
                output.extend(line for key, line in zip(OWNED[context], owned_lines(canonical, context))
                              if key not in seen[context])
            continue
        if skip_legacy: continue
        token, assignment_path = assignment_info(statement)
        if context == () and assignment_path in OWNED and modes.get(assignment_path) == "inline":
            output.extend(merge_inline(statement, assignment_path[0], canonical)); continue
        semantic_path = context + assignment_path if assignment_path else ()
        if semantic_path and semantic_path[:-1] in OWNED and semantic_path[-1] in OWNED[semantic_path[:-1]]:
            table, key = semantic_path[:-1], semantic_path[-1]
            value = canonical[table[0]][key] if table else canonical[key]
            output.extend(render_assignment(token, value, statement))
        else:
            output.extend(statement)
    for table in (("features",), ("agents",), ("tui",)):
        if table not in modes:
            output.extend(["\n", f"[{table[0]}]\n", *owned_lines(canonical, table)])
    return "".join(output)


def validate_local_shapes(local):
    for table in (("features",), ("agents",), ("tui",)):
        if table[0] in local and not isinstance(local[table[0]], dict):
            raise SystemExit(f"incompatible owned root shape: {table[0]}")


with template_path.open("rb") as fh:
    canonical = tomllib.load(fh)
with target_path.open("rb") as fh:
    local = tomllib.load(fh)
expected_paths = {table + (key,) for table, keys in OWNED.items() for key in keys}
if flatten(canonical) != expected_paths:
    raise SystemExit("canonical Codex config does not match the owned-key contract")
validate_local_shapes(local)
merged = merge_text(target_path.read_text(), canonical, local)
tomllib.loads(merged)
output_path.write_text(merged)
PY

merge_codex_toml() {
    local template="$1"
    local target="$2"
    local output="$3"
    if ! command -v uv >/dev/null 2>&1; then
        echo "[ERROR] uv is required for Codex TOML sync" >&2
        return 1
    fi
    uv run --no-project python - "$template" "$target" "$output" <<<"$CODEX_TOML_MERGER"
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
    local tmp_new=""

    trap 'rm -f "${tmp_new:-}"' RETURN

    if [[ ! -f "$target" ]]; then
        if [[ "$DRY_RUN" == "true" ]]; then
            tmp_new="$(mktemp)"
            merge_codex_toml "$template" "$template" "$tmp_new"
            log_change "$label -> $target (create)"
            trap - RETURN
            rm -f "$tmp_new"
            return
        fi
        ensure_parent_dir "$target"
        tmp_new="$(sync_make_target_tmp "$target")"
        merge_codex_toml "$template" "$template" "$tmp_new"
        mv -f "$tmp_new" "$target"
        tmp_new=""
        log_change "$label -> $target (create)"
        trap - RETURN
        return
    fi

    if [[ "$DRY_RUN" == "true" ]]; then
        tmp_new="$(mktemp)"
    else
        tmp_new="$(sync_make_target_tmp "$target")"
    fi
    merge_codex_toml "$template" "$target" "$tmp_new"

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
    rm -f "$tmp_new"
}

resolve_machine_roots() {
    # Prints machine name, workspace_root, and tier1_repo_root separated by tabs. Registry is authoritative.
    local registry="$WS_HUB/config/workstations/registry.yaml"
    local harness="$WS_HUB/scripts/readiness/harness-config.yaml"
    MACHINE="$MACHINE" run_config_python - "$registry" "$harness" <<'PY'
import os, pathlib, re, socket, sys, yaml
registry_path, harness_path = sys.argv[1], sys.argv[2]
requested = os.environ.get("MACHINE") or ""
host = socket.gethostname().split(".")[0].lower()

if os.path.exists(registry_path):
    with open(registry_path) as f:
        machines = (yaml.safe_load(f) or {}).get("machines") or {}
    harness_workstations = {}
    if os.path.exists(harness_path):
        with open(harness_path) as f:
            harness_workstations = (yaml.safe_load(f) or {}).get("workstations") or {}
        for candidate, cfg in machines.items():
            harness_cfg = harness_workstations.get(candidate) or {}
            h_root = harness_cfg.get("ws_hub_path")
            r_root = cfg.get("workspace_root")
            if h_root and r_root and str(h_root) != str(r_root):
                raise SystemExit(f"registry/harness workspace_root divergence for {candidate}: {r_root} != {h_root}")
    # PRIVATE-TIER identity — reusing the EXISTING mechanism (#3571), not a new one.
    #
    # This repo is PUBLIC, so real hostnames were removed from registry.yaml's
    # `hostname_aliases`. That field was load-bearing: the `else` branch below
    # resolves a machine by matching socket.gethostname() against it, and the
    # nightly cron (scripts/cron/harness-update.sh:346) invokes this script with
    # NO explicit --machine. Without a replacement the unknown-host branch fires,
    # GUESSES a workspace root, warns, and exits 0 — and harness-update.sh pipes
    # this script through `grep -i hermes`, discarding the warning. Silent
    # nightly degradation, indistinguishable from success.
    #
    # `scripts/readiness/lib/machine-identity.sh` already solves exactly this:
    # boxes whose OS hostname must never appear in a public repo declare their
    # fleet identity in an off-repo, gitignored file.
    #
    #   ~/.config/workspace-hub/machine-identity.yaml
    #   override: WORKSPACE_HUB_MACHINE_IDENTITY
    #
    # Reused rather than reinvented. A second private-tier host map would be a
    # second source of truth for one fact — the defect this epic exists to remove.
    #
    # Same contract as its resolve_identity_file(): absent file falls through;
    # malformed or FOREIGN fails loud, never falls through, because a bad file
    # silently minting the wrong machine is worse than no file at all.
    # Diagnostics omit hostname VALUES — this stderr can reach tracked logs.
    def identity_machine():
        path = os.environ.get("WORKSPACE_HUB_MACHINE_IDENTITY") or os.path.join(
            os.path.expanduser("~"), ".config", "workspace-hub",
            "machine-identity.yaml")
        if not os.path.exists(path):
            return None
        with open(path) as fh:
            data = yaml.safe_load(fh) or {}
        label = str(data.get("machine") or "").strip()
        if not label:
            raise SystemExit(
                f"machine-identity: {path} lacks the required 'machine:' key")
        # Validated against the REGISTRY, deliberately, rather than against a
        # copied label list. machine-identity.sh already notes that its
        # PowerShell mirror duplicates KNOWN_MACHINE_LABELS and needs a test to
        # keep the two identical; a third copy would need a third such test.
        if label not in machines:
            raise SystemExit(
                f"machine-identity: label in {path} is not a machine in the registry")
        expected = str(data.get("expected_hostname") or "").strip().lower()
        if expected and expected != host:
            raise SystemExit(
                f"machine-identity: expected_hostname in {path} does not match "
                f"this box — refusing a copied identity file")
        return label

    def machine_aliases(candidate, cfg):
        aliases = [str(candidate), str(cfg.get("hostname") or "")]
        aliases += [str(a) for a in (cfg.get("hostname_aliases") or [])]
        return [alias.split(".")[0].lower() for alias in aliases if alias]
    if requested:
        requested_key = requested.split(".")[0].lower()
        name = None
        for candidate, cfg in machines.items():
            if requested_key in machine_aliases(candidate, cfg):
                name = candidate
                break
        if name is None:
            raise SystemExit(f"unknown machine: {requested}")
    else:
        name = None
        for candidate, cfg in machines.items():
            if host in machine_aliases(candidate, cfg):
                name = candidate
                break
        if name is None:
            # Precedence matches machine-identity.sh: explicit > public map >
            # identity file > fail. Consulted only AFTER the registry, so the
            # off-repo file can never override a correctly-mapped host — it
            # exists solely for hostnames the public map must not know.
            name = identity_machine()
        if name is None:
            name = f"local-fallback-{host}"
            workspace_root = str(pathlib.Path(registry_path).resolve().parents[2])
            tier1_repo_root = str(pathlib.Path(workspace_root).parent)
            print(f"[WARN] unknown machine for hostname {host}; falling back to local workspace {workspace_root}", file=sys.stderr)
            print(f"{name}\t{workspace_root}\t{tier1_repo_root}")
            raise SystemExit(0)
    cfg = machines[name]
    workspace_root = cfg.get("workspace_root")
    tier1_repo_root = cfg.get("tier1_repo_root")
    if cfg.get("repo_layout") == "sibling" and (not workspace_root or not tier1_repo_root):
        raise SystemExit(f"machine {name} missing workspace_root/tier1_repo_root for sibling layout")
else:
    if not os.path.exists(harness_path):
        raise SystemExit(f"missing registry and harness config: {registry_path}, {harness_path}")
    with open(harness_path) as f:
        workstations = (yaml.safe_load(f) or {}).get("workstations") or {}
    name = requested or host
    cfg = workstations.get(name) or {}
    if not cfg and not requested:
        for candidate, candidate_cfg in workstations.items():
            if str(candidate).split(".")[0].lower() == host:
                name = candidate
                cfg = candidate_cfg or {}
                break
    if not cfg:
        raise SystemExit(f"unknown machine: {name}")
    workspace_root = cfg.get("workspace_root") or cfg.get("ws_hub_path")
    tier1_repo_root = cfg.get("tier1_repo_root")
if not workspace_root:
    raise SystemExit(f"machine {name} missing workspace_root")
if not tier1_repo_root:
    workspace_text = str(workspace_root).rstrip('/\\')
    slash = max(workspace_text.rfind('/'), workspace_text.rfind('\\'))
    if slash <= 0:
        raise SystemExit(f"machine {name} missing tier1_repo_root and cannot derive parent from workspace_root: {workspace_root}")
    tier1_repo_root = workspace_text[:slash]
    if re.match(r"^[A-Za-z]:$", tier1_repo_root):
        tier1_repo_root += "\\"
if os.path.exists(registry_path) and os.path.exists(harness_path):
    with open(harness_path) as f:
        harness = ((yaml.safe_load(f) or {}).get("workstations") or {}).get(name) or {}
    h_root = harness.get("ws_hub_path")
    if h_root and str(h_root) != str(workspace_root):
        raise SystemExit(f"registry/harness workspace_root divergence for {name}: {workspace_root} != {h_root}")
print(f"{name}\t{workspace_root}\t{tier1_repo_root}")
PY
}

resolve_ws_hub_path() {
    resolve_machine_roots | cut -f2
}

resolve_tier1_repo_root() {
    resolve_machine_roots | cut -f3
}

sync_hermes_yaml_config() {
    local template="$1"
    local target="$2"
    local label="$3"
    local ws_hub_path
    local tier1_repo_root
    local roots
    local resolved_template=""
    local merged=""

    trap 'rm -f "$resolved_template" "$merged"' RETURN

    local machine_name
    roots="$(resolve_machine_roots)"
    machine_name="$(printf '%s\n' "$roots" | cut -f1)"
    ws_hub_path="$(printf '%s\n' "$roots" | cut -f2)"
    tier1_repo_root="$(printf '%s\n' "$roots" | cut -f3)"

    if [[ "$DRY_RUN" != "true" ]]; then
        ensure_parent_dir "$target"
        resolved_template="$(sync_make_target_tmp "$target")"
    else
        resolved_template="$(mktemp)"
    fi

    if ! render_hermes_template "$template" "$resolved_template" "$machine_name" "$ws_hub_path" "$tier1_repo_root"; then
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
            log_change "$label -> $target (create, ws_hub=$ws_hub_path, tier1_repo_root=$tier1_repo_root)"
        else
            mv -f "$resolved_template" "$target"
            resolved_template=""
            log_change "$label -> $target (create, ws_hub=$ws_hub_path, tier1_repo_root=$tier1_repo_root)"
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

    if ! run_config_python - "$target" "$resolved_template" "$merged" <<'PY' 2>/dev/null
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

# NOTE (#2864): no longer called — the Hermes SOUL.md sync was removed because it
# clobbered install-soul-runtime.sh's symlink. RETAINED intentionally: its
# definition line is a text anchor used by
# tests/readiness/test_sync_agent_configs_pyyaml_fallback.py to delimit the
# sync_hermes_yaml_config body. Do not delete without updating that test.
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
    # Repo-local Codex files own their model selection and remain untouched.
    # The fleet-owned baseline applies only to the user-level Codex config.
    return
}

echo "=== Syncing Agent Configs ==="
echo "Workspace: $WS_HUB"
echo "Mode: force=$FORCE dry_run=$DRY_RUN"
echo

sync_json_merge "$CLAUDE_TEMPLATE" "$CLAUDE_TARGET" "Claude settings"
sync_codex_managed_config "$CODEX_TEMPLATE" "$CODEX_TARGET" "Codex config"
sync_json_merge "$GEMINI_TEMPLATE" "$GEMINI_TARGET" "Gemini settings"
sync_repo_codex_configs "$WS_HUB"

# Hermes — sync config.yaml only. ~/.hermes/SOUL.md is deliberately NOT synced
# here (#2864): it is a symlink owned by scripts/agents/install-soul-runtime.sh
# (→ config/agents/hermes/SOUL.runtime.md). harness-update.sh re-runs that
# installer so the symlink self-heals; copying the delta here would clobber it.
if [[ -f "$HERMES_TEMPLATE" ]]; then
    sync_hermes_yaml_config "$HERMES_TEMPLATE" "$HERMES_TARGET" "Hermes config"
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
    if [[ -d "$CLAUDE_MEM_TARGET" ]]; then
        EXISTING_COUNT=$(find "$CLAUDE_MEM_TARGET" -maxdepth 1 -type f -name '*.md' | wc -l)
    else
        EXISTING_COUNT=0
    fi
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
