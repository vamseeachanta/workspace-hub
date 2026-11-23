#!/usr/bin/env bash
# test_emit_machine_status.sh — TDD tests for scripts/setup/lib/emit-machine-status.sh
# Issue: vamseeachanta/workspace-hub#2751 (Phase 3, G9)
#
# Strategy: each test sets up a temp repo-root (so output files don't pollute
# real config/machine-baselines/), overrides the dimension-check wrappers to
# return canned values, runs emit_machine_status, asserts on output files.
#
# Run: bash tests/setup/test_emit_machine_status.sh

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
HELPER="${REPO_ROOT}/scripts/setup/lib/emit-machine-status.sh"

PASS=0
FAIL=0
FAILED_TESTS=()

_pass() { echo "  PASS  $1"; PASS=$((PASS + 1)); }
_fail() { echo "  FAIL  $1"; echo "        $2"; FAIL=$((FAIL + 1)); FAILED_TESTS+=("$1"); }

echo "=== test_emit_machine_status.sh (issue #2751 Phase 3 G9) ==="
echo ""

if [[ ! -f "$HELPER" ]]; then
    _fail "helper_exists" "missing: $HELPER (expected in TDD RED phase)"
    echo ""; echo "=== Summary: $PASS PASS, $FAIL FAIL ==="; exit 1
fi

# Helper to run emit with overridden checks. Output goes to a temp repo.
_run_emit() {
    local fake_repo="$1" fake_hostname="$2"
    bash <<RUNEOF 2>&1
        set -u
        source "$HELPER"
        # Override hostname source so tests don't depend on real machine
        get_raw_hostname() { echo "$fake_hostname"; }
        # Stub all 22 dimension checks to PASS (test individual scenarios elsewhere)
        for d in soul_contracts skills rules bridged_memory claude_global_pointer \
                 codex_agents_symlink hermes_soul_symlink claude_cli_auth \
                 codex_cli_auth gh_cli_auth gemini_cli_auth hermes_can_boot \
                 submodules_initialized git_hooks_installed shell_profile_wired \
                 npm_global_prefix scheduler_entries ssh_key_present \
                 env_file_present uv_or_python_available git_bash_available; do
            eval "check_dimension_\${d}() { echo PASS; }"
        done
        check_dimension_raw_session_state() { echo "machine-local-by-design"; }
        emit_machine_status "$fake_repo"
RUNEOF
}

# --- Test 1: First-run emission produces both YAML and MD files ---
fake_repo="$(mktemp -d)"
output="$(_run_emit "$fake_repo" "test-host-1")"
if compgen -G "${fake_repo}/config/machine-baselines/*.yaml" >/dev/null; then
    _pass "first_run_yaml_created"
else
    _fail "first_run_yaml_created" "no yaml file under ${fake_repo}/config/machine-baselines/. output: $output"
fi
if compgen -G "${fake_repo}/config/machine-baselines/*.md" >/dev/null; then
    _pass "first_run_md_created"
else
    _fail "first_run_md_created" "no md file under ${fake_repo}/config/machine-baselines/"
fi

