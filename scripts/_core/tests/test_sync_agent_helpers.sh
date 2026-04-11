#!/usr/bin/env bash
# test_sync_agent_helpers.sh — regression tests for non-Codex sync helpers
# Usage: bash scripts/_core/tests/test_sync_agent_helpers.sh
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

assert_path_missing() {
    local path="$1" label="$2"
    if [[ ! -e "$path" ]]; then
        pass "$label"
    else
        fail "$label"
    fi
}

make_workspace() {
    local ws_root="$1"
    mkdir -p "$ws_root/scripts/_core" \
             "$ws_root/scripts/readiness" \
             "$ws_root/config/agents/claude" \
             "$ws_root/config/agents/codex" \
             "$ws_root/config/agents/gemini" \
             "$ws_root/config/agents/hermes"

    cp "$SOURCE_SCRIPT" "$ws_root/scripts/_core/sync-agent-configs.sh"

    cat > "$ws_root/scripts/readiness/harness-config.yaml" <<EOF
workstations:
  $(hostname -s):
    ws_hub_path: $ws_root
EOF

    cat > "$ws_root/config/agents/claude/settings.json" <<'EOF'
{
  "statusLine": {
    "type": "command"
  }
}
EOF

    cat > "$ws_root/config/agents/gemini/settings.json" <<'EOF'
{
  "security": {
    "auth": {
      "selectedType": "oauth-personal"
    }
  }
}
EOF

    cat > "$ws_root/config/agents/codex/config.toml" <<'EOF'
model = "gpt-5.4"
model_reasoning_effort = "medium"

[status_line]
enabled = true
items = ["model"]
EOF

    cat > "$ws_root/config/agents/hermes/config.yaml.template" <<'EOF'
model:
  default: gpt-5.4
  provider: openai-codex
terminal:
  backend: local
  cwd: .
  timeout: 180
skills:
  external_dirs:
    - __WS_HUB_PATH__/.claude/skills
EOF

    cat > "$ws_root/config/agents/hermes/SOUL.md" <<'EOF'
# Hermes Soul
EOF
}

run_hermes_placeholder_and_terminal_test() {
    local tmpdir ws_root home_root hermes_cfg
    tmpdir="$(mktemp -d)"
    ws_root="$tmpdir/ws&hub"
    home_root="$tmpdir/home"
    hermes_cfg="$home_root/.hermes/config.yaml"

    make_workspace "$ws_root"
    mkdir -p "$home_root/.hermes"

    cat > "$hermes_cfg" <<'EOF'
terminal:
  backend: remote
  cwd: /custom/path
  timeout: 999
EOF

    if HOME="$home_root" bash "$ws_root/scripts/_core/sync-agent-configs.sh" >/dev/null 2>&1; then
        pass "hermes_placeholder_and_terminal sync completed"
    else
        fail "hermes_placeholder_and_terminal sync completed"
    fi

    if python3 - "$hermes_cfg" "$ws_root" <<'PY' >/dev/null 2>&1
import pathlib
import sys
import yaml
cfg_path = pathlib.Path(sys.argv[1])
ws_root = sys.argv[2]
with cfg_path.open() as fh:
    data = yaml.safe_load(fh)
terminal = data.get('terminal', {})
if terminal.get('backend') != 'remote':
    raise SystemExit(1)
if terminal.get('cwd') != '/custom/path':
    raise SystemExit(1)
if terminal.get('timeout') != 180:
    raise SystemExit(1)
skills = data.get('skills', {}).get('external_dirs', [])
expected = f"{ws_root}/.claude/skills"
if expected not in skills:
    raise SystemExit(1)
PY
    then
        pass "hermes_placeholder_and_terminal preserves backend/cwd and expands ws path literally"
    else
        fail "hermes_placeholder_and_terminal preserves backend/cwd and expands ws path literally"
    fi

    rm -rf "$tmpdir"
}

run_invalid_json_create_test() {
    local tmpdir ws_root home_root claude_cfg
    tmpdir="$(mktemp -d)"
    ws_root="$tmpdir/ws"
    home_root="$tmpdir/home"
    claude_cfg="$home_root/.claude/settings.json"

    make_workspace "$ws_root"
    mkdir -p "$home_root"
    printf '{invalid\n' > "$ws_root/config/agents/claude/settings.json"

    if HOME="$home_root" bash "$ws_root/scripts/_core/sync-agent-configs.sh" >/dev/null 2>&1; then
        fail "invalid_json_create should fail"
    else
        pass "invalid_json_create fails"
    fi

    assert_path_missing "$claude_cfg" "invalid_json_create leaves no ~/.claude/settings.json"
    rm -rf "$tmpdir"
}

run_invalid_json_create_without_jq_test() {
    local tmpdir ws_root home_root claude_cfg fake_bin path_without_jq
    tmpdir="$(mktemp -d)"
    ws_root="$tmpdir/ws"
    home_root="$tmpdir/home"
    claude_cfg="$home_root/.claude/settings.json"
    fake_bin="$tmpdir/fake-bin"

    make_workspace "$ws_root"
    mkdir -p "$home_root" "$fake_bin"
    printf '{invalid\n' > "$ws_root/config/agents/claude/settings.json"

    path_without_jq="$(python3 - <<'PY'
import os
parts = [p for p in os.environ['PATH'].split(':') if p and not os.path.exists(os.path.join(p, 'jq'))]
print(':'.join(parts))
PY
)"

    if HOME="$home_root" PATH="$fake_bin:${path_without_jq}" bash "$ws_root/scripts/_core/sync-agent-configs.sh" >/dev/null 2>&1; then
        fail "invalid_json_create_without_jq should fail"
    else
        pass "invalid_json_create_without_jq fails"
    fi

    assert_path_missing "$claude_cfg" "invalid_json_create_without_jq leaves no ~/.claude/settings.json"
    rm -rf "$tmpdir"
}

