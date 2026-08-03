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

assert_second_run_idempotent() {
    local ws_root="$1" home_root="$2" cfg="$3" before="$4" label="$5"
    cp "$cfg" "$before"
    if HOME="$home_root" bash "$ws_root/scripts/_core/sync-agent-configs.sh" >/dev/null 2>&1; then
        assert_same "$before" "$cfg" "$label"
    else
        fail "$label (second sync failed)"
    fi
}

assert_array_semantics() {
    local cfg="$1"
    uv run python - "$cfg" <<'PY' >/dev/null 2>&1
import pathlib, sys, tomllib
with pathlib.Path(sys.argv[1]).open("rb") as fh:
    data = tomllib.load(fh)
assert data["model"] == "array-local" and "status_line" not in data
assert data["features"]["goals"] is True
assert data["plugins"]["a]b"]["keep"] is True
assert data["plugins"]["normal[key"]["keep"] == "normal"
assert data["plugins"]["array]key"] == [{"keep": "array"}]
assert data["features"]["providers"] == [{"goals": False, "model": "nested-provider"}]
assert data["tui"]["profiles"] == [{"resume_cwd": "project", "animations": True}]
PY
}

run_array_scope_and_comment_test() {
    local tmpdir ws_root home_root cfg before
    tmpdir="$(mktemp -d)"; ws_root="$tmpdir/ws"; home_root="$tmpdir/home"; cfg="$home_root/.codex/config.toml"
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

[plugins."a]b"]
keep = true

[plugins."normal[key"]
keep = "normal"

[[plugins."array]key"]]
keep = "array"

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
    if assert_array_semantics "$cfg"; then pass "quoted/array headers preserve unowned data"; else fail "quoted/array headers preserve unowned data"; fi
    if grep -Fq 'goals = true # owned rationale survives' "$cfg"; then
        pass "owned assignment trailing comment survives"
    else
        fail "owned assignment trailing comment survives"
    fi
    before="$tmpdir/array.first"
    assert_second_run_idempotent "$ws_root" "$home_root" "$cfg" "$before" "array fixture is byte-idempotent"
    rm -rf "$tmpdir"
}

run_inline_owned_table_test() {
    local tmpdir ws_root home_root cfg before
    tmpdir="$(mktemp -d)"; ws_root="$tmpdir/ws"; home_root="$tmpdir/home"
    cfg="$home_root/.codex/config.toml"
    make_workspace "$ws_root"; mkdir -p "$home_root/.codex"
    cat > "$cfg" <<'EOF'
model = "inline-local"
tui = { animations = false, status_line = ["old"], resume_cwd = "root", theme = { name = "local" } } # inline TUI }
features = { js_repl = true, "goals" = false }
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
    before="$tmpdir/inline.first"
    assert_second_run_idempotent "$ws_root" "$home_root" "$cfg" "$before" "inline fixture is byte-idempotent"
    rm -rf "$tmpdir"
}

run_dotted_owned_table_test() {
    local tmpdir ws_root home_root cfg before
    tmpdir="$(mktemp -d)"; ws_root="$tmpdir/ws"; home_root="$tmpdir/home"
    cfg="$home_root/.codex/config.toml"
    make_workspace "$ws_root"; mkdir -p "$home_root/.codex"
    cat > "$cfg" <<'EOF'
model = "dotted-local"
tui.animations = false
tui . status_line = [
  "old", # retain-this-comment
] # dotted footer rationale
features . js_repl = true
features . "goals" = false
agents . max_threads = 11
agents . "enabled" = false
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
    if grep -Fq '# retain-this-comment' "$cfg"; then
        pass "multiline owned assignment comments survive"
    else
        fail "multiline owned assignment comments survive"
    fi
    before="$tmpdir/dotted.first"
    assert_second_run_idempotent "$ws_root" "$home_root" "$cfg" "$before" "dotted fixture is byte-idempotent"
    rm -rf "$tmpdir"
}

