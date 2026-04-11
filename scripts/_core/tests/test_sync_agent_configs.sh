#!/usr/bin/env bash
# test_sync_agent_configs.sh — regression tests for sync-agent-configs.sh
# Usage: bash scripts/_core/tests/test_sync_agent_configs.sh
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
SOURCE_SCRIPT="$REPO_ROOT/scripts/_core/sync-agent-configs.sh"
PASS=0
FAIL=0

pass() {
    echo "  PASS: $1"
    PASS=$((PASS + 1))
}

fail() {
    echo "  FAIL: $1"
    FAIL=$((FAIL + 1))
}

assert_file_exists() {
    local path="$1" label="$2"
    if [[ -f "$path" ]]; then
        pass "$label"
    else
        fail "$label"
    fi
}

assert_path_missing() {
    local path="$1" label="$2"
    if [[ ! -e "$path" ]]; then
        pass "$label"
    else
        fail "$label"
    fi
}

assert_toml_valid() {
    local file="$1" label="$2"
    if uv run python - "$file" <<'PY' >/dev/null 2>&1
import pathlib
import sys
import tomllib
path = pathlib.Path(sys.argv[1])
with path.open('rb') as fh:
    tomllib.load(fh)
PY
    then
        pass "$label"
    else
        fail "$label"
    fi
}

assert_managed_keys_root_only() {
    local label="$1"
    shift
    if uv run python - "$@" <<'PY' >/dev/null 2>&1
import pathlib
import sys
import tomllib

MANAGED_KEYS = {"model", "model_reasoning_effort"}

def walk(value, *, is_root=False):
    if isinstance(value, list):
        for child in value:
            walk(child, is_root=False)
        return
    if not isinstance(value, dict):
        return
    if not is_root:
        overlap = MANAGED_KEYS.intersection(value)
        if overlap:
            raise SystemExit(1)
    for child in value.values():
        walk(child, is_root=False)

for arg in sys.argv[1:]:
    path = pathlib.Path(arg)
    with path.open('rb') as fh:
        data = tomllib.load(fh)
    if data.get('model') != 'gpt-5.4':
        raise SystemExit(1)
    if data.get('model_reasoning_effort') != 'medium':
        raise SystemExit(1)
    walk(data, is_root=True)
PY
    then
        pass "$label"
    else
        fail "$label"
    fi
}

make_workspace() {
    local ws_root="$1"
    mkdir -p "$ws_root/scripts/_core" \
             "$ws_root/config/agents/claude" \
             "$ws_root/config/agents/codex" \
             "$ws_root/config/agents/gemini" \
             "$ws_root/.codex"

    cp "$SOURCE_SCRIPT" "$ws_root/scripts/_core/sync-agent-configs.sh"
    cat > "$ws_root/config/agents/claude/settings.json" <<'EOF'
{}
EOF
    cat > "$ws_root/config/agents/gemini/settings.json" <<'EOF'
{}
EOF
    cat > "$ws_root/config/agents/codex/config.toml" <<'EOF'
model = "gpt-5.4"
model_reasoning_effort = "medium"

[status_line]
enabled = true
items = ["model"]
EOF
}

