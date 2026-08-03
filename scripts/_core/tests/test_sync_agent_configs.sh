#!/usr/bin/env bash
# test_sync_agent_configs.sh — behavioral tests for Codex config synchronization
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
SOURCE_SCRIPT="$REPO_ROOT/scripts/_core/sync-agent-configs.sh"
PASS=0
FAIL=0

pass() { echo "  PASS: $1"; PASS=$((PASS + 1)); }
fail() { echo "  FAIL: $1"; FAIL=$((FAIL + 1)); }

assert_missing() {
    if [[ ! -e "$1" ]]; then pass "$2"; else fail "$2"; fi
}

assert_same() {
    if cmp -s "$1" "$2"; then pass "$3"; else fail "$3"; fi
}

make_workspace() {
    local ws_root="$1"
    mkdir -p "$ws_root/scripts/_core" "$ws_root/config/agents/"{claude,codex,gemini} "$ws_root/.codex"
    cp "$SOURCE_SCRIPT" "$ws_root/scripts/_core/sync-agent-configs.sh"
    cp "$REPO_ROOT/config/agents/codex/config.toml" "$ws_root/config/agents/codex/config.toml"
    printf '{}\n' > "$ws_root/config/agents/claude/settings.json"
    printf '{}\n' > "$ws_root/config/agents/gemini/settings.json"
}

assert_merged_semantics() {
    local file="$1" label="$2"
    if uv run python - "$file" <<'PY' >/dev/null 2>&1
import pathlib
import sys
import tomllib

with pathlib.Path(sys.argv[1]).open("rb") as fh:
    actual = tomllib.load(fh)

owned = {
    "plan_mode_reasoning_effort": "high",
    "personality": "pragmatic",
    "web_search": "live",
    "features": {
        "default_mode_request_user_input": True,
        "goals": True,
        "multi_agent": True,
        "hooks": True,
    },
    "agents": {"enabled": True, "interrupt_message": True},
    "tui": {
        "resume_cwd": "session",
        "status_line": [
            "model-with-reasoning", "context-remaining", "current-dir",
            "five-hour-limit", "weekly-limit",
        ],
    },
}
for key in ("plan_mode_reasoning_effort", "personality", "web_search"):
    if actual.get(key) != owned[key]:
        raise SystemExit(f"wrong owned root key: {key}")
for table, expected in (("features", owned["features"]), ("agents", owned["agents"]), ("tui", owned["tui"])):
    for key, value in expected.items():
        if actual.get(table, {}).get(key) != value:
            raise SystemExit(f"wrong owned nested key: {table}.{key}")

expected_unowned = {
    "model": "local-preview-model",
    "model_reasoning_effort": "xhigh",
    "notify": ["/opt/Local Tools/notify me"],
    "features.js_repl": True,
    "agents.max_threads": 7,
    "tui.animations": False,
    "projects./mnt/Repos With Spaces/workspace-hub.trust_level": "trusted",
    "mcp_servers.docs.command": "/opt/MCP Tools/docs server",
    "mcp_servers.docs.args": ["--root", "/mnt/Docs With Spaces"],
    "plugins.sample.enabled": False,
    "plugins.sample.options.model": "nested-local-model",
    "plugins.sample.options.keep": True,
    "prompts.text": "hello\nmodel = \"inside multiline\"\nbye\n",
}
paths = {
    "model": actual.get("model"),
    "model_reasoning_effort": actual.get("model_reasoning_effort"),
    "notify": actual.get("notify"),
    "features.js_repl": actual.get("features", {}).get("js_repl"),
    "agents.max_threads": actual.get("agents", {}).get("max_threads"),
    "tui.animations": actual.get("tui", {}).get("animations"),
    "projects./mnt/Repos With Spaces/workspace-hub.trust_level": actual.get("projects", {}).get("/mnt/Repos With Spaces/workspace-hub", {}).get("trust_level"),
    "mcp_servers.docs.command": actual.get("mcp_servers", {}).get("docs", {}).get("command"),
    "mcp_servers.docs.args": actual.get("mcp_servers", {}).get("docs", {}).get("args"),
    "plugins.sample.enabled": actual.get("plugins", {}).get("sample", {}).get("enabled"),
    "plugins.sample.options.model": actual.get("plugins", {}).get("sample", {}).get("options", {}).get("model"),
    "plugins.sample.options.keep": actual.get("plugins", {}).get("sample", {}).get("options", {}).get("keep"),
    "prompts.text": actual.get("prompts", {}).get("text"),
}
if paths != expected_unowned:
    raise SystemExit(f"unowned values changed: {paths!r}")
if "status_line" in actual:
    raise SystemExit("legacy status_line table survived")
PY
    then
        pass "$label"
    else
        fail "$label"
    fi
}