run_multiline_owned_comment_test() {
    local tmpdir ws_root home_root cfg
    tmpdir="$(mktemp -d)"; ws_root="$tmpdir/ws"; home_root="$tmpdir/home"
    cfg="$home_root/.codex/config.toml"
    make_workspace "$ws_root"; mkdir -p "$home_root/.codex"
    cat > "$cfg" <<'EOF'
[tui]
status_line = [
  # retain-before-item
  "old", # retain-after-item
]
EOF
    HOME="$home_root" bash "$ws_root/scripts/_core/sync-agent-configs.sh" >/dev/null 2>&1 || fail "multiline comment sync completes"
    if grep -Fq '# retain-before-item' "$cfg" && grep -Fq '# retain-after-item' "$cfg"; then
        pass "all multiline owned comments survive"
    else
        fail "all multiline owned comments survive"
    fi
    rm -rf "$tmpdir"
}

run_probe_component_collision_test() {
    local tmpdir ws_root home_root cfg
    tmpdir="$(mktemp -d)"; ws_root="$tmpdir/ws"; home_root="$tmpdir/home"
    cfg="$home_root/.codex/config.toml"
    make_workspace "$ws_root"; mkdir -p "$home_root/.codex"
    cat > "$cfg" <<'EOF'
[status_line]
enabled = false

[features.__codex_sync_probe__]
goals = false
keep = true
EOF
    if HOME="$home_root" bash "$ws_root/scripts/_core/sync-agent-configs.sh" >/dev/null 2>&1; then
        if uv run python - "$cfg" <<'PY' >/dev/null 2>&1
import pathlib, sys, tomllib
with pathlib.Path(sys.argv[1]).open("rb") as fh:
    data = tomllib.load(fh)
assert data["features"]["goals"] is True
assert data["features"]["__codex_sync_probe__"] == {"goals": False, "keep": True}
PY
        then pass "probe-named path component preserves exact scope"; else fail "probe-named path component preserves exact scope"; fi
    else
        fail "probe-named path component sync completes"
    fi
    rm -rf "$tmpdir"
}

assert_incompatible_owned_root_fails_closed() {
    local assignment="$1" label="$2" tmpdir ws_root home_root cfg before
    tmpdir="$(mktemp -d)"; ws_root="$tmpdir/ws"; home_root="$tmpdir/home"
    cfg="$home_root/.codex/config.toml"; before="$tmpdir/before"
    make_workspace "$ws_root"; mkdir -p "$home_root/.codex"
    printf 'model = "shape-local"\n%s\n' "$assignment" > "$cfg"; cp "$cfg" "$before"
    if HOME="$home_root" bash "$ws_root/scripts/_core/sync-agent-configs.sh" >/dev/null 2>&1; then
        fail "$label fails closed"
    else
        pass "$label fails closed"
    fi
    assert_same "$before" "$cfg" "$label remains byte-identical"
    if HOME="$home_root" bash "$ws_root/scripts/_core/sync-agent-configs.sh" --dry-run >/dev/null 2>&1; then
        fail "$label dry-run fails closed"
    else
        pass "$label dry-run fails closed"
    fi
    assert_same "$before" "$cfg" "$label dry-run remains byte-identical"
    rm -rf "$tmpdir"
}

run_incompatible_owned_root_tests() {
    assert_incompatible_owned_root_fails_closed \
        'features = [{ goals = false, keep = true }]' "owned-root array"
    assert_incompatible_owned_root_fails_closed 'agents = "local"' "owned-root string"
    assert_incompatible_owned_root_fails_closed 'tui = ["local"]' "owned-root scalar array"
}

run_final_header_without_newline_test() {
    local tmpdir ws_root home_root cfg first
    tmpdir="$(mktemp -d)"; ws_root="$tmpdir/ws"; home_root="$tmpdir/home"
    cfg="$home_root/.codex/config.toml"; first="$tmpdir/first"
    make_workspace "$ws_root"; mkdir -p "$home_root/.codex"
    printf 'model = "final-header-local"\n\n[plugins.final]' > "$cfg"
    if HOME="$home_root" bash "$ws_root/scripts/_core/sync-agent-configs.sh" >/dev/null 2>&1; then
        if uv run python - "$cfg" <<'PY' >/dev/null 2>&1
import pathlib, sys, tomllib
with pathlib.Path(sys.argv[1]).open("rb") as fh:
    data = tomllib.load(fh)
assert data["model"] == "final-header-local"
assert data["plugins"]["final"] == {}
assert data["features"]["goals"] is True
PY
        then pass "final header without newline converges"; else fail "final header without newline converges"; fi
    else
        fail "final header without newline converges"
    fi
    first="$tmpdir/final-header.first"
    assert_second_run_idempotent "$ws_root" "$home_root" "$cfg" "$first" "final-header fixture is byte-idempotent"
    rm -rf "$tmpdir"
}