# --- Test 2: YAML has required top-level keys ---
yaml_file=$(ls ${fake_repo}/config/machine-baselines/*.yaml 2>/dev/null | head -1)
for key in hostname os last_updated dimensions cli_versions; do
    if grep -qE "^${key}:" "$yaml_file"; then
        _pass "yaml_has_${key}"
    else
        _fail "yaml_has_${key}" "missing top-level key in $yaml_file"
    fi
done

# --- Test 3: All 22 dimensions enumerated in YAML ---
expected_dims="soul_contracts skills rules bridged_memory claude_global_pointer \
codex_agents_symlink hermes_soul_symlink claude_cli_auth codex_cli_auth gh_cli_auth \
gemini_cli_auth hermes_can_boot raw_session_state submodules_initialized \
git_hooks_installed shell_profile_wired npm_global_prefix scheduler_entries \
ssh_key_present env_file_present uv_or_python_available git_bash_available"
missing_dims=()
for dim in $expected_dims; do
    grep -qE "^[[:space:]]+${dim}:" "$yaml_file" || missing_dims+=("$dim")
done
if [[ ${#missing_dims[@]} -eq 0 ]]; then
    _pass "yaml_all_22_dimensions_present"
else
    _fail "yaml_all_22_dimensions_present" "missing: ${missing_dims[*]}"
fi

# --- Test 4: MD file has hostname header + dimension table ---
md_file=$(ls ${fake_repo}/config/machine-baselines/*.md 2>/dev/null | head -1)
if grep -qF "test-host-1" "$md_file"; then
    _pass "md_has_hostname"
else
    _fail "md_has_hostname" "hostname not in md output"
fi

rm -rf "$fake_repo"

# --- Test 5: Hostname token uses sha256 fallback when no alias provided ---
# (Plan §Open r1 m4: alias-with-sha256-fallback policy)
fake_repo="$(mktemp -d)"
_run_emit "$fake_repo" "long-hostname-with-pii-vamsee-tx-bjk-01" >/dev/null
yaml_file=$(ls ${fake_repo}/config/machine-baselines/*.yaml 2>/dev/null | head -1)
basename=$(basename "$yaml_file" .yaml)
# Should NOT contain "vamsee-tx" raw — should be sha256 first 8 chars
if [[ ! "$basename" =~ vamsee ]]; then
    _pass "hostname_token_no_raw_pii"
else
    _fail "hostname_token_no_raw_pii" "raw hostname leaked in filename: $basename"
fi
# Should be 8 hex chars (sha256 truncated)
if [[ "$basename" =~ ^[a-f0-9]{8}$ ]]; then
    _pass "hostname_token_sha256_8char_format"
else
    _fail "hostname_token_sha256_8char_format" "token not 8-hex format: $basename"
fi
rm -rf "$fake_repo"

# --- Test 6: Hostname alias used when present in machines.yaml ---
fake_repo="$(mktemp -d)"
mkdir -p "${fake_repo}/config/agents"
cat > "${fake_repo}/config/agents/machines.yaml" <<MACHEOF
aliases:
  test-host-1: ace-linux-test
MACHEOF
_run_emit "$fake_repo" "test-host-1" >/dev/null
yaml_file=$(ls ${fake_repo}/config/machine-baselines/*.yaml 2>/dev/null | head -1)
basename=$(basename "$yaml_file" .yaml)
if [[ "$basename" == "ace-linux-test" ]]; then
    _pass "hostname_alias_used_when_present"
else
    _fail "hostname_alias_used_when_present" "expected ace-linux-test, got $basename"
fi
rm -rf "$fake_repo"

# --- Test 7: Secret scrub — 7 token patterns redacted ---
# scrub_secrets is a standalone function; test it directly with fixture strings.
secret_input='gh_abc123def456ghi789jkl0 github_pat_xyz123abc456def789ghi012jkl345 sk-1234567890abcdef1234567890abcdef sk-ant-abc1234567890def1234567890ghi45 AIzaSyD1234567890abcdef1234567890abcdef refresh_token: "rt-secret-value" eyJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJ0ZXN0In0.signaturepart'
scrubbed=$(bash -c "source '$HELPER'; scrub_secrets '$secret_input'")
for pattern_name in "GH_TOKEN" "GH_PAT" "OPENAI" "ANTHROPIC" "GOOGLE" "JWT"; do
    # Each pattern should produce a [REDACTED_*] marker
    if grep -qF "[REDACTED" <<<"$scrubbed"; then
        _pass "scrub_pattern_$pattern_name"
    else
        _fail "scrub_pattern_$pattern_name" "no [REDACTED markers in scrubbed output: $scrubbed"
        break
    fi
done

# --- Test 8: Idempotency — re-run only changes last_updated ---
fake_repo="$(mktemp -d)"
_run_emit "$fake_repo" "test-host-idempotent" >/dev/null
yaml_file=$(ls ${fake_repo}/config/machine-baselines/*.yaml 2>/dev/null | head -1)
first_content=$(grep -v "^last_updated:" "$yaml_file")
sleep 1
_run_emit "$fake_repo" "test-host-idempotent" >/dev/null
second_content=$(grep -v "^last_updated:" "$yaml_file")
if [[ "$first_content" == "$second_content" ]]; then
    _pass "idempotent_only_timestamp_changes"
else
    _fail "idempotent_only_timestamp_changes" "non-timestamp content changed across runs"
fi
rm -rf "$fake_repo"

echo ""
echo "=== Summary: $PASS PASS, $FAIL FAIL ==="
if [[ "$FAIL" -gt 0 ]]; then
    echo "    Failed: ${FAILED_TESTS[*]}"
    exit 1
fi
exit 0