write_complex_local_config() {
    cat > "$1" <<'EOF'
# keep this local root comment
model = "local-preview-model"
model_reasoning_effort = "xhigh"
notify = ["/opt/Local Tools/notify me"]
plan_mode_reasoning_effort = "low"
personality = "friendly"
web_search = "disabled"

[features]
js_repl = true # keep this local feature comment
default_mode_request_user_input = false
goals = false
multi_agent = false
hooks = false

[agents]
max_threads = 7
enabled = false
interrupt_message = false

[tui]
animations = false # unrelated TUI sibling
resume_cwd = "root"
status_line = ["current-dir"]

[projects."/mnt/Repos With Spaces/workspace-hub"]
trust_level = "trusted"

[mcp_servers.docs]
command = "/opt/MCP Tools/docs server"
args = ["--root", "/mnt/Docs With Spaces"]

[plugins.sample]
enabled = false
options = { model = "nested-local-model", keep = true }

[prompts]
text = """
hello
model = "inside multiline"
bye
"""

[status_line] # obsolete managed syntax
enabled = false
items = ["cwd"]

EOF
}

run_nested_merge_and_idempotence_test() {
    local tmpdir ws_root home_root cfg first
    tmpdir="$(mktemp -d)"; ws_root="$tmpdir/ws"; home_root="$tmpdir/home"
    cfg="$home_root/.codex/config.toml"; first="$tmpdir/first.toml"
    make_workspace "$ws_root"; mkdir -p "$home_root/.codex"
    write_complex_local_config "$cfg"

    if HOME="$home_root" bash "$ws_root/scripts/_core/sync-agent-configs.sh" >/dev/null 2>&1; then
        pass "nested merge command completes"
    else
        fail "nested merge command completes"
    fi
    assert_merged_semantics "$cfg" "owned keys converge and all unowned semantics survive"
    if grep -Fq '# keep this local feature comment' "$cfg"; then
        pass "unowned comments survive"
    else
        fail "unowned comments survive"
    fi
    cp "$cfg" "$first"
    HOME="$home_root" bash "$ws_root/scripts/_core/sync-agent-configs.sh" >/dev/null 2>&1 || fail "second merge command completes"
    assert_same "$first" "$cfg" "second merge is byte-idempotent"
    rm -rf "$tmpdir"
}

run_create_test() {
    local tmpdir ws_root home_root cfg
    tmpdir="$(mktemp -d)"; ws_root="$tmpdir/ws"; home_root="$tmpdir/home"
    cfg="$home_root/.codex/config.toml"
    make_workspace "$ws_root"; mkdir -p "$home_root"
    HOME="$home_root" bash "$ws_root/scripts/_core/sync-agent-configs.sh" >/dev/null 2>&1 || fail "create command completes"
    if uv run python - "$cfg" <<'PY' >/dev/null 2>&1
import pathlib, sys, tomllib
with pathlib.Path(sys.argv[1]).open("rb") as fh:
    data = tomllib.load(fh)
if "model" in data or "model_reasoning_effort" in data:
    raise SystemExit(1)
if data.get("tui", {}).get("resume_cwd") != "session":
    raise SystemExit(1)
PY
    then pass "create uses canonical config without machine-local model defaults"; else fail "create uses canonical config without machine-local model defaults"; fi
    rm -rf "$tmpdir"
}

run_repo_model_preservation_test() {
    local tmpdir ws_root home_root repo_cfg before
    tmpdir="$(mktemp -d)"; ws_root="$tmpdir/ws"; home_root="$tmpdir/home"
    repo_cfg="$ws_root/.codex/config.toml"; before="$tmpdir/repo.before"
    make_workspace "$ws_root"; mkdir -p "$home_root"
    printf 'model = "repo-local-model"\nmodel_reasoning_effort = "minimal"\n' > "$repo_cfg"
    cp "$repo_cfg" "$before"
    HOME="$home_root" bash "$ws_root/scripts/_core/sync-agent-configs.sh" >/dev/null 2>&1 || fail "repo preservation command completes"
    assert_same "$before" "$repo_cfg" "repo-local model choices remain unowned"
    rm -rf "$tmpdir"
}

run_dry_run_test() {
    local tmpdir ws_root home_root cfg before
    tmpdir="$(mktemp -d)"; ws_root="$tmpdir/ws"; home_root="$tmpdir/home"
    cfg="$home_root/.codex/config.toml"; before="$tmpdir/before"
    make_workspace "$ws_root"; mkdir -p "$home_root/.codex"
    write_complex_local_config "$cfg"; cp "$cfg" "$before"
    HOME="$home_root" bash "$ws_root/scripts/_core/sync-agent-configs.sh" --dry-run >/dev/null 2>&1 || fail "dry-run command completes"
    assert_same "$before" "$cfg" "dry-run leaves existing config byte-identical"
    assert_missing "$home_root/.claude" "dry-run does not create unrelated home config directories"
    rm -rf "$tmpdir"
}