run_sanitize_test() {
    local tmpdir ws_root home_root home_cfg repo_cfg
    tmpdir="$(mktemp -d)"
    ws_root="$tmpdir/ws"
    home_root="$tmpdir/home"
    home_cfg="$home_root/.codex/config.toml"
    repo_cfg="$ws_root/.codex/config.toml"

    make_workspace "$ws_root"
    mkdir -p "$home_root/.codex"

    cat > "$home_cfg" <<'EOF'
suppress_unstable_features_warning = true

[features]
js_repl = true
guardian_approval = true
model = "gpt-5.4"
model_reasoning_effort = "medium"

[[features.providers]]
model = "bad-nested"
EOF

    cat > "$repo_cfg" <<'EOF'
suppress_unstable_features_warning = true

[features]
js_repl = true
model = "gpt-5.4"
model_reasoning_effort = "medium"
EOF

    if HOME="$home_root" bash "$ws_root/scripts/_core/sync-agent-configs.sh" >/dev/null 2>&1; then
        pass "sanitize_non_root_managed_keys sync command completed"
    else
        fail "sanitize_non_root_managed_keys sync command completed"
    fi

    assert_toml_valid "$home_cfg" "sanitize_non_root_managed_keys home config remains valid TOML"
    assert_toml_valid "$repo_cfg" "sanitize_non_root_managed_keys repo config remains valid TOML"
    assert_managed_keys_root_only \
        "sanitize_non_root_managed_keys parsed TOML keeps managed keys only at root" \
        "$home_cfg" "$repo_cfg"

    rm -rf "$tmpdir"
}

run_multiline_string_preservation_test() {
    local tmpdir ws_root home_root home_cfg
    tmpdir="$(mktemp -d)"
    ws_root="$tmpdir/ws"
    home_root="$tmpdir/home"
    home_cfg="$home_root/.codex/config.toml"

    make_workspace "$ws_root"
    mkdir -p "$home_root/.codex"

    cat > "$home_cfg" <<'EOF'
[prompts]
text = """
hello
model = "should stay literal"
bye
"""
EOF

    if HOME="$home_root" bash "$ws_root/scripts/_core/sync-agent-configs.sh" >/dev/null 2>&1; then
        pass "multiline_string_preservation sync command completed"
    else
        fail "multiline_string_preservation sync command completed"
    fi

    assert_toml_valid "$home_cfg" "multiline_string_preservation remains valid TOML"
    if uv run python - "$home_cfg" <<'PY' >/dev/null 2>&1
import pathlib
import sys
import tomllib
with pathlib.Path(sys.argv[1]).open('rb') as fh:
    data = tomllib.load(fh)
if data.get('prompts', {}).get('text') != 'hello\nmodel = "should stay literal"\nbye\n':
    raise SystemExit(1)
PY
    then
        pass "multiline_string_preservation keeps literal model line inside string"
    else
        fail "multiline_string_preservation keeps literal model line inside string"
    fi

    rm -rf "$tmpdir"
}

run_inline_table_sanitization_test() {
    local tmpdir ws_root home_root home_cfg
    tmpdir="$(mktemp -d)"
    ws_root="$tmpdir/ws"
    home_root="$tmpdir/home"
    home_cfg="$home_root/.codex/config.toml"

    make_workspace "$ws_root"
    mkdir -p "$home_root/.codex"

    cat > "$home_cfg" <<'EOF'
[features]
js_repl = true
provider = { model = "nested-inline", keep = true }
EOF

    if HOME="$home_root" bash "$ws_root/scripts/_core/sync-agent-configs.sh" >/dev/null 2>&1; then
        pass "inline_table_sanitization sync command completed"
    else
        fail "inline_table_sanitization sync command completed"
    fi

    assert_toml_valid "$home_cfg" "inline_table_sanitization remains valid TOML"
    if uv run python - "$home_cfg" <<'PY' >/dev/null 2>&1
import pathlib
import sys
import tomllib
with pathlib.Path(sys.argv[1]).open('rb') as fh:
    data = tomllib.load(fh)
provider = data.get('features', {}).get('provider', {})
if provider.get('keep') is not True:
    raise SystemExit(1)
if 'model' in provider:
    raise SystemExit(1)
PY
    then
        pass "inline_table_sanitization removes managed key from inline table"
    else
        fail "inline_table_sanitization removes managed key from inline table"
    fi

    rm -rf "$tmpdir"
}