write_quote_lexer_case() {
    local cfg="$1" form="$2" count="$3" header_kind="$4"
    uv run --no-project python - "$form" "$count" "$header_kind" > "$cfg" <<'PY'
import sys, tomllib
form, count, header_kind = sys.argv[1], int(sys.argv[2]), sys.argv[3]
slashes = "\\" * count
prefix = "first#inside\nvalue" if form.startswith("multiline") else "value#inside"
if form == "basic":
    value = f'"{prefix}{slashes}"' if count % 2 == 0 else f'"{prefix}{slashes}"tail"'
elif form == "multiline_basic":
    value = f'"""{prefix}{slashes}"""' if count % 2 == 0 else f'"""{prefix}{slashes}"""tail"""'
elif form == "literal":
    value = f"'{prefix}{slashes}'"
else:
    value = f"'''{prefix}{slashes}'''"
label = f"{form}-{count}"
header = ('[plugins."keep]normal"]' if header_kind == "normal"
          else '[[plugins."keep]array"]]')
source = f'[tui]\nstatus_line = [{value}] # outside comment " # ] }}\n\n{header}\nvalue = "{label}"\n'
tomllib.loads(source)
print(source, end="")
PY
}

assert_quote_lexer_semantics() {
    local cfg="$1" form="$2" count="$3" header_kind="$4"
    uv run --no-project python - "$cfg" "$form-$count" "$header_kind" <<'PY' >/dev/null 2>&1
import pathlib, sys, tomllib
with pathlib.Path(sys.argv[1]).open("rb") as fh:
    data = tomllib.load(fh)
expected, header_kind = sys.argv[2:]
assert len(data["tui"]["status_line"]) == 5
kept = data["plugins"]["keep]normal"] if header_kind == "normal" else data["plugins"]["keep]array"][0]
assert kept == {"value": expected}
PY
}

run_quote_lexer_case() {
    local form="$1" count="$2" tmpdir ws_root home_root cfg first header_kind label
    tmpdir="$(mktemp -d)"; ws_root="$tmpdir/ws"; home_root="$tmpdir/home"
    cfg="$home_root/.codex/config.toml"; first="$tmpdir/first"
    header_kind="normal"; (( count % 2 == 0 )) || header_kind="array"
    label="$form backslashes=$count"
    make_workspace "$ws_root"; mkdir -p "$home_root/.codex"
    write_quote_lexer_case "$cfg" "$form" "$count" "$header_kind"
    if HOME="$home_root" bash "$ws_root/scripts/_core/sync-agent-configs.sh" >/dev/null 2>&1; then
        if assert_quote_lexer_semantics "$cfg" "$form" "$count" "$header_kind"; then
            pass "$label preserves following statement"
        else
            fail "$label preserves following statement"
        fi
        cp "$cfg" "$first"
        assert_second_run_idempotent "$ws_root" "$home_root" "$cfg" "$first" "$label is byte-idempotent"
    else
        fail "$label sync completes"
    fi
    rm -rf "$tmpdir"
}

run_quote_lexer_matrix() {
    local form count
    for form in basic literal multiline_basic multiline_literal; do
        for count in 0 1 2 3 4 5 6; do
            run_quote_lexer_case "$form" "$count"
        done
    done
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
run_multiline_owned_comment_test
run_probe_component_collision_test
run_incompatible_owned_root_tests
run_final_header_without_newline_test
run_quote_lexer_matrix
run_read_only_dry_run_test
echo ""
echo "Results: ${PASS} PASS, ${FAIL} FAIL"
[[ $FAIL -eq 0 ]]