run_malformed_atomicity_test() {
    local tmpdir ws_root home_root cfg before
    tmpdir="$(mktemp -d)"; ws_root="$tmpdir/ws"; home_root="$tmpdir/home"
    cfg="$home_root/.codex/config.toml"; before="$tmpdir/before"
    make_workspace "$ws_root"; mkdir -p "$home_root/.codex"
    printf 'model = "unterminated\n' > "$cfg"; cp "$cfg" "$before"
    if HOME="$home_root" bash "$ws_root/scripts/_core/sync-agent-configs.sh" >/dev/null 2>&1; then
        fail "malformed local config fails closed"
    else
        pass "malformed local config fails closed"
    fi
    assert_same "$before" "$cfg" "malformed local config rolls back atomically"

    write_complex_local_config "$cfg"; cp "$cfg" "$before"
    printf '[tui\nresume_cwd = "session"\n' > "$ws_root/config/agents/codex/config.toml"
    if HOME="$home_root" bash "$ws_root/scripts/_core/sync-agent-configs.sh" >/dev/null 2>&1; then
        fail "malformed canonical config fails closed"
    else
        pass "malformed canonical config fails closed"
    fi
    assert_same "$before" "$cfg" "malformed canonical config rolls back atomically"

    rm -f "$cfg"; rm -rf "$home_root/.codex"
    if HOME="$home_root" bash "$ws_root/scripts/_core/sync-agent-configs.sh" --dry-run >/dev/null 2>&1; then
        fail "dry-run rejects malformed canonical config"
    else
        pass "dry-run rejects malformed canonical config"
    fi
    assert_missing "$home_root/.codex" "failed dry-run creates no Codex directory"
    rm -rf "$tmpdir"
}

run_uv_required_test() {
    local tmpdir ws_root home_root cfg before path_without_uv
    tmpdir="$(mktemp -d)"; ws_root="$tmpdir/ws"; home_root="$tmpdir/home"
    cfg="$home_root/.codex/config.toml"; before="$tmpdir/before"
    make_workspace "$ws_root"; mkdir -p "$home_root/.codex"
    write_complex_local_config "$cfg"; cp "$cfg" "$before"
    path_without_uv="$(python3 - <<'PY'
import os
print(":".join(part for part in os.environ["PATH"].split(":")
               if not os.path.isfile(os.path.join(part, "uv"))))
PY
)"
    if HOME="$home_root" PATH="$path_without_uv" bash "$ws_root/scripts/_core/sync-agent-configs.sh" >/dev/null 2>&1; then
        fail "Codex merge fails closed when uv is unavailable"
    else
        pass "Codex merge fails closed when uv is unavailable"
    fi
    assert_same "$before" "$cfg" "missing uv leaves Codex config byte-identical"
    rm -rf "$tmpdir"
}

run_hermes_soul_no_clobber_test() {
    local tmpdir ws_root home_root soul
    tmpdir="$(mktemp -d)"; ws_root="$tmpdir/ws"; home_root="$tmpdir/home"; soul="$home_root/.hermes/SOUL.md"
    make_workspace "$ws_root"
    mkdir -p "$ws_root/config/agents/hermes" "$home_root/.hermes"
    printf 'delta\n' > "$ws_root/config/agents/hermes/SOUL.md"
    printf 'runtime\n' > "$ws_root/config/agents/hermes/SOUL.runtime.md"
    ln -s "$ws_root/config/agents/hermes/SOUL.runtime.md" "$soul"
    HOME="$home_root" bash "$ws_root/scripts/_core/sync-agent-configs.sh" >/dev/null 2>&1 || true
    if [[ -L "$soul" && "$(readlink "$soul")" == *SOUL.runtime.md ]]; then
        pass "sync preserves the Hermes runtime symlink"
    else
        fail "sync preserves the Hermes runtime symlink"
    fi
    rm -rf "$tmpdir"
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
    echo "=== test_sync_agent_configs.sh ==="
    run_nested_merge_and_idempotence_test
    run_create_test
    run_repo_model_preservation_test
    run_dry_run_test
    run_malformed_atomicity_test
    run_uv_required_test
    run_hermes_soul_no_clobber_test
    echo ""
    echo "Results: ${PASS} PASS, ${FAIL} FAIL"
    [[ $FAIL -eq 0 ]] || exit 1
    bash "$(dirname "$0")/test_sync_agent_configs_edge_cases.sh"
fi
