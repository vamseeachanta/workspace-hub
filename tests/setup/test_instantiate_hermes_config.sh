#!/usr/bin/env bash
# test_instantiate_hermes_config.sh — TDD tests for scripts/setup/lib/instantiate-hermes-config.sh
# Issue: vamseeachanta/workspace-hub#2751 (Phase 2, G4)
#
# Strategy: each test sets up a temp HOME + temp template, sources the helper,
# calls instantiate_hermes_config with the temp paths, asserts on output file.
#
# Run: bash tests/setup/test_instantiate_hermes_config.sh

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
HELPER="${REPO_ROOT}/scripts/setup/lib/instantiate-hermes-config.sh"
TEMPLATE="${REPO_ROOT}/config/agents/hermes/config.yaml.template"

PASS=0
FAIL=0
FAILED_TESTS=()

_pass() { echo "  PASS  $1"; PASS=$((PASS + 1)); }
_fail() { echo "  FAIL  $1"; echo "        $2"; FAIL=$((FAIL + 1)); FAILED_TESTS+=("$1"); }

echo "=== test_instantiate_hermes_config.sh (issue #2751 Phase 2 G4) ==="
echo ""

if [[ ! -f "$HELPER" ]]; then
    _fail "helper_exists" "missing: $HELPER (expected in TDD RED phase)"
    echo ""; echo "=== Summary: $PASS PASS, $FAIL FAIL ==="; exit 1
fi

if [[ ! -f "$TEMPLATE" ]]; then
    _fail "template_exists" "missing: $TEMPLATE — cannot test render"
    echo ""; echo "=== Summary: $PASS PASS, $FAIL FAIL ==="; exit 1
fi

# Helper to run the function under test with a temp HOME.
_run() {
    local fake_home="$1" repo_root="$2"; shift 2
    bash <<RUNEOF 2>&1
        set -u
        export HOME="$fake_home"
        source "$HELPER"
        instantiate_hermes_config "$repo_root" "$@"
RUNEOF
}

# Test 1: first-run render — target missing, template renders cleanly
tmphome="$(mktemp -d)"
output="$(_run "$tmphome" "$REPO_ROOT")"
target="${tmphome}/.hermes/config.yaml"
if [[ -f "$target" ]]; then
    _pass "first_run_target_created"
else
    _fail "first_run_target_created" "target file not created: $target. output: $output"
fi
if grep -qF "__WS_HUB_PATH__" "$target" 2>/dev/null; then
    _fail "first_run_placeholder_substituted" "placeholder __WS_HUB_PATH__ still present in output"
else
    _pass "first_run_placeholder_substituted"
fi
if grep -qF "${REPO_ROOT}/.claude/skills" "$target" 2>/dev/null; then
    _pass "first_run_skills_path_resolved"
else
    _fail "first_run_skills_path_resolved" "expected ${REPO_ROOT}/.claude/skills in output"
fi
rm -rf "$tmphome"

# Test 2: idempotent — re-run when target exists → no overwrite
tmphome="$(mktemp -d)"
_run "$tmphome" "$REPO_ROOT" >/dev/null
target="${tmphome}/.hermes/config.yaml"
echo "USER_EDIT_MARKER" >> "$target"
mtime_before=$(stat -c '%Y' "$target")
sleep 1
_run "$tmphome" "$REPO_ROOT" >/dev/null
mtime_after=$(stat -c '%Y' "$target")
if [[ "$mtime_before" == "$mtime_after" ]] && grep -qF "USER_EDIT_MARKER" "$target"; then
    _pass "idempotent_skip_when_target_exists"
else
    _fail "idempotent_skip_when_target_exists" "re-run modified existing target (mtime: $mtime_before → $mtime_after, marker preserved: $(grep -q USER_EDIT_MARKER "$target" && echo yes || echo no))"
fi
rm -rf "$tmphome"

# Test 3: --force flag overrides idempotency
tmphome="$(mktemp -d)"
_run "$tmphome" "$REPO_ROOT" >/dev/null
target="${tmphome}/.hermes/config.yaml"
echo "USER_EDIT_MARKER_FORCE" >> "$target"
_run "$tmphome" "$REPO_ROOT" --force >/dev/null
if ! grep -qF "USER_EDIT_MARKER_FORCE" "$target"; then
    _pass "force_flag_overwrites"
else
    _fail "force_flag_overwrites" "--force did not overwrite user edits"
fi
rm -rf "$tmphome"

# Test 4: file permissions are restrictive (mode 600 — Hermes config is sensitive)
tmphome="$(mktemp -d)"
_run "$tmphome" "$REPO_ROOT" >/dev/null
target="${tmphome}/.hermes/config.yaml"
perms=$(stat -c '%a' "$target")
if [[ "$perms" == "600" ]]; then
    _pass "target_mode_600"
else
    _fail "target_mode_600" "expected mode 600, got $perms"
fi
rm -rf "$tmphome"

# Test 5: missing template path → error exit
tmphome="$(mktemp -d)"
fake_repo="$(mktemp -d)"   # has no template
output="$(_run "$tmphome" "$fake_repo" 2>&1)"
if echo "$output" | grep -qi "template not found\|template missing"; then
    _pass "missing_template_errors_clearly"
else
    _fail "missing_template_errors_clearly" "expected error message about missing template. got: $output"
fi
rm -rf "$tmphome" "$fake_repo"

echo ""
echo "=== Summary: $PASS PASS, $FAIL FAIL ==="
if [[ "$FAIL" -gt 0 ]]; then
    echo "    Failed: ${FAILED_TESTS[*]}"
    exit 1
fi
exit 0