run_invalid_yaml_create_test() {
    local tmpdir ws_root home_root hermes_cfg
    tmpdir="$(mktemp -d)"
    ws_root="$tmpdir/ws"
    home_root="$tmpdir/home"
    hermes_cfg="$home_root/.hermes/config.yaml"

    make_workspace "$ws_root"
    mkdir -p "$home_root"
    printf 'skills: [\n' > "$ws_root/config/agents/hermes/config.yaml.template"

    if HOME="$home_root" bash "$ws_root/scripts/_core/sync-agent-configs.sh" >/dev/null 2>&1; then
        fail "invalid_yaml_create should fail"
    else
        pass "invalid_yaml_create fails"
    fi

    assert_path_missing "$hermes_cfg" "invalid_yaml_create leaves no ~/.hermes/config.yaml"
    rm -rf "$tmpdir"
}

run_invalid_json_update_cleanup_test() {
    local tmpdir ws_root home_root claude_cfg claude_dir
    tmpdir="$(mktemp -d)"
    ws_root="$tmpdir/ws"
    home_root="$tmpdir/home"
    claude_cfg="$home_root/.claude/settings.json"
    claude_dir="$home_root/.claude"

    make_workspace "$ws_root"
    mkdir -p "$claude_dir"
    cat > "$claude_cfg" <<'EOF'
{
  "ok": true
}
EOF
    printf '{invalid\n' > "$ws_root/config/agents/claude/settings.json"

    if HOME="$home_root" bash "$ws_root/scripts/_core/sync-agent-configs.sh" >/dev/null 2>&1; then
        fail "invalid_json_update_cleanup should fail"
    else
        pass "invalid_json_update_cleanup fails"
    fi

    if python3 - "$claude_cfg" <<'PY' >/dev/null 2>&1
import json
import pathlib
import sys
with pathlib.Path(sys.argv[1]).open() as fh:
    data = json.load(fh)
if data.get('ok') is not True:
    raise SystemExit(1)
PY
    then
        pass "invalid_json_update_cleanup preserves existing target"
    else
        fail "invalid_json_update_cleanup preserves existing target"
    fi

    if find "$claude_dir" -maxdepth 1 -type f -name '.settings.json.tmp.*' -print -quit | grep -q .; then
        fail "invalid_json_update_cleanup removes temp files"
    else
        pass "invalid_json_update_cleanup removes temp files"
    fi

    rm -rf "$tmpdir"
}

run_python3_fallback_to_uv_test() {
    local tmpdir ws_root home_root fake_bin hermes_cfg uv_path
    tmpdir="$(mktemp -d)"
    ws_root="$tmpdir/ws"
    home_root="$tmpdir/home"
    fake_bin="$tmpdir/fake-bin"
    hermes_cfg="$home_root/.hermes/config.yaml"
    uv_path="$(command -v uv)"

    make_workspace "$ws_root"
    mkdir -p "$home_root/.hermes" "$fake_bin"

    cat > "$fake_bin/python3" <<'EOF'
#!/usr/bin/env bash
exit 1
EOF
    chmod +x "$fake_bin/python3"

    cat > "$hermes_cfg" <<'EOF'
terminal:
  backend: remote
  cwd: /custom/path
EOF

    if HOME="$home_root" PATH="$fake_bin:$(dirname "$uv_path"):/usr/bin:/bin" bash "$ws_root/scripts/_core/sync-agent-configs.sh" >/dev/null 2>&1; then
        pass "python3_fallback_to_uv sync completed"
    else
        fail "python3_fallback_to_uv sync completed"
    fi

    if python3 - "$hermes_cfg" "$ws_root" <<'PY' >/dev/null 2>&1
import pathlib
import sys
import yaml
cfg_path = pathlib.Path(sys.argv[1])
ws_root = sys.argv[2]
with cfg_path.open() as fh:
    data = yaml.safe_load(fh)
if data.get('terminal', {}).get('backend') != 'remote':
    raise SystemExit(1)
expected = f"{ws_root}/.claude/skills"
if expected not in data.get('skills', {}).get('external_dirs', []):
    raise SystemExit(1)
PY
    then
        pass "python3_fallback_to_uv uses uv-backed Hermes processing"
    else
        fail "python3_fallback_to_uv uses uv-backed Hermes processing"
    fi

    rm -rf "$tmpdir"
}

echo "=== test_sync_agent_helpers.sh ==="
run_hermes_placeholder_and_terminal_test
run_invalid_json_create_test
run_invalid_json_create_without_jq_test
run_invalid_yaml_create_test
run_invalid_json_update_cleanup_test
run_python3_fallback_to_uv_test

echo ""
echo "Results: ${PASS} PASS, ${FAIL} FAIL"
[[ $FAIL -eq 0 ]] && exit 0 || exit 1
