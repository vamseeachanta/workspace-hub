#!/usr/bin/env bash
# Focused #3555 edge cases for semantic Codex TOML merging.
set -euo pipefail

TEST_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=scripts/_core/tests/test_sync_agent_configs.sh
source "$TEST_DIR/test_sync_agent_configs.sh"
PASS=0
FAIL=0

list_codex_dir() {
    local path
    for path in "$1"/* "$1"/.[!.]* "$1"/..?*; do
        [[ -e "$path" ]] || continue
        basename "$path"
    done | sort
}

run_array_scope_and_comment_test() {
    local tmpdir ws_root home_root cfg
    tmpdir="$(mktemp -d)"; ws_root="$tmpdir/ws"; home_root="$tmpdir/home"
    cfg="$home_root/.codex/config.toml"
    make_workspace "$ws_root"; mkdir -p "$home_root/.codex"
    cat > "$cfg" <<'EOF'
model = "array-local"

[features]
goals = false # owned rationale survives

[[plugins.routes]]
name = "before"
status_line = ["plugin-before"]

[status_line]
enabled = false

[[mcp_servers.pool]]
name = "after"
status_line = ["mcp-after"]

[[features.providers]]
goals = false
model = "nested-provider"

[[tui.profiles]]
resume_cwd = "project"
animations = true
EOF
    if HOME="$home_root" bash "$ws_root/scripts/_core/sync-agent-configs.sh" >/dev/null 2>&1; then
        pass "array-table scopes converge"
    else
        fail "array-table scopes converge"
    fi
    if uv run python - "$cfg" <<'PY' >/dev/null 2>&1
import pathlib, sys, tomllib
with pathlib.Path(sys.argv[1]).open("rb") as fh:
    data = tomllib.load(fh)
assert data["model"] == "array-local" and "status_line" not in data
assert data["features"]["goals"] is True
assert data["plugins"]["routes"] == [{"name": "before", "status_line": ["plugin-before"]}]
assert data["mcp_servers"]["pool"] == [{"name": "after", "status_line": ["mcp-after"]}]
assert data["features"]["providers"] == [{"goals": False, "model": "nested-provider"}]
assert data["tui"]["profiles"] == [{"resume_cwd": "project", "animations": True}]
PY
    then pass "array-table scopes preserve colliding unowned leaves"; else fail "array-table scopes preserve colliding unowned leaves"; fi
    if grep -Fq 'goals = true # owned rationale survives' "$cfg"; then
        pass "owned assignment trailing comment survives"
    else
        fail "owned assignment trailing comment survives"
    fi
    rm -rf "$tmpdir"
}

run_inline_owned_table_test() {
    local tmpdir ws_root home_root cfg
    tmpdir="$(mktemp -d)"; ws_root="$tmpdir/ws"; home_root="$tmpdir/home"
    cfg="$home_root/.codex/config.toml"
    make_workspace "$ws_root"; mkdir -p "$home_root/.codex"
    cat > "$cfg" <<'EOF'
model = "inline-local"
tui = { animations = false, status_line = ["old"], resume_cwd = "root", theme = { name = "local" } } # inline TUI
features = { js_repl = true, goals = false }
agents = { max_threads = 9, enabled = false }
EOF
    if HOME="$home_root" bash "$ws_root/scripts/_core/sync-agent-configs.sh" >/dev/null 2>&1; then
        pass "inline owned tables converge"
    else
        fail "inline owned tables converge"
    fi
    if uv run python - "$cfg" <<'PY' >/dev/null 2>&1
import pathlib, sys, tomllib
with pathlib.Path(sys.argv[1]).open("rb") as fh:
    data = tomllib.load(fh)
assert data["model"] == "inline-local"
assert data["tui"]["animations"] is False and data["tui"]["theme"] == {"name": "local"}
assert data["tui"]["resume_cwd"] == "session" and len(data["tui"]["status_line"]) == 5
assert data["features"]["js_repl"] is True and data["features"]["goals"] is True
assert data["agents"]["max_threads"] == 9 and data["agents"]["enabled"] is True
PY
    then pass "inline owned tables preserve unowned siblings"; else fail "inline owned tables preserve unowned siblings"; fi
    rm -rf "$tmpdir"
}

run_dotted_owned_table_test() {
    local tmpdir ws_root home_root cfg
    tmpdir="$(mktemp -d)"; ws_root="$tmpdir/ws"; home_root="$tmpdir/home"
    cfg="$home_root/.codex/config.toml"
    make_workspace "$ws_root"; mkdir -p "$home_root/.codex"
    cat > "$cfg" <<'EOF'
model = "dotted-local"
tui.animations = false
tui.status_line = ["old"] # dotted footer rationale
features.js_repl = true
features.goals = false
agents.max_threads = 11
agents.enabled = false
EOF
    if HOME="$home_root" bash "$ws_root/scripts/_core/sync-agent-configs.sh" >/dev/null 2>&1; then
        pass "dotted owned tables converge"
    else
        fail "dotted owned tables converge"
    fi
    if uv run python - "$cfg" <<'PY' >/dev/null 2>&1
import pathlib, sys, tomllib
with pathlib.Path(sys.argv[1]).open("rb") as fh:
    data = tomllib.load(fh)
assert data["model"] == "dotted-local"
assert data["tui"]["animations"] is False and data["tui"]["resume_cwd"] == "session"
assert len(data["tui"]["status_line"]) == 5
assert data["features"]["js_repl"] is True and data["features"]["goals"] is True
assert data["agents"]["max_threads"] == 11 and data["agents"]["enabled"] is True
PY
    then pass "dotted owned tables preserve unowned siblings"; else fail "dotted owned tables preserve unowned siblings"; fi
    rm -rf "$tmpdir"
}

run_read_only_dry_run_test() {
    local tmpdir ws_root home_root cfg before_listing after_listing
    tmpdir="$(mktemp -d)"; ws_root="$tmpdir/ws"; home_root="$tmpdir/home"
    cfg="$home_root/.codex/config.toml"
    make_workspace "$ws_root"; mkdir -p "$home_root/.codex"
    write_complex_local_config "$cfg"
    before_listing="$(list_codex_dir "$home_root/.codex")"
    chmod 0555 "$home_root/.codex"
    if HOME="$home_root" bash "$ws_root/scripts/_core/sync-agent-configs.sh" --dry-run >/dev/null 2>&1; then
        pass "dry-run succeeds with read-only target directory"
    else
        fail "dry-run succeeds with read-only target directory"
    fi
    after_listing="$(list_codex_dir "$home_root/.codex")"
    chmod 0755 "$home_root/.codex"
    if [[ "$before_listing" == "$after_listing" ]]; then
        pass "dry-run creates no target-directory temp artifacts"
    else
        fail "dry-run creates no target-directory temp artifacts"
    fi
    rm -rf "$tmpdir"
}

echo "=== test_sync_agent_configs_edge_cases.sh ==="
run_array_scope_and_comment_test
run_inline_owned_table_test
run_dotted_owned_table_test
run_read_only_dry_run_test
echo ""
echo "Results: ${PASS} PASS, ${FAIL} FAIL"
[[ $FAIL -eq 0 ]]