run_status_line_comment_test() {
    local tmpdir ws_root home_root home_cfg
    tmpdir="$(mktemp -d)"
    ws_root="$tmpdir/ws"
    home_root="$tmpdir/home"
    home_cfg="$home_root/.codex/config.toml"

    make_workspace "$ws_root"
    mkdir -p "$home_root/.codex"

    cat > "$home_cfg" <<'EOF'
suppress_unstable_features_warning = true

[status_line] # keep local comment style
enabled = false
items = ["cwd"]
EOF

    if HOME="$home_root" bash "$ws_root/scripts/_core/sync-agent-configs.sh" >/dev/null 2>&1; then
        pass "status_line_comment_header sync command completed"
    else
        fail "status_line_comment_header sync command completed"
    fi

    assert_toml_valid "$home_cfg" "status_line_comment_header remains valid TOML"
    if uv run python - "$home_cfg" <<'PY' >/dev/null 2>&1
import pathlib
import sys
import tomllib
with pathlib.Path(sys.argv[1]).open('rb') as fh:
    data = tomllib.load(fh)
status = data.get('status_line', {})
if status.get('enabled') is not True:
    raise SystemExit(1)
if status.get('items') != ['model']:
    raise SystemExit(1)
PY
    then
        pass "status_line_comment_header replaced managed section"
    else
        fail "status_line_comment_header replaced managed section"
    fi

    rm -rf "$tmpdir"
}

run_dry_run_side_effect_test() {
    local tmpdir ws_root home_root
    tmpdir="$(mktemp -d)"
    ws_root="$tmpdir/ws"
    home_root="$tmpdir/home"

    make_workspace "$ws_root"
    mkdir -p "$home_root"

    if HOME="$home_root" bash "$ws_root/scripts/_core/sync-agent-configs.sh" --dry-run >/dev/null 2>&1; then
        pass "dry_run command completed"
    else
        fail "dry_run command completed"
    fi

    assert_path_missing "$home_root/.codex" "dry_run does not create ~/.codex"
    assert_path_missing "$home_root/.claude" "dry_run does not create ~/.claude"
    assert_path_missing "$home_root/.gemini" "dry_run does not create ~/.gemini"
    assert_path_missing "$home_root/.hermes" "dry_run does not create ~/.hermes"

    rm -rf "$tmpdir"
}

run_invalid_template_atomicity_test() {
    local tmpdir ws_root home_root home_cfg tmp_area
    tmpdir="$(mktemp -d)"
    ws_root="$tmpdir/ws"
    home_root="$tmpdir/home"
    home_cfg="$home_root/.codex/config.toml"
    tmp_area="$tmpdir/tmp"

    make_workspace "$ws_root"
    mkdir -p "$home_root" "$tmp_area"
    cat > "$ws_root/config/agents/codex/config.toml" <<'EOF'
model = "gpt-5.4"
model_reasoning_effort = "medium"

[status_line]
enabled = true
items = ["model"]

[status_line]
enabled = false
items = ["cwd"]
EOF

    if TMPDIR="$tmp_area" HOME="$home_root" bash "$ws_root/scripts/_core/sync-agent-configs.sh" >/dev/null 2>&1; then
        fail "invalid_template create path should fail"
    else
        pass "invalid_template create path fails"
    fi

    assert_path_missing "$home_cfg" "invalid_template create path does not leave ~/.codex/config.toml behind"

    if find "$tmp_area" -mindepth 1 -type f ! -name 'uv-*.lock' -print -quit | grep -q .; then
        fail "invalid_template create path cleans up tmp files"
    else
        pass "invalid_template create path cleans up tmp files"
    fi

    rm -rf "$tmpdir"
}

echo "=== test_sync_agent_configs.sh ==="
run_sanitize_test
run_multiline_string_preservation_test
run_inline_table_sanitization_test
run_status_line_comment_test
run_dry_run_side_effect_test
run_invalid_template_atomicity_test

echo ""
echo "Results: ${PASS} PASS, ${FAIL} FAIL"
[[ $FAIL -eq 0 ]] && exit 0 || exit 1
